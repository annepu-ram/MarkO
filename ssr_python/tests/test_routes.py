"""Tests for API endpoints."""
import pytest
import json


def ai_headers(client, token='test-ai-token'):
    with client.session_transaction() as sess:
        sess['ai_request_token'] = token
    return {
        'X-Requested-With': 'SwiftSitesApp',
        'X-AI-Request-Token': token,
        'Origin': 'http://localhost',
    }


class TestViewRoutes:
    def test_index_returns_200(self, client):
        """GET / returns 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_preview_frame_returns_200(self, client):
        """GET /preview-frame returns 200."""
        response = client.get('/preview-frame')
        assert response.status_code == 200


class TestMetadataRoutes:
    def test_schemas_returns_json(self, client):
        """GET /api/schemas returns JSON."""
        response = client.get('/api/schemas')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        # Should contain at least some component schemas
        assert len(data) > 0

    def test_defaults_returns_json(self, client):
        """GET /api/defaults returns JSON."""
        response = client.get('/api/defaults')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'heading' in data
        assert 'page' in data

    def test_tokens_returns_json(self, client):
        """GET /api/tokens returns JSON."""
        response = client.get('/api/tokens')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)


class TestRenderRoute:
    def test_render_valid_yaml(self, client, sample_page_yaml):
        """POST /render with valid YAML returns HTML."""
        response = client.post('/render', data=sample_page_yaml, content_type='text/plain')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Hello World' in html
        assert 'data-component-id' in html

    def test_render_minimal_yaml(self, client, minimal_heading_yaml):
        """POST /render with minimal YAML returns HTML."""
        response = client.post('/render', data=minimal_heading_yaml, content_type='text/plain')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Test Heading' in html

    def test_render_invalid_yaml(self, client):
        """POST /render with invalid YAML returns 400."""
        response = client.post('/render', data='{{invalid yaml', content_type='text/plain')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_render_empty_body(self, client):
        """POST /render with empty body returns error."""
        response = client.post('/render', data='', content_type='text/plain')
        # Empty YAML is parsed as None, which returns the invalid structure comment
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Invalid YAML' in html


class TestChatRoute:
    def test_chat_without_api_key(self, client, monkeypatch):
        """POST /api/chat without API key returns 503."""
        monkeypatch.delenv('OLLAMA_API_KEY', raising=False)
        response = client.post('/api/chat',
                               data=json.dumps({'message': 'test'}),
                               content_type='application/json',
                               headers=ai_headers(client))
        assert response.status_code == 503
        data = response.get_json()
        assert data['errorType'] == 'configuration'

    def test_chat_missing_message(self, client, monkeypatch):
        """POST /api/chat without message returns 400."""
        monkeypatch.setenv('OLLAMA_API_KEY', 'test-key')
        response = client.post('/api/chat',
                               data=json.dumps({}),
                               content_type='application/json',
                               headers=ai_headers(client))
        assert response.status_code == 400

    def test_chat_rejects_manual_post(self, client, monkeypatch):
        """POST /api/chat requires an app-issued AI request token."""
        monkeypatch.setenv('OLLAMA_API_KEY', 'test-key')
        response = client.post('/api/chat',
                               data=json.dumps({'message': 'test'}),
                               content_type='application/json')
        assert response.status_code == 403


class TestImageSearchRoute:
    def test_image_search_no_keys(self, client, monkeypatch):
        """GET /api/images/search without API keys returns 503."""
        monkeypatch.delenv('PEXELS_API_KEY', raising=False)
        monkeypatch.delenv('PIXABAY_API_KEY', raising=False)
        response = client.get('/api/images/search?q=test')
        assert response.status_code == 503

    def test_image_search_no_query(self, client, monkeypatch):
        """GET /api/images/search without query returns empty results."""
        monkeypatch.setenv('PEXELS_API_KEY', 'test-key')
        response = client.get('/api/images/search')
        assert response.status_code == 200
        data = response.get_json()
        assert data['results'] == []

    def test_visual_type_expands_stock_query(self):
        """Visual type adds controlled search terms without trusting free-form params."""
        from routes.images import _compose_search_query

        assert _compose_search_query('skincare', 'flat_lay') == 'skincare flat lay top view product photography'
        assert _compose_search_query('', 'product_photo') == 'product photography ecommerce clean background'
        assert _compose_search_query('logo', 'vector') == 'logo vector graphic clean scalable design'
        assert _compose_search_query('team', 'unknown') == 'team'

    def test_pexels_rejects_vector_visual_type(self, client, monkeypatch):
        """Pexels cannot serve vector or illustration image_type filters."""
        monkeypatch.setenv('PEXELS_API_KEY', 'pexels-key')
        monkeypatch.setenv('PIXABAY_API_KEY', 'pixabay-key')

        response = client.get('/api/images/search?q=logo&provider=pexels&visual_type=vector')

        assert response.status_code == 400
        assert 'Pexels does not support' in response.get_json()['error']

    def test_pixabay_maps_provider_specific_filters(self, monkeypatch):
        """Pixabay uses image_type plus horizontal/vertical orientation values."""
        from routes import images

        captured = {}

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    'totalHits': 1,
                    'hits': [{
                        'id': 123,
                        'previewURL': 'https://example.com/thumb.jpg',
                        'webformatURL': 'https://example.com/regular.jpg',
                        'largeImageURL': 'https://example.com/full.jpg',
                        'tags': 'logo, vector, blue',
                        'user': 'Designer',
                        'user_id': 42,
                        'imageWidth': 1200,
                        'imageHeight': 800,
                    }],
                }

        def fake_get(url, params, timeout):
            captured['url'] = url
            captured['params'] = params
            captured['timeout'] = timeout
            return FakeResponse()

        monkeypatch.setenv('PIXABAY_API_KEY', 'pixabay-key')
        monkeypatch.setattr(images.http_requests, 'get', fake_get)

        result = images._search_pixabay('logo vector', 'purple', 1, 24, 'landscape', 'vector')

        assert captured['url'] == 'https://pixabay.com/api/'
        assert captured['params']['image_type'] == 'vector'
        assert captured['params']['orientation'] == 'horizontal'
        assert captured['params']['colors'] == 'lilac'
        assert result['results'][0]['source'] == 'pixabay'

    def test_provider_only_search_returns_empty(self, client, monkeypatch):
        """Provider selection alone is not a search intent."""
        monkeypatch.setenv('PEXELS_API_KEY', 'pexels-key')
        response = client.get('/api/images/search?provider=pexels')
        assert response.status_code == 200
        assert response.get_json()['results'] == []
