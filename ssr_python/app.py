from flask import Flask, render_template, request, jsonify
from renderer import render_yaml_structure, transparency_to_hex
import yaml
import os
import random
import math
import requests as http_requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Register custom Jinja2 filters (defined in renderer.py)
app.template_filter('transparency_to_hex')(transparency_to_hex)

# Get the directory where this app.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root) for component schemas/defaults
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Load design tokens from tokens.yaml
TOKENS = {}
tokens_path = os.path.join(BASE_DIR, 'tokens.yaml')

if os.path.exists(tokens_path):
    with open(tokens_path, 'r') as f:
        TOKENS = yaml.safe_load(f)
    print(f"Loaded tokens from {tokens_path}")
    print(f"Tokens keys: {TOKENS.keys() if TOKENS else 'None'}")
else:
    print(f"Warning: tokens.yaml not found at {tokens_path}")

# Load component defaults from component_defaults.yaml
COMPONENT_DEFAULTS = {}
defaults_path = os.path.join(PROJECT_ROOT, 'component_defaults.yaml')

if os.path.exists(defaults_path):
    with open(defaults_path, 'r') as f:
        COMPONENT_DEFAULTS = yaml.safe_load(f)
    print(f"Loaded component defaults from {defaults_path}")
    print(f"Available components: {list(COMPONENT_DEFAULTS.keys()) if COMPONENT_DEFAULTS else 'None'}")
else:
    print(f"Warning: component_defaults.yaml not found at {defaults_path}")

# API endpoints for component metadata
@app.route('/api/schemas')
def get_schemas():
    """Serve component schemas as JSON"""
    schemas_path = os.path.join(PROJECT_ROOT, 'component_schemas.yaml')
    if os.path.exists(schemas_path):
        with open(schemas_path, 'r') as f:
            schemas = yaml.safe_load(f)
        return jsonify(schemas or {})
    return jsonify({}), 404

@app.route('/api/defaults')
def get_defaults():
    """Serve component defaults as JSON"""
    defaults_path = os.path.join(PROJECT_ROOT, 'component_defaults.yaml')
    if os.path.exists(defaults_path):
        with open(defaults_path, 'r') as f:
            defaults = yaml.safe_load(f)
        return jsonify(defaults or {})
    return jsonify({}), 404

@app.route('/api/tokens')
def get_schema_tokens():
    """Serve schema tokens as JSON"""
    tokens_path = os.path.join(PROJECT_ROOT, 'schema_tokens.yaml')
    if os.path.exists(tokens_path):
        with open(tokens_path, 'r') as f:
            tokens = yaml.safe_load(f)
        return jsonify(tokens or {})
    return jsonify({}), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview-frame')
def preview_frame():
    """Serve the preview iframe content"""
    return render_template('preview_frame.html')

@app.route('/render', methods=['POST'])
def render_from_yaml():
    try:
        yaml_data = request.get_data(as_text=True)
        # Safely parse the YAML
        structure = yaml.safe_load(yaml_data)
        # Render the structure to HTML, passing tokens and defaults
        html_content = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        return html_content
    except yaml.YAMLError as e:
        # Provide a more descriptive error with line and column numbers
        error_details = str(e)
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            error_details = f"YAML parsing error at Line {mark.line + 1}, Column {mark.column + 1}: {e.problem}"
        return jsonify({'error': 'Invalid YAML Format', 'details': error_details}), 400
    except Exception as e:
        import traceback
        # Log full traceback server-side only — never send to frontend
        app.logger.error(f"Render error: {traceback.format_exc()}")
        error_message = str(e)

        # Send only safe error description to frontend (no tracebacks)
        if 'line' in error_message.lower():
            details = error_message
        else:
            details = 'A rendering error occurred. Check server logs for details.'

        return jsonify({'error': 'An unexpected error occurred during rendering.', 'details': details}), 500


# Color mapping from our UI values to each API's accepted values
PEXELS_COLOR_MAP = {
    'red': 'red', 'orange': 'orange', 'yellow': 'yellow', 'green': 'green',
    'blue': 'blue', 'purple': 'violet', 'black': 'black', 'white': 'white',
}
PIXABAY_COLOR_MAP = {
    'red': 'red', 'orange': 'orange', 'yellow': 'yellow', 'green': 'green',
    'blue': 'blue', 'purple': 'lilac', 'black': 'black', 'white': 'white',
}


