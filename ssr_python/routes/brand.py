"""
Brand Kit & Content Library API — org-scoped reusable assets.

Content Library:
  GET    /api/content                  List content items (optional ?category= filter)
  POST   /api/content                  Create content item
  PATCH  /api/content/<id>             Update content item
  DELETE /api/content/<id>             Delete content item
  POST   /api/content/save-from-campaign   Save campaign messages to library
"""
import re
from datetime import datetime
from flask import Blueprint, g, jsonify, request, abort, current_app
from extensions import db
from models import ContentFolder, ContentItem, SectionItem, Organization, CampaignMessage, Campaign, Brand, Product
from guards import require_role
from cms_options import COLOR_PALETTE_OPTIONS, FONT_OPTIONS, THEME_CATEGORIES, THEME_OPTIONS
from campaign.content_type_catalog import (
    derive_content_from_slots,
    content_type_slot_schema,
    slots_from_content,
    serializable_content_families,
    serializable_content_types,
)
from campaign.offer_sync import build_campaign_content_item
from campaign.section_types import (
    is_valid_section_type,
    section_type_label,
    serializable_section_types,
    suggested_categories,
)
from brand_site_shell import ensure_brand_site
from site_composer import dump_composed_yaml, CompositionError
import json
import re

brand_bp = Blueprint('brand', __name__)


@brand_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


# =============================================================================
# Brand Options
# =============================================================================

def _slugify(value):
    slug = re.sub(r'[^a-z0-9]+', '-', (value or '').lower()).strip('-')
    return slug or 'brand'


def _unique_brand_slug(org_id, name, existing_id=None):
    base = _slugify(name)
    slug = base
    counter = 2
    while True:
        query = Brand.query.filter_by(org_id=org_id, slug=slug)
        if existing_id:
            query = query.filter(Brand.id != existing_id)
        if not query.first():
            return slug
        slug = f'{base}-{counter}'
        counter += 1


def _serialize_brand(brand):
    return brand.to_dict(include_counts=True)


def _refresh_brand_campaign_assets(brand):
    from campaign.section_rag import generate_brand_content_wording_prompt, generate_brand_section_style_prompt

    site_shell_config = _section_site_shell_config(brand, commit=False, regenerate=True)
    wording_prompt, wording_metadata = generate_brand_content_wording_prompt(
        brand,
        site_shell_config=site_shell_config,
        org_id=g.current_org_id,
    )
    brand.content_wording_prompt = wording_prompt
    brand.set_content_wording_prompt_metadata(wording_metadata)
    brand.content_wording_prompt_updated_at = datetime.utcnow()

    prompt, metadata = generate_brand_section_style_prompt(
        brand,
        site_shell_config=site_shell_config,
        org_id=g.current_org_id,
        content_wording_prompt=wording_prompt,
    )
    brand.section_style_prompt = prompt
    brand.set_section_style_prompt_metadata(metadata)
    brand.section_style_prompt_updated_at = datetime.utcnow()
    return site_shell_config


def _clean_social_links(data):
    if not isinstance(data, dict):
        return {}
    allowed = ('instagram', 'facebook', 'linkedin', 'x', 'youtube', 'tiktok', 'website')
    return {
        key: str(data.get(key) or '').strip()[:500]
        for key in allowed
        if str(data.get(key) or '').strip()
    }


def _text(value):
    if value is None:
        return ''
    if isinstance(value, list):
        return '\n'.join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _normalize_suggestion_text(value, limit=800):
    return _text(value).strip('"\'` ')[:limit]


def _normalize_suggestion_list(value, limit=6):
    if isinstance(value, list):
        parts = value
    else:
        parts = re.split(r'[\n;]+', _text(value))
    cleaned = []
    for part in parts:
        item = re.sub(r'^\s*[-*0-9.)]+\s*', '', _text(part)).strip()
        if item:
            cleaned.append(item[:240])
    return cleaned[:limit]


def _suggested_brand_strategy_from_model(data):
    colors = data.get('colors') if isinstance(data.get('colors'), dict) else {}
    fonts = data.get('fonts') if isinstance(data.get('fonts'), dict) else {}
    social_links = data.get('social_links') if isinstance(data.get('social_links'), dict) else {}
    strategy = data.get('strategy') if isinstance(data.get('strategy'), dict) else {}
    context = {
        'name': _normalize_suggestion_text(data.get('name'), 255),
        'tagline': _normalize_suggestion_text(data.get('tagline'), 500),
        'description': _normalize_suggestion_text(data.get('description'), 1600),
        'industry': _normalize_suggestion_text(data.get('industry'), 120),
        'website_url': _normalize_suggestion_text(data.get('website_url'), 500),
        'logo_url': _normalize_suggestion_text(data.get('logo_url'), 500),
        'tone': _normalize_suggestion_text(data.get('tone'), 80),
        'default_style': _normalize_suggestion_text(data.get('default_style'), 120),
        'voice_guidelines': _normalize_suggestion_text(data.get('voice_guidelines'), 1000),
        'colors': {key: _normalize_suggestion_text(value, 20) for key, value in colors.items()},
        'fonts': {key: _normalize_suggestion_text(value, 100) for key, value in fonts.items()},
        'social_links': _clean_social_links(social_links),
        'strategy': strategy,
    }
    system_prompt = (
        "You are a senior brand strategist inside a campaign CMS. "
        "Create practical AI strategy and voice guardrails from the user's current brand draft. "
        "Return ONLY a valid JSON object. Do not use markdown fences. "
        "Do not invent proof, guarantees, testimonials, statistics, pricing, compliance status, "
        "locations, awards, customer names, or unsupported claims."
    )
    user_prompt = (
        "Current brand draft:\n"
        f"{json.dumps(context, ensure_ascii=True, indent=2)}\n\n"
        "Return JSON with this exact top-level shape:\n"
        "{\n"
        '  "voice_guidelines": "durable voice guidance",\n'
        '  "strategy": {\n'
        '    "target_audience": "...",\n'
        '    "brand_promise": "...",\n'
        '    "positioning_statement": "...",\n'
        '    "differentiators": ["...", "..."],\n'
        '    "voice_examples": ["...", "..."],\n'
        '    "voice_anti_examples": ["...", "..."],\n'
        '    "forbidden_words": ["...", "..."],\n'
        '    "forbidden_claims": ["...", "..."],\n'
        '    "required_claims": ["...", "..."],\n'
        '    "compliance_notes": "...",\n'
        '    "image_style": "...",\n'
        '    "cta_style": "...",\n'
        '    "primary_market": "...",\n'
        '    "locale": "...",\n'
        '    "competitors": ["...", "..."]\n'
        "  }\n"
        "}\n\n"
        "Make every value concise and useful for downstream AI content generation. "
        "Use empty strings or empty arrays when the draft does not support a specific field."
    )

    from rag.agent.model_backend import ModelBackend
    raw = ModelBackend().generate(system_prompt, user_prompt)
    json_match = re.search(r'\{[\s\S]*\}', raw or '')
    if not json_match:
        raise ValueError('AI returned no JSON object')
    parsed = json.loads(json_match.group())
    if not isinstance(parsed, dict):
        raise ValueError('AI returned invalid JSON shape')

    parsed_strategy = parsed.get('strategy') if isinstance(parsed.get('strategy'), dict) else parsed
    normalized_strategy = {}
    for field in Brand.STRATEGY_TEXT_FIELDS:
        value = _normalize_suggestion_text(parsed_strategy.get(field), 800)
        if field == 'primary_market':
            value = value[:120]
        elif field == 'locale':
            value = value[:40]
        normalized_strategy[field] = value
    for field in Brand.STRATEGY_LIST_FIELDS:
        normalized_strategy[field] = _normalize_suggestion_list(parsed_strategy.get(field))

    voice_guidelines = _normalize_suggestion_text(parsed.get('voice_guidelines'), 1200)
    if not voice_guidelines and isinstance(parsed_strategy, dict):
        voice_guidelines = _normalize_suggestion_text(parsed_strategy.get('voice_guidelines'), 1200)

    has_suggestion = bool(voice_guidelines) or any(
        bool(value) for value in normalized_strategy.values()
    )
    if not has_suggestion:
        raise ValueError('AI returned no usable strategy suggestions')

    return {
        'voice_guidelines': voice_guidelines,
        'strategy': normalized_strategy,
        'source': 'ai',
    }


