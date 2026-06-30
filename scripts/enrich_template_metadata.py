"""scripts/enrich_template_metadata.py — Add Tone, Intent, Image requirement,
Interactivity, and Industries header lines to every template.

Idempotent: skips lines that already exist. Inserts each missing line in a
deterministic header position so all templates have the same field order.

Heuristics (operator may hand-edit afterwards):
  Tone               from visual_style + section_type
  Conversion intent  from section_type
  Image requirement  from #image / #gif occurrences in body
  Interactivity      from AST scan (form/tabs/carousel/accordion/video components)
  Industries         from regex match against existing Perfect-for line

Header order after enrichment:
    Title
    Description
    Base components: ...
    Section type: ...
    Layout: ...
    Visual style: ...
    Content volume: ...
    Tone: ...
    Conversion intent: ...
    Image requirement: ...
    Interactivity: ...
    Industries: ...
    Perfect for: ...
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ssr_python"))
from rag.indexing.metadata import INDUSTRY_PATTERNS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1] / "example_templates"

# Style → tone mapping. Default to "neutral" when style is unknown.
STYLE_TO_TONE = {
    "modern_minimalist": "neutral",
    "glassmorphism": "neutral",
    "retro_vintage": "casual",
    "neubrutalism": "playful",
    "claymorphism": "playful",
    "aurora_gradient": "neutral",
    "monochrome_dark": "formal",
    "elegant_luxury": "formal",
    "organic_natural": "casual",
    "corporate_professional": "formal",
    "bold_editorial": "neutral",
    "cyberpunk_neon": "playful",
    "pastel_soft": "casual",
    "scandinavian_clean": "neutral",
    "art_deco_geometric": "formal",
    "tropical_vibrant": "playful",
    "dark_academia": "formal",
    "memphis_design": "playful",
    "zen_japanese": "neutral",
    "industrial_grunge": "casual",
    "y2k_retro-futurism": "playful",
    "bohemian_eclectic": "casual",
}

# Section type → conversion intent mapping.
SECTION_TO_INTENT = {
    "hero": "awareness",
    "cta": "lead",
    "form_cta": "lead",
    "newsletter": "lead",
    "contact": "lead",
    "order_form": "purchase",
    "reservation": "lead",
    "pricing": "purchase",
    "products": "purchase",
    "menu": "purchase",
    "testimonials": "trust",
    "trusted_by": "trust",
    "achievements": "trust",
    "stats": "trust",
    "team": "trust",
    "about": "trust",
    "features": "engagement",
    "services": "engagement",
    "how_it_works": "engagement",
    "faq": "engagement",
    "gallery": "engagement",
    "blog": "engagement",
    "schedule": "engagement",
    "dashboard": "engagement",
    "countdown": "lead",
    "ticker": "awareness",
    "navigation": "awareness",
    "footer": "awareness",
    "banner": "awareness",
    "social_links": "engagement",
    "delivery_areas": "trust",
    "divider": "awareness",
}

# Components that signal interactivity beyond static.
INTERACTIVITY_RULES = [
    ("form", re.compile(r"name:\s*(form|textbox|textarea|dropdown|checkbox|radio|calendar)\b")),
    ("tabs", re.compile(r"name:\s*tabs\b")),
    ("accordion", re.compile(r"name:\s*accordion\b")),
    ("carousel", re.compile(r"name:\s*carousel\b")),
    ("video", re.compile(r"name:\s*video(-background)?\b")),
]

IMAGE_PATTERN = re.compile(r"name:\s*(image|gif)\b")

HEADER_ORDER = [
    "Base components",
    "Section type",
    "Layout",
    "Visual style",
    "Content volume",
    "Tone",
    "Conversion intent",
    "Image requirement",
    "Interactivity",
    "Industries",
    "Perfect for",
    "Use cases",
    "Best for",
]


def _read_field(comments_block: list[str], prefix: str) -> str:
    """Return value of `# {prefix}: ...` line or '' if missing."""
    for line in comments_block:
        m = re.match(rf"^\s*#\s*{re.escape(prefix)}\s*:\s*(.*)$", line, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def _classify_image_requirement(body: str) -> str:
    n = len(IMAGE_PATTERN.findall(body))
    if n == 0:
        return "none"
    if n >= 5:
        return "many"
    if n >= 2:
        return "required"
    return "decorative"


def _classify_interactivity(body: str) -> str:
    found: list[str] = []
    for label, pat in INTERACTIVITY_RULES:
        if pat.search(body) and label not in found:
            found.append(label)
    return ", ".join(found) if found else "static"


def _classify_industries(perfect_for: str) -> str:
    """Map Perfect-for free text to canonical industry CSV via INDUSTRY_PATTERNS."""
    text = perfect_for.lower()
    matched: list[str] = []
    for ind, pat in INDUSTRY_PATTERNS.items():
        if re.search(pat, text) and ind not in matched:
            matched.append(ind)
    return ", ".join(matched[:5])  # cap to keep header readable


def _normalize_visual_style(s: str) -> str:
    return s.strip().lower().split(",")[0].replace(" ", "_") if s else ""


def _classify_tone(visual_style: str, section_type: str) -> str:
    key = _normalize_visual_style(visual_style)
    if key in STYLE_TO_TONE:
        return STYLE_TO_TONE[key]
    # Fallback by section
    if section_type in {"hero", "features", "cta"}:
        return "neutral"
    return "neutral"


def _classify_intent(section_type: str) -> str:
    return SECTION_TO_INTENT.get(section_type, "awareness")


def header_block_end(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#") or s == "":
            continue
        return i
    return len(lines)


def insertion_index(header: list[str], new_prefix: str) -> int:
    """Return the index in header where `# {new_prefix}: …` should be placed.

    Preserves HEADER_ORDER so all templates have stable field order.
    """
    target_pos = HEADER_ORDER.index(new_prefix) if new_prefix in HEADER_ORDER else len(HEADER_ORDER)
    for i, line in enumerate(header):
        m = re.match(r"^\s*#\s*([A-Za-z][A-Za-z _-]+)\s*:", line)
        if not m:
            continue
        pfx = m.group(1).strip()
        if pfx in HEADER_ORDER and HEADER_ORDER.index(pfx) > target_pos:
            return i
    # Otherwise append after last comment line in header block.
    last_comment = -1
    for i, line in enumerate(header):
        if line.strip().startswith("#"):
            last_comment = i
    return (last_comment + 1) if last_comment >= 0 else len(header)


def enrich_file(path: Path) -> tuple[bool, dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=False)
    end_idx = header_block_end(lines)
    header = lines[:end_idx]
    body = "\n".join(lines[end_idx:])

    visual_style = _read_field(header, "Visual style")
    section_type = _read_field(header, "Section type") or path.parent.name
    perfect_for = _read_field(header, "Perfect for") or _read_field(header, "Use cases") or _read_field(header, "Best for")

    derived = {
        "Tone": _classify_tone(visual_style, section_type),
        "Conversion intent": _classify_intent(section_type),
        "Image requirement": _classify_image_requirement(body),
        "Interactivity": _classify_interactivity(body),
        "Industries": _classify_industries(perfect_for),
    }

    new_header = list(header)
    changed = False
    for prefix, value in derived.items():
        if not value:
            continue
        if _read_field(new_header, prefix):
            continue  # already present
        ins_at = insertion_index(new_header, prefix)
        new_header.insert(ins_at, f"# {prefix}: {value}")
        changed = True

    if not changed:
        return False, derived

    keep_eol = "\r\n" if "\r\n" in text[:200] else "\n"
    out = keep_eol.join(new_header + lines[end_idx:])
    if text.endswith(("\n", "\r\n")):
        out += keep_eol
    path.write_text(out, encoding="utf-8")
    return True, derived


def main(dry_run: bool) -> int:
    files = sorted(ROOT.rglob("*.yaml"))
    written = 0
    skipped = 0
    summary = {"Tone": {}, "Conversion intent": {}, "Image requirement": {}, "Interactivity": {}, "Industries": {}}
    for f in files:
        if dry_run:
            text = f.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines(keepends=False)
            end = header_block_end(lines)
            visual_style = _read_field(lines[:end], "Visual style")
            section_type = _read_field(lines[:end], "Section type") or f.parent.name
            perfect_for = _read_field(lines[:end], "Perfect for") or _read_field(lines[:end], "Use cases") or _read_field(lines[:end], "Best for")
            body = "\n".join(lines[end:])
            derived = {
                "Tone": _classify_tone(visual_style, section_type),
                "Conversion intent": _classify_intent(section_type),
                "Image requirement": _classify_image_requirement(body),
                "Interactivity": _classify_interactivity(body),
                "Industries": _classify_industries(perfect_for),
            }
            new_count = sum(1 for k, v in derived.items() if v and not _read_field(lines[:end], k))
            if new_count:
                written += 1
            else:
                skipped += 1
        else:
            ok, derived = enrich_file(f)
            if ok:
                written += 1
            else:
                skipped += 1
        for k, v in derived.items():
            summary[k][v] = summary[k].get(v, 0) + 1

    print(f"\nTotal YAML files: {len(files)}")
    print(f"{'Would write' if dry_run else 'Wrote'}: {written}")
    print(f"Already complete: {skipped}")
    print()
    for axis, counts in summary.items():
        items = ", ".join(f"{k or '(empty)'}={v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f"  {axis}: {items}")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(main(dry))
