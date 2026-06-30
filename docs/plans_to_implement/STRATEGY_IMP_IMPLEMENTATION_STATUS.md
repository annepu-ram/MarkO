# strategy imp.md — Implementation Status

Tracks what is **built + tested** vs **remaining** for the technical plan in
[STRATEGY_IMP_IMPLEMENTATION.md](STRATEGY_IMP_IMPLEMENTATION.md) (source plan:
`.claude/plans/analyze-issues-with-brand-memoized-spring.md`).

**Last updated:** 2026-06-30.

Dependency order shipped so far: **A → B0 → B → C (+C2 partial)**. Remaining: rest
of C2 (structured product context) + **D** (recipe pre-generation).

---

## ✅ Done & tested

### Phase A — Goal as scored input + expanded mapping
- `campaign/vocabulary.py::derive_conversion_goal` now takes `awareness_stage` +
  `traffic_source` (keyword args, backward compatible) and reaches refined goals
  no user goal hit before: `appointment_booking` (calls + impulse/transactional/
  seasonal), `repeat_purchase`/`upsell` (sales + retention/expansion lifecycle),
  `trial_signup` (signups + recurring), `webinar_registration` (webinar traffic).
  User `goal` list stays 6; only the **mapping** expanded (decision 3).
- `page_compiler.py` passes the new signals through.
- Tests: `tests/test_campaign_schema.py` — every `USER_GOAL × sales_cycle ×
  awareness` resolves to a valid `CONVERSION_GOAL`; old positional calls still work.

### Phase B0 — Canonical content-type registry (keystone)
- **New** `campaign/content_registry.py` — one entry per content concept carrying
  both names (`catalog_key` ↔ `ontology_key`), slot schema, family, group_key,
  channel affinity. Resolves the two-vocabulary divergence.
- `vocabulary.py` (`CONTENT_TYPE`/`COMPOSITE_TYPES`/`GROUP_KEY_TO_TYPE`) and
  `content_type_catalog.py` (`CONTENT_TYPES` + all slot schemas) are now **derived**
  from the registry. Verified byte-identical to the pre-refactor catalog.
- ORM→normalized bridge: `normalize_content_item()` / `normalize_content_items()`
  map a stored `ContentItem` into the recipe engine's typed-item shape so
  `content.<group>` refs resolve via the standard `content_refs` resolver.
- Audit updated: [docs/CONTENT_TYPES_AUDIT.md](../CONTENT_TYPES_AUDIT.md) "Resolution".
- Tests: `tests/test_campaign_content_registry.py` (20).

### Phase B — Unified data model (campaign offer = ContentItem)
- **New** `campaign/offer_sync.py`:
  - `build_campaign_content_item(...)` — single shared ContentItem constructor.
  - `sync_offer_to_content_items(campaign)` — idempotent upsert of offer fields
    (offer/CTAs/benefits/proof/objections/faqs) into typed `ContentItem` rows;
    prunes removed offer-derived items; never touches message-derived items.
- Offer PATCH ([routes/campaign.py](../../ssr_python/routes/campaign.py)) dual-writes:
  `CampaignOffer` columns stay the read source; ContentItems materialize as a side
  effect so the Library auto-populates.
- `routes/brand.py::save_from_campaign` reuses the shared constructor (one code path).
- Tests: `tests/test_campaign_offer_sync.py` (8).

### Phase C — Recipes select, RAG fills (the spine)
- **New** `campaign/section_mapper.py::build_recipe_sections(...)` — selects a
  recipe (scored, explainable; honors an explicit pinned id), then maps its
  `section_sequence` → guided-flow section dicts: purpose→builder `section_type`,
  `content_refs` resolved against typed content → each section's `content`,
  `section_purposes.allowed_components` → builder component allow-list, optional
  empty sections dropped.
- `compiler.py::compile_to_business_context` now calls the mapper
  (`_build_recipe_driven_sections`) instead of hardcoded `_build_guided_sections`;
  legacy outline kept as a **graceful fallback** if no usable recipe sequence.
- `planner_agent.py::plan_from_context` honors recipe-provided `components` /
  `style_notes` / `conversion_intent` instead of generic per-type defaults.
