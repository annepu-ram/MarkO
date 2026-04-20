"""ssr_python/rag/agent/rag_agent.py — Orchestrator: routes intent to single-call or multi-agent."""
import os
import re
import logging

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
from rag.agent.prompt_logger import log_prompt, log_output
from rag.agent.yaml_fixer import quick_validate, auto_fix_yaml

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
            logger.debug("RAG indexes loaded")

    def chat(
        self,
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
        selected_images: list | None = None,
        progress_fn=None,
        business_context: dict | None = None,
    ) -> str:
        """Full RAG pipeline: analyze -> retrieve -> build prompt -> generate.

        Returns raw LLM response text (with ACTION comment + YAML block).
        The caller (llm_service.py) parses this via _parse_response().

        When `business_context` is provided (guided flow), routes to
        _create_page_guided() which skips the LLM planner and uses the
        user's structured selections as the outline.
        """
        self.load()

        # Guided flow short-circuit — business_context is the authoritative
        # signal (Phase 3). No intent detection needed; we already know the
        # user wants a page and we have their selections.
        if business_context:
            if progress_fn:
                progress_fn("Planning site structure...")
            return self._create_page_guided(
                business_context,
                selected_images=selected_images,
                progress_fn=progress_fn,
            )

        # 1. Analyze intent
        if progress_fn:
            progress_fn("Analyzing request...")
        intent = self.analyzer.analyze(message)
        logger.info(
            f"=== RAG CHAT: intent={intent.action} "
            f"| section={intent.section_filter} | style={intent.style_filter} "
            f"| {message}"
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
            meta_filter["visual_style"] = intent.style_filter

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
            logger.debug(f"Tier '{tier}' returned {len(all_chunks)} results, falling back to 'section'")
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
        log_prompt("SINGLE-CALL", system, user_prompt)

        # Generate
        response = self.model.generate(system, user_prompt)
        log_output("SINGLE-CALL", response)

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

    def _create_page_guided(
        self,
        business_context: dict,
        selected_images: list | None = None,
        progress_fn=None,
    ) -> str:
        """Guided-flow pipeline — deterministic planner, then styler + builders.

        Differences from _create_page_pipeline:
          * Planner is skipped entirely (no LLM call). The outline is built
            directly from the user's guided-flow selections.
          * Style chunks are retrieved using the user's explicit style
            preference rather than the intent analyzer.
          * Builders receive real business content so they do not
            hallucinate names, products, prices, or testimonials.
        """
        self.load()

        # 1. Deterministic outline from user selections
        outline = self.planner.plan_from_context(business_context)
        if not outline.get("sections"):
            # Guard: user posted an empty context. Fall back to a useful error.
            logger.warning("_create_page_guided: no sections in business_context")
            return (
                "<!-- ACTION: error -->\n"
                "No sections were selected for generation. Please re-run the "
                "guided flow and pick at least one section."
            )

        # 2. Retrieve style chunks using the user's explicit preference.
        style_pref = (business_context.get("style_preference") or "").strip().lower()
        color_pref = (business_context.get("color_preference") or "").strip()
        industry = (business_context.get("industry") or "").strip()
        business_name = (business_context.get("business_name") or "").strip()

        style_meta = {"visual_style": style_pref} if style_pref else None
        style_query = " ".join(filter(None, [
            style_pref.replace("_", " "),
            color_pref,
            industry,
            business_name,
        ])) or "website style"

        style_chunks = self.search.search(
            style_query,
            top_k=config.style_top_k,
            tier="style",
            metadata_filter=style_meta,
        )
        if not style_chunks and style_meta:
            # Preference didn't match the metadata index — retry unfiltered.
            style_chunks = self.search.search(
                style_query, top_k=config.style_top_k, tier="style",
            )
        style_context = "\n\n".join(c.get("content", "") for c in style_chunks)

        # 3. Styler — visual design + image assignment (1 LLM call)
        if progress_fn:
            progress_fn("Designing visual style...")
        styled_outline = self.styler.style(
            outline,
            planner_md="",  # no planner markdown in guided flow
            style_context=style_context,
            selected_images=selected_images,
            style_hints=style_pref,
            color_hints=color_pref,
            business_context=business_context,
        )
        sections = styled_outline.get("sections", [])
        style_name = styled_outline.get("style_name", "")
        theme = styled_outline.get("theme") or config.default_theme

        # 4. Builders — per-section YAML with REAL business content (N LLM calls)
        business_description = business_context.get("description") or ""
        section_yamls = []
        for i, section in enumerate(sections):
            if progress_fn:
                progress_fn(f"Building section {i + 1}/{len(sections)}...")
            section_image_context = section.get("image_context", "")

            yaml_str = self.builder.build_section(
                section,
                theme,
                image_context=section_image_context,
                style_name=style_name,
                style_notes=section.get("style_notes", ""),
                business_name=business_name,
                business_content=section.get("business_content") or {},
                business_description=business_description,
            )
            section_yamls.append(yaml_str)

        # 5. Stitch (no LLM)
        if progress_fn:
            progress_fn("Assembling page...")
        full_yaml = stitch_page(styled_outline, section_yamls)

        full_yaml, fixes = auto_fix_yaml(full_yaml)
        if fixes:
            logger.info(f"Auto-fixed guided page ({len(fixes)} fixes): {fixes}")

        log_output("STITCHER", full_yaml)

        page_title = styled_outline.get("page_title") or outline.get("page_title") or "page"
        friendly = business_name or page_title
        return (
            f"<!-- ACTION: create -->\n"
            f"Here's your {friendly} website:\n\n"
            f"```yaml\n{full_yaml}```"
        )

    def _create_page_pipeline(self, message: str, intent, selected_images=None, progress_fn=None) -> str:
        """Multi-agent pipeline: planner -> styler -> builder x N -> stitcher."""

        # Agent 1: Plan the page structure (markdown output, no images)
        if progress_fn:
            progress_fn("Planning site structure...")
        planner_md = self.planner.plan(message)
        outline = self.planner.parse_outline(planner_md)

        # Retrieve style chunks for the styler
        style_meta = {"visual_style": intent.style_filter} if intent.style_filter else None
        style_chunks = self.search.search(message, top_k=config.style_top_k, tier="style", metadata_filter=style_meta)
        style_context = "\n\n".join([c['content'] for c in style_chunks])

        # Agent 2: Styler — visual design direction + image assignment
        if progress_fn:
            progress_fn("Designing visual style...")
        styled_outline = self.styler.style(
            outline, planner_md, style_context,
            selected_images=selected_images,
            style_hints=intent.style_keywords,
            color_hints=intent.color_keywords,
        )
        sections = styled_outline.get("sections", [])
        style_name = styled_outline.get("style_name", "")

        # Agent 3: Build each section (YAML from specs + style direction)
        section_yamls = []
        theme = styled_outline.get("theme") or config.default_theme
        for i, section in enumerate(sections):
            if progress_fn:
                progress_fn(f"Building section {i + 1}/{len(sections)}...")
            # Use pre-rendered image context from styler
            section_image_context = section.get("image_context", "")

            yaml_str = self.builder.build_section(
                section, theme,
                image_context=section_image_context,
                style_name=style_name,
                style_notes=section.get("style_notes", ""),
            )
            section_yamls.append(yaml_str)

        # Stitch into complete page
        if progress_fn:
            progress_fn("Assembling page...")
        full_yaml = stitch_page(styled_outline, section_yamls)

        # Auto-fix token/name errors the stitcher doesn't catch
        full_yaml, fixes = auto_fix_yaml(full_yaml)
        if fixes:
            logger.info(f"Auto-fixed stitched page ({len(fixes)} fixes): {fixes}")

        log_output("STITCHER", full_yaml)

        # Return in expected format (ACTION comment + YAML block)
        page_title = styled_outline.get("page_title", outline.get("page_title", "page"))
        return (
            f"<!-- ACTION: create -->\n"
            f"Here's your {page_title}:\n\n"
            f"```yaml\n{full_yaml}```"
        )

    def _validate_and_retry(
        self, response: str, message: str, system: str, chunks: list[dict],
        max_retries: int = 1,
    ) -> str:
        """If YAML validation fails, auto-fix first, then retry with LLM if needed."""
        for attempt in range(max_retries):
            error = quick_validate(response)
            if error is None:
                return response

            logger.warning(f"Validation failed (attempt {attempt + 1}): {error}")

            # Try auto-fix before expensive LLM retry
            fixed = self._attempt_auto_fix(response)
            if fixed is not None:
                return fixed

            # Fall through to LLM retry
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

    def _attempt_auto_fix(self, response: str) -> str | None:
        """Try to auto-fix YAML errors. Returns fixed response or None."""
        match = re.search(r"```(?:yaml)?\s*\n(.+?)```", response, re.DOTALL)
        if not match:
            return None

        fixed_yaml, fixes = auto_fix_yaml(match.group(1))
        if not fixes:
            return None

        logger.info(f"Auto-fixed {len(fixes)} issues: {fixes}")
        fixed_response = response[:match.start(1)] + fixed_yaml + response[match.end(1):]

        # Re-validate after fix
        if quick_validate(fixed_response) is not None:
            logger.warning("Auto-fix insufficient, falling through to LLM retry")
            return None

        return fixed_response