def _apply_brand_fields(brand, data):
    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return 'Brand name is required.'
        brand.name = name[:255]
        brand.slug = _unique_brand_slug(g.current_org_id, name, existing_id=brand.id)

    for field, limit in [
        ('tagline', 500),
        ('industry', 80),
        ('website_url', 500),
        ('logo_url', 500),
    ]:
        if field in data:
            setattr(brand, field, (data[field] or '').strip()[:limit] or None)

    if 'description' in data:
        brand.description = (data['description'] or '').strip() or None
    if 'voice_guidelines' in data:
        brand.voice_guidelines = (data['voice_guidelines'] or '').strip() or None

    if 'status' in data:
        status = (data['status'] or '').strip() or 'active'
        if status not in Brand.VALID_STATUSES:
            return f'Invalid status. Must be one of: {", ".join(sorted(Brand.VALID_STATUSES))}'
        brand.status = status

    if 'tone' in data:
        tone = (data['tone'] or '').strip() or None
        if tone and tone not in Brand.VALID_TONES:
            return f'Invalid tone. Must be one of: {", ".join(sorted(Brand.VALID_TONES))}'
        brand.tone = tone

    if 'default_style' in data:
        valid_styles = {item['value'] for item in THEME_OPTIONS}
        style = (data['default_style'] or '').strip() or None
        if style and style not in valid_styles:
            return 'Invalid theme selection.'
        brand.default_style = style

    if 'colors' in data and isinstance(data['colors'], dict):
        colors = data['colors']
        if 'primary' in colors:
            brand.color_primary = (colors['primary'] or '').strip()[:20] or None
        if 'secondary' in colors:
            brand.color_secondary = (colors['secondary'] or '').strip()[:20] or None
        if 'text' in colors:
            brand.color_text = (colors['text'] or '').strip()[:20] or None
        if 'accent' in colors:
            brand.color_accent = (colors['accent'] or '').strip()[:20] or None
        if 'background' in colors:
            brand.color_background = (colors['background'] or '').strip()[:20] or None

    if 'fonts' in data and isinstance(data['fonts'], dict):
        fonts = data['fonts']
        if 'heading' in fonts:
            brand.font_heading = (fonts['heading'] or '').strip()[:100] or None
        if 'body' in fonts:
            brand.font_body = (fonts['body'] or '').strip()[:100] or None

    if 'social_links' in data:
        if not isinstance(data['social_links'], dict):
            return 'Field "social_links" must be an object.'
        brand.set_social_links(_clean_social_links(data['social_links']))

    # --- Brand strategy fields (Phase 2) ---
    # Accept either a nested `strategy` object or flat top-level keys.
    strategy = data.get('strategy') if isinstance(data.get('strategy'), dict) else data

    for field in Brand.STRATEGY_TEXT_FIELDS:
        if field in strategy:
            value = (strategy[field] or '').strip() or None
            if field in ('primary_market', 'locale') and value:
                value = value[:120 if field == 'primary_market' else 40]
            setattr(brand, field, value)

    for field in Brand.STRATEGY_LIST_FIELDS:
        if field in strategy:
            value = strategy[field]
            if isinstance(value, str):
                # Allow comma/newline separated strings as a convenience
                value = [part for part in re.split(r'[\n,]', value)]
            if not isinstance(value, list):
                return f'Field "{field}" must be a list or comma-separated string.'
            brand.set_strategy_list(field, value)

    if 'is_default' in data:
        brand.is_default = bool(data['is_default'])

    brand.updated_at = datetime.utcnow()
    return None


def _ensure_single_default(default_brand):
    if not default_brand.is_default:
        return
    Brand.query.filter(
        Brand.org_id == default_brand.org_id,
        Brand.id != default_brand.id,
    ).update({'is_default': False})


@brand_bp.route('/api/brands/options', methods=['GET'])
def get_brand_options():
    return jsonify({
        'color_palettes': COLOR_PALETTE_OPTIONS,
        'fonts': FONT_OPTIONS,
        'theme_categories': THEME_CATEGORIES,
        'themes': THEME_OPTIONS,
        'tones': sorted(Brand.VALID_TONES),
    })


