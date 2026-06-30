"""ssr_python/rag/agent/builder_agent.py — Per-section YAML generator.

Generates valid SwiftSites YAML for each section using component specs,
RAG examples, and natural language style direction from the styler.
"""
import re
import logging

from rag.config import config
from rag.indexing.metadata import SECTION_TYPE_ALIASES
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
        # Cached theme_str keyed by tuple(theme.items()) so repeated sections in
        # one page don't rebuild the same string. Reset when the theme changes.
        self._theme_cache: dict[tuple, str] = {}
        self._last_used_ids: set[str] = set()

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
        industry: str = "",
        content_volume: str | None = None,
        tone: str | None = None,
        conversion_intent: str | None = None,
        interactivity: str | None = None,
        exclude_chunk_ids: set[str] | None = None,
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
        raw_type = section.get("type", "other")
        # Normalize planner/UI section type to canonical index vocabulary
        # (e.g. "testimonials" → "testimonial", "booking_form" → "form_cta").
        # Without this, metadata_filter misses chunks indexed under the alias.
        section_type = SECTION_TYPE_ALIASES.get(raw_type, raw_type)
        description = section.get("description", "")
        layout_hint = section.get("layout_hint", "")

        # Normalize style name for metadata filter
        style_key = style_name.lower().replace(" ", "_") if style_name else ""

        # Build a query that carries the user's actual intent: section type +
        # style + industry + the planner's description. Without the description
        # every "hero" section retrieves the same candidates regardless of
        # business context.
        desc_snippet = description[:120] if description else ""
        search_query = " ".join(filter(None, [
            section_type, style_name, industry, desc_snippet,
        ])).strip() or f"{section_type} section template"

        # Soft-prefer ladder: progressively drop filters until we get hits.
        # Each rung adds graceful degradation — exact-match templates win when
        # they exist, but we never end up with zero results just because the
        # query was over-constrained.
        chunks = []
        rungs: list[dict] = []
        full_filter = {"section_type": section_type}
        if style_key:
            full_filter["visual_style"] = style_key
        if content_volume:
            full_filter["content_volume"] = content_volume
        if tone:
            full_filter["tone"] = tone
        if conversion_intent:
            full_filter["conversion_intent"] = conversion_intent
        if interactivity:
            full_filter["interactivity"] = interactivity

        # Build the ladder: full → drop interactivity → drop intent → drop tone
        # → drop content_volume → keep just style → keep just section_type.
        if len(full_filter) > 1:
            rungs.append(full_filter)
        for k in ("interactivity", "conversion_intent", "tone", "content_volume"):
            if k in full_filter:
                d = {kk: vv for kk, vv in full_filter.items() if kk != k}
                if d not in rungs:
                    rungs.append(d)
                full_filter = d
        if style_key:
            d = {"section_type": section_type, "visual_style": style_key}
            if d not in rungs:
                rungs.append(d)
        # Layout-biased rung: prefer templates matching the planner's layout hint
        if layout_hint:
            rungs.append({"section_type": section_type, "layout_primary": layout_hint})
        rungs.append({"section_type": section_type})

        for filter_d in rungs:
            chunks = self.search.search(
                search_query,
                top_k=config.vector_top_k,
                metadata_filter=filter_d,
                tier="section",
            )
            if chunks:
                logger.debug(f"Builder: {len(chunks)} chunks at filter={filter_d}")
                break

        # Final fallback: component tier
        if not chunks:
            logger.debug(f"Section tier empty for {section_type}, falling back to component tier")
            chunks = self.search.search(
                f"{section_type} section template",
                top_k=config.vector_top_k,
                metadata_filter={"section_type": section_type},
                tier="component",
            )

        # Exclude chunks already used by previous sections on this page
        if exclude_chunk_ids:
            chunks = [c for c in chunks if c.get("id") not in exclude_chunk_ids]

        # Rerank with a larger pool, then apply stratified diversity selection
        ranked = self.reranker.rerank(
            f"{section_type} {description}",
            chunks,
            top_k=config.section_rerank_pool_k,
        )

        # Stratified: pick final_top_k from different layout groups
        ranked = self._stratified_select(ranked, layout_hint, config.section_final_top_k)

        # Track used IDs for cross-section deduplication
        self._last_used_ids = {c.get("id") for c in ranked if c.get("id")}

        logger.debug(f"Builder using {len(ranked)} chunks after rerank")

        theme_str = self._build_theme_str(theme)

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

        response = self.model.generate(
            system, user_prompt,
            model_override=config.builder_model_name,
            temperature_override=config.builder_temperature if config.builder_model_name else None,
        )
        log_output(f"BUILDER [{section_type}]", response)

        yaml_str = self._extract_yaml(response)
        return yaml_str

    def _build_theme_str(self, theme: dict) -> str:
        """Compact theme string with palette + aliases. Cached by theme content."""
        dt = config.default_theme
        primary = theme.get('primary', dt['primary'])
        text_color = theme.get('text', dt['text'])
        secondary = theme.get('secondary', dt['secondary'])
        accent = theme.get('accent', dt['accent'])
        background = theme.get('background', dt['background'])
        key = (primary, text_color, secondary, accent, background)
        cached = self._theme_cache.get(key)
        if cached is not None:
            return cached
        theme_str = (
            f"Palette: primary={primary} text={text_color} secondary={secondary} "
            f"accent={accent} bg={background}. "
            f"Use *color-primary/*color-text/*color-secondary/*color-accent/*color-background "
            f"and *font-heading/*font-content."
        )
        # Bound cache size to avoid leaking across long-running processes.
        if len(self._theme_cache) > 32:
            self._theme_cache.clear()
        self._theme_cache[key] = theme_str
        return theme_str

    def _stratified_select(
        self,
        ranked: list[dict],
        layout_hint: str,
        top_k: int,
    ) -> list[dict]:
        """Pick top_k results ensuring layout_primary diversity."""
        if len(ranked) <= top_k:
            return ranked

        selected: list[dict] = []
        used_layouts: set[str] = set()

        # Priority 1: match layout_hint
        if layout_hint:
            for chunk in ranked:
                lp = chunk.get("metadata", {}).get("layout_primary", "")
                if lp == layout_hint:
                    selected.append(chunk)
                    used_layouts.add(lp)
                    break

        # Priority 2: fill from distinct layout groups (rank order)
        for chunk in ranked:
            if chunk in selected:
                continue
            lp = chunk.get("metadata", {}).get("layout_primary", "")
            if lp not in used_layouts:
                selected.append(chunk)
                used_layouts.add(lp)
                if len(selected) >= top_k:
                    break

        # Priority 3: fill remaining from rank order
        if len(selected) < top_k:
            for chunk in ranked:
                if chunk not in selected:
                    selected.append(chunk)
                    if len(selected) >= top_k:
                        break

        return selected

    def _extract_yaml(self, response: str) -> str:
        """Extract YAML from model response and sanitize common LLM errors."""
        match = re.search(r'```(?:yaml)?\s*\n(.+?)```', response, re.DOTALL)
        text = match.group(1).strip() if match else response.strip()
        return self._sanitize_raw_yaml(text)

    @staticmethod
    def _sanitize_raw_yaml(text: str) -> str:
        """Fix common fine-tuned model YAML quirks before parsing."""
        lines = text.split('\n')
        fixed = []
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                fixed.append(line)
                continue
            m = re.match(r'^(\s*\S+:\s+)(.*)', line)
            if not m:
                fixed.append(line)
                continue
            prefix, value = m.group(1), m.group(2)
            # Broken block scalar: |+text or |>text → quoted string
            block_match = re.match(r'^([|>][+\-]?)(\S.*)$', value)
            if block_match:
                value = '"' + block_match.group(2).replace('"', '\\"') + '"'
            # Unquoted parentheses: rgba(...), calc(...)
            elif not value.startswith(("'", '"', '[', '{', '|', '>', '*')) \
                    and '(' in value and ')' in value:
                value = '"' + value.replace('"', '\\"') + '"'
            fixed.append(prefix + value)
        return '\n'.join(fixed)
