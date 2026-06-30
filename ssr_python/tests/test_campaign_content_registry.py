"""Tests for the canonical content-type registry (Phase B0).

The registry (campaign/content_registry.py) is the single source of truth that
both campaign/vocabulary.py (ontology) and campaign/content_type_catalog.py
(Library catalog) now derive from. These tests pin the parity between the three
and verify the ORM ContentItem -> normalized-item bridge resolves through the
content_refs resolver exactly like transient campaign content.
"""
import pytest

from campaign import vocabulary as V
from campaign import content_registry as R
from campaign.content_type_catalog import content_type_keys
from campaign.content import group_by_type
from campaign.content_refs import resolve_ref


# --- parity: registry is the source both legacy views derive from ------------

class TestRegistryParity:
    def test_ontology_matches_vocabulary_content_type(self):
        assert R.ontology_keys() == set(V.CONTENT_TYPE)

    def test_composite_matches_vocabulary(self):
        assert R.composite_ontology_keys() == set(V.COMPOSITE_TYPES)

    def test_group_key_map_matches_vocabulary(self):
        assert R.group_key_to_ontology_type() == V.GROUP_KEY_TO_TYPE

    def test_catalog_keys_match_catalog(self):
        assert R.catalog_keys() == set(content_type_keys())

    def test_vocabulary_symbols_are_registry_derived(self):
        # Sanity: the derived sets are non-empty and snake_case (no drift).
        assert V.CONTENT_TYPE and V.COMPOSITE_TYPES and V.GROUP_KEY_TO_TYPE
        assert all(k == k.lower() for k in V.CONTENT_TYPE)


# --- cross-name bridges -------------------------------------------------------

class TestNameBridges:
    @pytest.mark.parametrize('catalog_key,ontology_key', [
        ('headline', 'title'),
        ('product_feature', 'feature'),
        ('form', 'form_spec'),
        ('benefit', 'benefit'),       # same name in both
        ('offer', 'offer'),
    ])
    def test_catalog_to_ontology(self, catalog_key, ontology_key):
        assert R.to_ontology_type(catalog_key) == ontology_key

    def test_to_ontology_passes_through_ontology_keys(self):
        assert R.to_ontology_type('pain_point') == 'pain_point'
        assert R.to_ontology_type('promise') == 'promise'

    def test_to_catalog_key_reverse(self):
        assert R.to_catalog_key('title') == 'headline'
        assert R.to_catalog_key('feature') == 'product_feature'

    def test_ontology_only_types_have_no_catalog_key(self):
        # Atoms/primitives are ontology-only — they are not Library categories.
        assert R.to_catalog_key('pain_point') is None
        assert R.to_catalog_key('paragraph') is None

    def test_unknown_key_passes_through(self):
        assert R.to_ontology_type('totally_unknown') == 'totally_unknown'


# --- ORM ContentItem -> normalized bridge -------------------------------------

class _FakeContentItem:
    """Duck-typed stand-in for the ORM ContentItem (no DB needed)."""

    def __init__(self, category, content, slots=None, tags=None, source='campaign', id=None):
        self.category = category
        self.content = content
        self._slots = slots or {}
        self._tags = tags or []
        self.source = source
        self.id = id

    def get_slots(self):
        return self._slots

    def get_tags(self):
        return self._tags


class TestNormalizeContentItem:
    def test_maps_category_to_ontology_type(self):
        # A Library 'headline' (catalog key) becomes ontology 'title'.
        item = _FakeContentItem('headline', 'Build faster')
        norm = R.normalize_content_item(item)
        assert norm['type'] == 'title'
        assert norm['content'] == 'Build faster'

    def test_product_feature_maps_to_feature(self):
        item = _FakeContentItem('product_feature', 'Realtime sync')
        norm = R.normalize_content_item(item)
        assert norm['type'] == 'feature'

    def test_preserves_slots_and_source(self):
        item = _FakeContentItem('faq', 'Is it free?',
                                slots={'question': 'Is it free?', 'answer': 'Yes.'},
                                source='campaign')
        norm = R.normalize_content_item(item)
        assert norm['slots']['answer'] == 'Yes.'
        assert norm['source'] == 'campaign'

    def test_resolves_through_content_refs(self):
        # The whole point: a normalized library item resolves like campaign content.
        items = [
            _FakeContentItem('benefit', 'Ship in minutes'),
            _FakeContentItem('benefit', 'No code needed'),
        ]
        normalized = R.normalize_content_items(items)
        # content.benefits[0] resolves through the standard resolver
        assert resolve_ref('content.benefits[0]', {}, normalized) == 'Ship in minutes'
        assert resolve_ref('content.benefits[1]', {}, normalized) == 'No code needed'

    def test_grouping_indexes_are_per_type(self):
        items = [
            _FakeContentItem('headline', 'H1'),
            _FakeContentItem('benefit', 'B1'),
            _FakeContentItem('headline', 'H2'),
        ]
        normalized = R.normalize_content_items(items)
        grouped = group_by_type(normalized)
        # headline -> ontology 'title'
        assert [i['content'] for i in grouped['title']] == ['H1', 'H2']
        assert [i['content'] for i in grouped['benefit']] == ['B1']

    def test_faq_object_resolves_question_answer(self):
        items = [_FakeContentItem('faq', 'Is it free?',
                                  slots={'question': 'Is it free?', 'answer': 'Yes, 14-day trial.'})]
        normalized = R.normalize_content_items(items)
        resolved = resolve_ref('content.faqs[0]', {}, normalized)
        assert resolved == {'question': 'Is it free?', 'answer': 'Yes, 14-day trial.'}
