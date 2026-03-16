"""ssr_python/rag/agent/builder_agent.py — Per-section YAML generator."""
import re
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.model_backend import ModelBackend
from rag.agent.component_specs import build_component_specs, VALID_TOKENS

logger = logging.getLogger(__name__)

BUILDER_SYSTEM = """You are a SwiftSites YAML component builder. Given a section description and theme, generate YAML components.

OUTPUT: Return ONLY valid YAML in a ```yaml code block.

COLORS (wrong colors = invisible text):
- Light bg sections: text = *color-primary, eyebrow/link = *color-accent, caption = *color-secondary
- Dark bg sections: ALL text = *color-background
- Button CTA: bg = *color-accent, text = *color-background
- NEVER put same color on both text and background

RULES:
- Follow the component specs and reference templates exactly
- Icon: `- name: icon` with `properties: {name: <icon-name>}`
- Use ALL images provided in the image context — they are pre-assigned to this section
"""


class BuilderAgent:
    def __init__(self, search: HybridSearch, reranker: Reranker, model: ModelBackend):
        self.search = search
        self.reranker = reranker
        self.model = model

    def build_section(
        self,
        section: dict,
        theme: dict,
        image_context: str = "",
        style_name: str = "",
        style_context: str = "",
    ) -> str:
        """Generate YAML for a single section.

        Args:
            section: {type, description, components, style_props} from planner/styler outline
            theme: {primary, secondary, accent, background, heading_font, content_font}
            image_context: Pre-built image context string with available local URLs
            style_name: Identified style name (e.g. "Glassmorphism") for search query enrichment
            style_context: Raw style reference text (capped excerpt) for LLM context

        Returns:
            YAML string for this section's components
        """
        section_type = section.get("type", "other")
        description = section.get("description", "")

        # Normalize style name for metadata filter (e.g. "Glassmorphism" → "glassmorphism")
        style_key = style_name.lower().replace(" ", "_") if style_name else ""

        # Enrich search query with style name for better semantic matching
        search_query = f"{section_type} {style_name} section" if style_name else f"{section_type} section template"

        # Try style-filtered retrieval first when a style name is known
        chunks = []
        if style_key:
            chunks = self.search.search(
                search_query,
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type, "visual_style": style_key},
                tier="section",
            )
            if chunks:
                logger.info(
                    f"Builder: found {len(chunks)} style-tagged chunks "
                    f"(section_type={section_type}, visual_style={style_key})"
                )

        # Fallback: section_type only (no style filter)
        if not chunks:
            chunks = self.search.search(
                search_query,
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type},
                tier="section",
            )

        # Final fallback: component tier
        if not chunks:
            logger.info(f"Section tier empty for {section_type}, falling back to component tier")
            chunks = self.search.search(
                f"{section_type} section template",
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type},
                tier="component",
            )

        logger.info(f"Builder retrieved {len(chunks)} chunks for section_type={section_type}")
        for i, c in enumerate(chunks[:5]):
            logger.debug(f"  Chunk {i}: {c.get('source_file', '?')} | {c.get('id', '?')}")

        # Rerank for relevance (no-op if disabled)
        ranked = self.reranker.rerank(
            f"{section_type} {description}",
            chunks,
            top_k=config.final_top_k,
        )

        logger.info(f"Builder using {len(ranked)} chunks after rerank")

        # Build context from retrieved templates
        context = "\n\n".join([
            f"--- Example: {c['source_file']} ---\n{c['content']}"
            for c in ranked
        ])

        # Build compact theme string
        dt = config.default_theme
        primary = theme.get('primary', dt['primary'])
        text_color = theme.get('text', dt['text'])
        secondary = theme.get('secondary', dt['secondary'])
        accent = theme.get('accent', dt['accent'])
        background = theme.get('background', dt['background'])
        theme_str = (
            f"Colors: primary='{primary}' (*color-primary), text='{text_color}' (*color-text), "
            f"secondary='{secondary}' (*color-secondary), "
            f"accent='{accent}' (*color-accent), background='{background}' (*color-background)\n"
            f"Fonts: heading=*font-heading, content=*font-content\n"
            f"USE aliases everywhere. Headings = *color-primary. Paragraphs/body = *color-text. "
            f"On dark bg, use *color-background for all text."
        )

        # Build component specifications for the suggested components
        suggested = section.get("components", [])
        comp_specs = build_component_specs(suggested)

        # Include available images if provided
        image_block = f"\n\n{image_context}\n" if image_context else ""

        # Build structured style rules block from styler's style_props
        style_props = section.get("style_props", {})
        style_rules_lines = []
        if style_props:
            shadow = style_props.get("container_shadow")
            radius = style_props.get("container_radius")
            blur = style_props.get("container_blur")
            border = style_props.get("container_border")
            btn_radius = style_props.get("button_radius")
            btn_shadow = style_props.get("button_shadow")
            bg_gradient = style_props.get("background_gradient")
            bg_transparency = style_props.get("background_transparency")
            dark_section = style_props.get("dark_section")

            if shadow:
                style_rules_lines.append(f"- Layout containers: shadow: {shadow}")
            if radius:
                style_rules_lines.append(f"- Layout containers: cornerStyle: {radius}")
            if blur:
                style_rules_lines.append(
                    "- Layout containers: blur: true  # glassmorphism backdrop-filter"
                )
            if border:
                style_rules_lines.append(f"- Layout containers: border color/width: {border}")
            if btn_radius:
                style_rules_lines.append(f"- Buttons: cornerStyle: {btn_radius}")
            if btn_shadow:
                style_rules_lines.append(f"- Buttons: shadow: {btn_shadow}")
            if bg_gradient:
                style_rules_lines.append(
                    "- Section background: use type: gradient with colorStart/colorEnd/direction"
                )
            if bg_transparency is not None and bg_transparency < 100:
                style_rules_lines.append(
                    f"- Section background: transparency: {bg_transparency}  "
                    f"# frosted/translucent effect"
                )
            if dark_section:
                style_rules_lines.append(
                    "- DARK SECTION: use *color-primary for background. "
                    "ALL text (heading/paragraph/eyebrow/caption) must use *color-background."
                )

        style_props_block = ""
        if style_rules_lines:
            style_props_block = (
                "\n[Component Style Rules — APPLY THESE to every layout container and button]\n"
                + "\n".join(style_rules_lines) + "\n"
            )

        # Include a brief style reference excerpt for additional context
        style_ref_block = ""
        if style_context and style_name:
            style_ref_block = (
                f"\n[Style Reference: {style_name} — follow these visual rules]\n"
                f"{style_context[:600]}\n"
            )

        # Include style guidance from planner if available
        style_notes = section.get("style_notes", "")
        style_block = f"\n[Style Guide for this section]\n{style_notes}\n" if style_notes else ""

        user_prompt = (
            f"[Section to Build. Remember Section is just logical structure not actual component.]\n"
            f"Type: {section_type}\n"
            f"Below is the Components Definition Yaml, with various properties of Components."
            f"Default Properties are already Mentioned, if you want to keep default property value, dont use that property."
            f"STRICTLY FOLLOW COMPONENT PROPERTIES IN SPECS BELOW \n\n\n```{comp_specs}```\n"
            f"[Reference Templates]\n{context}\n\n"
            f"For Font, Background colors recommended to use only theme alias"
            f" \n{theme_str}\n\n"
            f"{style_props_block}"
            f"{style_ref_block}"
            f"{image_block}"
            f"{style_block}"
            f"Description: {description}\n"
            f"Suggested components: {', '.join(suggested)}"
        )

        icons = section.get("icons", [])
        if icons:
            user_prompt += (
                f"\nAvailable icons: {', '.join(icons)}"
        )

        logger.debug(f"Builder user prompt ({len(user_prompt)} chars):\n{user_prompt[:500]}...")

        response = self.model.generate(BUILDER_SYSTEM, user_prompt)
        logger.info(f"Builder raw LLM response ({len(response)} chars):\n{response}")

        yaml_str = self._extract_yaml(response)
        logger.info(f"Builder extracted YAML ({len(yaml_str)} chars):\n{yaml_str}")
        return yaml_str

    def _extract_yaml(self, response: str) -> str:
        """Extract YAML from model response."""
        match = re.search(r'```(?:yaml)?\s*\n(.+?)```', response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()
