# Swift Sites → Marketing Campaign Engine (North Star + Phased Roadmap)

## Context
The product is being repositioned: it is **no longer "a website generator"** — it is a **marketing
campaign engine** that happens to produce websites as one of several campaign outputs. This document
reframes the product's north star and folds every prior decision (RAG header/footer, unified content model,
recipes-as-categories, goal mapping, brand guardrails) under this banner, then lays out a phased build
sequence.

Scope: **both multi-channel + closed-loop, sequenced** — measurement/closed-loop first (it leverages what
already exists), then multi-channel expansion.

Related docs: [strategy imp.md](strategy%20imp.md), [RAG_BRAND_HEADER_FOOTER_PLAN.md](RAG_BRAND_HEADER_FOOTER_PLAN.md),
[BRAND_FIELDS_USAGE_PLAN.md](BRAND_FIELDS_USAGE_PLAN.md),
[CONTENT_LIBRARY_CAMPAIGN_SYSTEM_EXPLAINED.md](CONTENT_LIBRARY_CAMPAIGN_SYSTEM_EXPLAINED.md),
[SEMANTIC_LAYER_ONTOLOGY.md](SEMANTIC_LAYER_ONTOLOGY.md).

---

## North Star
A marketer describes **one campaign** (who, what, goal). The engine generates a **coordinated set of
assets** from a single typed-content core (landing page first; email, ads, social next), publishes them,
**measures conversions per campaign**, and **promotes what works** back into the content library to make the
next campaign better. Brand defines the look + voice; recipes define the campaign type; content is the
shared, typed substance that flows across channels and improves over time.

```
BRAND ──┐
        ▼
   CAMPAIGN (brief + goal → recipe auto-selected)
        │   one typed-content core (headline/benefit/proof/offer/faq/cta...)
        ├──► LANDING PAGE        (built today)
        ├──► EMAIL / ADS / SOCIAL (modeled, unbuilt — Phase 3)
        ▼
   PUBLISH → public URL  (built today, site-level)
        ▼
   MEASURE  (submissions per campaign → conversion metrics — Phase 2)
        ▼
   LEARN    (promote performance_winner content back to library — Phase 2/4)
        └──► feeds the NEXT campaign
```

## Where we are (verified inventory)
**Wired end-to-end today:** 6-step Campaign Studio (brief/audience/goal/offer/messages) →
message generation via RAG → landing-page generation + per-section regenerate
(`routes/campaign.py`, `static/js/campaignStudio.js`) → Site/SitePage creation → publish to `/s/{slug}`
(`routes/site.py`, `routes/published.py`).

**Modeled but dormant (schema exists, no logic):**
- `Campaign.status` draft/active/paused/completed — no lifecycle transitions.
- `Site.campaign_id` EXISTS (models.py:70) — so campaign↔site is already linked.
- Channels `email/ad/social/ecommerce` + content types `ad_copy/email_subject/social_post` exist in the
  catalog (`campaign/content_type_catalog.py`) but only `landing_page` is generated.
- `ContentItem.source='performance_winner'` and `quality_score` — never set.
- `CampaignMessage.used_in_section` — never populated.

**Entirely missing:** campaign-scoped conversion metrics, A/B testing, multi-channel generation/export,
scheduling/automation, CRM/email-platform/analytics integrations.

**Key leverage point:** conversion attribution is ONE JOIN away — `FormSubmission.site_id → Site.campaign_id`.
No new core wiring needed to start measuring; `FormSubmission` only needs campaign attribution surfaced.

## Strategic pillars (reframes prior decisions under the engine banner)
1. **Typed content is the substance, channels are renderings.** The unified-content-model decision (campaign
   offer fields → typed `ContentItem`s with slots) becomes the engine's backbone: the same headline/benefit/
   proof renders to a page section, an email block, an ad variant. One core, many outputs.
2. **Recipes are campaign types.** Recipe = campaign category; `goal`→`conversion_goal` mapping
   (`vocabulary.py derive_conversion_goal`) feeds the scorer. Expanding the engine = adding recipes, not
   enlarging forms.
3. **Brand is the consistency layer.** Brand voice/theme (+ RAG header/footer, the active build plan) and
   brand guardrails (see BRAND_FIELDS_USAGE_PLAN.md) guarantee every channel asset looks and sounds like the
   brand — and stays compliant.
4. **The loop is the moat.** Publish → measure → promote winners → reuse. This is what turns a generator into
   an *engine*.
