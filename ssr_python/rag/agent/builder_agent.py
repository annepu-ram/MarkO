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

    def build_section(self, section: dict, theme: dict, image_context: str = "") -> str:
        """Generate YAML for a single section.

        Args:
            section: {type, description, components} from planner outline
            theme: {primary, secondary, accent, background, heading_font, content_font}
            image_context: Pre-built image context string with available local URLs

        Returns:
            YAML string for this section's components
        """
        section_type = section.get("type", "other")
        description = section.get("description", "")

        # Retrieve section-level template chunks matching this section type
        chunks = self.search.search(
            f"{section_type} section template",
            top_k=config.vector_top_k,
            metadata_filter={"section_type": section_type},
            tier="section",
        )

        # Fallback: if section tier returned nothing, try without tier filter
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
