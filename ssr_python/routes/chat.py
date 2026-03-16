from flask import Blueprint, request, jsonify, current_app
import os
import traceback

from models import SiteImage
from extensions import db

chat_bp = Blueprint('chat', __name__)


def _clean_filename(name):
    """Convert filename to readable alt text: 'hero-banner.jpg' → 'hero banner'"""
    if not name:
        return ''
    stem = os.path.splitext(name)[0]
    return stem.replace('-', ' ').replace('_', ' ')

# Shared progress status — updated by the chat endpoint, polled by the frontend
_chat_status = {"message": "", "active": False}


@chat_bp.route('/api/chat/status', methods=['GET'])
def chat_status():
    """Return current pipeline progress status for frontend polling."""
    return jsonify(_chat_status)


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
    # Check if Ollama API key is configured (required for cloud)
    if not os.environ.get('OLLAMA_API_KEY'):
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI chat is not configured. Please contact the administrator.',
            'details': 'The AI service has not been set up on this server.'
        }), 503

    def _update_status(msg):
        _chat_status["message"] = msg

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
                                  selected_images=selected_images, progress_fn=_update_status)
        _chat_status["active"] = False
        _chat_status["message"] = ""

        return jsonify(result)

    except ValueError as e:
        _chat_status["active"] = False
        _chat_status["message"] = ""
        current_app.logger.error(f"Chat configuration error: {e}")
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI service configuration error. Please contact the administrator.',
            'details': 'Check server logs for details.'
        }), 503

    except Exception as e:
        _chat_status["active"] = False
        _chat_status["message"] = ""
        current_app.logger.error(f"Chat API error: {traceback.format_exc()}")
        return jsonify({
            'error': True,
            'errorType': 'api',
            'message': 'Failed to get AI response. Please try again.',
            'details': 'An internal error occurred. Check server logs for details.'
        }), 500
