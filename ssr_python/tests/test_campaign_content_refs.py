"""Tests for content reference resolution (Task 2)."""
import pytest
from campaign.content import normalize_campaign_content
from campaign.content_refs import (
    resolve_ref, resolve_refs, try_resolve_refs, ContentRefError,
)


def _ctx():
    campaign = {
        'id': 'c1', 'product': 'Swift Sites', 'name': 'Summer Launch',
    }
    content = normalize_campaign_content({
        'pain_points': ['Agencies duplicate messages.'],
        'promises': ['Build from one source.', 'Ship faster.'],
        'proof': ['SSR pages', 'YAML layouts'],
        'objections': [{'concern': 'Reliable?', 'response': 'Compiler controls it.'}],
        'calls_to_action': {'primary': 'Generate Campaign', 'secondary': 'View Demo'},
    })
    return campaign, content


class TestCampaignRefs:
    def test_resolve_campaign_field(self):
        c, items = _ctx()
        assert resolve_ref('campaign.product', c, items) == 'Swift Sites'

    def test_missing_campaign_field(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_ref('campaign.nonexistent', c, items)

    def test_nested_campaign_ref_unsupported(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_ref('campaign.foo.bar', c, items)


class TestContentRefs:
    def test_indexed_ref(self):
        c, items = _ctx()
        assert resolve_ref('content.promises[0]', c, items) == 'Build from one source.'
        assert resolve_ref('content.promises[1]', c, items) == 'Ship faster.'

    def test_index_out_of_range(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_ref('content.promises[5]', c, items)

    def test_whole_group_returns_list(self):
        c, items = _ctx()
        proof = resolve_ref('content.proof', c, items)
        assert proof == ['SSR pages', 'YAML layouts']

    def test_empty_group_raises(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_ref('content.testimonials', c, items)

    def test_cta_primary_secondary(self):
        c, items = _ctx()
        assert resolve_ref('content.calls_to_action.primary', c, items) == 'Generate Campaign'
        assert resolve_ref('content.calls_to_action.secondary', c, items) == 'View Demo'

    def test_objection_returns_structured(self):
        c, items = _ctx()
        val = resolve_ref('content.objections[0]', c, items)
        assert val['concern'] == 'Reliable?'
        assert val['response'] == 'Compiler controls it.'

    def test_bad_prefix(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_ref('promises[0]', c, items)


class TestResolveRefs:
    def test_resolve_mapping(self):
        c, items = _ctx()
        out = resolve_refs({
            'eyebrow': 'campaign.product',
            'headline': 'content.promises[0]',
            'primary_cta': 'content.calls_to_action.primary',
        }, c, items)
        assert out['eyebrow'] == 'Swift Sites'
        assert out['headline'] == 'Build from one source.'
        assert out['primary_cta'] == 'Generate Campaign'

    def test_resolve_mapping_raises_on_missing(self):
        c, items = _ctx()
        with pytest.raises(ContentRefError):
            resolve_refs({'x': 'content.promises[9]'}, c, items)

    def test_try_resolve_collects_missing(self):
        c, items = _ctx()
        resolved, missing = try_resolve_refs({
            'headline': 'content.promises[0]',
            'proof': 'content.testimonials',   # empty -> missing
        }, c, items)
        assert resolved['headline'] == 'Build from one source.'
        assert 'proof' in missing
