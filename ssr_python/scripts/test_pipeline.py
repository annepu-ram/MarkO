#!/usr/bin/env python
"""
CLI test script for the RAG multi-agent pipeline.

Usage:
    cd ssr_python
    python scripts/test_pipeline.py "Create a bakery website with hero, menu, and testimonials"

Drives each pipeline component directly and displays every intermediate
input/output with clear visual separation.
"""
import sys
import os
import json
import time
import re
import textwrap

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
from rag.agent.planner_agent import PLANNER_SYSTEM, PlannerAgent
from rag.agent.builder_agent import BUILDER_SYSTEM, BuilderAgent
from rag.agent.component_specs import build_component_specs, VALID_TOKENS
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


def block(content: str, color: str = DIM, max_lines: int = 40):
    """Print indented block content, optionally truncated."""
    lines = content.split("\n")
    truncated = len(lines) > max_lines
    for line in lines[:max_lines]:
        print(f"  {color}{line}{RESET}")
    if truncated:
        print(f"  {DIM}... ({len(lines) - max_lines} more lines truncated){RESET}")


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


def main():
    if len(sys.argv) < 2:
        print(f"{RED}Usage: python scripts/test_pipeline.py \"Your prompt here\"{RESET}")
        print(f"{DIM}Example: python scripts/test_pipeline.py \"Create a bakery website with hero, menu, and testimonials\"{RESET}")
        sys.exit(1)

    prompt = sys.argv[1]
    total_steps = 5
    llm_calls = 0
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
    model = ModelBackend()
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
    # Step 2: Planner Agent
    # ══════════════════════════════════════════════════════════════════════
    header(2, total_steps, "Planner Agent — Site Outline")

    # 2a: Retrieve outline chunks
    sub_header("Retrieved Outline Chunks")
    outline_chunks = search.search(prompt, top_k=3, tier="guide")
    if not outline_chunks:
        print(f"  {YELLOW}No outline chunks found (metadata_filter may be too strict).{RESET}")
        print(f"  {DIM}Falling back to unfiltered search...{RESET}")
        outline_chunks = search.search(prompt, top_k=3)

    for i, c in enumerate(outline_chunks):
        src = os.path.basename(c.get("source_file", "?"))
        snippet = c["content"][:200].replace("\n", " ")
        print(f"  {DIM}[{i}] {src}{RESET}")
        print(f"      {DIM}{snippet}...{RESET}")

    # 2b: Build planner prompt
    context = "\n\n".join([
        f"--- Reference: {c['source_file']} ---\n{c['content'][:800]}"
        for c in outline_chunks
    ])
    planner_user_prompt = f"[Reference Outlines]\n{context}\n\n[User Request]\n{prompt}"

    sub_header("Planner System Prompt")
    block(PLANNER_SYSTEM, DIM, max_lines=20)

    sub_header("Planner User Prompt")
    block(planner_user_prompt, DIM, max_lines=30)

    # 2c: Call LLM
    sub_header("Planner LLM Response")
    print(f"  {DIM}Calling {config.model_backend}/{config.model_name}...{RESET}", flush=True)
    t_plan = time.time()
    planner_raw = model.generate(PLANNER_SYSTEM, planner_user_prompt)
    llm_calls += 1
    print(f"  {DIM}({time.time() - t_plan:.1f}s){RESET}")
    block(planner_raw, YELLOW, max_lines=50)

    # 2d: Parse JSON outline
    sub_header("Parsed Outline")
    planner = PlannerAgent(search, model)
    try:
        outline = planner._parse_outline(planner_raw)
        print(f"  {GREEN}JSON parsed successfully{RESET}")
        block(json.dumps(outline, indent=2), GREEN, max_lines=40)
    except (ValueError, json.JSONDecodeError) as e:
        error(f"Failed to parse planner JSON: {e}")
        print(f"\n  {RED}Cannot continue without a valid outline. Exiting.{RESET}")
        sys.exit(1)

    sections = outline.get("sections", [])
    theme = outline.get("theme", {})
    print(f"\n  {BOLD}Page title:{RESET} {outline.get('page_title', '?')}")
    print(f"  {BOLD}Theme:{RESET} {json.dumps(theme, indent=None)}")
    print(f"  {BOLD}Sections:{RESET} {len(sections)}")
    for i, s in enumerate(sections):
        print(f"    [{i}] type={s.get('type', '?')}  components={s.get('components', [])}")

    # ══════════════════════════════════════════════════════════════════════
    # Step 3: Builder Agent (per section)
    # ══════════════════════════════════════════════════════════════════════
    header(3, total_steps, f"Builder Agent — {len(sections)} Sections")

    section_yamls = []
    builder = BuilderAgent(search, reranker, model)

    for i, section in enumerate(sections):
        section_type = section.get("type", "other")
        description = section.get("description", "")

        sub_header(f"Section {i + 1}/{len(sections)}: {section_type}")

        # 3a: Retrieve template chunks
        label(f"Retrieving chunks for section_type={section_type}")
        chunks = search.search(
            f"{section_type} section template",
            top_k=config.vector_top_k,
            metadata_filter={"section_type": section_type},
        )
        ranked = reranker.rerank(f"{section_type} {description}", chunks, top_k=3)
        print(f"  {DIM}Retrieved {len(chunks)} -> reranked to {len(ranked)} chunks{RESET}")
        for j, c in enumerate(ranked):
            src = os.path.basename(c.get("source_file", "?"))
            print(f"    {DIM}[{j}] {src}{RESET}")

        # 3b: Build component specs for this section
        suggested = section.get("components", [])
        comp_specs = build_component_specs(suggested)

        label("Component Specifications (injected)")
        block(comp_specs, DIM, max_lines=30)

        label("Valid Tokens (injected)")
        block(VALID_TOKENS, DIM, max_lines=15)

        # 3c: Build builder prompt
        context = "\n\n".join([
            f"--- Example: {c['source_file']} ---\n{c['content']}"
            for c in ranked
        ])
        primary = theme.get('primary', '#1a1a1a')
        secondary = theme.get('secondary', '#666')
        accent = theme.get('accent', '#3b82f6')
        background = theme.get('background', '#ffffff')
        theme_str = (
            f"Colors: primary='{primary}' (*color-primary), secondary='{secondary}' (*color-secondary), "
            f"accent='{accent}' (*color-accent), background='{background}' (*color-background)\n"
            f"Fonts: heading=*font-heading, content=*font-content\n"
            f"USE aliases everywhere. Text = *color-primary on light bg, *color-background on dark bg."
        )
        builder_user_prompt = (
            f"[Component Specifications — ONLY these properties are valid]\n{comp_specs}\n"
            f"Properties not listed here are auto-filled by defaults — do NOT invent new ones.\n\n"
            f"[Valid Tokens]\n{VALID_TOKENS}\n\n"
            f"[Reference Templates]\n{context}\n\n"
            f"[Theme]\n{theme_str}\n\n"
            f"[Section to Build]\n"
            f"Type: {section_type}\n"
            f"Description: {description}\n"
            f"Suggested components: {', '.join(suggested)}"
        )

        sub_header("Builder System Prompt")
        block(BUILDER_SYSTEM, DIM, max_lines=80)

        label("Builder User Prompt (full)")
        block(builder_user_prompt, DIM, max_lines=200)

        # 3d: Call LLM
        label("Builder LLM Response")
        print(f"  {DIM}Calling {config.model_backend}/{config.model_name}...{RESET}", flush=True)
        t_build = time.time()
        builder_raw = model.generate(BUILDER_SYSTEM, builder_user_prompt)
        llm_calls += 1
        print(f"  {DIM}({time.time() - t_build:.1f}s){RESET}")
        block(builder_raw, YELLOW, max_lines=50)

        # 3e: Extract YAML
        yaml_str = builder._extract_yaml(builder_raw)
        label("Extracted YAML")
        block(yaml_str, GREEN, max_lines=40)

        section_yamls.append(yaml_str)

    # ══════════════════════════════════════════════════════════════════════
    # Step 4: Stitcher
    # ══════════════════════════════════════════════════════════════════════
    header(4, total_steps, "Stitcher — Page Assembly")

    full_yaml = stitch_page(outline, section_yamls)

    label("FINAL PAGE YAML:")
    block(full_yaml, GREEN, max_lines=100)

    # ══════════════════════════════════════════════════════════════════════
    # Step 5: Validation
    # ══════════════════════════════════════════════════════════════════════
    header(5, total_steps, "Validation")

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
    print(f"\n{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  Summary{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 80}{RESET}")
    print(f"  Prompt:      {prompt}")
    print(f"  Sections:    {len(sections)}")
    print(f"  LLM calls:   {llm_calls} (1 planner + {llm_calls - 1} builders)")
    print(f"  Total time:  {elapsed:.1f}s")
    print(f"  YAML lines:  {len(full_yaml.splitlines())}")
    if doc:
        invalid = find_invalid_components(doc)
        status = f"{GREEN}PASS{RESET}" if not invalid else f"{RED}FAIL ({len(invalid)} invalid){RESET}"
    else:
        status = f"{RED}FAIL (syntax error){RESET}"
    print(f"  Validation:  {status}")
    print()


if __name__ == "__main__":
    main()
