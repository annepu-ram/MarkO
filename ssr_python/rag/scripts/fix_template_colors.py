#!/usr/bin/env python
"""
Fix hardcoded hex colors in example_templates/ YAML files.

Adds YAML anchors to theme color definitions and replaces hardcoded hex
values with aliases throughout each template.

Usage:
    cd ssr_python
    python -m rag.scripts.fix_template_colors --dry-run   # Preview changes
    python -m rag.scripts.fix_template_colors              # Apply changes
"""
import re
import os
import sys
import glob
import argparse
from collections import Counter

# ── Config ──────────────────────────────────────────────────────────────────

# The 5 core theme color keys -> anchor names
THEME_KEYS = {
    "primary": "color-primary",
    "text": "color-text",
    "secondary": "color-secondary",
    "accent": "color-accent",
    "background": "color-background",
}

# Common border/surface colors to add as custom anchors if found 2+ times
COMMON_COLORS = {
    "#e5e7eb": "color-border",
    "#d1d5db": "color-border-light",
}

# Lines containing these patterns are skipped (never replaced)
SKIP_LINE_PATTERNS = [
    re.compile(r"&color-"),       # anchor definitions
    re.compile(r"\*color-"),      # already aliased
    re.compile(r"placehold\.co"), # placeholder URLs with colors
    re.compile(r"colorStart"),    # gradient start
    re.compile(r"colorEnd"),      # gradient end
    re.compile(r"rgba\("),        # rgba values
]

# Regex to find hex colors (quoted)
HEX_QUOTED = re.compile(
    r"""(?P<prefix>['"])(?P<hex>#[0-9a-fA-F]{3,8})(?P=prefix)"""
)

# Regex to find theme color lines (with or without anchors)
# Matches: "  primary: &color-primary '#111827'" or "  primary: '#111827'"
THEME_LINE = re.compile(
    r"^(?P<indent>\s+)"
    r"(?P<key>primary|text|secondary|accent|background)"
    r":\s+"
    r"(?:&color-\w+\s+)?"  # optional existing anchor
    r"(?P<quote>['\"])"
    r"(?P<hex>#[0-9a-fA-F]{3,8})"
    r"(?P=quote)"
    r"\s*$"
)


def extract_theme_colors(lines):
    """Extract theme color definitions and their line indices.

    Returns:
        dict: {hex_lower: (alias_name, line_index)}
    """
    colors = {}
    in_colors_block = False
    colors_indent = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect "colors:" block start
        if stripped == "colors:" or stripped.startswith("colors:"):
            in_colors_block = True
            # Measure the indent of "colors:" to know when we leave
            colors_indent = len(line) - len(line.lstrip())
            continue

        if in_colors_block:
            if stripped == "" or stripped.startswith("#"):
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= colors_indent and stripped:
                in_colors_block = False
                continue

            m = THEME_LINE.match(line)
            if m:
                key = m.group("key")
                hex_val = m.group("hex").lower()
                anchor_name = THEME_KEYS.get(key, f"color-{key}")
                colors[hex_val] = (anchor_name, i)

    return colors


def add_anchors_to_theme(lines, theme_colors):
    """Add missing &color-X anchors to theme color definition lines.

    Returns:
        list: modified lines
        int: number of anchors added
    """
    new_lines = list(lines)
    added = 0

    for hex_val, (anchor_name, line_idx) in theme_colors.items():
        line = new_lines[line_idx]
        # Already has an anchor? Skip
        if f"&{anchor_name}" in line:
            continue

        m = THEME_LINE.match(line)
        if not m:
            continue

        indent = m.group("indent")
        key = m.group("key")
        quote = m.group("quote")
        hex_orig = m.group("hex")

        new_line = f"{indent}{key}: &{anchor_name} {quote}{hex_orig}{quote}\n"
        new_lines[line_idx] = new_line
        added += 1

    return new_lines, added


def find_common_unanchored(lines, theme_hexes):
    """Find common border/surface colors not in theme that appear 2+ times.

    Returns:
        dict: {hex_lower: anchor_name} for colors to add
    """
    hex_counts = Counter()
    for line in lines:
        if any(p.search(line) for p in SKIP_LINE_PATTERNS):
            continue
        for m in HEX_QUOTED.finditer(line):
            h = m.group("hex").lower()
            if h not in theme_hexes:
                hex_counts[h] += 1

    result = {}
    for hex_val, anchor_name in COMMON_COLORS.items():
        if hex_counts.get(hex_val, 0) >= 2:
            result[hex_val] = anchor_name

    return result


