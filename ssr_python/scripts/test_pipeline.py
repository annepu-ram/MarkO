#!/usr/bin/env python
"""
CLI test script for the RAG multi-agent pipeline.

Usage:
    cd ssr_python
    python scripts/test_pipeline.py "Create a bakery website with hero, menu, and testimonials"

Drives the exact same pipeline as rag_agent._create_page_pipeline() and
displays every intermediate input/output including full prompts.
"""
import sys
import os
import time

# Add ssr_python to path so rag.* imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import yaml as pyyaml

from rag.config import config
from rag.agent.query_analyzer import QueryAnalyzer
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.model_backend import ModelBackend
from rag.agent.planner_agent import PlannerAgent
from rag.agent.styler_agent import StylerAgent
from rag.agent.builder_agent import BuilderAgent
from rag.agent.stitcher import stitch_page
from rag.agent.rag_agent import VALID_COMPONENTS

# ── ANSI Colors ──
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
DIM     = "\033[2m"
BOLD    = "\033[1m"
RESET   = "\033[0m"


def header(step: int, total: int, title: str):
    """Print a step header."""
    print(f"\n{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  [Step {step}/{total}] {title}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 80}{RESET}")


def sub_header(title: str):
    """Print a sub-section header."""
    print(f"\n{MAGENTA}  {'─' * 60}{RESET}")
    print(f"{MAGENTA}  {title}{RESET}")
    print(f"{MAGENTA}  {'─' * 60}{RESET}")


def label(text: str):
    """Print a label."""
    print(f"\n  {BOLD}{text}{RESET}")


def block(content: str, color: str = DIM, max_lines: int = 0):
    """Print indented block content. max_lines=0 means no truncation."""
    lines = content.split("\n")
    limit = max_lines if max_lines > 0 else len(lines)
    truncated = len(lines) > limit
    for line in lines[:limit]:
        print(f"  {color}{line}{RESET}")
    if truncated:
        print(f"  {DIM}... ({len(lines) - limit} more lines truncated){RESET}")


def success(text: str):
    print(f"\n  {GREEN}{BOLD}{text}{RESET}")


def error(text: str):
    print(f"\n  {RED}{BOLD}{text}{RESET}")


def find_invalid_components(doc) -> set:
    """Recursively walk YAML and find invalid component names."""
    invalid = set()
    if isinstance(doc, list):
        for item in doc:
            invalid |= find_invalid_components(item)
    elif isinstance(doc, dict):
        name = doc.get("name")
        if name and name not in VALID_COMPONENTS:
            invalid.add(name)
        for key in ("components", "items", "tabs", "slides", "columns"):
            if key in doc:
                invalid |= find_invalid_components(doc[key])
    return invalid


class VerboseModelBackend(ModelBackend):
    """Wraps ModelBackend to display full prompts and responses in the terminal."""

    def __init__(self):
        super().__init__()
        self.call_count = 0

    def generate(self, system: str, user_prompt: str) -> str:
        self.call_count += 1

        sub_header(f"LLM Call #{self.call_count} — System Prompt")
        block(system, DIM)

        sub_header(f"LLM Call #{self.call_count} — User Prompt")
        block(user_prompt, DIM)

        print(f"\n  {DIM}Calling {config.model_backend}/{config.model_name}...{RESET}", flush=True)
        t = time.time()
        response = super().generate(system, user_prompt)
        elapsed = time.time() - t
        print(f"  {DIM}({elapsed:.1f}s, {len(response)} chars){RESET}")

        sub_header(f"LLM Call #{self.call_count} — Raw Response")
        block(response, YELLOW)

        return response


