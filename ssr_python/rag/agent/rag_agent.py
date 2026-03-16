"""ssr_python/rag/agent/rag_agent.py — Orchestrator: routes intent to single-call or multi-agent."""
import os
import re
import logging

import yaml as pyyaml

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.query_analyzer import QueryAnalyzer
from rag.agent.prompt_builder import PromptBuilder
from rag.agent.model_backend import ModelBackend
from rag.agent.planner_agent import PlannerAgent
from rag.agent.builder_agent import BuilderAgent
from rag.agent.styler_agent import StylerAgent
from rag.agent.stitcher import stitch_page

# ── RAG Agent Logging ──
# Configure a file handler for the entire `rag` namespace so all agents
# (planner, builder, rag_agent) write to the same log file.
_rag_logger = logging.getLogger("rag")
if not _rag_logger.handlers:
    _rag_logger.setLevel(logging.DEBUG)
    _log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
    os.makedirs(_log_dir, exist_ok=True)
    _fh = logging.FileHandler(os.path.join(_log_dir, "rag_agent.log"), encoding="utf-8")
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    _rag_logger.addHandler(_fh)

logger = logging.getLogger(__name__)

# ── Valid Component Names ──
# Authoritative list from _dispatcher.html — anything not in this set is invalid.
VALID_COMPONENTS = frozenset({
    "site", "page",
    "layout-row", "layout-column", "columnsgrid", "form",
    "heading", "paragraph", "eyebrow", "caption", "blockquote", "link",
    "image", "video", "gif", "video-background", "br",
    "button", "titlebar", "hamburger",
    "tabs", "accordion", "carousel", "ticker", "panorama-display",
    "icon", "badge", "rating", "progress-bar", "counter-up", "countdown",
    "textbox", "textarea", "dropdown", "checkbox", "radio", "calendar",
})


# Map intent action to search tier
INTENT_TO_TIER = {
    "create_section": "section",
    "create_page": "section",
    "modify": "component",
    "add": "component",
    "explain": "guide",
}


