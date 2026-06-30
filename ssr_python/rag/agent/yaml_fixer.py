"""ssr_python/rag/agent/yaml_fixer.py — Consolidated YAML validation and auto-fix pipeline.

Single source of truth for all YAML validation constants, error detection,
structural fixes, and auto-repair logic. Used by rag_agent.py and stitcher.py.
"""
import difflib
import logging
import re

import yaml as pyyaml

logger = logging.getLogger(__name__)

# ── Valid Component Names ──
# Authoritative list from _dispatcher.html — anything not in this set is invalid.
VALID_COMPONENTS = frozenset({
    "site", "page",
    "layout-row", "layout-column", "columnsgrid", "form",
    "heading", "paragraph", "eyebrow", "caption", "blockquote", "link",
    "image", "video", "gif", "video-background", "br",
    "button", "titlebar", "hamburger",
    "tabs", "accordion", "carousel", "ticker", "panorama-display",
    "icon", "badge", "rating", "progress-bar", "counter-up", "countdown",
    "textbox", "textarea", "dropdown", "checkbox", "radio", "calendar",
})

# ── Valid Token Value Sets ──
# Sourced from schema_tokens.yaml — the authoritative token definitions.

VALID_WIDTH_MODES = frozenset({
    "stretch", "fit", "16", "25", "33", "50", "66", "75", "83",
})

VALID_TICKER_WIDTHS = frozenset({
    "fit", "120", "200", "280", "360", "480",
})

VALID_TYPOGRAPHY_SIZES = frozenset({
    "xxs", "xs", "sm", "md", "lg", "xl", "xxl", "xxxl", "auto",
})

VALID_FONT_WEIGHTS = frozenset({
    "light", "regular", "medium", "semibold", "bold", "extrabold",
})

VALID_SPACING = frozenset({
    "none", "xxs", "xs", "sm", "md", "lg", "xl", "xxl", "xxxl", "auto",
})

VALID_RADIUS = frozenset({
    "none", "xs", "sm", "md", "lg", "xl", "xxl", "pill",
})

VALID_SHADOW = frozenset({
    "none", "soft", "medium", "elevated", "dramatic", "retro",
})

# Map of (property_group, property_name) -> valid value set
TOKEN_VALIDATORS: dict[tuple[str, str], frozenset] = {
    ("layout", "widthMode"): VALID_WIDTH_MODES,
    ("layout", "gap"): VALID_SPACING,
    ("typography", "size"): VALID_TYPOGRAPHY_SIZES,
    ("typography", "weight"): VALID_FONT_WEIGHTS,
    ("appearance", "radius"): VALID_RADIUS,
    ("appearance", "shadow"): VALID_SHADOW,
    ("spacing", "paddingBlock"): VALID_SPACING,
    ("spacing", "paddingInline"): VALID_SPACING,
    ("spacing", "marginBlock"): VALID_SPACING,
    ("spacing", "marginInline"): VALID_SPACING,
}

# ── Component Nesting Rules ──

# Components that CANNOT contain children of any kind.
LEAF_COMPONENTS = frozenset({
    "button", "icon", "badge", "rating", "progress-bar", "counter-up",
    "countdown", "heading", "paragraph", "eyebrow", "caption", "blockquote",
    "link", "textbox", "textarea", "checkbox", "radio", "dropdown",
    "calendar", "video", "gif", "panorama-display", "br", "titlebar",
})

# Components that use a child array OTHER than `components:`.
SPECIAL_CHILD_KEYS: dict[str, str] = {
    "columnsgrid": "columns",
    "ticker": "columns",
    "tabs": "tabs",
    "accordion": "items",
    "carousel": "slides",
}

# All possible child array keys.
ALL_CHILD_KEYS = frozenset({"components", "columns", "tabs", "items", "slides", "links"})

# Keys that are array properties at component level, not inside properties
ARRAY_KEYS = frozenset({"items", "tabs", "slides", "columns"})
CHILD_KEYS = frozenset({"components", "children"})