@brand_bp.route('/api/brands', methods=['GET'])
def list_brands():
    status = request.args.get('status')
    query = Brand.query.filter_by(org_id=g.current_org_id)
    if status and status in Brand.VALID_STATUSES:
        query = query.filter_by(status=status)
    else:
        query = query.filter(Brand.status != 'archived')
    brands = query.order_by(Brand.is_default.desc(), Brand.updated_at.desc()).all()
    return jsonify([_serialize_brand(b) for b in brands])


@brand_bp.route('/api/brands/suggest-strategy', methods=['POST'])
@require_role('editor')
def suggest_brand_strategy():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'JSON body required.'}), 400
    try:
        return jsonify(_suggested_brand_strategy_from_model(data))
    except Exception as exc:
        current_app.logger.info(f"Brand strategy suggestion failed: {exc}")
        return jsonify({'error': f'Brand strategy suggestion failed: {exc}'}), 502


@brand_bp.route('/api/brands', methods=['POST'])
@require_role('editor')
def create_brand():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Brand name is required.'}), 400

    is_first = Brand.query.filter_by(org_id=g.current_org_id).filter(Brand.status != 'archived').count() == 0
    brand = Brand(
        org_id=g.current_org_id,
        name=name[:255],
        slug=_unique_brand_slug(g.current_org_id, name),
        is_default=bool(data.get('is_default', is_first)),
    )
    db.session.add(brand)
    db.session.flush()

    error = _apply_brand_fields(brand, data)
    if error:
        db.session.rollback()
        return jsonify({'error': error}), 400
    _ensure_single_default(brand)
    try:
        _refresh_brand_campaign_assets(brand)
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': f'Brand campaign RAG preparation failed: {exc}'}), 500
    db.session.commit()
    return jsonify(_serialize_brand(brand)), 201


@brand_bp.route('/api/brands/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        abort(404)
    return jsonify(_serialize_brand(brand))


@brand_bp.route('/api/brands/<brand_id>', methods=['PATCH'])
@require_role('editor')
def update_brand(brand_id):
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        abort(404)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    error = _apply_brand_fields(brand, data)
    if error:
        return jsonify({'error': error}), 400
    _ensure_single_default(brand)
    try:
        _refresh_brand_campaign_assets(brand)
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': f'Brand campaign RAG preparation failed: {exc}'}), 500
    db.session.commit()
    return jsonify(_serialize_brand(brand))


@brand_bp.route('/api/brands/<brand_id>', methods=['DELETE'])
@require_role('editor')
def delete_brand(brand_id):
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        abort(404)
    brand.status = 'archived'
    brand.is_default = False
    brand.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


@brand_bp.route('/api/brands/<brand_id>/site', methods=['POST'])
@require_role('editor')
def create_or_refresh_brand_site(brand_id):
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        abort(404)

    data = request.get_json(silent=True) or {}
    regenerate = bool(data.get('regenerate'))
    site = ensure_brand_site(brand.id, org_id=g.current_org_id, regenerate=regenerate)
    if not site:
        abort(404)
    db.session.commit()

    homepage = next((page for page in site.source_pages if page.is_homepage), None)
    try:
        composed_yaml = dump_composed_yaml(site, homepage) if homepage else ''
    except CompositionError as exc:
        return jsonify({'error': f'Generated brand site shell is invalid: {exc}'}), 500

    return jsonify({
        'id': site.id,
        'brand_id': brand.id,
        'name': site.name,
        'slug': site.slug,
        'theme': site.theme,
        'homepage': {
            'id': homepage.id,
            'slug': homepage.slug,
            'title': homepage.title,
            'body_yaml_content': homepage.body_yaml_content,
        } if homepage else None,
        'shared_blocks': [
            {
                'id': block.id,
                'key': block.key,
                'label': block.label,
                'yaml_content': block.yaml_content,
            }
            for block in site.shared_blocks
        ],
        'composed_yaml': composed_yaml,
    }), 200


@brand_bp.route('/api/brands/<brand_id>/site/preview', methods=['GET'])
def preview_brand_site(brand_id):
    from extensions import TOKENS, COMPONENT_DEFAULTS
    from renderer import render_yaml_structure
    from site_composer import compose_page_yaml

    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        abort(404)

    site = ensure_brand_site(brand.id, org_id=g.current_org_id, regenerate=False)
    if not site:
        abort(404)
    db.session.commit()

    homepage = next((page for page in site.source_pages if page.is_homepage), None)
    if not homepage:
        return jsonify({'error': 'Brand site homepage was not found.'}), 404

    try:
        structure = compose_page_yaml(site, homepage)
        fragment = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    except Exception as exc:
        current_app.logger.error(f"Brand site preview render error for {brand_id}: {exc}")
        return jsonify({'error': 'Failed to render brand site preview.'}), 500

    theme = {}
    if site.theme:
        try:
            theme = json.loads(site.theme)
        except (TypeError, json.JSONDecodeError):
            theme = {}
    background = ((theme.get('colors') or {}).get('background')) or '#ffffff'
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<style>html,body{{margin:0;padding:0;background:{background};}}</style>'
        f'</head><body>{fragment}</body></html>'
    )
    return current_app.response_class(doc, mimetype='text/html')


# =============================================================================
# Content Library
# =============================================================================

def _serialize_content_item(item):
    return {
        'id': item.id,
        'brand_id': item.brand_id,
        'product_id': item.product_id,
        'folder_id': item.folder_id,
        'brand': item.brand.to_dict() if item.brand else None,
        'product': item.product.to_dict() if item.product else None,
        'folder': item.folder.to_dict() if item.folder else None,
        'category': item.category,
        'status': item.status,
        'source': item.source,
        'channel': item.channel,
        'title': item.title,
        'content': item.content,
        'slots': item.get_slots(),
        'tags': item.get_tags(),
        'source_campaign_id': item.source_campaign_id,
        'source_message_id': item.source_message_id,
        'tone': item.tone,
        'proof_source': item.proof_source,
        'proof_permission_status': item.proof_permission_status,
        'expires_at': item.expires_at.isoformat() if item.expires_at else None,
        'quality_score': item.quality_score,
        'ai_notes': item.ai_notes,
        'is_pinned': item.is_pinned,
        'created_at': item.created_at.isoformat() if item.created_at else None,
        'updated_at': item.updated_at.isoformat() if item.updated_at else None,
    }


