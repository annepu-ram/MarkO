"""
Replace hardcoded hex color values with YAML anchor aliases in all example templates.

Rules:
1. Extract theme color anchors from each file (e.g., &color-primary '#111827')
2. Replace hardcoded occurrences of those hex values with *anchor-name aliases
3. If &color-background is '#ffffff', also replace standalone '#ffffff' with *color-background
4. Skip the anchor definition line itself
5. Case-insensitive hex matching
"""

import re
import os
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "example_templates"

ANCHOR_PATTERN = re.compile(
    r"&(color-\w+)\s+['\"]?(#[0-9a-fA-F]{3,8})['\"]?"
)


def extract_color_anchors(content: str) -> dict:
    """Extract {hex_value_lower: anchor_name} from anchor definitions."""
    color_map = {}
    for match in ANCHOR_PATTERN.finditer(content):
        anchor_name = match.group(1)
        hex_value = match.group(2).lower()
        color_map[hex_value] = anchor_name
    return color_map


def fix_file(filepath: Path) -> int:
    """Fix hardcoded colors in a single file. Returns number of replacements."""
    content = filepath.read_text(encoding="utf-8")
    color_map = extract_color_anchors(content)

    if not color_map:
        return 0

    lines = content.split("\n")
    total_replacements = 0

    for hex_val, anchor_name in color_map.items():
        for i, line in enumerate(lines):
            if f"&{anchor_name}" in line:
                continue

            hex_variants = [hex_val, hex_val.upper()]
            if hex_val == hex_val.lower():
                mixed = "#" + hex_val[1:].upper()
                hex_variants.append(mixed)

            for variant in hex_variants:
                for quote in ["'", '"']:
                    old = f"{quote}{variant}{quote}"
                    new = f"*{anchor_name}"
                    if old in lines[i]:
                        lines[i] = lines[i].replace(old, new)
                        total_replacements += 1

    if total_replacements > 0:
        filepath.write_text("\n".join(lines), encoding="utf-8")

    return total_replacements


def main():
    total_files = 0
    total_replacements = 0

    yaml_files = sorted(TEMPLATES_DIR.rglob("*.yaml"))
    print(f"Processing {len(yaml_files)} YAML files...")

    for filepath in yaml_files:
        replacements = fix_file(filepath)
        if replacements > 0:
            rel_path = filepath.relative_to(TEMPLATES_DIR)
            print(f"  {rel_path}: {replacements} replacement(s)")
            total_files += 1
            total_replacements += replacements

    print(f"\nDone: {total_replacements} replacements across {total_files} files.")


if __name__ == "__main__":
    main()