# Keys that belong inside `properties:`, not at component level
PROPERTY_KEYS = frozenset({
    "layout", "appearance", "spacing", "typography", "label", "field",
    "behavior", "source", "playback", "responsive", "scroll",
    "branding", "navigation", "submit", "display", "action",
    "content", "animation", "poster",
})

# ── Auto-Fix Alias Maps ──

# Common LLM token mistakes → correct values (per token category)
TOKEN_ALIASES: dict[str, str] = {
    # widthMode numeric approximations
    "40": "33", "45": "50", "48": "50", "60": "66", "70": "66",
    "80": "83", "100": "stretch",
    # spacing long-form names
    "small": "sm", "medium": "md", "large": "lg",
    "extra-large": "xl", "extra-small": "xs",
    "x-small": "xs", "x-large": "xl", "xx-large": "xxl",
    "zero": "none",
    # Garbled spacing/size tokens (LLM concatenation errors)
    "xxlg": "xl", "xxmd": "md", "xxsm": "sm",
    "xlg": "xl", "xsm": "xs",
    "xxxs": "xxs", "xxxxl": "xxxl",
    "sml": "sm", "lrg": "lg", "med": "md",
    "xx40": "xxl", "xx50": "xxl",
    # font weight
    "normal": "regular", "thin": "light",
    "semi-bold": "semibold", "extra-bold": "extrabold", "black": "extrabold",
    # radius
    "full": "pill", "rounded": "md", "round": "pill",
    # shadow
    "light": "soft", "heavy": "dramatic",
}

# Numeric widthMode values to snap to nearest valid
_WIDTH_SNAP_VALUES = sorted([16, 25, 33, 50, 66, 75, 83])

