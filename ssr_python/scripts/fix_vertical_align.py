"""
Fix vertical alignment in layout-row/layout-column templates.

Problem: `layout.align` on layout-row/layout-column is dead code — the engine
skips it in build_styles (_utilities.html:22). The actual property is
`layout.verticalAlign` (used by build_flex_styles). Many templates set
`align: center` thinking it vertically centers children — it doesn't.

This script:
1. For layout-row: migrates layout.align -> layout.verticalAlign (if not set),
   then deletes layout.align
2. For layout-column: deletes layout.align (dead code)
3. For banner-pattern rows (text-only children): ensures verticalAlign: center

Usage:
    python fix_vertical_align.py <directory>
"""

import sys
import os
import glob

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

# Text-type components (banner children)
TEXT_COMPONENTS = {
    'paragraph', 'heading', 'eyebrow', 'caption', 'link',
    'button', 'badge', 'icon',
}


def is_banner_row(node):
    """Check if a layout-row contains only text-type children (banner pattern)."""
    comps = node.get('components')
    if not comps or not isinstance(comps, list):
        return False
    if len(comps) < 1:
        return False
    return all(
        isinstance(c, CommentedMap) and c.get('name', '') in TEXT_COMPONENTS
        for c in comps
    )


def fix_component(node, changes):
    """Fix a single component node and recurse."""
    if not isinstance(node, CommentedMap):
        return

    comp_name = node.get('name', '')
    props = node.get('properties')

    if isinstance(props, CommentedMap):
        layout = props.get('layout')
        if isinstance(layout, CommentedMap) and comp_name in ('layout-row', 'layout-column'):
            align_val = layout.get('align')

            if comp_name == 'layout-row':
                # Migrate align -> verticalAlign if verticalAlign not set
                if align_val is not None and 'verticalAlign' not in layout:
                    layout['verticalAlign'] = align_val
                    changes.append(f"  {comp_name}: migrated align='{align_val}' -> verticalAlign")

                # Delete dead align property
                if 'align' in layout:
                    del layout['align']
                    changes.append(f"  {comp_name}: removed dead layout.align")

                # For banner-pattern rows, ensure verticalAlign: center
                if is_banner_row(node):
                    current_va = layout.get('verticalAlign')
                    if current_va != 'center':
                        layout['verticalAlign'] = 'center'
                        changes.append(f"  {comp_name} (banner): set verticalAlign=center (was '{current_va}')")

            elif comp_name == 'layout-column':
                # Just delete dead align property
                if 'align' in layout:
                    del layout['align']
                    changes.append(f"  {comp_name}: removed dead layout.align")

    # Recurse into children
    for key in ('components', 'columns', 'tabs', 'slides', 'items'):
        children = node.get(key)
        if not children or not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, CommentedMap):
                if 'name' in child:
                    fix_component(child, changes)
                if key in ('columns', 'slides', 'tabs', 'items') and 'components' in child:
                    for sub in child['components']:
                        if isinstance(sub, CommentedMap):
                            fix_component(sub, changes)


def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
    except Exception as e:
        return [f"  ERROR loading: {e}"]

    if data is None:
        return []

    changes = []

    if isinstance(data, list):
        for item in data:
            fix_component(item, changes)
    elif isinstance(data, CommentedMap):
        fix_component(data, changes)
        comps = data.get('components')
        if isinstance(comps, list):
            for item in comps:
                fix_component(item, changes)

    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    return changes


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_vertical_align.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    files = glob.glob(os.path.join(directory, '**', '*.yaml'), recursive=True)

    total = 0
    for filepath in sorted(files):
        changes = fix_file(filepath)
        if changes:
            print(f"FIXED: {filepath}")
            for c in changes:
                print(c)
            total += len(changes)

    print(f"\nDone: {total} fixes applied")


if __name__ == '__main__':
    main()