def _serialize_content_folder(folder):
    return folder.to_dict()


def _content_ref_preview(item):
    """A lightweight content-item preview for section cards/editor lists."""
    return {
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'content': (item.content or '')[:160],
    }


def _serialize_section_item(item, *, ref_previews=None):
    """Serialize a SectionItem. `ref_previews` maps content_item id -> preview dict
    so the card can show the bound items (and which ones are missing/deleted).

    When `ref_previews` is None (single-item create/update), the previews are
    resolved here from the item's own refs. The list route passes a batch dict
    instead to avoid a per-section query."""
    ref_ids = item.get_content_refs()
    if ref_previews is None:
        rows = ContentItem.query.filter(
            ContentItem.org_id == item.org_id,
            ContentItem.id.in_(ref_ids),
        ).all() if ref_ids else []
        previews = {c.id: _content_ref_preview(c) for c in rows}
    else:
        previews = ref_previews
    items = [previews[rid] for rid in ref_ids if rid in previews]
    return {
        'id': item.id,
        'org_id': item.org_id,
        'brand_id': item.brand_id,
        'brand': item.brand.to_dict() if item.brand else None,
        'name': item.name,
        'description': item.description,
        'section_type': item.section_type or 'custom',
        'section_type_label': section_type_label(item.section_type),
        'suggested_categories': suggested_categories(item.section_type),
        'status': item.status,
        'content_refs': ref_ids,
        'yaml_content': item.yaml_content,
        'generation_metadata': item.get_generation_metadata(),
        'items': items,
        'item_count': len(ref_ids),
        'missing_count': len(ref_ids) - len(items),
        'tags': item.get_tags(),
        'is_pinned': item.is_pinned,
        'created_at': item.created_at.isoformat() if item.created_at else None,
        'updated_at': item.updated_at.isoformat() if item.updated_at else None,
    }


def _apply_section_fields(item, data, *, creating=False):
    if creating or 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return 'Section name is required.'
        item.name = name[:255]

    if 'description' in data:
        item.description = (data.get('description') or '').strip() or None

    if creating or 'section_type' in data:
        section_type = (data.get('section_type') or item.section_type or 'custom').strip()
        if not is_valid_section_type(section_type):
            return f'Invalid section_type. Must be one of: {", ".join(sorted(SectionItem.VALID_SECTION_TYPES))}'
        item.section_type = section_type

    if creating or 'brand_id' in data:
        brand_id = data.get('brand_id', item.brand_id) or None
        if brand_id:
            _, error = _validate_brand(brand_id)
            if error:
                return error
        item.brand_id = brand_id

    if creating or 'status' in data:
        status = (data.get('status') or item.status or 'draft').strip()
        if status not in SectionItem.VALID_STATUSES:
            return f'Invalid status. Must be one of: {", ".join(sorted(SectionItem.VALID_STATUSES))}'
        item.status = status

    if creating or 'content_refs' in data:
        raw_refs = data.get('content_refs') or []
        if not isinstance(raw_refs, list):
            return 'content_refs must be a list of content item ids.'
        ids = []
        for ref in raw_refs:
            if isinstance(ref, str):
                rid = ref.strip()
            elif isinstance(ref, dict):
                rid = str(ref.get('content_item_id') or ref.get('id') or '').strip()
            else:
                rid = ''
            if rid:
                ids.append(rid)
        if ids:
            # Validate every referenced content item belongs to this org.
            found = {
                c.id for c in ContentItem.query.filter(
                    ContentItem.org_id == g.current_org_id,
                    ContentItem.id.in_(ids),
                ).all()
            }
            unknown = [rid for rid in ids if rid not in found]
            if unknown:
                return f'Unknown content item(s): {", ".join(unknown)}'
        item.set_content_refs(ids)

    if 'yaml_content' in data:
        yaml_content = data.get('yaml_content')
        if yaml_content in (None, ''):
            item.yaml_content = None
        else:
            valid, error = _validate_section_body_yaml(str(yaml_content), 'yaml_content')
            if not valid:
                return error
            item.yaml_content = str(yaml_content)

    if 'generation_metadata' in data:
        payload, error = _normalize_json_payload(data.get('generation_metadata'), 'generation_metadata')
        if error:
            return error
        item.set_generation_metadata(payload)

    if 'tags' in data:
        item.set_tags(_normalize_tags(data.get('tags')))

    if 'is_pinned' in data:
        item.is_pinned = bool(data.get('is_pinned'))

    item.updated_at = datetime.utcnow()
    return None


def _parse_datetime(value, field_name):
    if value in (None, ''):
        return None, None
    if isinstance(value, datetime):
        return value, None
    text = str(value).strip()
    if not text:
        return None, None
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00')).replace(tzinfo=None), None
    except ValueError:
        return None, f'{field_name} must be an ISO date or datetime.'


def _validate_brand(brand_id):
    if not brand_id:
        return None, None
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        return None, 'Selected brand was not found.'
    return brand, None


def _validate_product(product_id):
    if not product_id:
        return None, None
    product = Product.query.filter_by(id=product_id, org_id=g.current_org_id).first()
    if not product:
        return None, 'Selected product was not found.'
    return product, None


def _validate_content_scope(brand_id, product_id):
    brand, error = _validate_brand(brand_id)
    if error:
        return None, None, error
    product, error = _validate_product(product_id)
    if error:
        return None, None, error
    if brand and product:
        product_brand_ids = set(product.to_dict().get('brand_ids') or [])
        if product_brand_ids and brand.id not in product_brand_ids:
            return None, None, 'Selected product is not tagged to the selected brand.'
    return brand, product, None


def _normalize_tags(value):
    if value in (None, ''):
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(',')
    return list(dict.fromkeys(str(item).strip()[:60] for item in items if str(item).strip()))


def _normalize_json_payload(value, field_name):
    if value in (None, ''):
        return {}, None
    if isinstance(value, dict):
        return value, None
    if isinstance(value, list):
        return {'items': value}, None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None, f'{field_name} must be valid JSON when provided as text.'
        if isinstance(parsed, dict):
            return parsed, None
        if isinstance(parsed, list):
            return {'items': parsed}, None
    return None, f'{field_name} must be an object, array, or JSON string.'


