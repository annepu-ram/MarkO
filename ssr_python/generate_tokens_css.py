#!/usr/bin/env python3
"""
Generate CSS tokens file from tokens.yaml
This creates CSS custom properties (variables) from the YAML token definitions.
"""
import yaml
import os

def generate_tokens_css(tokens_yaml_path, output_css_path):
    """Generate CSS variables from tokens.yaml"""
    
    # Load tokens
    with open(tokens_yaml_path, 'r') as f:
        tokens = yaml.safe_load(f)
    
    css_lines = [
        "/* CSS Design Tokens - Auto-generated from tokens.yaml */",
        "/* DO NOT EDIT MANUALLY - Regenerate with: python generate_tokens_css.py */",
        "",
        ":root {",
    ]
    
    # Spacing tokens
    if 'spacing' in tokens:
        css_lines.append("    /* Spacing Scale */")
        for key, value in tokens['spacing'].items():
            css_lines.append(f"    --spacing-{key}: {value};")
        css_lines.append("")
    
    # Typography sizes
    if 'typography_sizes' in tokens:
        css_lines.append("    /* Typography Sizes */")
        for key, value in tokens['typography_sizes'].items():
            css_lines.append(f"    --font-size-{key}: {value};")
        css_lines.append("")
    
    # Font weights
    if 'font_weights' in tokens:
        css_lines.append("    /* Font Weights */")
        for key, value in tokens['font_weights'].items():
            css_lines.append(f"    --font-weight-{key}: {value};")
        css_lines.append("")
    
    # Border radius
    if 'border_radius' in tokens:
        css_lines.append("    /* Border Radius */")
        for key, value in tokens['border_radius'].items():
            css_lines.append(f"    --border-radius-{key}: {value};")
        css_lines.append("")
    
    # Letter spacing
    if 'letter_spacing' in tokens:
        css_lines.append("    /* Letter Spacing */")
        for key, value in tokens['letter_spacing'].items():
            css_lines.append(f"    --letter-spacing-{key}: {value};")
        css_lines.append("")
    
    css_lines.append("}")
    css_lines.append("")
    
    # Write CSS file
    with open(output_css_path, 'w') as f:
        f.write('\n'.join(css_lines))
    
    print(f"✅ Generated {output_css_path} from {tokens_yaml_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tokens_yaml = os.path.join(base_dir, 'tokens.yaml')
    tokens_css = os.path.join(base_dir, 'static', 'css', 'tokens.css')
    
    generate_tokens_css(tokens_yaml, tokens_css)


