"""
Deterministic campaign compiler.

compile_campaign_to_page_yaml(campaign_doc) turns a validated campaign document
into existing renderer-compatible YAML (a list whose first item is `site`).

Flow (brief §3 compiler flow):
    validate campaign
      -> normalize typed content
      -> derive conversion_goal (if only user goal present)
      -> select recipe (explicit recipe id or scored)
      -> resolve content refs per section
      -> build renderer components per section purpose
      -> assemble site > page
"""

from campaign import vocabulary as V
from campaign.validators import validate_campaign
from campaign.schema import CampaignValidationError
from campaign.content import normalize_campaign_content, available_types
from campaign.content_refs import try_resolve_refs
from campaign.recipes import select_recipe, build_recipe_context, load_section_purposes
from campaign.section_builders import build_section

_DEFAULT_THEME = {
    'colors': {
        'primary': '#111827',
        'text': '#374151',
        'secondary': '#6b7280',
        'accent': '#6366f1',
        'background': '#ffffff',
    }
}


def compile_campaign_to_page_yaml(campaign_doc, *, strip_metadata=False):
    """Compile a campaign document into renderer-compatible YAML.

    Args:
        campaign_doc: dict with `campaign`, `content`, `landing_page`.
        strip_metadata: if True, remove non-renderer keys (section_id) from
            the output — use when a renderer rejects unknown keys.

    Returns:
        dict with:
          - yaml: list[dict] renderer structure (site > page > sections)
          - recipe: the selection result (id, score, explanation, ...)
          - missing: {section_id: {slot: reason}} for unresolved refs
          - metadata: {campaign_id, recipe_id}

    Raises:
        CampaignValidationError if the campaign document is invalid.
    """
    errors = validate_campaign(campaign_doc)
    if errors:
        raise CampaignValidationError(errors)

    campaign_block = dict(campaign_doc['campaign'])
    landing = campaign_doc['landing_page']

    # Derive conversion_goal if a simple user goal slipped in without it.
    if not campaign_block.get('conversion_goal') and campaign_block.get('goal'):
        campaign_block['conversion_goal'] = V.derive_conversion_goal(
            campaign_block.get('goal'),
            campaign_block.get('sales_cycle'),
            awareness_stage=campaign_block.get('awareness_stage'),
            traffic_source=campaign_block.get('traffic_source'),
        )

    # Normalize typed content.
    content_items = normalize_campaign_content(campaign_doc['content'])
    avail = available_types(content_items)

    # Select recipe (explicit landing_page.recipe wins, still scored for reason).
    context = build_recipe_context(campaign_block)
    chosen = select_recipe(context, avail, explicit_id=landing.get('recipe'))
    recipe = chosen['recipe']
    section_purposes = load_section_purposes()

    # Section source: prefer the campaign's own sections if provided, else the
    # recipe's section_sequence.
    sections_spec = landing.get('sections') or recipe.get('section_sequence') or []

    page_components = []
    missing = {}
    for spec in sections_spec:
        purpose = spec.get('purpose')
        section_id = spec.get('id') or purpose
        refs = spec.get('content_refs') or {}

        resolved, slot_missing = try_resolve_refs(refs, campaign_block, content_items)

        # Skip optional sections that resolved nothing.
        is_optional = bool(spec.get('optional'))
        if is_optional and not resolved:
            continue
        if slot_missing:
            missing[section_id] = slot_missing

        # Unknown purpose -> still build generically, but record it.
        if purpose not in section_purposes:
            missing.setdefault(section_id, {})['__purpose__'] = \
                f'unknown section purpose "{purpose}"'

        section = build_section(purpose, resolved, section_id=section_id)
        if section and section.get('components', [{}])[0].get('components'):
            page_components.append(section)

    theme = landing.get('theme') or _DEFAULT_THEME
    structure = [{
        'name': 'site',
        'properties': {'theme': theme},
        'components': [{
            'name': 'page',
            'slug': landing.get('slug', 'home'),
            'title': landing.get('title', campaign_block.get('name', 'Campaign')),
            'properties': {
                'appearance': {
                    'background': {
                        'color': theme.get('colors', {}).get('background', '#ffffff'),
                        'opacity': 100,
                    }
                }
            },
            'components': page_components,
        }],
    }]

    if strip_metadata:
        _strip_metadata(structure)

    return {
        'yaml': structure,
        'recipe': {
            'id': chosen['id'],
            'name': chosen['name'],
            'score': chosen['score'],
            'explanation': chosen['explanation'],
        },
        'missing': missing,
        'metadata': {
            'campaign_id': campaign_block.get('id'),
            'recipe_id': chosen['id'],
        },
    }


def _strip_metadata(node):
    """Recursively remove non-renderer bookkeeping keys (section_id)."""
    if isinstance(node, dict):
        node.pop('section_id', None)
        for v in node.values():
            _strip_metadata(v)
    elif isinstance(node, list):
        for item in node:
            _strip_metadata(item)
