"""Tests for Campaign CRUD API and compiler."""
import json
import pytest
from unittest.mock import patch, MagicMock
from extensions import db
from models import (
    Campaign, CampaignBrief, CampaignOffer, CampaignMessage, Organization,
    Site, SitePage,
)


@pytest.fixture
def campaign_app(tmp_path):
    """Create app with a fresh temporary database for campaign tests."""
    db_path = str(tmp_path / 'test_campaign.db')
    db_uri = 'sqlite:///' + db_path

    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True

    yield app


@pytest.fixture
def client(campaign_app):
    return campaign_app.test_client()


@pytest.fixture
def org_id(campaign_app):
    with campaign_app.app_context():
        org = Organization.query.filter_by(slug='default').first()
        return org.id


# =============================================================================
# Campaign CRUD
# =============================================================================

class TestCreateCampaign:
    def test_create_requires_name(self, client):
        # Name is required up front (for reporting/analytics) — no silent default.
        res = client.post('/api/campaigns', json={})
        assert res.status_code == 400
        assert 'name' in res.get_json()['error'].lower()

    def test_create_blank_name_rejected(self, client):
        res = client.post('/api/campaigns', json={'name': '   '})
        assert res.status_code == 400

    def test_create_minimal(self, client):
        res = client.post('/api/campaigns', json={'name': 'My Campaign'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['name'] == 'My Campaign'
        assert data['status'] == 'draft'
        assert data['goal'] is None
        assert data['brief'] is not None
        assert data['offer'] is not None
        assert data['messages'] == []

    def test_create_with_name_and_goal(self, client):
        res = client.post('/api/campaigns', json={
            'name': 'Summer Sale',
            'goal': 'sales',
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['name'] == 'Summer Sale'
        assert data['goal'] == 'sales'

    def test_create_with_brief(self, client):
        res = client.post('/api/campaigns', json={
            'name': 'Yoga Studio Launch',
            'goal': 'leads',
            'brief': {
                'product_or_service': 'Hot yoga classes',
                'target_audience': 'Health-conscious professionals',
            },
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data['brief']['product_or_service'] == 'Hot yoga classes'
        assert data['brief']['target_audience'] == 'Health-conscious professionals'

    def test_create_invalid_goal(self, client):
        res = client.post('/api/campaigns', json={'name': 'X', 'goal': 'invalid'})
        assert res.status_code == 400
        assert 'Invalid goal' in res.get_json()['error']


class TestCampaignTargeting:
    def _make_products(self, client, n=2):
        ids = []
        for i in range(n):
            r = client.post('/api/products', json={'name': f'Product {i}'})
            assert r.status_code in (200, 201)
            ids.append(r.get_json()['id'])
        return ids

    def test_generic_campaign_has_no_products(self, client):
        res = client.post('/api/campaigns', json={'name': 'Generic Push'})
        assert res.status_code == 201
        assert res.get_json()['product_ids'] == []

    def test_create_targets_products(self, client):
        pids = self._make_products(client, 2)
        res = client.post('/api/campaigns', json={
            'name': 'Targeted Push', 'product_ids': pids,
        })
        assert res.status_code == 201
        data = res.get_json()
        assert set(data['product_ids']) == set(pids)
        assert len(data['products']) == 2

    def test_patch_updates_targeting(self, client):
        pids = self._make_products(client, 2)
        cid = client.post('/api/campaigns', json={'name': 'C'}).get_json()['id']
        # add both
        client.patch(f'/api/campaigns/{cid}', json={'product_ids': pids})
        got = client.get(f'/api/campaigns/{cid}').get_json()
        assert set(got['product_ids']) == set(pids)
        # back to generic (empty)
        client.patch(f'/api/campaigns/{cid}', json={'product_ids': []})
        got = client.get(f'/api/campaigns/{cid}').get_json()
        assert got['product_ids'] == []

    def test_invalid_product_id_rejected(self, client):
        res = client.post('/api/campaigns', json={
            'name': 'Bad', 'product_ids': ['nonexistent-id'],
        })
        assert res.status_code == 400


class TestListCampaigns:
    def test_list_empty(self, client):
        res = client.get('/api/campaigns')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_list_with_campaigns(self, client):
        client.post('/api/campaigns', json={'name': 'A'})
        client.post('/api/campaigns', json={'name': 'B'})
        res = client.get('/api/campaigns')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 2

    def test_list_filter_by_status(self, client):
        r1 = client.post('/api/campaigns', json={'name': 'Draft'})
        campaign_id = r1.get_json()['id']
        client.patch(f'/api/campaigns/{campaign_id}', json={'status': 'active'})

        client.post('/api/campaigns', json={'name': 'Still Draft'})

        res = client.get('/api/campaigns?status=active')
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Draft'


class TestGetCampaign:
    def test_get_full(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.get(f'/api/campaigns/{campaign_id}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['name'] == 'Test'
        assert 'brief' in data
        assert 'offer' in data
        assert 'messages' in data

    def test_get_nonexistent(self, client):
        res = client.get('/api/campaigns/nonexistent-id')
        assert res.status_code == 404


class TestUpdateCampaign:
    def test_update_name(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Old'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}', json={'name': 'New'})
        assert res.status_code == 200

        get_res = client.get(f'/api/campaigns/{campaign_id}')
        assert get_res.get_json()['name'] == 'New'

    def test_update_status(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}', json={'status': 'active'})
        assert res.status_code == 200

        get_res = client.get(f'/api/campaigns/{campaign_id}')
        assert get_res.get_json()['status'] == 'active'

    def test_update_invalid_status(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}', json={'status': 'bogus'})
        assert res.status_code == 400

    def test_update_empty_name_rejected(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}', json={'name': ''})
        assert res.status_code == 400


class TestDeleteCampaign:
    def test_delete(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Doomed'})
        campaign_id = create_res.get_json()['id']

        res = client.delete(f'/api/campaigns/{campaign_id}')
        assert res.status_code == 200

        get_res = client.get(f'/api/campaigns/{campaign_id}')
        assert get_res.status_code == 404

    def test_delete_nonexistent(self, client):
        res = client.delete('/api/campaigns/no-such-id')
        assert res.status_code == 404


# =============================================================================
# Brief
# =============================================================================

class TestBrief:
    def test_update_brief(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/brief', json={
            'product_or_service': 'Web design services',
            'target_audience': 'Small business owners',
            'awareness_level': 'problem_aware',
            'buying_stage': 'consideration',
        })
        assert res.status_code == 200
        brief = res.get_json()['brief']
        assert brief['product_or_service'] == 'Web design services'
        assert brief['awareness_level'] == 'problem_aware'
        assert brief['buying_stage'] == 'consideration'

    def test_invalid_awareness_level(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/brief', json={
            'awareness_level': 'super_aware',
        })
        assert res.status_code == 400

    def test_invalid_buying_stage(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/brief', json={
            'buying_stage': 'panic',
        })
        assert res.status_code == 400


# =============================================================================
# Offer
# =============================================================================

class TestOffer:
    def test_update_offer_text_fields(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'offer': '50% off first month',
            'primary_cta': 'Start Free Trial',
            'secondary_cta': 'Learn More',
        })
        assert res.status_code == 200
        offer = res.get_json()['offer']
        assert offer['offer'] == '50% off first month'
        assert offer['primary_cta'] == 'Start Free Trial'

    def test_update_offer_arrays(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'benefits': ['Fast delivery', 'Free returns', '24/7 support'],
            'proof_points': ['10k+ customers', '4.9 star rating'],
            'objections': ['Too expensive', 'Not sure it works'],
            'faqs': [
                {'question': 'How long?', 'answer': '3-5 days'},
                {'question': 'Refund?', 'answer': '30-day guarantee'},
            ],
        })
        assert res.status_code == 200
        offer = res.get_json()['offer']
        assert offer['benefits'] == ['Fast delivery', 'Free returns', '24/7 support']
        assert len(offer['faqs']) == 2
        assert offer['faqs'][0]['question'] == 'How long?'

    def test_invalid_benefits_type(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'benefits': 'not an array',
        })
        assert res.status_code == 400

    def test_invalid_faq_structure(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'faqs': [{'only_question': 'missing answer'}],
        })
        assert res.status_code == 400


# =============================================================================
# Messages
# =============================================================================

class TestMessages:
    def test_add_single_message(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'headline',
            'content': 'Transform Your Business Today',
        })
        assert res.status_code == 201
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['category'] == 'headline'
        assert data[0]['content'] == 'Transform Your Business Today'
        assert data[0]['is_kept'] is False

    def test_add_multiple_messages(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [
                {'category': 'headline', 'content': 'Headline 1'},
                {'category': 'headline', 'content': 'Headline 2'},
                {'category': 'benefit', 'content': 'Save time'},
            ],
        })
        assert res.status_code == 201
        data = res.get_json()
        assert len(data) == 3

    def test_add_message_invalid_category(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'invalid_cat',
            'content': 'Some text',
        })
        assert res.status_code == 400

    def test_add_message_empty_content(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'headline',
            'content': '',
        })
        assert res.status_code == 400

    def test_update_message(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        add_res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'headline',
            'content': 'Original',
        })
        msg_id = add_res.get_json()[0]['id']

        res = client.patch(f'/api/campaigns/{campaign_id}/messages/{msg_id}', json={
            'content': 'Updated',
            'is_kept': True,
        })
        assert res.status_code == 200
        assert res.get_json()['content'] == 'Updated'
        assert res.get_json()['is_kept'] is True

    def test_delete_message(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        add_res = client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'headline',
            'content': 'To delete',
        })
        msg_id = add_res.get_json()[0]['id']

        res = client.delete(f'/api/campaigns/{campaign_id}/messages/{msg_id}')
        assert res.status_code == 200

        list_res = client.get(f'/api/campaigns/{campaign_id}/messages')
        assert len(list_res.get_json()) == 0

    def test_list_messages_filter_by_category(self, client):
        create_res = client.post('/api/campaigns', json={'name': 'Test'})
        campaign_id = create_res.get_json()['id']

        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [
                {'category': 'headline', 'content': 'H1'},
                {'category': 'benefit', 'content': 'B1'},
                {'category': 'headline', 'content': 'H2'},
            ],
        })

        res = client.get(f'/api/campaigns/{campaign_id}/messages?category=headline')
        data = res.get_json()
        assert len(data) == 2
        assert all(m['category'] == 'headline' for m in data)


