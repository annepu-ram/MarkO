"""ssr_python/rag/agent/styler_agent.py — Visual style designer.

Picks a visual style and theme, writes natural language design direction
per section, and assigns images to sections. Single LLM call.
"""
import copy
import re
import logging

from rag.config import config, CANONICAL_STYLES
from rag.agent.model_backend import ModelBackend
from rag.agent.prompt_loader import load_system, render_user
from rag.agent.prompt_logger import log_prompt, log_output

logger = logging.getLogger(__name__)


def _dedupe_csv(*sources: str) -> str:
    """Merge comma-separated strings, dropping duplicate tokens (case-insensitive)."""
    seen: set[str] = set()
    out: list[str] = []
    for src in sources:
        if not src:
            continue
        for tok in src.split(","):
            tok = tok.strip()
            if not tok:
                continue
            key = tok.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(tok)
    return ", ".join(out)


class StylerAgent:
    def __init__(self, model: ModelBackend):
        self.model = model

    def style(
        self,
        outline: dict,
        planner_md: str,
        style_context: str,
        selected_images: list | None = None,
        style_hints: str = "",
        color_hints: str = "",
        business_context: dict | None = None,
    ) -> dict:
        """Pick a style, generate theme, write design direction, and assign images.

        Args:
            outline: Parsed planner outline dict with page_title, sections[]
            planner_md: Raw planner markdown (for context)
            style_context: Raw style chunk text from STYLE_THEMES_REFERENCE.md
            selected_images: List of image dicts {url, altText, orientation, photographer}
            style_hints: Comma-separated style keywords extracted from user query
            color_hints: Comma-separated color words extracted from user query
            business_context: Optional guided-flow context dict with shape
                {business_name, industry, variant_label, description,
                 style_preference, color_preference}. Used to inform
                style/theme selection for business-specific generation.

        Returns:
            Enriched outline dict with theme, style_name, and per-section
            style_notes + dark_section + images.
        """
        sections = outline.get("sections", [])
        if not sections:
            logger.debug("Styler: no sections, skipping")
            return outline

        # Build section summary from planner outline
        section_summary = []
        for s in sections:
            comps = ", ".join(s.get("components", []))
            icons = s.get("icons", [])
            icon_hint = f"\n- Icons: {len(icons)} (one per item)" if icons else ""
            section_summary.append(
                f"## {s['type'].replace('_', ' ').title()}\n"
                f"- {s.get('description', '')}\n"
                f"- Components: {comps}{icon_hint}"
            )

        # Fold guided-flow preferences into the hints so the existing template
        # and prompt wiring keep working without a schema change. Dedupe tokens
        # because the guided flow passes style_preference as both style_hints
        # and inside business_context, which otherwise produces duplicate lists
        # like "dark_academia, dark_academia".
        bc = business_context or {}
        bc_style_pref = (bc.get("style_preference") or "").strip()
        bc_color_pref = (bc.get("color_preference") or "").strip()
        effective_style_hints = _dedupe_csv(style_hints, bc_style_pref)
        effective_color_hints = _dedupe_csv(color_hints, bc_color_pref)

        system = load_system("styler")
        user_prompt = render_user("styler",
            style_context=style_context,
            selected_images=selected_images or [],
            section_summary=section_summary,
            section_count=len(sections),
            style_hints=effective_style_hints,
            color_hints=effective_color_hints,
            business_name=(bc.get("business_name") or "").strip(),
            business_industry=(bc.get("industry") or "").strip(),
            business_variant=(bc.get("variant_label") or "").strip(),
            business_description=(bc.get("description") or "").strip(),
        )

        log_prompt("STYLER", system, user_prompt)

        response = self.model.generate(system, user_prompt)
        log_output("STYLER", response)

        return self._parse_and_merge(outline, response, selected_images)

    def _parse_and_merge(
        self, outline: dict, response: str, selected_images: list | None = None,
    ) -> dict:
        """Parse styler markdown and merge into outline dict."""
        enriched = copy.deepcopy(outline)

        try:
            parsed = self._parse_styler_markdown(response)
        except Exception as e:
            logger.warning(f"Styler: failed to parse markdown: {e}. Using defaults.")
            enriched["theme"] = dict(config.default_theme)
            return enriched

        # Set style_name — validate against canonical list, fall back if not.
        raw_name = (parsed.get("style_name") or "").strip()
        normalized = raw_name.lower().replace(" ", "_")
        if normalized in CANONICAL_STYLES:
            enriched["style_name"] = normalized
        elif raw_name:
            # LLM ignored the canonical-key rule (e.g. wrote "Midnight Scholar").
            # Keep the raw value only if the caller can't supply a fallback.
            logger.warning(
                f"Styler: '{raw_name}' is not a canonical style key; "
                f"builder style-filtered retrieval will miss."
            )
            enriched["style_name"] = normalized
        if parsed.get("theme_label"):
            enriched["theme_label"] = parsed["theme_label"]
        logger.debug(
            f"Styler: style='{enriched.get('style_name','')}' "
            f"theme='{enriched.get('theme_label','')}'"
        )

        # Set theme (with fallback to defaults)
        theme = parsed.get("theme", {})
        if theme:
            merged_theme = dict(config.default_theme)
            merged_theme.update(theme)
            enriched["theme"] = merged_theme
        else:
            enriched["theme"] = dict(config.default_theme)

        # Merge per-section data
        styled_sections = parsed.get("sections", [])
        outline_sections = enriched.get("sections", [])

        for i, outline_section in enumerate(outline_sections):
            if i < len(styled_sections):
                ss = styled_sections[i]
                if ss.get("style_notes"):
                    outline_section["style_notes"] = ss["style_notes"]
                if ss.get("dark_section") is not None:
                    outline_section["dark_section"] = ss["dark_section"]

                # Resolve image indices to rendered image context for builder
                if ss.get("image_indices") and selected_images:
                    image_lines = []
                    count = 0
                    for idx in ss["image_indices"]:
                        if 0 <= idx < len(selected_images):
                            img = selected_images[idx]
                            count += 1
                            url = img.get('url', '')
                            alt = img.get('altText', '')
                            orientation = img.get('orientation', 'unknown')
                            tags = img.get('tags') or []
                            source = img.get('source', '')
                            width = img.get('width')
                            height = img.get('height')
                            metadata = []
                            if tags:
                                metadata.append(f"tags: {', '.join(tags)}")
                            if source:
                                metadata.append(f"source: {source}")
                            if width and height:
                                metadata.append(f"size: {width}x{height}")
                            if metadata:
                                image_lines.append(f"   metadata for image {count}: {'; '.join(metadata)}")
                            image_lines.append(
                                f"{count}. {url} — \"{alt}\" [{orientation}]"
                            )
                    if image_lines:
                        outline_section["image_context"] = "\n".join(image_lines)
                    logger.debug(
                        f"Styler: section {i} ({outline_section.get('type')}) "
                        f"assigned {count} images"
                    )

                logger.debug(
                    f"Styler: section {i} ({outline_section.get('type')}) "
                    f"dark={ss.get('dark_section')}"
                )
            else:
                logger.warning(f"Styler: no style data for section {i}")

        return enriched

    def _parse_styler_markdown(self, md: str) -> dict:
        """Parse styler markdown into structured dict.

        Returns:
            {
                "style_name": str,
                "theme": {primary, text, secondary, accent, background, ...},
                "sections": [{type, dark_section, style_notes, image_indices}, ...]
            }
        """
        result = {"style_name": "", "theme_label": "", "theme": {}, "sections": []}

        # Extract style name from # Style: heading (canonical key)
        m = re.search(r'^#\s+Style:\s*(.+)', md, re.MULTILINE)
        if m:
            result["style_name"] = m.group(1).strip()

        # Extract palette label from # Theme: heading (human-readable name).
        # Must anchor on a single `#` (level-1) so the `## Theme` block below
        # doesn't match.
        t = re.search(r'^#\s+Theme:\s*(.+)', md, re.MULTILINE)
        if t:
            result["theme_label"] = t.group(1).strip()

        # Split at ## headings
        h2_parts = re.split(r'\n(?=## )', md)

        for part in h2_parts:
            heading_match = re.match(r'^## (.+)', part)
            if not heading_match:
                continue
            heading = heading_match.group(1).strip()

            if heading.lower() == "theme":
                result["theme"] = self._parse_kv_lines(part)
            else:
                section = self._parse_section(heading, part)
                result["sections"].append(section)

        return result

    def _parse_section(self, heading: str, part: str) -> dict:
        """Parse a ## section block into structured section dict."""
        section_type = heading.lower().replace(" ", "_")

        dark_section = None
        image_indices = []
        style_lines = []

        for line in part.split("\n")[1:]:  # Skip the ## heading line
            stripped = line.strip()
            if not stripped or not stripped.startswith("- "):
                continue
            bullet = stripped[2:].strip()

            if bullet.lower().startswith("dark_section:"):
                val = bullet.split(":", 1)[1].strip().lower()
                dark_section = val in ("true", "yes", "1")
            elif bullet.lower().startswith("images:"):
                # Parse image numbers: "Images: 1, 3" → indices [0, 2]
                nums_str = bullet.split(":", 1)[1].strip()
                for num in re.findall(r'\d+', nums_str):
                    image_indices.append(int(num) - 1)  # Convert 1-based to 0-based
            else:
                style_lines.append(bullet)

        return {
            "type": section_type,
            "dark_section": dark_section,
            "style_notes": "\n".join(style_lines),
            "image_indices": image_indices,
        }

    def _parse_kv_lines(self, text: str) -> dict:
        """Parse - key: value lines from a markdown block into a flat dict."""
        result = {}
        for line in text.split("\n"):
            m = re.match(r'^\s*-\s+([\w_]+)\s*:\s*(.+)', line)
            if m:
                result[m.group(1)] = m.group(2).strip()
        return result
