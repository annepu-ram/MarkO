"""One-time migration: update # Visual style: comments to canonical style keys.

Maps informal style tags (modern, card_based, dark_mode, etc.) to canonical
compound keys matching STYLE_THEMES_REFERENCE.md and builder_agent.py normalization.

Usage:
    python -m rag.scripts.update_template_styles          # dry-run (default)
    python -m rag.scripts.update_template_styles --apply   # write changes
"""
import re
import sys
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "example_templates"

# ── Tag → canonical key mapping ──
# Multi-word tags are split on comma first, then each tag is mapped individually.
TAG_MAP = {
    # Modern/minimal family → modern_minimalist
    "modern": "modern_minimalist",
    "minimal": "modern_minimalist",
    "minimalist": "modern_minimalist",
    "clean": "modern_minimalist",
    "light": "modern_minimalist",
    "sleek": "modern_minimalist",
    # Dark family → monochrome_dark
    "dark_mode": "monochrome_dark",
    "dark": "monochrome_dark",
    "monochrome": "monochrome_dark",
    "noir": "monochrome_dark",
    # Direct matches (single-word official names)
    "glassmorphism": "glassmorphism",
    "frosted": "glassmorphism",
    "neubrutalism": "neubrutalism",
    "claymorphism": "claymorphism",
    "playful": "claymorphism",
    # Compound expansions
    "retro": "retro_vintage",
    "vintage": "retro_vintage",
    "aurora": "aurora_gradient",
    "gradient": "aurora_gradient",
    "bold_typography": "bold_editorial",
    "editorial": "bold_editorial",
    "colorful": "bold_editorial",
    "bold": "bold_editorial",
    "elegant": "elegant_luxury",
    "luxury": "elegant_luxury",
    "premium": "elegant_luxury",
    "organic": "organic_natural",
    "natural": "organic_natural",
    "corporate": "corporate_professional",
    "professional": "corporate_professional",
    "zen": "zen_japanese",
    # Layout descriptors (not styles) → need context-based assignment
    "card_based": None,  # handled specially below
    "animated": None,     # not a visual style
}


def _resolve_card_based(content: str) -> str:
    """Examine template content to assign a canonical style for 'card_based' templates.

    Checks the *background* color (not primary, which is usually text).
    Dark background = monochrome_dark, light background = modern_minimalist.
    """
    # Look for background color definition
    bg_match = re.search(r"background:\s*[&*\w-]*\s*['\"]?(#[0-9a-fA-F]{3,8})", content)
    if bg_match:
        hex_color = bg_match.group(1).lower().lstrip("#")
        # Normalize 3-char hex to 6-char
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        if len(hex_color) >= 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            if luminance < 80:  # Dark background
                return "monochrome_dark"
    return "modern_minimalist"


def _map_style_line(current_value: str, file_content: str) -> str:
    """Map a Visual style comment value to canonical key(s)."""
    tags = [t.strip().lower().replace(" ", "_") for t in current_value.split(",")]

    canonical = set()
    has_explicit_style = False  # Track if any non-layout tag was mapped

    for tag in tags:
        if tag in TAG_MAP:
            mapped = TAG_MAP[tag]
            if mapped is not None:
                canonical.add(mapped)
                has_explicit_style = True
            elif tag == "card_based":
                pass  # Defer card_based resolution
            # animated/None tags are dropped
        else:
            # Unknown tag — keep if it looks like a canonical key
            from rag.config import CANONICAL_STYLES
            if tag in CANONICAL_STYLES:
                canonical.add(tag)
                has_explicit_style = True

    # Only resolve card_based if no explicit style tag was found
    if not has_explicit_style and "card_based" in tags:
        canonical.add(_resolve_card_based(file_content))

    if not canonical:
        # Fallback: infer from background color
        canonical.add(_resolve_card_based(file_content))

    # If multiple styles, prefer the more specific one over modern_minimalist
    if len(canonical) > 1 and "modern_minimalist" in canonical:
        canonical.discard("modern_minimalist")

    return ", ".join(sorted(canonical))


# ── Filename-based overrides for templates whose name strongly implies a style ──
FILENAME_OVERRIDES = {
    "13_zen_wellness": "zen_japanese",
}


def migrate(apply: bool = False):
    """Scan all templates and update Visual style comments."""
    yaml_files = sorted(TEMPLATES_DIR.rglob("*.yaml"))
    changes = []

    for fpath in yaml_files:
        content = fpath.read_text(encoding="utf-8")
        match = re.search(r"^(# Visual style: )(.+)$", content, re.MULTILINE)
        if not match:
            continue

        prefix = match.group(1)
        old_value = match.group(2).strip()

        # Check filename-based overrides first
        stem = fpath.stem
        if stem in FILENAME_OVERRIDES:
            new_value = FILENAME_OVERRIDES[stem]
        else:
            new_value = _map_style_line(old_value, content)

        if old_value != new_value:
            changes.append((fpath, old_value, new_value))
            if apply:
                new_line = f"{prefix}{new_value}"
                updated = content[:match.start()] + new_line + content[match.end():]
                fpath.write_text(updated, encoding="utf-8")

    # Report
    print(f"\nScanned {len(yaml_files)} files, {len(changes)} need updates\n")
    for fpath, old, new in changes:
        rel = fpath.relative_to(TEMPLATES_DIR)
        status = "UPDATED" if apply else "WOULD UPDATE"
        print(f"  [{status}] {rel}")
        print(f"    {old} -> {new}")

    if not apply and changes:
        print(f"\nRe-run with --apply to write changes.")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    migrate(apply=apply)
