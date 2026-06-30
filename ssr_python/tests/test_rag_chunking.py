"""Regression tests for RAG chunking and metadata enrichment.

These tests pin down behaviors that the RAG-quality plan tightened:
  * `template_full_page` chunks are not emitted by default.
  * Per-component and section chunks carry AST-derived `component_types`
    (no regex re-scan).
  * Style chunks expose structured metadata (mood / industries / palettes / fonts).
  * Icon chunks carry a `groups` list.
  * `INDUSTRY_PATTERNS` covers all 22 canonical industries.
  * Folder name → canonical `section_type` mapping works.
"""
import sys
import os
import textwrap
from pathlib import Path
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.config import config, INDUSTRY_DEFAULT_STYLE
from rag.indexing.chunker import DocumentChunker
from rag.indexing.metadata import (
    INDUSTRY_PATTERNS,
    FOLDER_TO_SECTION_TYPE,
    extract_metadata,
)
from rag.indexing.icon_chunker import _classify


HERO_YAML = textwrap.dedent("""\
    # Test Hero
    # Section type: hero
    # Layout: split
    # Visual style: modern_minimalist
    # Perfect for: SaaS, fintech

    - name: page
      slug: home
      title: Home
      properties: {}
      components:
        - name: layout-row
          properties:
            layout: { wrap: wrap }
          components:
            - name: heading
              properties: { text: Hello }
            - name: button
              properties: { text: Go }
""")


@pytest.fixture
def tmp_yaml_file(tmp_path):
    f = tmp_path / "example_templates" / "hero" / "01_test.yaml"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(HERO_YAML, encoding="utf-8")
    return f


class TestChunkingNoFullPage:
    def test_no_full_page_chunks_by_default(self, tmp_yaml_file):
        assert config.emit_full_page is False, "Default should suppress full_page chunks"
        chunks = DocumentChunker().chunk_file(tmp_yaml_file)
        doc_types = {c.doc_type for c in chunks}
        assert "template_full_page" not in doc_types
        # Should still get per-component + one section chunk.
        assert "template" in doc_types
        assert "template_section" in doc_types

    def test_full_page_emitted_when_enabled(self, tmp_yaml_file, monkeypatch):
        monkeypatch.setattr(config, "emit_full_page", True)
        chunks = DocumentChunker().chunk_file(tmp_yaml_file)
        doc_types = [c.doc_type for c in chunks]
        assert "template_full_page" in doc_types


class TestComponentTypesFromAST:
    def test_per_component_chunk_carries_ast_types(self, tmp_yaml_file):
        chunks = DocumentChunker().chunk_file(tmp_yaml_file)
        component_chunks = [c for c in chunks if c.doc_type == "template"]
        # The first top-level component is layout-row; its AST contains
        # layout-row, heading, button (recursive walk).
        assert component_chunks
        types = component_chunks[0].metadata.get("component_types", [])
        assert "layout-row" in types
        assert "heading" in types
        assert "button" in types

    def test_section_chunk_has_component_count_and_chars(self, tmp_yaml_file):
        chunks = DocumentChunker().chunk_file(tmp_yaml_file)
        section_chunk = next(c for c in chunks if c.doc_type == "template_section")
        meta = section_chunk.metadata
        assert meta.get("component_count") == 1
        assert isinstance(meta.get("chars"), int) and meta["chars"] > 0
        assert "layout-row" in meta.get("component_types", [])


class TestIndustryCoverage:
    def test_all_canonical_industries_have_a_pattern(self):
        canonical = set(INDUSTRY_DEFAULT_STYLE.keys())
        covered = set(INDUSTRY_PATTERNS.keys())
        missing = canonical - covered
        assert not missing, f"INDUSTRY_PATTERNS missing entries for: {missing}"

    @pytest.mark.parametrize("industry,sample_text", [
        ("homeservices", "plumbing service for residential homes"),
        ("beauty", "premium hair salon and spa"),
        ("food_services", "artisan brewery and tasting room"),
        ("retail_local", "neighborhood florist shop"),
        ("professional_services", "tax accounting firm"),
        ("trades", "custom carpentry workshop"),
        ("community", "volunteer community center"),
        ("fitness_recreation", "yoga studio and pilates classes"),
        ("construction", "general contractor renovation"),
        ("automotive_services", "auto repair and detailing"),
    ])
    def test_industry_regex_matches_expected_text(self, industry, sample_text):
        import re
        pat = INDUSTRY_PATTERNS[industry]
        assert re.search(pat, sample_text), f"{industry} pattern missed '{sample_text}'"


