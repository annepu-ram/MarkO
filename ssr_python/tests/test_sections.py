"""Tests for the Sections API (live-binding compositions of content items)."""
import pytest
from flask import g
from unittest.mock import patch
from extensions import db
from models import SectionItem, ContentItem, Organization, Brand
from campaign.content_type_catalog import slots_from_content


@pytest.fixture
def section_app(tmp_path):
    db_path = str(tmp_path / 'test_sections.db')
    db_uri = 'sqlite:///' + db_path
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(section_app):
    return section_app.test_client()


def _make_content(client, category='headline', content='Save 40% this week', **extra):
    slots = extra.pop('slots', None)
    payload = {
        'category': category,
        'slots': slots if slots is not None else slots_from_content(category, content),
    }
    payload.update(extra)
    res = client.post('/api/content', json=payload)
    assert res.status_code == 201
    return res.get_json()['id']


def ai_headers(client, token='sections-ai-token'):
    with client.session_transaction() as sess:
        sess['ai_request_token'] = token
    return {
        'X-Requested-With': 'SwiftSitesApp',
        'X-AI-Request-Token': token,
        'Origin': 'http://localhost',
    }


def _mock_rag_section_generation(monkeypatch):
    def fake_generate(section_type, content_items, brand=None, product=None, site_shell_config=None, section_metadata=None):
        components = []
        if section_type == 'faq':
            items = []
            for item in content_items:
                payload = item.get_slots()
                items.append({
                    'title': payload.get('question') or item.title or 'Question',
                    'components': [{
                        'name': 'paragraph',
                        'properties': {'text': payload.get('answer') or item.content or ''},
                    }],
                })
            components = [{
                'name': 'layout-row',
                'components': [{'name': 'accordion', 'properties': {}, 'items': items}],
            }]
        else:
            children = []
            for item in content_items:
                payload = item.get_slots()
                if item.category == 'cta':
                    if payload.get('headline'):
                        children.append({'name': 'heading', 'properties': {'text': payload['headline']}})
                    if payload.get('paragraph'):
                        children.append({'name': 'paragraph', 'properties': {'text': payload['paragraph']}})
                    children.append({
                        'name': 'button',
                        'properties': {
                            'text': payload.get('button_label') or item.content,
                            'action': {'type': 'link', 'href': payload.get('link') or '#lead'},
                        },
                    })
                elif item.category == 'headline':
                    children.append({'name': 'heading', 'properties': {'text': item.content}})
                else:
                    children.append({'name': 'paragraph', 'properties': {'text': item.content}})
            components = [{'name': 'layout-row', 'components': children}]

        import yaml
        return yaml.dump(components, default_flow_style=False, allow_unicode=True, sort_keys=False), {
            'compiler': 'campaign_section_rag.v1',
            'section_type': section_type,
            'source_content_ids': [item.id for item in content_items],
            'brand_id': getattr(brand, 'id', None),
            'site_id': (site_shell_config or {}).get('site_id'),
            'style_prompt': {},
            'retrieval': {'section_chunk_ids': [], 'component_chunk_ids': [], 'repairs': []},
            'render_wrapper': {
                'source': 'brand_site_shell',
                'uses': ['theme.colors', 'theme.fonts'],
            },
        }

    monkeypatch.setattr(
        'campaign.content_to_section.generate_section_yaml_with_agents',
        fake_generate,
    )


# =============================================================================
# CRUD + validation
# =============================================================================

