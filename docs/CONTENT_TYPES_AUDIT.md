# Content Types in Swift Sites — Audit

> Read-only audit of every "content type" catalog in the codebase: where each is
> defined, where it is consumed, how they relate, and where they diverge.
> **Last reviewed:** 2026-06-11.

## ✅ Resolution (2026-06-29) — canonical registry

Findings 1 & 2 below are **resolved**. The two marketing content-type catalogs
no longer drift: both are now **derived from one canonical registry**,
[campaign/content_registry.py](../ssr_python/campaign/content_registry.py).

- Each concept is declared **once**, carrying the name it uses in each view
  (`catalog_key` for the Library catalog / `ContentItem.category`, `ontology_key`
  for `vocabulary.CONTENT_TYPE`). The silent `headline`↔`title`,
  `product_feature`↔`feature`, `form`↔`form_spec` divergence is now an explicit,
  tested mapping.
- `vocabulary.CONTENT_TYPE`, `COMPOSITE_TYPES`, and `GROUP_KEY_TO_TYPE` are
  computed from the registry (`vocabulary.py`); `content_type_catalog.CONTENT_TYPES`
  + all slot schemas are computed from the registry (`content_type_catalog.py`).
  Both kept their public symbols/functions, so every existing importer is
  unaffected (verified: full catalog is byte-identical to the pre-refactor data).
- **The library↔compiler bridge is no longer lossy** (Finding 2): a stored ORM
  `ContentItem` can be turned into the recipe engine's normalized typed-item shape
  via `content_registry.normalize_content_item()` / `normalize_content_items()`,
  which maps `category`→ontology type so `content.<group>` refs resolve through
  the standard `content_refs` resolver. This is the substrate Phases B and C use.
- Parity is pinned by `tests/test_campaign_content_registry.py`.

The remaining sections below describe the **pre-resolution** state for historical
context (channel-vs-on-page mixing and rendering-coverage gaps, Findings 3-5,
are still open).

## TL;DR