class RAGAgent:
    def __init__(self):
        self.search = HybridSearch()
        self.reranker = Reranker()
        self.analyzer = QueryAnalyzer()
        self.prompt_builder = PromptBuilder()
        self.model = ModelBackend()
        self.planner = PlannerAgent(self.search, self.model)
        self.styler = StylerAgent(self.model)
        self.builder = BuilderAgent(self.search, self.reranker, self.model)
        self._loaded = False

    def load(self):
        """Load indexes into memory. Call once at app startup."""
        if not self._loaded:
            self.search.load()
            self._loaded = True
            logger.info("RAG indexes loaded")

    def chat(
        self,
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
        selected_images: list | None = None,
        progress_fn=None,
    ) -> str:
        """Full RAG pipeline: analyze -> retrieve -> build prompt -> generate.

        Returns raw LLM response text (with ACTION comment + YAML block).
        The caller (llm_service.py) parses this via _parse_response().
        """
        self.load()

        logger.info("=" * 80)
        logger.info(f"RAG CHAT REQUEST: {message}")
        logger.info(f"Selected Images: {len(selected_images or [])} images")

        # 1. Analyze intent
        if progress_fn:
            progress_fn("Analyzing request...")
        intent = self.analyzer.analyze(message)
        logger.info(
            f"Intent: {intent.action} | section={intent.section_filter} "
            f"| industry={intent.industry_filter} | style={intent.style_filter} "
            f"| sub_queries={intent.sub_queries}"
        )

        # 2. Route to appropriate pipeline
        if intent.action == "create_page":
            return self._create_page_pipeline(message, intent,
                                               selected_images=selected_images,
                                               progress_fn=progress_fn)
        else:
            if progress_fn:
                progress_fn("Generating response...")
            return self._single_call_rag(message, intent, current_yaml, selected_component,
                                          selected_images=selected_images)

    def _single_call_rag(
        self,
        message: str,
        intent,
        current_yaml: str | None,
        selected_component: str | None,
        selected_images: list | None = None,
    ) -> str:
        """Standard RAG: retrieve -> prompt -> generate -> validate."""
        # Build metadata filter from intent
        meta_filter = {}
        if intent.section_filter:
            meta_filter["section_type"] = intent.section_filter
        if intent.industry_filter:
            meta_filter["industry"] = intent.industry_filter
        if intent.style_filter:
            meta_filter["style"] = intent.style_filter

        # Select search tier based on intent
        tier = INTENT_TO_TIER.get(intent.action, "section")

        # Retrieve for each sub-query, deduplicate
        all_chunks = []
        seen_ids = set()
        for sub_q in intent.sub_queries:
            results = self.search.search(
                sub_q,
                top_k=config.vector_top_k,
                metadata_filter=meta_filter or None,
                tier=tier,
            )
            for chunk in results:
                if chunk["id"] not in seen_ids:
                    seen_ids.add(chunk["id"])
                    all_chunks.append(chunk)

        # Fallback: if tier search returned too few results, retry with section tier
        if len(all_chunks) < config.min_fallback_results and tier != "section":
            logger.info(f"Tier '{tier}' returned {len(all_chunks)} results, falling back to 'section'")
            for sub_q in intent.sub_queries:
                results = self.search.search(
                    sub_q,
                    top_k=config.vector_top_k,
                    metadata_filter=meta_filter or None,
                    tier="section",
                )
                for chunk in results:
                    if chunk["id"] not in seen_ids:
                        seen_ids.add(chunk["id"])
                        all_chunks.append(chunk)

        # Rerank (no-op if config.use_reranker is False)
        ranked = self.reranker.rerank(message, all_chunks, top_k=config.final_top_k)
        logger.info(f"Retrieved {len(ranked)} chunks for generation")
        for i, c in enumerate(ranked):
            logger.debug(f"  Chunk {i}: {c.get('source_file', '?')} | {c.get('id', '?')}")

        # Build image context for prompt
        image_context = self._build_image_context(selected_images)

        # Build prompt
        augmented_message = f"{image_context}\n\n{message}" if image_context else message
        system, user_prompt = self.prompt_builder.build(
            intent=intent,
            chunks=ranked,
            message=augmented_message,
            current_yaml=current_yaml,
            selected_component=selected_component,
        )
        logger.debug(f"USER PROMPT ({len(user_prompt)} chars):\n{user_prompt[:500]}...")

        # Generate
        response = self.model.generate(system, user_prompt)
        logger.info(f"RAW LLM RESPONSE ({len(response)} chars):\n{response}")

        # Validation-guided retry
        response = self._validate_and_retry(response, message, system, ranked)

        return response

    def _build_image_context(self, selected_images: list | None) -> str:
        """Build image context string for LLM prompts."""
        if not selected_images:
            return ""
        lines = ["[AVAILABLE IMAGES - You MUST use these URLs in image components]"]
        for i, img in enumerate(selected_images, 1):
            url = img.get('url', '')
            alt = img.get('altText', '')
            orientation = img.get('orientation', 'unknown')
            photographer = img.get('photographer', '')
            credit = f" (Photo by {photographer})" if photographer else ""
            lines.append(f"{i}. {url} — \"{alt}\" [{orientation}]{credit}")
        lines.append("Match images to sections by orientation. Do NOT use external URLs.")
        return "\n".join(lines)

    def _create_page_pipeline(self, message: str, intent, selected_images=None, progress_fn=None) -> str:
        """Multi-agent pipeline: planner -> builder x N -> stitcher."""
        import json as _json

        # Agent 1: Plan the page structure
        if progress_fn:
            progress_fn("Planning site structure...")
        logger.info("-" * 40)
        logger.info("PLANNER AGENT: starting")
        outline, style_context = self.planner.plan(message, selected_images=selected_images)
        sections = outline.get("sections", [])
        logger.info(f"PLANNER AGENT: produced {len(sections)} sections")
        logger.info(f"PLANNER OUTPUT:\n{_json.dumps(outline, indent=2)}")

        # Validate and deduplicate planner image assignments
        if selected_images:
            valid_urls = {img.get("url") for img in selected_images}
            assigned_urls = set()
            for section in sections:
                unique_images = []
                for img in section.get("images", []):
                    url = img.get("url", "")
                    if url in valid_urls and url not in assigned_urls:
                        assigned_urls.add(url)
                        unique_images.append(img)
                section["images"] = unique_images

            unassigned = valid_urls - assigned_urls
            if unassigned:
                logger.warning(f"Planner did not assign {len(unassigned)} images: {unassigned}")

                # Build lookup for full image objects
                img_lookup = {img.get("url"): img for img in selected_images}

                # Identify visual sections that can accept more images
                VISUAL_TYPES = {"hero", "features", "about", "testimonials", "cta",
                                "portfolio", "team", "gallery", "services", "showcase"}
                visual_sections = [s for s in sections if s.get("type", "") in VISUAL_TYPES]

                # Fallback: if no visual sections matched, use all sections except FAQ/footer
                if not visual_sections:
                    NON_VISUAL = {"faq", "footer", "contact", "pricing"}
                    visual_sections = [s for s in sections if s.get("type", "") not in NON_VISUAL]

                # Round-robin distribute unassigned images
                if visual_sections:
                    for i, url in enumerate(sorted(unassigned)):
                        target = visual_sections[i % len(visual_sections)]
                        if "images" not in target:
                            target["images"] = []
                        target["images"].append(img_lookup[url])
                        logger.info(f"Redistributed image {url} → section '{target.get('type')}'")
                else:
                    logger.warning("No visual sections available for image redistribution")

        # Agent 1.5: Apply visual style props to each section
        if progress_fn:
            progress_fn("Applying visual style...")
        logger.info("-" * 40)
        logger.info("STYLER AGENT: starting")
        styled_outline = self.styler.style(outline, style_context)
        sections = styled_outline.get("sections", [])
        style_name = styled_outline.get("style_name", "")
        logger.info(f"STYLER AGENT: style_name='{style_name}', enriched {len(sections)} sections")
        logger.info(f"STYLER OUTPUT:\n{_json.dumps(styled_outline.get('sections', []), indent=2)}")

        # Agent 2: Build each section
        if progress_fn:
            progress_fn("Building components...")
        section_yamls = []
        theme = styled_outline.get("theme", outline.get("theme", {}))
        for i, section in enumerate(sections):
            logger.info("-" * 40)
            logger.info(f"BUILDER AGENT: section {i + 1}/{len(sections)} — type={section.get('type')}")
            logger.info(f"BUILDER INPUT: {_json.dumps(section, indent=2)}")

            # Build image context from planner-assigned images for THIS section only
            section_images = section.get("images", [])
            section_image_context = self._build_image_context(section_images) if section_images else ""

            yaml_str = self.builder.build_section(
                section, theme,
                image_context=section_image_context,
                style_name=style_name,
                style_context=style_context,
            )
            logger.info(f"BUILDER OUTPUT ({len(yaml_str)} chars):\n{yaml_str}")
            section_yamls.append(yaml_str)

        # Stitch into complete page
        if progress_fn:
            progress_fn("Assembling page...")
        logger.info("-" * 40)
        logger.info("STITCHER: assembling final page")
        full_yaml = stitch_page(styled_outline, section_yamls)
        logger.info(f"STITCHER OUTPUT ({len(full_yaml)} chars):\n{full_yaml}")

        # Return in expected format (ACTION comment + YAML block)
        page_title = styled_outline.get("page_title", "page")
        return (
            f"<!-- ACTION: create -->\n"
            f"Here's your {page_title}:\n\n"
            f"```yaml\n{full_yaml}```"
        )

    def _validate_and_retry(
        self, response: str, message: str, system: str, chunks: list[dict],
        max_retries: int = 1,
    ) -> str:
        """If YAML validation fails, retry with error context. Up to max_retries."""
        for attempt in range(max_retries):
            error = self._quick_validate(response)
            if error is None:
                return response

            logger.warning(f"Validation failed (attempt {attempt + 1}): {error}")

            # Re-prompt with error info
            retry_prompt = (
                f"Your previous output had a YAML error: {error}\n"
                f"Fix the error and regenerate. Original request: {message}"
            )
            _, user_prompt = self.prompt_builder.build(
                intent=self.analyzer.analyze(message),
                chunks=chunks,
                message=retry_prompt,
            )
            response = self.model.generate(system, user_prompt)

        return response

    def _quick_validate(self, response: str) -> str | None:
        """Fast validation: check YAML parses, has required structure, and valid component names.

        Returns error message string, or None if valid.
        """
        # Extract YAML block from response
        match = re.search(r"```(?:yaml)?\s*\n(.+?)```", response, re.DOTALL)
        if not match:
            # If no code block, check if response itself is YAML
            if "site:" not in response and "- name:" not in response:
                return None  # Probably an EXPLAIN response, skip validation
            yaml_str = response
        else:
            yaml_str = match.group(1)

        try:
            doc = pyyaml.safe_load(yaml_str)
        except pyyaml.YAMLError as e:
            return f"YAML parse error: {e}"

        if doc is None:
            return "Empty YAML document"

        # Validate component names recursively
        invalid = self._find_invalid_components(doc)
        if invalid:
            names_str = ", ".join(sorted(invalid))
            return (
                f"Invalid component names found: {names_str}. "
                f"Use ONLY valid SwiftSites components: "
                f"layout-row, layout-column, columnsgrid, heading, paragraph, eyebrow, "
                f"caption, blockquote, link, image, video, gif, button, titlebar, br, "
                f"icon, badge, rating, progress-bar, counter-up, countdown, tabs, "
                f"accordion, carousel, hamburger, ticker, textbox, textarea, dropdown, "
                f"checkbox, radio, calendar, video-background, panorama-display, form"
            )

        # Validate structure (children vs components, inline format, array props)
        structural = self._find_structural_errors(doc)
        if structural:
            return (
                f"Structural errors: {'; '.join(structural[:3])}. "
                f"RULES: Use 'components:' not 'children:'. "
                f"Use '- name: X' format not '- X:'. "
                f"Put array props (items/tabs/slides/columns) at component level, not inside properties."
            )

        return None

    def _find_invalid_components(self, doc) -> set[str]:
        """Recursively walk YAML and find any component names not in VALID_COMPONENTS."""
        invalid = set()

        if isinstance(doc, list):
            for item in doc:
                invalid |= self._find_invalid_components(item)
        elif isinstance(doc, dict):
            name = doc.get("name")
            if name and name not in VALID_COMPONENTS:
                invalid.add(name)
            # Check nested components
            for key in ("components", "items", "tabs", "slides", "columns", "children"):
                if key in doc:
                    invalid |= self._find_invalid_components(doc[key])

        return invalid

    # Keys that belong inside `properties:`, not at component level
    _PROPERTY_KEYS = frozenset({
        "layout", "appearance", "spacing", "typography", "label", "field",
        "behavior", "source", "playback", "responsive", "scroll",
        "branding", "navigation", "submit", "display", "action",
        "content", "animation", "poster",
    })

    def _find_structural_errors(self, doc) -> list[str]:
        """Recursively find structural errors (children, inline format, misplaced array props, orphaned properties)."""
        errors = []

        if isinstance(doc, list):
            for item in doc:
                errors.extend(self._find_structural_errors(item))
        elif isinstance(doc, dict):
            if "children" in doc:
                errors.append("'children:' used instead of 'components:'")
            # Inline format: dict has a component name key but no "name" key
            if "name" not in doc:
                for key in doc:
                    if key in VALID_COMPONENTS:
                        errors.append(f"inline format '- {key}:' instead of '- name: {key}'")
                        break
            # Array props inside properties
            if "properties" in doc and isinstance(doc["properties"], dict):
                for key in ("items", "tabs", "slides", "columns"):
                    if key in doc["properties"]:
                        errors.append(f"'{key}' inside properties instead of component level")
            # Properties outside `properties:` wrapper
            if "name" in doc:
                for key in doc:
                    if key in self._PROPERTY_KEYS:
                        errors.append(f"'{key}' at component level — must be inside 'properties:'")
            # Recurse
            for key in ("components", "items", "tabs", "slides", "columns", "children"):
                if key in doc and isinstance(doc[key], list):
                    for item in doc[key]:
                        errors.extend(self._find_structural_errors(item))

        return errors
