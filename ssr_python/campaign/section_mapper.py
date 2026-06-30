"""
Recipe → guided-section mapper (the spine: "recipes select, RAG fills").

Strategy imp.md decision 2: a recipe governs WHICH sections appear, in what
ORDER, and WHAT content fills each — the RAG builder still generates the YAML.
This module replaces the hardcoded ``compiler._build_guided_sections`` section
list with a recipe-driven one.

For a selected recipe it walks ``section_sequence`` and, for each step:
  * maps the section ``purpose`` to a builder ``section_type`` the RAG index
    knows (e.g. ``problem_aware_hero`` -> ``hero``),
  * resolves the step's ``content_refs`` against the campaign's typed content
    (normalized ORM ``ContentItem`` rows + the campaign block) using the
    standard ``content_refs`` resolver, producing the ``business_content`` dict
    the builder consumes verbatim,
  * attaches the section purpose's ``allowed_components`` so the builder stays
    within the layout the purpose intends,
  * carries a ``conversion_intent`` derived from the campaign goal (Phase C2),
  * drops optional sections that resolved no content.

Output is a list of section dicts in the exact shape
``rag_agent._create_page_guided`` already expects (``type``, ``description``,
``business_content``, ``components``, ``conversion_intent``, ``style_notes``).
"""

from campaign import vocabulary as V
from campaign.content_refs import try_resolve_refs
from campaign.recipes import (
    select_recipe, build_recipe_context, load_section_purposes,
)


# Recipe section purpose -> builder/RAG section_type. The builder normalizes
# further via SECTION_TYPE_ALIASES, so these target canonical index types.
PURPOSE_TO_SECTION_TYPE = {
    "problem_aware_hero": "hero",
    "aspirational_hero": "hero",
    "problem_cost": "features",
    "proof_points": "stats",
    "objection_handling": "faq",
    "offer_highlight": "pricing",
    "final_cta": "cta",
    # richer purposes (Phase D atoms) — mapped here so new recipes work too.
    "benefit_highlights": "features",
    "feature_grid": "features",
    "how_it_works": "how_it_works",
    "social_proof": "testimonials",
    "testimonial_wall": "testimonials",
    "urgency_countdown": "countdown",
    "pricing_table": "pricing",
    "comparison_table": "features",
    "faq_section": "faq",
    "lead_capture_form": "form_cta",
    "newsletter_signup": "newsletter",
    "trust_badges": "trusted_by",
    "about_story": "about",
    "stats_band": "stats",
}

# Campaign conversion_goal (14) -> builder conversion_intent (5). The builder's
# metadata filter only knows {awareness, lead, purchase, trust, engagement}.
CONVERSION_GOAL_TO_INTENT = {
    "purchase": "purchase",
    "repeat_purchase": "purchase",
    "upsell": "purchase",
    "lead_generation": "lead",
    "demo_booking": "lead",
    "consultation_booking": "lead",
    "appointment_booking": "lead",
    "trial_signup": "lead",
    "webinar_registration": "lead",
    "newsletter_signup": "engagement",
    "community_join": "engagement",
    "app_install": "purchase",
    "donation": "purchase",
    "retention": "trust",
}


def conversion_intent_for_goal(conversion_goal):
    """Map a refined conversion_goal to the builder's conversion_intent (Phase C2)."""
    return CONVERSION_GOAL_TO_INTENT.get(conversion_goal, "awareness")


def section_type_for_purpose(purpose):
    """Map a recipe section purpose to a builder/RAG section_type."""
    return PURPOSE_TO_SECTION_TYPE.get(purpose, purpose or "other")


