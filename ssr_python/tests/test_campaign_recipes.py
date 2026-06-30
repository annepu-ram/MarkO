"""Tests for the recipe engine (Task 3)."""
import pytest
from campaign.recipes import (
    load_recipes, load_recipe, load_section_purposes,
    score_recipe, score_recipe_candidates, select_recipe, build_recipe_context,
)


# --- loading ------------------------------------------------------------------

class TestLoading:
    def test_recipes_load_and_validate(self):
        recipes = load_recipes(force_reload=True)
        assert 'problem_aware_lead_gen' in recipes
        assert 'local_impulse_offer' in recipes

    def test_load_single_recipe(self):
        r = load_recipe('problem_aware_lead_gen')
        assert r['name'] == 'Problem-Aware Lead Generation'
        assert 'section_sequence' in r

    def test_load_unknown_recipe_raises(self):
        with pytest.raises(KeyError):
            load_recipe('does_not_exist')

    def test_section_purposes_load_and_validate(self):
        sp = load_section_purposes(force_reload=True)
        assert 'problem_aware_hero' in sp
        assert 'proof_points' in sp
        assert 'allowed_components' in sp['proof_points']

    def test_every_recipe_purpose_exists_in_library(self):
        recipes = load_recipes(force_reload=True)
        purposes = load_section_purposes(force_reload=True)
        for r in recipes.values():
            for step in r['section_sequence']:
                assert step['purpose'] in purposes, \
                    f'recipe {r["id"]} uses unknown purpose {step["purpose"]}'


# --- scoring ------------------------------------------------------------------

class TestScoring:
    def _saas_context(self):
        return {
            'conversion_goal': 'consultation_booking',
            'awareness_stage': 'problem_aware',
            'traffic_source': 'linkedin',
            'industry': 'saas',
            'sales_cycle': 'consultative',
            'brand_style': 'technical',
            'audience_sophistication': 'informed',
        }

    def test_full_match_high_score(self):
        recipe = load_recipe('problem_aware_lead_gen')
        ctx = self._saas_context()
        available = {'pain_point', 'promise', 'proof', 'cta'}
        score, reasons = score_recipe(recipe, ctx, available)
        # 30+25+15+15+10+5+5 = 105, +20 required available = 125
        assert score == 125
        assert any('all required content available' in r for r in reasons)

    def test_missing_required_content_penalized(self):
        recipe = load_recipe('problem_aware_lead_gen')
        ctx = self._saas_context()
        available = {'pain_point', 'promise'}  # missing proof + cta
        score, reasons = score_recipe(recipe, ctx, available)
        assert score < 105  # penalties applied
        assert any('missing required content "proof"' in r for r in reasons)
        assert any('missing required content "cta"' in r for r in reasons)

    def test_partial_context_match(self):
        recipe = load_recipe('problem_aware_lead_gen')
        ctx = {'conversion_goal': 'consultation_booking', 'industry': 'saas'}
        available = {'pain_point', 'promise', 'proof', 'cta'}
        score, _ = score_recipe(recipe, ctx, available)
        # 30 (goal) + 15 (industry) + 20 (content) = 65
        assert score == 65

    def test_no_match_zero_or_low(self):
        recipe = load_recipe('problem_aware_lead_gen')
        ctx = {'conversion_goal': 'purchase', 'industry': 'fashion'}
        available = {'pain_point', 'promise', 'proof', 'cta'}
        score, _ = score_recipe(recipe, ctx, available)
        # no context match, but required content present = +20
        assert score == 20


# --- selection ----------------------------------------------------------------

class TestSelection:
    def test_saas_context_selects_lead_gen(self):
        ctx = {
            'conversion_goal': 'consultation_booking',
            'awareness_stage': 'problem_aware',
            'traffic_source': 'linkedin',
            'industry': 'saas',
            'sales_cycle': 'consultative',
        }
        available = {'pain_point', 'promise', 'proof', 'cta'}
        chosen = select_recipe(ctx, available)
        assert chosen['id'] == 'problem_aware_lead_gen'
        assert 'Selected' in chosen['explanation']

    def test_local_context_selects_impulse(self):
        ctx = {
            'conversion_goal': 'appointment_booking',
            'awareness_stage': 'solution_aware',
            'traffic_source': 'instagram',
            'industry': 'local_services',
            'sales_cycle': 'impulse',
        }
        available = {'promise', 'offer', 'cta'}
        chosen = select_recipe(ctx, available)
        assert chosen['id'] == 'local_impulse_offer'

    def test_explicit_id_overrides_ranking(self):
        ctx = {'conversion_goal': 'appointment_booking', 'industry': 'local_services'}
        available = {'promise', 'offer', 'cta'}
        chosen = select_recipe(ctx, available, explicit_id='problem_aware_lead_gen')
        assert chosen['id'] == 'problem_aware_lead_gen'

    def test_explicit_unknown_raises(self):
        with pytest.raises(KeyError):
            select_recipe({}, set(), explicit_id='nope')

    def test_candidates_sorted_desc(self):
        ctx = {
            'conversion_goal': 'consultation_booking',
            'awareness_stage': 'problem_aware',
            'industry': 'saas',
        }
        available = {'pain_point', 'promise', 'proof', 'cta'}
        ranked = score_recipe_candidates(ctx, available)
        scores = [r['score'] for r in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_explanation_is_human_readable(self):
        ctx = {'conversion_goal': 'consultation_booking', 'industry': 'saas'}
        available = {'pain_point', 'promise', 'proof', 'cta'}
        chosen = select_recipe(ctx, available)
        assert 'conversion_goal=consultation_booking' in chosen['explanation']


# --- context helper -----------------------------------------------------------

class TestBuildContext:
    def test_extracts_scoring_fields(self):
        campaign = {
            'id': 'c1', 'name': 'X', 'conversion_goal': 'purchase',
            'awareness_stage': 'most_aware', 'industry': 'ecommerce',
            'unused_field': 'ignored',
        }
        ctx = build_recipe_context(campaign)
        assert ctx['conversion_goal'] == 'purchase'
        assert ctx['industry'] == 'ecommerce'
        assert 'unused_field' not in ctx
        assert ctx['traffic_source'] is None
