"""ssr_python/rag/agent/styler_agent.py — Per-section style property generator."""
import json
import re
import logging

from rag.agent.model_backend import ModelBackend

logger = logging.getLogger(__name__)

STYLER_SYSTEM = """You are a web design specialist. Given a website outline and a style reference, assign precise visual property values to each section.

OUTPUT: Return ONLY valid JSON (no markdown, no explanation).
{
  "style_name": "Style Name from reference",
  "sections": [
    {
      "type": "hero",
      "style_props": {
        "container_shadow": "none | soft | medium | elevated | retro",
        "container_radius": "none | xs | sm | md | lg | xl | xxl | pill",
        "container_blur": false,
        "container_border": "CSS border string or null",
        "button_radius": "none | xs | sm | md | lg | xl | xxl | pill",
        "button_shadow": "none | soft | medium | elevated | retro",
        "background_gradient": false,
        "background_transparency": 100,
        "dark_section": false
      }
    }
  ]
}

PROPERTY RULES:
- container_shadow: apply to layout-row and layout-column containers
- container_radius: cornerStyle value for layout-row, layout-column, columnsgrid
- container_blur: true ONLY for glassmorphism — applies backdrop-filter blur
- container_border: for neubrutalism use "3px solid #000000", glassmorphism use "1px solid rgba(255,255,255,0.3)", minimal styles use null
- button_radius: cornerStyle for button components
- button_shadow: shadow for button components
- background_gradient: true when section background should use gradient (colorStart/colorEnd)
- background_transparency: 0-100 (100=fully opaque, 80-90=frosted glass effect for glassmorphism)
- dark_section: true means dark background — builder must use *color-background for ALL text

STYLE RHYTHM RULES — vary across sections for visual interest:
- Alternate dark/light sections (e.g., hero dark, features light, CTA dark)
- FAQ and footer sections: match overall style but keep simple (dark_section: false unless style dictates)
- At least 1-2 sections should have dark_section: true for contrast
- CTA sections benefit from gradient backgrounds or dark backgrounds

IMPORTANT: Output one entry per section in the same order as the input outline."""


class StylerAgent:
    def __init__(self, model: ModelBackend):
        self.model = model

    def style(self, outline: dict, style_context: str) -> dict:
        """Assign style_props to each section based on style reference.

        Args:
            outline: Planner's JSON output with page_title, theme, sections[]
            style_context: Raw style chunk text from STYLE_THEMES_REFERENCE.md

        Returns:
            Enriched outline dict with style_props added to each section,
            plus top-level style_name. Falls back gracefully on parse errors.
        """
        sections = outline.get("sections", [])
        if not sections or not style_context:
            logger.info("Styler: no sections or style_context, skipping")
            return outline

        theme = outline.get("theme", {})
        primary = theme.get("primary", "#1a1a1a")
        accent = theme.get("accent", "#3b82f6")
        background = theme.get("background", "#ffffff")

        section_list = ", ".join(s.get("type", "unknown") for s in sections)

        user_prompt = (
            f"[Style Reference]\n{style_context}\n\n"
            f"[Page Outline]\n"
            f"Page: {outline.get('page_title', 'Website')}\n"
            f"Theme: primary={primary}, accent={accent}, background={background}\n"
            f"Sections ({len(sections)} total): {section_list}\n\n"
            f"Generate style_props for each section to match the [Style Reference]. "
            f"Output exactly {len(sections)} section entries in the same order."
        )

        logger.info(f"Styler: styling {len(sections)} sections")
        logger.debug(f"Styler user prompt ({len(user_prompt)} chars):\n{user_prompt[:400]}...")

        response = self.model.generate(STYLER_SYSTEM, user_prompt)
        logger.info(f"Styler raw LLM response ({len(response)} chars):\n{response}")

        return self._merge_style_props(outline, response)

    def _merge_style_props(self, outline: dict, response: str) -> dict:
        """Parse styler JSON response and merge style_props into outline sections."""
        import copy
        enriched = copy.deepcopy(outline)

        try:
            styled = self._parse_json(response)
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Styler: failed to parse JSON response: {e}. Using outline as-is.")
            return enriched

        # Extract style_name
        style_name = styled.get("style_name", "")
        if style_name:
            enriched["style_name"] = style_name
            logger.info(f"Styler: identified style '{style_name}'")

        # Merge style_props into matching sections by index
        styled_sections = styled.get("sections", [])
        outline_sections = enriched.get("sections", [])

        for i, outline_section in enumerate(outline_sections):
            if i < len(styled_sections):
                style_props = styled_sections[i].get("style_props", {})
                if style_props:
                    outline_section["style_props"] = style_props
                    logger.debug(
                        f"Styler: section {i} ({outline_section.get('type')}) "
                        f"style_props={style_props}"
                    )
            else:
                logger.warning(f"Styler: no style_props for section {i}, using defaults")

        return enriched

    def _parse_json(self, response: str) -> dict:
        """Extract JSON from model response, handling markdown code blocks."""
        match = re.search(r'```(?:json)?\s*\n(.+?)```', response, re.DOTALL)
        text = match.group(1) if match else response

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Could not parse styler JSON: {text[:200]}")
