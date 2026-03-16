"""
Migrate YAML template properties for consistency:
1. appearance.padding.block/inline → spacing.paddingBlock/paddingInline
2. Ticker: spacing.gap → layout.gap
3. Ticker: layout.width → layout.widthMode

Uses ruamel.yaml to preserve comments, anchors, flow style, and indentation.

Usage:
    python migrate_properties.py <directory>
    python migrate_properties.py ../example_templates/
"""

import sys
import glob
import os
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096  # prevent line wrapping


def migrate_padding(props):
    """Move appearance.padding.block/inline → spacing.paddingBlock/paddingInline"""
    if not isinstance(props, CommentedMap):
        return False

    appearance = props.get('appearance')
    if not isinstance(appearance, CommentedMap):
        return False

    padding = appearance.get('padding')
    if not isinstance(padding, (CommentedMap, dict)):
        return False

    block_val = padding.get('block')
    inline_val = padding.get('inline')

    if block_val is None and inline_val is None:
        return False

    # Ensure spacing dict exists
    if 'spacing' not in props:
        props['spacing'] = CommentedMap()
    spacing = props['spacing']
    if not isinstance(spacing, CommentedMap):
        spacing = CommentedMap()
        props['spacing'] = spacing

    # Only migrate if spacing doesn't already have these keys
    changed = False
    if block_val is not None and 'paddingBlock' not in spacing:
        spacing['paddingBlock'] = block_val
        changed = True
    if inline_val is not None and 'paddingInline' not in spacing:
        spacing['paddingInline'] = inline_val
        changed = True

    if changed or (block_val is not None or inline_val is not None):
        # Remove padding from appearance
        del appearance['padding']
        # Clean up empty appearance
        if len(appearance) == 0:
            del props['appearance']
        return True

    return False


def migrate_ticker_gap(props):
    """Move spacing.gap → layout.gap for ticker components"""
    if not isinstance(props, CommentedMap):
        return False

    spacing = props.get('spacing')
    if not isinstance(spacing, CommentedMap):
        return False

    gap_val = spacing.get('gap')
    if gap_val is None:
        return False

    # Ensure layout dict exists
    if 'layout' not in props:
        props['layout'] = CommentedMap()
    layout = props['layout']
    if not isinstance(layout, CommentedMap):
        layout = CommentedMap()
        props['layout'] = layout

    if 'gap' not in layout:
        layout['gap'] = gap_val

    del spacing['gap']
    # Clean up empty spacing
    if len(spacing) == 0:
        del props['spacing']

    return True


def migrate_ticker_width(props):
    """Rename layout.width → layout.widthMode for ticker components"""
    if not isinstance(props, CommentedMap):
        return False

    layout = props.get('layout')
    if not isinstance(layout, CommentedMap):
        return False

    if 'width' not in layout:
        return False
    if 'widthMode' in layout:
        # Already migrated, just remove old key
        del layout['width']
        return True

    width_val = layout['width']
    # Insert widthMode at same position, then delete width
    layout['widthMode'] = width_val
    del layout['width']
    return True


def walk_components(node, parent_name=None):
    """Recursively walk all components in the YAML structure."""
    changes = 0

    if isinstance(node, list):
        for item in node:
            changes += walk_components(item, parent_name)
        return changes

    if not isinstance(node, CommentedMap):
        return changes

    comp_name = node.get('name', '')
    props = node.get('properties')

    if isinstance(props, CommentedMap):
        # Fix 1: Padding migration (all components)
        if migrate_padding(props):
            changes += 1

        # Fix 2 & 3: Ticker-specific fixes
        if comp_name == 'ticker':
            if migrate_ticker_gap(props):
                changes += 1
            if migrate_ticker_width(props):
                changes += 1

    # Recurse into children
    components = node.get('components')
    if components:
        changes += walk_components(components, comp_name)

    # Handle columnsgrid/ticker columns
    columns = node.get('columns')
    if columns and isinstance(columns, list):
        for col in columns:
            if isinstance(col, CommentedMap):
                col_components = col.get('components')
                if col_components:
                    changes += walk_components(col_components, comp_name)

    # Handle tabs
    tabs = node.get('tabs')
    if tabs and isinstance(tabs, list):
        for tab in tabs:
            if isinstance(tab, CommentedMap):
                tab_components = tab.get('components')
                if tab_components:
                    changes += walk_components(tab_components, comp_name)

    return changes


def migrate_file(filepath):
    """Migrate a single YAML file. Returns number of changes made."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
    except Exception as e:
        print(f"  SKIP (parse error): {filepath} - {str(e)[:60]}")
        return -1

    if data is None:
        return 0

    changes = walk_components(data)

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    return changes


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_properties.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    files = glob.glob(os.path.join(directory, '**', '*.yaml'), recursive=True)

    total_changes = 0
    files_changed = 0
    files_skipped = 0

    for filepath in sorted(files):
        changes = migrate_file(filepath)
        if changes < 0:
            files_skipped += 1
        elif changes > 0:
            total_changes += changes
            files_changed += 1
            print(f"  MIGRATED ({changes} changes): {filepath}")

    print(f"\nDone: {files_changed} files changed, {total_changes} total changes, {files_skipped} skipped")


if __name__ == '__main__':
    main()