class TestFolderToSectionType:
    @pytest.mark.parametrize("folder,expected", [
        # Canonical (post-reorg) folder names map identity.
        ("hero", "hero"),
        ("pricing", "pricing"),
        ("testimonials", "testimonials"),
        ("features", "features"),
        ("contact", "contact"),
        ("dashboard", "dashboard"),
        # Transitional aliases still resolve.
        ("pricing_plan_cards", "pricing"),
        ("review_testimonial_cards", "testimonials"),
        ("features_benefits", "features"),
        ("contact_section", "contact"),
        ("dashboard_data_cards", "dashboard"),
    ])
    def test_known_folder_maps_to_section(self, folder, expected):
        assert FOLDER_TO_SECTION_TYPE[folder] == expected


class TestStyleChunkMetadata:
    def test_style_block_parses_mood_industries_palettes(self):
        body = textwrap.dedent("""\
            Mood: clean, professional, sleek
            Industries: SaaS, consulting, legal
            Sections: hero, features, pricing

            Themes:
            1. Slate Professional — primary #1E3A5F, text #4B5563, fonts Inter/Inter
            2. Warm Neutral — primary #2D3748, text #4A4540, fonts Inter/Inter

            Properties:
            - Container: radius sm
        """)
        meta = DocumentChunker._parse_style_block("Style: Modern Minimalist", body)
        assert meta["mood"] == ["clean", "professional", "sleek"]
        assert "saas" in meta["industries"]
        assert "hero" in meta["sections"]
        assert "Slate Professional" in meta["palette_names"]
        assert "Warm Neutral" in meta["palette_names"]
        assert any(f.startswith("Inter") for f in meta["fonts"])
        assert meta["visual_style"] == ["modern_minimalist"]


class TestExtractMetadataPreservesStyleAndIcon:
    def test_style_chunk_metadata_not_clobbered(self):
        from rag.indexing.chunker import Chunk
        c = Chunk(
            id="x", content="...", context_header="", content_with_context="x",
            source_file="STYLE_THEMES_REFERENCE.md", doc_type="style",
            metadata={
                "section_heading": "Style: Glassmorphism",
                "visual_style": ["glassmorphism"],
                "mood": ["frosted", "translucent"],
                "industries": ["saas"],
            },
            token_count=0,
        )
        extract_metadata(c)
        assert c.metadata["visual_style"] == ["glassmorphism"]
        assert c.metadata["mood"] == ["frosted", "translucent"]


class TestIconGroupClassification:
    @pytest.mark.parametrize("name,expected_group", [
        ("shopping-cart", "ecommerce"),
        ("facebook", "social"),
        ("home", "navigation"),
        ("mail", "communication"),
        ("calendar", "time"),
        ("camera", "media"),
        ("lock", "security"),
        ("car", "transport"),
        ("heart", "health"),
        ("coffee", "food"),
    ])
    def test_classify_returns_expected_group(self, name, expected_group):
        groups = _classify(name)
        assert expected_group in groups, f"{name} → {groups} missed {expected_group}"


class TestQueryAnalyzerDecomposition:
    """Verify the loosened sub-query decomposition handles common phrasings."""

    @pytest.mark.parametrize("query,min_subs", [
        ("Build a website with hero, pricing, and testimonials", 3),
        ("Create a page containing hero and footer", 2),
        ("Make a website that has hero, features, and contact", 3),
        ("Build a site including pricing and testimonials", 2),
    ])
    def test_decomposes_natural_phrasings(self, query, min_subs):
        from rag.agent.query_analyzer import QueryAnalyzer
        intent = QueryAnalyzer().analyze(query)
        assert len(intent.sub_queries) >= min_subs, (
            f"Expected ≥{min_subs} sub-queries, got {intent.sub_queries}"
        )
