"""
Fix invalid token values and structural errors in YAML template files.

Fixes:
1. Shadow values: sm→soft, md→medium, lg→elevated, xl→dramatic, CSS strings→medium
2. Width values: 30→33, 40→33, 48→50, 60→66, 70→75, percentage→stretch
3. Structural: move tabs/slides/items from inside properties to component level

Usage:
    python fix_template_values.py <directory>
"""

import sys
import os
import glob
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

SHADOW_MAP = {
    'sm': 'soft',
    'md': 'medium',
    'lg': 'elevated',
    'xl': 'dramatic',
}

WIDTH_MAP = {
    '30': '33',
    '40': '33',
    '48': '50',
    '60': '66',
    '70': '75',
    'percentage': 'stretch',
}

STRUCTURAL_KEYS = ('tabs', 'slides', 'items')


def fix_component(node, changes, filepath):
    """Fix a single component node."""
    if not isinstance(node, CommentedMap):
        return

    comp_name = node.get('name', '?')
    props = node.get('properties')

    if isinstance(props, CommentedMap):
        # Fix shadow values
        appearance = props.get('appearance')
        if isinstance(appearance, CommentedMap):
            shadow = appearance.get('shadow')
            if shadow is not None and isinstance(shadow, str):
                if shadow in SHADOW_MAP:
                    appearance['shadow'] = SHADOW_MAP[shadow]
                    changes.append(f"  {comp_name}: shadow '{shadow}' -> '{SHADOW_MAP[shadow]}'")
                elif shadow not in ('none', 'soft', 'medium', 'elevated', 'dramatic', 'retro'):
                    # CSS string or other invalid value
                    appearance['shadow'] = 'medium'
                    changes.append(f"  {comp_name}: shadow '{shadow}' -> 'medium' (was CSS/invalid)")

        # Fix width values
        layout = props.get('layout')
        if isinstance(layout, CommentedMap):
            width_mode = layout.get('widthMode')
            if width_mode is not None:
                w_str = str(width_mode)
                if w_str in WIDTH_MAP:
                    layout['widthMode'] = WIDTH_MAP[w_str]
                    changes.append(f"  {comp_name}: widthMode '{w_str}' -> '{WIDTH_MAP[w_str]}'")

        # Fix structural: move tabs/slides/items from properties to component level
        for key in STRUCTURAL_KEYS:
            if key in props:
                val = props[key]
                node[key] = val
                del props[key]
                changes.append(f"  {comp_name}: moved '{key}' from properties to component level")

    # Recurse into children
    for key in ('components', 'columns', 'tabs', 'slides', 'items'):
        children = node.get(key)
        if not children or not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, CommentedMap):
                if key in ('columns', 'slides', 'tabs', 'items') and 'components' in child:
                    for sub in child['components']:
                        fix_component(sub, changes, filepath)
                elif key == 'components':
                    fix_component(child, changes, filepath)
                # Also check if the child itself is a component (has 'name')
                if 'name' in child:
                    fix_component(child, changes, filepath)


def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
    except Exception as e:
        return [f"  ERROR loading: {e}"]

    if data is None:
        return []

    changes = []

    # Handle top-level list or dict with components
    if isinstance(data, list):
        for item in data:
            fix_component(item, changes, filepath)
    elif isinstance(data, CommentedMap):
        # Could be a page-level structure
        fix_component(data, changes, filepath)
        comps = data.get('components')
        if isinstance(comps, list):
            for item in comps:
                fix_component(item, changes, filepath)

    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    return changes


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_template_values.py <directory>")
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
