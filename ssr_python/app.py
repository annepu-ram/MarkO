from flask import Flask, render_template, request, jsonify
from renderer import render_yaml_structure
import yaml
import os

app = Flask(__name__)

# Add custom Jinja2 filter for transparency to hex alpha conversion
@app.template_filter('transparency_to_hex')
def transparency_to_hex(transparency):
    """
    Convert transparency (0-100) to hex alpha (00-ff)
    0 = fully transparent (00)
    100 = fully opaque (ff)
    """
    if transparency is None:
        return 'ff'  # Default to fully opaque
    
    try:
        trans_int = int(transparency)
        # Clamp to 0-100
        trans_int = max(0, min(100, trans_int))
        # Convert to 0-255 range
        alpha = int(trans_int * 255 / 100)
        # Convert to hex (00-ff)
        return format(alpha, '02x')
    except (ValueError, TypeError):
        return 'ff'  # Default to fully opaque on error

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
        # Enhanced error reporting for template and rendering errors
        import traceback
        error_trace = traceback.format_exc()
        error_message = str(e)
        
        # Extract line number from Jinja2 template errors if available
        if 'line' in error_message.lower():
            details = f"{error_message}\n\nFull traceback:\n{error_trace}"
        else:
            details = f"{error_message}\n\nFull traceback:\n{error_trace}"
        
        return jsonify({'error': 'An unexpected error occurred during rendering.', 'details': details}), 500

if __name__ == '__main__':
    app.run(debug=True)
