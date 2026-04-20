"""ssr_python/rag/agent/component_specs.py — Component spec extractor for LLM prompts.

Extracts annotated component syntax blocks from COMPONENT_SYNTAX_REFERENCE.md.
This gives the LLM properly annotated specs with color rules, valid values,
and comments — single source of truth instead of dumping raw defaults.
"""
import re
from pathlib import Path

_syntax_ref: str | None = None
_component_blocks: dict[str, str] | None = None


def _load() -> dict[str, str]:
    """Lazy-load and parse COMPONENT_SYNTAX_REFERENCE.md into per-component syntax blocks."""
    global _syntax_ref, _component_blocks
    if _component_blocks is not None:
        return _component_blocks

    path = Path(__file__).resolve().parent.parent.parent / "config" / "COMPONENT_SYNTAX_REFERENCE.md"
    _syntax_ref = path.read_text(encoding="utf-8")

    _component_blocks = {}

    # Find each component section: <!-- section_type: component | component_name: X -->
    # Extract the ```yaml ... ``` block from its ### Syntax section
    pattern = re.compile(
        r'<!-- section_type: component \| component_name: (\S+)',
    )

    for match in pattern.finditer(_syntax_ref):
        comp_name = match.group(1)
        start = match.end()

        # Find the ```yaml block after ### Syntax
        yaml_match = re.search(r'```yaml\n(.+?)```', _syntax_ref[start:start + 3000], re.DOTALL)
        if yaml_match:
            _component_blocks[comp_name] = yaml_match.group(1).strip()

    return _component_blocks


def build_component_specs(component_names: list[str]) -> str:
    """Return annotated YAML specs for the given components.

    Extracts the ### Syntax code blocks from COMPONENT_SYNTAX_REFERENCE.md.
    Shows the full syntax reference with all annotations — the LLM should
    only set properties it needs to change from defaults.
    Always includes layout-row and layout-column since every section uses them.
    """
    blocks = _load()
    names = set(component_names) | {"layout-row", "layout-column"}
    parts = []
    for name in sorted(names):
        if name in blocks:
            parts.append(blocks[name])
    return "\n\n".join(parts) if parts else ""


VALID_TOKENS = """Spacing (paddingBlock, paddingInline, marginBlock, marginInline, gap): none, xxs, xs, sm, md, lg, xl, xxl, xxxl
Typography size: xxs, xs, sm, md, lg, xl, xxl, xxxl
Font weight: light, regular, medium, semibold, bold, extrabold
Border radius: none, xs, sm, md, lg, xl, xxl, pill
Shadow: none, soft, medium, elevated, dramatic, retro
Width mode (layout.widthMode as STRING): fit, "16", "25", "33", "50", "66", "75", "83", "stretch"
Hover effect: none, zoom, lift, brighten, darken
Letter spacing: normal, tight, wide, wider
Horizontal align: center, left, right, space-between, space-around, space-evenly
Vertical align: center, start, end, stretch, baseline"""
