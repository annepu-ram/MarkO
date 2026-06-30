"""Tests for Brand Kit & Content Library API."""
import pathlib
import re
import pytest
from unittest.mock import patch
from extensions import db
from models import ContentItem, Organization, Campaign, CampaignMessage, Brand, SectionItem, Site, SiteSharedBlock
from campaign.content_type_catalog import slots_from_content


@pytest.fixture
def brand_app(tmp_path, monkeypatch):
    db_path = str(tmp_path / 'test_brand.db')
    db_uri = 'sqlite:///' + db_path
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    monkeypatch.setattr(
        'campaign.section_rag.generate_brand_section_style_prompt',
        lambda brand, site_shell_config=None, org_id=None, content_wording_prompt=None: (
            f"Style sections for {brand.name} using {brand.default_style or 'brand defaults'}. Wording: {content_wording_prompt or ''}",
            {
                'compiler': 'campaign_brand_styler.v1',
                'site_shell': {
                    'source': 'brand_site_shell',
                    'site_id': (site_shell_config or {}).get('site_id'),
                    'uses': ['theme.colors', 'theme.fonts'],
                },
            },
        ),
    )
    monkeypatch.setattr(
        'campaign.section_rag.generate_brand_content_wording_prompt',
        lambda brand, site_shell_config=None, org_id=None: (
            f"Write content for {brand.name} using {brand.tone or 'brand voice'}.",
            {
                'compiler': 'campaign_brand_wording.v1',
                'site_shell': {
                    'source': 'brand_site_shell',
                    'site_id': (site_shell_config or {}).get('site_id'),
                    'uses': ['theme.colors', 'theme.fonts'],
                },
            },
        ),
    )
    yield app


@pytest.fixture
def client(brand_app):
    return brand_app.test_client()


def ai_headers(client, token='brand-ai-token'):
    with client.session_transaction() as sess:
        sess['ai_request_token'] = token
    return {
        'X-Requested-With': 'SwiftSitesApp',
        'X-AI-Request-Token': token,
        'Origin': 'http://localhost',
    }


def content_payload(category, content='', **extra):
    slots = extra.pop('slots', None)
    payload = {
        'category': category,
        'slots': slots if slots is not None else slots_from_content(category, content),
    }
    payload.update(extra)
    return payload


# =============================================================================
# Content Library
# =============================================================================