# =============================================================================
# Compiler
# =============================================================================

class TestCompiler:
    def _setup_full_campaign(self, client):
        """Create a campaign with brief, offer, and messages populated."""
        create_res = client.post('/api/campaigns', json={
            'name': 'Full Campaign',
            'goal': 'leads',
            'brief': {
                'product_or_service': 'AI Writing Tool',
                'description': 'An AI tool that writes marketing copy',
                'target_audience': 'Marketing managers',
            },
        })
        campaign_id = create_res.get_json()['id']

        client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'offer': 'Free 14-day trial',
            'primary_cta': 'Start Writing Free',
            'secondary_cta': 'See Examples',
            'benefits': ['Save 10 hours/week', 'Better conversion rates', 'Brand-consistent copy'],
            'proof_points': ['500+ companies trust us', '4.8/5 on G2'],
            'faqs': [
                {'question': 'Is it free?', 'answer': 'Yes, 14-day trial with no credit card.'},
            ],
        })

        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [
                {'category': 'headline', 'content': 'Write Better Copy in Half the Time'},
                {'category': 'headline', 'content': 'AI-Powered Marketing Copy That Converts'},
                {'category': 'benefit', 'content': 'Generate weeks of content in minutes'},
                {'category': 'testimonial', 'content': 'Cut our content production time by 60%'},
            ],
        })

        return campaign_id

    def test_compile_returns_sections(self, client):
        campaign_id = self._setup_full_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        assert res.status_code == 200
        data = res.get_json()

        assert 'sections' in data
        assert 'theme_hint' in data
        assert 'metadata' in data
        assert len(data['sections']) == 8
        assert data['metadata']['campaign_id'] == campaign_id
        assert data['metadata']['goal'] == 'leads'

    def test_compile_hero_section(self, client):
        campaign_id = self._setup_full_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        sections = res.get_json()['sections']
        hero = sections[0]

        assert hero['type'] == 'hero'
        assert hero['business_content']['headline'] == 'Write Better Copy in Half the Time'
        assert hero['business_content']['cta_text'] == 'Start Writing Free'
        assert hero['business_content']['product_name'] == 'AI Writing Tool'

    def test_compile_benefits_section(self, client):
        campaign_id = self._setup_full_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        sections = res.get_json()['sections']
        benefits = sections[2]

        assert benefits['type'] == 'features'
        assert 'Save 10 hours/week' in benefits['business_content']['benefits']
        assert 'Generate weeks of content in minutes' in benefits['business_content']['benefit_messages']

    def test_compile_faq_section(self, client):
        campaign_id = self._setup_full_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        sections = res.get_json()['sections']
        faq = sections[6]

        assert faq['type'] == 'faq'
        assert len(faq['business_content']['faqs']) == 1
        assert faq['business_content']['faqs'][0]['question'] == 'Is it free?'

    def test_compile_without_offer_fails(self, client, campaign_app):
        create_res = client.post('/api/campaigns', json={'name': 'Empty'})
        campaign_id = create_res.get_json()['id']

        with campaign_app.app_context():
            campaign = Campaign.query.get(campaign_id)
            if campaign.offer:
                db.session.delete(campaign.offer)
                db.session.commit()

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        assert res.status_code == 400
        assert 'offer is required' in res.get_json()['error']

    def test_compile_theme_hint(self, client):
        campaign_id = self._setup_full_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/compile')
        assert 'trust' in res.get_json()['theme_hint']


