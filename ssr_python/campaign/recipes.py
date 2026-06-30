"""
Recipe engine — load recipes & section purposes, score candidates against a
campaign context, and select the best recipe with an explainable reason.

Scoring is deterministic (brief §6). No ML, no graph library. Recipes and
section purposes are YAML data loaded from disk and cached.
"""

import os
import yaml

from campaign.validators import validate_recipe, validate_section_purpose
from campaign.schema import CampaignValidationError

_HERE = os.path.dirname(os.path.abspath(__file__))
_RECIPES_DIR = os.path.join(_HERE, 'recipes')
_SECTION_PURPOSES_PATH = os.path.join(_HERE, 'section_purposes.yaml')

# Deterministic scoring weights (brief §6).
_WEIGHTS = {
    'conversion_goal': 30,
    'awareness_stage': 25,
    'traffic_source': 15,
    'industry': 15,
    'sales_cycle': 10,
    'brand_style': 5,
    'audience_sophistication': 5,
}
_REQUIRED_CONTENT_AVAILABLE = 20
_MISSING_REQUIRED_CONTENT = -50

_recipe_cache = None
_section_purpose_cache = None


# --- loading ------------------------------------------------------------------

def load_recipes(force_reload=False):
    """Load and validate all recipe YAML files. Returns {id: recipe_dict}."""
    global _recipe_cache
    if _recipe_cache is not None and not force_reload:
        return _recipe_cache

    recipes = {}
    if os.path.isdir(_RECIPES_DIR):
        for fname in sorted(os.listdir(_RECIPES_DIR)):
            if not fname.endswith(('.yaml', '.yml')):
                continue
            path = os.path.join(_RECIPES_DIR, fname)
            with open(path, 'r', encoding='utf-8') as f:
                recipe = yaml.safe_load(f)
            errors = validate_recipe(recipe)
            if errors:
                raise CampaignValidationError(
                    [f'Recipe "{fname}": {e}' for e in errors]
                )
            recipes[recipe['id']] = recipe
    _recipe_cache = recipes
    return recipes


def load_recipe(recipe_id):
    """Return a single recipe by id, or raise KeyError."""
    recipes = load_recipes()
    if recipe_id not in recipes:
        raise KeyError(f'Recipe "{recipe_id}" not found.')
    return recipes[recipe_id]


def load_section_purposes(force_reload=False):
    """Load and validate the section-purpose library. Returns {purpose: def}."""
    global _section_purpose_cache
    if _section_purpose_cache is not None and not force_reload:
        return _section_purpose_cache

    with open(_SECTION_PURPOSES_PATH, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or []
    purposes = {}
    for sp in raw:
        errors = validate_section_purpose(sp)
        if errors:
            raise CampaignValidationError(
                [f'Section purpose "{sp.get("purpose", "?")}": {e}' for e in errors]
            )
        purposes[sp['purpose']] = sp
    _section_purpose_cache = purposes
    return purposes


# --- scoring & selection ------------------------------------------------------

def score_recipe(recipe, context, available_content_types):
    """Score one recipe against a campaign context + available content types.

    Returns (score, reasons) where reasons is a list of human-readable strings.
    """
    score = 0
    reasons = []
    applies = recipe.get('applies_when') or {}

    for field, weight in _WEIGHTS.items():
        ctx_val = context.get(field)
        recipe_val = applies.get(field)
        if ctx_val and recipe_val and ctx_val == recipe_val:
            score += weight
            reasons.append(f'{field}={ctx_val} (+{weight})')

    # Required content availability.
    required = recipe.get('required_content_types') or []
    missing = [t for t in required if t not in available_content_types]
    if required and not missing:
        score += _REQUIRED_CONTENT_AVAILABLE
        reasons.append(f'all required content available (+{_REQUIRED_CONTENT_AVAILABLE})')
    for t in missing:
        score += _MISSING_REQUIRED_CONTENT
        reasons.append(f'missing required content "{t}" ({_MISSING_REQUIRED_CONTENT})')

    return score, reasons


def score_recipe_candidates(context, available_content_types, recipes=None):
    """Rank all recipes. Returns a list of dicts sorted by score desc.

    Each entry: {id, name, score, reasons, recipe}.
    """
    recipes = recipes if recipes is not None else load_recipes()
    ranked = []
    for rid, recipe in recipes.items():
        score, reasons = score_recipe(recipe, context, available_content_types)
        ranked.append({
            'id': rid,
            'name': recipe.get('name', rid),
            'score': score,
            'reasons': reasons,
            'recipe': recipe,
        })
    ranked.sort(key=lambda r: (r['score'], r['id']), reverse=True)
    return ranked


def select_recipe(context, available_content_types, recipes=None, explicit_id=None):
    """Select the best recipe.

    If `explicit_id` is given (e.g. landing_page.recipe), that recipe is used
    directly but still scored for explanation. Otherwise the top-ranked
    candidate wins.

    Returns: {id, name, score, reasons, recipe, explanation}.
    Raises KeyError if explicit_id is unknown, ValueError if no recipe is usable.
    """
    recipes = recipes if recipes is not None else load_recipes()
    if not recipes:
        raise ValueError('No recipes are available to select from.')

    ranked = score_recipe_candidates(context, available_content_types, recipes)

    if explicit_id:
        chosen = next((r for r in ranked if r['id'] == explicit_id), None)
        if chosen is None:
            raise KeyError(f'Requested recipe "{explicit_id}" not found.')
    else:
        chosen = ranked[0]

    chosen = dict(chosen)
    chosen['explanation'] = _explain(chosen)
    return chosen


def _explain(chosen):
    name = chosen['name']
    if not chosen['reasons']:
        return f'Selected "{name}" as the default; no strong context match.'
    return f'Selected "{name}" (score {chosen["score"]}) because ' + ', '.join(chosen['reasons']) + '.'


# --- context helper -----------------------------------------------------------

def build_recipe_context(campaign_block):
    """Extract the scoring dimensions from a campaign block.

    Reads conversion_goal/awareness_stage/etc. directly; callers should have
    already derived conversion_goal from the user goal where needed.
    """
    fields = [
        'conversion_goal', 'awareness_stage', 'traffic_source', 'industry',
        'sales_cycle', 'brand_style', 'audience_sophistication',
    ]
    return {f: (campaign_block or {}).get(f) for f in fields}
