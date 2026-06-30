"""Tests for site composition shared blocks."""
import json
from unittest.mock import patch

import pytest
import yaml

from extensions import COMPONENT_DEFAULTS, TOKENS, db
from models import (
    Brand, Organization, SectionItem, Site, SitePage, SiteSharedBlock,
    PageSharedBlockOverride, SiteVersionSharedBlock,
)
from site_composer import compose_page_yaml
from renderer import render_yaml_structure


@pytest.fixture
def composition_app(tmp_path):
    db_uri = 'sqlite:///' + str(tmp_path / 'composition.db')
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    yield app


@pytest.fixture
def composition_client(composition_app):
    return composition_app.test_client()


@pytest.fixture
def composition_site(composition_app):
    with composition_app.app_context():
        org = Organization.query.filter_by(slug='default').first()
        site = Site(
            org_id=org.id,
            name='Composed Site',
            slug='composed-site',
            theme=json.dumps({
                'fonts': {
                    'heading': "'Inter', sans-serif",
                    'content': "'Inter', sans-serif",
                },
                'colors': {
                    'primary': '#111827',
                    'text': '#374151',
                    'secondary': '#6b7280',
                    'accent': '#6366f1',
                    'background': '#ffffff',
                },
            }),
        )
        db.session.add(site)
        db.session.flush()

        page = SitePage(
            site_id=site.id,
            slug='home',
            title='Home',
            yaml_content='- name: site\n  components: []\n',
            body_yaml_content="""\
- name: heading
  properties:
    text: Page Headline
""",
            sort_order=0,
            is_homepage=True,
        )
        db.session.add(page)

        header = SiteSharedBlock(
            site_id=site.id,
            key='header',
            label='Header',
            yaml_content="""\
- name: titlebar
  properties:
    branding:
      title: Shared Brand
""",
            sort_order=0,
        )
        footer = SiteSharedBlock(
            site_id=site.id,
            key='footer',
            label='Footer',
            yaml_content="""\
- name: paragraph
  properties:
    text: Shared Footer
""",
            sort_order=10,
        )
        db.session.add_all([header, footer])
        db.session.commit()
        return site.id, page.id


def test_compose_page_yaml_includes_shared_blocks(composition_app, composition_site):
    site_id, page_id = composition_site
    with composition_app.app_context():
        site = Site.query.get(site_id)
        page = SitePage.query.get(page_id)
        composed = compose_page_yaml(site, page)

    site_node = composed[0]
    page_node = site_node['components'][0]
    assert site_node['name'] == 'site'
    assert site_node['header'][0]['name'] == 'titlebar'
    assert site_node['footer'][0]['properties']['text'] == 'Shared Footer'
    assert page_node['components'][0]['properties']['text'] == 'Page Headline'


def test_hidden_override_omits_shared_block(composition_app, composition_site):
    site_id, page_id = composition_site
    with composition_app.app_context():
        override = PageSharedBlockOverride(
            page_id=page_id,
            block_key='footer',
            mode='hidden',
        )
        db.session.add(override)
        db.session.commit()

        site = Site.query.get(site_id)
        page = SitePage.query.get(page_id)
        composed = compose_page_yaml(site, page)

    assert 'footer' not in composed[0]
    assert composed[0]['header'][0]['name'] == 'titlebar'


def test_custom_override_replaces_shared_block(composition_app, composition_site):
    site_id, page_id = composition_site
    with composition_app.app_context():
        override = PageSharedBlockOverride(
            page_id=page_id,
            block_key='header',
            mode='custom',
            custom_yaml_content="""\
- name: heading
  properties:
    text: Custom Header
""",
        )
        db.session.add(override)
        db.session.commit()

        site = Site.query.get(site_id)
        page = SitePage.query.get(page_id)
        composed = compose_page_yaml(site, page)

    assert composed[0]['header'][0]['name'] == 'heading'
    assert composed[0]['header'][0]['properties']['text'] == 'Custom Header'


