"""Tests for security headers and error sanitization."""
import pytest


class TestSecurityHeaders:
    def test_x_frame_options(self, client):
        """Every response has X-Frame-Options header."""
        response = client.get('/')
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_content_security_policy(self, client):
        """Every response has Content-Security-Policy header."""
        response = client.get('/')
        csp = response.headers.get('Content-Security-Policy')
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp

    def test_x_content_type_options(self, client):
        """Every response has X-Content-Type-Options header."""
        response = client.get('/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_security_headers_on_api(self, client):
        """Security headers present on API responses too."""
        response = client.get('/api/schemas')
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'


class TestErrorSanitization:
    def test_render_error_no_traceback(self, client):
        """Render errors don't leak tracebacks."""
        # Send YAML that will fail during rendering (valid YAML, invalid structure)
        response = client.post('/render', data='- name: nonexistent_component\n  properties: {}',
                               content_type='text/plain')
        # Should return 500 with safe error message
        if response.status_code == 500:
            data = response.get_json()
            assert 'traceback' not in str(data).lower() or 'Traceback' not in data.get('details', '')

    def test_chat_error_no_api_key_leak(self, client, monkeypatch):
        """Chat errors don't leak API keys."""
        monkeypatch.delenv('OLLAMA_API_KEY', raising=False)
        response = client.post('/api/chat',
                               data='{"message": "test"}',
                               content_type='application/json')
        response_text = response.get_data(as_text=True)
        assert 'OLLAMA_API_KEY' not in response_text
        assert 'PEXELS_API_KEY' not in response_text

    def test_image_error_no_key_leak(self, client, monkeypatch):
        """Image search errors don't leak API keys."""
        monkeypatch.delenv('PEXELS_API_KEY', raising=False)
        monkeypatch.delenv('PIXABAY_API_KEY', raising=False)
        response = client.get('/api/images/search?q=test')
        response_text = response.get_data(as_text=True)
        assert 'PEXELS_API_KEY' not in response_text
        assert 'PIXABAY_API_KEY' not in response_text