# =============================================================================
# Cascade Delete
# =============================================================================

class TestCascadeDelete:
    def test_delete_removes_brief_offer_messages(self, client, campaign_app):
        create_res = client.post('/api/campaigns', json={'name': 'Cascade Test'})
        campaign_id = create_res.get_json()['id']

        client.patch(f'/api/campaigns/{campaign_id}/brief', json={
            'product_or_service': 'Test product',
        })
        client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'offer': 'Test offer',
        })
        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'category': 'headline',
            'content': 'Test headline',
        })

        client.delete(f'/api/campaigns/{campaign_id}')

        with campaign_app.app_context():
            assert Campaign.query.get(campaign_id) is None
            assert CampaignBrief.query.filter_by(campaign_id=campaign_id).first() is None
            assert CampaignOffer.query.filter_by(campaign_id=campaign_id).first() is None
            assert CampaignMessage.query.filter_by(campaign_id=campaign_id).count() == 0


# =============================================================================
# Landing Page Generation
# =============================================================================

class TestGeneratePage:
    def _setup_campaign(self, client):
        """Create a fully populated campaign ready for generation."""
        create_res = client.post('/api/campaigns', json={
            'name': 'AI Writing Tool Launch',
            'goal': 'leads',
            'brief': {
                'product_or_service': 'AI Writing Tool',
                'description': 'An AI-powered tool that writes marketing copy',
                'target_audience': 'Marketing managers at SaaS companies',
            },
        })
        campaign_id = create_res.get_json()['id']

        client.patch(f'/api/campaigns/{campaign_id}/offer', json={
            'offer': 'Free 14-day trial',
            'primary_cta': 'Start Writing Free',
            'benefits': ['Save 10 hours/week', 'Better conversion rates'],
            'proof_points': ['500+ companies trust us'],
            'faqs': [{'question': 'Is it free?', 'answer': 'Yes, 14-day free trial.'}],
        })

        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [
                {'category': 'headline', 'content': 'Write Better Copy in Half the Time'},
                {'category': 'benefit', 'content': 'Generate weeks of content in minutes'},
            ],
        })

        return campaign_id

    @patch('llm_service.get_llm_service')
    def test_generate_page_creates_site(self, mock_get_llm, client, campaign_app):
        """Generate page should create a site and page linked to the campaign."""
        mock_service = MagicMock()
        mock_service.chat.return_value = {
            'response': '<!-- ACTION: create -->',
            'yaml': '- name: site\n  components:\n    - name: page\n      components: []\n',
            'action': 'create',
        }
        mock_get_llm.return_value = mock_service

        campaign_id = self._setup_campaign(client)

        res = client.post(f'/api/campaigns/{campaign_id}/generate-page')
        assert res.status_code == 200
        data = res.get_json()
        assert data['ok'] is True
        assert data['site_id'] is not None
        assert data['page_id'] is not None
        assert data['yaml'] is not None

        # Verify campaign is now linked to site
        get_res = client.get(f'/api/campaigns/{campaign_id}')
        assert get_res.get_json()['site_id'] == data['site_id']

    @patch('llm_service.get_llm_service')
    def test_generate_page_updates_existing(self, mock_get_llm, client, campaign_app):
        """Second generation should update the same site/page."""
        mock_service = MagicMock()
        mock_service.chat.return_value = {
            'response': '<!-- ACTION: create -->',
            'yaml': '- name: site\n  components:\n    - name: page\n      components: []\n',
            'action': 'create',
        }
        mock_get_llm.return_value = mock_service

        campaign_id = self._setup_campaign(client)

        res1 = client.post(f'/api/campaigns/{campaign_id}/generate-page')
        site_id_1 = res1.get_json()['site_id']

        res2 = client.post(f'/api/campaigns/{campaign_id}/generate-page')
        site_id_2 = res2.get_json()['site_id']

        assert site_id_1 == site_id_2

    def test_generate_page_without_offer_fails(self, client, campaign_app):
        """Cannot generate without offer data."""
        create_res = client.post('/api/campaigns', json={'name': 'Empty'})
        campaign_id = create_res.get_json()['id']

        with campaign_app.app_context():
            campaign = Campaign.query.get(campaign_id)
            if campaign.offer:
                db.session.delete(campaign.offer)
                db.session.commit()

        res = client.post(f'/api/campaigns/{campaign_id}/generate-page')
        assert res.status_code == 400
        assert 'offer is required' in res.get_json()['error']

    def test_preview_without_site_returns_404(self, client):
        """Preview should return 404 if no page generated yet."""
        create_res = client.post('/api/campaigns', json={'name': 'No Site'})
        campaign_id = create_res.get_json()['id']

        res = client.get(f'/api/campaigns/{campaign_id}/preview')
        assert res.status_code == 404


