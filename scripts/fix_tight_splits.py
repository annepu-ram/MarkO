"""
Fix layout-rows with 33%/25% width children:
1. Ensure wrap: wrap
2. Reduce gap > md to md
3. Reduce row paddingInline > md to md
4. Reduce child paddingInline > md to md

Uses text-based line scanning to preserve YAML formatting and anchors.
"""

import re
import os
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "example_templates"

TOO_LARGE = {"lg", "xl", "xxl", "xxxl"}
TARGET_WIDTHS = {"33", "25", "16"}


def find_layout_rows_with_tight_children(lines):
    """
    Find layout-row blocks whose children have widthMode: "33" or "25".
    Returns list of (row_start_line, row_indent, children_lines) tuples.
    """
    results = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Find "- name: layout-row"
        match = re.match(r'^(\s*)- name: layout-row\s*$', line)
        if match:
            row_indent = len(match.group(1))
            row_start = i
            # Scan forward to find this row's children and their widthModes
            has_tight_child = False
            row_block_end = i + 1
            # Find the extent of this row block (until next sibling at same indent)
            for j in range(i + 1, len(lines)):
                stripped = lines[j].strip()
                if not stripped:
                    row_block_end = j + 1
                    continue
                line_indent = len(lines[j]) - len(lines[j].lstrip())
                if line_indent <= row_indent and stripped.startswith('- name:'):
                    break
                if line_indent <= row_indent and not stripped.startswith('#'):
                    break
                row_block_end = j + 1
                # Check for widthMode in children
                wm_match = re.search(r'widthMode:\s*["\']?(33|25|16)["\']?', lines[j])
                if wm_match:
                    has_tight_child = True

            if has_tight_child:
                results.append((row_start, row_indent, row_block_end))
            i = row_block_end
        else:
            i += 1

    return results


def fix_row_block(lines, row_start, row_indent, row_end):
    """Fix wrap, gap, and paddingInline within a layout-row block."""
    changes = []

    # Find the layout: and spacing: sections of THIS row (not children)
    # Row properties are at indent row_indent + 2 (after "- name: layout-row")
    prop_indent = row_indent + 4  # properties level under the row component

    for i in range(row_start, row_end):
        line = lines[i]
        stripped = line.strip()

        # Fix wrap: nowrap -> wrap (within this row's layout section)
        if re.match(r'^\s+wrap:\s*nowrap\s*$', line):
            # Check it's at the right nesting level (inside this row's layout)
            line_indent = len(line) - len(line.lstrip())
            if line_indent > row_indent:
                lines[i] = line.replace('nowrap', 'wrap')
                changes.append(f"wrap: nowrap -> wrap")

        # Fix gap > md -> md
        gap_match = re.match(r'^(\s+gap:\s*)(' + '|'.join(TOO_LARGE) + r')\s*$', line)
        if gap_match:
            line_indent = len(line) - len(line.lstrip())
            if line_indent > row_indent:
                old_val = gap_match.group(2)
                lines[i] = gap_match.group(1) + 'md\n'
                changes.append(f"gap: {old_val} -> md")

        # Fix paddingInline > md -> md
        pi_match = re.match(r'^(\s+paddingInline:\s*)(' + '|'.join(TOO_LARGE) + r')\s*$', line)
        if pi_match:
            line_indent = len(line) - len(line.lstrip())
            if line_indent > row_indent:
                old_val = pi_match.group(2)
                lines[i] = pi_match.group(1) + 'md\n'
                changes.append(f"paddingInline: {old_val} -> md")

    return changes


def fix_file(filepath):
    """Process a single YAML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split('\n')
    # Add newline tracking
    lines = [l + '\n' for l in lines]
    if content.endswith('\n'):
        lines[-1] = lines[-1]  # already has newline
    else:
        lines[-1] = lines[-1].rstrip('\n')  # remove extra newline from last

    row_blocks = find_layout_rows_with_tight_children(lines)

    if not row_blocks:
        return []

    all_changes = []
    for (row_start, row_indent, row_end) in row_blocks:
        changes = fix_row_block(lines, row_start, row_indent, row_end)
        all_changes.extend(changes)

    if all_changes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(''.join(lines))

    return all_changes


def main():
    yaml_files = sorted(TEMPLATES_DIR.rglob("*.yaml"))
    print(f"Scanning {len(yaml_files)} YAML files...")

    total_files = 0
    total_changes = 0

    for filepath in yaml_files:
        changes = fix_file(filepath)
        if changes:
            rel = filepath.relative_to(TEMPLATES_DIR)
            print(f"\n  {rel}:")
            for c in changes:
                print(f"    {c}")
            total_files += 1
            total_changes += len(changes)

    print(f"\nDone: {total_changes} changes across {total_files} files.")


if __name__ == "__main__":
    main()
