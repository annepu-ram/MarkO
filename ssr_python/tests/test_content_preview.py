"""Tests for content preview + brand theme propagation."""
import pytest
from unittest.mock import patch

from campaign.theme import brand_to_theme, merge_brand_theme
from campaign.content_preview import content_item_to_components, build_preview_structure
from campaign.content_type_catalog import slots_from_content


# --- brand_to_theme (pure) ----------------------------------------------------

class _FakeBrand:
    def __init__(self, **kw):
        self.color_primary = kw.get('color_primary')
        self.color_secondary = kw.get('color_secondary')
        self.color_text = kw.get('color_text')
        self.color_accent = kw.get('color_accent')
        self.color_background = kw.get('color_background')
        self.font_heading = kw.get('font_heading')
        self.font_body = kw.get('font_body')


class TestBrandToTheme:
    def test_none_brand_returns_defaults(self):
        theme = brand_to_theme(None)
        assert set(theme['colors']) == {'primary', 'text', 'secondary', 'accent', 'background'}
        assert theme['fonts']['heading'] and theme['fonts']['content']

    def test_five_colors_mapped(self):
        brand = _FakeBrand(color_primary='#111', color_secondary='#222',
                           color_text='#333', color_accent='#444', color_background='#555')
        c = brand_to_theme(brand)['colors']
        assert c == {'primary': '#111', 'secondary': '#222', 'text': '#333',
                     'accent': '#444', 'background': '#555'}

    def test_font_body_maps_to_content(self):
        brand = _FakeBrand(font_heading='Poppins', font_body='Inter')
        fonts = brand_to_theme(brand)['fonts']
        assert fonts['heading'] == 'Poppins'
        assert fonts['content'] == 'Inter'  # body -> content

    def test_partial_brand_falls_back(self):
        brand = _FakeBrand(color_accent='#e94560')
        c = brand_to_theme(brand)['colors']
        assert c['accent'] == '#e94560'
        assert c['primary'] == '#111827'  # default kept

    def test_merge_brand_theme_overlays(self):
        existing = {'colors': {'primary': '#old', 'extra': '#keep'}, 'fonts': {}}
        brand = _FakeBrand(color_primary='#new', color_text='#txt')
        merged = merge_brand_theme(existing, brand)
        assert merged['colors']['primary'] == '#new'   # brand wins
        assert merged['colors']['extra'] == '#keep'    # preserved
        assert merged['colors']['text'] == '#txt'

    def test_merge_none_brand_passthrough(self):
        existing = {'colors': {'primary': '#x'}}
        assert merge_brand_theme(existing, None) == existing


# --- content_item_to_components (pure) ----------------------------------------

class TestContentToComponents:
    def test_headline_to_h1(self):
        comps = content_item_to_components({'category': 'headline', 'content': 'Big Promise'})
        assert comps[0]['name'] == 'heading'
        assert comps[0]['properties']['level'] == 1
        assert comps[0]['properties']['text'] == 'Big Promise'

    def test_cta_to_button(self):
        comps = content_item_to_components({
            'category': 'cta', 'content': 'Book Now',
            'slots': {'link': '/book'},
        })
        assert comps[0]['name'] == 'button'
        assert comps[0]['properties']['action']['href'] == '/book'

    def test_faq_to_accordion_items_sibling(self):
        comps = content_item_to_components({
            'category': 'faq', 'content': '',
            'slots': {'question': 'Is it free?', 'answer': 'Yes.'},
        })
        acc = comps[0]
        assert acc['name'] == 'accordion'
        # items must be a component-level sibling of properties (renderer contract)
        assert 'items' in acc and 'items' not in acc['properties']
        assert acc['items'][0]['title'] == 'Is it free?'

    def test_offer_includes_code_badge(self):
        comps = content_item_to_components({
            'category': 'offer', 'title': 'Spring Sale', 'content': '40% off',
            'slots': {'code': 'SPRING40'},
        })
        names = [c['name'] for c in comps]
        assert 'badge' in names

    def test_fallback_paragraph(self):
        comps = content_item_to_components({'category': 'boilerplate', 'content': 'Legal text'})
        assert any(c['name'] == 'paragraph' for c in comps)

    def test_build_preview_structure_shape(self):
        theme = brand_to_theme(_FakeBrand(color_background='#fafafa'))
        struct = build_preview_structure({'category': 'headline', 'content': 'Hi'}, theme)
        assert struct[0]['name'] == 'site'
        assert struct[0]['properties']['theme']['colors']['background'] == '#fafafa'
        page = struct[0]['components'][0]
        assert page['name'] == 'page'
        # no leftover bookkeeping key
        section = page['components'][0]
        assert 'section_id' not in section


# --- endpoint + render round-trip (needs app) ---------------------------------

@pytest.fixture
def preview_app(tmp_path):
    db_uri = 'sqlite:///' + str(tmp_path / 'test_preview.db')
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(preview_app):
    return preview_app.test_client()


class TestPreviewEndpoint:
    def _brand(self, client):
        return client.post('/api/brands', json={
            'name': 'Glow', 'is_default': True,
            'colors': {'primary': '#1a1a2e', 'text': '#cc1166', 'secondary': '#777',
                       'accent': '#e94560', 'background': '#fafafa'},
            'fonts': {'heading': 'Poppins', 'body': 'Mulish'},
        }).get_json()

    def test_headline_preview_renders(self, client):
        brand = self._brand(client)
        item = client.post('/api/content', json={
            'category': 'headline',
            'slots': slots_from_content('headline', 'Transform Your Body'),
            'brand_id': brand['id'],
        }).get_json()
        res = client.get(f'/api/content/{item["id"]}/preview')
        assert res.status_code == 200
        assert 'text/html' in res.headers['Content-Type']
        html = res.get_data(as_text=True)
        assert 'Transform Your Body' in html
        assert 'Poppins' in html            # heading font propagated
        assert '#fafafa' in html            # background propagated

    def test_paragraph_preview_uses_text_color(self, client):
        brand = self._brand(client)
        item = client.post('/api/content', json={
            'category': 'about',
            'title': 'Our Story',
            'slots': slots_from_content('about', 'We make fitness simple.'),
            'brand_id': brand['id'],
        }).get_json()
        html = client.get(f'/api/content/{item["id"]}/preview').get_data(as_text=True)
        assert 'We make fitness simple.' in html
        assert '#cc1166' in html            # $color-text now resolves from theme

    def test_preview_without_brand_uses_defaults(self, client):
        item = client.post('/api/content', json={
            'category': 'headline',
            'slots': slots_from_content('headline', 'No Brand Here'),
        }).get_json()
        # delete the auto-created default brand link by leaving brand_id null;
        # org default brand may still apply — either way it must render.
        res = client.get(f'/api/content/{item["id"]}/preview')
        assert res.status_code == 200
        assert 'No Brand Here' in res.get_data(as_text=True)

    def test_unknown_item_404(self, client):
        assert client.get('/api/content/does-not-exist/preview').status_code == 404


# --- renderer $color-text resolution ------------------------------------------

class TestRendererTextColor:
    def test_color_text_resolves_from_theme(self, preview_app):
        with preview_app.app_context():
            from extensions import TOKENS, COMPONENT_DEFAULTS
            from renderer import render_yaml_structure
            structure = [{
                'name': 'site',
                'properties': {'theme': {'colors': {'text': '#abcdef'}}},
                'components': [{
                    'name': 'page', 'slug': 'p', 'title': 't',
                    'components': [{'name': 'paragraph', 'properties': {'text': 'Body copy'}}],
                }],
            }]
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
            assert '#abcdef' in html