class TestCompileToBusinessContext:
    def test_produces_valid_business_context(self, campaign_app):
        """The compiler should produce business_context matching guided flow format."""
        from campaign.compiler import compile_to_business_context

        with campaign_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            campaign = Campaign(org_id=org.id, name='Test', goal='leads')
            db.session.add(campaign)
            db.session.flush()

            brief = CampaignBrief(
                campaign_id=campaign.id,
                product_or_service='Yoga Classes',
                description='Hot yoga for beginners',
                target_audience='Health-conscious adults',
            )
            db.session.add(brief)

            offer = CampaignOffer(campaign_id=campaign.id)
            offer.offer = 'First class free'
            offer.primary_cta = 'Book Now'
            offer.set_benefits(['Stress relief', 'Better flexibility'])
            offer.set_faqs([{'question': 'What to bring?', 'answer': 'Just yourself'}])
            db.session.add(offer)

            msg = CampaignMessage(
                campaign_id=campaign.id,
                category='headline',
                content='Transform Your Body',
                sort_order=0,
            )
            db.session.add(msg)
            db.session.commit()

            bc = compile_to_business_context(campaign)

            assert bc['business_name'] == 'Test'
            assert bc['description'] == 'Hot yoga for beginners'
            assert bc['style_preference'] == 'modern_minimalist'
            assert isinstance(bc['sections'], list)
            assert len(bc['sections']) >= 1

            # Phase C: sections are now recipe-driven ("recipes select, RAG fills").
            # A recipe is selected and explained, the campaign goal becomes a
            # builder conversion_intent (Phase C2), and the hero resolves its
            # content from the campaign's typed content via content_refs.
            assert bc['recipe']['id']
            assert 'Selected' in bc['recipe']['explanation']
            assert bc['conversion_intent'] == 'lead'  # goal 'leads' -> lead intent

            hero = bc['sections'][0]
            assert hero['type'] == 'hero'
            # headline resolved from the kept 'headline' message (content.promises[0])
            assert hero['content']['headline'] == 'Transform Your Body'
            # primary CTA resolved from the offer (content.calls_to_action.primary)
            assert hero['content']['primary_cta'] == 'Book Now'


