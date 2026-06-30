"""Tests for campaign vocabulary + schema validation (Task 1)."""
import pytest
from campaign import vocabulary as V
from campaign.validators import (
    validate_campaign, validate_campaign_or_raise, validate_recipe,
    validate_section_purpose,
)
from campaign.schema import CampaignValidationError


def _valid_campaign():
    return {
        'campaign': {
            'id': 'summer_launch_2026',
            'name': 'Summer Launch 2026',
            'product': 'Swift Sites',
            'audience': 'marketing agencies',
            'conversion_goal': 'consultation_booking',
            'awareness_stage': 'problem_aware',
            'traffic_source': 'linkedin',
            'audience_sophistication': 'informed',
            'sales_cycle': 'consultative',
            'industry': 'saas',
            'brand_style': 'technical',
        },
        'content': {
            'pain_points': ['Agencies duplicate the same message everywhere.'],
            'promises': ['Build pages, emails, and ads from one source.'],
            'proof': ['Server-side rendered landing pages'],
            'calls_to_action': {'primary': 'Generate Campaign'},
        },
        'landing_page': {
            'slug': 'summer-launch',
            'title': 'Summer Launch Campaign',
            'recipe': 'problem_aware_lead_gen',
            'sections': [
                {
                    'id': 'hero',
                    'purpose': 'problem_aware_hero',
                    'content_refs': {
                        'eyebrow': 'campaign.product',
                        'headline': 'content.promises[0]',
                        'subheadline': 'content.pain_points[0]',
                        'primary_cta': 'content.calls_to_action.primary',
                    },
                },
            ],
        },
    }


# --- vocabulary ---------------------------------------------------------------

class TestVocabulary:
    def test_value_sets_nonempty(self):
        for name in ['INDUSTRY', 'CONVERSION_GOAL', 'AWARENESS_STAGE',
                     'CONTENT_TYPE', 'TRUTH_LEVEL', 'PERSUASION_ROLE']:
            assert getattr(V, name), f'{name} should be populated'

    def test_snake_case_no_uppercase(self):
        # ROI/CTA/FAQ must be lowercased
        assert 'roi' in V.DECISION_DRIVER
        assert 'ROI' not in V.DECISION_DRIVER
        assert 'cta' in V.CONTENT_TYPE
        assert 'faq' in V.CONTENT_TYPE

    @pytest.mark.parametrize('goal,cycle,expected', [
        ('calls', 'consultative', 'consultation_booking'),
        ('calls', 'enterprise', 'demo_booking'),
        ('leads', None, 'lead_generation'),
        ('sales', 'impulse', 'purchase'),
        ('sales', 'recurring', 'trial_signup'),
        ('signups', None, 'newsletter_signup'),
        ('traffic', None, 'community_join'),
        ('inform', None, 'newsletter_signup'),
    ])
    def test_goal_derivation(self, goal, cycle, expected):
        assert V.derive_conversion_goal(goal, cycle) == expected

    def test_goal_derivation_unmapped_falls_back(self):
        assert V.derive_conversion_goal('something_weird') == 'lead_generation'

    @pytest.mark.parametrize('goal,cycle,awareness,traffic,expected', [
        # calls + impulse-ish cycle -> a quick appointment, not a sales call.
        ('calls', 'impulse', None, None, 'appointment_booking'),
        ('calls', 'transactional', None, None, 'appointment_booking'),
        ('calls', 'seasonal', None, None, 'appointment_booking'),
        # sales to existing customers (lifecycle) -> repeat_purchase / upsell.
        ('sales', 'recurring', 'retention', None, 'repeat_purchase'),
        ('sales', 'transactional', 'reactivation', None, 'repeat_purchase'),
        ('sales', 'recurring', 'expansion', None, 'upsell'),
        # signups for a recurring product -> trial, not newsletter.
        ('signups', 'recurring', None, None, 'trial_signup'),
        # webinar traffic registers regardless of the headline goal.
        ('leads', 'consultative', None, 'webinar', 'webinar_registration'),
        ('inform', None, None, 'webinar', 'webinar_registration'),
    ])
    def test_goal_derivation_expanded_signals(self, goal, cycle, awareness, traffic, expected):
        assert V.derive_conversion_goal(
            goal, cycle, awareness_stage=awareness, traffic_source=traffic
        ) == expected

    def test_every_user_goal_x_sales_cycle_maps_to_valid_conversion_goal(self):
        # Decision 3: every user goal × sales_cycle resolves to a real
        # CONVERSION_GOAL — the scorer never sees an unknown value.
        for goal in V.USER_GOALS:
            for cycle in (None, *V.SALES_CYCLE):
                for awareness in (None, *V.AWARENESS_STAGE):
                    result = V.derive_conversion_goal(
                        goal, cycle, awareness_stage=awareness
                    )
                    assert result in V.CONVERSION_GOAL, \
                        f'{goal}/{cycle}/{awareness} -> {result} not in CONVERSION_GOAL'

    def test_expanded_signature_is_backward_compatible(self):
        # Old positional call (goal, sales_cycle) still works unchanged.
        assert V.derive_conversion_goal('calls', 'consultative') == 'consultation_booking'
        assert V.derive_conversion_goal('leads') == 'lead_generation'