def _normalize_slots(value):
    if value in (None, ''):
        return {}, None
    if isinstance(value, dict):
        return value, None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None, 'slots must be valid JSON when provided as text.'
        if isinstance(parsed, dict):
            return parsed, None
    return None, 'slots must be an object.'


def _validate_content_folder(folder_id):
    if not folder_id:
        return None, None
    folder = ContentFolder.query.filter_by(id=folder_id, org_id=g.current_org_id).first()
    if not folder:
        return None, 'Selected folder was not found.'
    return folder, None


def _validate_slots(category, slots):
    slots = slots or {}
    missing = []
    for slot in content_type_slot_schema(category):
        key = slot.get('key')
        if slot.get('required') and not str(slots.get(key) or '').strip():
            missing.append(slot.get('label') or key)
    if missing:
        return f'Missing required {category} field(s): {", ".join(missing)}'
    return None


def _validate_component_list_yaml(yaml_content, field_name='yaml_content'):
    import yaml as yaml_lib
    try:
        parsed = yaml_lib.safe_load(yaml_content or '[]')
    except yaml_lib.YAMLError as exc:
        return False, f'{field_name} is not valid YAML: {exc}'
    if parsed is None:
        parsed = []
    if not isinstance(parsed, list):
        return False, f'{field_name} must be a YAML list of components.'
    return True, None


def _validate_section_body_yaml(yaml_content, field_name='yaml_content'):
    valid, error = _validate_component_list_yaml(yaml_content, field_name)
    if not valid:
        return valid, error
    parsed = _parse_component_list_yaml(yaml_content, field_name)
    wrappers = _find_component_names(parsed, {'site', 'page'})
    if wrappers:
        return False, f'{field_name} must be a body-only component list; remove {", ".join(wrappers)} wrapper.'
    return True, None


def _find_component_names(node, names):
    found = []
    if isinstance(node, list):
        for item in node:
            found.extend(_find_component_names(item, names))
    elif isinstance(node, dict):
        name = node.get('name')
        if name in names:
            found.append(name)
        for key in ('components', 'items', 'tabs', 'slides', 'columns'):
            found.extend(_find_component_names(node.get(key), names))
    return found


def _parse_component_list_yaml(yaml_content, field_name='yaml_content'):
    import yaml as yaml_lib
    try:
        parsed = yaml_lib.safe_load(yaml_content or '[]')
    except yaml_lib.YAMLError as exc:
        raise ValueError(f'{field_name} is not valid YAML: {exc}') from exc
    if parsed is None:
        return []
    if not isinstance(parsed, list):
        raise ValueError(f'{field_name} must be a YAML list of components.')
    return parsed


def _load_ordered_content_items(ref_ids):
    if not ref_ids:
        return []
    rows = {
        c.id: c for c in ContentItem.query.filter(
            ContentItem.org_id == g.current_org_id,
            ContentItem.id.in_(ref_ids),
        ).all()
    }
    return [rows[rid] for rid in ref_ids if rid in rows]


def _compile_section_yaml(item):
    return _compile_section_yaml_with_mode(item, generation_mode='agent')


def _compile_section_yaml_with_mode(item, generation_mode='agent'):
    from campaign.content_to_section import compile_content_to_section_yaml

    items = _load_ordered_content_items(item.get_content_refs())
    brand = _resolve_section_brand(item)
    site_shell_config = _section_site_shell_config(brand, commit=True)
    yaml_content, metadata = compile_content_to_section_yaml(
        item.section_type,
        items,
        brand=brand,
        site_shell_config=site_shell_config,
        generation_mode=generation_mode,
        section_metadata={
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'section_type': item.section_type,
            'status': item.status,
        },
    )
    valid, error = _validate_section_body_yaml(yaml_content)
    if not valid:
        raise ValueError(error)
    _smoke_render_section_body_yaml(yaml_content, item, site_shell_config.get('theme') or {})
    metadata = dict(metadata or {})
    metadata.setdefault('render_wrapper', {
        'source': 'brand_site_shell',
        'uses': ['theme.colors', 'theme.fonts'],
    })
    if site_shell_config.get('site_id'):
        metadata['render_wrapper']['site_id'] = site_shell_config.get('site_id')
    if brand:
        metadata['render_wrapper']['brand_id'] = brand.id
    item.yaml_content = yaml_content
    item.set_generation_metadata(metadata)
    return item


def _resolve_section_brand(item):
    brand = item.brand
    if brand is None:
        brand = Brand.query.filter_by(org_id=g.current_org_id, is_default=True).first()
    return brand


def _section_site_shell_config(brand, *, commit=False, regenerate=False):
    from campaign.theme import brand_to_theme

    if brand is None:
        return {'theme': brand_to_theme(None)}

    site = ensure_brand_site(brand.id, org_id=g.current_org_id, regenerate=regenerate)
    if commit:
        db.session.commit()
    theme = None
    if site and site.theme:
        try:
            theme = json.loads(site.theme)
        except (TypeError, json.JSONDecodeError):
            theme = None
    if not isinstance(theme, dict) or not theme.get('colors') or not theme.get('fonts'):
        theme = brand_to_theme(brand)
    return {
        'source': 'brand_site_shell',
        'brand_id': brand.id,
        'site_id': site.id if site else None,
        'theme': {
            'colors': theme.get('colors') or {},
            'fonts': theme.get('fonts') or {},
        },
    }


def _smoke_render_section_body_yaml(yaml_content, item, theme):
    from extensions import TOKENS, COMPONENT_DEFAULTS
    from renderer import render_yaml_structure

    structure = _build_section_body_preview_structure(
        yaml_content,
        theme,
        title=item.name or 'Section preview',
    )
    render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)


def _build_section_body_preview_structure(yaml_content, theme, title='Section preview'):
    components = _parse_component_list_yaml(yaml_content or '[]', 'section yaml_content')
    if not components:
        from campaign.section_builders import _paragraph, _row
        section = _row([_paragraph('This section has no content yet. Add content items to see a preview.')])
        components = [section]
    background = (theme.get('colors') or {}).get('background', '#ffffff')
    return [{
        'name': 'site',
        'properties': {'theme': theme},
        'components': [{
            'name': 'page',
            'slug': 'section-preview',
            'title': title,
            'properties': {
                'appearance': {
                    'background': {'color': background, 'opacity': 100}
                }
            },
            'components': components,
        }],
    }]


