"""ssr_python/rag/agent/stitcher.py — Pure Python page assembler (no LLM).

Uses ruamel.yaml to preserve YAML anchors (&color-primary) and aliases
(*color-primary) through the parse → fix → dump round-trip.
"""
import io
import logging
import re

from ruamel.yaml import YAML

from rag.config import config
from rag.agent.yaml_fixer import fix_structure

logger = logging.getLogger(__name__)

# Shared ruamel.yaml instance (round-trip mode preserves anchors/aliases/comments)
_yaml = YAML()
_yaml.default_flow_style = False
_yaml.allow_unicode = True
_yaml.width = config.yaml_line_width


def _resolve_aliases(section_yaml: str, theme: dict) -> str:
    """Replace YAML alias references (*color-primary etc.) with quoted actual values.

    This is needed because each section is parsed independently — the anchors
    are only defined at the site level, so aliases would cause parse errors.
    After stitching, we re-introduce anchors/aliases in the final output.

    Values are single-quoted to prevent '#' being parsed as a YAML comment.
    """
    dt = config.default_theme
    replacements = {
        "*color-primary": "'" + theme.get("primary", dt["primary"]) + "'",
        "*color-text": "'" + theme.get("text", dt["text"]) + "'",
        "*color-secondary": "'" + theme.get("secondary", dt["secondary"]) + "'",
        "*color-accent": "'" + theme.get("accent", dt["accent"]) + "'",
        "*color-background": "'" + theme.get("background", dt["background"]) + "'",
        "*font-heading": "'" + theme.get("heading_font", dt["heading_font"]) + "'",
        "*font-content": "'" + theme.get("content_font", dt["content_font"]) + "'",
    }
    for alias, value in replacements.items():
        section_yaml = section_yaml.replace(alias, value)
    return section_yaml


def _sanitize_yaml(text: str) -> str:
    """Fix common LLM YAML output errors before parsing.

    Handles:
    1. Nested single quotes: font: ''Font Name', serif' → font: "'Font Name', serif"
    2. Unquoted values with colons: text: Foo: bar → text: "Foo: bar"
    3. Broken block scalars: text: |+Some text → text: "Some text"
    4. Unquoted values with parentheses: color: rgba(...) → color: "rgba(...)"
    """
    lines = text.split('\n')
    fixed = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            fixed.append(line)
            i += 1
            continue

        m = re.match(r'^(\s*\S+:\s+)(.*)', line)
        if not m:
            fixed.append(line)
            i += 1
            continue

        prefix, value = m.group(1), m.group(2)

        # Fix 3: Broken block scalar — |+text or |>text or |-text (no space/newline after indicator)
        block_match = re.match(r'^([|>][+\-]?)(\S.*)$', value)
        if block_match:
            value = '"' + block_match.group(2).replace('"', '\\"') + '"'

        # Fix 4: Unquoted values containing parentheses — rgba(...), calc(...), etc.
        elif not value.startswith(("'", '"', '[', '{', '|', '>', '*')) \
                and '(' in value and ')' in value:
            value = '"' + value.replace('"', '\\"') + '"'

        # Fix 1: Nested single quotes — ''Something', rest'
        elif re.match(r"^''[^']+',\s*[^']+?'$", value):
            inner = value[1:-1]
            value = '"' + inner.replace('"', '\\"') + '"'

        # Fix 2: Unquoted value containing a colon (not already quoted, not a URL, not an alias)
        elif not value.startswith(("'", '"', '[', '{', '|', '>', '*')) \
                and ':' in value \
                and not re.match(r'^https?://', value):
            value = '"' + value.replace('"', '\\"') + '"'

        fixed.append(prefix + value)
        i += 1
    return '\n'.join(fixed)


