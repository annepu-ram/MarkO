"""Evaluate retrieval quality with sample queries across tiers, diversity, and relevance.

Usage:
    cd ssr_python
    python -m rag.scripts.evaluate_retrieval
    python -m rag.scripts.evaluate_retrieval --verbose
    python -m rag.scripts.evaluate_retrieval --tier section
"""
import sys
import os
import json
import time
import argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.retrieval.hybrid import HybridSearch
from rag.agent.query_analyzer import QueryAnalyzer

# ── Test Suites ──

# Suite 1: Basic relevance — expected keywords should appear in top-5 results
RELEVANCE_QUERIES = [
    {
        "query": "hero section for a bakery website",
        "expected_section": "hero",
        "expected_keywords": ["hero", "bakery"],
        "tier": "section",
    },
    {
        "query": "pricing table with three tiers",
        "expected_section": "pricing",
        "expected_keywords": ["pricing"],
        "tier": "section",
    },
    {
        "query": "testimonial carousel with star ratings",
        "expected_section": "testimonial",
        "expected_keywords": ["testimonial", "rating"],
        "tier": "section",
    },
    {
        "query": "footer with social links and copyright",
        "expected_section": "footer",
        "expected_keywords": ["footer"],
        "tier": "section",
    },
    {
        "query": "restaurant menu with food images",
        "expected_section": "product",
        "expected_keywords": ["restaurant", "image"],
        "tier": "section",
    },
    {
        "query": "FAQ accordion section",
        "expected_section": "faq",
        "expected_keywords": ["accordion", "faq"],
        "tier": "section",
    },
    {
        "query": "SaaS feature grid with icons",
        "expected_section": "features",
        "expected_keywords": ["icon", "feature"],
        "tier": "section",
    },
    {
        "query": "team members grid with photos",
        "expected_section": "team",
        "expected_keywords": ["team", "image"],
        "tier": "section",
    },
    {
        "query": "contact form with email and message fields",
        "expected_section": "contact",
        "expected_keywords": ["form", "contact"],
        "tier": "section",
    },
    {
        "query": "call to action with a sign up button",
        "expected_section": "cta",
        "expected_keywords": ["button"],
        "tier": "section",
    },
    {
        "query": "product cards with images and prices",
        "expected_section": "product",
        "expected_keywords": ["product", "image"],
        "tier": "section",
    },
    {
        "query": "navigation header with logo and links",
        "expected_section": "navigation",
        "expected_keywords": ["titlebar", "link"],
        "tier": "section",
    },
    {
        "query": "countdown timer for a flash sale",
        "expected_section": "other",
        "expected_keywords": ["countdown"],
        "tier": "section",
    },
    {
        "query": "badge component for new arrivals",
        "expected_section": "product",
        "expected_keywords": ["badge"],
        "tier": "component",
    },
    {
        "query": "image gallery with hover effects",
        "expected_section": "gallery",
        "expected_keywords": ["image"],
        "tier": "section",
    },
    {
        "query": "stats counter section with big numbers",
        "expected_section": "stats",
        "expected_keywords": ["counter"],
        "tier": "section",
    },
    {
        "query": "tabs component for product details",
        "expected_section": "product",
        "expected_keywords": ["tabs"],
        "tier": "component",
    },
    {
        "query": "video background hero section",
        "expected_section": "hero",
        "expected_keywords": ["video", "hero"],
        "tier": "section",
    },
    {
        "query": "blockquote testimonial with author citation",
        "expected_section": "testimonial",
        "expected_keywords": ["blockquote"],
        "tier": "section",
    },
    {
        "query": "ticker scrolling client logos",
        "expected_section": "other",
        "expected_keywords": ["ticker"],
        "tier": "section",
    },
]

