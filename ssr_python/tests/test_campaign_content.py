"""Tests for content normalization (Task 2)."""
import pytest
from campaign.content import (
    normalize_campaign_content, group_by_type, available_types,
)


def _grouped():
    return {
        'pain_points': ['Agencies duplicate messages everywhere.'],
        'promises': ['Build pages, emails, ads from one source.', 'Ship faster.'],
        'proof': ['SSR landing pages', 'YAML layouts'],
        'objections': [
            {'concern': 'Will AI be reliable?', 'response': 'The compiler controls output.'},
        ],
        'faqs': [{'question': 'Is it free?', 'answer': 'Yes, 14-day trial.'}],
        'testimonials': [{'quote': 'Loved it', 'author': 'Sarah', 'rating': 5}],
        'calls_to_action': {'primary': 'Generate Campaign', 'secondary': 'View Demo'},
    }


class TestNormalizeGrouped:
    def test_expands_simple_groups(self):
        items = normalize_campaign_content(_grouped())
        by_type = group_by_type(items)
        assert len(by_type['promise']) == 2
        assert len(by_type['proof']) == 2
        assert by_type['pain_point'][0]['content'] == 'Agencies duplicate messages everywhere.'

    def test_group_key_maps_to_type(self):
        items = normalize_campaign_content({'pain_points': ['x']})
        assert items[0]['type'] == 'pain_point'

    def test_unknown_group_raises(self):
        with pytest.raises(ValueError):
            normalize_campaign_content({'random_group': ['x']})

    def test_ctas_get_role_and_style(self):
        items = normalize_campaign_content(_grouped())
        ctas = group_by_type(items)['cta']
        primary = next(c for c in ctas if c['slots']['role'] == 'primary')
        secondary = next(c for c in ctas if c['slots']['role'] == 'secondary')
        assert primary['content'] == 'Generate Campaign'
        assert primary['slots']['style'] == 'direct'
        assert secondary['slots']['style'] == 'soft'

    def test_objection_payload(self):
        items = normalize_campaign_content(_grouped())
        obj = group_by_type(items)['objection'][0]
        assert obj['slots']['concern'] == 'Will AI be reliable?'
        assert obj['slots']['response'] == 'The compiler controls output.'

    def test_faq_payload(self):
        items = normalize_campaign_content(_grouped())
        faq = group_by_type(items)['faq'][0]
        assert faq['slots']['answer'] == 'Yes, 14-day trial.'

    def test_testimonial_payload(self):
        items = normalize_campaign_content(_grouped())
        t = group_by_type(items)['testimonial'][0]
        assert t['slots']['author'] == 'Sarah'
        assert t['slots']['rating'] == 5

    def test_default_truth_level_and_source(self):
        items = normalize_campaign_content({'promises': ['x']})
        assert items[0]['truth_level'] == 'approved'
        assert items[0]['source'] == 'human_input'

    def test_ids_are_unique_per_type(self):
        items = normalize_campaign_content({'promises': ['a', 'b']})
        ids = [i['id'] for i in items]
        assert ids == ['content_promise_0', 'content_promise_1']


class TestNormalizeTypedList:
    def test_typed_list_passthrough(self):
        items = normalize_campaign_content([
            {'type': 'promise', 'content': 'Ship faster'},
            {'type': 'proof', 'content': '2000+ clients', 'truth_level': 'verified'},
        ])
        assert items[0]['type'] == 'promise'
        assert items[1]['truth_level'] == 'verified'

    def test_typed_list_missing_type_raises(self):
        with pytest.raises(ValueError):
            normalize_campaign_content([{'content': 'no type'}])

    def test_typed_list_unknown_type_raises(self):
        with pytest.raises(ValueError):
            normalize_campaign_content([{'type': 'zzz', 'content': 'x'}])


class TestHelpers:
    def test_available_types(self):
        items = normalize_campaign_content(_grouped())
        types = available_types(items)
        assert {'promise', 'proof', 'cta', 'objection', 'faq', 'testimonial', 'pain_point'} <= types

    def test_invalid_content_shape(self):
        with pytest.raises(ValueError):
            normalize_campaign_content('just a string')
