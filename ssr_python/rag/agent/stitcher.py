"""ssr_python/rag/agent/stitcher.py — Pure Python page assembler (no LLM).

Uses ruamel.yaml to preserve YAML anchors (&color-primary) and aliases
(*color-primary) through the parse → fix → dump round-trip.
"""
import io
import logging

from ruamel.yaml import YAML

from rag.config import config

logger = logging.getLogger(__name__)

# Shared ruamel.yaml instance (round-trip mode preserves anchors/aliases/comments)
_yaml = YAML()
_yaml.default_flow_style = False
_yaml.allow_unicode = True
_yaml.width = config.yaml_line_width

# Valid component names for inline-format detection
_VALID_NAMES = frozenset({
    "site", "page",
    "layout-row", "layout-column", "columnsgrid", "form",
    "heading", "paragraph", "eyebrow", "caption", "blockquote", "link",
    "image", "video", "gif", "video-background", "br",
    "button", "titlebar", "hamburger",
    "tabs", "accordion", "carousel", "ticker", "panorama-display",
    "icon", "badge", "rating", "progress-bar", "counter-up", "countdown",
    "textbox", "textarea", "dropdown", "checkbox", "radio", "calendar",
})

# Keys that are array properties at component level, not inside properties
_ARRAY_KEYS = {"items", "tabs", "slides", "columns"}
_CHILD_KEYS = {"components", "children"}

# Keys that belong inside `properties:`, not at component level
_PROPERTY_KEYS = {
    "layout", "appearance", "spacing", "typography", "label", "field",
    "behavior", "source", "playback", "responsive", "scroll",
    "branding", "navigation", "submit", "display", "action",
    "content", "animation", "poster",
}


def _fix_structure(node):
    """Recursively fix common LLM structural errors in parsed YAML.

    Fixes:
    1. Inline component format: {layout-row: {props}} → {name: layout-row, properties: {props}}
    2. children → components
    3. Array props (items/tabs/slides/columns) inside properties → move to component level
    4. Properties outside properties wrapper → move inside
    5. Icon names as component names → convert to name: icon with properties.name
    """
    if isinstance(node, list):
        fixed = []
        for item in node:
            result = _fix_structure(item)
            if result is not None:
                fixed.append(result)
        return fixed
    if not isinstance(node, dict):
        return node

    # Fix 1: Inline component format
    if "name" not in node:
        for key in list(node.keys()):
            if key in _VALID_NAMES:
                props = node.pop(key)
                node["name"] = key
                if isinstance(props, dict):
                    for ak in _ARRAY_KEYS | _CHILD_KEYS:
                        if ak in props:
                            target = "components" if ak in _CHILD_KEYS else ak
                            node[target] = props.pop(ak)
                    if props:
                        node["properties"] = props
                break

    # Fix 2: children → components
    if "children" in node:
        existing = node.get("components", [])
        children = node.pop("children")
        if isinstance(children, list):
            if isinstance(existing, list) and existing:
                existing.extend(children)
                node["components"] = existing
            else:
                node["components"] = children

    # Fix 3: Array props inside properties → move to component level
    if "properties" in node and isinstance(node["properties"], dict):
        for key in list(_ARRAY_KEYS):
            if key in node["properties"]:
                node[key] = node["properties"].pop(key)

    # Fix 4: Properties outside `properties:` wrapper → move inside
    if "name" in node:
        orphaned = {k: node[k] for k in list(node.keys()) if k in _PROPERTY_KEYS}
        if orphaned:
            props = node.setdefault("properties", {})
            if isinstance(props, dict):
                for k, v in orphaned.items():
                    props.setdefault(k, v)
                    del node[k]

    # Fix 5: Container key mismatches
    if "name" in node:
        comp_name = node["name"]

        # layout-row/layout-column: `columns:` list → `components:`
        if comp_name in ("layout-row", "layout-column") and "columns" in node and isinstance(node["columns"], list):
            node["components"] = node.pop("columns")
            logger.debug(f"Fixed {comp_name}: columns → components")

        # columnsgrid/ticker: `components:` → `columns:`
        if comp_name in ("columnsgrid", "ticker") and "components" in node and isinstance(node["components"], list):
            node["columns"] = node.pop("components")
            logger.debug(f"Fixed {comp_name}: components → columns")

        # columnsgrid: `columns: <int>` at root → move to properties.layout.columns
        if comp_name == "columnsgrid" and "columns" in node and isinstance(node["columns"], int):
            col_count = node.pop("columns")
            props = node.setdefault("properties", {})
            if isinstance(props, dict):
                layout = props.setdefault("layout", {})
                if isinstance(layout, dict):
                    layout.setdefault("columns", col_count)
            logger.debug(f"Fixed columnsgrid: columns={col_count} → properties.layout.columns")

        # tabs: `items:` → `tabs:`
        if comp_name == "tabs" and "items" in node and "tabs" not in node:
            node["tabs"] = node.pop("items")
            logger.debug("Fixed tabs: items → tabs")

        # accordion: `tabs:` → `items:`
        if comp_name == "accordion" and "tabs" in node and "items" not in node:
            node["items"] = node.pop("tabs")
            logger.debug("Fixed accordion: tabs → items")

        # carousel: `items:` → `slides:`
        if comp_name == "carousel" and "items" in node and "slides" not in node:
            node["slides"] = node.pop("items")
            logger.debug("Fixed carousel: items → slides")

        # Coerce widthMode to string (YAML may parse 33 as int)
        if "properties" in node and isinstance(node["properties"], dict):
            layout = node["properties"].get("layout")
            if isinstance(layout, dict) and "widthMode" in layout:
                layout["widthMode"] = str(layout["widthMode"])

    # Fix 6: Icon names used as component names
    if "name" in node and node["name"] not in _VALID_NAMES:
        icon_name = node["name"]
        props = node.get("properties", {})
        has_icon_props = isinstance(props, dict) and any(
            k in props for k in ("size", "color", "weight", "name")
        )
        has_no_children = not any(k in node for k in ("components", "items", "tabs", "slides", "columns"))
        if has_icon_props or has_no_children:
            node["name"] = "icon"
            if not isinstance(props, dict):
                props = {}
            props["name"] = icon_name
            node["properties"] = props
            logger.debug(f"Fixed icon: '{icon_name}' → name: icon, properties.name: {icon_name}")

    # Recurse into all nested structures
    for key in ("components", "items", "tabs", "slides", "columns"):
        if key in node and isinstance(node[key], list):
            node[key] = _fix_structure(node[key])

    return node


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
          transparency: 100
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

        try:
            parsed = pyyaml.safe_load(resolved)
            if parsed is None:
                logger.warning(f"Section {i} produced empty YAML after parsing, skipping")
                continue
            # Fix structural issues from LLM output
            parsed = _fix_structure(parsed)
            if isinstance(parsed, list):
                page_components.extend(parsed)
            elif isinstance(parsed, dict):
                page_components.append(parsed)
            logger.info(f"Section {i} stitched successfully ({type(parsed).__name__})")
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

    logger.info(f"Stitcher final output ({len(result)} chars)")
    return result