# Suite 2: Business-specific queries — tests the enhanced "Perfect for" matching
BUSINESS_QUERIES = [
    {
        "query": "create a landing page for a dental clinic",
        "expected_categories": ["hero", "features_benefits", "contact_section", "team_about"],
        "expected_keywords": ["dental", "clinic"],
        "tier": "section",
    },
    {
        "query": "website for a coffee shop",
        "expected_categories": ["hero", "product_cards", "rating"],
        "expected_keywords": ["coffee", "restaurant", "bakery", "cafe"],
        "tier": "section",
    },
    {
        "query": "online store product page",
        "expected_categories": ["product_cards", "hero", "pricing_plan_cards"],
        "expected_keywords": ["product", "store", "shop", "ecommerce"],
        "tier": "section",
    },
    {
        "query": "law firm website with attorney profiles",
        "expected_categories": ["hero", "team_about", "contact_section"],
        "expected_keywords": ["law", "legal", "consulting"],
        "tier": "section",
    },
    {
        "query": "gym membership pricing page",
        "expected_categories": ["pricing_plan_cards", "hero", "features_benefits"],
        "expected_keywords": ["gym", "fitness", "pricing"],
        "tier": "section",
    },
    {
        "query": "real estate property listing",
        "expected_categories": ["hero", "product_cards", "portfolio_showcase_cards"],
        "expected_keywords": ["real estate", "property"],
        "tier": "section",
    },
    {
        "query": "tutoring center with class schedule",
        "expected_categories": ["hero", "schedule", "features_benefits"],
        "expected_keywords": ["tutoring", "education", "class", "school"],
        "tier": "section",
    },
    {
        "query": "hotel booking page with room photos",
        "expected_categories": ["hero", "product_cards", "panorama-display"],
        "expected_keywords": ["hotel", "hospitality", "room"],
        "tier": "section",
    },
    {
        "query": "car dealership showroom",
        "expected_categories": ["hero", "product_cards", "portfolio_showcase_cards"],
        "expected_keywords": ["car", "auto", "vehicle", "dealer"],
        "tier": "section",
    },
    {
        "query": "SaaS dashboard analytics page",
        "expected_categories": ["dashboard_data_cards", "hero", "features_benefits"],
        "expected_keywords": ["dashboard", "analytics", "saas"],
        "tier": "section",
    },
    {
        "query": "photography portfolio showcase",
        "expected_categories": ["portfolio_showcase_cards", "hero"],
        "expected_keywords": ["portfolio", "photography", "gallery"],
        "tier": "section",
    },
    {
        "query": "restaurant with menu and reservations",
        "expected_categories": ["hero", "product_cards", "rating", "contact_section"],
        "expected_keywords": ["restaurant", "menu", "food"],
        "tier": "section",
    },
]

# Suite 3: Tier-specific queries — verify correct tier returns results
TIER_QUERIES = [
    {
        "query": "hero section with gradient background",
        "tier": "section",
        "expected_doc_type": "template_section",
        "min_results": 2,
    },
    {
        "query": "add a button component",
        "tier": "component",
        "expected_doc_type": "template",
        "min_results": 1,
    },
    {
        "query": "how does the accordion component work",
        "tier": "guide",
        "expected_doc_type": "guide",
        "min_results": 1,
    },
    {
        "query": "pricing card with features list",
        "tier": "section",
        "expected_doc_type": "template_section",
        "min_results": 2,
    },
    {
        "query": "modify heading text color",
        "tier": "component",
        "expected_doc_type": "template",
        "min_results": 1,
    },
    {
        "query": "what properties does image component have",
        "tier": "guide",
        "expected_doc_type": "guide",
        "min_results": 1,
    },
    {
        "query": "testimonial section with reviews",
        "tier": "section",
        "expected_doc_type": "template_section",
        "min_results": 2,
    },
    {
        "query": "add icon to layout column",
        "tier": "component",
        "expected_doc_type": "template",
        "min_results": 1,
    },
]

# Suite 4: Diversity queries — top-5 results should come from multiple source files
DIVERSITY_QUERIES = [
    {
        "query": "hero section for website",
        "tier": "section",
        "min_unique_sources": 3,  # At least 3 different source files in top 5
    },
    {
        "query": "pricing plans comparison",
        "tier": "section",
        "min_unique_sources": 3,
    },
    {
        "query": "product card with image",
        "tier": "section",
        "min_unique_sources": 3,
    },
    {
        "query": "testimonial section",
        "tier": "section",
        "min_unique_sources": 3,
    },
    {
        "query": "navigation header",
        "tier": "section",
        "min_unique_sources": 2,
    },
    {
        "query": "footer with links",
        "tier": "section",
        "min_unique_sources": 2,
    },
]

# Suite 5: Section type accuracy — metadata section_type should match expected
SECTION_TYPE_QUERIES = [
    {
        "query": "hero banner for tech startup",
        "tier": "section",
        "expected_section_type": "hero",
        "match_top_n": 3,  # At least 1 of top-3 should have this section_type
    },
    {
        "query": "pricing plans with toggle",
        "tier": "section",
        "expected_section_type": "pricing",
        "match_top_n": 3,
    },
    {
        "query": "customer testimonials wall",
        "tier": "section",
        "expected_section_type": "testimonial",
        "match_top_n": 3,
    },
    {
        "query": "FAQ questions and answers",
        "tier": "section",
        "expected_section_type": "faq",
        "match_top_n": 3,
    },
    {
        "query": "feature grid with icons and descriptions",
        "tier": "section",
        "expected_section_type": "features",
        "match_top_n": 3,
    },
    {
        "query": "team members about us",
        "tier": "section",
        "expected_section_type": "team",
        "match_top_n": 3,
    },
    {
        "query": "contact us form",
        "tier": "section",
        "expected_section_type": "contact",
        "match_top_n": 3,
    },
    {
        "query": "product showcase cards",
        "tier": "section",
        "expected_section_type": "product",
        "match_top_n": 3,
    },
    {
        "query": "portfolio gallery projects",
        "tier": "section",
        "expected_section_type": "gallery",
        "match_top_n": 3,
    },
    {
        "query": "blog posts and articles",
        "tier": "section",
        "expected_section_type": "blog",
        "match_top_n": 3,
    },
]


