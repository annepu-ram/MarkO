"""Tests for externalized Jinja2 prompt templates."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.agent.prompt_loader import load_system, render_user


TEMPLATE_NAMES = ("planner", "builder", "styler", "condensed")


class TestSystemPrompts:
    """Verify all system prompts load and contain expected content."""

    def test_all_system_prompts_load(self):
        for name in TEMPLATE_NAMES:
            text = load_system(name)
            assert len(text) > 100, f"{name}_system.j2 is too short"

    def test_planner_system_content(self):
        text = load_system("planner")
        assert "website architect" in text.lower()
        assert "SectionType" in text

    def test_builder_system_content(self):
        text = load_system("builder")
        assert "YAML builder" in text
        assert "Component Specs" in text

    def test_styler_system_content(self):
        text = load_system("styler")
        assert "visual web designer" in text
        assert "dark_section" in text

    def test_condensed_system_content(self):
        text = load_system("condensed")
        assert "SwiftSites" in text
        assert "VALID COMPONENTS" in text


class TestPlannerUserTemplate:
    def test_renders_with_chunks_and_icons(self):
        result = render_user("planner",
            outline_chunks=[
                {"source_file": "test.yaml", "content": "example outline content"},
                {"source_file": "test2.yaml", "content": "another outline"},
            ],
            icon_names=["star", "heart", "zap"],
            query="build a restaurant website",
        )
        assert "[Outline]" in result
        assert "--- Reference: test.yaml ---" in result
        assert "example outline content" in result
        assert "[Available Icons]" in result
        assert "star, heart, zap" in result
        assert "[User Request]" in result
        assert "build a restaurant website" in result

    def test_renders_without_icons(self):
        result = render_user("planner",
            outline_chunks=[{"source_file": "t.yaml", "content": "content"}],
            icon_names=[],
            query="test query",
        )
        assert "[Available Icons]" not in result
        assert "[User Request]" in result


class TestBuilderUserTemplate:
    def test_renders_full(self):
        result = render_user("builder",
            section_type="hero",
            description="A bold hero section",
            suggested=["layout-row", "heading", "button"],
            comp_specs="layout-row:\n  layout:\n    wrap: wrap",
            ranked_chunks=[
                {"source_file": "hero_example.yaml", "content": "- name: layout-row"},
            ],
            theme_str="Colors: primary='#1a1a1a' (*color-primary)",
            style_notes="Use bold typography with generous whitespace",
            image_context="1. https://example.com/hero.jpg — \"Hero image\" [landscape]",
            icons=["star", "rocket"],
        )
        assert "[Section to Build]" in result
        assert "Type: hero" in result
        assert "layout-row, heading, button" in result
        assert "[Component Specs" in result
        assert "[Reference Example Templates" in result
        assert "--- Example Section: hero_example.yaml ---" in result
        assert "[Theme]" in result
        assert "[Style Direction" in result
        assert "[Images" in result
        assert "Available icons (2 total" in result
        assert "star, rocket" in result

    def test_renders_without_optional_blocks(self):
        result = render_user("builder",
            section_type="faq",
            description="FAQ section",
            suggested=["accordion"],
            comp_specs="accordion:\n  items: []",
            ranked_chunks=[],
            theme_str="Colors: ...",
            style_notes="",
            image_context="",
            icons=[],
        )
        # Style Direction heading should not appear (empty style_notes)
        assert "## [Style Direction" not in result
        # Images heading should not appear (empty image_context)
        assert "## [Images" not in result
        assert "Available icons" not in result


class TestStylerUserTemplate:
    def test_renders_with_images(self):
        result = render_user("styler",
            style_context="Modern Minimalist: clean lines, whitespace",
            selected_images=[
                {"url": "https://example.com/office.jpg", "altText": "Office workspace", "orientation": "landscape", "photographer": "John"},
                {"url": "https://example.com/team.jpg", "altText": "Team meeting", "orientation": "square", "photographer": ""},
            ],
            section_summary=["## Hero\n- Bold headline with CTA", "## Features\n- 3-column grid"],
            section_count=2,
        )
        assert "[Style Reference]" in result
        assert "Modern Minimalist" in result
        assert "[Available Images — assign ALL 2 images" in result
        assert '1. https://example.com/office.jpg — "Office workspace" [landscape] (Photo by John)' in result
        assert '2. https://example.com/team.jpg — "Team meeting" [square]' in result
        assert "[Outline to Design]" in result
        assert "2-section page" in result

    def test_renders_without_images(self):
        result = render_user("styler",
            style_context="",
            selected_images=[],
            section_summary=["## Hero\n- content"],
            section_count=1,
        )
        assert "[Available Images" not in result
        assert "[Style Reference]" not in result
        assert "[Outline to Design]" in result


class TestCondensedUserTemplate:
    def test_renders_full(self):
        result = render_user("condensed",
            comp_specs="heading:\n  text: str",
            valid_tokens="size: xs, sm, md, lg, xl",
            context_block="--- Example from: hero.yaml ---\ncontent here",
            current_yaml="- name: site\n  components: []",
            selected_component="heading",
            message="Change the heading color to red",
        )
        assert "[Component Specifications" in result
        assert "[Valid Tokens]" in result
        assert "[Reference Examples]" in result
        assert "[Current YAML]" in result
        assert "[Selected Component]" in result
        assert "[User Request]" in result

    def test_renders_minimal(self):
        result = render_user("condensed",
            comp_specs="",
            valid_tokens="size: xs, sm, md",
            context_block="",
            current_yaml=None,
            selected_component=None,
            message="Create a hero section",
        )
        assert "[Component Specifications" not in result
        assert "[Reference Examples]" not in result
        assert "[Current YAML]" not in result
        assert "[Selected Component]" not in result
        assert "[User Request]" in result
        assert "Create a hero section" in result
