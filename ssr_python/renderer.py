from flask import render_template_string, current_app
from jinja2 import TemplateSyntaxError, Environment, FileSystemLoader
import traceback
import copy
import os


# ============================================================================
# Custom Jinja2 Filters
# ============================================================================

def transparency_to_hex(transparency):
    """
    Convert transparency (0-100) to hex alpha (00-ff).
    Used as a Jinja2 filter in _components.html for background colors.

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


def hex_to_rgb(hex_color):
    """Convert hex color (#3C4043) to space-separated RGB (60 64 67) for CSS rgb()."""
    if not hex_color or not isinstance(hex_color, str):
        return '0 0 0'
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return '0 0 0'
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f'{r} {g} {b}'
    except ValueError:
        return '0 0 0'


# ============================================================================
# Deep Merge & Validation
# ============================================================================

def deep_merge(base, override):
    """
    Deep merge two dictionaries. Override values take precedence.
    Arrays are replaced, not merged.
    None and empty string values in override are skipped (preserves base defaults).
    """
    if override is None or override == '':
        return copy.deepcopy(base) if isinstance(base, dict) else base
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override

    result = copy.deepcopy(base)
    for key, value in override.items():
        if value is None or value == '':
            continue  # Skip None/empty values, preserve defaults
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result

def validate_token_value(property_path, value, tokens):
    """
    Validate that a property value exists in the corresponding token category.
    Returns error message if invalid, None if valid.
    """
    # Map property paths to token categories
    token_mappings = {
        'spacing.marginBlock': 'spacing',
        'spacing.marginInline': 'spacing',
        'spacing.paddingBlock': 'spacing',
        'spacing.paddingInline': 'spacing',
        'typography.size': 'typography_sizes',
        'typography.weight': 'font_weights',
        'typography.letterSpacing': 'letter_spacing',
        'appearance.radius': 'border_radius',
        'layout.padding.top': 'spacing',
        'layout.padding.right': 'spacing',
        'layout.padding.bottom': 'spacing',
        'layout.padding.left': 'spacing',
        'layout.margin.top': 'spacing',
        'layout.margin.bottom': 'spacing',
    }
    
    token_category = token_mappings.get(property_path)
    if not token_category:
        # Not a token-based property, skip validation
        return None
    
    # Skip validation for None, empty string, or numeric values
    if value is None or value == '' or isinstance(value, (int, float)):
        return None
    
    # Check if token category exists
    if token_category not in tokens:
        return f"Token category '{token_category}' not found for property '{property_path}'"
    
    # Check if value exists in token category
    token_values = tokens[token_category]
    if not isinstance(token_values, dict):
        return f"Invalid token category structure for '{token_category}'"
    
    if value not in token_values:
        available = ', '.join(token_values.keys())
        return f"Invalid value '{value}' for property '{property_path}'. Must be one of: {available}"
    
    return None

def validate_component_properties(component, tokens, component_path=''):
    """
    Validate component properties against token definitions.
    Raises exception if invalid values are found.
    """
    if not isinstance(component, dict):
        return
    
    component_name = component.get('name', 'unknown')
    properties = component.get('properties', {})
    
    # Validate nested properties
    def check_nested(obj, path_prefix=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if isinstance(value, dict):
                    check_nested(value, current_path)
                else:
                    # Validate token-based values
                    error = validate_token_value(current_path, value, tokens)
                    if error:
                        raise ValueError(f"Component '{component_name}' at {component_path}: {error}")
    
    check_nested(properties)


# ============================================================================
# Theme Color Resolution
# ============================================================================

DEFAULT_THEME_COLORS = {
    '$color-primary': '#111827',
    '$color-secondary': '#6b7280',
    '$color-accent': '#6366f1',
    '$color-background': '#ffffff',
}

def _extract_theme_colors(structure):
    """Extract theme colors from the site component, with fallbacks."""
    colors = dict(DEFAULT_THEME_COLORS)
    for component in structure:
        if component.get('name') == 'site':
            theme = component.get('properties', {}).get('theme', {})
            theme_colors = theme.get('colors', {})
            if theme_colors.get('primary'):
                colors['$color-primary'] = theme_colors['primary']
            if theme_colors.get('secondary'):
                colors['$color-secondary'] = theme_colors['secondary']
            if theme_colors.get('accent'):
                colors['$color-accent'] = theme_colors['accent']
            if theme_colors.get('background'):
                colors['$color-background'] = theme_colors['background']
            break
    return colors

def _resolve_color_placeholders(obj, color_map):
    """Recursively replace $color-xxx placeholders with actual theme colors."""
    if isinstance(obj, str):
        return color_map.get(obj, obj)
    if isinstance(obj, dict):
        return {k: _resolve_color_placeholders(v, color_map) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_color_placeholders(item, color_map) for item in obj]
    return obj


def merge_component_with_defaults(component, defaults, tokens=None, component_path=''):
    """
    Merge a component with its defaults from component_defaults.yaml.
    Validates properties if tokens are provided.
    """
    if not isinstance(component, dict):
        return component
    
    component_name = component.get('name')
    if not component_name:
        raise ValueError(f"Component at {component_path} is missing 'name' property")
    
    if component_name not in defaults:
        raise ValueError(f"Unknown component type '{component_name}' at {component_path}. No defaults found.")
    
    # Get defaults for this component type
    component_defaults = defaults.get(component_name, {})
    
    # Merge component properties with defaults (component properties override defaults)
    component_properties = component.get('properties', {})
    merged_properties = deep_merge(component_defaults, component_properties)
    
    # Create new component with merged properties
    merged_component = copy.deepcopy(component)
    merged_component['properties'] = merged_properties
    
    # Validate properties if tokens are provided
    if tokens:
        validate_component_properties(merged_component, tokens, component_path)
    
    # Recursively merge nested components
    # Use `or []` because dict.get() returns None when key exists with null value
    if 'components' in merged_component:
        merged_component['components'] = [
            merge_component_with_defaults(child, defaults, tokens, f"{component_path}.components[{i}]")
            for i, child in enumerate(merged_component.get('components') or [])
        ]
    
    # Handle nested structures in specific component types
    if 'columns' in merged_component:
        merged_component['columns'] = [
            {
                **col,
                'components': [
                    merge_component_with_defaults(child, defaults, tokens, f"{component_path}.columns[{col_idx}].components[{i}]")
                    for i, child in enumerate(col.get('components') or [])
                ]
            }
            for col_idx, col in enumerate(merged_component.get('columns') or [])
        ]

    if 'tabs' in merged_component:
        merged_component['tabs'] = [
            {
                **tab,
                'components': [
                    merge_component_with_defaults(child, defaults, tokens, f"{component_path}.tabs[{tab_idx}].components[{i}]")
                    for i, child in enumerate(tab.get('components') or [])
                ]
            }
            for tab_idx, tab in enumerate(merged_component.get('tabs') or [])
        ]

    if 'slides' in merged_component:
        merged_component['slides'] = [
            {
                **slide,
                'components': [
                    merge_component_with_defaults(child, defaults, tokens, f"{component_path}.slides[{slide_idx}].components[{i}]")
                    for i, child in enumerate(slide.get('components') or [])
                ]
            }
            for slide_idx, slide in enumerate(merged_component.get('slides') or [])
        ]

    if 'items' in merged_component:
        merged_component['items'] = [
            {
                **item,
                'components': [
                    merge_component_with_defaults(child, defaults, tokens, f"{component_path}.items[{item_idx}].components[{i}]")
                    for i, child in enumerate(item.get('components') or [])
                ]
            }
            for item_idx, item in enumerate(merged_component.get('items') or [])
        ]

    return merged_component

def _build_component_template(templates_dir):
    """
    Build a single Jinja2 template string by concatenating all component macro files.
    Reads the _assembly.html manifest, parses include directives, and concatenates
    the referenced files in order. This keeps all macros in one template scope.
    """
    import re
    assembly_path = os.path.join(templates_dir, 'components', '_assembly.html')

    with open(assembly_path, 'r', encoding='utf-8') as f:
        assembly_content = f.read()

    # Parse {% include "path" %} directives from assembly
    include_pattern = re.compile(r'{%[-\s]*include\s+["\'](.+?)["\']\s*[-]?%}')
    parts = []
    for match in include_pattern.finditer(assembly_content):
        filepath = os.path.join(templates_dir, match.group(1))
        with open(filepath, 'r', encoding='utf-8') as f:
            parts.append(f.read())

    # Append the rendering loop
    parts.append("""
        {% for component in structure %}
            {{ render_component(component, tokens, [loop.index0]) }}
        {% endfor %}
    """)

    return '\n'.join(parts)


def render_yaml_structure(structure, tokens=None, defaults=None):
    """
    Recursively renders a YAML structure to HTML using Jinja2 templates.
    Merges component defaults before rendering.
    """
    if tokens is None:
        tokens = {}
    
    if defaults is None:
        defaults = {}
    
    # Validate inputs
    if not isinstance(tokens, dict):
        raise Exception(f"Tokens must be a dict, got {type(tokens)}")
    
    if not isinstance(defaults, dict):
        raise Exception(f"Defaults must be a dict, got {type(defaults)}")
        
    if not isinstance(structure, list) or not structure:
        return "<!-- Invalid YAML: Root should be a list of components -->"

    # Merge each component with its defaults and validate
    # Site wrapper is handled by the Jinja2 render_site macro (transparent pass-through)
    merged_structure = [
        merge_component_with_defaults(component, defaults, tokens, f"[{i}]")
        for i, component in enumerate(structure)
    ]

    # Resolve $color-xxx placeholders in defaults with the user's theme colors
    theme_colors = _extract_theme_colors(structure)
    merged_structure = _resolve_color_placeholders(merged_structure, theme_colors)

    # Build the template by concatenating all component macro files.
    # Jinja2 {% include %} does NOT export macros to the parent scope,
    # so we concatenate files in Python to keep all macros in one template.
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    template_str = _build_component_template(templates_dir)

    try:
        # Create Jinja2 environment with whitespace trimming to avoid empty lines in inline styles
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,      # Remove first newline after block tag
            lstrip_blocks=True     # Strip leading whitespace before block tags
        )

        # Add custom filters from Flask app if available
        if current_app:
            env.filters.update(current_app.jinja_env.filters)

        template = env.from_string(template_str)
        return template.render(structure=merged_structure, tokens=tokens)
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

