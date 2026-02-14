from flask import Blueprint, request, jsonify, current_app
import yaml
import traceback

from renderer import render_yaml_structure
from extensions import TOKENS, COMPONENT_DEFAULTS

render_bp = Blueprint('render', __name__)


@render_bp.route('/render', methods=['POST'])
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
        # Log full traceback server-side only — never send to frontend
        current_app.logger.error(f"Render error: {traceback.format_exc()}")
        error_message = str(e)

        # Send only safe error description to frontend (no tracebacks)
        if 'line' in error_message.lower():
            details = error_message
        else:
            details = 'A rendering error occurred. Check server logs for details.'

        return jsonify({'error': 'An unexpected error occurred during rendering.', 'details': details}), 500
