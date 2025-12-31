from flask import render_template_string
from jinja2 import TemplateSyntaxError
import traceback

def render_yaml_structure(structure, tokens=None):
    """
    Recursively renders a YAML structure to HTML using Jinja2 templates.
    """
    if tokens is None:
        tokens = {}
    
    # Debug: Check if tokens is valid
    if not isinstance(tokens, dict):
        raise Exception(f"Tokens must be a dict, got {type(tokens)}")
        
    if not isinstance(structure, list) or not structure:
        return "<!-- Invalid YAML: Root should be a list of components -->"

    # The main template string that will contain the logic to render components
    # It imports the component macros and then iterates through the structure.
    # Pass path information for component ID generation
    template = """
        {% import 'macros/_components.html' as components %}
        {% for component in structure %}
            {{ components.render_component(component, tokens, [loop.index0]) }}
        {% endfor %}
    """
    try:
        return render_template_string(template, structure=structure, tokens=tokens)
    except TemplateSyntaxError as e:
        # Provide detailed error information for template syntax errors
        error_msg = f"Template Syntax Error in {e.filename or 'template'} at line {e.lineno}: {e.message}"
        raise Exception(error_msg) from e
    except TypeError as e:
        # Catch iteration errors
        if 'not iterable' in str(e):
            error_msg = f"Iteration Error: {str(e)}\n\nThis usually means you're trying to iterate over a method/function instead of calling it.\n\nStructure type: {type(structure)}\nTokens type: {type(tokens)}\n\nFull traceback:\n{traceback.format_exc()}"
            raise Exception(error_msg) from e
        raise