def run_relevance_suite(search, analyzer, verbose=False):
    """Suite 1: Basic keyword relevance in top-5 results."""
    print("\n" + "=" * 60)
    print("Suite 1: RELEVANCE (keyword match in top-5)")
    print("=" * 60)

    passed = 0
    for i, test in enumerate(RELEVANCE_QUERIES, 1):
        query = test["query"]
        expected_kw = test["expected_keywords"]
        tier = test.get("tier", "section")

        intent = analyzer.analyze(query)
        meta_filter = {}
        if intent.section_filter:
            meta_filter["section_type"] = intent.section_filter

        start = time.time()
        results = search.search(query, top_k=5, metadata_filter=meta_filter or None, tier=tier)
        elapsed_ms = (time.time() - start) * 1000

        combined_text = " ".join(r.get("content", "").lower() for r in results)
        hits = [kw for kw in expected_kw if kw in combined_text]
        is_pass = len(hits) > 0

        if is_pass:
            passed += 1
        status = "PASS" if is_pass else "FAIL"

        print(f"  [{status}] {i:2d}. {query}")
        if verbose or not is_pass:
            print(f"       Intent: {intent.action} | Section: {intent.section_filter} | Tier: {tier} | {elapsed_ms:.0f}ms")
            print(f"       Hits: {hits} / Expected: {expected_kw}")
            if results:
                print(f"       Top: {results[0].get('source_file', 'none')}")
            print()

    return passed, len(RELEVANCE_QUERIES)


def run_business_suite(search, analyzer, verbose=False):
    """Suite 2: Business-specific queries — concrete business names should surface relevant templates."""
    print("\n" + "=" * 60)
    print("Suite 2: BUSINESS MATCHING (specific business queries)")
    print("=" * 60)

    passed = 0
    for i, test in enumerate(BUSINESS_QUERIES, 1):
        query = test["query"]
        expected_kw = test["expected_keywords"]
        expected_cats = test.get("expected_categories", [])
        tier = test.get("tier", "section")

        results = search.search(query, top_k=5, tier=tier)

        # Check keyword presence
        combined_text = " ".join(r.get("content", "").lower() for r in results)
        kw_hits = [kw for kw in expected_kw if kw in combined_text]

        # Check category presence (from source_file path)
        result_cats = set()
        for r in results:
            src = r.get("source_file", "")
            parts = src.replace("\\", "/").split("/")
            for p in parts:
                if p in (
                    "hero", "pricing_plan_cards", "product_cards", "review_testimonial_cards",
                    "portfolio_showcase_cards", "story_blog_cards", "navigation_footer",
                    "dashboard_data_cards", "features_benefits", "faq_section",
                    "contact_section", "banner_announcement", "cta_banners", "ticker",
                    "badge", "countdown", "counter-up", "icon", "progress-bar", "rating",
                    "panorama-display", "team_about", "schedule", "titlebar", "styles",
                ):
                    result_cats.add(p)

        cat_hits = [c for c in expected_cats if c in result_cats]
        is_pass = len(kw_hits) > 0 or len(cat_hits) > 0

        if is_pass:
            passed += 1
        status = "PASS" if is_pass else "FAIL"

        print(f"  [{status}] {i:2d}. {query}")
        if verbose or not is_pass:
            print(f"       Keywords: {kw_hits}/{expected_kw} | Categories: {cat_hits}/{expected_cats}")
            print(f"       Result categories: {sorted(result_cats)}")
            if results:
                print(f"       Top: {results[0].get('source_file', 'none')}")
            print()

    return passed, len(BUSINESS_QUERIES)


def run_tier_suite(search, verbose=False):
    """Suite 3: Tier-specific queries — verify correct doc_types are returned per tier."""
    print("\n" + "=" * 60)
    print("Suite 3: TIER ROUTING (correct doc_type per tier)")
    print("=" * 60)

    passed = 0
    for i, test in enumerate(TIER_QUERIES, 1):
        query = test["query"]
        tier = test["tier"]
        expected_dt = test.get("expected_doc_type")
        min_results = test.get("min_results", 1)

        results = search.search(query, top_k=5, tier=tier)

        # Check doc_type matches
        doc_types = [r.get("doc_type", "unknown") for r in results]
        dt_match = any(dt == expected_dt for dt in doc_types) if expected_dt else True
        enough_results = len(results) >= min_results

        is_pass = dt_match and enough_results
        if is_pass:
            passed += 1
        status = "PASS" if is_pass else "FAIL"

        print(f"  [{status}] {i:2d}. [{tier}] {query}")
        if verbose or not is_pass:
            dt_counts = Counter(doc_types)
            print(f"       Expected doc_type: {expected_dt} | Got: {dict(dt_counts)}")
            print(f"       Results: {len(results)} (min {min_results})")
            print()

    return passed, len(TIER_QUERIES)