def build_recipe_sections(campaign_block, content_items, *,
                          explicit_recipe_id=None, recipes=None):
    """Select a recipe for the campaign and map it to guided-flow sections.

    Args:
        campaign_block: dict of scoring dimensions for the campaign. Must carry a
            derived ``conversion_goal`` (Phase A); may carry awareness_stage,
            industry, traffic_source, sales_cycle, brand_style,
            audience_sophistication. Also used as the ``campaign.<field>`` ref
            namespace for content resolution.
        content_items: list of normalized typed-content dicts (from
            ``content_registry.normalize_content_items`` or
            ``content.normalize_campaign_content``).
        explicit_recipe_id: force a specific recipe (still scored for the reason).
        recipes: optional pre-loaded recipe map (mostly for tests).

    Returns:
        dict: {
            sections: [ {type, description, business_content, components,
                         conversion_intent, style_notes, purpose, section_id}, ... ],
            recipe: {id, name, score, explanation},
            missing: {section_id: {slot: reason}},   # unresolved refs
        }

    Raises:
        ValueError: if no recipe is available to select.
        KeyError: if explicit_recipe_id is unknown.
    """
    from campaign.content import available_types

    avail = available_types(content_items)
    context = build_recipe_context(campaign_block)
    chosen = select_recipe(
        context, avail, recipes=recipes, explicit_id=explicit_recipe_id,
    )
    recipe = chosen["recipe"]
    purposes = load_section_purposes()

    conversion_goal = campaign_block.get("conversion_goal")
    conversion_intent = conversion_intent_for_goal(conversion_goal)

    sections = []
    missing = {}
    for step in recipe.get("section_sequence") or []:
        purpose = step.get("purpose")
        section_id = step.get("id") or purpose
        refs = step.get("content_refs") or {}

        resolved, slot_missing = try_resolve_refs(refs, campaign_block, content_items)

        # Skip optional sections that resolved nothing real.
        if step.get("optional") and not _has_content(resolved):
            continue
        if slot_missing:
            missing[section_id] = slot_missing

        sp = purposes.get(purpose) or {}
        components = list(sp.get("allowed_components") or [])
        section_type = section_type_for_purpose(purpose)

        # `content` is the field the guided planner (plan_from_context) reads and
        # turns into the builder's business_content — emitting it keeps this a
        # drop-in replacement for _build_guided_sections. `components` /
        # `conversion_intent` / `style_notes` are honored downstream where the
        # guided pipeline now respects pre-provided values.
        sections.append({
            "type": section_type,
            "purpose": purpose,
            "section_id": section_id,
            "description": _describe(section_type, purpose, resolved),
            "content": _to_business_content(resolved),
            "components": components,
            "conversion_intent": conversion_intent,
            "style_notes": _style_notes(sp),
        })

    return {
        "sections": sections,
        "recipe": {
            "id": chosen["id"],
            "name": chosen["name"],
            "score": chosen["score"],
            "explanation": chosen["explanation"],
        },
        "conversion_intent": conversion_intent,
        "missing": missing,
    }


# --- internals ----------------------------------------------------------------

def _has_content(resolved):
    """True when at least one resolved slot carries a real value."""
    for value in (resolved or {}).values():
        if value in (None, "", [], {}):
            continue
        return True
    return False


def _to_business_content(resolved):
    """Flatten resolved content_refs into the builder's business_content dict.

    Strings/lists pass through; structured objection/faq dicts are expanded into
    readable lines so the builder can use them verbatim (matching the builder
    prompt's "one item per line -> separate cards" contract).
    """
    out = {}
    for slot, value in (resolved or {}).items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            flattened = [_flatten_value(v) for v in value]
            out[slot] = [v for v in flattened if v]
        else:
            out[slot] = _flatten_value(value)
    return {k: v for k, v in out.items() if v not in (None, "", [], {})}


def _flatten_value(value):
    """Render a single resolved value (str or objection/faq dict) for the builder."""
    if isinstance(value, dict):
        if "question" in value or "answer" in value:
            q = str(value.get("question") or "").strip()
            a = str(value.get("answer") or "").strip()
            return f"Q: {q} A: {a}".strip() if (q or a) else ""
        if "concern" in value or "response" in value:
            c = str(value.get("concern") or "").strip()
            r = str(value.get("response") or "").strip()
            return f"{c} — {r}".strip(" —") if (c or r) else ""
        return str(value.get("content") or "")
    return str(value) if value is not None else ""


def _describe(section_type, purpose, resolved):
    """Build a short section description for the builder's search query."""
    label = (purpose or section_type or "section").replace("_", " ")
    base = f"{label} section"
    for value in (resolved or {}).values():
        snippet = _flatten_value(value if not isinstance(value, list) else (value[0] if value else ""))
        snippet = (snippet or "").strip()
        if snippet:
            excerpt = snippet[:140] + "..." if len(snippet) > 140 else snippet
            return f"{base} — {excerpt}"
    return base


def _style_notes(section_purpose):
    """Surface per-purpose persuasion guidance as builder style notes."""
    roles = section_purpose.get("preferred_persuasion_roles") or []
    if not roles:
        return ""
    pretty = ", ".join(r.replace("_", " ") for r in roles)
    return f"Lead with {pretty}."
