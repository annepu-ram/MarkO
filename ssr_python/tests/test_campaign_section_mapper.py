"""Tests for the recipe → guided-section mapper (Phase C / C2).

Verifies "recipes select, RAG fills": a scored recipe drives the section
sequence + per-section content, content_refs resolve against typed content, the
campaign goal becomes a builder conversion_intent, and optional empty sections
drop out.
"""
import pytest

from campaign.section_mapper import (
    build_recipe_sections, conversion_intent_for_goal,
    section_type_for_purpose, CONVERSION_GOAL_TO_INTENT,
)
from campaign import vocabulary as V


def _saas_lead_gen_block():
    return {
        'id': 'c1', 'name': 'Acme', 'goal': 'calls',
        'conversion_goal': 'consultation_booking',
        'awareness_stage': 'problem_aware', 'industry': 'saas',
        'sales_cycle': 'consultative',
        'product': 'Acme Analytics', 'audience': 'data teams',
    }


def _content(with_objection=False):
    items = [
        {'id': 'p0', 'type': 'promise', 'content': 'See your funnel in one view'},
        {'id': 'pp0', 'type': 'pain_point', 'content': 'Dashboards are scattered'},
        {'id': 'pr0', 'type': 'proof', 'content': '500+ teams onboarded'},
        {'id': 'cta0', 'type': 'cta', 'content': 'Book a call', 'slots': {'role': 'primary'}},
    ]
    if with_objection:
        items.append({'id': 'o0', 'type': 'objection', 'content': 'Too pricey',
                      'slots': {'concern': 'Too pricey', 'response': 'ROI in 30 days'}})
    return items


class TestRecipeSelection:
    def test_selects_problem_aware_lead_gen(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content())
        assert res['recipe']['id'] == 'problem_aware_lead_gen'
        assert 'Selected' in res['recipe']['explanation']

    def test_explicit_recipe_overrides(self):
        res = build_recipe_sections(
            _saas_lead_gen_block(), _content(),
            explicit_recipe_id='local_impulse_offer',
        )
        assert res['recipe']['id'] == 'local_impulse_offer'

    def test_sequence_matches_recipe_not_hardcoded(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content())
        purposes = [s['purpose'] for s in res['sections']]
        # problem_aware_lead_gen recipe sequence (objections dropped — none given)
        assert purposes == ['problem_aware_hero', 'problem_cost', 'proof_points', 'final_cta']


class TestContentResolution:
    def test_hero_content_resolved_from_refs(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content())
        hero = next(s for s in res['sections'] if s['purpose'] == 'problem_aware_hero')
        assert hero['content']['headline'] == 'See your funnel in one view'
        assert hero['content']['eyebrow'] == 'Acme Analytics'   # campaign.product
        assert hero['content']['primary_cta'] == 'Book a call'

    def test_optional_objection_section_dropped_when_empty(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content(with_objection=False))
        assert all(s['purpose'] != 'objection_handling' for s in res['sections'])

    def test_optional_objection_section_kept_when_present(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content(with_objection=True))
        objection = next((s for s in res['sections'] if s['purpose'] == 'objection_handling'), None)
        assert objection is not None
        assert objection['content']['items']  # resolved content present

    def test_sections_use_content_key_for_guided_pipeline(self):
        # plan_from_context reads section['content'] — mapper must emit it.
        res = build_recipe_sections(_saas_lead_gen_block(), _content())
        assert all('content' in s for s in res['sections'])


class TestConversionIntent:
    def test_goal_becomes_intent(self):
        res = build_recipe_sections(_saas_lead_gen_block(), _content())
        assert res['conversion_intent'] == 'lead'
        assert all(s['conversion_intent'] == 'lead' for s in res['sections'])

    @pytest.mark.parametrize('goal,intent', [
        ('purchase', 'purchase'),
        ('lead_generation', 'lead'),
        ('newsletter_signup', 'engagement'),
        ('retention', 'trust'),
    ])
    def test_intent_mapping(self, goal, intent):
        assert conversion_intent_for_goal(goal) == intent

    def test_every_conversion_goal_maps_to_valid_builder_intent(self):
        valid = {'awareness', 'lead', 'purchase', 'trust', 'engagement'}
        for goal in V.CONVERSION_GOAL:
            assert conversion_intent_for_goal(goal) in valid

    def test_unknown_goal_defaults_to_awareness(self):
        assert conversion_intent_for_goal('not_a_goal') == 'awareness'


class TestPurposeMapping:
    def test_known_purposes_map_to_builder_types(self):
        assert section_type_for_purpose('problem_aware_hero') == 'hero'
        assert section_type_for_purpose('offer_highlight') == 'pricing'
        assert section_type_for_purpose('objection_handling') == 'faq'

    def test_unknown_purpose_passes_through(self):
        assert section_type_for_purpose('mystery') == 'mystery'