def run_diversity_suite(search, verbose=False):
    """Suite 4: Diversity — top-5 results should come from multiple source files."""
    print("\n" + "=" * 60)
    print("Suite 4: DIVERSITY (unique sources in top-5)")
    print("=" * 60)

    passed = 0
    for i, test in enumerate(DIVERSITY_QUERIES, 1):
        query = test["query"]
        tier = test.get("tier", "section")
        min_unique = test["min_unique_sources"]

        results = search.search(query, top_k=5, tier=tier)

        sources = set(r.get("source_file", "") for r in results)
        unique_count = len(sources)

        is_pass = unique_count >= min_unique
        if is_pass:
            passed += 1
        status = "PASS" if is_pass else "FAIL"

        print(f"  [{status}] {i:2d}. {query}")
        print(f"       Unique sources: {unique_count}/{min_unique} required")
        if verbose or not is_pass:
            for s in sorted(sources):
                print(f"         - {s}")
            print()

    return passed, len(DIVERSITY_QUERIES)


def run_section_type_suite(search, verbose=False):
    """Suite 5: Section type accuracy — metadata section_type should match in top results."""
    print("\n" + "=" * 60)
    print("Suite 5: SECTION TYPE ACCURACY (metadata match)")
    print("=" * 60)

    passed = 0
    for i, test in enumerate(SECTION_TYPE_QUERIES, 1):
        query = test["query"]
        tier = test.get("tier", "section")
        expected_st = test["expected_section_type"]
        top_n = test.get("match_top_n", 3)

        results = search.search(query, top_k=5, tier=tier)

        # Check if any of the top-N have the expected section_type
        top_results = results[:top_n]
        section_types = [
            r.get("metadata", {}).get("section_type", "unknown")
            for r in top_results
        ]
        is_pass = expected_st in section_types

        if is_pass:
            passed += 1
        status = "PASS" if is_pass else "FAIL"

        print(f"  [{status}] {i:2d}. {query}")
        if verbose or not is_pass:
            print(f"       Expected: {expected_st} | Top-{top_n} types: {section_types}")
            if results:
                print(f"       Top: {results[0].get('source_file', 'none')}")
            print()

    return passed, len(SECTION_TYPE_QUERIES)


def evaluate(args):
    print("=" * 60)
    print("RAG Retrieval Evaluation — Enhanced")
    print("=" * 60)

    search = HybridSearch()
    analyzer = QueryAnalyzer()

    print("Loading indexes...")
    search.load()
    print("Indexes loaded.")

    verbose = args.verbose
    tier_filter = args.tier

    suite_results = []

    # Run suites (skip if tier filter doesn't match)
    if not tier_filter or tier_filter in ("section", "component"):
        p, t = run_relevance_suite(search, analyzer, verbose)
        suite_results.append(("Relevance", p, t))

    if not tier_filter or tier_filter == "section":
        p, t = run_business_suite(search, analyzer, verbose)
        suite_results.append(("Business Match", p, t))

    if not tier_filter:
        p, t = run_tier_suite(search, verbose)
        suite_results.append(("Tier Routing", p, t))

    if not tier_filter or tier_filter == "section":
        p, t = run_diversity_suite(search, verbose)
        suite_results.append(("Diversity", p, t))

    if not tier_filter or tier_filter == "section":
        p, t = run_section_type_suite(search, verbose)
        suite_results.append(("Section Type", p, t))

    # Overall summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_passed = 0
    total_tests = 0
    for name, passed, total in suite_results:
        pct = (passed / total * 100) if total > 0 else 0
        marker = "OK" if pct >= 70 else "!!"
        print(f"  [{marker}] {name:20s}: {passed:2d}/{total:2d} ({pct:.0f}%)")
        total_passed += passed
        total_tests += total

    overall_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n  OVERALL: {total_passed}/{total_tests} ({overall_pct:.0f}%)")

    target = 75
    if overall_pct >= target:
        print(f"  TARGET MET: >= {target}%")
    else:
        print(f"  BELOW TARGET: {overall_pct:.0f}% < {target}%")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details for passing tests too")
    parser.add_argument("--tier", choices=["section", "component", "guide"], help="Run only tests for this tier")
    evaluate(parser.parse_args())