def _search_pexels(query, color, page, per_page, orientation):
    """Search via Pexels API. Returns normalized results dict."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        return None

    params = {'query': query, 'page': page, 'per_page': min(per_page, 80)}
    if color:
        params['color'] = PEXELS_COLOR_MAP.get(color, color)
    if orientation:
        params['orientation'] = orientation

    resp = http_requests.get(
        'https://api.pexels.com/v1/search',
        params=params,
        headers={'Authorization': api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    total = data.get('total_results', 0)
    results = []
    for photo in data.get('photos', []):
        src = photo.get('src', {})
        results.append({
            'id': str(photo['id']),
            'thumbUrl': src.get('tiny', src.get('small', '')),
            'smallUrl': src.get('small', ''),
            'regularUrl': src.get('medium', src.get('large', '')),
            'fullUrl': src.get('original', ''),
            'photographer': photo.get('photographer', 'Unknown'),
            'photographerUrl': photo.get('photographer_url', ''),
            'altText': photo.get('alt', query),
            'width': photo.get('width', 0),
            'height': photo.get('height', 0),
            'source': 'pexels',
        })

    return {
        'results': results,
        'total': total,
        'total_pages': math.ceil(total / max(per_page, 1)),
        'source': 'pexels',
    }


def _search_pixabay(query, color, page, per_page, orientation):
    """Search via Pixabay API. Returns normalized results dict."""
    api_key = os.environ.get('PIXABAY_API_KEY', '')
    if not api_key:
        return None

    params = {
        'key': api_key,
        'q': query,
        'page': page,
        'per_page': min(per_page, 200),
        'image_type': 'photo',
    }
    if color:
        params['colors'] = PIXABAY_COLOR_MAP.get(color, color)
    if orientation:
        params['orientation'] = orientation

    resp = http_requests.get(
        'https://pixabay.com/api/',
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    total = data.get('totalHits', 0)
    results = []
    for hit in data.get('hits', []):
        results.append({
            'id': str(hit['id']),
            'thumbUrl': hit.get('previewURL', ''),
            'smallUrl': hit.get('webformatURL', ''),
            'regularUrl': hit.get('webformatURL', ''),
            'fullUrl': hit.get('largeImageURL', ''),
            'photographer': hit.get('user', 'Unknown'),
            'photographerUrl': f"https://pixabay.com/users/{hit.get('user', '')}-{hit.get('user_id', '')}/" if hit.get('user') else '',
            'altText': hit.get('tags', query),
            'width': hit.get('imageWidth', 0),
            'height': hit.get('imageHeight', 0),
            'source': 'pixabay',
        })

    return {
        'results': results,
        'total': total,
        'total_pages': math.ceil(total / max(per_page, 1)),
        'source': 'pixabay',
    }


@app.route('/api/images/search')
def search_images():
    """Proxy stock photo search — randomly picks Pexels or Pixabay to spread rate limits."""
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    pixabay_key = os.environ.get('PIXABAY_API_KEY', '')

    if not pexels_key and not pixabay_key:
        return jsonify({'error': 'Image search is not configured. Please contact the administrator.'}), 503

    query = request.args.get('q', '')
    color = request.args.get('color', '')
    page = request.args.get('page', 1, type=int)
    orientation = request.args.get('orientation', '')
    per_page = request.args.get('per_page', 30, type=int)

    if not query and not color:
        return jsonify({'results': [], 'total': 0, 'total_pages': 0})

    search_query = query or 'wallpaper'

    # Build list of available providers and pick one randomly
    providers = []
    if pexels_key:
        providers.append(_search_pexels)
    if pixabay_key:
        providers.append(_search_pixabay)
    random.shuffle(providers)

    # Try each provider in shuffled order; fall back on failure
    for provider in providers:
        try:
            result = provider(search_query, color, page, per_page, orientation)
            if result and result.get('results'):
                return jsonify(result)
        except http_requests.exceptions.Timeout:
            continue
        except http_requests.exceptions.HTTPError:
            continue
        except Exception:
            continue

    # All providers failed — try once more with explicit error reporting
    try:
        result = providers[0](search_query, color, page, per_page, orientation)
        if result is not None:
            return jsonify(result)
    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'Image search timed out. Please try again.'}), 504
    except http_requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        return jsonify({'error': f'Image API error ({status})'}), status
    except Exception as e:
        # Log full error server-side — never send raw exception to frontend (may contain API keys in URLs)
        app.logger.error(f"Image search failed: {e}")
        return jsonify({'error': 'Image search failed. Please try again later.'}), 500

    return jsonify({'results': [], 'total': 0, 'total_pages': 0})


@app.route('/api/chat', methods=['POST'])
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
        app.logger.error(f"Chat configuration error: {e}")
        return jsonify({
            'error': True,
            'errorType': 'configuration',
            'message': 'AI service configuration error. Please contact the administrator.',
            'details': 'Check server logs for details.'
        }), 503

    except Exception as e:
        import traceback
        # Log full traceback server-side only — never send to frontend
        app.logger.error(f"Chat API error: {traceback.format_exc()}")
        return jsonify({
            'error': True,
            'errorType': 'api',
            'message': 'Failed to get AI response. Please try again.',
            'details': 'An internal error occurred. Check server logs for details.'
        }), 500


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    # Restrict iframe embedding to same origin only (prevents clickjacking)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Content Security Policy
    # - default-src 'self': Only allow resources from same origin
    # - script-src 'self' 'unsafe-inline': Allow same-origin scripts and inline scripts (needed for module initialization)
    # - style-src 'self' 'unsafe-inline': Allow same-origin styles and inline styles (needed for component styling)
    # - img-src 'self' data: https:: Allow images from same origin, data URIs, and HTTPS sources
    # - frame-src 'self': Only allow same-origin frames
    # - frame-ancestors 'self': Prevent this page from being embedded elsewhere
    # - connect-src 'self': Allow fetch/XHR to same origin (for API calls)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob: https:; "
        "frame-src 'self'; "
        "frame-ancestors 'self'; "
        "connect-src 'self';"
    )

    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)