- There are **two marketing content-type catalogs** that are *meant* to describe the same thing but don't match:
  - `ContentItem.VALID_CATEGORIES` — **25** durable Content-Library categories ([models.py:940](../ssr_python/models.py#L940)).
  - `vocabulary.CONTENT_TYPE` — **32** campaign-compiler semantic types (15 primitive + 15 composite + 2 shorthand) ([campaign/vocabulary.py:83](../ssr_python/campaign/vocabulary.py#L83)).
- They share **14 names exactly**, but encode **equivalent concepts under different names** (`headline`↔`title`, `product_feature`↔`feature`, `form`↔`form_spec`, `promotion`↔offer-style), and each has members the other lacks.
- Two more "type" systems share vocabulary but are unrelated to marketing content: **RAG doc types** (7, template indexing) and **renderer component types** (~30, HTML output).
- The bridge between the library and the compiler is thin: `GROUP_KEY_TO_TYPE` (12 entries) and `content_preview.py`'s `category→component` map. Several library categories have **no compiler path** and only render as a generic title+paragraph.

---

## The four "type" systems

| # | System | Source of truth | Count | Scope / lifecycle |
|---|--------|-----------------|-------|-------------------|
| 1 | **Content-Library category** (`ContentItem.category`) | [models.py:940](../ssr_python/models.py#L940) `VALID_CATEGORIES` | 25 | Durable DB asset; user-facing tag + filter in the library UI |
| 2 | **Semantic content type** (normalized `type`) | [campaign/vocabulary.py:83](../ssr_python/campaign/vocabulary.py#L83) `CONTENT_TYPE` | 32 | Per-campaign, in-memory; drives recipe selection + section building |
| 3 | **RAG doc type** | [rag/config.py](../ssr_python/rag/config.py) `tier_doc_types` | 7 | Per-chunk in the search index; tiered retrieval routing |
| 4 | **Renderer component type** | [rag/indexing/metadata.py:46](../ssr_python/rag/indexing/metadata.py#L46) `COMPONENT_TYPES` | ~30 | Per-node in the final HTML component tree |

Systems **3 and 4 are not marketing-content concepts** — they describe templates and rendered components. They reuse words like `cta`/`testimonial` (doc/section metadata) and `heading`/`button`/`badge` (components), which is the main source of confusion. They are out of scope for "content types" except to note the naming collision.

---

## System 1 — Content-Library categories (25)

Verbatim ([models.py:940-946](../ssr_python/models.py#L940)):

```
headline, subheadline, tagline, benefit, testimonial, case_study, about,
cta, boilerplate, faq, offer, promotion, proof, objection, product_feature,
product_spec, comparison, form, value_proposition, guarantee, seo_meta,
ad_copy, email_subject, social_post, announcement
```

Companion enums on the same model: `VALID_STATUSES` (draft/approved/active/archived/expired), `VALID_SOURCES` (manual/ai/campaign/import/performance_winner), `VALID_CHANNELS` (general/landing_page/email/ad/social/ecommerce), `VALID_PERMISSION_STATUSES`.

**Defined / validated / exposed:**
- Validation on create/update: [routes/brand.py:431](../ssr_python/routes/brand.py#L431) `_apply_content_fields()` (400 if `category ∉ VALID_CATEGORIES`).
- Exposed to UI: `GET /api/content/options` → `sorted(VALID_CATEGORIES)` ([routes/brand.py:529](../ssr_python/routes/brand.py#L529)).
- Filtered: `GET /api/content?category=…` ([routes/brand.py:546](../ssr_python/routes/brand.py#L546)).
- UI labels: `categoryLabel()` ([dashboard-v2.js:2141](../ssr_python/static/js/dashboard-v2.js#L2141)) — only 10 categories get pretty labels; the other 15 fall back to `capitalize(replace(_," "))`.
- Per-category preview rendering: `content_item_to_components()` ([campaign/content_preview.py:33](../ssr_python/campaign/content_preview.py#L33)).

---

## System 2 — Semantic content types (32)

Verbatim ([campaign/vocabulary.py:83-101](../ssr_python/campaign/vocabulary.py#L83)):

- **Primitive (15)** — single string value:
  `title, subheadline, eyebrow, paragraph, tagline, cta_label, link, stat, rating, quote, image_ref, icon_ref, badge_label, question, answer`
- **Composite (15)** — extra fields in `structured_payload` (`COMPOSITE_TYPES`):
  `cta, value_proposition, benefit, feature, offer, testimonial, proof, case_study, faq, objection, guarantee, comparison, announcement, form_spec, narrative`
- **Campaign shorthand (2)**: `pain_point, promise`

**Companion semantic dimensions** (same module, used as tags / anti-hallucination controls): `TRUTH_LEVEL` (verified/approved/inferred/generated/experimental), `SOURCE` (10), `CHANNEL` (6), `PERSUASION_ROLE` (16), `EMOTION` (15), `PROOF_TYPE` (13), `SPECIFICITY_LEVEL` (4), `COMPLIANCE_SENSITIVITY` (4).

**Defined / validated / consumed:**
- Validated in campaign YAML: [campaign/validators.py](../ssr_python/campaign/validators.py) `_validate_content_block()` (type must ∈ `CONTENT_TYPE`).
- Normalization: [campaign/content.py](../ssr_python/campaign/content.py) turns grouped shorthand or typed lists into `{id,type,content,truth_level,source,structured_payload?,tags?}`; object groups `{objections, faqs, testimonials}` extract structured fields.
- Group→type bridge: `GROUP_KEY_TO_TYPE` (12 entries, [vocabulary.py:175](../ssr_python/campaign/vocabulary.py#L175)).
- Recipe scoring: [campaign/recipes.py](../ssr_python/campaign/recipes.py) matches a recipe's `required_content_types` against `available_types()`.
- Refs + section builders: [campaign/content_refs.py](../ssr_python/campaign/content_refs.py) resolve `content.<group>[i]`; [campaign/section_builders.py](../ssr_python/campaign/section_builders.py) build component trees from **resolved slot values** (not from `type` directly).

---

## The mismatch (key finding)

Comparing the 25 library categories against the 32 semantic types:

**Exact-name overlap (14):** `subheadline, tagline, benefit, testimonial, case_study, cta, faq, offer, proof, objection, comparison, value_proposition, guarantee, announcement`.

**Same concept, different name (silent divergence):**

| Library category | Semantic type | Bridged? |
|---|---|---|
| `headline` | `title` | preview maps `headline`→heading L1; no name link to `title` |
| `product_feature` | `feature` | preview maps both to heading+paragraph; names differ |
| `form` | `form_spec` | no shared handling |
| `promotion` | — (none) | preview folds `promotion` into offer-style render |

**Library-only categories (no semantic type, 11):** `headline, about, boilerplate, promotion, product_feature, product_spec, form, seo_meta, ad_copy, email_subject, social_post`.

**Semantic-only types (no library category, 18):** `title, eyebrow, paragraph, cta_label, link, stat, rating, quote, image_ref, icon_ref, badge_label, question, answer, feature, form_spec, narrative, pain_point, promise`. (Most are *primitive* sub-parts that composites decompose into, so it's expected they aren't user-saved categories — but `pain_point`, `promise`, `narrative`, `stat` are campaign-meaningful and have no durable home.)

---

## Rendering coverage gap

`content_item_to_components()` ([content_preview.py:45-104](../ssr_python/campaign/content_preview.py#L45)) gives explicit, tailored rendering to ~14 categories. The remaining ones hit the `else` branch and render as **generic title + paragraph**:

`about, boilerplate, guarantee, ad_copy, email_subject, social_post, seo_meta, form` (+ any unknown).

Implication: categories like `seo_meta`, `email_subject`, `social_post`, `form` are **storable and filterable but have no meaningful page representation** — they're channel artifacts (email/social/SEO/forms) being kept in the same catalog as on-page copy. `guarantee` notably renders generically even though the compiler treats it as a composite type.

---

## Findings summary

1. **Two catalogs, one concept, no single source of truth.** `VALID_CATEGORIES` (25) and `CONTENT_TYPE` (32) describe overlapping marketing content but are maintained independently and disagree on names (`headline`/`title`, `product_feature`/`feature`, `form`/`form_spec`) and membership.
2. **Thin, lossy bridge.** Only `GROUP_KEY_TO_TYPE` (12) and the preview `category→component` map connect them. A library item's `category` is never translated to a semantic `type` for compilation — the library and the compiler are effectively separate type spaces.
3. **Channel vs. on-page mixing.** Library categories conflate on-page copy (`headline`, `benefit`, `cta`) with off-page channel artifacts (`email_subject`, `social_post`, `seo_meta`, `ad_copy`), which is why ~8 categories have no real rendering.
4. **Orphan semantic types.** `pain_point`, `promise`, `narrative`, `stat` matter to recipes/sections but have no durable library category, so they can't be authored/reused as standalone assets.
5. **Naming collisions across unrelated systems.** `cta`/`testimonial` appear in content types, RAG section metadata, and `PROOF_TYPE`; `badge`/`heading`/`button` are renderer components, not content. Worth naming these tiers explicitly in any future doc.

---

## App strategy: Content vs Sections

The intended product model (confirmed) resolves several of the findings above:

- **Primitive vs composite is an internal property of a content type, not a behavioral split.** Both are just kinds of content (`primitive` = single text value; `composite` = a few structured fields in `structured_payload`). They are authored, stored, filtered, and rendered the same way — the distinction does not change a content item's characteristics or get its own UI.
- **The Content page has two tabs, on a different axis than primitive/composite:**
  - **Content** — the existing reusable marketing **atoms** (facts & truths): the brand's verified claims, offers, testimonials, stats, FAQs, CTAs, etc. Single-source-of-truth content.
  - **Sections** — first-class, reusable **page blocks composed from content items**. A section is an *ordered composition* of existing content items (not a slot template), rendered with the brand theme.
- **Sections are the durable bridge between atoms and pages.** Previously sections existed only ephemerally inside the campaign compiler (recipes → section_builders); making them a CMS asset means a marketer can curate a block once and reuse it.
- **Live binding (single source of truth).** A section stores *references* to content items (ordered ids) plus its layout — never a frozen copy. It re-renders on demand from the current content values and the current brand theme, so editing an item or the brand propagates to every section (and, in future, every page) that uses it. This reuses the same render path as the per-item content preview (`content_item_to_components` → `render_yaml_structure` with `brand_to_theme`).
- **v1 scope:** create + live preview of sections; single stacked centered-column layout; composition-based. Inserting saved sections into pages/sites, and multi-column/split layouts, are deferred follow-ups.

This does **not** unify the two type catalogs (Finding 1) — that remains open — but it does establish where reusable, page-ready blocks live, addressing the "sections aren't first-class assets" gap implied by Finding 4.

---

## Source references

- `VALID_CATEGORIES` — [models.py:940](../ssr_python/models.py#L940)
- `CONTENT_TYPE` / `COMPOSITE_TYPES` / `GROUP_KEY_TO_TYPE` — [vocabulary.py:83](../ssr_python/campaign/vocabulary.py#L83), [vocabulary.py:175](../ssr_python/campaign/vocabulary.py#L175)
- Category→component preview map — [content_preview.py:33](../ssr_python/campaign/content_preview.py#L33)
- UI category labels — [dashboard-v2.js:2141](../ssr_python/static/js/dashboard-v2.js#L2141)
- Content options + filter endpoint — [brand.py:529](../ssr_python/routes/brand.py#L529)
- Campaign content validation — [campaign/validators.py](../ssr_python/campaign/validators.py) `_validate_content_block()`
