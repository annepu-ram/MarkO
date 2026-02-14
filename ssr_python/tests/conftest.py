import pytest
import os
import yaml
from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('development')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_page_yaml():
    """Load sample page YAML fixture."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    with open(os.path.join(fixtures_dir, 'sample_page.yaml'), 'r') as f:
        return f.read()


@pytest.fixture
def sample_page_structure():
    """Load sample page as parsed structure."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    with open(os.path.join(fixtures_dir, 'sample_page.yaml'), 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def minimal_heading_yaml():
    """Minimal YAML with just a page and heading."""
    return """- name: page
  components:
    - name: heading
      properties:
        text: Test Heading
"""