- Tests: `tests/test_campaign_section_mapper.py` (16) + updated
  `tests/test_campaign.py::TestCompileToBusinessContext` to the recipe contract.

### Phase C2 — Campaign-conditioned generation (partial)
- **Done:** goal → `conversion_intent` (`CONVERSION_GOAL_TO_INTENT`, 14→5) threaded
  into the builder via section dicts + top-level `business_context['conversion_intent']`;
  `rag_agent._create_page_guided` passes it to `builder.build_section`. Per-section
  content comes from typed `ContentItem`s (via the mapper) — real benefits/proof/
  offer/FAQ verbatim, not invented.
- Tests: intent mapping covered in `test_campaign_section_mapper.py`
  (`TestConversionIntent`); compiler test asserts `conversion_intent == 'lead'`.

---

## ⏳ Remaining

### Phase C2 (remainder) — structured product context per section
**Goal:** product facts (name/price/availability/description) should reach the
offer/pricing/features sections as **structured** `content`, not just appended to
the global `description` prose blob ([compiler.py:104-117](../../ssr_python/campaign/compiler.py#L104)).
**Approach (not yet wired):**
- Pass `products` (already loaded in `generate_page`) into
  `_build_recipe_driven_sections` → the mapper.
- In the mapper, for sections whose purpose ∈ {`offer_highlight`, `pricing_table`,
  `comparison_table`, `feature_grid`}, merge a structured `product` block into
  `content` (name, price+currency, availability, short description).
- Keep the prose-blob fallback for the legacy path.
- Tests to add: a campaign with a product generates an offer/features section whose
  `content` carries the exact product facts.

*Note:* brief/offer field→section guidance (audience→hero/about, objections→
objection_handling) is **already** handled by the recipe `content_refs`, so no
extra work there beyond authoring recipes that reference those fields (Phase D).

### Phase D — Pre-generate a recipe library
Nothing built yet. Plan:
1. **Expand `campaign/section_purposes.yaml`** (currently 7) with the atoms new
   recipes need: hero variants, benefit/feature grids, pricing, urgency/countdown,
   signup form, social proof, comparison, FAQ, about/story, trust badges, stats.
   The mapper's `PURPOSE_TO_SECTION_TYPE` already has entries for these names —
   add the matching purpose definitions and keep the two in sync. Validate each via
   `validators.validate_section_purpose`.
2. **New** `campaign/scripts/generate_recipes.py` — per archetype (curated
   `conversion_goal × awareness_stage × modifiers`), prompt an LLM with the
   available section_purposes + dimension vocab → recipe YAML; deterministic
   post-step validates with `validators.validate_recipe`, rejects unknown
   purposes/types, dedupes by `applies_when` signature.
3. **Store** generated recipes under `campaign/recipes/generated/*.yaml`
   (`recipes.load_recipes` already globs the dir). Review in PR; CI validates.
4. Selection scales automatically (scorer ranks the bigger pool — no engine change).
5. Tests: every generated recipe passes `validate_recipe`; representative contexts
   select sensible recipes; every `required_content_type` is a real registry type;
   every recipe purpose exists in `section_purposes.yaml`.

### Cleanup / follow-ups (deferred, from the plan's transition notes)
- `CampaignOffer` column deprecation: after a release of dual-write, add a backfill
  script and switch reads to ContentItems, then drop the columns. (Currently
  dual-write only.)
- Optional: surface `business_context['recipe']['explanation']` ("why this layout")
  in the Campaign Studio UI.

---

## How to verify what's done
```bash
cd ssr_python
python -m pytest tests/test_campaign_schema.py tests/test_campaign_content_registry.py \
  tests/test_campaign_offer_sync.py tests/test_campaign_section_mapper.py \
  tests/test_campaign_compiler.py tests/test_campaign.py -v
```
Manual: PATCH a campaign offer → items appear in the Content Library (typed);
`POST /api/campaigns/<id>/generate-page` selects a recipe (see
`business_context['recipe']` / logs) and builds its section sequence from the
campaign's typed content; changing the goal/awareness selects a different recipe
and shifts the builder's `conversion_intent`.
