"""Tests for dashboard routes, version API, and submissions API."""
import os
import pytest
import json
from unittest.mock import patch
from extensions import db
from models import Site, SitePage, SiteVersion, SiteVersionPage, FormSubmission


@pytest.fixture
def dashboard_app(tmp_path):
    """Create app with a fresh temporary database for dashboard tests."""
    db_path = str(tmp_path / 'test_dashboard.db')
    db_uri = 'sqlite:///' + db_path

    # Patch the config class BEFORE create_app runs
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True

    yield app


@pytest.fixture
def client(dashboard_app):
    """Test client using temp database."""
    return dashboard_app.test_client()


@pytest.fixture
def sample_site(dashboard_app):
    """Create a sample site with one homepage. Returns site ID string."""
    with dashboard_app.app_context():
        from models import Organization
        org = Organization.query.filter_by(slug='default').first()
        site = Site(org_id=org.id, name='Test Site', slug='test-site')
        db.session.add(site)
        db.session.flush()
        page = SitePage(
            site_id=site.id, slug='home', title='Home',
            yaml_content='- name: page\n  components: []\n',
            sort_order=0, is_homepage=True,
        )
        db.session.add(page)
        db.session.commit()
        return site.id  # Return ID to avoid detached instance issues


# =============================================================================
# Dashboard & Editor Routes
# =============================================================================

class TestDashboardRoutes:
    def test_dashboard_returns_200(self, client):
        """GET / returns the dashboard page."""
        res = client.get('/')
        assert res.status_code == 200
        assert b'dashboard' in res.data.lower()

    def test_editor_returns_200(self, client, sample_site):
        """GET /editor/<site_id> returns the editor page."""
        res = client.get(f'/editor/{sample_site}')
        assert res.status_code == 200
        assert b'Swift Sites' in res.data

    def test_preview_frame_still_works(self, client):
        """GET /preview-frame still works after route changes."""
        res = client.get('/preview-frame')
        assert res.status_code == 200


# =============================================================================
# Sites API — sections + version info
# =============================================================================

class TestSitesWithSections:
    def test_list_sites_includes_sections(self, client, sample_site):
        """GET /api/sites includes sections array."""
        res = client.get('/api/sites')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) >= 1
        site_data = next(s for s in data if s['id'] == sample_site)
        assert 'sections' in site_data
        assert 'development' in site_data['sections']  # draft site
        assert site_data['version_count'] == 0

    def test_published_site_in_published_section(self, client, sample_site):
        """After publishing, site appears in published section only."""
        client.post(f'/api/sites/{sample_site}/publish')
        res = client.get('/api/sites')
        site_data = next(s for s in res.get_json() if s['id'] == sample_site)
        assert site_data['sections'] == ['published']
        assert site_data['version_count'] == 1


# =============================================================================
# Version API
# =============================================================================

class TestVersionAPI:
    def test_publish_creates_version(self, client, sample_site):
        """Publishing creates a SiteVersion snapshot."""
        res = client.post(f'/api/sites/{sample_site}/publish')
        assert res.status_code == 200

        versions_res = client.get(f'/api/sites/{sample_site}/versions')
        versions = versions_res.get_json()
        assert len(versions) == 1
        assert versions[0]['version_number'] == 1
        assert versions[0]['is_current'] is True

    def test_multiple_publishes_increment_version(self, client, sample_site):
        """Each publish increments version number."""
        client.post(f'/api/sites/{sample_site}/publish')
        client.post(f'/api/sites/{sample_site}/publish')

        versions = client.get(f'/api/sites/{sample_site}/versions').get_json()
        assert len(versions) == 2
        assert versions[0]['version_number'] == 2  # newest first
        assert versions[1]['version_number'] == 1

    def test_rollback_restores_yaml(self, dashboard_app, client, sample_site):
        """Rollback restores YAML from a specific version."""
        # Publish v1 with original YAML
        client.post(f'/api/sites/{sample_site}/publish')

        # Modify the page YAML via API
        with dashboard_app.app_context():
            page = SitePage.query.filter_by(site_id=sample_site).first()
            page_id = page.id

        client.put(f'/api/sites/{sample_site}/pages/{page_id}',
                    json={'yaml_content': '- name: page\n  components:\n    - name: heading\n      properties:\n        text: Modified\n'})

        # Publish v2 with modified YAML
        client.post(f'/api/sites/{sample_site}/publish')

        # Get v1 ID
        versions = client.get(f'/api/sites/{sample_site}/versions').get_json()
        v1 = next(v for v in versions if v['version_number'] == 1)

        # Rollback to v1
        res = client.post(f'/api/sites/{sample_site}/versions/{v1["id"]}/rollback')
        assert res.status_code == 200
        assert res.get_json()['restored_version'] == 1

        # Verify YAML was restored
        with dashboard_app.app_context():
            page = SitePage.query.filter_by(site_id=sample_site).first()
            assert 'Modified' not in page.yaml_content

    def test_update_version_label(self, client, sample_site):
        """PATCH updates version label."""
        client.post(f'/api/sites/{sample_site}/publish')
        versions = client.get(f'/api/sites/{sample_site}/versions').get_json()
        v = versions[0]

        res = client.patch(f'/api/sites/{sample_site}/versions/{v["id"]}',
                           json={'label': 'Initial launch'})
        assert res.status_code == 200

        updated = client.get(f'/api/sites/{sample_site}/versions').get_json()
        assert updated[0]['label'] == 'Initial launch'

    def test_list_versions_empty(self, client, sample_site):
        """Unpublished site has no versions."""
        res = client.get(f'/api/sites/{sample_site}/versions')
        assert res.status_code == 200
        assert res.get_json() == []