def _build_section_yaml_preview_structure(item, theme):
    return _build_section_body_preview_structure(
        item.yaml_content or '[]',
        theme,
        title=item.name or 'Section preview',
    )


def _apply_content_fields(item, data, *, creating=False):
    if creating or 'category' in data:
        category = (data.get('category') or '').strip()
        if not category or category not in ContentItem.VALID_CATEGORIES:
            return f'Invalid category. Must be one of: {", ".join(sorted(ContentItem.VALID_CATEGORIES))}'
        item.category = category

    slots = None
    if 'slots' in data:
        slots, error = _normalize_slots(data.get('slots'))
        if error:
            return error
    else:
        slots = item.get_slots()

    slot_error = _validate_slots(item.category, slots)
    if slot_error:
        return slot_error

    if creating or 'slots' in data or 'category' in data:
        content = derive_content_from_slots(item.category, slots)
        if not content:
            return 'Content is required.'
        item.content = content

    if 'title' in data:
        item.title = (data.get('title') or '').strip()[:255] or None

    brand_id = data.get('brand_id', item.brand_id) or None
    product_id = data.get('product_id', item.product_id) or None
    if creating or 'brand_id' in data or 'product_id' in data:
        _, _, error = _validate_content_scope(brand_id, product_id)
        if error:
            return error
        item.brand_id = brand_id
        item.product_id = product_id

    if creating or 'folder_id' in data:
        folder_id = data.get('folder_id', item.folder_id) or None
        _, error = _validate_content_folder(folder_id)
        if error:
            return error
        item.folder_id = folder_id

    if creating or 'status' in data:
        source = (data.get('source') or item.source or 'manual').strip()
        default_status = 'draft' if source == 'ai' else 'approved'
        status = (data.get('status') or item.status or default_status).strip()
        if status not in ContentItem.VALID_STATUSES:
            return f'Invalid status. Must be one of: {", ".join(sorted(ContentItem.VALID_STATUSES))}'
        item.status = status

    if creating or 'source' in data:
        source = (data.get('source') or item.source or 'manual').strip()
        if source not in ContentItem.VALID_SOURCES:
            return f'Invalid source. Must be one of: {", ".join(sorted(ContentItem.VALID_SOURCES))}'
        item.source = source

    if creating or 'channel' in data:
        channel = (data.get('channel') or item.channel or 'general').strip()
        if channel not in ContentItem.VALID_CHANNELS:
            return f'Invalid channel. Must be one of: {", ".join(sorted(ContentItem.VALID_CHANNELS))}'
        item.channel = channel

    if creating or 'slots' in data:
        item.set_slots(slots)

    if 'tags' in data:
        item.set_tags(_normalize_tags(data.get('tags')))

    if 'source_campaign_id' in data:
        item.source_campaign_id = data.get('source_campaign_id') or None

    if 'source_message_id' in data:
        item.source_message_id = data.get('source_message_id') or None

    if 'tone' in data:
        item.tone = (data.get('tone') or '').strip()[:30] or None

    if 'proof_source' in data:
        item.proof_source = (data.get('proof_source') or '').strip()[:500] or None

    if 'proof_permission_status' in data:
        permission_status = (data.get('proof_permission_status') or '').strip() or None
        if permission_status and permission_status not in ContentItem.VALID_PERMISSION_STATUSES:
            return f'Invalid proof_permission_status. Must be one of: {", ".join(sorted(ContentItem.VALID_PERMISSION_STATUSES))}'
        item.proof_permission_status = permission_status

    if 'expires_at' in data:
        expires_at, error = _parse_datetime(data.get('expires_at'), 'expires_at')
        if error:
            return error
        item.expires_at = expires_at

    if 'quality_score' in data:
        raw_score = data.get('quality_score')
        if raw_score in (None, ''):
            item.quality_score = None
        else:
            try:
                score = int(raw_score)
            except (TypeError, ValueError):
                return 'quality_score must be a number from 0 to 100.'
            if score < 0 or score > 100:
                return 'quality_score must be between 0 and 100.'
            item.quality_score = score

    if 'ai_notes' in data:
        item.ai_notes = (data.get('ai_notes') or '').strip() or None

    if 'is_pinned' in data:
        item.is_pinned = bool(data.get('is_pinned'))

    item.updated_at = datetime.utcnow()
    return None


@brand_bp.route('/api/content/options', methods=['GET'])
def content_options():
    return jsonify({
        'content_types': serializable_content_types(),
        'content_type_families': serializable_content_families(),
        'statuses': sorted(ContentItem.VALID_STATUSES),
        'sources': sorted(ContentItem.VALID_SOURCES),
        'channels': sorted(ContentItem.VALID_CHANNELS),
        'permission_statuses': sorted(ContentItem.VALID_PERMISSION_STATUSES),
    })


@brand_bp.route('/api/content/folders', methods=['GET'])
def list_content_folders():
    folders = ContentFolder.query.filter_by(org_id=g.current_org_id).order_by(
        ContentFolder.sort_order.asc(),
        ContentFolder.name.asc(),
    ).all()
    return jsonify([_serialize_content_folder(folder) for folder in folders])


@brand_bp.route('/api/content/folders', methods=['POST'])
@require_role('editor')
def create_content_folder():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Folder name is required.'}), 400
    try:
        sort_order = int(data.get('sort_order') or 0)
    except (TypeError, ValueError):
        return jsonify({'error': 'sort_order must be a number.'}), 400
    folder = ContentFolder(
        org_id=g.current_org_id,
        name=name[:255],
        description=(data.get('description') or '').strip() or None,
        sort_order=sort_order,
    )
    db.session.add(folder)
    db.session.commit()
    return jsonify(_serialize_content_folder(folder)), 201


