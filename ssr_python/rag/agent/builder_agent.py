"""ssr_python/rag/agent/builder_agent.py — Per-section YAML generator.

Generates valid SwiftSites YAML for each section using component specs,
RAG examples, and natural language style direction from the styler.
"""
import re
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.model_backend import ModelBackend
from rag.agent.component_specs import build_component_specs
from rag.agent.prompt_logger import log_prompt, log_output
from rag.agent.prompt_loader import load_system, render_user

logger = logging.getLogger(__name__)


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
        style_notes: str = "",
        business_name: str = "",
        business_content: dict | None = None,
        business_description: str = "",
    ) -> str:
        """Generate YAML for a single section.

        Args:
            section: Section dict from styled outline (type, description, components, etc.)
            theme: {primary, secondary, accent, background, heading_font, content_font}
            image_context: Pre-built image context string with available local URLs
            style_name: Identified style name for search query enrichment
            style_notes: Natural language design direction from the styler
            business_name: User's business name (guided flow only); empty otherwise
            business_content: Per-section real content dict from the guided flow
                (e.g. {"tagline": "...", "cta_text": "..."}). When provided the
                builder must use these values EXACTLY instead of hallucinating.
            business_description: Short business pitch (guided flow only)

        Returns:
            YAML string for this section's components
        """
        section_type = section.get("type", "other")
        description = section.get("description", "")

        # Normalize style name for metadata filter
        style_key = style_name.lower().replace(" ", "_") if style_name else ""

        # Enrich search query with style name for better semantic matching
        search_query = f"{section_type} {style_name} section" if style_name else f"{section_type} section template"

        # Try style-filtered retrieval first
        chunks = []
        if style_key:
            chunks = self.search.search(
                search_query,
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type, "visual_style": style_key},
                tier="section",
            )
            if chunks:
                logger.debug(
                    f"Builder: found {len(chunks)} style-tagged chunks "
                    f"(section_type={section_type}, visual_style={style_key})"
                )

        # Fallback: section_type only
        if not chunks:
            chunks = self.search.search(
                search_query,
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type},
                tier="section",
            )

        # Final fallback: component tier
        if not chunks:
            logger.debug(f"Section tier empty for {section_type}, falling back to component tier")
            chunks = self.search.search(
                f"{section_type} section template",
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type},
                tier="component",
            )

        # Rerank for relevance
        ranked = self.reranker.rerank(
            f"{section_type} {description}",
            chunks,
            top_k=config.final_top_k,
        )

        logger.debug(f"Builder using {len(ranked)} chunks after rerank")

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

        # Build component specifications
        suggested = section.get("components", [])
        comp_specs = build_component_specs(suggested)

        icons = section.get("icons", [])

        # Guided-flow real content — prefer per-section payload, then fall back
        # to anything the planner stashed on the section dict (plan_from_context).
        effective_business_content = business_content
        if not effective_business_content:
            effective_business_content = section.get("business_content") or {}

        system = load_system("builder")
        user_prompt = render_user("builder",
            section_type=section_type,
            description=description,
            suggested=suggested,
            comp_specs=comp_specs,
            ranked_chunks=ranked,
            theme_str=theme_str,
            style_notes=style_notes,
            image_context=image_context,
            icons=icons,
            business_name=business_name,
            business_description=business_description,
            business_content=effective_business_content or {},
        )

        log_prompt(f"BUILDER [{section_type}]", system, user_prompt)

        response = self.model.generate(system, user_prompt)
        log_output(f"BUILDER [{section_type}]", response)

        yaml_str = self._extract_yaml(response)
        return yaml_str

    def _extract_yaml(self, response: str) -> str:
        """Extract YAML from model response."""
        match = re.search(r'```(?:yaml)?\s*\n(.+?)```', response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()