class TestSectionCrud:
    def test_list_empty(self, client):
        res = client.get('/api/sections')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_create_requires_name(self, client):
        res = client.post('/api/sections', json={'content_refs': []})
        assert res.status_code == 400
        assert 'name' in res.get_json()['error'].lower()

    def test_create_minimal(self, client):
        res = client.post('/api/sections', json={'name': 'Hero block'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['name'] == 'Hero block'
        assert data['status'] == 'draft'
        assert data['section_type'] == 'custom'
        assert data['section_type_label'] == 'Custom'
        assert data['content_refs'] == []
        assert data['item_count'] == 0

    def test_section_types_endpoint(self, client):
        res = client.get('/api/sections/types')
        assert res.status_code == 200
        data = res.get_json()
        keys = {item['key'] for item in data}
        assert {'hero', 'features', 'custom'}.issubset(keys)
        hero = next(item for item in data if item['key'] == 'hero')
        assert 'headline' in hero['suggested_categories']

    def test_create_with_section_type(self, client):
        res = client.post('/api/sections', json={'name': 'Hero block', 'section_type': 'hero'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['section_type'] == 'hero'
        assert data['section_type_label'] == 'Hero'
        assert 'headline' in data['suggested_categories']

    def test_create_rejects_invalid_section_type(self, client):
        res = client.post('/api/sections', json={'name': 'Bad block', 'section_type': 'made_up'})
        assert res.status_code == 400
        assert 'section_type' in res.get_json()['error']

    def test_create_with_ordered_refs(self, client):
        a = _make_content(client, 'headline', 'H1')
        b = _make_content(client, 'testimonial', 'Great product')
        c = _make_content(client, 'cta', 'Start free trial')

        res = client.post('/api/sections', json={
            'name': 'Homepage hero',
            'content_refs': [c, a, b],   # deliberately not creation order
            'tags': ['homepage', 'launch'],
        })
        assert res.status_code == 201
        data = res.get_json()
        # Order is preserved exactly as submitted.
        assert data['content_refs'] == [c, a, b]
        assert data['item_count'] == 3
        assert data['missing_count'] == 0
        assert data['tags'] == ['homepage', 'launch']
        # Card previews resolve the bound items.
        assert [it['id'] for it in data['items']] == [c, a, b]

    def test_create_rejects_unknown_content_ref(self, client):
        good = _make_content(client)
        res = client.post('/api/sections', json={
            'name': 'Bad section',
            'content_refs': [good, 'does-not-exist'],
        })
        assert res.status_code == 400
        assert 'unknown' in res.get_json()['error'].lower()

    def test_update_section(self, client):
        a = _make_content(client, 'headline', 'H1')
        section_id = client.post('/api/sections', json={'name': 'Sec'}).get_json()['id']

        res = client.patch(f'/api/sections/{section_id}', json={
            'name': 'Renamed',
            'status': 'active',
            'content_refs': [a],
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['name'] == 'Renamed'
        assert data['status'] == 'active'
        assert data['content_refs'] == [a]

    def test_update_invalid_status_rejected(self, client):
        section_id = client.post('/api/sections', json={'name': 'Sec'}).get_json()['id']
        res = client.patch(f'/api/sections/{section_id}', json={'status': 'published'})
        assert res.status_code == 400

    def test_delete_section(self, client):
        section_id = client.post('/api/sections', json={'name': 'Sec'}).get_json()['id']
        res = client.delete(f'/api/sections/{section_id}')
        assert res.status_code == 200
        assert client.get('/api/sections').get_json() == []

    def test_list_filters(self, client):
        client.post('/api/sections', json={'name': 'Active one', 'status': 'active'})
        client.post('/api/sections', json={'name': 'Draft one', 'status': 'draft'})

        res = client.get('/api/sections?status=active')
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Active one'

        res = client.get('/api/sections?q=draft')
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Draft one'


# =============================================================================
# Live-binding preview
# =============================================================================

class TestSectionPreview:
    def test_preview_renders_bound_items(self, client):
        a = _make_content(client, 'headline', 'Save 40% this week')
        b = _make_content(client, 'cta', 'Start free trial')
        section_id = client.post('/api/sections', json={
            'name': 'Hero', 'content_refs': [a, b],
        }).get_json()['id']

        res = client.get(f'/api/sections/{section_id}/preview')
        assert res.status_code == 200
        assert res.mimetype == 'text/html'
        html = res.get_data(as_text=True)
        assert 'Save 40% this week' in html
        assert 'Start free trial' in html

    def test_preview_reflects_live_content_edits(self, client):
        """Editing a referenced content item changes the section preview (no stored HTML)."""
        a = _make_content(client, 'headline', 'Original headline')
        section_id = client.post('/api/sections', json={
            'name': 'Hero', 'content_refs': [a],
        }).get_json()['id']

        before = client.get(f'/api/sections/{section_id}/preview').get_data(as_text=True)
        assert 'Original headline' in before

        client.patch(f'/api/content/{a}', json={'slots': {'headline': 'Updated headline'}})

        after = client.get(f'/api/sections/{section_id}/preview').get_data(as_text=True)
        assert 'Updated headline' in after
        assert 'Original headline' not in after

    def test_preview_skips_deleted_refs(self, client):
        a = _make_content(client, 'headline', 'Keep me')
        b = _make_content(client, 'cta', 'Delete me')
        section_id = client.post('/api/sections', json={
            'name': 'Hero', 'content_refs': [a, b],
        }).get_json()['id']

        client.delete(f'/api/content/{b}')

        res = client.get(f'/api/sections/{section_id}/preview')
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert 'Keep me' in html
        assert 'Delete me' not in html

    def test_preview_empty_section_is_not_fatal(self, client):
        section_id = client.post('/api/sections', json={'name': 'Empty'}).get_json()['id']
        res = client.get(f'/api/sections/{section_id}/preview')
        assert res.status_code == 200
        assert res.mimetype == 'text/html'

    def test_preview_missing_section_404(self, client):
        res = client.get('/api/sections/nope/preview')
        assert res.status_code == 404


# =============================================================================
# YAML-backed section generation
# =============================================================================

class TestYamlBackedSections:
    def test_create_section_from_composite_cta_stores_yaml(self, client, monkeypatch):
        _mock_rag_section_generation(monkeypatch)
        cta = _make_content(
            client,
            'cta',
            '',
            slots={
                'headline': 'Create campaigns once. Publish everywhere.',
                'paragraph': 'Turn campaign truth into pages, emails, and ads.',
                'button_label': 'Book a demo',
                'link': '#demo',
            },
        )

        res = client.post('/api/sections/from-content', json={
            'name': 'Final CTA',
            'section_type': 'cta',
            'content_refs': [cta],
        })

        assert res.status_code == 201
        section = res.get_json()['section']
        assert section['yaml_content']
        assert 'Create campaigns once. Publish everywhere.' in section['yaml_content']
        assert 'Book a demo' in section['yaml_content']
        assert section['generation_metadata']['compiler'] == 'campaign_section_rag.v1'

        html = client.get(f'/api/sections/{section["id"]}/preview').get_data(as_text=True)
        assert 'Create campaigns once. Publish everywhere.' in html
        assert 'Book a demo' in html

    def test_regenerate_yaml_updates_from_current_content_refs(self, client, monkeypatch):
        _mock_rag_section_generation(monkeypatch)
        headline = _make_content(client, 'headline', 'Original headline')
        section = client.post('/api/sections/from-content', json={
            'name': 'Hero',
            'section_type': 'hero',
            'content_refs': [headline],
        }).get_json()['section']

        client.patch(f'/api/content/{headline}', json={'slots': {'headline': 'Updated headline'}})
        before = client.get(f'/api/sections/{section["id"]}/preview').get_data(as_text=True)
        assert 'Original headline' in before
        assert 'Updated headline' not in before

        res = client.post(f'/api/sections/{section["id"]}/regenerate-yaml')
        assert res.status_code == 200
        updated = res.get_json()['section']
        assert 'Updated headline' in updated['yaml_content']

        after = client.get(f'/api/sections/{section["id"]}/preview').get_data(as_text=True)
        assert 'Updated headline' in after

    def test_faq_composite_compiles_to_accordion_yaml(self, client, monkeypatch):
        _mock_rag_section_generation(monkeypatch)
        faq = _make_content(
            client,
            'faq',
            '',
            slots={'question': 'Is it reusable?', 'answer': 'Yes, sections store YAML.'},
        )
        res = client.post('/api/sections/from-content', json={
            'name': 'FAQ',
            'section_type': 'faq',
            'content_refs': [faq],
        })
        assert res.status_code == 201
        yaml_content = res.get_json()['section']['yaml_content']
        assert 'accordion' in yaml_content
        assert 'Is it reusable?' in yaml_content

    def test_section_preview_uses_brand_site_shell_theme_without_header_footer(self, section_app, client, monkeypatch):
        _mock_rag_section_generation(monkeypatch)
        with section_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            brand = Brand(
                org_id=org.id,
                name='Shell Theme Brand',
                slug='shell-theme-brand',
                tagline='Header tagline should not render in section preview.',
                color_primary='#123456',
                color_text='#654321',
                color_secondary='#777777',
                color_accent='#abcdef',
                color_background='#f7f7f7',
                font_heading='Theme Heading',
                font_body='Theme Body',
            )
            db.session.add(brand)
            db.session.commit()
            brand_id = brand.id

        headline = _make_content(client, 'headline', 'Themed section heading', brand_id=brand_id)
        res = client.post('/api/sections/from-content', json={
            'name': 'Themed Hero',
            'section_type': 'hero',
            'brand_id': brand_id,
            'content_refs': [headline],
        })
        assert res.status_code == 201
        section = res.get_json()['section']
        assert section['yaml_content'].lstrip().startswith('- name: layout-row')
        assert '- name: site' not in section['yaml_content']
        assert '- name: page' not in section['yaml_content']

        html = client.get(f'/api/sections/{section["id"]}/preview').get_data(as_text=True)
        assert '--font-heading: Theme Heading' in html
        assert '--font-content: Theme Body' in html
        assert 'Themed section heading' in html
        assert 'Header tagline should not render in section preview.' not in html

        with section_app.app_context():
            from routes.brand import _build_section_yaml_preview_structure, _section_site_shell_config
            g.current_org_id = Organization.query.filter_by(slug='default').first().id
            stored_section = SectionItem.query.get(section['id'])
            stored_brand = Brand.query.get(brand_id)
            config = _section_site_shell_config(stored_brand)
            structure = _build_section_yaml_preview_structure(stored_section, config['theme'])
            theme = structure[0]['properties']['theme']
            assert theme['colors']['text'] == '#654321'
            assert theme['colors']['primary'] == '#123456'
            assert theme['fonts']['heading'] == 'Theme Heading'
            assert 'header' not in structure[0]
            assert 'footer' not in structure[0]

    def test_agent_generation_stores_body_only_yaml_and_metadata(self, client, monkeypatch):
        headline = _make_content(client, 'headline', 'Agent headline')
        captured = {}

        def fake_generate(section_type, content_items, brand=None, product=None, site_shell_config=None, section_metadata=None):
            captured['section_type'] = section_type
            captured['content'] = [item.content for item in content_items]
            captured['site_shell_config'] = site_shell_config
            return (
                "- name: layout-row\n"
                "  components:\n"
                "    - name: heading\n"
                "      properties:\n"
                "        text: Agent headline\n",
                {
                    "compiler": "campaign_section_rag.v1",
                    "source_content_ids": [headline],
                    "style_prompt": {},
                    "retrieval": {"section_chunk_ids": [], "component_chunk_ids": [], "repairs": []},
                    "render_wrapper": {
                        "source": "brand_site_shell",
                        "uses": ["theme.colors", "theme.fonts"],
                    },
                },
            )

        monkeypatch.setattr(
            'campaign.content_to_section.generate_section_yaml_with_agents',
            fake_generate,
        )

        res = client.post('/api/sections/from-content', json={
            'name': 'Agent Hero',
            'section_type': 'hero',
            'content_refs': [headline],
        })
        assert res.status_code == 201
        section = res.get_json()['section']
        assert section['generation_metadata']['compiler'] == 'campaign_section_rag.v1'
        assert '- name: site' not in section['yaml_content']
        assert '- name: page' not in section['yaml_content']
        assert captured['section_type'] == 'hero'
        assert captured['content'] == ['Agent headline']
        assert captured['site_shell_config']['theme']['colors']

    def test_section_yaml_rejects_site_page_wrappers(self, client):
        res = client.post('/api/sections', json={
            'name': 'Wrapped',
            'yaml_content': '- name: site\n  components: []\n',
        })
        assert res.status_code == 400
        assert 'body-only' in res.get_json()['error']

    def test_fallback_generation_mode_is_rejected(self, client):
        headline = _make_content(client, 'headline', 'No fallback')
        res = client.post('/api/sections/from-content', json={
            'name': 'No fallback',
            'section_type': 'hero',
            'content_refs': [headline],
            'generation_mode': 'fallback',
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'generation_mode must be agent.'

    def test_agent_generation_failure_returns_error(self, client, monkeypatch):
        headline = _make_content(client, 'headline', 'Generation should fail')

        def fail_generate(*args, **kwargs):
            raise ValueError('RAG generation failed')

        monkeypatch.setattr(
            'campaign.content_to_section.generate_section_yaml_with_agents',
            fail_generate,
        )

        res = client.post('/api/sections/from-content', json={
            'name': 'Broken generation',
            'section_type': 'hero',
            'content_refs': [headline],
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'RAG generation failed'

    def test_agent_context_exposes_composite_slots(self, section_app, client):
        cta = _make_content(
            client,
            'cta',
            '',
            slots={
                'headline': 'Create once',
                'paragraph': 'Publish everywhere',
                'button_label': 'Book a demo',
            },
        )
        faq = _make_content(
            client,
            'faq',
            '',
            slots={
                'question': 'Is it reusable?',
                'answer': 'Yes.',
            },
        )

        with section_app.app_context():
            from campaign.content_to_section import _build_agent_section_context
            items = ContentItem.query.filter(ContentItem.id.in_([cta, faq])).all()
            by_id = {item.id: item for item in items}
            context = _build_agent_section_context('faq', [by_id[cta], by_id[faq]], None, None, {})

        assert context['derived_atoms']['cta.headline'] == 'Create once'
        assert context['derived_atoms']['cta.paragraph'] == 'Publish everywhere'
        assert context['derived_atoms']['cta.button_label'] == 'Book a demo'
        assert context['derived_atoms']['faq.question'] == 'Is it reusable?'
        assert context['derived_atoms']['faq.answer'] == 'Yes.'

    def test_campaign_section_rag_uses_saved_brand_style_prompt_and_logs(self, section_app, client, monkeypatch):
        headline = _make_content(client, 'headline', 'Launch faster')
        captured = {'prompts': [], 'outputs': []}

        class FakeSearch:
            def load(self):
                return None

            def search(self, *args, **kwargs):
                return [({'id': 'example-1', 'content': '- name: layout-row\n  components: []\n'}, 1.0)]

        def fake_generate(self, system, user_prompt, **kwargs):
            captured['system'] = system
            captured['user_prompt'] = user_prompt
            return """```yaml
- name: layout-row
  components:
    - name: layout-column
      properties:
        layout:
          widthMode: stretch
      components:
        - name: heading
          properties:
            text: Launch faster
```"""

        monkeypatch.setattr('campaign.section_rag.KeywordSearch', FakeSearch)
        monkeypatch.setattr('campaign.section_rag.CampaignModelBackend.generate', fake_generate)
        monkeypatch.setattr('campaign.section_rag.log_campaign_prompt', lambda *args, **kwargs: captured['prompts'].append((args, kwargs)))
        monkeypatch.setattr('campaign.section_rag.log_campaign_output', lambda *args, **kwargs: captured['outputs'].append((args, kwargs)))

        with section_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            brand = Brand(
                org_id=org.id,
                name='Prompt Brand',
                slug='prompt-brand',
                section_style_prompt='Use sharp editorial hero spacing.',
                section_style_prompt_metadata='{"compiler":"campaign_brand_styler.v1"}',
            )
            db.session.add(brand)
            db.session.commit()
            item = ContentItem.query.get(headline)

            from campaign.section_rag import generate_section_yaml
            yaml_text, metadata = generate_section_yaml(
                'hero',
                [item],
                brand=brand,
                site_shell_config={'theme': {'colors': {}, 'fonts': {}}, 'site_id': 'site-1'},
                section_metadata={'name': 'Hero'},
            )

        assert 'Use sharp editorial hero spacing.' in captured['user_prompt']
        assert 'Launch faster' in captured['user_prompt']
        assert captured['prompts']
        assert captured['outputs']
        assert metadata['compiler'] == 'campaign_section_rag.v1'
        assert metadata['style_prompt']['compiler'] == 'campaign_brand_styler.v1'
        assert '- name: site' not in yaml_text
        assert '- name: page' not in yaml_text

    def test_campaign_rag_config_reads_independent_env_overrides(self, monkeypatch):
        monkeypatch.setenv('CAMPAIGN_SECTION_TOP_K', '7')
        monkeypatch.setenv('CAMPAIGN_RAG_MODEL_NAME', 'campaign-model')
        from campaign.rag_config import CampaignRAGConfig

        cfg = CampaignRAGConfig()
        assert cfg.section_top_k == 7
        assert cfg.model_name == 'campaign-model'


# =============================================================================
# AI section drafting
# =============================================================================

class TestAiSectionDrafting:
    def test_generate_section_returns_unsaved_section_draft(self, client):
        seed = _make_content(client, 'headline', 'Launch faster')
        cta = _make_content(client, 'cta', 'Book a demo')

        class FakeBackend:
            def generate(self, system_prompt, user_prompt):
                return (
                    '{"section_type":"hero","name":"Launch hero",'
                    f'"ordered_existing_ids":["{seed}","{cta}"],'
                    '"new_items":[{"category":"subheadline","title":"Support line",'
                    '"content":"Turn approved content into campaign-ready sections."}]}'
                )

        with patch('rag.agent.model_backend.ModelBackend', return_value=FakeBackend()):
            res = client.post(
                '/api/chat/generate-section',
                json={'seed_content_id': seed},
                headers=ai_headers(client),
            )

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'ai'
        assert data['section']['section_type'] == 'hero'
        assert data['section']['name'] == 'Launch hero'
        assert data['section']['content_refs'][:2] == [seed, cta]
        assert len(data['created_draft_ids']) == 1

        saved_sections = client.get('/api/sections').get_json()
        assert saved_sections == []

        draft_content = client.get('/api/content?status=draft&source=ai').get_json()
        assert any(item['id'] == data['created_draft_ids'][0] for item in draft_content)

    def test_generate_section_rejects_invalid_generated_category(self, client):
        seed = _make_content(client, 'headline', 'Launch faster')

        class FakeBackend:
            def generate(self, system_prompt, user_prompt):
                return (
                    '{"section_type":"hero","name":"Bad hero",'
                    f'"ordered_existing_ids":["{seed}"],'
                    '"new_items":[{"category":"not_real","content":"Bad"}]}'
                )

        with patch('rag.agent.model_backend.ModelBackend', return_value=FakeBackend()):
            res = client.post(
                '/api/chat/generate-section',
                json={'seed_content_id': seed},
                headers=ai_headers(client),
            )

        assert res.status_code == 400
        assert 'category' in res.get_json()['error']


# =============================================================================
# Model helpers
# =============================================================================

class TestSectionModel:
    def test_content_refs_roundtrip_and_dict_form(self, section_app):
        with section_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            section = SectionItem(org_id=org.id, name='S')
            # Accept both bare ids and {content_item_id: ...} dicts.
            section.content_refs = None
            assert section.get_content_refs() == []
            section.set_content_refs(['x', 'y', 'z'])
            assert section.get_content_refs() == ['x', 'y', 'z']