class TestContentLibrary:
    def test_list_empty(self, client):
        res = client.get('/api/content')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_content_options_return_grouped_content_type_catalog(self, client):
        res = client.get('/api/content/options')
        assert res.status_code == 200
        data = res.get_json()
        assert 'categories' not in data
        assert {'content_types', 'content_type_families'}.issubset(data)

        families = {family['key']: family['label'] for family in data['content_type_families']}
        assert families['core_message'] == 'Core Message'
        assert families['channel_assets'] == 'Channel Assets'

        types = {item['key']: item for item in data['content_types']}
        assert types['headline']['family'] == 'core_message'
        assert all(item.get('slot_schema') for item in data['content_types'])
        assert types['headline']['slot_schema'][0]['key'] == 'headline'
        assert types['testimonial']['proof_sensitive'] is True
        assert types['cta']['slot_schema'][0]['key'] == 'headline'
        assert any(slot['key'] == 'button_label' for slot in types['cta']['slot_schema'])
        assert types['email_subject']['page_usable'] is False
        assert {slot['key'] for slot in types['email_subject']['slot_schema']} == {'subject', 'preview_text'}

    def test_create_item(self, client):
        res = client.post('/api/content', json=content_payload(
            'headline',
            'Build Faster, Ship Sooner',
            title='Main headline',
            status='active',
            source='manual',
            channel='landing_page',
            tags=['launch', 'hero'],
            proof_source='Approved launch brief',
            proof_permission_status='approved',
            quality_score=88,
        ))
        assert res.status_code == 201
        data = res.get_json()
        assert data['category'] == 'headline'
        assert data['content'] == 'Build Faster, Ship Sooner'
        assert data['slots'] == {'headline': 'Build Faster, Ship Sooner'}
        assert data['title'] == 'Main headline'
        assert data['status'] == 'active'
        assert data['source'] == 'manual'
        assert data['channel'] == 'landing_page'
        assert data['tags'] == ['launch', 'hero']
        assert data['proof_source'] == 'Approved launch brief'
        assert data['proof_permission_status'] == 'approved'
        assert data['quality_score'] == 88
        assert data['is_pinned'] is False

    def test_content_folders_crud_and_filter(self, client):
        create = client.post('/api/content/folders', json={'name': 'Homepage', 'sort_order': 2})
        assert create.status_code == 201
        folder = create.get_json()
        assert folder['name'] == 'Homepage'

        update = client.patch(f'/api/content/folders/{folder["id"]}', json={'name': 'Homepage blocks'})
        assert update.status_code == 200
        assert update.get_json()['name'] == 'Homepage blocks'

        filed = client.post('/api/content', json=content_payload(
            'headline',
            'Filed headline',
            folder_id=folder['id'],
        )).get_json()
        client.post('/api/content', json=content_payload('headline', 'Unfiled headline'))

        filtered = client.get(f'/api/content?folder_id={folder["id"]}').get_json()
        assert [item['id'] for item in filtered] == [filed['id']]
        assert filtered[0]['folder']['name'] == 'Homepage blocks'

        unfiled = client.get('/api/content?folder_id=unfiled').get_json()
        assert len(unfiled) == 1
        assert unfiled[0]['content'] == 'Unfiled headline'

        delete = client.delete(f'/api/content/folders/{folder["id"]}')
        assert delete.status_code == 200
        refetched = client.get(f'/api/content?folder_id=unfiled').get_json()
        assert {item['content'] for item in refetched} == {'Filed headline', 'Unfiled headline'}

    def test_composite_content_can_derive_summary_from_slots(self, client):
        res = client.post('/api/content', json={
            'category': 'faq',
            'slots': {
                'question': 'Can sections render this?',
                'answer': 'Yes, the answer becomes fallback content.',
            },
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['content'] == 'Yes, the answer becomes fallback content.'
        assert data['slots']['question'] == 'Can sections render this?'

    def test_primitive_content_can_derive_summary_from_slots(self, client):
        res = client.post('/api/content', json={
            'category': 'headline',
            'slots': {'headline': 'Structured headline'},
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['content'] == 'Structured headline'
        assert data['slots']['headline'] == 'Structured headline'

    def test_create_invalid_category(self, client):
        res = client.post('/api/content', json={
            'category': 'random_stuff',
            'slots': {'headline': 'Hello'},
        })
        assert res.status_code == 400

    def test_create_expanded_marketing_categories(self, client):
        categories = ['value_proposition', 'guarantee', 'seo_meta', 'announcement']
        for category in categories:
            res = client.post('/api/content', json=content_payload(category, f'{category} content'))
            assert res.status_code == 201
            assert res.get_json()['category'] == category

    def test_create_empty_content(self, client):
        res = client.post('/api/content', json={
            'category': 'headline',
            'slots': {'headline': ''},
        })
        assert res.status_code == 400

    def test_list_filter_by_category(self, client):
        client.post('/api/content', json=content_payload('headline', 'H1'))
        client.post('/api/content', json=content_payload('testimonial', 'T1'))
        client.post('/api/content', json=content_payload('headline', 'H2'))

        res = client.get('/api/content?category=headline')
        data = res.get_json()
        assert len(data) == 2
        assert all(i['category'] == 'headline' for i in data)

    def test_list_filter_by_status_source_and_product(self, client):
        brand_res = client.post('/api/brands', json={'name': 'FitZone'})
        brand_id = brand_res.get_json()['id']
        product_res = client.post('/api/products', json={
            'name': 'Training Plan',
            'brand_ids': [brand_id],
        })
        product_id = product_res.get_json()['id']

        client.post('/api/content', json=content_payload(
            'offer',
            'Save 20% this week',
            status='approved',
            source='manual',
            brand_id=brand_id,
            product_id=product_id,
        ))
        client.post('/api/content', json=content_payload(
            'offer',
            'Draft offer',
            status='draft',
            source='ai',
        ))

        res = client.get(f'/api/content?status=approved&source=manual&product_id={product_id}')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['content'] == 'Save 20% this week'
        assert data[0]['brand_id'] == brand_id
        assert data[0]['product_id'] == product_id

    def test_reject_product_not_tagged_to_selected_brand(self, client):
        brand_a = client.post('/api/brands', json={'name': 'Brand A'}).get_json()['id']
        brand_b = client.post('/api/brands', json={'name': 'Brand B'}).get_json()['id']
        product_id = client.post('/api/products', json={
            'name': 'Brand A Product',
            'brand_ids': [brand_a],
        }).get_json()['id']

        res = client.post('/api/content', json=content_payload(
            'product_feature',
            'Fast setup',
            brand_id=brand_b,
            product_id=product_id,
        ))
        assert res.status_code == 400

    def test_update_item(self, client):
        create_res = client.post('/api/content', json=content_payload('benefit', 'Original'))
        item_id = create_res.get_json()['id']

        res = client.patch(f'/api/content/{item_id}', json={
            'slots': {'paragraph': 'Updated benefit text'},
            'is_pinned': True,
            'status': 'approved',
            'tags': 'speed, conversion',
        })
        assert res.status_code == 200
        assert res.get_json()['content'] == 'Updated benefit text'
        assert res.get_json()['is_pinned'] is True
        assert res.get_json()['status'] == 'approved'
        assert res.get_json()['tags'] == ['speed', 'conversion']

    def test_delete_item(self, client):
        create_res = client.post('/api/content', json=content_payload('cta', 'Get Started Now'))
        item_id = create_res.get_json()['id']

        res = client.delete(f'/api/content/{item_id}')
        assert res.status_code == 200

        list_res = client.get('/api/content')
        assert len(list_res.get_json()) == 0

    def test_pinned_items_sort_first(self, client):
        client.post('/api/content', json=content_payload('headline', 'Unpinned'))
        res2 = client.post('/api/content', json=content_payload('headline', 'Pinned', is_pinned=True))

        list_res = client.get('/api/content')
        items = list_res.get_json()
        assert items[0]['content'] == 'Pinned'
        assert items[0]['is_pinned'] is True


class TestContentEnhance:
    def test_enhance_content_rejects_empty_content(self, client):
        res = client.post(
            '/api/chat/enhance-content',
            json={'content_type': 'cta', 'content': ''},
            headers=ai_headers(client),
        )
        assert res.status_code == 400
        assert 'slot content' in res.get_json()['error']

    def test_enhance_content_parses_composite_slots_with_fallback(self, client):
        class FailingBackend:
            def generate(self, system_prompt, user_prompt):
                raise RuntimeError('offline')

        with patch('rag.agent.model_backend.ModelBackend', return_value=FailingBackend()):
            res = client.post(
                '/api/chat/enhance-content',
                json={
                    'content_type': 'cta',
                    'content': 'Headline: Launch faster\nParagraph: Build every section once.\nButton: Book a demo',
                },
                headers=ai_headers(client),
            )

        assert res.status_code == 200
        data = res.get_json()
        assert data['content'] == 'Build every section once.'
        assert data['slots']['headline'] == 'Launch faster'
        assert data['slots']['button_label'] == 'Book a demo'


# =============================================================================
# Save From Campaign
# =============================================================================

class TestSaveFromCampaign:
    def _create_campaign_with_messages(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test Campaign'})
        campaign_id = create_res.get_json()['id']

        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [
                {'category': 'headline', 'content': 'Great Headline', 'is_kept': True},
                {'category': 'benefit', 'content': 'Fast delivery', 'is_kept': True},
                {'category': 'cta', 'content': 'Try now', 'is_kept': False},
            ],
        })

        # Mark first two as kept
        msgs_res = client.get(f'/api/campaigns/{campaign_id}/messages')
        msgs = msgs_res.get_json()
        for m in msgs[:2]:
            client.patch(f'/api/campaigns/{campaign_id}/messages/{m["id"]}', json={'is_kept': True})

        return campaign_id

    def test_save_kept_messages(self, client):
        campaign_id = self._create_campaign_with_messages(client)

        res = client.post('/api/content/save-from-campaign', json={
            'campaign_id': campaign_id,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['saved_count'] == 2

        library = client.get('/api/content').get_json()
        assert len(library) == 2
        contents = [i['content'] for i in library]
        assert 'Great Headline' in contents
        assert 'Fast delivery' in contents
        assert all(i['source'] == 'campaign' for i in library)
        assert all(i['status'] == 'approved' for i in library)
        assert all(i['channel'] == 'landing_page' for i in library)
        assert all(i['source_campaign_id'] == campaign_id for i in library)

    def test_save_deduplicates(self, client):
        campaign_id = self._create_campaign_with_messages(client)

        client.post('/api/content/save-from-campaign', json={'campaign_id': campaign_id})
        res2 = client.post('/api/content/save-from-campaign', json={'campaign_id': campaign_id})
        assert res2.get_json()['saved_count'] == 0

    def test_save_without_campaign_id(self, client):
        res = client.post('/api/content/save-from-campaign', json={})
        assert res.status_code == 400


# =============================================================================
# Phase 1: Expanded preset options
# =============================================================================

class TestBrandOptions:
    def test_options_include_expanded_tones(self, client):
        res = client.get('/api/brands/options')
        assert res.status_code == 200
        tones = res.get_json()['tones']
        for tone in ['confident', 'premium', 'empathetic', 'educational', 'energetic',
                     'trustworthy', 'aspirational', 'technical', 'witty', 'calm']:
            assert tone in tones
        # Legacy tones still present
        assert 'professional' in tones and 'warm' in tones

    def test_options_include_expanded_fonts(self, client):
        res = client.get('/api/brands/options')
        fonts = {f['value'] for f in res.get_json()['fonts']}
        for font in ['Geist', 'Work Sans', 'Fraunces', 'Libre Baskerville', 'Rubik']:
            assert font in fonts

    def test_options_include_expanded_themes(self, client):
        res = client.get('/api/brands/options')
        payload = res.get_json()
        themes = {t['value'] for t in payload['themes']}
        for theme in ['clean_b2b_saas', 'conversion_landing_page', 'premium_ecommerce',
                      'fintech_trust', 'technical_docs']:
            assert theme in themes
        assert all(t.get('category') for t in payload['themes'])
        category_keys = {c['key'] for c in payload['theme_categories']}
        assert {'clean_professional', 'premium_editorial', 'soft_wellness',
                'bold_experimental', 'commerce_conversion'}.issubset(category_keys)

    def test_options_include_color_palettes(self, client):
        res = client.get('/api/brands/options')
        assert res.status_code == 200
        palettes = res.get_json()['color_palettes']
        assert palettes
        assert len(palettes) >= 80
        required = {'primary', 'secondary', 'text', 'accent', 'background'}
        assert all(required.issubset((palette.get('colors') or {}).keys()) for palette in palettes)
        assert all(palette.get('category') for palette in palettes)
        assert all(palette.get('theme_keys') for palette in palettes)
        assert all(palette.get('tone_tags') for palette in palettes)

    def test_new_tone_accepted(self, client):
        brand_id = client.post('/api/brands', json={'name': 'Tone Test'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={'tone': 'premium'})
        assert res.status_code == 200
        assert res.get_json()['tone'] == 'premium'

    def test_invalid_tone_still_rejected(self, client):
        brand_id = client.post('/api/brands', json={'name': 'Bad Tone'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={'tone': 'sarcastic'})
        assert res.status_code == 400

    def test_new_theme_accepted(self, client):
        brand_id = client.post('/api/brands', json={'name': 'Theme Test'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={'default_style': 'fintech_trust'})
        assert res.status_code == 200
        assert res.get_json()['default_style'] == 'fintech_trust'

    def test_delete_brand_archives_and_hides_from_default_list(self, brand_app, client):
        create = client.post('/api/brands', json={'name': 'Delete Me', 'is_default': True})
        assert create.status_code == 201
        brand_id = create.get_json()['id']

        res = client.delete(f'/api/brands/{brand_id}')

        assert res.status_code == 200
        assert res.get_json() == {'ok': True}
        with brand_app.app_context():
            brand = Brand.query.get(brand_id)
            assert brand is not None
            assert brand.status == 'archived'
            assert brand.is_default is False

        active = client.get('/api/brands').get_json()
        assert brand_id not in {brand['id'] for brand in active}

        archived = client.get('/api/brands?status=archived').get_json()
        assert brand_id in {brand['id'] for brand in archived}

    def test_new_brand_after_archiving_all_active_brands_becomes_default(self, client):
        old_id = client.post('/api/brands', json={'name': 'Old Active'}).get_json()['id']
        client.delete(f'/api/brands/{old_id}')

        create = client.post('/api/brands', json={'name': 'New Active'})

        assert create.status_code == 201
        assert create.get_json()['is_default'] is True

    def test_create_brand_prepares_site_shell_and_section_style_prompt(self, brand_app, client):
        res = client.post('/api/brands', json={
            'name': 'Campaign Brand',
            'default_style': 'fintech_trust',
            'colors': {'primary': '#101010', 'text': '#222222'},
            'fonts': {'heading': 'Inter', 'body': 'Inter'},
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['site_id']
        assert data['content_wording_prompt']['exists'] is True
        assert data['content_wording_prompt']['metadata']['compiler'] == 'campaign_brand_wording.v1'
        assert data['section_style_prompt']['exists'] is True
        assert data['section_style_prompt']['metadata']['compiler'] == 'campaign_brand_styler.v1'

        with brand_app.app_context():
            brand = Brand.query.get(data['id'])
            site = Site.query.filter_by(brand_id=brand.id).first()
            assert site is not None
            assert brand.content_wording_prompt
            assert brand.section_style_prompt

    def test_create_brand_persists_full_create_editor_payload(self, client):
        res = client.post('/api/brands', json={
            'name': 'Full Payload',
            'tagline': 'One complete brand',
            'description': 'A complete brand description',
            'website_url': 'https://full.example',
            'logo_url': 'https://full.example/logo.png',
            'industry': 'SaaS',
            'tone': 'confident',
            'voice_guidelines': 'Use direct, precise language.',
            'default_style': 'clean_b2b_saas',
            'colors': {
                'primary': '#123456',
                'secondary': '#234567',
                'text': '#345678',
                'accent': '#456789',
                'background': '#f7f7f7',
            },
            'fonts': {'heading': 'Inter', 'body': 'Manrope'},
            'social_links': {'linkedin': 'https://linkedin.com/company/full'},
            'strategy': {
                'target_audience': 'Marketing teams',
                'brand_promise': 'Faster campaign creation',
                'positioning_statement': 'For marketers, Full Payload is the campaign builder.',
                'compliance_notes': 'Avoid revenue guarantees.',
                'image_style': 'Clean product UI',
                'cta_style': 'Action-first',
                'primary_market': 'United States',
                'locale': 'en-US',
                'differentiators': ['Fast', 'Brand-safe'],
                'forbidden_claims': ['Guaranteed revenue'],
                'required_claims': ['Human review available'],
                'voice_examples': ['Ship faster with brand-safe AI.'],
                'voice_anti_examples': ['Crush it with magic.'],
                'competitors': ['Generic Builder'],
            },
        })

        assert res.status_code == 201
        data = res.get_json()
        assert data['description'] == 'A complete brand description'
        assert data['website_url'] == 'https://full.example'
        assert data['voice_guidelines'] == 'Use direct, precise language.'
        assert data['colors']['primary'] == '#123456'
        assert data['fonts']['body'] == 'Manrope'
        assert data['social_links']['linkedin'] == 'https://linkedin.com/company/full'
        assert data['strategy']['differentiators'] == ['Fast', 'Brand-safe']
        assert data['strategy']['required_claims'] == ['Human review available']

        with client.application.app_context():
            brand = Brand.query.get(data['id'])
            context = brand.to_generation_context()
            assert context['social_links']['linkedin'] == 'https://linkedin.com/company/full'
            assert context['target_audience'] == 'Marketing teams'
            assert context['required_claims'] == ['Human review available']

    def test_create_brand_stores_social_links_and_footer_section(self, brand_app, client):
        res = client.post('/api/brands', json={
            'name': 'Social Brand',
            'tagline': 'Find us everywhere',
            'website_url': 'https://social.example',
            'social_links': {
                'instagram': 'https://instagram.com/socialbrand',
                'linkedin': 'https://linkedin.com/company/socialbrand',
                'unknown': 'https://example.com/ignored',
            },
        })

        assert res.status_code == 201
        data = res.get_json()
        assert data['social_links'] == {
            'instagram': 'https://instagram.com/socialbrand',
            'linkedin': 'https://linkedin.com/company/socialbrand',
        }

        with brand_app.app_context():
            brand = Brand.query.filter_by(name='Social Brand').first()
            footer_section = SectionItem.query.filter_by(
                brand_id=brand.id,
                section_type='footer',
            ).first()
            assert footer_section is not None
            assert footer_section.status == 'active'
            assert 'Social Brand' in footer_section.yaml_content
            assert 'https://instagram.com/socialbrand' in footer_section.yaml_content
            assert footer_section.get_generation_metadata()['compiler'] == 'brand_footer_section.v1'

            site = Site.query.filter_by(brand_id=brand.id).first()
            footer_block = SiteSharedBlock.query.filter_by(site_id=site.id, key='footer').first()
            assert footer_block is not None
            assert 'https://linkedin.com/company/socialbrand' in footer_block.yaml_content

    def test_update_brand_refreshes_footer_section_social_links(self, brand_app, client):
        create = client.post('/api/brands', json={
            'name': 'Refresh Footer',
            'social_links': {'instagram': 'https://instagram.com/original'},
        })
        brand_id = create.get_json()['id']

        res = client.patch(f'/api/brands/{brand_id}', json={
            'social_links': {'youtube': 'https://youtube.com/@refresh'},
        })

        assert res.status_code == 200
        assert res.get_json()['social_links'] == {'youtube': 'https://youtube.com/@refresh'}
        with brand_app.app_context():
            footer_sections = SectionItem.query.filter_by(
                brand_id=brand_id,
                section_type='footer',
            ).all()
            assert len(footer_sections) == 1
            assert 'https://youtube.com/@refresh' in footer_sections[0].yaml_content
            assert 'https://instagram.com/original' not in footer_sections[0].yaml_content

    def test_brand_site_preview_renders_header_and_footer(self, brand_app, client):
        create = client.post('/api/brands', json={
            'name': 'Preview Brand',
            'tagline': 'Preview footer text',
            'social_links': {'x': 'https://x.com/previewbrand'},
        })
        brand_id = create.get_json()['id']

        with brand_app.app_context():
            site = Site.query.filter_by(brand_id=brand_id).first()
            page = next(page for page in site.source_pages if page.is_homepage)
            page.body_yaml_content = ''
            db.session.commit()

        res = client.get(f'/api/brands/{brand_id}/site/preview')

        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert 'Preview Brand' in html
        assert 'Preview footer text' in html
        assert 'https://x.com/previewbrand' in html

    def test_update_style_field_regenerates_section_style_prompt(self, client, monkeypatch):
        calls = []

        def fake_prompt(brand, site_shell_config=None, org_id=None, content_wording_prompt=None):
            calls.append((brand.default_style, (site_shell_config or {}).get('site_id'), content_wording_prompt))
            return f"Prompt for {brand.name}: {brand.default_style}", {
                'compiler': 'campaign_brand_styler.v1',
                'style': brand.default_style,
            }

        monkeypatch.setattr('campaign.section_rag.generate_brand_section_style_prompt', fake_prompt)
        brand_id = client.post('/api/brands', json={'name': 'Style Regen', 'default_style': 'fintech_trust'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={'default_style': 'technical_docs'})
        assert res.status_code == 200
        assert len(calls) == 2
        assert calls[-1][0] == 'technical_docs'
        assert calls[-1][2]
        assert res.get_json()['section_style_prompt']['metadata']['style'] == 'technical_docs'

    def test_update_any_brand_field_regenerates_section_style_prompt(self, client, monkeypatch):
        calls = []

        def fake_prompt(brand, site_shell_config=None, org_id=None, content_wording_prompt=None):
            calls.append((brand.name, brand.tagline, (site_shell_config or {}).get('site_id'), content_wording_prompt))
            return f"Prompt for {brand.name}: {brand.tagline}", {
                'compiler': 'campaign_brand_styler.v1',
                'tagline': brand.tagline,
            }

        monkeypatch.setattr('campaign.section_rag.generate_brand_section_style_prompt', fake_prompt)
        brand_id = client.post('/api/brands', json={'name': 'Every Save', 'tagline': 'Original'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={'tagline': 'Updated'})
        assert res.status_code == 200
        assert len(calls) == 2
        assert calls[-1][1] == 'Updated'
        assert calls[-1][3]
        assert res.get_json()['section_style_prompt']['metadata']['tagline'] == 'Updated'


# =============================================================================
# Phase 2: Brand strategy fields
# =============================================================================

class TestBrandStrategy:
    def test_strategy_persists_via_nested_object(self, client):
        brand_id = client.post('/api/brands', json={'name': 'Strategy Co'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={
            'strategy': {
                'target_audience': 'Marketing managers at SaaS companies',
                'brand_promise': 'Ship campaigns in minutes',
                'differentiators': ['AI-first', 'No code', 'Brand-safe'],
                'forbidden_words': ['cheap', 'guru'],
                'required_claims': ['GDPR compliant'],
                'compliance_notes': 'Never promise specific revenue numbers.',
                'primary_market': 'United States',
                'locale': 'en-US',
            },
        })
        assert res.status_code == 200
        strategy = res.get_json()['strategy']
        assert strategy['target_audience'] == 'Marketing managers at SaaS companies'
        assert strategy['brand_promise'] == 'Ship campaigns in minutes'
        assert strategy['differentiators'] == ['AI-first', 'No code', 'Brand-safe']
        assert strategy['forbidden_words'] == ['cheap', 'guru']
        assert strategy['required_claims'] == ['GDPR compliant']
        assert strategy['compliance_notes'] == 'Never promise specific revenue numbers.'
        assert strategy['primary_market'] == 'United States'
        assert strategy['locale'] == 'en-US'

    def test_strategy_persists_across_reload(self, client):
        brand_id = client.post('/api/brands', json={'name': 'Reload Co'}).get_json()['id']
        client.patch(f'/api/brands/{brand_id}', json={
            'strategy': {'differentiators': ['Speed', 'Trust']},
        })
        # Fetch fresh
        listed = client.get('/api/brands').get_json()
        brand = next(b for b in listed if b['id'] == brand_id)
        assert brand['strategy']['differentiators'] == ['Speed', 'Trust']

    def test_strategy_accepts_comma_separated_string(self, client):
        brand_id = client.post('/api/brands', json={'name': 'CSV Co'}).get_json()['id']
        res = client.patch(f'/api/brands/{brand_id}', json={
            'strategy': {'forbidden_words': 'cheap, spammy\nguru'},
        })
        assert res.status_code == 200
        assert set(res.get_json()['strategy']['forbidden_words']) == {'cheap', 'spammy', 'guru'}

    def test_strategy_in_generation_context(self, brand_app):
        with brand_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            brand = Brand(org_id=org.id, name='Ctx Co', slug='ctx-co')
            brand.target_audience = 'Founders'
            brand.brand_promise = 'Launch faster'
            brand.set_strategy_list('differentiators', ['AI-first', 'No code'])
            brand.set_strategy_list('forbidden_claims', ['#1 in the world'])
            brand.set_strategy_list('voice_examples', ['Clear, calm, confident.'])
            brand.compliance_notes = 'No medical claims.'
            db.session.add(brand)
            db.session.commit()

            ctx = brand.to_generation_context()
            assert ctx['target_audience'] == 'Founders'
            assert ctx['brand_promise'] == 'Launch faster'
            assert ctx['differentiators'] == ['AI-first', 'No code']
            assert ctx['forbidden_claims'] == ['#1 in the world']
            assert ctx['voice_examples'] == ['Clear, calm, confident.']
            assert ctx['compliance_notes'] == 'No medical claims.'

    def test_brand_guidance_block_built(self, brand_app):
        from campaign.compiler import _build_brand_guidance
        gen_ctx = {
            'tone': 'confident',
            'target_audience': 'Founders',
            'forbidden_words': ['cheap', 'guru'],
            'compliance_notes': 'No medical claims.',
            'voice_examples': ['Clear and direct.'],
        }
        guidance = _build_brand_guidance(gen_ctx)
        assert 'Brand guidelines' in guidance
        assert 'Founders' in guidance
        assert 'cheap' in guidance
        assert 'No medical claims' in guidance
        assert 'Clear and direct' in guidance

    def test_brand_guidance_empty_when_no_context(self, brand_app):
        from campaign.compiler import _build_brand_guidance
        assert _build_brand_guidance({}) == ''


# =============================================================================
# Brand field AI enhancement
# =============================================================================

class TestBrandAiEnhance:
    def test_enhance_rejects_manual_call(self, client):
        res = client.post('/api/chat/enhance', json={
            'section_type': 'brand',
            'target_field': 'tagline',
            'current_content': {'name': 'Acme', 'industry': 'SaaS'},
        })
        assert res.status_code == 403

    def test_enhance_brand_field_uses_fallback_when_ai_unavailable(self, client):
        with patch('rag.agent.model_backend.ModelBackend.generate', side_effect=RuntimeError('offline')):
            res = client.post('/api/chat/enhance', json={
                'business_name': 'Acme CMS',
                'industry': 'SaaS',
                'description': 'Marketing CMS for campaign sites',
                'section_type': 'brand',
                'target_field': 'tagline',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'target_audience': 'B2B marketers',
                    'brand_promise': 'launch campaign sites faster',
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'fallback'
        assert data['enhanced_fields']['tagline']

    def test_enhance_brand_choice_returns_valid_tone(self, client):
        with patch('rag.agent.model_backend.ModelBackend.generate', return_value='{"tone": "trustworthy"}'):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'tone',
                'current_content': {'name': 'FinCo', 'industry': 'finance'},
            }, headers=ai_headers(client))

        assert res.status_code == 200
        assert res.get_json()['enhanced_fields']['tone'] in Brand.VALID_TONES

    def test_enhance_brand_prompt_includes_target_value(self, client):
        captured = {}

        def fake_generate(system_prompt, user_prompt):
            captured['system_prompt'] = system_prompt
            captured['user_prompt'] = user_prompt
            return '{"brand_promise": "Launch campaign sites faster without drifting from brand rules."}'

        with patch('rag.agent.model_backend.ModelBackend.generate', side_effect=fake_generate):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'brand_promise',
                'target_value': 'Launch sites faster',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'brand_promise': 'Launch sites faster',
                    'full': {
                        'name': 'Acme CMS',
                        'strategy': {'target_audience': 'B2B marketers'},
                    },
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        assert res.get_json()['source'] == 'ai'
        assert 'Current target field value (primary): Launch sites faster' in captured['user_prompt']
        assert 'Supporting brand context (secondary)' in captured['user_prompt']
        assert 'Full editor payload' in captured['user_prompt']

    def test_enhance_brand_voice_guidelines_with_ai(self, client):
        with patch(
            'rag.agent.model_backend.ModelBackend.generate',
            return_value='{"voice_guidelines": "Use direct, calm language. Avoid hype and unsupported claims."}',
        ):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'voice_guidelines',
                'target_value': 'Be clear and direct.',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'tone': 'confident',
                    'target_audience': 'B2B marketers',
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'ai'
        assert data['enhanced_fields']['voice_guidelines'].startswith('Use direct')

    def test_enhance_brand_description_with_ai(self, client):
        with patch(
            'rag.agent.model_backend.ModelBackend.generate',
            return_value='{"description": "Acme CMS helps B2B marketing teams plan content and launch campaign sites from approved brand assets."}',
        ):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'description',
                'target_value': 'Campaign site CMS for marketers.',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'target_audience': 'B2B marketers',
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'ai'
        assert 'B2B marketing teams' in data['enhanced_fields']['description']

    def test_enhance_brand_voice_guidelines_fallback_is_useful(self, client):
        with patch('rag.agent.model_backend.ModelBackend.generate', side_effect=RuntimeError('offline')):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'voice_guidelines',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'tone': 'confident',
                    'target_audience': 'B2B marketers',
                    'forbidden_claims': ['Do not promise revenue lift'],
                    'required_claims': ['Use approved proof points'],
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'fallback'
        value = data['enhanced_fields']['voice_guidelines']
        assert 'confident voice' in value
        assert 'Do not invent proof' in value

    def test_enhance_brand_description_fallback_is_useful(self, client):
        with patch('rag.agent.model_backend.ModelBackend.generate', side_effect=RuntimeError('offline')):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'brand',
                'target_field': 'description',
                'current_content': {
                    'name': 'Acme CMS',
                    'industry': 'SaaS',
                    'tagline': 'Campaign sites, ready faster.',
                    'target_audience': 'B2B marketers',
                    'brand_promise': 'launch campaign sites faster',
                },
            }, headers=ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'fallback'
        value = data['enhanced_fields']['description']
        assert 'Acme CMS' in value
        assert 'B2B marketers' in value

    def test_frontend_brand_ai_fields_are_backend_supported(self, brand_app):
        from routes.chat import BRAND_ENHANCE_FIELDS

        js_path = pathlib.Path(brand_app.root_path) / 'static' / 'js' / 'dashboard-v2.js'
        js = js_path.read_text(encoding='utf-8')
        frontend_fields = set(re.findall(r"\{ key: '([^']+)', id: 'brand", js))

        assert frontend_fields
        assert frontend_fields.issubset(set(BRAND_ENHANCE_FIELDS))
        assert not {'name', 'tagline', 'industry', 'tone', 'default_style'} & frontend_fields
        assert 'voice_guidelines' in frontend_fields

    def test_frontend_brand_create_uses_ai_preparation_loading_state(self, brand_app):
        js_path = pathlib.Path(brand_app.root_path) / 'static' / 'js' / 'dashboard-v2.js'
        js = js_path.read_text(encoding='utf-8')

        assert 'Enhancing brand with AI...' in js
        assert 'Creating your brand shell and AI prompt context. This can take a moment.' in js
        assert 'setAiGeneratingState({' in js
        assert "#dashBrandEditorView input, #dashBrandEditorView select, #dashBrandEditorView textarea" in js
        assert "confirmBtn.textContent = 'Creating...'" not in js

    def test_enhance_brand_invalid_field_rejected(self, client):
        res = client.post('/api/chat/enhance', json={
            'section_type': 'brand',
            'target_field': 'api_key',
            'current_content': {'name': 'Acme'},
        }, headers=ai_headers(client))
        assert res.status_code == 400


class TestBrandStrategySuggestion:
    def test_suggest_strategy_returns_structured_fields_without_persisting(self, client):
        raw = '''
        {
          "voice_guidelines": "Clear, practical, and specific. Avoid hype.",
          "strategy": {
            "target_audience": "Marketing teams at B2B SaaS companies",
            "brand_promise": "Launch on-brand campaign sites faster",
            "positioning_statement": "For B2B marketers, Acme is the campaign CMS that keeps content and sites aligned.",
            "differentiators": ["Reusable brand prompts", "Renderer-ready sections"],
            "voice_examples": ["Launch a polished campaign page from approved content"],
            "voice_anti_examples": ["Guaranteed growth overnight"],
            "forbidden_words": ["guaranteed"],
            "forbidden_claims": ["Do not promise revenue lift"],
            "required_claims": ["Use approved proof points only"],
            "compliance_notes": "Do not invent compliance status.",
            "image_style": "Clean product visuals with real UI context.",
            "cta_style": "Action-first and specific.",
            "primary_market": "United States",
            "locale": "en-US",
            "competitors": ["Generic page builders"]
          }
        }
        '''
        with patch('rag.agent.model_backend.ModelBackend.generate', return_value=raw):
            res = client.post('/api/brands/suggest-strategy', json={
                'name': 'Acme',
                'tagline': 'Campaign sites faster',
                'industry': 'SaaS',
                'tone': 'confident',
                'colors': {'primary': '#111111', 'background': '#ffffff'},
                'fonts': {'heading': 'Inter', 'body': 'Inter'},
                'social_links': {'linkedin': 'https://linkedin.com/company/acme'},
            })

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'ai'
        assert data['voice_guidelines'] == 'Clear, practical, and specific. Avoid hype.'
        assert data['strategy']['target_audience'] == 'Marketing teams at B2B SaaS companies'
        assert data['strategy']['differentiators'] == ['Reusable brand prompts', 'Renderer-ready sections']

        with client.application.app_context():
            assert Brand.query.filter_by(name='Acme').first() is None

    def test_suggest_strategy_fails_without_fallback_when_ai_unavailable(self, client):
        with patch('rag.agent.model_backend.ModelBackend.generate', side_effect=RuntimeError('offline')):
            res = client.post('/api/brands/suggest-strategy', json={
                'name': 'Acme',
                'industry': 'SaaS',
            })

        assert res.status_code == 502
        assert 'Brand strategy suggestion failed' in res.get_json()['error']
