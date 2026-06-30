from flask import Blueprint, request, jsonify, current_app, session, abort, g
import os
import hmac
import json
import re
import threading
import traceback
from functools import wraps
from urllib.parse import urlparse

from models import Brand, ContentItem, IndustryConfig, MediaAsset, Organization
from extensions import db
from exceptions import CancelledError
from guards import require_role
from campaign.content_type_catalog import content_type_slot_schema, derive_content_from_slots, slots_from_content
from campaign.section_types import (
    is_valid_section_type,
    section_type_for_category,
    section_type_label,
    suggested_categories,
)

chat_bp = Blueprint('chat', __name__)


@chat_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


def _request_origin_matches_app():
    expected = request.host_url.rstrip('/')
    source = request.headers.get('Origin') or request.headers.get('Referer')
    if not source:
        return False
    parsed = urlparse(source)
    return f'{parsed.scheme}://{parsed.netloc}' == expected


def require_app_ai_request(f):
    """Require an app-rendered page token before allowing AI spend endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        expected_token = session.get('ai_request_token') or ''
        provided_token = request.headers.get('X-AI-Request-Token') or ''
        requested_by = request.headers.get('X-Requested-With') or ''
        if requested_by != 'SwiftSitesApp':
            abort(403)
        if not expected_token or not hmac.compare_digest(expected_token, provided_token):
            abort(403)
        if not _request_origin_matches_app():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _clean_filename(name):
    """Convert filename to readable alt text: 'hero-banner.jpg' → 'hero banner'"""
    if not name:
        return ''
    stem = os.path.splitext(name)[0]
    return stem.replace('-', ' ').replace('_', ' ')


def _load_org_media_images(limit=40):
    assets = MediaAsset.query.filter_by(org_id=g.current_org_id) \
        .order_by(MediaAsset.created_at.desc()) \
        .limit(limit) \
        .all()
    return [
        {
            'id': asset.id,
            'url': asset.url or (f'/uploads/{asset.storage_path}' if asset.storage_path else ''),
            'altText': asset.alt_text or _clean_filename(asset.original_name) or asset.filename,
            'orientation': asset.orientation or 'unknown',
            'photographer': asset.photographer or '',
            'source': asset.source or '',
            'sourceUrl': asset.source_url or '',
            'license': asset.license_label or '',
            'tags': asset.get_tags(),
            'width': asset.width,
            'height': asset.height,
        }
        for asset in assets
        if asset.url or asset.storage_path
    ]


# Shared progress status — updated by the chat endpoint, polled by the frontend
_chat_status = {"message": "", "active": False}

# Cancellation event for the active chat request
_active_cancel_event: threading.Event | None = None


BRAND_ENHANCE_FIELDS = {
    'name': {'label': 'Brand name', 'hint': 'A concise, memorable brand name.'},
    'tagline': {'label': 'Tagline', 'hint': 'A short one-line promise for the brand.'},
    'description': {
        'label': 'Brand description',
        'hint': 'A factual overview of what the brand offers, who it serves, and why it matters.',
        'limit': 1200,
    },
    'industry': {'label': 'Industry', 'hint': 'The most accurate business category.'},
    'tone': {'label': 'Tone of voice', 'choice': 'tones'},
    'default_style': {'label': 'Default theme', 'choice': 'themes'},
    'font_heading': {'label': 'Heading font', 'choice': 'fonts'},
    'font_body': {'label': 'Body font', 'choice': 'fonts'},
    'voice_guidelines': {
        'label': 'Voice guidelines',
        'hint': 'Durable voice rules for generated copy, including tone, audience, phrasing, and constraints.',
        'limit': 1400,
    },
    'target_audience': {'label': 'Target audience', 'hint': 'The roles, needs, and context the brand speaks to.'},
    'brand_promise': {'label': 'Brand promise', 'hint': 'The reliable value the brand delivers.'},
    'differentiators': {'label': 'Differentiators', 'list': True},
    'positioning_statement': {'label': 'Positioning statement'},
    'voice_examples': {'label': 'Voice examples', 'list': True},
    'voice_anti_examples': {'label': 'Voice anti-examples', 'list': True},
    'forbidden_words': {'label': 'Forbidden words', 'list': True},
    'forbidden_claims': {'label': 'Forbidden claims', 'list': True},
    'required_claims': {'label': 'Required claims', 'list': True},
    'compliance_notes': {'label': 'Compliance notes'},
    'image_style': {'label': 'Image style'},
    'cta_style': {'label': 'CTA style'},
    'primary_market': {'label': 'Primary market'},
    'locale': {'label': 'Locale'},
    'competitors': {'label': 'Competitors', 'list': True},
}


# Campaign Studio free-text fields that support per-field AI enhancement.
# Keys match the client-side data-field paths sent in current_content.
CAMPAIGN_ENHANCE_FIELDS = {
    'brief.product_or_service': {
        'label': 'Product or service',
        'hint': 'What is being promoted — a clear, specific name or description.',
    },
    'brief.description': {
        'label': 'Short description',
        'hint': 'A concise summary of what it is and why it matters to the audience.',
    },
    'brief.target_audience': {
        'label': 'Target audience',
        'hint': 'Who the campaign is for — roles, needs, and context.',
    },
    'brief.problem_or_desire': {
        'label': 'Problem or desire',
        'hint': 'The core problem solved or desire fulfilled for the audience.',
    },
    'brief.location_or_segment': {
        'label': 'Location or segment',
        'hint': 'The geographic market or customer segment being targeted.',
    },
    'offer.offer': {
        'label': 'Offer',
        'hint': 'The specific offer or value proposition presented to the audience.',
    },
    'offer.primary_cta': {
        'label': 'Primary call to action',
        'hint': 'A short, action-first primary button label.',
    },
    'offer.secondary_cta': {
        'label': 'Secondary call to action',
        'hint': 'A short, lower-commitment secondary button label.',
    },
}


def _make_progress_fn(cancel_event: threading.Event):
    """Create a progress callback that raises CancelledError if cancelled."""
    def progress_fn(msg):
        if cancel_event.is_set():
            raise CancelledError("Request cancelled by user")
        _chat_status["message"] = msg
    return progress_fn


def _brand_choice_sets():
    from models import Brand
    from cms_options import FONT_OPTIONS, THEME_OPTIONS

    return {
        'tones': sorted(Brand.VALID_TONES),
        'themes': [item['value'] for item in THEME_OPTIONS],
        'fonts': [item['value'] for item in FONT_OPTIONS],
    }


def _text(value):
    if value is None:
        return ''
    if isinstance(value, list):
        return '\n'.join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _pick_choice(value, choices, fallback):
    if value in choices:
        return value
    normalized = re.sub(r'[^a-z0-9]+', '_', _text(value).lower()).strip('_')
    for choice in choices:
        if normalized == re.sub(r'[^a-z0-9]+', '_', choice.lower()).strip('_'):
            return choice
    return fallback if fallback in choices else (choices[0] if choices else '')


def _brand_fallback_value(field_key, content):
    choices = _brand_choice_sets()
    name = _text(content.get('name')) or 'Your Brand'
    industry = _text(content.get('industry')) or 'marketing'
    audience = _text(content.get('target_audience')) or f'{industry.title()} teams and business owners'
    promise = _text(content.get('brand_promise')) or 'create clear, on-brand marketing content faster'

    industry_l = industry.lower()
    if field_key == 'name':
        return name
    if field_key == 'tagline':
        return f'On-brand campaigns, ready faster.'
    if field_key == 'description':
        description = _text(content.get('description'))
        if description:
            return description
        tagline = _text(content.get('tagline'))
        parts = [f'{name} is a {industry.lower()} brand for {audience}.']
        if tagline:
            parts.append(tagline)
        if promise:
            parts.append(f'It helps customers {promise}.')
        return ' '.join(parts)
    if field_key == 'industry':
        return industry if industry != 'marketing' else 'Marketing Technology'
    if field_key == 'tone':
        if any(word in industry_l for word in ('finance', 'legal', 'health', 'medical')):
            return _pick_choice('trustworthy', choices['tones'], 'confident')
        if any(word in industry_l for word in ('education', 'course', 'training')):
            return _pick_choice('educational', choices['tones'], 'confident')
        if any(word in industry_l for word in ('consumer', 'retail', 'ecommerce', 'fashion')):
            return _pick_choice('aspirational', choices['tones'], 'confident')
        return _pick_choice(_text(content.get('tone')) or 'confident', choices['tones'], 'confident')
    if field_key == 'default_style':
        style = 'modern_minimalist'
        if any(word in industry_l for word in ('saas', 'software', 'ai', 'technology')):
            style = 'clean_b2b_saas'
        elif any(word in industry_l for word in ('shop', 'retail', 'ecommerce', 'fashion')):
            style = 'premium_ecommerce'
        elif any(word in industry_l for word in ('health', 'wellness', 'medical')):
            style = 'health_wellness'
        elif any(word in industry_l for word in ('finance', 'fintech', 'bank')):
            style = 'fintech_trust'
        return _pick_choice(_text(content.get('default_style')) or style, choices['themes'], style)
    if field_key == 'font_heading':
        font = 'Inter'
        if any(word in industry_l for word in ('luxury', 'fashion', 'editorial')):
            font = 'Playfair Display'
        elif any(word in industry_l for word in ('saas', 'software', 'ai', 'technology')):
            font = 'Space Grotesk'
        return _pick_choice(_text(content.get('font_heading')) or font, choices['fonts'], font)
    if field_key == 'font_body':
        return _pick_choice(_text(content.get('font_body')) or 'Inter', choices['fonts'], 'Inter')
    if field_key == 'voice_guidelines':
        voice_guidelines = _text(content.get('voice_guidelines'))
        if voice_guidelines:
            return voice_guidelines
        tone = _text(content.get('tone')) or 'clear'
        lines = [
            f'Use a {tone} voice that speaks directly to {audience.lower()}.',
            'Keep wording specific, practical, and grounded in approved brand facts.',
            'Preserve the user intent of existing copy when refining it.',
        ]
        voice_examples = _text(content.get('voice_examples'))
        if voice_examples:
            lines.append(f'Use these voice examples as positive references: {voice_examples}.')
        forbidden_words = _text(content.get('forbidden_words'))
        if forbidden_words:
            lines.append(f'Avoid these words: {forbidden_words}.')
        forbidden_claims = _text(content.get('forbidden_claims'))
        if forbidden_claims:
            lines.append(f'Never make these claims: {forbidden_claims}.')
        required_claims = _text(content.get('required_claims'))
        if required_claims:
            lines.append(f'Include these approved claims when relevant: {required_claims}.')
        compliance_notes = _text(content.get('compliance_notes'))
        if compliance_notes:
            lines.append(f'Follow these compliance notes: {compliance_notes}.')
        lines.append('Do not invent proof, guarantees, testimonials, statistics, pricing, locations, or customer names.')
        return '\n'.join(lines)
    if field_key == 'target_audience':
        return f'{audience} who need consistent campaigns, reusable content, and faster website launches.'
    if field_key == 'brand_promise':
        return f'Help {audience.lower()} {promise}.'
    if field_key == 'differentiators':
        return 'AI-assisted content planning\nBrand rules applied across every campaign\nReusable CMS assets for pages, media, and offers'
    if field_key == 'positioning_statement':
        return f'For {audience.lower()}, {name} is the {industry.lower()} solution that helps teams {promise} with one connected brand, content, and campaign workflow.'
    if field_key == 'voice_examples':
        return 'Clear next step, no heavy setup\nBuilt around your approved brand voice\nLaunch polished campaigns from reusable content'
    if field_key == 'voice_anti_examples':
        return 'Revolutionary magic for everyone\nGuaranteed results overnight\nJust trust the algorithm'
    if field_key == 'forbidden_words':
        return 'guaranteed\nbest-in-class\nrisk-free'
    if field_key == 'forbidden_claims':
        return 'Do not promise guaranteed revenue lift\nDo not claim legal or regulatory compliance without proof\nDo not invent customer logos or testimonials'
    if field_key == 'required_claims':
        return 'Use only approved proof points\nTie benefits to the target audience\nKeep every call to action specific and measurable'
    if field_key == 'compliance_notes':
        return 'Use approved claims only. Avoid absolute promises unless they are backed by documented proof.'
    if field_key == 'image_style':
        return 'Clean product-led visuals, real interface moments, natural lighting, no generic stock cliches.'
    if field_key == 'cta_style':
        return 'Direct, action-first CTAs that set a clear expectation without false urgency.'
    if field_key == 'primary_market':
        return _text(content.get('primary_market')) or 'United States'
    if field_key == 'locale':
        return _text(content.get('locale')) or 'en-US'
    if field_key == 'competitors':
        return 'Generic website builders\nManual agency workflows\nDisconnected campaign tools'
    return _text(content.get(field_key))


def _normalize_brand_field_value(field_key, value):
    field = BRAND_ENHANCE_FIELDS[field_key]
    choices = _brand_choice_sets()
    if isinstance(value, list):
        value = '\n'.join(_text(item) for item in value if _text(item))
    value = _text(value).strip('"\'` ')
    if field.get('choice'):
        fallback = _brand_fallback_value(field_key, {})
        return _pick_choice(value, choices[field['choice']], fallback)
    if field.get('list'):
        lines = []
        for part in re.split(r'[\n;]+', value):
            part = re.sub(r'^\s*[-*0-9.)]+\s*', '', part).strip()
            if part:
                lines.append(part)
        return '\n'.join(lines[:6])
    return value[:int(field.get('limit') or 600)]


def _enhance_brand_section(data, current_content):
    field_key = _text(data.get('target_field') or current_content.get('__target_field'))
    if field_key not in BRAND_ENHANCE_FIELDS:
        return jsonify({'error': True, 'message': 'Valid target_field is required for brand enhancement'}), 400

    target_value = _text(data.get('target_value'))
    clean_content = {
        key: value for key, value in current_content.items()
        if not str(key).startswith('__')
    }
    full_editor_payload = clean_content.get('full') if isinstance(clean_content.get('full'), dict) else {}
    secondary_context = {
        key: value for key, value in clean_content.items()
        if key != 'full'
    }
    field = BRAND_ENHANCE_FIELDS[field_key]
    choices = _brand_choice_sets()
    choice_note = ''
    if field.get('choice'):
        choice_note = f"\nAllowed values for {field_key}: {', '.join(choices[field['choice']])}"
    target_instruction = (
        "The current target field value is the primary input. Refine, clarify, or strengthen it "
        "without changing its intent."
        if target_value
        else "The current target field value is empty. Fill it from the supporting brand context."
    )

    system_prompt = (
        "You are a senior brand strategist inside a marketing CMS. "
        "Improve or fill one requested brand field. Treat the target field value as primary "
        "and the rest of the brand form as secondary context. "
        "Return ONLY a valid JSON object with the requested field key. "
        "Do not invent customer names, awards, pricing, or guaranteed outcomes."
    )
    user_prompt = (
        f"Requested field: {field_key} ({field['label']})\n"
        f"Field guidance: {field.get('hint', 'Make it concise and useful for campaign generation.')}\n"
        f"Current target field value (primary): {target_value or '(empty)'}\n"
        f"{target_instruction}\n"
        f"Supporting brand context (secondary): {json.dumps(secondary_context, ensure_ascii=True)}\n"
        f"Full editor payload: {json.dumps(full_editor_payload, ensure_ascii=True)}"
        f"{choice_note}\n\n"
        f"Return JSON exactly like: {{\"{field_key}\": \"...\"}}. "
        "For list fields, return a newline-separated string. "
        "For choice fields, return exactly one allowed value."
    )

    try:
        from rag.agent.model_backend import ModelBackend
        raw = ModelBackend().generate(system_prompt, user_prompt)
        json_match = re.search(r'\{[\s\S]*\}', raw or '')
        enhanced = json.loads(json_match.group()) if json_match else {}
        value = enhanced.get(field_key)
        if not value:
            raise ValueError('AI returned no usable value')
        return jsonify({
            'enhanced_fields': {
                field_key: _normalize_brand_field_value(field_key, value)
            },
            'source': 'ai',
        })
    except Exception as e:
        current_app.logger.info(f"Brand enhance fallback for {field_key}: {e}")
        fallback_value = target_value or _brand_fallback_value(field_key, secondary_context)
        return jsonify({
            'enhanced_fields': {
                field_key: _normalize_brand_field_value(field_key, fallback_value)
            },
            'source': 'fallback',
        })


def _enhance_campaign_section(data, current_content):
    field_key = _text(data.get('target_field') or current_content.get('__target_field'))
    if field_key not in CAMPAIGN_ENHANCE_FIELDS:
        return jsonify({'error': True, 'message': 'Valid target_field is required for campaign enhancement'}), 400

    clean_content = {
        key: value for key, value in current_content.items()
        if not str(key).startswith('__')
    }
    field = CAMPAIGN_ENHANCE_FIELDS[field_key]
    current_value = _text(clean_content.get(field_key))

    system_prompt = (
        "You are a senior marketing copywriter inside a campaign CMS. "
        "Improve or fill ONE requested campaign field using the full campaign draft "
        "(brand, product or service, audience, goal, and offer) as context. "
        "Keep it concise, specific, and on-message for the audience. "
        "Return ONLY a valid JSON object with the requested field key. "
        "Do not invent prices, guarantees, fake testimonials, awards, or specific statistics."
    )
    user_prompt = (
        f"Requested field: {field_key} ({field['label']})\n"
        f"Field guidance: {field.get('hint', 'Make it concise and effective for this campaign.')}\n"
        f"Current value (improve it, or write it if empty): {current_value or '(empty)'}\n"
        f"Full campaign draft: {json.dumps(clean_content, ensure_ascii=True)}\n\n"
        f"Return JSON exactly like: {{\"{field_key}\": \"...\"}}. "
        "Return a single concise string value, no markdown fences."
    )

    try:
        from rag.agent.model_backend import ModelBackend
        raw = ModelBackend().generate(system_prompt, user_prompt)
        json_match = re.search(r'\{[\s\S]*\}', raw or '')
        enhanced = json.loads(json_match.group()) if json_match else {}
        value = enhanced.get(field_key)
        if not value:
            raise ValueError('AI returned no usable value')
        return jsonify({
            'enhanced_fields': {
                field_key: _text(value).strip('"\'` ')[:600]
            },
            'source': 'ai',
        })
    except Exception as e:
        current_app.logger.info(f"Campaign enhance fallback for {field_key}: {e}")
        return jsonify({
            'enhanced_fields': {
                field_key: current_value[:600]
            },
            'source': 'fallback',
        })


@chat_bp.route('/api/chat/status', methods=['GET'])
def chat_status():
    """Return current pipeline progress status for frontend polling."""
    return jsonify(_chat_status)


@chat_bp.route('/api/chat/cancel', methods=['POST'])
@require_app_ai_request
def chat_cancel():
    """Cancel the active chat request."""
    if _active_cancel_event is not None:
        _active_cancel_event.set()
    return jsonify({"cancelled": True})


# Keys exposed by /api/chat/industry-config. Must stay in sync with
# rag/scripts/seed_industry_config.py CONFIG_KEYS.
_INDUSTRY_CONFIG_KEYS = ("industries", "section_questions", "recommendations", "page_purposes")


def _industry_config_fallback(key: str):
    """Build the JSON-serializable value for a config key from git-tracked defaults."""
    from rag.industry_defaults import (
        INDUSTRY_REGISTRY,
        SECTION_QUESTIONS,
        SECTION_RECOMMENDATIONS,
        CATEGORY_FLOWS,
        PAGE_PURPOSES,
    )
    if key == "industries":
        return INDUSTRY_REGISTRY
    if key == "section_questions":
        return SECTION_QUESTIONS
    if key == "recommendations":
        return {"section_pairs": SECTION_RECOMMENDATIONS, "category_flows": CATEGORY_FLOWS}
    if key == "page_purposes":
        return {"purposes": PAGE_PURPOSES}
    return None


@chat_bp.route('/api/chat/industry-config', methods=['GET'])
def industry_config():
    """
    Return the guided-flow industry configuration.

    Response shape:
      {
        "industries":        { <industry_key>: {label, category, variants, ...} },
        "section_questions": { <section_type>: {label, base_fields, ...} },
        "recommendations":   { section_pairs, category_flows },
        "page_purposes":     { purposes: [...] }
      }

    Sources data from the `industry_configs` DB table. For any key missing
    from the table, falls back to `rag/industry_defaults.py` so the endpoint
    never returns an empty config even on a fresh / un-seeded DB.
    """
    result = {}
    try:
        rows = {r.config_key: r for r in IndustryConfig.query.filter(
            IndustryConfig.config_key.in_(_INDUSTRY_CONFIG_KEYS)
        ).all()}
    except Exception:
        # DB unavailable / table missing → pure fallback
        rows = {}

    for key in _INDUSTRY_CONFIG_KEYS:
        row = rows.get(key)
        if row is not None:
            result[key] = row.get_data()
        else:
            result[key] = _industry_config_fallback(key)

    # Styles aren't stored in DB — pulled from rag.config each request.
    # Shape: {styles: [{id, label}, ...], industry_default_style: {...}}
    try:
        from rag.config import CANONICAL_STYLES, INDUSTRY_DEFAULT_STYLE
        style_list = sorted(CANONICAL_STYLES)
        result["styles"] = {
            "canonical": [{"id": s, "label": s.replace("_", " ").title()} for s in style_list],
            "industry_default_style": dict(INDUSTRY_DEFAULT_STYLE),
        }
    except Exception:
        result["styles"] = {"canonical": [], "industry_default_style": {}}

    # Industry detection regex patterns — single source of truth for frontend.
    # Frontend uses these instead of maintaining a duplicate pattern list.
    try:
        from rag.agent.query_analyzer import QueryAnalyzer
        result["detection_patterns"] = dict(QueryAnalyzer.INDUSTRY_KEYWORDS)
    except Exception:
        result["detection_patterns"] = {}

    return jsonify(result)


@chat_bp.route('/api/chat/enhance', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def enhance_section():
    """
    LLM-powered auto-fill for guided flow section content fields.

    Request body:
      {
        "business_name": str,
        "industry": str,
        "description": str,
        "section_type": str (required),
        "current_content": { field_key: str, ... }
      }

    Response:
      { "enhanced_fields": { field_key: str, ... } }
    """
    import json as _json
    import re as _re

    data = request.get_json() or {}
    section_type = (data.get('section_type') or '').strip()
    if not section_type:
        return jsonify({'error': True, 'message': 'section_type is required'}), 400

    business_name = (data.get('business_name') or '').strip()
    industry = (data.get('industry') or '').strip()
    description = (data.get('description') or '').strip()
    current_content = data.get('current_content') or {}
    if section_type == 'brand':
        return _enhance_brand_section(data, current_content)
    if section_type == 'campaign':
        return _enhance_campaign_section(data, current_content)

    from rag.industry_defaults import SECTION_QUESTIONS
    sq = SECTION_QUESTIONS.get(section_type, {})
    fields = sq.get('base_fields', [])
    field_keys = [f['key'] for f in fields]
    if not field_keys:
        return jsonify({'enhanced_fields': {}})

    field_descriptions = ', '.join(
        f"{f['key']} ({f.get('label', f['key'])})" for f in fields
    )
    existing = {k: v for k, v in current_content.items() if v and str(v).strip()}

    system_prompt = (
        "You are an expert website copywriter. Generate realistic, specific "
        "content for a website section. Return ONLY a valid JSON object mapping "
        "field keys to suggested text values. No markdown fences, no explanation "
        "— just the raw JSON object."
    )

    user_prompt = (
        f"Business name: {business_name or 'Unknown'}\n"
        f"Industry: {industry or 'general'}\n"
        f"Business description: {description or 'N/A'}\n"
        f"Section type: {section_type}\n"
        f"Fields to generate: {field_descriptions}\n"
    )
    if existing:
        user_prompt += f"User has already entered (preserve meaning, improve if needed): {_json.dumps(existing)}\n"
    user_prompt += (
        f"\nReturn a JSON object with exactly these keys: {', '.join(field_keys)}. "
        "Each value must be concise, specific to this business, and ready to use "
        "on a real website. Use realistic details, not generic placeholders."
    )

    try:
        from rag.agent.model_backend import ModelBackend
        backend = ModelBackend()
        raw = backend.generate(system_prompt, user_prompt)

        json_match = _re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            enhanced = _json.loads(json_match.group())
        else:
            enhanced = {}

        enhanced_fields = {
            k: v for k, v in enhanced.items()
            if k in field_keys and isinstance(v, str)
        }
        return jsonify({'enhanced_fields': enhanced_fields})

    except Exception as e:
        current_app.logger.error(f"Enhance section error: {e}\n{traceback.format_exc()}")
        return jsonify({
            'error': True,
            'message': 'Enhancement failed',
            'details': str(e),
        }), 500


def _content_preview(item):
    return {
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'content': item.content,
        'brand_id': item.brand_id,
        'status': item.status,
        'source': item.source,
    }


def _json_object_from_text(raw):
    match = re.search(r'\{[\s\S]*\}', raw or '')
    return json.loads(match.group()) if match else {}


def _fallback_enhance_content(content_type, content, title=None):
    """Best-effort formatter used when the model is unavailable."""
    slot_schema = content_type_slot_schema(content_type)
    if not slot_schema:
        return {'content': content.strip()}

    aliases = {
        'headline': ('headline', 'title'),
        'subheadline': ('subheadline', 'subtitle'),
        'tagline': ('tagline',),
        'paragraph': ('paragraph', 'body', 'description', 'details'),
        'body': ('body', 'paragraph', 'copy'),
        'button_label': ('button', 'button_label', 'cta', 'cta_label'),
        'cta_label': ('button', 'button_label', 'cta', 'cta_label'),
        'link': ('link', 'href', 'url'),
        'question': ('question', 'q'),
        'answer': ('answer', 'a'),
        'quote': ('quote', 'testimonial'),
        'author': ('author', 'name'),
        'author_role': ('role', 'title'),
        'company': ('company',),
        'details': ('details', 'paragraph', 'body', 'description'),
        'code': ('code', 'promo code'),
        'expiry_note': ('expiry', 'deadline', 'expiry_note'),
        'concern': ('concern', 'objection', 'question'),
        'response': ('response', 'answer'),
        'statement': ('statement', 'guarantee'),
        'conditions': ('conditions', 'terms'),
        'date_note': ('date', 'date_note', 'timing'),
        'claim': ('claim', 'proof'),
        'metric': ('metric', 'stat', 'number'),
        'source_note': ('source', 'source_note'),
        'customer': ('customer', 'client'),
        'problem': ('problem', 'challenge'),
        'result': ('result', 'outcome'),
        'name': ('name', 'spec'),
        'value': ('value',),
        'note': ('note',),
        'form_title': ('form_title', 'title', 'headline'),
        'form_subtext': ('form_subtext', 'subtext', 'description'),
        'form_fields': ('form_fields', 'fields'),
        'submit_text': ('submit_text', 'submit', 'button'),
        'story': ('story', 'about'),
        'since_year': ('since', 'since_year', 'year'),
        'team_note': ('team', 'team_note'),
        'seo_title': ('seo_title', 'title'),
        'meta_description': ('meta_description', 'description'),
        'subject': ('subject', 'subject_line'),
        'preview_text': ('preview', 'preview_text'),
        'post_copy': ('post', 'post_copy', 'copy'),
        'hashtags': ('hashtags', 'tags'),
    }
    parsed = {}
    loose_lines = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ':' not in line:
            loose_lines.append(line)
            continue
        label, value = line.split(':', 1)
        label = label.strip().lower().replace('-', '_')
        value = value.strip()
        if not value:
            continue
        for slot in slot_schema:
            key = slot.get('key')
            if label == key or label in aliases.get(key, ()):
                parsed[key] = value
                break
        else:
            loose_lines.append(line)

    remaining = ' '.join(loose_lines).strip()
    if remaining:
        for candidate in ('paragraph', 'details', 'answer', 'quote', 'response', 'body', 'story', 'description', 'post_copy'):
            if any(slot.get('key') == candidate for slot in slot_schema) and candidate not in parsed:
                parsed[candidate] = remaining
                break
    if title and any(slot.get('key') == 'headline' for slot in slot_schema) and 'headline' not in parsed:
        parsed['headline'] = title

    preferred_summary = {
        'cta': ('paragraph', 'headline', 'button_label'),
        'faq': ('answer', 'question'),
        'testimonial': ('quote',),
        'offer': ('details', 'headline', 'cta_label'),
        'value_proposition': ('paragraph', 'headline'),
        'benefit': ('paragraph', 'headline'),
        'product_feature': ('paragraph', 'headline'),
        'objection': ('response', 'concern'),
        'comparison': ('differentiator', 'subject'),
    }.get(content_type)
    summary = ''
    schema_keys = tuple(slot.get('key') for slot in slot_schema if slot.get('key'))
    for key in (preferred_summary or schema_keys):
        value = parsed.get(key)
        if str(value or '').strip():
            summary = str(value).strip()
            break
    for slot in slot_schema:
        if summary:
            break
        value = parsed.get(slot.get('key'))
        if str(value or '').strip():
            summary = str(value).strip()
            break
    if not summary:
        summary = content.strip()
    return {'content': summary, 'slots': parsed}


def _fallback_section_payload(seed):
    section_type = section_type_for_category(seed.category)
    return {
        'section': {
            'section_type': section_type,
            'section_type_label': section_type_label(section_type),
            'name': f'{section_type_label(section_type)} section',
            'description': 'Drafted from one selected content item.',
            'status': 'draft',
            'brand_id': seed.brand_id,
            'content_refs': [seed.id],
            'items': [_content_preview(seed)],
            'suggested_categories': suggested_categories(section_type),
        },
        'created_draft_ids': [],
        'source': 'fallback',
    }


@chat_bp.route('/api/chat/generate-section', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def generate_section_from_content():
    """Draft a typed section from one seed content item without persisting the section."""
    data = request.get_json(silent=True) or {}
    seed_content_id = (data.get('seed_content_id') or '').strip()
    if not seed_content_id:
        return jsonify({'error': 'seed_content_id is required'}), 400

    seed = ContentItem.query.filter_by(id=seed_content_id, org_id=g.current_org_id).first()
    if not seed:
        abort(404)

    brand_id = (data.get('brand_id') or seed.brand_id or '').strip() or None
    if brand_id:
        brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
        if not brand:
            return jsonify({'error': 'Selected brand was not found.'}), 400

    candidates_query = ContentItem.query.filter(ContentItem.org_id == g.current_org_id)
    if brand_id:
        candidates_query = candidates_query.filter(db.or_(
            ContentItem.brand_id == brand_id,
            ContentItem.brand_id.is_(None),
        ))
    else:
        candidates_query = candidates_query.filter(ContentItem.brand_id.is_(None))
    candidates = candidates_query.order_by(
        ContentItem.is_pinned.desc(), ContentItem.updated_at.desc()
    ).limit(40).all()

    candidate_payload = [
        {
            'id': item.id,
            'category': item.category,
            'title': item.title,
            'content': (item.content or '')[:500],
        }
        for item in candidates
    ]

    system_prompt = (
        "You are a campaign content architect. Build a reusable website section "
        "from approved content atoms. Return ONLY valid JSON with keys: "
        "section_type, name, ordered_existing_ids, new_items. "
        "section_type must be one of hero, features, pricing, testimonials, faq, "
        "cta, about, offer, products, value_prop, stats, custom. "
        "new_items must be an array of objects with category, title, content."
    )
    seed_payload = {
        'id': seed.id,
        'category': seed.category,
        'title': seed.title,
        'content': (seed.content or '')[:500],
    }

    user_prompt = (
        f"Seed content: {json.dumps(seed_payload)}\n"
        f"Available content atoms: {json.dumps(candidate_payload)}\n"
        f"Allowed content categories: {json.dumps(sorted(ContentItem.VALID_CATEGORIES))}\n"
        "Choose useful existing ids in display order. Add new draft items only when "
        "a needed atom is missing. Do not invent facts, pricing, testimonials, or proof."
    )

    try:
        from rag.agent.model_backend import ModelBackend
        raw = ModelBackend().generate(system_prompt, user_prompt)
        draft = _json_object_from_text(raw)
    except Exception as exc:
        current_app.logger.warning(f"Generate section AI fallback for {seed_content_id}: {exc}")
        return jsonify(_fallback_section_payload(seed))

    section_type = (draft.get('section_type') or '').strip() or section_type_for_category(seed.category)
    if not is_valid_section_type(section_type):
        section_type = section_type_for_category(seed.category)

    candidate_ids = {item.id for item in candidates}
    ordered_existing_ids = []
    for raw_id in draft.get('ordered_existing_ids') or []:
        item_id = str(raw_id).strip()
        if item_id in candidate_ids and item_id not in ordered_existing_ids:
            ordered_existing_ids.append(item_id)
    if seed.id not in ordered_existing_ids:
        ordered_existing_ids.insert(0, seed.id)

    created_items = []
    for new_item in draft.get('new_items') or []:
        if not isinstance(new_item, dict):
            continue
        category = (new_item.get('category') or '').strip()
        title = (new_item.get('title') or '').strip() or None
        content = (new_item.get('content') or '').strip()
        if not category or category not in ContentItem.VALID_CATEGORIES:
            return jsonify({'error': f'Invalid generated content category: {category or "(blank)"}'}), 400
        if not content:
            continue
        slots = slots_from_content(category, content)
        content = derive_content_from_slots(category, slots)
        item = ContentItem(
            org_id=g.current_org_id,
            brand_id=brand_id,
            category=category,
            status='draft',
            source='ai',
            channel='landing_page',
            title=title,
            content=content,
            ai_notes='Generated while drafting a reusable section from content library atoms.',
        )
        item.set_slots(slots)
        db.session.add(item)
        created_items.append(item)

    if created_items:
        db.session.commit()
        ordered_existing_ids.extend(item.id for item in created_items)

    rows = ContentItem.query.filter(
        ContentItem.org_id == g.current_org_id,
        ContentItem.id.in_(ordered_existing_ids),
    ).all()
    item_map = {item.id: item for item in rows}
    ordered_items = [_content_preview(item_map[item_id]) for item_id in ordered_existing_ids if item_id in item_map]

    name = (draft.get('name') or '').strip() or f'{section_type_label(section_type)} section'
    return jsonify({
        'section': {
            'section_type': section_type,
            'section_type_label': section_type_label(section_type),
            'name': name[:255],
            'description': 'AI-drafted section. Review the order and save when ready.',
            'status': 'draft',
            'brand_id': brand_id,
            'content_refs': ordered_existing_ids,
            'items': ordered_items,
            'suggested_categories': suggested_categories(section_type),
        },
        'created_draft_ids': [item.id for item in created_items],
        'source': 'ai',
    })


@chat_bp.route('/api/chat/enhance-content', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def enhance_content_item_format():
    """Format rough typed content into schema-backed slots."""
    data = request.get_json(silent=True) or {}
    content_type = (data.get('content_type') or data.get('category') or '').strip()
    if not content_type or content_type not in ContentItem.VALID_CATEGORIES:
        return jsonify({'error': 'Valid content_type is required.'}), 400

    slots = data.get('slots') if isinstance(data.get('slots'), dict) else {}
    content = (data.get('content') or '').strip() or derive_content_from_slots(content_type, slots)
    if not content:
        return jsonify({'error': 'Add slot content first, then enhance the format.'}), 400

    title = (data.get('title') or '').strip() or None
    slot_schema = content_type_slot_schema(content_type)
    fallback = _fallback_enhance_content(content_type, content, title=title)

    system_prompt = (
        "You format rough marketing content into the selected content type. "
        "Return only JSON. Preserve known facts and user intent. Do not invent "
        "proof, testimonials, pricing, guarantees, customer names, metrics, or permission notes."
    )
    user_prompt = json.dumps({
        'mode': data.get('mode') or 'format',
        'channel': data.get('channel') or 'general',
        'content_type': content_type,
        'title': title,
        'content': content,
        'slots': slots,
        'tags': data.get('tags') or '',
        'slot_schema': slot_schema,
        'response_shape': (
            {'content': 'summary text', 'slots': {'slot_key': 'slot value'}}
            if slot_schema else {'content': 'formatted content text'}
        ),
    })

    try:
        from rag.agent.model_backend import ModelBackend
        raw = ModelBackend().generate(system_prompt, user_prompt)
        enhanced = _json_object_from_text(raw)
        if not isinstance(enhanced, dict):
            enhanced = {}
    except Exception as exc:
        current_app.logger.info(f"Content enhance fallback for {content_type}: {exc}")
        enhanced = {}

    if slot_schema:
        payload = enhanced.get('slots') if isinstance(enhanced.get('slots'), dict) else {}
        allowed = {slot.get('key') for slot in slot_schema}
        payload = {k: str(v).strip() for k, v in payload.items() if k in allowed and str(v).strip()}
        if not payload:
            payload = fallback.get('slots') or {}
        summary = (enhanced.get('content') or fallback.get('content') or content).strip()
        return jsonify({'content': summary, 'slots': payload})

    formatted = (enhanced.get('content') or fallback.get('content') or content).strip()
    return jsonify({'content': formatted})


@chat_bp.route('/api/chat/guided', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def chat_guided():
    """
    Guided-flow generation endpoint.

    Accepts a rich `businessContext` collected by the frontend wizard and
    passes it directly to the RAG pipeline. The planner LLM call is skipped
    entirely — the outline is built deterministically from the user's
    section selections (see PlannerAgent.plan_from_context).

    Request body:
      {
        "businessContext": { business_name, industry, variant_id, variant_label,
                             description, sections[], style_preference,
                             color_preference },
        "currentYaml": str (optional, usually empty for create_page),
        "siteId": str | null
      }

    Response: same shape as /api/chat — {response, yaml, action}.
    """
    global _active_cancel_event

    base_url = (os.environ.get('OLLAMA_BASE_URL') or '').lower()
    is_local = not base_url or 'localhost' in base_url or '127.0.0.1' in base_url
    if not is_local and not os.environ.get('OLLAMA_API_KEY'):
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI chat is not configured. Please contact the administrator.',
            'details': 'The AI service has not been set up on this server.'
        }), 503

    cancel_event = threading.Event()
    _active_cancel_event = cancel_event
    progress_fn = _make_progress_fn(cancel_event)

    try:
        data = request.get_json() or {}
        bc = data.get('businessContext')
        if not isinstance(bc, dict) or not bc:
            return jsonify({
                'error': True,
                'errorType': 'validation',
                'message': 'businessContext is required',
                'details': 'Request body must include a non-empty "businessContext" object'
            }), 400

        current_yaml = data.get('currentYaml', '')
        current_app.logger.info(
            f"[guided-flow] business={bc.get('business_name')} "
            f"industry={bc.get('industry')} variant={bc.get('variant_id')} "
            f"sections={len(bc.get('sections') or [])}"
        )

        # Pull available images from the org media library.
        selected_images = _load_org_media_images()

        from llm_service import get_llm_service
        llm_service = get_llm_service()

        # The RAG agent uses the structured business_context to drive a
        # deterministic planner. `message` is kept as a short, human-readable
        # tag so it still shows up in logs.
        message_tag = f"[guided] {bc.get('business_name') or 'new site'}"

        _chat_status["active"] = True
        _chat_status["message"] = "Planning your site..."
        result = llm_service.chat(
            message_tag, current_yaml, None,
            selected_images=selected_images, progress_fn=progress_fn,
            business_context=bc,
        )
        _chat_status["active"] = False
        _chat_status["message"] = ""

        return jsonify(result)

    except CancelledError:
        current_app.logger.info("Guided chat request cancelled by user")
        _chat_status["active"] = False
        return jsonify({
            'response': 'Request cancelled.',
            'yaml': None,
            'action': 'error',
            'errorType': 'cancelled'
        }), 499

    except Exception as e:
        _chat_status["active"] = False
        current_app.logger.error(f"Guided chat error: {e}\n{traceback.format_exc()}")
        return jsonify({
            'error': True,
            'errorType': 'internal',
            'message': 'An error occurred while generating the site',
            'details': str(e),
            'response': f'Error: {e}',
            'yaml': None,
            'action': 'error',
        }), 500


@chat_bp.route('/api/chat/campaign-handoff', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def campaign_handoff():
    """
    Detect create_page intent and create a campaign draft for handoff.

    If the message matches create_page patterns, creates a draft campaign
    and returns a redirect URL. Otherwise returns {handoff: false}.

    Request: { "message": str }
    Response: { handoff: true, campaign_id, redirect_url } or { handoff: false }
    """
    from flask import g
    from models import Organization
    from routes.campaign import _get_campaign_or_404

    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'handoff': False})

    try:
        from rag.agent.query_analyzer import QueryAnalyzer
        analyzer = QueryAnalyzer()
        intent = analyzer.analyze(message)

        if intent.action != 'create_page':
            return jsonify({'handoff': False})

        default_org = Organization.query.filter_by(slug='default').first()
        if not default_org:
            return jsonify({'handoff': False})

        from models import Campaign, CampaignBrief
        from extensions import db

        name_hint = message[:80].strip() if len(message) > 3 else 'New Campaign'

        campaign = Campaign(
            org_id=default_org.id,
            name=name_hint,
        )
        db.session.add(campaign)
        db.session.flush()

        brief = CampaignBrief(
            campaign_id=campaign.id,
            description=message,
        )
        db.session.add(brief)

        from models import CampaignOffer
        offer = CampaignOffer(campaign_id=campaign.id)
        db.session.add(offer)

        db.session.commit()

        return jsonify({
            'handoff': True,
            'campaign_id': campaign.id,
            'redirect_url': f'/campaign-studio/{campaign.id}',
            'message': f"I'll set up a campaign for you.",
        })

    except Exception as e:
        current_app.logger.error(f"Campaign handoff error: {e}")
        return jsonify({'handoff': False})


@chat_bp.route('/api/chat', methods=['POST'])
@require_app_ai_request
@require_role('editor')
def chat():
    """
    LLM chat endpoint for website generation and modification.

    Request body:
    {
        "message": "user's message",
        "currentYaml": "current YAML content",
        "selectedComponent": { ... } | null,
        "siteId": "site-uuid" | null
    }

    Response:
    {
        "response": "AI response text",
        "yaml": "generated/modified YAML" | null,
        "action": "create" | "modify" | "explain" | "error"
    }
    """
    global _active_cancel_event

    # Cloud Ollama requires an API key; local daemon does not.
    base_url = (os.environ.get('OLLAMA_BASE_URL') or '').lower()
    is_local = not base_url or 'localhost' in base_url or '127.0.0.1' in base_url
    if not is_local and not os.environ.get('OLLAMA_API_KEY'):
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI chat is not configured. Please contact the administrator.',
            'details': 'The AI service has not been set up on this server.'
        }), 503

    cancel_event = threading.Event()
    _active_cancel_event = cancel_event
    progress_fn = _make_progress_fn(cancel_event)

    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'error': True,
                'errorType': 'validation',
                'message': 'Message is required',
                'details': 'Request body must include a "message" field'
            }), 400

        message = data.get('message', '')
        current_yaml = data.get('currentYaml', '')
        selected_component = data.get('selectedComponent', None)

        # Query reusable organization media for generation context.
        selected_images = _load_org_media_images()

        # Import and use LLM service
        from llm_service import get_llm_service
        llm_service = get_llm_service()

        # Get response from LLM with progress tracking
        _chat_status["active"] = True
        _chat_status["message"] = "Analyzing request..."
        result = llm_service.chat(message, current_yaml, selected_component,
                                  selected_images=selected_images, progress_fn=progress_fn)
        _chat_status["active"] = False
        _chat_status["message"] = ""

        return jsonify(result)

    except CancelledError:
        current_app.logger.info("Chat request cancelled by user")
        return jsonify({
            'response': 'Request cancelled.',
            'yaml': None,
            'action': 'error',
            'errorType': 'cancelled'
        }), 499

    except ValueError as e:
        current_app.logger.error(f"Chat configuration error: {e}")
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI service configuration error. Please contact the administrator.',
            'details': 'Check server logs for details.'
        }), 503

    except Exception as e:
        current_app.logger.error(f"Chat API error: {traceback.format_exc()}")
        return jsonify({
            'error': True,
            'errorType': 'api',
            'message': 'Failed to get AI response. Please try again.',
            'details': 'An internal error occurred. Check server logs for details.'
        }), 500

    finally:
        _active_cancel_event = None
        _chat_status["active"] = False
        _chat_status["message"] = ""
