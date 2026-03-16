"""
Fix image/gif minHeight values that were specified in px but are rendered as rem.

Values > 50 are clearly px-intended (e.g., 200px -> 200rem = 3200px is way too tall).
Convert them to their rem equivalent by dividing by 16.

Conversion table:
  80px  -> 5rem
  100px -> 6.25rem
  120px -> 7.5rem
  150px -> 9.375rem
  180px -> 11.25rem
  200px -> 12.5rem
  280px -> 17.5rem
  300px -> 18.75rem
  400px -> 25rem
  500px -> 31.25rem
  600px -> 37.5rem

Usage:
    python fix_image_heights.py <directory>
"""

import sys
import os
import glob
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

PX_THRESHOLD = 50  # Values above this are px-intended


def fix_heights(node, changes):
    """Recursively fix minHeight values in appearance blocks."""
    if isinstance(node, list):
        for item in node:
            fix_heights(item, changes)
        return

    if not isinstance(node, CommentedMap):
        return

    comp_name = node.get('name', '')
    props = node.get('properties')

    if isinstance(props, CommentedMap):
        appearance = props.get('appearance')
        if isinstance(appearance, CommentedMap):
            for key in ('minHeight', 'maxHeight'):
                val = appearance.get(key)
                if val is not None and isinstance(val, (int, float)) and val > PX_THRESHOLD:
                    rem_val = val / 16
                    # Use clean number if possible
                    if rem_val == int(rem_val):
                        rem_val = int(rem_val)
                    appearance[key] = rem_val
                    changes.append(f"  {comp_name}: {key} {val} -> {rem_val}")

    # Recurse
    for key in ('components', 'columns', 'tabs', 'slides', 'items'):
        children = node.get(key)
        if not children or not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, CommentedMap):
                if key in ('columns', 'slides', 'tabs', 'items') and 'components' in child:
                    fix_heights(child['components'], changes)
                elif key == 'components':
                    fix_heights(child, changes)


def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
    except Exception:
        return []

    if data is None:
        return []

    changes = []
    fix_heights(data, changes)

    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    return changes


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_image_heights.py <directory>")
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

    print(f"\nDone: {total} height values fixed")


if __name__ == '__main__':
    main()