# =============================================================================
# Campaign field AI enhancement
# =============================================================================

def _ai_headers(client, token='campaign-ai-token'):
    with client.session_transaction() as sess:
        sess['ai_request_token'] = token
    return {
        'X-Requested-With': 'SwiftSitesApp',
        'X-AI-Request-Token': token,
        'Origin': 'http://localhost',
    }


class TestCampaignAiEnhance:
    def test_enhance_rejects_manual_call(self, client):
        # Missing the AI-request token → blocked by the AI-spend guard.
        res = client.post('/api/chat/enhance', json={
            'section_type': 'campaign',
            'target_field': 'offer.offer',
            'current_content': {'brief.product_or_service': 'Online yoga classes'},
        })
        assert res.status_code == 403

    def test_enhance_campaign_field_returns_ai_value(self, client):
        with patch(
            'rag.agent.model_backend.ModelBackend.generate',
            return_value='{"offer.offer": "Two weeks of unlimited classes, free."}',
        ):
            res = client.post('/api/chat/enhance', json={
                'business_name': 'Calm Studio',
                'industry': 'fitness',
                'description': 'Online yoga classes',
                'section_type': 'campaign',
                'target_field': 'offer.offer',
                'current_content': {
                    'name': 'Jun-2026 Calm Leads',
                    'goal': 'leads',
                    'brief.product_or_service': 'Online yoga classes',
                    'brief.target_audience': 'busy professionals',
                    'offer.offer': 'free trial',
                    'brand': {'name': 'Calm Studio', 'tone': 'aspirational'},
                },
            }, headers=_ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'ai'
        assert data['enhanced_fields']['offer.offer'] == 'Two weeks of unlimited classes, free.'

    def test_enhance_campaign_field_falls_back_when_ai_unavailable(self, client):
        with patch(
            'rag.agent.model_backend.ModelBackend.generate',
            side_effect=RuntimeError('offline'),
        ):
            res = client.post('/api/chat/enhance', json={
                'section_type': 'campaign',
                'target_field': 'brief.description',
                'current_content': {
                    'brief.description': 'A short existing description',
                    'brief.product_or_service': 'Online yoga classes',
                },
            }, headers=_ai_headers(client))

        assert res.status_code == 200
        data = res.get_json()
        assert data['source'] == 'fallback'
        # Fallback echoes the current value so the UI never hard-errors.
        assert data['enhanced_fields']['brief.description'] == 'A short existing description'

    def test_enhance_campaign_invalid_field_rejected(self, client):
        res = client.post('/api/chat/enhance', json={
            'section_type': 'campaign',
            'target_field': 'brief.awareness_level',
            'current_content': {'brief.product_or_service': 'Online yoga classes'},
        }, headers=_ai_headers(client))
        assert res.status_code == 400
