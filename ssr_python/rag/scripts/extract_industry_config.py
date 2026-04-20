"""
ssr_python/rag/scripts/extract_industry_config.py
─────────────────────────────────────────────────
Parses every `website_example_outlines/**/*.md` file and prints a
starter INDUSTRY_REGISTRY dict that you can paste / merge into
`rag/industry_defaults.py`.

This is a development utility — run it when new outline files are added,
compare the output to `industry_defaults.py`, and hand-merge. The registry
in `industry_defaults.py` is still the source of truth; this script only
helps you keep it in sync with the outlines.

Usage:
    cd ssr_python
    python -m rag.scripts.extract_industry_config
    python -m rag.scripts.extract_industry_config --json > registry_preview.json

What it extracts per file:
    - industry label     from the top-level `# Heading`
    - category           from the parent folder (services/products/events)
    - variants           from each `## Variant X — Name`
    - sections per variant from numbered bullets like `1. **titlebar**`

Sections are emitted using the raw component names from outlines; you'll
need to map them to the canonical section types in SECTION_QUESTIONS when
merging (see COMPONENT_TO_SECTION below for the common aliases).
"""
from __future__ import annotations

import sys
import os
import re
import json
from pathlib import Path

# Ensure ssr_python is on the Python path when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# Outline directory (relative to repo root, two levels up from ssr_python/)
REPO_ROOT = Path(__file__).resolve().parents[3]
OUTLINES_DIR = REPO_ROOT / "website_example_outlines"


# Map raw outline component names → canonical section types used by the
# guided flow (keys of SECTION_QUESTIONS). Unknown names pass through as-is
# so you can inspect them manually.
COMPONENT_TO_SECTION = {
    "titlebar": "navigation",
    "nav": "navigation",
    "header": "navigation",
    "hero": "hero",
    "video-background": "hero",
    "layout-row": None,          # structural, skip unless the label hints otherwise
    "columnsgrid": None,
    "tabs": None,
    "menu": "menu",
    "counter-up": "stats",
    "counter": "stats",
    "carousel": "gallery",
    "ticker": "testimonials",    # most outlines use tickers for reviews/brands
    "accordion": "faq",
    "faq": "faq",
    "countdown": "countdown",
    "form": "order_form",
    "footer": "footer",
    "cta": "cta",
}


HEADING_RE = re.compile(r"^#\s+(.+?)(?:\s+—|\s+-|\s*$)", re.MULTILINE)
VARIANT_RE = re.compile(r"^##\s+Variant\s+([A-Z])\s+[—-]\s+(.+?)\s*$", re.MULTILINE)
# Captures numbered bullets like:  "1. **titlebar**"  or  "10. **layout-row (Footer)**"
SECTION_RE = re.compile(r"^\s*\d+\.\s+\*\*([a-z][a-z0-9_-]*)(?:\s*\(([^)]+)\))?\*\*", re.MULTILINE)


def parse_outline(path: Path) -> dict | None:
    """Parse a single outline file; return None if it can't be parsed."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Category = parent folder name
    category = path.parent.name  # services | products | events

    # Industry label = first `# Heading` (trimmed of any "— focus" suffix)
    m = HEADING_RE.search(text)
    if not m:
        return None
    industry_label = m.group(1).strip()

    # Industry key: lowercase + underscores from filename stem (without leading number_)
    stem = path.stem
    stem = re.sub(r"^\d+_", "", stem)
    stem = re.sub(r"^(product|event)_\d+_", "", stem)
    industry_key = stem.lower()

    # Parse variants
    variants = []
    variant_matches = list(VARIANT_RE.finditer(text))
    for i, vm in enumerate(variant_matches):
        variant_letter = vm.group(1)
        variant_label = vm.group(2).strip()
        block_start = vm.end()
        block_end = variant_matches[i + 1].start() if i + 1 < len(variant_matches) else len(text)
        block = text[block_start:block_end]

        # Extract section names, preserving order, deduping
        seen = set()
        sections = []
        for sm in SECTION_RE.finditer(block):
            raw_name = sm.group(1).lower()
            hint = (sm.group(2) or "").lower()
            # Apply component → section mapping
            mapped = COMPONENT_TO_SECTION.get(raw_name, raw_name)
            if mapped is None:
                # Structural (layout-row, columnsgrid); try the hint instead
                for keyword, section_type in [
                    ("hero", "hero"),
                    ("menu", "menu"),
                    ("about", "about"),
                    ("story", "about"),
                    ("pricing", "pricing"),
                    ("faq", "faq"),
                    ("testimonial", "testimonials"),
                    ("review", "testimonials"),
                    ("team", "team"),
                    ("gallery", "gallery"),
                    ("contact", "contact"),
                    ("footer", "footer"),
                    ("feature", "features"),
                    ("service", "services"),
                    ("cta", "cta"),
                    ("how it works", "how_it_works"),
                    ("process", "how_it_works"),
                    ("schedule", "schedule"),
                    ("booking", "order_form"),
                    ("reservation", "reservation"),
                    ("delivery", "delivery_areas"),
                ]:
                    if keyword in hint:
                        mapped = section_type
                        break
            if mapped and mapped not in seen:
                seen.add(mapped)
                sections.append(mapped)

        variants.append({
            "id": f"{industry_key}_{variant_letter.lower()}",
            "label": variant_label,
            "sections": sections,
        })

    return {
        "industry_key": industry_key,
        "label": industry_label,
        "category": category,
        "source_outline": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "variants": variants,
    }


def extract_all() -> dict:
    """Parse every outline file; return {industry_key: entry} dict."""
    if not OUTLINES_DIR.exists():
        print(f"ERROR: outlines directory not found at {OUTLINES_DIR}", file=sys.stderr)
        sys.exit(1)

    registry = {}
    for md_path in sorted(OUTLINES_DIR.rglob("*.md")):
        parsed = parse_outline(md_path)
        if parsed is None:
            continue
        key = parsed.pop("industry_key")
        # Collision → append category suffix to disambiguate
        if key in registry:
            key = f"{key}_{parsed['category']}"
        registry[key] = parsed
    return registry


def main():
    as_json = "--json" in sys.argv
    registry = extract_all()

    if as_json:
        print(json.dumps(registry, indent=2))
        return

    print(f"# Extracted {len(registry)} industries from outlines in {OUTLINES_DIR}")
    print(f"# (Paste into rag/industry_defaults.py and edit to match canonical section types.)\n")
    for key, entry in registry.items():
        print(f'    "{key}": {{')
        print(f'        "label": {entry["label"]!r},')
        print(f'        "category": {entry["category"]!r},')
        print(f'        "source_outline": {entry["source_outline"]!r},')
        print(f'        "variants": [')
        for v in entry["variants"]:
            print(f'            {{')
            print(f'                "id": {v["id"]!r},')
            print(f'                "label": {v["label"]!r},')
            print(f'                "sections": {v["sections"]!r},')
            print(f'            }},')
        print(f'        ],')
        print(f'    }},')


if __name__ == "__main__":
    main()