# Common LLM component name mistakes → correct names
COMPONENT_ALIASES: dict[str, str] = {
    "row": "layout-row", "column": "layout-column", "col": "layout-column",
    "img": "image", "text": "paragraph", "p": "paragraph",
    "h1": "heading", "h2": "heading", "h3": "heading",
    "h4": "heading", "h5": "heading", "h6": "heading",
    "a": "link", "btn": "button",
    "divider": "br", "separator": "br", "hr": "br", "spacer": "br",
    "nav": "titlebar", "navbar": "titlebar", "header": "titlebar",
    "grid": "columnsgrid", "columns": "columnsgrid",
    "slider": "carousel", "slideshow": "carousel",
    "star-rating": "rating", "stars": "rating",
    "timer": "countdown", "count-up": "counter-up",
    "marquee": "ticker", "scroll": "ticker",
    "input": "textbox", "text-input": "textbox", "select": "dropdown",
    "check": "checkbox",
    "progress": "progress-bar",
    "video-bg": "video-background",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Detection functions — find errors without fixing them
# ═══════════════════════════════════════════════════════════════════════════════

def find_invalid_components(doc) -> set[str]:
    """Recursively walk YAML and find any component names not in VALID_COMPONENTS."""
    invalid = set()

    if isinstance(doc, list):
        for item in doc:
            invalid |= find_invalid_components(item)
    elif isinstance(doc, dict):
        name = doc.get("name")
        if name and name not in VALID_COMPONENTS:
            invalid.add(name)
        for key in ("components", "items", "tabs", "slides", "columns", "children"):
            if key in doc:
                invalid |= find_invalid_components(doc[key])

    return invalid


def find_structural_errors(doc) -> list[str]:
    """Recursively find structural errors (children, inline format, misplaced array props, orphaned properties)."""
    errors = []

    if isinstance(doc, list):
        for item in doc:
            errors.extend(find_structural_errors(item))
    elif isinstance(doc, dict):
        if "children" in doc:
            errors.append("'children:' used instead of 'components:'")
        if "name" not in doc:
            for key in doc:
                if key in VALID_COMPONENTS:
                    errors.append(f"inline format '- {key}:' instead of '- name: {key}'")
                    break
        if "properties" in doc and isinstance(doc["properties"], dict):
            for key in ("items", "tabs", "slides", "columns"):
                if key in doc["properties"]:
                    errors.append(f"'{key}' inside properties instead of component level")
        if "name" in doc:
            for key in doc:
                if key in PROPERTY_KEYS:
                    errors.append(f"'{key}' at component level — must be inside 'properties:'")
        for key in ("components", "items", "tabs", "slides", "columns", "children"):
            if key in doc and isinstance(doc[key], list):
                for item in doc[key]:
                    errors.extend(find_structural_errors(item))

    return errors


def find_token_errors(doc) -> list[str]:
    """Recursively find invalid design token values in parsed YAML."""
    errors = []

    if isinstance(doc, list):
        for item in doc:
            errors.extend(find_token_errors(item))
    elif isinstance(doc, dict):
        comp_name = doc.get("name", "?")
        props = doc.get("properties", {})
        if isinstance(props, dict):
            for (group, prop), valid_set in TOKEN_VALIDATORS.items():
                group_dict = props.get(group)
                if isinstance(group_dict, dict) and prop in group_dict:
                    val = group_dict[prop]
                    if isinstance(val, (str, int, float)):
                        str_val = str(val)
                        actual_set = valid_set
                        if group == "layout" and prop == "widthMode" and comp_name == "ticker":
                            actual_set = VALID_TICKER_WIDTHS
                        if str_val not in actual_set:
                            errors.append(
                                f"'{comp_name}' has invalid {group}.{prop}: '{str_val}' "
                                f"— valid: {', '.join(sorted(actual_set))}"
                            )

            _check_at_references(props, comp_name, errors)

        for key in ALL_CHILD_KEYS | {"children"}:
            child = doc.get(key)
            if isinstance(child, list):
                for item in child:
                    errors.extend(find_token_errors(item))

    return errors


def _check_at_references(obj, comp_name: str, errors: list[str]):
    """Detect '@reference' string literals that should be *color- YAML anchor aliases."""
    if isinstance(obj, str):
        if obj.startswith("@"):
            errors.append(
                f"'{comp_name}' has '@' reference '{obj}' — "
                f"use YAML anchor aliases like *color-primary instead"
            )
    elif isinstance(obj, dict):
        for v in obj.values():
            _check_at_references(v, comp_name, errors)
    elif isinstance(obj, list):
        for item in obj:
            _check_at_references(item, comp_name, errors)


def find_nesting_errors(doc) -> list[str]:
    """Check component nesting rules: leaf nodes, correct child keys, components-in-properties."""
    errors = []

    if isinstance(doc, list):
        for item in doc:
            errors.extend(find_nesting_errors(item))
    elif isinstance(doc, dict):
        comp_name = doc.get("name")

        if comp_name:
            if comp_name in LEAF_COMPONENTS:
                for key in ALL_CHILD_KEYS:
                    if key in doc:
                        errors.append(
                            f"'{comp_name}' is a leaf component and cannot have '{key}:'"
                        )

            if comp_name in SPECIAL_CHILD_KEYS and "components" in doc:
                expected = SPECIAL_CHILD_KEYS[comp_name]
                errors.append(
                    f"'{comp_name}' should use '{expected}:' not 'components:' for its children"
                )

            if "properties" in doc and isinstance(doc["properties"], dict):
                if "components" in doc["properties"]:
                    errors.append(
                        f"'{comp_name}' has 'components:' inside 'properties:' — "
                        f"move it to be a sibling of 'properties:'"
                    )

        for key in ALL_CHILD_KEYS | {"children"}:
            child = doc.get(key)
            if isinstance(child, list):
                for item in child:
                    errors.extend(find_nesting_errors(item))

    return errors


# ═══════════════════════════════════════════════════════════════════════════════
# Validation — combines all detection into a single check
# ═══════════════════════════════════════════════════════════════════════════════

def quick_validate(response: str) -> str | None:
    """Fast validation of LLM response. Returns error message string, or None if valid."""
    match = re.search(r"```(?:yaml)?\s*\n(.+?)```", response, re.DOTALL)
    if not match:
        if "site:" not in response and "- name:" not in response:
            return None  # Probably an EXPLAIN response, skip validation
        yaml_str = response
    else:
        yaml_str = match.group(1)

    try:
        doc = pyyaml.safe_load(yaml_str)
    except pyyaml.YAMLError as e:
        return f"YAML parse error: {e}"

    if doc is None:
        return "Empty YAML document"

    invalid = find_invalid_components(doc)
    if invalid:
        names_str = ", ".join(sorted(invalid))
        return (
            f"Invalid component names found: {names_str}. "
            f"Use ONLY valid SwiftSites components: "
            f"layout-row, layout-column, columnsgrid, heading, paragraph, eyebrow, "
            f"caption, blockquote, link, image, video, gif, button, titlebar, br, "
            f"icon, badge, rating, progress-bar, counter-up, countdown, tabs, "
            f"accordion, carousel, hamburger, ticker, textbox, textarea, dropdown, "
            f"checkbox, radio, calendar, video-background, panorama-display, form"
        )

    structural = find_structural_errors(doc)
    if structural:
        return (
            f"Structural errors: {'; '.join(structural[:3])}. "
            f"RULES: Use 'components:' not 'children:'. "
            f"Use '- name: X' format not '- X:'. "
            f"Put array props (items/tabs/slides/columns) at component level, not inside properties."
        )

    token_errors = find_token_errors(doc)
    if token_errors:
        return (
            f"Invalid token values: {'; '.join(token_errors[:3])}. "
            f"Use only valid design token values from the SwiftSites system."
        )

    nesting_errors = find_nesting_errors(doc)
    if nesting_errors:
        return (
            f"Nesting errors: {'; '.join(nesting_errors[:3])}. "
            f"RULES: Leaf components (button, heading, icon, etc.) cannot have children. "
            f"Use correct child key per component (tabs→tabs:, accordion→items:, carousel→slides:, "
            f"columnsgrid/ticker→columns:). 'components:' must be a sibling of 'name:', never inside 'properties:'."
        )

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Fix functions — repair errors in-place on parsed YAML dicts
# ═══════════════════════════════════════════════════════════════════════════════

def fix_structure(node):
    """Recursively fix common LLM structural errors in parsed YAML.

    Fixes:
    1. Inline component format: {layout-row: {props}} → {name: layout-row, properties: {props}}
    2. children → components
    3. Array props (items/tabs/slides/columns) inside properties → move to component level
    4. Properties outside properties wrapper → move inside
    5. Container key mismatches
    6. Icon names as component names → convert to name: icon with properties.name
    """
    if isinstance(node, list):
        fixed = []
        for item in node:
            result = fix_structure(item)
            if result is not None:
                fixed.append(result)
        return fixed
    if not isinstance(node, dict):
        return node

    # Fix 1: Inline component format
    if "name" not in node:
        for key in list(node.keys()):
            if key in VALID_COMPONENTS:
                props = node.pop(key)
                node["name"] = key
                if isinstance(props, dict):
                    for ak in ARRAY_KEYS | CHILD_KEYS:
                        if ak in props:
                            target = "components" if ak in CHILD_KEYS else ak
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
        for key in list(ARRAY_KEYS):
            if key in node["properties"]:
                node[key] = node["properties"].pop(key)

    # Fix 4: Properties outside `properties:` wrapper → move inside
    if "name" in node:
        orphaned = {k: node[k] for k in list(node.keys()) if k in PROPERTY_KEYS}
        if orphaned:
            props = node.setdefault("properties", {})
            if isinstance(props, dict):
                for k, v in orphaned.items():
                    props.setdefault(k, v)
                    del node[k]

    # Fix 5: Container key mismatches
    if "name" in node:
        comp_name = node["name"]

        if comp_name in ("layout-row", "layout-column") and "columns" in node and isinstance(node["columns"], list):
            node["components"] = node.pop("columns")
            logger.debug(f"Fixed {comp_name}: columns → components")

        if comp_name in ("columnsgrid", "ticker") and "components" in node and isinstance(node["components"], list):
            node["columns"] = node.pop("components")
            logger.debug(f"Fixed {comp_name}: components → columns")

        if comp_name == "columnsgrid" and "columns" in node and isinstance(node["columns"], int):
            col_count = node.pop("columns")
            props = node.setdefault("properties", {})
            if isinstance(props, dict):
                layout = props.setdefault("layout", {})
                if isinstance(layout, dict):
                    layout.setdefault("columns", col_count)
            logger.debug(f"Fixed columnsgrid: columns={col_count} → properties.layout.columns")

        if comp_name == "tabs" and "items" in node and "tabs" not in node:
            node["tabs"] = node.pop("items")
            logger.debug("Fixed tabs: items → tabs")

        if comp_name == "accordion" and "tabs" in node and "items" not in node:
            node["items"] = node.pop("tabs")
            logger.debug("Fixed accordion: tabs → items")

        if comp_name == "carousel" and "items" in node and "slides" not in node:
            node["slides"] = node.pop("items")
            logger.debug("Fixed carousel: items → slides")

        # Coerce widthMode to string (YAML may parse 33 as int)
        if "properties" in node and isinstance(node["properties"], dict):
            layout = node["properties"].get("layout")
            if isinstance(layout, dict) and "widthMode" in layout:
                layout["widthMode"] = str(layout["widthMode"])

    # Fix 6: Icon names used as component names
    if "name" in node and node["name"] not in VALID_COMPONENTS:
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
            node[key] = fix_structure(node[key])

    return node


def fix_component_names(node, fixes: list[str]) -> None:
    """In-place fix of invalid component names via alias map and fuzzy matching.

    Runs AFTER fix_structure (which handles icon-name-as-component).
    """
    if isinstance(node, list):
        for item in node:
            fix_component_names(item, fixes)
    elif isinstance(node, dict):
        name = node.get("name")
        if name and name not in VALID_COMPONENTS:
            # Try alias map first
            if name.lower() in COMPONENT_ALIASES:
                new_name = COMPONENT_ALIASES[name.lower()]
                fixes.append(f"component name '{name}' → '{new_name}' (alias)")
                node["name"] = new_name
            else:
                # Try fuzzy match
                matches = difflib.get_close_matches(name, VALID_COMPONENTS, n=1, cutoff=0.6)
                if matches:
                    new_name = matches[0]
                    fixes.append(f"component name '{name}' → '{new_name}' (fuzzy)")
                    node["name"] = new_name

        # Recurse
        for key in ("components", "items", "tabs", "slides", "columns"):
            if key in node and isinstance(node[key], list):
                fix_component_names(node[key], fixes)


def _snap_width_mode(val: str) -> str | None:
    """Snap a numeric widthMode value to the nearest valid value."""
    try:
        num = int(val)
    except (ValueError, TypeError):
        return None

    if num <= 0:
        return "fit"
    if num >= 100:
        return "stretch"

    # Find nearest valid width
    closest = min(_WIDTH_SNAP_VALUES, key=lambda v: abs(v - num))
    return str(closest)


def fix_token_values(node, fixes: list[str]) -> None:
    """In-place fix of invalid token values using alias map, snapping, and fuzzy matching."""
    if isinstance(node, list):
        for item in node:
            fix_token_values(item, fixes)
    elif isinstance(node, dict):
        comp_name = node.get("name", "?")
        props = node.get("properties", {})
        if isinstance(props, dict):
            for (group, prop), valid_set in TOKEN_VALIDATORS.items():
                group_dict = props.get(group)
                if not isinstance(group_dict, dict) or prop not in group_dict:
                    continue

                val = group_dict[prop]
                if not isinstance(val, (str, int, float)):
                    continue

                str_val = str(val)

                # Determine the correct valid set
                actual_set = valid_set
                if group == "layout" and prop == "widthMode" and comp_name == "ticker":
                    actual_set = VALID_TICKER_WIDTHS

                if str_val in actual_set:
                    continue  # Already valid

                old_val = str_val
                new_val = None

                # Strategy 1: Alias map
                lower_val = str_val.lower()
                if lower_val in TOKEN_ALIASES:
                    candidate = TOKEN_ALIASES[lower_val]
                    if candidate in actual_set:
                        new_val = candidate

                # Strategy 2: Numeric width snapping (for widthMode only)
                if new_val is None and group == "layout" and prop == "widthMode":
                    snapped = _snap_width_mode(str_val)
                    if snapped and snapped in actual_set:
                        new_val = snapped

                # Strategy 3: Extract valid token embedded in garbled value
                if new_val is None:
                    lower_str = str_val.lower()
                    for valid in sorted(actual_set, key=len, reverse=True):
                        if valid != "none" and len(valid) > 1 and valid in lower_str:
                            new_val = valid
                            break

                # Strategy 4: Fuzzy match
                if new_val is None:
                    matches = difflib.get_close_matches(
                        str_val.lower(), actual_set, n=1, cutoff=0.5
                    )
                    if matches:
                        new_val = matches[0]

                # Strategy 5: Default to a safe fallback
                if new_val is None:
                    if group == "spacing" or (group == "layout" and prop == "gap"):
                        new_val = "md"
                    elif group == "layout" and prop == "widthMode":
                        new_val = "stretch"
                    elif group == "typography" and prop == "size":
                        new_val = "md"
                    elif group == "typography" and prop == "weight":
                        new_val = "regular"
                    elif group == "appearance" and prop == "radius":
                        new_val = "none"
                    elif group == "appearance" and prop == "shadow":
                        new_val = "none"

                if new_val and new_val != str_val:
                    group_dict[prop] = new_val
                    fixes.append(f"{comp_name}.{group}.{prop}: '{old_val}' → '{new_val}'")

        # Recurse
        for key in ALL_CHILD_KEYS | {"children"}:
            child = node.get(key)
            if isinstance(child, list):
                fix_token_values(child, fixes)


def fix_layout_overflow(node, fixes: list[str]) -> None:
    """Detect split rows where gap + widthMode sum would cause overflow, and fix them.

    Pattern: layout-row with children whose numeric widthMode values sum to >= 100
    AND gap is xl/xxl/xxxl. Fix: downgrade gap to lg.
    """
    if isinstance(node, list):
        for item in node:
            fix_layout_overflow(item, fixes)
    elif isinstance(node, dict):
        comp_name = node.get("name")
        if comp_name == "layout-row":
            props = node.get("properties", {})
            layout = props.get("layout", {})
            if isinstance(layout, dict):
                gap = layout.get("gap", "md")
                children = node.get("components", [])
                width_sum = 0
                has_width = False
                for child in children:
                    if isinstance(child, dict):
                        child_props = child.get("properties", {})
                        child_layout = child_props.get("layout", {}) if isinstance(child_props, dict) else {}
                        wm = child_layout.get("widthMode", "") if isinstance(child_layout, dict) else ""
                        try:
                            width_sum += int(wm)
                            has_width = True
                        except (ValueError, TypeError):
                            pass

                if has_width and width_sum >= 100 and gap in ("xl", "xxl", "xxxl"):
                    layout["gap"] = "lg"
                    fixes.append(
                        f"layout-row: gap '{gap}' -> 'lg' "
                        f"(children sum {width_sum}% would overflow)"
                    )

        for key in ("components", "items", "tabs", "slides", "columns"):
            child = node.get(key)
            if isinstance(child, list):
                fix_layout_overflow(child, fixes)


_GRID_COMPONENTS = frozenset({"columnsgrid", "tabs", "accordion", "carousel"})


def fix_narrow_grid_parent(node, fixes: list[str]) -> None:
    """Fix layout-columns with widthMode '75' that contain grid components.

    The LLM often wraps an entire section (header + columnsgrid) in a single
    widthMode:'75' column, cramping the grid. Correct pattern: only header text
    should be narrow, grid should be full-width.
    """
    if isinstance(node, list):
        for item in node:
            fix_narrow_grid_parent(item, fixes)
    elif isinstance(node, dict):
        comp_name = node.get("name")
        if comp_name == "layout-column":
            props = node.get("properties", {})
            layout = props.get("layout", {})
            if isinstance(layout, dict):
                wm = str(layout.get("widthMode", ""))
                if wm == "75":
                    children = node.get("components", [])
                    has_grid = any(
                        isinstance(c, dict) and c.get("name") in _GRID_COMPONENTS
                        for c in children
                    )
                    if has_grid:
                        del layout["widthMode"]
                        fixes.append(
                            f"layout-column: removed widthMode '75' "
                            f"(contains grid component that needs full width)"
                        )

        for key in ("components", "items", "tabs", "slides", "columns"):
            child = node.get(key)
            if isinstance(child, list):
                fix_narrow_grid_parent(child, fixes)


def fix_nesting(node, fixes: list[str]) -> None:
    """In-place fix of nesting violations."""
    if isinstance(node, list):
        for item in node:
            fix_nesting(item, fixes)
    elif isinstance(node, dict):
        comp_name = node.get("name")

        if comp_name:
            # Fix 1: Remove child arrays from leaf components
            if comp_name in LEAF_COMPONENTS:
                for key in list(ALL_CHILD_KEYS):
                    if key in node:
                        node.pop(key)
                        fixes.append(f"removed '{key}:' from leaf component '{comp_name}'")

            # Fix 2: Wrong child key → correct key
            if comp_name in SPECIAL_CHILD_KEYS and "components" in node:
                expected = SPECIAL_CHILD_KEYS[comp_name]
                if expected not in node:
                    node[expected] = node.pop("components")
                    fixes.append(f"'{comp_name}': 'components:' → '{expected}:'")

            # Fix 3: components: inside properties: → move to component level
            if "properties" in node and isinstance(node["properties"], dict):
                if "components" in node["properties"]:
                    node["components"] = node["properties"].pop("components")
                    fixes.append(f"'{comp_name}': moved 'components:' out of 'properties:'")

        # Recurse into all child arrays
        for key in ALL_CHILD_KEYS:
            child = node.get(key)
            if isinstance(child, list):
                fix_nesting(child, fixes)


# ═══════════════════════════════════════════════════════════════════════════════
# Auto-fix pipeline — main entry point
# ═══════════════════════════════════════════════════════════════════════════════

def auto_fix_yaml(yaml_str: str) -> tuple[str, list[str]]:
    """Attempt to programmatically fix common YAML errors.

    Pipeline: parse → fix_structure → fix_component_names → fix_token_values → fix_nesting → re-serialize.

    Args:
        yaml_str: Raw YAML string (e.g. extracted from LLM response code block)

    Returns:
        (fixed_yaml_str, list_of_fixes_applied)
        If no fixes needed or fixing fails, returns (original_yaml_str, [])
    """
    # Parse
    try:
        doc = pyyaml.safe_load(yaml_str)
    except pyyaml.YAMLError:
        # Try basic line-level fixes before giving up
        cleaned = _fix_parse_errors(yaml_str)
        try:
            doc = pyyaml.safe_load(cleaned)
        except pyyaml.YAMLError:
            return yaml_str, []  # Can't parse, fall through to LLM retry

    if doc is None:
        return yaml_str, []

    fixes: list[str] = []

    # 1. Component name repair FIRST (before fix_structure converts unknowns to icons)
    fix_component_names(doc, fixes)

    # 2. Structural fixes (children→components, inline format, container keys, icons, etc.)
    original_repr = repr(doc)
    doc = fix_structure(doc)
    if repr(doc) != original_repr:
        fixes.append("structural fixes applied")

    # 3. Token value repair (aliases + snapping + fuzzy match)
    fix_token_values(doc, fixes)

    # 4. Layout overflow fix (split rows with large gap)
    fix_layout_overflow(doc, fixes)

    # 5. Narrow grid parent fix (columnsgrid inside widthMode:'75' column)
    fix_narrow_grid_parent(doc, fixes)

    # 6. Nesting fixes (leaf children, wrong child keys, components in properties)
    fix_nesting(doc, fixes)

    if not fixes:
        return yaml_str, []

    # Re-serialize
    fixed = pyyaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False)
    logger.info(f"Auto-fixed YAML ({len(fixes)} fixes): {fixes}")
    return fixed, fixes


def _fix_parse_errors(yaml_str: str) -> str:
    """Attempt line-level fixes for unparseable YAML."""
    lines = yaml_str.split("\n")
    fixed_lines = []
    for line in lines:
        # Replace tabs with spaces
        line = line.replace("\t", "  ")
        # Remove trailing commas after values
        line = re.sub(r",\s*$", "", line)
        fixed_lines.append(line)
    return "\n".join(fixed_lines)