5. **Media is sourced, then attached.** Every image slot is filled by a fallback ladder — **owned**
   (brand-tagged / product / curated) → **auto-sourced stock** by section concept → **generated** (future).
   Attachment still layers brand → product → campaign → content. The dominant marketer need is *sourcing*
   ("find me a hero of X") then *inline swap*, not up-front curation. Today the campaign section/content layer
   is media-blind and generation never auto-sources — see [MEDIA_USAGE_PLAN.md](MEDIA_USAGE_PLAN.md).

---

## Phased roadmap

### Phase 0 — In flight (already planned)
RAG-driven brand-aware header/footer + semantic retrieval ([RAG_BRAND_HEADER_FOOTER_PLAN.md](RAG_BRAND_HEADER_FOOTER_PLAN.md)).
Keep; it is the brand-consistency foundation every channel depends on.

### Phase 1 — Unify the content core (foundation for everything)
Make campaign offer fields (benefits/proof/objections/faqs) persist as typed `ContentItem`s with slots, so
campaign and library share one source of truth, and auto-populate the library from kept campaign messages.
This is the substrate multi-channel rendering needs. (Builds on the "unify the model" decision in
[strategy imp.md](strategy%20imp.md).)

### Phase 1b — Brand guardrails: enforce at the CONTENT gate
Make content creation the guardrail enforcement gate (inject + validate forbidden/required/compliance rules
where content is born, so sections and all channels inherit compliant copy). **Full detail:**
[BRAND_FIELDS_USAGE_PLAN.md](BRAND_FIELDS_USAGE_PLAN.md). Done alongside Phase 1, since both live in the
content core.

### Phase 2 — Close the loop (measurement first — highest leverage, lowest new wiring)
- Attribute `FormSubmission` to a campaign via `Site.campaign_id` (surface the existing join; add
  `campaign_id` denormalized on submission only if query ergonomics require).
- Campaign-scoped views: submissions + a simple conversion metric (visits→submissions) per campaign.
- Campaign lifecycle: activate/pause/complete transitions actually do something (e.g. published+active).
- Seed `quality_score` / `performance_winner` from real submission data → "promote winning copy" action.
- **Media — auto-source + plumbing** (highest marketer value; see [MEDIA_USAGE_PLAN.md](MEDIA_USAGE_PLAN.md)):
  hybrid sourcing — planner emits a per-section image query, generation prefers owned media and **falls back
  to auto stock search** so empty-library campaigns return real imagery, not placeholders. Plus low-risk
  fixes: pass images into `generate_section_yaml` (media-blind today), fix `regenerate_section`'s hardcoded
  empty list, resolve the unused `Brand.logo_media_id` / `Product.default_media_id`, and inline image swap in
  Campaign Studio (no more jump to the full editor).

### Phase 3 — Multi-channel asset generation (breadth)
One campaign brief → coordinated asset set. Reuse the existing RAG section pipeline pattern + the typed
content core from Phase 1 to generate `email_subject`/`ad_copy`/`social_post` (channel-affinity already in
the catalog). Add channel tabs in Studio + export (copy/CSV) before any external API integrations.
- **Media — brand library + curation override** (see [MEDIA_USAGE_PLAN.md](MEDIA_USAGE_PLAN.md)): add an
  optional `brand_id` **tag** on media so a brand's photos ("upload once, reuse across campaigns") rank first
  in the sourcing ladder; per-campaign curation (`CampaignMedia`) becomes a light "pin the hero / drop this
  one" override, not the entry point. Chosen images travel across page + email/ad/social. *(AI-generated media
  is a noted future ladder rung — owned → stock → generated.)*

### Phase 4 — Automation & integrations (scale)
Scheduling (launch/expiry tied to lifecycle), recurring/evergreen campaign templates, and outbound
integrations (email platforms, ad platforms, GA4/analytics, CRM). Largest surface; do last.

## Recipe library expansion (cross-cutting, supports Phases 2-3)
Author campaign-type recipes beyond the current 2 (product launch, webinar/event, ecommerce sale, free
trial, waitlist, newsletter), each declaring its content-type set + section sequence; extend
`derive_conversion_goal` + `CONVERSION_GOAL` as new types need finer intents. See [strategy imp.md](strategy%20imp.md)
"Campaign categories = recipes".

## Out of scope
This is a positioning + sequencing document. Each phase gets its own build plan when picked up.
