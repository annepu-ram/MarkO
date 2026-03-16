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


class TestSiteRendering:
    """Tests for site rendering."""

    def test_render_page_without_site_wrapper(self, app):
        """Page-only YAML (no site wrapper) still renders correctly."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: page
  properties:
    appearance:
      background:
        color: '#ffffff'
        transparency: 100
  components:
    - name: heading
      properties:
        text: Regression Test
        typography:
          size: lg
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'class="page"' in html
            assert 'Regression Test' in html
            assert 'comp_0' in html
            assert 'comp_0_components_0' in html
            # No site-wrapper div should appear
            assert 'site-wrapper' not in html

    def test_site_without_theme_no_wrapper(self, app):
        """Site with no theme fonts produces no wrapper div."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: heading
          properties:
            text: No Theme
            typography:
              size: lg
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'No Theme' in html
            assert 'class="page"' in html
            assert 'site-wrapper' not in html

    def test_existing_fixture_unchanged(self, app, sample_page_structure):
        """Existing sample_page.yaml fixture renders exactly as before."""
        with app.app_context():
            html = render_yaml_structure(sample_page_structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'Hello World' in html
            assert 'comp_0' in html
            assert 'comp_0_components_2' in html
            assert 'comp_0_components_2_components_0' in html
            assert 'comp_0_components_2_components_1' in html
            assert 'site-wrapper' not in html


class TestSiteTheme:
    """Tests for site-level theme (site.properties.theme) with font CSS vars."""

    def test_site_theme_fonts_on_wrapper(self, app):
        """Site-level theme fonts produce CSS vars on .site-wrapper."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  properties:
    theme:
      fonts:
        heading: "'Playfair Display', serif"
        content: "'Inter', sans-serif"
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
      components:
        - name: heading
          properties:
            text: Hello
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'site-wrapper' in html
            assert '--font-heading' in html
            assert '--font-content' in html
            assert 'Playfair Display' in html

    def test_site_theme_gets_wrapper(self, app):
        """Site with theme fonts gets .site-wrapper for font cascade."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  properties:
    theme:
      fonts:
        heading: "'Roboto', sans-serif"
        content: "'Roboto', sans-serif"
  components:
    - name: page
      components:
        - name: paragraph
          properties:
            text: Content
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'site-wrapper' in html
            assert '--font-heading' in html

    def test_page_level_theme_fallback(self, app):
        """Old YAML with page-level theme still renders fonts on wrapper (via fallback)."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  components:
    - name: page
      properties:
        theme:
          fonts:
            heading: "'Merriweather', serif"
            content: "'Open Sans', sans-serif"
        appearance:
          background:
            color: '#ffffff'
      components:
        - name: paragraph
          properties:
            text: Body
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'site-wrapper' in html
            assert '--font-heading' in html
            assert 'Merriweather' in html

    def test_no_theme_no_header_no_wrapper(self, app):
        """Bare site with no theme, no header/footer = no .site-wrapper div."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  components:
    - name: page
      components:
        - name: paragraph
          properties:
            text: Just text
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'site-wrapper' not in html
            assert 'Just text' in html

    def test_site_theme_with_page_components(self, app):
        """Site theme renders wrapper with fonts and page content."""
        with app.app_context():
            import yaml
            structure = yaml.safe_load("""
- name: site
  properties:
    theme:
      fonts:
        heading: "'Lato', sans-serif"
        content: "'Lato', sans-serif"
  components:
    - name: page
      components:
        - name: heading
          properties:
            text: Page Title
        - name: paragraph
          properties:
            text: Page Body
""")
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert 'site-wrapper' in html
            assert '--font-heading' in html
            assert 'Lato' in html
            assert 'Page Title' in html
            assert 'Page Body' in html
