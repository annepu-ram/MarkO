from flask import Blueprint, request, jsonify, current_app
import os
import traceback

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    LLM chat endpoint for website generation and modification.

    Request body:
    {
        "message": "user's message",
        "currentYaml": "current YAML content",
        "selectedComponent": {
            "id": "comp_0_1",
            "path": [0, "components", 1],
            "name": "heading"
        } | null
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

        # Import and use LLM service
        from llm_service import get_llm_service
        llm_service = get_llm_service()

        # Get response from LLM
        result = llm_service.chat(message, current_yaml, selected_component)

        return jsonify(result)

    except ValueError as e:
        # Log the real error server-side
        current_app.logger.error(f"Chat configuration error: {e}")
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI service configuration error. Please contact the administrator.',
            'details': 'Check server logs for details.'
        }), 503

    except Exception as e:
        # Log full traceback server-side only — never send to frontend
        current_app.logger.error(f"Chat API error: {traceback.format_exc()}")
        return jsonify({
            'error': True,
            'errorType': 'api',
            'message': 'Failed to get AI response. Please try again.',
            'details': 'An internal error occurred. Check server logs for details.'
        }), 500