@brand_bp.route('/api/content/folders/<folder_id>', methods=['PATCH'])
@require_role('editor')
def update_content_folder(folder_id):
    folder = ContentFolder.query.filter_by(id=folder_id, org_id=g.current_org_id).first()
    if not folder:
        abort(404)
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Folder name is required.'}), 400
        folder.name = name[:255]
    if 'description' in data:
        folder.description = (data.get('description') or '').strip() or None
    if 'sort_order' in data:
        try:
            folder.sort_order = int(data.get('sort_order') or 0)
        except (TypeError, ValueError):
            return jsonify({'error': 'sort_order must be a number.'}), 400
    folder.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_content_folder(folder))


@brand_bp.route('/api/content/folders/<folder_id>', methods=['DELETE'])
@require_role('editor')
def delete_content_folder(folder_id):
    folder = ContentFolder.query.filter_by(id=folder_id, org_id=g.current_org_id).first()
    if not folder:
        abort(404)
    ContentItem.query.filter_by(org_id=g.current_org_id, folder_id=folder.id).update({'folder_id': None})
    db.session.delete(folder)
    db.session.commit()
    return jsonify({'ok': True})


@brand_bp.route('/api/content', methods=['GET'])
def list_content():
    """List content library items with marketer-facing filters."""
    query = ContentItem.query.filter_by(org_id=g.current_org_id)

    category = request.args.get('category')
    if category and category in ContentItem.VALID_CATEGORIES:
        query = query.filter_by(category=category)

    status = request.args.get('status')
    if status and status in ContentItem.VALID_STATUSES:
        query = query.filter_by(status=status)

    source = request.args.get('source')
    if source and source in ContentItem.VALID_SOURCES:
        query = query.filter_by(source=source)

    channel = request.args.get('channel')
    if channel and channel in ContentItem.VALID_CHANNELS:
        query = query.filter_by(channel=channel)

    brand_id = request.args.get('brand_id')
    if brand_id == 'shared':
        query = query.filter(ContentItem.brand_id.is_(None))
    elif brand_id:
        query = query.filter_by(brand_id=brand_id)

    product_id = request.args.get('product_id')
    if product_id == 'none':
        query = query.filter(ContentItem.product_id.is_(None))
    elif product_id:
        query = query.filter_by(product_id=product_id)

    folder_id = request.args.get('folder_id')
    if folder_id == 'unfiled':
        query = query.filter(ContentItem.folder_id.is_(None))
    elif folder_id:
        query = query.filter_by(folder_id=folder_id)

    search = (request.args.get('q') or '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(
            ContentItem.title.ilike(like),
            ContentItem.content.ilike(like),
            ContentItem.proof_source.ilike(like),
        ))

    items = query.order_by(ContentItem.is_pinned.desc(), ContentItem.updated_at.desc()).all()
    return jsonify([_serialize_content_item(i) for i in items])


@brand_bp.route('/api/content', methods=['POST'])
@require_role('editor')
def create_content():
    """Create a content library item."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    item = ContentItem(org_id=g.current_org_id)
    error = _apply_content_fields(item, data, creating=True)
    if error:
        return jsonify({'error': error}), 400

    db.session.add(item)
    db.session.commit()
    return jsonify(_serialize_content_item(item)), 201


@brand_bp.route('/api/content/<item_id>', methods=['PATCH'])
@require_role('editor')
def update_content(item_id):
    """Update a content library item."""
    item = ContentItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    error = _apply_content_fields(item, data)
    if error:
        return jsonify({'error': error}), 400

    db.session.commit()
    return jsonify(_serialize_content_item(item))


@brand_bp.route('/api/content/<item_id>', methods=['DELETE'])
@require_role('editor')
def delete_content(item_id):
    """Delete a content library item."""
    item = ContentItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})


@brand_bp.route('/api/content/<item_id>/preview', methods=['GET'])
def preview_content(item_id):
    """Render one content item to standalone HTML using its brand's theme.

    Always renders on demand, so it reflects the current brand colors/fonts.
    Returns text/html (for an iframe) or a JSON error.
    """
    from flask import current_app
    from extensions import TOKENS, COMPONENT_DEFAULTS
    from renderer import render_yaml_structure
    from campaign.theme import brand_to_theme
    from campaign.content_preview import build_preview_structure

    item = ContentItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    # Resolve brand: the item's brand, else the org's default brand, else none.
    brand = item.brand
    if brand is None:
        brand = Brand.query.filter_by(org_id=g.current_org_id, is_default=True).first()

    theme = brand_to_theme(brand)

    try:
        structure = build_preview_structure(item, theme)
        fragment = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    except Exception as e:
        current_app.logger.error(f"Content preview render error for {item_id}: {e}")
        return jsonify({'error': 'Failed to render content preview.'}), 500

    background = (theme.get('colors') or {}).get('background', '#ffffff')
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<style>html,body{{margin:0;padding:0;background:{background};}}</style>'
        f'</head><body>{fragment}</body></html>'
    )
    return current_app.response_class(doc, mimetype='text/html')


# =============================================================================
# Sections (live-binding compositions of content items)
# =============================================================================

@brand_bp.route('/api/sections/options', methods=['GET'])
def section_options():
    return jsonify({'statuses': sorted(SectionItem.VALID_STATUSES)})


@brand_bp.route('/api/sections/types', methods=['GET'])
def section_types():
    return jsonify(serializable_section_types())


@brand_bp.route('/api/sections', methods=['GET'])
def list_sections():
    """List section items with optional brand/status/search filters."""
    query = SectionItem.query.filter_by(org_id=g.current_org_id)

    status = request.args.get('status')
    if status and status in SectionItem.VALID_STATUSES:
        query = query.filter_by(status=status)

    brand_id = request.args.get('brand_id')
    if brand_id == 'shared':
        query = query.filter(SectionItem.brand_id.is_(None))
    elif brand_id:
        query = query.filter_by(brand_id=brand_id)

    search = (request.args.get('q') or '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(
            SectionItem.name.ilike(like),
            SectionItem.description.ilike(like),
        ))

    sections = query.order_by(
        SectionItem.is_pinned.desc(), SectionItem.updated_at.desc()
    ).all()

    # Batch-load referenced content items once, for card previews.
    all_ref_ids = {rid for s in sections for rid in s.get_content_refs()}
    previews = {}
    if all_ref_ids:
        rows = ContentItem.query.filter(
            ContentItem.org_id == g.current_org_id,
            ContentItem.id.in_(all_ref_ids),
        ).all()
        previews = {c.id: _content_ref_preview(c) for c in rows}

    return jsonify([_serialize_section_item(s, ref_previews=previews) for s in sections])


@brand_bp.route('/api/sections', methods=['POST'])
@require_role('editor')
def create_section():
    """Create a section (ordered composition of content items)."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    item = SectionItem(org_id=g.current_org_id)
    error = _apply_section_fields(item, data, creating=True)
    if error:
        return jsonify({'error': error}), 400

    db.session.add(item)
    db.session.commit()
    return jsonify(_serialize_section_item(item)), 201


