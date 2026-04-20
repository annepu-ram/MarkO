from flask import Blueprint, request, jsonify, current_app
import os
import threading
import traceback

from models import SiteImage, IndustryConfig
from extensions import db
from exceptions import CancelledError

chat_bp = Blueprint('chat', __name__)


def _clean_filename(name):
    """Convert filename to readable alt text: 'hero-banner.jpg' → 'hero banner'"""
    if not name:
        return ''
    stem = os.path.splitext(name)[0]
    return stem.replace('-', ' ').replace('_', ' ')


# Shared progress status — updated by the chat endpoint, polled by the frontend
_chat_status = {"message": "", "active": False}

# Cancellation event for the active chat request
_active_cancel_event: threading.Event | None = None


def _make_progress_fn(cancel_event: threading.Event):
    """Create a progress callback that raises CancelledError if cancelled."""
    def progress_fn(msg):
        if cancel_event.is_set():
            raise CancelledError("Request cancelled by user")
        _chat_status["message"] = msg
    return progress_fn


@chat_bp.route('/api/chat/status', methods=['GET'])
def chat_status():
    """Return current pipeline progress status for frontend polling."""
    return jsonify(_chat_status)


@chat_bp.route('/api/chat/cancel', methods=['POST'])
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

    return jsonify(result)


@chat_bp.route('/api/chat/guided', methods=['POST'])
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
        site_id = data.get('siteId')

        current_app.logger.info(
            f"[guided-flow] business={bc.get('business_name')} "
            f"industry={bc.get('industry')} variant={bc.get('variant_id')} "
            f"sections={len(bc.get('sections') or [])}"
        )

        # Pull available images from DB (same as /api/chat)
        selected_images = []
        if site_id:
            db_images = SiteImage.query.filter(
                db.or_(SiteImage.site_id == site_id, SiteImage.site_id.is_(None))
            ).order_by(SiteImage.created_at.desc()).all()
            selected_images = [
                {
                    'url': f'/uploads/{img.storage_path}' if img.storage_path else f'/uploads/{img.filename}',
                    'altText': img.alt_text or _clean_filename(img.original_name) or img.filename,
                    'orientation': img.orientation or 'unknown',
                    'photographer': img.photographer or '',
                }
                for img in db_images
            ]

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


@chat_bp.route('/api/chat', methods=['POST'])
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

        # Query images from DB by siteId (single source of truth)
        site_id = data.get('siteId')
        selected_images = []
        if site_id:
            db_images = SiteImage.query.filter(
                db.or_(SiteImage.site_id == site_id, SiteImage.site_id.is_(None))
            ).order_by(SiteImage.created_at.desc()).all()
            selected_images = [
                {
                    'url': f'/uploads/{img.storage_path}' if img.storage_path else f'/uploads/{img.filename}',
                    'altText': img.alt_text or _clean_filename(img.original_name) or img.filename,
                    'orientation': img.orientation or 'unknown',
                    'photographer': img.photographer or '',
                }
                for img in db_images
            ]

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
