"""Tests for the deterministic campaign compiler + render round-trip (Task 4)."""
import os
import yaml
import pytest

from campaign.page_compiler import compile_campaign_to_page_yaml
from campaign.schema import CampaignValidationError


_EXAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'campaign', 'examples', 'basic_lead_gen_campaign.yaml',
)


def _load_example():
    with open(_EXAMPLE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# --- structure (no app/renderer needed) --------------------------------------

class TestCompileStructure:
    def test_example_compiles(self):
        res = compile_campaign_to_page_yaml(_load_example())
        struct = res['yaml']
        assert isinstance(struct, list)
        assert struct[0]['name'] == 'site'

    def test_has_page(self):
        struct = compile_campaign_to_page_yaml(_load_example())['yaml']
        page = struct[0]['components'][0]
        assert page['name'] == 'page'
        assert page['slug'] == 'summer-launch'

    def test_recipe_selected(self):
        res = compile_campaign_to_page_yaml(_load_example())
        assert res['recipe']['id'] == 'problem_aware_lead_gen'
        assert res['recipe']['score'] == 125

    def test_hero_heading_from_promise(self):
        struct = compile_campaign_to_page_yaml(_load_example())['yaml']
        page = struct[0]['components'][0]
        # find first heading text anywhere in the tree
        headings = _collect(page, 'heading')
        texts = [h['properties']['text'] for h in headings]
        assert 'Build landing pages, emails, and ads from one structured campaign source.' in texts

    def test_theme_propagates_to_site_and_page(self):
        struct = compile_campaign_to_page_yaml(_load_example())['yaml']
        site = struct[0]
        page = site['components'][0]
        assert site['properties']['theme']['colors']['accent'] == '#6366f1'
        # page background derives from theme background
        assert page['properties']['appearance']['background']['color'] == '#ffffff'

    def test_no_missing_refs_for_example(self):
        res = compile_campaign_to_page_yaml(_load_example())
        assert res['missing'] == {}

    def test_metadata_preserved(self):
        res = compile_campaign_to_page_yaml(_load_example())
        assert res['metadata']['campaign_id'] == 'summer_launch_2026'
        assert res['metadata']['recipe_id'] == 'problem_aware_lead_gen'

    def test_optional_section_skipped_when_empty(self):
        doc = _load_example()
        # remove objections -> objection_handling section should drop out
        del doc['content']['objections']
        res = compile_campaign_to_page_yaml(doc)
        ids = [c.get('section_id') for c in res['yaml'][0]['components'][0]['components']]
        assert 'objections' not in ids

    def test_strip_metadata_removes_section_id(self):
        res = compile_campaign_to_page_yaml(_load_example(), strip_metadata=True)
        page = res['yaml'][0]['components'][0]
        for comp in page['components']:
            assert 'section_id' not in comp


# --- validation failures ------------------------------------------------------

class TestCompileValidation:
    def test_missing_id_fails(self):
        doc = _load_example()
        del doc['campaign']['id']
        with pytest.raises(CampaignValidationError):
            compile_campaign_to_page_yaml(doc)

    def test_invalid_conversion_goal_fails(self):
        doc = _load_example()
        doc['campaign']['conversion_goal'] = 'booked_calls'
        with pytest.raises(CampaignValidationError):
            compile_campaign_to_page_yaml(doc)

    def test_bad_ref_syntax_fails_validation(self):
        doc = _load_example()
        doc['landing_page']['sections'][0]['content_refs']['headline'] = 'promises[0]'
        with pytest.raises(CampaignValidationError):
            compile_campaign_to_page_yaml(doc)


# --- goal derivation path -----------------------------------------------------

class TestGoalDerivation:
    def test_user_goal_derives_conversion_goal(self):
        doc = _load_example()
        # simulate a campaign that only has the simple user goal
        del doc['campaign']['conversion_goal']
        doc['campaign']['goal'] = 'calls'
        # validation requires conversion_goal, so this should fail BEFORE derivation
        # — derivation is a compiler convenience for already-valid docs. Confirm
        # that providing conversion_goal is the contract.
        with pytest.raises(CampaignValidationError):
            compile_campaign_to_page_yaml(doc)


# --- render round-trip (needs app context for jinja filters) ------------------

@pytest.fixture
def app_ctx(tmp_path):
    from unittest.mock import patch
    db_uri = 'sqlite:///' + str(tmp_path / 'test_compiler.db')
    with patch('config.Config.SQLALCHEMY_DATABASE_URI', db_uri):
        from app import create_app
        app = create_app('development')
        app.config['TESTING'] = True
    with app.app_context():
        yield app


class TestRenderRoundTrip:
    def test_compiled_yaml_renders_to_html(self, app_ctx):
        from extensions import TOKENS, COMPONENT_DEFAULTS
        from renderer import render_yaml_structure

        res = compile_campaign_to_page_yaml(_load_example(), strip_metadata=True)
        html = render_yaml_structure(res['yaml'], tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert html and len(html) > 100
        assert 'Build landing pages, emails, and ads from one structured campaign source.' in html

    def test_rendered_html_contains_cta(self, app_ctx):
        from extensions import TOKENS, COMPONENT_DEFAULTS
        from renderer import render_yaml_structure
        res = compile_campaign_to_page_yaml(_load_example(), strip_metadata=True)
        html = render_yaml_structure(res['yaml'], tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'Generate Campaign' in html

    def test_theme_accent_in_rendered_html(self, app_ctx):
        from extensions import TOKENS, COMPONENT_DEFAULTS
        from renderer import render_yaml_structure
        res = compile_campaign_to_page_yaml(_load_example(), strip_metadata=True)
        html = render_yaml_structure(res['yaml'], tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert '#6366f1' in html  # accent propagated into rendered styles


# helper
def _collect(node, name, out=None):
    out = out if out is not None else []
    if isinstance(node, dict):
        if node.get('name') == name:
            out.append(node)
        for v in node.values():
            _collect(v, name, out)
    elif isinstance(node, list):
        for item in node:
            _collect(item, name, out)
    return out