def main():
    if len(sys.argv) < 2:
        print(f"{RED}Usage: python scripts/test_pipeline.py \"Your prompt here\"{RESET}")
        print(f"{DIM}Example: python scripts/test_pipeline.py \"Create a bakery website with hero, menu, and testimonials\"{RESET}")
        sys.exit(1)

    prompt = sys.argv[1]
    total_steps = 7
    t_start = time.time()

    print(f"\n{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  RAG Multi-Agent Pipeline Test{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 80}{RESET}")
    label("INPUT PROMPT:")
    print(f"  {YELLOW}{prompt}{RESET}")
    label("MODEL:")
    print(f"  {DIM}backend={config.model_backend}  model={config.model_name}{RESET}")
    base_url = os.getenv("RAG_OLLAMA_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    has_key = "yes" if os.getenv("OLLAMA_API_KEY") else "no"
    print(f"  {DIM}url={base_url}  api_key={has_key}{RESET}")

    # ── Load indexes ──
    print(f"\n  {DIM}Loading RAG indexes...{RESET}", end=" ", flush=True)
    search = HybridSearch()
    search.load()
    reranker = Reranker()
    model = VerboseModelBackend()
    print(f"{GREEN}done{RESET}")

    # ══════════════════════════════════════════════════════════════════════
    # Step 1: Intent Analysis
    # ══════════════════════════════════════════════════════════════════════
    header(1, total_steps, "Intent Analysis")

    analyzer = QueryAnalyzer()
    intent = analyzer.analyze(prompt)

    label("RESULT:")
    print(f"  action:           {GREEN}{intent.action}{RESET}")
    print(f"  section_filter:   {intent.section_filter or DIM + 'none' + RESET}")
    print(f"  industry_filter:  {intent.industry_filter or DIM + 'none' + RESET}")
    print(f"  style_filter:     {intent.style_filter or DIM + 'none' + RESET}")
    print(f"  component_filter: {intent.component_filter or DIM + '[]' + RESET}")
    print(f"  sub_queries:      {intent.sub_queries}")

    if intent.action != "create_page":
        print(f"\n  {YELLOW}Note: Intent is '{intent.action}', not 'create_page'.")
        print(f"  The multi-agent pipeline only runs for create_page.")
        print(f"  Proceeding anyway to test the pipeline.{RESET}")

    # ══════════════════════════════════════════════════════════════════════
    # Step 2: Planner Agent (markdown output — structure only)
    # ══════════════════════════════════════════════════════════════════════
    header(2, total_steps, "Planner Agent — Site Outline (Markdown)")

    planner = PlannerAgent(search, model)

    try:
        planner_md = planner.plan(prompt)
    except (ValueError, Exception) as e:
        error(f"Planner failed: {e}")
        print(f"\n  {RED}Cannot continue without a valid outline. Exiting.{RESET}")
        sys.exit(1)

    label("RAW PLANNER MARKDOWN:")
    block(planner_md, GREEN)

    # Parse into structured outline
    outline = planner.parse_outline(planner_md)
    sections = outline.get("sections", [])

    label("PARSED OUTLINE:")
    print(f"  {BOLD}Page title:{RESET} {outline.get('page_title', '?')}")
    print(f"  {BOLD}Sections:{RESET} {len(sections)}")
    for i, s in enumerate(sections):
        print(f"    [{i}] type={s.get('type', '?')}  components={s.get('components', [])}")

    # ══════════════════════════════════════════════════════════════════════
    # Step 3: Style Chunk Retrieval (moved from planner to orchestrator)
    # ══════════════════════════════════════════════════════════════════════
    header(3, total_steps, "Style Chunk Retrieval")

    style_chunks = search.search(prompt, top_k=config.style_top_k, tier="style")
    style_context = "\n\n".join([c['content'] for c in style_chunks])

    label(f"RETRIEVED {len(style_chunks)} STYLE CHUNKS:")
    block(style_context or "(empty)", DIM)

    # ══════════════════════════════════════════════════════════════════════
    # Step 4: Styler Agent — Visual Design Direction
    # ══════════════════════════════════════════════════════════════════════
    header(4, total_steps, "Styler Agent — Visual Design")

    styler = StylerAgent(model)
    styled_outline = styler.style(outline, planner_md, style_context, selected_images=[])

    sections = styled_outline.get("sections", [])
    style_name = styled_outline.get("style_name", "")
    theme = styled_outline.get("theme") or config.default_theme

    label(f"STYLE NAME: {style_name or '(none)'}")

    label("THEME:")
    for k, v in theme.items():
        print(f"  {DIM}{k}: {v}{RESET}")

    label("STYLED SECTIONS:")
    for i, s in enumerate(sections):
        images = s.get("images", [])
        img_count = f"  images={len(images)}" if images else ""
        print(f"  [{i}] {s.get('type', '?')}  dark={s.get('dark_section', '?')}{img_count}")
        if s.get("style_notes"):
            print(f"      {DIM}style_notes:{RESET}")
            for line in s["style_notes"].split("\n"):
                print(f"        {DIM}{line}{RESET}")

    # ══════════════════════════════════════════════════════════════════════
    # Step 5: Builder Agent (per section — translator role)
    # ══════════════════════════════════════════════════════════════════════
    header(5, total_steps, f"Builder Agent — {len(sections)} Sections")

    builder = BuilderAgent(search, reranker, model)
    section_yamls = []

    for i, section in enumerate(sections):
        section_type = section.get("type", "other")

        label(f"Section {i + 1}/{len(sections)}: {section_type}")

        yaml_str = builder.build_section(
            section, theme,
            image_context="",
            style_name=style_name,
            style_notes=section.get("style_notes", ""),
        )

        label("EXTRACTED YAML:")
        block(yaml_str, GREEN)

        section_yamls.append(yaml_str)

    # ══════════════════════════════════════════════════════════════════════
    # Step 6: Stitcher
    # ══════════════════════════════════════════════════════════════════════
    header(6, total_steps, "Stitcher — Page Assembly")

    full_yaml = stitch_page(styled_outline, section_yamls)

    label("FINAL PAGE YAML:")
    block(full_yaml, GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # Step 7: Validation
    # ══════════════════════════════════════════════════════════════════════
    header(7, total_steps, "Validation")

    # YAML syntax check
    try:
        doc = pyyaml.safe_load(full_yaml)
        success("YAML syntax: PASS")
    except pyyaml.YAMLError as e:
        error(f"YAML syntax: FAIL — {e}")
        doc = None

    # Component name check
    if doc:
        invalid = find_invalid_components(doc)
        if invalid:
            error(f"Invalid components: FAIL — {', '.join(sorted(invalid))}")
        else:
            success("Component names: PASS (all valid)")

    # ══════════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    n_builders = len(sections)
    print(f"\n{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  Summary{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"  Prompt:      {prompt}")
    print(f"  Style:       {style_name or '(none)'}")
    print(f"  Sections:    {len(sections)}")
    print(f"  LLM calls:   {model.call_count} (1 planner + 1 styler + {n_builders} builders)")
    print(f"  Total time:  {elapsed:.1f}s")
    print(f"  YAML lines:  {len(full_yaml.splitlines())}")
    if doc:
        invalid = find_invalid_components(doc)
        status = f"{GREEN}PASS{RESET}" if not invalid else f"{RED}FAIL ({len(invalid)} invalid){RESET}"
    else:
        status = f"{RED}FAIL (syntax error){RESET}"
    print(f"  Validation:  {status}")
    print(f"  Log file:    logs/rag_agent.log")
    print()


if __name__ == "__main__":
    main()
