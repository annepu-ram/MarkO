"""Dump the exact prompt the RAG agent would send for a sample query.

Useful for eyeballing prompt size + content before/after RAG-quality changes.

Usage (from `ssr_python/`):
    python -m rag.scripts.dump_prompt "create a vegan bakery website"
    python -m rag.scripts.dump_prompt --section hero --style glassmorphism --industry saas \
        --description "split-screen hero with bold tagline" --kind builder

Modes:
    --kind single   : Renders the single-call (modify/add/explain) prompt
                      that PromptBuilder produces.
    --kind builder  : Simulates a Builder.build_section() call (without
                      hitting an LLM) so you can see the full per-section
                      prompt the multi-agent pipeline would send.
"""
from __future__ import annotations

import argparse
import sys
import textwrap

import tiktoken

# Allow running as `python -m rag.scripts.dump_prompt` from ssr_python/.
sys.path.insert(0, str((__import__("pathlib").Path(__file__).resolve().parents[2])))

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.query_analyzer import QueryAnalyzer
from rag.agent.prompt_builder import PromptBuilder
from rag.agent.prompt_loader import load_system, render_user
from rag.agent.component_specs import build_component_specs

_enc = tiktoken.get_encoding("cl100k_base")


def _tokens(s: str) -> int:
    return len(_enc.encode(s or ""))


def _print_prompt(label: str, system: str, user: str) -> None:
    sys_tok = _tokens(system)
    user_tok = _tokens(user)
    total = sys_tok + user_tok
    sep = "=" * 78
    print(sep)
    print(f"{label}  |  system={sys_tok}  user={user_tok}  total={total} tokens")
    print(sep)
    print("--- SYSTEM ---")
    print(system.rstrip())
    print()
    print("--- USER ---")
    print(user.rstrip())
    print()


def dump_single(message: str) -> None:
    search = HybridSearch()
    search.load()
    reranker = Reranker()
    analyzer = QueryAnalyzer()
    builder = PromptBuilder()

    intent = analyzer.analyze(message)
    print(f"[intent] action={intent.action} section={intent.section_filter} "
          f"industry={intent.industry_filter} style={intent.style_filter} "
          f"section_filters={intent.section_filters} sub_queries={intent.sub_queries}")

    meta_filter = {}
    if intent.section_filter:
        meta_filter["section_type"] = intent.section_filter
    if intent.industry_filter:
        meta_filter["industry"] = intent.industry_filter
    if intent.style_filter:
        meta_filter["visual_style"] = intent.style_filter
    from rag.agent.rag_agent import INTENT_TO_TIER
    tier = INTENT_TO_TIER.get(intent.action, "section")

    chunks = []
    seen = set()
    for sub in intent.sub_queries:
        for c in search.search(sub, top_k=config.vector_top_k,
                                metadata_filter=meta_filter or None, tier=tier):
            if c["id"] not in seen:
                seen.add(c["id"])
                chunks.append(c)

    ranked = reranker.rerank(message, chunks, top_k=config.final_top_k_for(tier))
    print(f"[retrieval] tier={tier} candidates={len(chunks)} ranked={len(ranked)} "
          f"sources={[c.get('source_file', '?') for c in ranked]}")

    system, user = builder.build(intent=intent, chunks=ranked, message=message)
    _print_prompt("SINGLE-CALL", system, user)


def dump_builder(section_type: str, description: str, style: str,
                  industry: str) -> None:
    search = HybridSearch()
    search.load()
    reranker = Reranker()

    style_key = style.lower().replace(" ", "_") if style else ""
    desc_snippet = description[:120]
    query = " ".join(filter(None, [section_type, style, industry, desc_snippet]))

    chunks = []
    if style_key:
        chunks = search.search(query, top_k=config.vector_top_k,
                                metadata_filter={"section_type": section_type,
                                                 "visual_style": style_key},
                                tier="section")
    if not chunks:
        chunks = search.search(query, top_k=config.vector_top_k,
                                metadata_filter={"section_type": section_type},
                                tier="section")
    ranked = reranker.rerank(f"{section_type} {description}", chunks,
                              top_k=config.final_top_k_for("section"))

    print(f"[retrieval] tier=section candidates={len(chunks)} ranked={len(ranked)} "
          f"sources={[c.get('source_file', '?') for c in ranked]}")

    suggested = ["layout-row", "heading", "paragraph", "button", "image"]
    comp_specs = build_component_specs(suggested) if not ranked else ""
    theme_str = ("Palette: primary=#1a1a1a text=#374151 secondary=#6b7280 "
                 "accent=#3b82f6 bg=#ffffff. "
                 "Use *color-primary/*color-text/*color-secondary/*color-accent/*color-background.")

    system = load_system("builder")
    user = render_user("builder",
        section_type=section_type,
        description=description,
        suggested=suggested,
        comp_specs=comp_specs,
        ranked_chunks=ranked,
        theme_str=theme_str,
        style_notes="Use bold contrast and generous spacing." if style else "",
        image_context="",
        icons=[],
        business_name="",
        business_description="",
        business_content={},
    )
    _print_prompt(f"BUILDER [{section_type}]", system, user)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("message", nargs="?", default="",
                    help="User query (for --kind single)")
    p.add_argument("--kind", choices=("single", "builder"), default="single")
    p.add_argument("--section", default="hero")
    p.add_argument("--style", default="modern_minimalist")
    p.add_argument("--industry", default="")
    p.add_argument("--description", default="")
    args = p.parse_args()

    if args.kind == "builder":
        desc = args.description or f"A {args.style.replace('_', ' ')} {args.section} section."
        dump_builder(args.section, desc, args.style, args.industry)
    else:
        if not args.message:
            p.error("message is required for --kind single")
        dump_single(args.message)


if __name__ == "__main__":
    main()