def insert_new_anchors(lines, new_anchors, theme_colors):
    """Insert new anchor definitions into the theme colors block.

    Inserts right after the last existing theme color line.
    """
    if not new_anchors:
        return lines, 0

    # Find the last theme color line
    last_theme_line = max(idx for _, idx in theme_colors.values())

    # Determine indent from that line
    m = THEME_LINE.match(lines[last_theme_line])
    indent = m.group("indent") if m else "        "

    # Build new anchor lines
    insert_lines = []
    for hex_val, anchor_name in new_anchors.items():
        insert_lines.append(f"{indent}{anchor_name.replace('color-', '')}: &{anchor_name} '{hex_val}'\n")

    new_lines = list(lines)
    for j, insert_line in enumerate(insert_lines):
        new_lines.insert(last_theme_line + 1 + j, insert_line)

    return new_lines, len(insert_lines)


def replace_hex_with_aliases(lines, color_map):
    """Replace hardcoded hex values with YAML aliases.

    Args:
        lines: list of line strings
        color_map: {hex_lower: alias_name} e.g. {'#111827': 'color-primary'}

    Returns:
        list: modified lines
        int: number of replacements made
    """
    new_lines = []
    total_replacements = 0

    for line in lines:
        # Skip lines that shouldn't be modified
        if any(p.search(line) for p in SKIP_LINE_PATTERNS):
            new_lines.append(line)
            continue

        replaced_line = line
        line_replacements = 0

        for hex_val, anchor_name in color_map.items():
            alias = f"*{anchor_name}"

            # Replace quoted hex with unquoted alias
            # Match both 'HEX' and "HEX" (case-insensitive)
            def replace_match(m):
                nonlocal line_replacements
                found_hex = m.group("hex").lower()
                if found_hex == hex_val:
                    line_replacements += 1
                    return alias
                return m.group(0)

            replaced_line = HEX_QUOTED.sub(replace_match, replaced_line)

        new_lines.append(replaced_line)
        total_replacements += line_replacements

    return new_lines, total_replacements


def process_file(filepath, dry_run=False):
    """Process a single YAML file. Returns (anchors_added, replacements, new_anchors)."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Step 1: Extract theme colors
    theme_colors = extract_theme_colors(lines)
    if not theme_colors:
        return 0, 0, 0  # No theme block -> skip

    # Step 2: Add missing anchors to theme definitions
    lines, anchors_added = add_anchors_to_theme(lines, theme_colors)

    # Step 3: Find common unanchored colors (borders/surfaces)
    theme_hexes = set(theme_colors.keys())
    common = find_common_unanchored(lines, theme_hexes)
    lines, new_anchor_count = insert_new_anchors(lines, common, theme_colors)

    # Re-extract after possible line insertions
    if new_anchor_count > 0:
        theme_colors = extract_theme_colors(lines)

    # Step 4: Build full color map for replacement
    color_map = {}
    for hex_val, (anchor_name, _) in theme_colors.items():
        color_map[hex_val] = anchor_name

    # Step 5: Replace hardcoded hex with aliases
    lines, replacements = replace_hex_with_aliases(lines, color_map)

    if not dry_run and (anchors_added > 0 or replacements > 0 or new_anchor_count > 0):
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return anchors_added, replacements, new_anchor_count


def main():
    parser = argparse.ArgumentParser(description="Fix hardcoded colors in YAML templates")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    # Find all YAML files
    base = os.path.join(os.path.dirname(__file__), "..", "..", "..", "example_templates")
    base = os.path.normpath(base)

    if not os.path.isdir(base):
        print(f"ERROR: Directory not found: {base}")
        sys.exit(1)

    yaml_files = sorted(glob.glob(os.path.join(base, "**", "*.yaml"), recursive=True))
    print(f"Found {len(yaml_files)} YAML files in {base}")

    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    total_files_changed = 0
    total_anchors = 0
    total_replacements = 0
    total_new_anchors = 0

    for filepath in yaml_files:
        rel = os.path.relpath(filepath, base)
        anchors, replacements, new_anchors = process_file(filepath, dry_run=args.dry_run)

        if anchors > 0 or replacements > 0 or new_anchors > 0:
            total_files_changed += 1
            total_anchors += anchors
            total_replacements += replacements
            total_new_anchors += new_anchors
            print(f"  {rel}: +{anchors} anchors, +{new_anchors} new anchors, {replacements} replacements")

    print(f"\n{'DRY RUN ' if args.dry_run else ''}SUMMARY:")
    print(f"  Files changed: {total_files_changed} / {len(yaml_files)}")
    print(f"  Anchors added to theme: {total_anchors}")
    print(f"  New custom anchors: {total_new_anchors}")
    print(f"  Hex -> alias replacements: {total_replacements}")


if __name__ == "__main__":
    main()