# =============================================================================
# Submissions API
# =============================================================================

class TestSubmissionsAPI:
    @pytest.fixture
    def site_with_submissions(self, dashboard_app, sample_site):
        """Add some test submissions."""
        with dashboard_app.app_context():
            for i in range(3):
                sub = FormSubmission(
                    site_id=sample_site,
                    page_slug='home',
                    form_name='contact',
                    data=json.dumps({'name': f'User {i}', 'email': f'user{i}@test.com'}),
                    is_read=i == 0,
                    is_spam=i == 2,
                )
                db.session.add(sub)
            db.session.commit()
        return sample_site

    def test_list_submissions(self, client, site_with_submissions):
        """GET /api/submissions returns paginated list."""
        res = client.get('/api/submissions')
        assert res.status_code == 200
        data = res.get_json()
        assert data['total'] == 3
        assert len(data['items']) == 3

    def test_filter_unread(self, client, site_with_submissions):
        """Filter=unread excludes read and spam."""
        res = client.get('/api/submissions?filter=unread')
        data = res.get_json()
        assert data['total'] == 1  # Only one that is not read and not spam

    def test_filter_spam(self, client, site_with_submissions):
        """Filter=spam shows only spam."""
        res = client.get('/api/submissions?filter=spam')
        data = res.get_json()
        assert data['total'] == 1

    def test_mark_read(self, client, site_with_submissions):
        """PATCH marks submission as read."""
        subs = client.get('/api/submissions').get_json()['items']
        unread = next(s for s in subs if not s['is_read'] and not s['is_spam'])
        res = client.patch(f'/api/submissions/{unread["id"]}', json={'is_read': True})
        assert res.status_code == 200

    def test_mark_spam(self, client, site_with_submissions):
        """PATCH marks submission as spam."""
        subs = client.get('/api/submissions').get_json()['items']
        non_spam = next(s for s in subs if not s['is_spam'])
        res = client.patch(f'/api/submissions/{non_spam["id"]}', json={'is_spam': True})
        assert res.status_code == 200

    def test_delete_submission(self, client, site_with_submissions):
        """DELETE removes submission."""
        subs = client.get('/api/submissions').get_json()['items']
        res = client.delete(f'/api/submissions/{subs[0]["id"]}')
        assert res.status_code == 200
        updated = client.get('/api/submissions').get_json()
        assert updated['total'] == 2

    def test_csv_export(self, client, site_with_submissions):
        """GET /api/submissions/export returns CSV."""
        res = client.get('/api/submissions/export')
        assert res.status_code == 200
        assert res.content_type == 'text/csv; charset=utf-8'
        assert b'form_name' in res.data  # CSV header
        assert b'contact' in res.data    # Form name value

    def test_empty_submissions(self, client, sample_site):
        """Empty submission list returns properly."""
        res = client.get('/api/submissions')
        assert res.status_code == 200
        data = res.get_json()
        assert data['total'] == 0
        assert data['items'] == []