def _restore_aliases(dumped: str, theme: dict) -> str:
    """Replace literal theme values back with YAML aliases in the final output.

    Skips the site.properties.theme block (where anchors are defined) and only
    replaces in the component sections below it.
    """
    # Find where the theme block ends (after colors/fonts definition)
    # We split at the first `components:` under site to preserve anchors in theme
    marker = "  components:"
    marker_pos = dumped.find(marker)
    if marker_pos == -1:
        return dumped

    header = dumped[:marker_pos]
    body = dumped[marker_pos:]

    # Replace hex values with aliases in the body (component sections only)
    dt = config.default_theme
    color_map = {
        theme.get("primary", dt["primary"]): "*color-primary",
        theme.get("text", dt["text"]): "*color-text",
        theme.get("secondary", dt["secondary"]): "*color-secondary",
        theme.get("accent", dt["accent"]): "*color-accent",
        theme.get("background", dt["background"]): "*color-background",
    }
    font_map = {
        theme.get("heading_font", dt["heading_font"]): "*font-heading",
        theme.get("content_font", dt["content_font"]): "*font-content",
    }

    for value, alias in color_map.items():
        if value:
            # Match both quoted and unquoted forms
            body = body.replace(f"'{value}'", alias)
            body = body.replace(f'"{value}"', alias)
            body = body.replace(f" {value}", f" {alias}")
    for value, alias in font_map.items():
        if value:
            body = body.replace(f"'{value}'", alias)
            body = body.replace(f'"{value}"', alias)

    return header + body


def stitch_page(outline: dict, section_yamls: list[str]) -> str:
    """Combine planner outline + builder outputs into full page YAML.

    Args:
        outline: Planner JSON with page_title, theme, sections
        section_yamls: List of YAML strings from builder (one per section)

    Returns:
        Complete page YAML string with anchors/aliases for theme colors
    """
    theme = outline.get("theme", {})

    dt = config.default_theme
    primary = theme.get("primary", dt["primary"])
    text_color = theme.get("text", dt["text"])
    secondary = theme.get("secondary", dt["secondary"])
    accent = theme.get("accent", dt["accent"])
    background = theme.get("background", dt["background"])
    heading_font = theme.get("heading_font", dt["heading_font"])
    content_font = theme.get("content_font", dt["content_font"])

    # Build the site wrapper as a YAML string with explicit anchors.
    # ruamel.yaml round-trip mode preserves these anchors in the output.
    # Use double quotes for values that may contain single quotes (fonts).
    page_title = outline.get("page_title", "New Page").replace('"', '\\"')
    heading_esc = heading_font.replace('"', '\\"')
    content_esc = content_font.replace('"', '\\"')
    site_template = f"""\
- name: site
  properties:
    theme:
      fonts:
        heading: &font-heading "{heading_esc}"
        content: &font-content "{content_esc}"
      colors:
        primary: &color-primary '{primary}'
        text: &color-text '{text_color}'
        secondary: &color-secondary '{secondary}'
        accent: &color-accent '{accent}'
        background: &color-background '{background}'
  components:
  - name: page
    slug: home
    title: "{page_title}"
    properties:
      appearance:
        background:
          color: *color-background
          opacity: 100
    components: []
"""

    # Parse site template with ruamel (preserves anchors)
    page = _yaml.load(site_template)

    # Target list: page[0].components[0].components
    page_components = page[0]["components"][0]["components"]

    # Parse and merge each section's YAML into the page
    import yaml as pyyaml  # Use PyYAML for sections (simpler error handling)

    for i, section_yaml in enumerate(section_yamls):
        if not section_yaml or not section_yaml.strip():
            logger.warning(f"Section {i} is empty, skipping")
            continue

        # Resolve alias references to actual values before parsing
        resolved = _resolve_aliases(section_yaml, theme)
        resolved = _sanitize_yaml(resolved)

        try:
            parsed = pyyaml.safe_load(resolved)
            if parsed is None:
                logger.warning(f"Section {i} produced empty YAML after parsing, skipping")
                continue
            # Fix structural issues from LLM output
            parsed = fix_structure(parsed)
            if isinstance(parsed, list):
                page_components.extend(parsed)
            elif isinstance(parsed, dict):
                page_components.append(parsed)
            logger.debug(f"Section {i} stitched successfully ({type(parsed).__name__})")
        except pyyaml.YAMLError as e:
            logger.error(f"Section {i} has invalid YAML: {e}")
            logger.debug(f"Section {i} raw YAML:\n{section_yaml[:500]}")
            # Skip bad sections rather than failing the whole page
            continue

    # Dump with ruamel to preserve anchors in the site theme block
    stream = io.StringIO()
    _yaml.dump(page, stream)
    dumped = stream.getvalue()

    # Restore aliases in component sections (replace hex values back to *color-xxx)
    result = _restore_aliases(dumped, theme)

    logger.debug(f"Stitcher final output ({len(result)} chars)")
    return result
