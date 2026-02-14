"""Tests for the core rendering engine."""
import pytest
from renderer import render_yaml_structure, deep_merge, merge_component_with_defaults
from extensions import TOKENS, COMPONENT_DEFAULTS


class TestDeepMerge:
    def test_simple_merge(self):
        base = {'a': 1, 'b': 2}
        override = {'b': 3, 'c': 4}
        result = deep_merge(base, override)
        assert result == {'a': 1, 'b': 3, 'c': 4}

    def test_nested_merge(self):
        base = {'a': {'x': 1, 'y': 2}}
        override = {'a': {'y': 3, 'z': 4}}
        result = deep_merge(base, override)
        assert result == {'a': {'x': 1, 'y': 3, 'z': 4}}

    def test_none_override_preserves_base(self):
        base = {'a': 1}
        result = deep_merge(base, None)
        assert result == {'a': 1}

    def test_empty_string_override_preserves_base(self):
        base = {'a': 1}
        result = deep_merge(base, '')
        assert result == {'a': 1}

    def test_array_replacement(self):
        base = {'items': [1, 2, 3]}
        override = {'items': [4, 5]}
        result = deep_merge(base, override)
        assert result == {'items': [4, 5]}


class TestRenderYamlStructure:
    def test_render_simple_page(self, app, sample_page_yaml):
        """POST /render with page+heading YAML returns HTML with expected tags."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load(sample_page_yaml)
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'Hello World' in html
            assert 'data-component-id' in html
            assert 'class="page"' in html

    def test_render_nested_components(self, app, sample_page_yaml):
        """Nested layout-row with columns has correct component IDs."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load(sample_page_yaml)
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            # Page component
            assert 'comp_0' in html
            # Layout row
            assert 'comp_0_components_2' in html
            # Columns inside row
            assert 'comp_0_components_2_components_0' in html
            assert 'comp_0_components_2_components_1' in html

    def test_render_invalid_structure(self, app):
        """Invalid YAML structure returns error comment."""
        with app.app_context():
            result = render_yaml_structure(None, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'Invalid YAML' in result

    def test_render_empty_list(self, app):
        """Empty list returns error comment."""
        with app.app_context():
            result = render_yaml_structure([], tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'Invalid YAML' in result

    def test_merge_with_defaults(self, app):
        """Component without properties gets defaults applied."""
        with app.app_context():
            component = {'name': 'heading', 'properties': {'text': 'Test'}}
            merged = merge_component_with_defaults(component, COMPONENT_DEFAULTS, TOKENS)
            # Should have defaults merged in (typography, spacing, etc.)
            assert 'typography' in merged['properties']
            assert 'text' in merged['properties']
            assert merged['properties']['text'] == 'Test'