# --- campaign validation ------------------------------------------------------

class TestCampaignValidation:
    def test_valid_campaign_passes(self):
        assert validate_campaign(_valid_campaign()) == []

    def test_valid_campaign_or_raise(self):
        assert validate_campaign_or_raise(_valid_campaign()) is True

    def test_missing_top_level_key(self):
        doc = _valid_campaign()
        del doc['content']
        errors = validate_campaign(doc)
        assert any('content' in e for e in errors)

    def test_missing_campaign_id(self):
        doc = _valid_campaign()
        del doc['campaign']['id']
        errors = validate_campaign(doc)
        assert any('id' in e for e in errors)

    def test_invalid_conversion_goal(self):
        doc = _valid_campaign()
        doc['campaign']['conversion_goal'] = 'booked_calls'  # old/invalid value
        errors = validate_campaign(doc)
        assert any('conversion_goal' in e for e in errors)

    def test_invalid_awareness_stage(self):
        doc = _valid_campaign()
        doc['campaign']['awareness_stage'] = 'cold'
        errors = validate_campaign(doc)
        assert any('awareness_stage' in e for e in errors)

    def test_invalid_optional_industry(self):
        doc = _valid_campaign()
        doc['campaign']['industry'] = 'rocketry'
        errors = validate_campaign(doc)
        assert any('industry' in e for e in errors)

    def test_unknown_content_group_key(self):
        doc = _valid_campaign()
        doc['content']['random_stuff'] = ['x']
        errors = validate_campaign(doc)
        assert any('random_stuff' in e for e in errors)

    def test_typed_content_list_accepted(self):
        doc = _valid_campaign()
        doc['content'] = [
            {'type': 'promise', 'content': 'Ship faster'},
            {'type': 'proof', 'content': '2000+ clients'},
        ]
        assert validate_campaign(doc) == []

    def test_typed_content_missing_type(self):
        doc = _valid_campaign()
        doc['content'] = [{'content': 'no type here'}]
        errors = validate_campaign(doc)
        assert any('type' in e for e in errors)

    def test_bad_content_ref_syntax(self):
        doc = _valid_campaign()
        doc['landing_page']['sections'][0]['content_refs']['headline'] = 'promises[0]'
        errors = validate_campaign(doc)
        assert any('headline' in e for e in errors)

    def test_section_missing_purpose(self):
        doc = _valid_campaign()
        del doc['landing_page']['sections'][0]['purpose']
        errors = validate_campaign(doc)
        assert any('purpose' in e for e in errors)

    def test_raise_collects_errors(self):
        doc = _valid_campaign()
        del doc['campaign']['id']
        doc['campaign']['conversion_goal'] = 'nope'
        with pytest.raises(CampaignValidationError) as exc:
            validate_campaign_or_raise(doc)
        assert len(exc.value.errors) >= 2


# --- recipe validation --------------------------------------------------------

class TestRecipeValidation:
    def _recipe(self):
        return {
            'id': 'problem_aware_lead_gen',
            'name': 'Problem-Aware Lead Generation',
            'applies_when': {
                'conversion_goal': 'consultation_booking',
                'awareness_stage': 'problem_aware',
                'traffic_source': 'linkedin',
                'industry': 'saas',
                'sales_cycle': 'consultative',
            },
            'required_content_types': ['pain_point', 'promise', 'proof', 'cta'],
            'optional_content_types': ['objection', 'testimonial', 'faq'],
            'section_sequence': [
                {'purpose': 'problem_aware_hero'},
                {'purpose': 'final_cta'},
            ],
        }

    def test_valid_recipe(self):
        assert validate_recipe(self._recipe()) == []

    def test_recipe_missing_section_sequence(self):
        r = self._recipe()
        del r['section_sequence']
        assert any('section_sequence' in e for e in validate_recipe(r))

    def test_recipe_invalid_applies_when_enum(self):
        r = self._recipe()
        r['applies_when']['industry'] = 'rocketry'
        assert any('industry' in e for e in validate_recipe(r))

    def test_recipe_invalid_content_type(self):
        r = self._recipe()
        r['required_content_types'] = ['pain_point', 'made_up_type']
        assert any('required_content_types' in e for e in validate_recipe(r))


# --- section-purpose validation ----------------------------------------------

class TestSectionPurposeValidation:
    def test_valid(self):
        sp = {
            'purpose': 'proof_points',
            'required_content_types': ['proof'],
            'preferred_persuasion_roles': ['authority', 'trust_building'],
            'allowed_components': ['layout-row', 'heading', 'paragraph'],
        }
        assert validate_section_purpose(sp) == []

    def test_missing_allowed_components(self):
        sp = {'purpose': 'proof_points', 'allowed_components': []}
        assert any('allowed_components' in e for e in validate_section_purpose(sp))

    def test_invalid_persuasion_role(self):
        sp = {
            'purpose': 'proof_points',
            'preferred_persuasion_roles': ['not_a_role'],
            'allowed_components': ['heading'],
        }
        assert any('preferred_persuasion_roles' in e for e in validate_section_purpose(sp))
