"""Tests for site settings API (SEO, branding, social)."""
import pytest
from unittest.mock import patch
from extensions import db
from models import Site, SitePage


@pytest.fixture
def settings_app(tmp_path):
    """Create app with a fresh temporary database for settings tests."""
    db_path = str(tmp_path / 'test_settings.db')
    db_uri = 'sqlite:///' + db_path

    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True

    yield app


@pytest.fixture
def client(settings_app):
    return settings_app.test_client()


@pytest.fixture
def sample_site(settings_app):
    """Create a sample site with one homepage. Returns site ID."""
    with settings_app.app_context():
        from models import Organization
        org = Organization.query.filter_by(slug='default').first()
        site = Site(org_id=org.id, name='Test Site', slug='test-settings')
        db.session.add(site)
        db.session.flush()
        page = SitePage(
            site_id=site.id, slug='home', title='Home',
            yaml_content='- name: page\n  components: []\n',
            sort_order=0, is_homepage=True,
        )
        db.session.add(page)
        db.session.commit()
        return site.id


class TestSiteSettings:

    def test_get_settings_returns_defaults(self, client, sample_site):
        """GET /api/sites/<id>/settings returns default settings for a new site."""
        resp = client.get(f'/api/sites/{sample_site}/settings')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'seo' in data
        assert 'branding' in data
        assert 'social' in data
        assert data['seo']['titleTemplate'] == '{pageTitle} | {siteName}'
        assert data['seo']['metaDescription'] == ''
        assert data['branding']['faviconUrl'] == ''
        assert data['social']['twitterHandle'] == ''

    def test_update_settings_persists(self, client, sample_site):
        """PUT /api/sites/<id>/settings persists and round-trips."""
        resp = client.put(f'/api/sites/{sample_site}/settings', json={
            'seo': {'metaDescription': 'A great test site'},
        })
        assert resp.status_code == 200
        assert resp.get_json()['ok'] is True

        # Verify persistence
        resp = client.get(f'/api/sites/{sample_site}/settings')
        data = resp.get_json()
        assert data['seo']['metaDescription'] == 'A great test site'
        # Other defaults preserved
        assert data['seo']['titleTemplate'] == '{pageTitle} | {siteName}'

    def test_partial_update_preserves_other_categories(self, client, sample_site):
        """Updating seo doesn't wipe branding or social."""
        # Set branding first
        client.put(f'/api/sites/{sample_site}/settings', json={
            'branding': {'siteName': 'My Brand'},
        })

        # Now update seo only
        client.put(f'/api/sites/{sample_site}/settings', json={
            'seo': {'ogTitle': 'Custom OG Title'},
        })

        # Verify branding is preserved
        resp = client.get(f'/api/sites/{sample_site}/settings')
        data = resp.get_json()
        assert data['branding']['siteName'] == 'My Brand'
        assert data['seo']['ogTitle'] == 'Custom OG Title'

    def test_rejects_unknown_category(self, client, sample_site):
        """PUT rejects unknown settings categories."""
        resp = client.put(f'/api/sites/{sample_site}/settings', json={
            'analytics': {'trackingId': 'UA-123'},
        })
        assert resp.status_code == 400
        assert 'Unknown settings category' in resp.get_json()['error']

    def test_rejects_unknown_key(self, client, sample_site):
        """PUT rejects unknown keys within a category."""
        resp = client.put(f'/api/sites/{sample_site}/settings', json={
            'seo': {'robots': 'noindex'},
        })
        assert resp.status_code == 400
        assert 'Unknown setting' in resp.get_json()['error']

    def test_rejects_non_string_value(self, client, sample_site):
        """PUT rejects non-string values."""
        resp = client.put(f'/api/sites/{sample_site}/settings', json={
            'seo': {'metaDescription': 42},
        })
        assert resp.status_code == 400
        assert 'must be a string' in resp.get_json()['error']

    def test_get_site_includes_settings(self, client, sample_site):
        """GET /api/sites/<id> includes settings in response."""
        # Set a setting first
        client.put(f'/api/sites/{sample_site}/settings', json={
            'branding': {'faviconUrl': '/uploads/icon.webp'},
        })

        resp = client.get(f'/api/sites/{sample_site}')
        data = resp.get_json()
        assert 'settings' in data
        assert data['settings']['branding']['faviconUrl'] == '/uploads/icon.webp'

    def test_list_sites_includes_has_settings(self, client, sample_site):
        """GET /api/sites includes has_settings flag."""
        resp = client.get('/api/sites')
        data = resp.get_json()
        site = next(s for s in data if s['id'] == sample_site)
        assert site['has_settings'] is False

        # Set a setting
        client.put(f'/api/sites/{sample_site}/settings', json={
            'seo': {'metaDescription': 'Test'},
        })

        resp = client.get('/api/sites')
        data = resp.get_json()
        site = next(s for s in data if s['id'] == sample_site)
        assert site['has_settings'] is True

    def test_settings_404_for_nonexistent_site(self, client):
        """Settings endpoints return 404 for nonexistent site."""
        resp = client.get('/api/sites/nonexistent-id/settings')
        assert resp.status_code == 404

        resp = client.put('/api/sites/nonexistent-id/settings', json={
            'seo': {'metaDescription': 'test'},
        })
        assert resp.status_code == 404

    def test_put_requires_json_body(self, client, sample_site):
        """PUT without JSON body returns 400."""
        resp = client.put(f'/api/sites/{sample_site}/settings',
                          data='not json', content_type='text/plain')
        assert resp.status_code == 400