@brand_bp.route('/api/sections/from-content', methods=['POST'])
@require_role('editor')
def create_section_from_content():
    """Create a YAML-backed section from selected content items."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    item = SectionItem(org_id=g.current_org_id)
    error = _apply_section_fields(item, data, creating=True)
    if error:
        return jsonify({'error': error}), 400
    if not item.get_content_refs():
        return jsonify({'error': 'content_refs must include at least one content item.'}), 400

    generation_mode = (data.get('generation_mode') or 'agent').strip()
    if generation_mode != 'agent':
        return jsonify({'error': 'generation_mode must be agent.'}), 400

    try:
        _compile_section_yaml_with_mode(item, generation_mode=generation_mode)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    db.session.add(item)
    db.session.commit()
    return jsonify({'section': _serialize_section_item(item)}), 201


@brand_bp.route('/api/sections/<item_id>', methods=['PATCH'])
@require_role('editor')
def update_section(item_id):
    """Update a section."""
    item = SectionItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    error = _apply_section_fields(item, data)
    if error:
        return jsonify({'error': error}), 400

    db.session.commit()
    return jsonify(_serialize_section_item(item))


@brand_bp.route('/api/sections/<item_id>/regenerate-yaml', methods=['POST'])
@require_role('editor')
def regenerate_section_yaml(item_id):
    """Rebuild a section YAML artifact from current content references."""
    item = SectionItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    data = request.get_json(silent=True) or {}
    generation_mode = (data.get('generation_mode') or 'agent').strip()
    if generation_mode != 'agent':
        return jsonify({'error': 'generation_mode must be agent.'}), 400

    try:
        _compile_section_yaml_with_mode(item, generation_mode=generation_mode)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'section': _serialize_section_item(item)})


@brand_bp.route('/api/sections/<item_id>', methods=['DELETE'])
@require_role('editor')
def delete_section(item_id):
    """Delete a section."""
    item = SectionItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    db.session.delete(item)
    db.session.commit()
    return jsonify({'ok': True})


@brand_bp.route('/api/sections/<item_id>/preview', methods=['GET'])
def preview_section(item_id):
    """Render a section to standalone HTML from its bound content items + brand theme.

    Renders on demand, so it reflects current content values and brand colors/fonts
    (live binding). Deleted referenced items are skipped, not fatal.
    """
    from flask import current_app
    from extensions import TOKENS, COMPONENT_DEFAULTS
    from renderer import render_yaml_structure
    from campaign.content_preview import build_section_preview_structure

    item = SectionItem.query.filter_by(id=item_id, org_id=g.current_org_id).first()
    if not item:
        abort(404)

    brand = _resolve_section_brand(item)
    site_shell_config = _section_site_shell_config(brand)
    theme = site_shell_config.get('theme') or {}

    try:
        if item.yaml_content:
            structure = _build_section_yaml_preview_structure(item, theme)
        else:
            items = _load_ordered_content_items(item.get_content_refs())
            structure = build_section_preview_structure(items, theme, title=item.name or 'Section preview')
        fragment = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    except Exception as e:
        current_app.logger.error(f"Section preview render error for {item_id}: {e}")
        return jsonify({'error': 'Failed to render section preview.'}), 500

    background = (theme.get('colors') or {}).get('background', '#ffffff')
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<style>html,body{{margin:0;padding:0;background:{background};}}</style>'
        f'</head><body>{fragment}</body></html>'
    )
    return current_app.response_class(doc, mimetype='text/html')


@brand_bp.route('/api/content/save-from-campaign', methods=['POST'])
@require_role('editor')
def save_from_campaign():
    """Save kept campaign messages to the content library.

    Request JSON: { campaign_id, message_ids?: [str] }
    If message_ids not provided, saves all kept messages from the campaign.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    campaign_id = data.get('campaign_id')
    if not campaign_id:
        return jsonify({'error': 'campaign_id is required.'}), 400

    campaign = Campaign.query.filter_by(id=campaign_id, org_id=g.current_org_id).first()
    if not campaign:
        abort(404)

    message_ids = data.get('message_ids')
    query = CampaignMessage.query.filter_by(campaign_id=campaign.id)

    if message_ids:
        query = query.filter(CampaignMessage.id.in_(message_ids))
    else:
        query = query.filter_by(is_kept=True)

    messages = query.all()
    if not messages:
        return jsonify({'error': 'No messages found to save.'}), 400

    category_map = {
        'headline': 'headline',
        'subheadline': 'subheadline',
        'benefit': 'benefit',
        'proof': 'proof',
        'testimonial': 'testimonial',
        'cta': 'cta',
        'faq': 'faq',
        'objection': 'objection',
    }

    selected_product_ids = [
        cp.product_id for cp in (campaign.campaign_products or [])
        if cp.product_id
    ]
    product_id = selected_product_ids[0] if len(selected_product_ids) == 1 else None

    saved = []
    for msg in messages:
        category = category_map.get(msg.category, 'boilerplate')
        slots = slots_from_content(category, msg.content)
        content = derive_content_from_slots(category, slots)
        existing = ContentItem.query.filter_by(
            org_id=g.current_org_id,
            content=content,
            category=category,
            brand_id=campaign.brand_id,
            product_id=product_id,
        ).first()
        if existing:
            continue

        item = build_campaign_content_item(
            campaign, category, content, slots,
            source_message_id=msg.id,
            product_id=product_id,
            is_pinned=bool(data.get('pin_saved', False)),
        )
        db.session.add(item)
        saved.append(item)

    db.session.commit()
    return jsonify({
        'ok': True,
        'saved_count': len(saved),
        'items': [_serialize_content_item(i) for i in saved],
    })