def test_append_section_yaml_to_page_body(composition_app, composition_client, composition_site):
    site_id, page_id = composition_site
    with composition_app.app_context():
        org = Organization.query.filter_by(slug='default').first()
        section = SectionItem(
            org_id=org.id,
            name='CTA',
            section_type='cta',
            yaml_content="""\
- name: layout-row
  components:
    - name: layout-column
      components:
        - name: heading
          properties:
            text: Generated CTA
""",
        )
        db.session.add(section)
        db.session.commit()
        section_id = section.id

    res = composition_client.post(
        f'/api/sites/{site_id}/pages/{page_id}/sections',
        json={'section_id': section_id},
    )
    assert res.status_code == 200
    assert 'Generated CTA' in res.get_json()['body_yaml_content']

    with composition_app.app_context():
        site = Site.query.get(site_id)
        page = SitePage.query.get(page_id)
        composed = compose_page_yaml(site, page)

    body = composed[0]['components'][0]['components']
    assert body[0]['properties']['text'] == 'Page Headline'
    assert body[1]['name'] == 'layout-row'


def test_publish_uses_composer_and_snapshots_shared_blocks(composition_app, composition_client, composition_site):
    site_id, _page_id = composition_site
    res = composition_client.post(f'/api/sites/{site_id}/publish')
    assert res.status_code == 200

    with composition_app.app_context():
        from models import PublishedPage, SiteVersion

        published = PublishedPage.query.filter_by(site_id=site_id, slug='home').first()
        assert published is not None
        assert 'Shared Brand' in published.rendered_html
        assert 'Page Headline' in published.rendered_html
        assert 'Shared Footer' in published.rendered_html

        version = SiteVersion.query.filter_by(site_id=site_id, version_number=1).first()
        assert version is not None
        snapshot_count = SiteVersionSharedBlock.query.filter_by(version_id=version.id).count()
        assert snapshot_count == 2


def test_brand_site_shell_creates_renderer_valid_site(composition_app, composition_client):
    with composition_app.app_context():
        org = Organization.query.filter_by(slug='default').first()
        brand = Brand(
            org_id=org.id,
            name='Acme Studio',
            slug='acme-studio',
            tagline='Design systems that ship.',
            color_primary='#101010',
            color_text='#202020',
            color_secondary='#606060',
            color_accent='#ff5500',
            color_background='#ffffff',
            font_heading='Inter',
            font_body='Inter',
        )
        db.session.add(brand)
        db.session.commit()
        brand_id = brand.id

    res = composition_client.post(f'/api/brands/{brand_id}/site', json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data['brand_id'] == brand_id
    assert data['homepage']['body_yaml_content'].lstrip().startswith('- name: layout-row')
    assert any(block['key'] == 'header' for block in data['shared_blocks'])
    assert any(block['key'] == 'footer' for block in data['shared_blocks'])

    composed = yaml.safe_load(data['composed_yaml'])
    assert composed[0]['name'] == 'site'
    assert composed[0]['properties']['theme']['colors']['primary'] == '#101010'
    assert composed[0]['components'][0]['name'] == 'page'
    with composition_app.app_context():
        assert render_yaml_structure(composed, TOKENS, COMPONENT_DEFAULTS)

    with composition_app.app_context():
        sites = Site.query.filter_by(brand_id=brand_id).all()
        assert len(sites) == 1
        assert sites[0].theme


def test_brand_site_shell_regenerate_preserves_page_body(composition_app, composition_client):
    with composition_app.app_context():
        org = Organization.query.filter_by(slug='default').first()
        brand = Brand(
            org_id=org.id,
            name='Acme Studio',
            slug='acme-studio',
            tagline='Original tagline',
            color_primary='#111111',
        )
        db.session.add(brand)
        db.session.commit()
        brand_id = brand.id

    create = composition_client.post(f'/api/brands/{brand_id}/site', json={})
    assert create.status_code == 200

    with composition_app.app_context():
        site = Site.query.filter_by(brand_id=brand_id).first()
        page = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
        page.body_yaml_content = """\
- name: heading
  properties:
    text: Keep this body
"""
        brand = Brand.query.get(brand_id)
        brand.tagline = 'Updated tagline'
        brand.color_primary = '#222222'
        db.session.commit()
        site_id = site.id

    refresh = composition_client.post(f'/api/brands/{brand_id}/site', json={'regenerate': True})
    assert refresh.status_code == 200
    data = refresh.get_json()
    assert data['id'] == site_id

    with composition_app.app_context():
        site = Site.query.get(site_id)
        page = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
        assert 'Keep this body' in page.body_yaml_content
        composed = compose_page_yaml(site, page)
        assert composed[0]['properties']['theme']['colors']['primary'] == '#222222'
        assert render_yaml_structure(composed, TOKENS, COMPONENT_DEFAULTS)
