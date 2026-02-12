#!/usr/bin/env python3
"""
Generate CSS tokens file from tokens.yaml
This creates CSS custom properties (variables) from the YAML token definitions.
Typography sizes use clamp() for fluid responsive scaling with step-down on mobile.
"""
import yaml
import os

# Font size step-down mapping: each token's mobile minimum is the desktop value
# of a smaller token. Larger sizes step down 2 levels, mid sizes 1 level.
# Viewport range: 400px (mobile) to 1200px (desktop)
FONT_SIZE_STEP_DOWN = {
    # token: (mobile_min_rem, desktop_max_rem)
    'xxs':  (0.9, 0.9),    # static - no scaling
    'xs':   (1.1, 1.1),    # static - no scaling
    'sm':   (1.1, 1.4),    # XS → SM
    'md':   (1.4, 1.8),    # SM → MD
    'lg':   (1.8, 2.2),    # MD → LG
    'xl':   (1.8, 3.0),    # MD → XL (down 2)
    'xxl':  (2.2, 4.5),    # LG → XXL (down 2)
    'xxxl': (3.0, 6.0),    # XL → XXXL (down 2)
}

VP_MIN = 400   # mobile viewport px
VP_MAX = 1200  # desktop viewport px


def calc_clamp(min_rem, max_rem):
    """Calculate CSS clamp() value for fluid scaling between VP_MIN and VP_MAX."""
    if min_rem == max_rem:
        return f"{min_rem}rem"

    # slope = (max - min) / ((VP_MAX - VP_MIN) / 100)  [in vw units]
    vw_range = (VP_MAX - VP_MIN) / 100  # 8
    slope = (max_rem - min_rem) / vw_range
    intercept = min_rem - slope * (VP_MIN / 100)

    # Round for clean CSS output
    slope_r = round(slope, 3)
    intercept_r = round(intercept, 2)

    return f"clamp({min_rem}rem, {slope_r}vw + {intercept_r}rem, {max_rem}rem)"


def generate_tokens_css(tokens_yaml_path, output_css_path):
    """Generate CSS variables from tokens.yaml"""

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

    # Typography sizes with fluid clamp() scaling
    if 'typography_sizes' in tokens:
        css_lines.append("    /* Typography Sizes - Fluid responsive with step-down scaling */")
        css_lines.append(f"    /* Scales smoothly between mobile ({VP_MIN}px) and desktop ({VP_MAX}px) viewport */")
        css_lines.append("    /* Larger sizes step down more aggressively on mobile */")
        for key, value in tokens['typography_sizes'].items():
            if key == 'auto':
                css_lines.append(f"    --font-size-{key}: auto;")
            elif key in FONT_SIZE_STEP_DOWN:
                min_rem, max_rem = FONT_SIZE_STEP_DOWN[key]
                clamp_val = calc_clamp(min_rem, max_rem)
                # Find what the min maps to for the comment
                step_down_labels = {
                    'xxs': 'static - no scaling',
                    'xs': 'static - no scaling',
                    'sm': 'XS \u2192 SM',
                    'md': 'SM \u2192 MD',
                    'lg': 'MD \u2192 LG',
                    'xl': 'MD \u2192 XL',
                    'xxl': 'LG \u2192 XXL',
                    'xxxl': 'XL \u2192 XXXL',
                }
                label = step_down_labels.get(key, '')
                css_lines.append(f"    --font-size-{key}: {clamp_val};{' ' * max(1, 56 - len(clamp_val) - len(key))}/* {label} */")
            else:
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

    with open(output_css_path, 'w') as f:
        f.write('\n'.join(css_lines))

    print(f"Generated {output_css_path} from {tokens_yaml_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tokens_yaml = os.path.join(base_dir, 'tokens.yaml')
    tokens_css = os.path.join(base_dir, 'static', 'css', 'tokens.css')

    generate_tokens_css(tokens_yaml, tokens_css)






