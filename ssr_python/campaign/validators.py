"""
Campaign / recipe / section-purpose validation.

Validates the campaign YAML contract (brief §5) before compilation, plus recipe
and section-purpose definitions. Pure functions returning error lists; callers
may raise CampaignValidationError(errors) when they want hard failures.
"""

from campaign import vocabulary as V
from campaign.schema import (
    CampaignValidationError, require_keys, check_enum, check_enum_list,
)

# Content-ref syntax: campaign.<field>  OR  content.<type>[idx]  OR content.<type>.<key>
_REF_PREFIXES = ('campaign.', 'content.')


def validate_campaign(doc):
    """Validate a full campaign document. Returns a list of error strings."""
    errors = []
    if not isinstance(doc, dict):
        return ['Campaign document must be a mapping/object.']

    errors += require_keys(doc, ['campaign', 'content', 'landing_page'], 'campaign document')
    # If top-level keys are missing, deeper checks are not meaningful.
    if errors:
        return errors

    errors += _validate_campaign_block(doc['campaign'])
    errors += _validate_content_block(doc['content'])
    errors += _validate_landing_page(doc['landing_page'], doc['content'])
    return errors


def validate_campaign_or_raise(doc):
    errors = validate_campaign(doc)
    if errors:
        raise CampaignValidationError(errors)
    return True


# --- campaign block -----------------------------------------------------------

def _validate_campaign_block(campaign):
    errors = require_keys(
        campaign,
        ['id', 'name', 'product', 'audience', 'conversion_goal', 'awareness_stage'],
        'campaign',
    )
    if not isinstance(campaign, dict):
        return errors

    check_enum(campaign.get('conversion_goal'), V.CONVERSION_GOAL,
               'conversion_goal', 'campaign', errors, allow_empty=False)
    check_enum(campaign.get('awareness_stage'), V.AWARENESS_STAGE,
               'awareness_stage', 'campaign', errors, allow_empty=False)
    # Optional context fields — validated only when present.
    check_enum(campaign.get('industry'), V.INDUSTRY, 'industry', 'campaign', errors)
    check_enum(campaign.get('traffic_source'), V.TRAFFIC_SOURCE, 'traffic_source', 'campaign', errors)
    check_enum(campaign.get('sales_cycle'), V.SALES_CYCLE, 'sales_cycle', 'campaign', errors)
    check_enum(campaign.get('audience_sophistication'), V.AUDIENCE_SOPHISTICATION,
               'audience_sophistication', 'campaign', errors)
    check_enum(campaign.get('brand_style'), V.BRAND_STYLE, 'brand_style', 'campaign', errors)
    return errors


# --- content block ------------------------------------------------------------

def _validate_content_block(content):
    """Accept grouped shorthand or an explicit typed-item list."""
    errors = []
    if isinstance(content, dict):
        for group_key in content:
            if group_key not in V.GROUP_KEY_TO_TYPE:
                errors.append(
                    f'content has unknown group key "{group_key}" '
                    f'(no matching content type).'
                )
    elif isinstance(content, list):
        for i, item in enumerate(content):
            if not isinstance(item, dict):
                errors.append(f'content[{i}] must be a mapping with type+content.')
                continue
            if 'type' not in item:
                errors.append(f'content[{i}] is missing "type".')
            elif item['type'] not in V.CONTENT_TYPE:
                errors.append(f'content[{i}].type = "{item["type"]}" is not a known content type.')
            if 'content' not in item or item['content'] in (None, ''):
                errors.append(f'content[{i}] is missing "content".')
    else:
        errors.append('content must be a grouped mapping or a list of typed items.')
    return errors


# --- landing_page block -------------------------------------------------------

def _validate_landing_page(lp, content):
    errors = require_keys(lp, ['slug', 'title', 'recipe', 'sections'], 'landing_page')
    if not isinstance(lp, dict):
        return errors

    sections = lp.get('sections')
    if not isinstance(sections, list) or not sections:
        errors.append('landing_page.sections must be a non-empty list.')
        return errors

    for i, sec in enumerate(sections):
        where = f'landing_page.sections[{i}]'
        if not isinstance(sec, dict):
            errors.append(f'{where} must be a mapping.')
            continue
        errors += require_keys(sec, ['id', 'purpose'], where)
        refs = sec.get('content_refs') or {}
        if refs and not isinstance(refs, dict):
            errors.append(f'{where}.content_refs must be a mapping.')
            continue
        for slot, ref in refs.items():
            errors += _validate_ref_syntax(ref, f'{where}.content_refs.{slot}')
    return errors


def _validate_ref_syntax(ref, where):
    """Validate the *syntax* of a content_ref. Resolution is checked separately."""
    if not isinstance(ref, str) or not ref.strip():
        return [f'{where} must be a non-empty reference string.']
    if not ref.startswith(_REF_PREFIXES):
        return [f'{where} = "{ref}" must start with "campaign." or "content.".']
    return []


# --- recipe validation --------------------------------------------------------

def validate_recipe(recipe):
    """Validate a recipe definition (brief §6). Returns error list."""
    errors = require_keys(recipe, ['id', 'name', 'section_sequence'], 'recipe')
    if not isinstance(recipe, dict):
        return errors

    applies = recipe.get('applies_when') or {}
    if applies and isinstance(applies, dict):
        check_enum(applies.get('conversion_goal'), V.CONVERSION_GOAL, 'conversion_goal', 'recipe.applies_when', errors)
        check_enum(applies.get('awareness_stage'), V.AWARENESS_STAGE, 'awareness_stage', 'recipe.applies_when', errors)
        check_enum(applies.get('traffic_source'), V.TRAFFIC_SOURCE, 'traffic_source', 'recipe.applies_when', errors)
        check_enum(applies.get('industry'), V.INDUSTRY, 'industry', 'recipe.applies_when', errors)
        check_enum(applies.get('sales_cycle'), V.SALES_CYCLE, 'sales_cycle', 'recipe.applies_when', errors)
        check_enum(applies.get('audience_sophistication'), V.AUDIENCE_SOPHISTICATION, 'audience_sophistication', 'recipe.applies_when', errors)
        check_enum(applies.get('brand_style'), V.BRAND_STYLE, 'brand_style', 'recipe.applies_when', errors)

    for field in ('required_content_types', 'optional_content_types'):
        check_enum_list(recipe.get(field), V.CONTENT_TYPE, field, 'recipe', errors)

    seq = recipe.get('section_sequence')
    if not isinstance(seq, list) or not seq:
        errors.append('recipe.section_sequence must be a non-empty list.')
    else:
        for i, step in enumerate(seq):
            if not isinstance(step, dict) or 'purpose' not in step:
                errors.append(f'recipe.section_sequence[{i}] must have a "purpose".')
    return errors


# --- section-purpose validation ----------------------------------------------

def validate_section_purpose(sp):
    """Validate a single section-purpose definition (brief §6.1)."""
    errors = require_keys(sp, ['purpose', 'allowed_components'], 'section_purpose')
    if not isinstance(sp, dict):
        return errors
    check_enum_list(sp.get('required_content_types'), V.CONTENT_TYPE,
                    'required_content_types', 'section_purpose', errors)
    check_enum_list(sp.get('preferred_persuasion_roles'), V.PERSUASION_ROLE,
                    'preferred_persuasion_roles', 'section_purpose', errors)
    if not isinstance(sp.get('allowed_components'), list) or not sp.get('allowed_components'):
        errors.append('section_purpose.allowed_components must be a non-empty list.')
    return errors
