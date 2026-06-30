"""Tests for offer → ContentItem materialization (Phase B).

Verifies the unified data model: a campaign's offer fields persist as typed
ContentItem rows (shared with the Content Library), idempotently, via the
offer PATCH route and the standalone sync function.
"""
import pytest
from unittest.mock import patch

from extensions import db
from models import Campaign, CampaignOffer, ContentItem, Organization


@pytest.fixture
def campaign_app(tmp_path):
    db_uri = 'sqlite:///' + str(tmp_path / 'test_offer_sync.db')
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(campaign_app):
    return campaign_app.test_client()


def _create_campaign(client, name='Offer Campaign', goal='leads'):
    res = client.post('/api/campaigns', json={'name': name, 'goal': goal})
    return res.get_json()['id']


def _full_offer():
    return {
        'offer': '50% off your first month',
        'primary_cta': 'Start free trial',
        'secondary_cta': 'Book a demo',
        'benefits': ['Ship in minutes', 'No code required'],
        'proof_points': ['2,000+ teams', '99.9% uptime'],
        'objections': [{'concern': 'Is setup hard?', 'response': 'Five minutes.'}],
        'faqs': [{'question': 'Is there a free trial?', 'answer': 'Yes, 14 days.'}],
    }


class TestOfferPatchMaterializes:
    def test_offer_fields_become_content_items(self, client):
        campaign_id = _create_campaign(client)
        res = client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())
        assert res.status_code == 200

        library = client.get('/api/content').get_json()
        by_cat = {}
        for item in library:
            by_cat.setdefault(item['category'], []).append(item)

        # offer(1) + cta(2) + benefit(2) + proof(2) + objection(1) + faq(1) = 9
        assert len(library) == 9
        assert len(by_cat['benefit']) == 2
        assert len(by_cat['proof']) == 2
        assert len(by_cat['cta']) == 2
        assert by_cat['offer'][0]['content'] == '50% off your first month'
        assert all(i['source'] == 'campaign' for i in library)
        assert all(i['source_campaign_id'] == campaign_id for i in library)
        assert all(i['channel'] == 'landing_page' for i in library)

    def test_faq_and_objection_carry_slots(self, client):
        campaign_id = _create_campaign(client)
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())
        library = client.get('/api/content').get_json()

        faq = next(i for i in library if i['category'] == 'faq')
        assert faq['slots']['question'] == 'Is there a free trial?'
        assert faq['slots']['answer'] == 'Yes, 14 days.'

        objection = next(i for i in library if i['category'] == 'objection')
        assert objection['slots']['concern'] == 'Is setup hard?'
        assert objection['slots']['response'] == 'Five minutes.'

    def test_cta_roles_recorded(self, client):
        campaign_id = _create_campaign(client)
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())
        library = client.get('/api/content').get_json()
        ctas = [i for i in library if i['category'] == 'cta']
        roles = {c['slots'].get('role') for c in ctas}
        assert roles == {'primary', 'secondary'}


class TestIdempotency:
    def test_repeated_save_does_not_duplicate(self, client):
        campaign_id = _create_campaign(client)
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())
        first = client.get('/api/content').get_json()
        # Re-PATCH with the same data (debounced save scenario).
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())
        second = client.get('/api/content').get_json()
        assert len(second) == len(first) == 9

    def test_editing_offer_prunes_removed_and_adds_new(self, client):
        campaign_id = _create_campaign(client)
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=_full_offer())

        # Drop one benefit, add a different one.
        updated = _full_offer()
        updated['benefits'] = ['Ship in minutes', 'Cancel anytime']
        client.patch(f'/api/campaigns/{campaign_id}/offer', json=updated)

        library = client.get('/api/content').get_json()
        benefits = sorted(i['content'] for i in library if i['category'] == 'benefit')
        assert benefits == ['Cancel anytime', 'Ship in minutes']
        # still 9 total (2 benefits)
        assert len([i for i in library if i['category'] == 'benefit']) == 2


class TestSyncFunction:
    def test_sync_returns_counts(self, campaign_app):
        from campaign.offer_sync import sync_offer_to_content_items
        with campaign_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            campaign = Campaign(org_id=org.id, name='Direct Sync', goal='sales')
            db.session.add(campaign)
            db.session.flush()
            offer = CampaignOffer(campaign_id=campaign.id, offer='Buy one get one')
            offer.set_benefits(['Tastes great'])
            campaign.offer = offer
            db.session.add(offer)
            db.session.flush()

            result = sync_offer_to_content_items(campaign, commit=True)
            assert result['created'] == 2  # offer + benefit
            assert result['pruned'] == 0

            # Second run is a no-op.
            result2 = sync_offer_to_content_items(campaign, commit=True)
            assert result2['created'] == 0
            assert result2['kept'] == 2

    def test_empty_offer_creates_nothing(self, campaign_app):
        from campaign.offer_sync import sync_offer_to_content_items
        with campaign_app.app_context():
            org = Organization.query.filter_by(slug='default').first()
            campaign = Campaign(org_id=org.id, name='Empty', goal='leads')
            db.session.add(campaign)
            db.session.flush()
            campaign.offer = CampaignOffer(campaign_id=campaign.id)
            db.session.add(campaign.offer)
            db.session.flush()
            result = sync_offer_to_content_items(campaign, commit=True)
            assert result['created'] == 0


class TestSaveFromCampaignStillWorks:
    """save_from_campaign now shares the constructor; behavior unchanged and its
    message-derived items are never pruned by the offer sync."""

    def test_message_items_survive_offer_sync(self, client):
        campaign_id = _create_campaign(client)
        # Add a kept message and save it to the library.
        client.post(f'/api/campaigns/{campaign_id}/messages', json={
            'messages': [{'category': 'headline', 'content': 'Big News', 'is_kept': True}],
        })
        client.post('/api/content/save-from-campaign', json={'campaign_id': campaign_id})
        # Now PATCH an offer (runs the prune-capable sync).
        client.patch(f'/api/campaigns/{campaign_id}/offer', json={'benefits': ['Speed']})

        library = client.get('/api/content').get_json()
        contents = {i['content'] for i in library}
        assert 'Big News' in contents   # message-derived item not pruned
        assert 'Speed' in contents      # offer-derived benefit present
