"""Tests for ssr_python/rag/agent/yaml_fixer.py — YAML validation and auto-fix pipeline."""
import pytest
import yaml as pyyaml

from rag.agent.yaml_fixer import (
    auto_fix_yaml,
    fix_component_names,
    fix_nesting,
    fix_structure,
    fix_token_values,
    find_invalid_components,
    find_nesting_errors,
    find_structural_errors,
    find_token_errors,
    quick_validate,
    VALID_COMPONENTS,
    VALID_SPACING,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Detection tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestFindInvalidComponents:
    def test_valid_components(self):
        doc = [{"name": "layout-row", "components": [{"name": "heading"}]}]
        assert find_invalid_components(doc) == set()

    def test_invalid_name(self):
        doc = [{"name": "hero-banner"}]
        assert "hero-banner" in find_invalid_components(doc)

    def test_nested_invalid(self):
        doc = [{"name": "layout-row", "components": [{"name": "invalid-comp"}]}]
        assert "invalid-comp" in find_invalid_components(doc)


class TestFindStructuralErrors:
    def test_children_instead_of_components(self):
        doc = [{"name": "layout-row", "children": [{"name": "heading"}]}]
        errors = find_structural_errors(doc)
        assert any("children" in e for e in errors)

    def test_inline_format(self):
        doc = [{"layout-row": {"gap": "md"}}]
        errors = find_structural_errors(doc)
        assert any("inline format" in e for e in errors)

    def test_array_props_in_properties(self):
        doc = [{"name": "tabs", "properties": {"tabs": [{"label": "Tab 1"}]}}]
        errors = find_structural_errors(doc)
        assert any("tabs" in e and "inside properties" in e for e in errors)

    def test_valid_structure(self):
        doc = [{"name": "layout-row", "components": [{"name": "heading"}]}]
        assert find_structural_errors(doc) == []


class TestFindTokenErrors:
    def test_invalid_width_mode(self):
        doc = [{"name": "layout-column", "properties": {"layout": {"widthMode": "40"}}}]
        errors = find_token_errors(doc)
        assert any("widthMode" in e for e in errors)

    def test_valid_width_mode(self):
        doc = [{"name": "layout-column", "properties": {"layout": {"widthMode": "50"}}}]
        assert find_token_errors(doc) == []

    def test_invalid_spacing(self):
        doc = [{"name": "layout-row", "properties": {"spacing": {"paddingBlock": "large"}}}]
        errors = find_token_errors(doc)
        assert any("paddingBlock" in e for e in errors)

    def test_ticker_width_modes(self):
        doc = [{"name": "ticker", "properties": {"layout": {"widthMode": "280"}}}]
        assert find_token_errors(doc) == []


class TestFindNestingErrors:
    def test_leaf_with_children(self):
        doc = [{"name": "button", "components": [{"name": "heading"}]}]
        errors = find_nesting_errors(doc)
        assert any("leaf component" in e for e in errors)

    def test_wrong_child_key(self):
        doc = [{"name": "tabs", "components": [{"name": "heading"}]}]
        errors = find_nesting_errors(doc)
        assert any("tabs:" in e for e in errors)

    def test_components_in_properties(self):
        doc = [{"name": "layout-row", "properties": {"components": [{"name": "heading"}]}}]
        errors = find_nesting_errors(doc)
        assert any("inside 'properties:'" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════════
# Fix tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestFixStructure:
    def test_children_to_components(self):
        node = {"name": "layout-row", "children": [{"name": "heading"}]}
        fixed = fix_structure(node)
        assert "components" in fixed
        assert "children" not in fixed

    def test_inline_format(self):
        node = {"layout-row": {"layout": {"gap": "md"}}}
        fixed = fix_structure(node)
        assert fixed["name"] == "layout-row"
        assert "properties" in fixed

    def test_array_props_moved(self):
        node = {"name": "tabs", "properties": {"tabs": [{"label": "Tab 1"}]}}
        fixed = fix_structure(node)
        assert "tabs" in fixed
        assert "tabs" not in fixed.get("properties", {})

    def test_orphaned_properties(self):
        node = {"name": "heading", "typography": {"size": "xl"}}
        fixed = fix_structure(node)
        assert "typography" in fixed["properties"]
        assert "typography" not in {k for k in fixed if k != "properties"}

    def test_container_key_mismatch_row(self):
        node = {"name": "layout-row", "columns": [{"name": "heading"}]}
        fixed = fix_structure(node)
        assert "components" in fixed
        assert "columns" not in fixed

    def test_container_key_mismatch_ticker(self):
        node = {"name": "ticker", "components": [{"name": "heading"}]}
        fixed = fix_structure(node)
        assert "columns" in fixed
        assert "components" not in fixed

    def test_tabs_items_to_tabs(self):
        node = {"name": "tabs", "items": [{"label": "Tab 1"}]}
        fixed = fix_structure(node)
        assert "tabs" in fixed
        assert "items" not in fixed

    def test_carousel_items_to_slides(self):
        node = {"name": "carousel", "items": [{"content": "slide 1"}]}
        fixed = fix_structure(node)
        assert "slides" in fixed
        assert "items" not in fixed

    def test_width_mode_int_to_string(self):
        node = {"name": "layout-column", "properties": {"layout": {"widthMode": 50}}}
        fixed = fix_structure(node)
        assert fixed["properties"]["layout"]["widthMode"] == "50"

    def test_icon_name_as_component(self):
        node = {"name": "arrow-right"}
        fixed = fix_structure(node)
        assert fixed["name"] == "icon"
        assert fixed["properties"]["name"] == "arrow-right"


class TestFixComponentNames:
    def test_alias_row(self):
        node = [{"name": "row", "components": [{"name": "heading"}]}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "layout-row"
        assert len(fixes) == 1

    def test_alias_btn(self):
        node = [{"name": "btn"}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "button"

    def test_alias_slider(self):
        node = [{"name": "slider"}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "carousel"

    def test_alias_img(self):
        node = [{"name": "img"}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "image"

    def test_fuzzy_match(self):
        node = [{"name": "lay-out-row"}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "layout-row"

    def test_valid_name_unchanged(self):
        node = [{"name": "heading"}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["name"] == "heading"
        assert fixes == []

    def test_nested_fix(self):
        node = [{"name": "layout-row", "components": [{"name": "btn"}]}]
        fixes = []
        fix_component_names(node, fixes)
        assert node[0]["components"][0]["name"] == "button"


class TestFixTokenValues:
    def test_width_mode_snap(self):
        node = [{"name": "layout-column", "properties": {"layout": {"widthMode": "40"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["layout"]["widthMode"] == "33"
        assert len(fixes) == 1

    def test_width_mode_alias(self):
        node = [{"name": "layout-column", "properties": {"layout": {"widthMode": "100"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["layout"]["widthMode"] == "stretch"

    def test_spacing_alias_large(self):
        node = [{"name": "layout-row", "properties": {"spacing": {"paddingBlock": "large"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["spacing"]["paddingBlock"] == "lg"

    def test_spacing_alias_small(self):
        node = [{"name": "layout-row", "properties": {"spacing": {"paddingInline": "small"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["spacing"]["paddingInline"] == "sm"

    def test_font_weight_normal(self):
        node = [{"name": "heading", "properties": {"typography": {"weight": "normal"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["typography"]["weight"] == "regular"

    def test_radius_full(self):
        node = [{"name": "button", "properties": {"appearance": {"radius": "full"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["appearance"]["radius"] == "pill"

    def test_valid_token_unchanged(self):
        node = [{"name": "heading", "properties": {"typography": {"size": "xl"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["typography"]["size"] == "xl"
        assert fixes == []

    def test_nested_fix(self):
        node = [{"name": "layout-row", "components": [
            {"name": "layout-column", "properties": {"layout": {"widthMode": "45"}}}
        ]}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["components"][0]["properties"]["layout"]["widthMode"] == "50"

    def test_shadow_alias(self):
        node = [{"name": "layout-row", "properties": {"appearance": {"shadow": "heavy"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["appearance"]["shadow"] == "dramatic"

    # Garbled token tests
    def test_garbled_xxlg(self):
        node = [{"name": "heading", "properties": {"typography": {"size": "xxlg"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["typography"]["size"] == "xl"
        assert len(fixes) == 1

    def test_garbled_xxmd(self):
        node = [{"name": "layout-row", "properties": {"spacing": {"paddingBlock": "xxmd"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["spacing"]["paddingBlock"] == "md"

    def test_garbled_xxsm(self):
        node = [{"name": "layout-row", "properties": {"spacing": {"paddingInline": "xxsm"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["spacing"]["paddingInline"] == "sm"

    def test_garbled_xlg(self):
        node = [{"name": "heading", "properties": {"typography": {"size": "xlg"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["typography"]["size"] == "xl"

    def test_garbled_sml(self):
        node = [{"name": "layout-row", "properties": {"layout": {"gap": "sml"}}}]
        fixes = []
        fix_token_values(node, fixes)
        # "sml" is in TOKEN_ALIASES → "sm"
        assert node[0]["properties"]["layout"]["gap"] == "sm"

    def test_garbled_lrg(self):
        node = [{"name": "layout-row", "properties": {"spacing": {"paddingBlock": "lrg"}}}]
        fixes = []
        fix_token_values(node, fixes)
        assert node[0]["properties"]["spacing"]["paddingBlock"] == "lg"

    def test_garbled_xx40_width(self):
        node = [{"name": "layout-column", "properties": {"layout": {"widthMode": "xx40"}}}]
        fixes = []
        fix_token_values(node, fixes)
        # Should be fixed (either via alias or substring extraction)
        assert node[0]["properties"]["layout"]["widthMode"] in {"xxl", "33", "stretch", "fit", "16", "25", "50", "66", "75", "83"}


class TestFixNesting:
    def test_leaf_children_removed(self):
        node = [{"name": "button", "components": [{"name": "heading"}]}]
        fixes = []
        fix_nesting(node, fixes)
        assert "components" not in node[0]
        assert len(fixes) == 1

    def test_wrong_child_key_fixed(self):
        node = [{"name": "tabs", "components": [{"label": "Tab 1"}]}]
        fixes = []
        fix_nesting(node, fixes)
        assert "tabs" in node[0]
        assert "components" not in node[0]

    def test_components_moved_from_properties(self):
        node = [{"name": "layout-row", "properties": {"components": [{"name": "heading"}]}}]
        fixes = []
        fix_nesting(node, fixes)
        assert "components" in node[0]
        assert "components" not in node[0]["properties"]

    def test_valid_nesting_unchanged(self):
        node = [{"name": "layout-row", "components": [{"name": "heading"}]}]
        fixes = []
        fix_nesting(node, fixes)
        assert "components" in node[0]
        assert fixes == []


# ═══════════════════════════════════════════════════════════════════════════════
# Auto-fix pipeline tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoFixYaml:
    def test_valid_yaml_no_fixes(self):
        yaml_str = pyyaml.dump([{"name": "heading", "properties": {"typography": {"size": "xl"}}}])
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert fixes == []

    def test_fixes_invalid_width(self):
        yaml_str = pyyaml.dump([
            {"name": "layout-row", "components": [
                {"name": "layout-column", "properties": {"layout": {"widthMode": "40"}}}
            ]}
        ])
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert len(fixes) > 0
        parsed = pyyaml.safe_load(fixed)
        assert parsed[0]["components"][0]["properties"]["layout"]["widthMode"] == "33"

    def test_fixes_component_name(self):
        yaml_str = pyyaml.dump([{"name": "btn", "properties": {"label": "Click"}}])
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert len(fixes) > 0
        parsed = pyyaml.safe_load(fixed)
        assert parsed[0]["name"] == "button"

    def test_fixes_structural_children(self):
        yaml_str = pyyaml.dump([{"name": "layout-row", "children": [{"name": "heading"}]}])
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert len(fixes) > 0
        parsed = pyyaml.safe_load(fixed)
        assert "components" in parsed[0]
        assert "children" not in parsed[0]

    def test_round_trip_passes_validation(self):
        """Fixed YAML should pass quick_validate when wrapped in a response."""
        yaml_str = pyyaml.dump([
            {"name": "layout-row", "children": [
                {"name": "layout-column", "properties": {"layout": {"widthMode": "40"}}},
            ]}
        ])
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert len(fixes) > 0
        response = f"<!-- ACTION: create -->\nHere is the section:\n\n```yaml\n{fixed}```"
        assert quick_validate(response) is None

    def test_unparseable_yaml_returns_original(self):
        yaml_str = "- name: heading\n  properties:\n    invalid: [unclosed"
        fixed, fixes = auto_fix_yaml(yaml_str)
        assert fixed == yaml_str
        assert fixes == []


# ═══════════════════════════════════════════════════════════════════════════════
# quick_validate tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuickValidate:
    def test_valid_response(self):
        response = "```yaml\n- name: heading\n  properties:\n    typography:\n      size: xl\n```"
        assert quick_validate(response) is None

    def test_invalid_component(self):
        response = "```yaml\n- name: invalid-comp\n```"
        error = quick_validate(response)
        assert error is not None
        assert "invalid-comp" in error

    def test_explain_response_skipped(self):
        response = "This is an explanation of how components work."
        assert quick_validate(response) is None

    def test_parse_error(self):
        response = "```yaml\n- name: heading\n  invalid: [unclosed\n```"
        error = quick_validate(response)
        assert error is not None
        assert "parse error" in error.lower()

    def test_structural_error(self):
        response = "```yaml\n- name: layout-row\n  children:\n  - name: heading\n```"
        error = quick_validate(response)
        assert error is not None
        assert "Structural" in error

    def test_nesting_error(self):
        response = "```yaml\n- name: button\n  components:\n  - name: heading\n```"
        error = quick_validate(response)
        assert error is not None
        assert "Nesting" in error
