# Swift Sites - Campaign Compiler Implementation Brief

## 1. Direction

Swift Sites should evolve from a YAML-based website builder into a structured campaign intelligence platform.

The product should not be positioned as another AI website generator, no-code page builder, drag-and-drop CMS, or generic marketing automation suite. The stronger position is:

> A campaign intelligence layer that compiles structured business truth into synchronized multi-channel marketing outputs.

The current product already has a working server-side renderer, a browser editor, component selection, property editing, image management, site/page persistence, and an AI/RAG pipeline that generates renderer-compatible YAML. The next layer should not replace that foundation. It should compile higher-level campaign intent into the existing page YAML shape.

Current production model:

```text
Renderer-compatible YAML -> Flask/Jinja SSR -> iframe preview/export/publish
```

Target model:

```text
Business truth
  -> campaign context
  -> structured campaign graph
  -> typed content (Content Library: primitive + composite, semantically tagged)
  -> recipe selection
  -> channel compiler
  -> existing renderer-compatible YAML
  -> landing page first
  -> email/ad/social/SEO outputs later
  -> analytics feedback
```

The existing renderer remains the presentation layer. The campaign source graph becomes the planning/source layer above it. YAML can be the first serialized representation of that graph, but YAML itself is not the moat. The moat is structured campaign intelligence: a typed, semantically tagged Content Library, campaign memory, performance-aware recipes, synchronized messaging, and deterministic output generation.

> Terminology decision (supersedes earlier "semantic atoms" framing): **Atoms are not a separate model. They are Content Library items.** The Content Library stores **typed content** — primitive types (title, paragraph, cta_label, image_ref, stat, quote…) and composite types built from primitives (cta, offer, testimonial, benefit, faq…) — each carrying **semantic tags** (persuasion_role, awareness_stage, truth_level, emotion, etc.). Where this brief says "atom," read it as "a Content Library item viewed through its type + semantic tags during compilation." The authoritative type catalog and tag schema live in `docs/plans_to_implement/SEMANTIC_LAYER_ONTOLOGY.md` and the content-types catalog. The compiler consumes typed, tagged content from the Content Library plus campaign/brand/product/media records; it does not require a separate atom table in V1.

The website is the first output channel because the renderer already exists. It should not remain the primary product object. The campaign is the primary source object.

## 2. Current Implementation To Preserve

The live app is under `ssr_python/`, not a generic `app/` package.

Product-state note:

- The app does not have production users yet, so implementation does not need to preserve backward compatibility for existing saved customer sites.
- We can change the internal YAML/source model if it gives a cleaner long-term architecture.
- We still need a deliberate migration of repository-owned assets: `example_templates/`, tests, RAG references, default page YAML, and generated examples must be updated to the new model in the same implementation phase.
- Do not carry compatibility shims indefinitely just to support old local/dev YAML examples. Prefer one clean source format and convert the examples.

Important current facts:

- Flask app factory: `ssr_python/app.py`
- Main render endpoint: `ssr_python/routes/render.py`, `POST /render`
- Renderer entry point: `ssr_python/renderer.py::render_yaml_structure(structure, tokens, defaults)`
- Component defaults: `ssr_python/config/component_defaults.yaml`
- Inspector schemas: `ssr_python/config/component_schemas.yaml`
- Token options: `ssr_python/config/schema_tokens.yaml`
- Design tokens: `ssr_python/tokens.yaml`
- Component syntax/RAG guide: `ssr_python/config/COMPONENT_SYNTAX_REFERENCE.md`
- Style RAG guide: `ssr_python/config/STYLE_THEMES_REFERENCE.md`
- AI/RAG pipeline: `ssr_python/rag/agent/`
- Current tests: `ssr_python/tests/`
- Current examples: `example_templates/`

Current renderer-compatible YAML is a list of components. Components use `name`, optional `properties`, and nested `components`. It does not use `page.sections`, `component`, or `props`.

Example current shape:

```yaml
- name: site
  properties:
    theme:
      colors:
        primary: "#111827"
        text: "#374151"
        secondary: "#6b7280"
        accent: "#6366f1"
        background: "#ffffff"
  components:
    - name: page
      slug: home
      title: Campaign Landing Page
      properties:
        appearance:
          background:
            color: "#ffffff"
            opacity: 100
      components:
        - name: layout-row
          properties:
            layout:
              tag: section
              horizontalAlign: center
              verticalAlign: center
              wrap: wrap
            spacing:
              paddingBlock: xxxl
              paddingInline: xl
          components:
            - name: layout-column
              properties:
                layout:
                  widthMode: "60"
                  gap: md
              components:
                - name: heading
                  properties:
                    text: Build campaign assets from one source
                    level: 1
                - name: paragraph
                  properties:
                    text: Generate landing pages, emails, and ads without duplicating content.
                - name: button
                  properties:
                    text: Generate Campaign
                    action:
                      type: link
                      href: "#lead"
```

All campaign work must compile into this shape before calling the renderer.

## 3. Product Thesis

Swift Sites should not become a generic AI website builder.

It should be positioned as:

> A structured campaign compiler that turns business truth and campaign context into landing pages first, then emails, ads, social posts, SEO pages, and analytics-ready marketing assets.

The differentiator is not AI generation, YAML, templates, or website rendering. The differentiator is structured campaign intelligence.

Specifically:

- a typed, semantically tagged Content Library (reusable marketing units)
- campaign memory
- recipe strategy by audience, channel, and buying context
- synchronized multi-channel outputs
- deterministic rendering
- analytics-linked learning loops

Long-term, the system should learn patterns like:

```text
Audience X
+ Offer Y
+ Traffic source Z
+ Funnel stage N
= Recipe A converts best
```

Execution systems such as HubSpot, Mailchimp, Meta Ads Manager, Buffer, Salesforce, and CRMs should remain external. Swift Sites should own the campaign source and feed those systems, not replace them.

## 4. Layered Architecture

Recommended architecture using the current codebase:

```text
Layer 1: Business truth intake
Layer 2: Campaign context
Layer 3: Structured campaign graph
Layer 4: Existing RAG/LLM pipeline, extended for campaign extraction
Layer 5: Campaign YAML/JSON draft as serialized source graph
Layer 6: Campaign schema validation
Layer 7: Typed content normalization and content reference resolution
Layer 8: Recipe selection
Layer 9: Channel compiler
Layer 10: Existing renderer-compatible YAML for landing pages
Layer 11: Existing Flask/Jinja renderer
Layer 12: Existing preview/export/publish flow
Layer 13: Future email/ad/social/SEO outputs and analytics
```

The important boundary:

```text
campaign YAML != renderer YAML
```

Campaign YAML is semantic and strategic. Renderer YAML is concrete visual component data.

Conceptually, campaign YAML should represent a structured campaign graph:

```text
Brand
Product or offer
Audience
Traffic source
Funnel stage
Sales cycle
Proof
Objections
Typed content (Content Library items)
Recipe
Channel outputs
Analytics IDs
```

The serialized format can stay simple in phase 1, but the domain model should be designed around campaign intelligence rather than page structure.

## 4.1 Human Truth vs AI Adaptation

A critical architectural principle:

```text
Humans own truth.
AI owns adaptation.
```

Truth includes:

- pricing
- availability
- testimonials
- company facts
- customer counts
- case studies
- product capabilities
- compliance constraints
- proof sources

AI must not invent or silently change truth when a brand, product, campaign, or content-library record already defines it.

AI may adapt:

- headlines
- hooks
- CTA variants
- emotional framing
- channel-specific rewrites
- ad/email/social variants
- section copy derived from verified content

This separation reduces hallucinations and makes the compiler reliable. The deterministic campaign compiler should treat AI output as draft data that validates against known truth before it reaches rendering.

## 4.2 Truth Collection Strategy

Truth acquisition is a product problem, not just an AI prompt problem. Businesses do not naturally store marketing truth in one structured place.

Truth can come from:

- conversational campaign intake
- brand and product records
- approved content library items
- uploaded media and metadata
- websites
- PDFs, decks, case studies, and onboarding documents
- CRM segments and lifecycle data later

MVP truth collection should focus on manual brand/product/content entry plus conversational campaign intake. Website crawling, document import, and CRM integrations can come later, but the typed-content model should be ready to accept those sources.

## 5. Proposed Campaign YAML Contract

The first campaign schema should be intentionally small. It should describe one campaign and one landing page output, then expand later.

```yaml
campaign:
  id: summer_launch_2026
  name: Summer Launch 2026
  product: Swift Sites
  audience: marketing agencies
  conversion_goal: consultation_booking
  awareness_stage: problem_aware
  traffic_source: linkedin
  audience_sophistication: informed
  sales_cycle: consultative
  tone: confident
  industry: saas
  brand_style: modern_minimalist

content:
  pain_points:
    - Agencies spend hours duplicating the same campaign message across pages, emails, and ads.
  promises:
    - Build landing pages, emails, and ads from one structured campaign source.
  proof:
    - Server-side rendered landing pages
    - YAML-controlled layouts
    - Existing AI-assisted page generation
  objections:
    - concern: Will AI output be unreliable?
      response: AI generates structured campaign data. The compiler and renderer control the final output.
  calls_to_action:
    primary: Generate Campaign
    secondary: View Demo

landing_page:
  slug: summer-launch
  title: Summer Launch Campaign
  recipe: problem_aware_lead_gen
  theme:
    colors:
      primary: "#111827"
      text: "#374151"
      secondary: "#6b7280"
      accent: "#6366f1"
      background: "#ffffff"
  sections:
    - id: hero
      purpose: problem_aware_hero
      content_refs:
        eyebrow: campaign.product
        headline: content.promises[0]
        subheadline: content.pain_points[0]
        primary_cta: content.calls_to_action.primary
    - id: proof
      purpose: proof_points
      content_refs:
        heading: content.proof
    - id: objections
      purpose: objection_handling
      content_refs:
        objections: content.objections
    - id: final_cta
      purpose: final_cta
      content_refs:
        headline: content.promises[0]
        primary_cta: content.calls_to_action.primary
```

Notes:

- The `content:` block is the campaign's typed-content map (Content Library items, grouped by type). It replaces the earlier `atoms:` key.
- `landing_page.sections[].purpose` is semantic. It is not a renderer component name.
- `content_refs` must resolve before compilation.
- The compiler decides which renderer components to emit for each purpose.
- For phase 1, only landing page output should compile to renderer YAML.

### Grouped shorthand is normalized into typed items (one format, two stages)

The grouped form above (`content: { pain_points: [...], promises: [...] }`) is **authoring shorthand**, not a second data model. The compiler's `normalize_campaign_content(...)` step **expands grouped shorthand into typed content items** before anything else runs:

```text
content.pain_points[i]            -> { type: pain_point,  content: <str>, truth_level: <inferred from source> }
content.promises[i]               -> { type: promise,     content: <str> }
content.proof[i]                  -> { type: proof,        content: <str> }
content.objections[i]             -> { type: objection,    content: {concern, response} }
content.calls_to_action.primary   -> { type: cta,          content: <str>, structured_payload: {style} }
```

Rules:
- The group key determines `type` (`pain_points` → `pain_point`). Unknown group keys are a validation error.
- After expansion, the rest of the pipeline only ever sees **typed content items** — grouped strings never reach recipe matching, ref resolution, or the compiler. There is exactly one internal representation and one parser.
- Both the grouped shorthand and an explicit typed-object list (each item already carrying `type` + tags) are accepted as input; they converge to the same typed-item list after normalization.
- Truth level on expanded items follows the source: items derived from trusted records (offer, proof_points, required_claims) become `verified`; free-typed campaign-YAML strings default to `approved` (human-entered) unless marked otherwise; AI-drafted gaps are `generated`.

## 5.1 Typed Content (Content Library) — replaces "Semantic Atoms"

There is no separate "atom" model. The reusable marketing units are **Content Library items** classified on two axes:

```text
Axis 1 — TYPE (structural): what shape is this, and which renderer component(s) does it map to?
Axis 2 — SEMANTIC TAGS (strategic): what persuasion job does it do, for whom, and is it true?
```

Recipes match on **type + semantic tags**. The renderer cares about **type**. Same word, two jobs, one record.

### Two type families

**Primitive types** carry a single value and map to one renderer component:

```text
title        -> heading            paragraph   -> paragraph
subheadline  -> heading/paragraph  eyebrow     -> eyebrow
tagline      -> heading/eyebrow    cta_label   -> button text (+ link)
link         -> link               stat        -> counter-up/heading
rating       -> rating             quote       -> blockquote
image_ref    -> image (media_id)   icon_ref    -> icon
badge_label  -> badge              question/answer -> text (used in faq)
```

**Composite types** are built from primitives and map to a component subtree:

```text
cta               = cta_label + link
value_proposition = title + paragraph
benefit / feature = icon_ref + title + paragraph
offer             = title + paragraph + cta  (+ discount/code/expiry → optional countdown)
testimonial       = quote + author + rating + image_ref
proof             = stat/paragraph + image_ref
case_study        = title + paragraph + stat(before/after)
faq               = question + answer        (renders to accordion row)
objection         = question(doubt) + answer(response)
guarantee         = title + paragraph
comparison        = title + rows(feature, us, them)
announcement      = eyebrow + paragraph + cta
form_spec         = label + fields[]         (renders to form)
narrative         = title + paragraph(s)
```

Channel-output types (`email_subject`, `ad_headline`, `social_caption`, `seo_meta`, …) are **derived per channel at compile time**, not hand-authored.

> Composite reference rule for V1: store composite type-specific fields **inline** in `ContentItem.structured_payload`. Do not build a primitive-reference graph (composite pointing at separate primitive rows) until reuse demands it.

### Universal semantic tags (every content item)

`type`, `content`, `brand_id` (null = global), `product_id` (null = not product-specific),
`persuasion_role`, `emotion` (multi), `awareness_stage` (multi), `truth_level`, `source`,
`compliance_sensitivity`, `tone`, `specificity_level`, `channel` (multi), `status`, `is_pinned`, `performance` (JSON, null until analytics).

### Type-specific fields (in `structured_payload`)

```text
offer        -> { discount_type, discount_value, code, expiry, conditions, min_purchase }
proof        -> { proof_type, proof_source, metric_before, metric_after, permission_status }
testimonial  -> { author, author_role, company, rating, media_id, permission_status }
stat         -> { value, unit, label }
rating       -> { score, max, count }
cta          -> { link, style }
form_spec    -> { fields[], submit_label, success_message, redirect_url }
comparison   -> { competitor, rows[] }
```

### V1: derive typed content from existing records (no new table)

The compiler builds a typed-content view in memory from existing data (the same normalization the brief previously called "atom normalization"):

```text
pain_point   <- CampaignBrief.problem_or_desire
promise       <- CampaignOffer.benefits + Brand.brand_promise
benefit       <- CampaignOffer.benefits
proof         <- CampaignOffer.proof_points + Brand.required_claims + ContentItem(proof/testimonial)
objection     <- CampaignOffer.objections + CampaignMessage(objection)
cta           <- CampaignOffer.primary_cta / secondary_cta
offer         <- CampaignOffer (discount/code/expiry in structured_payload)
audience      <- CampaignBrief.target_audience + Brand.target_audience
product_*     <- selected Product records
brand_claim   <- Brand.required_claims
visual_asset  <- selected/relevant MediaAsset records
```

### Truth levels (provenance-driven; the anti-hallucination gate)

- `verified`: human-confirmed fact, or pulled from a trusted Brand/Product/Offer/ContentItem record (price, proof, required_claims).
- `approved`: human-approved AI rewrite (e.g. a "kept" message).
- `inferred`: AI extracted from a source (crawl/doc import) but unconfirmed.
- `generated`: AI-created messaging, not yet approved.
- `experimental`: under A/B test (later).

Hard rules:
- Content of type `proof, testimonial, statistic, guarantee, offer` carrying a price/number must be `verified` or `approved`. AI may **never** fabricate them.
- `Brand.forbidden_words` / `Brand.forbidden_claims` are hard filters: AI output containing them is rejected before it becomes a content item.
- `Brand.required_claims` become `verified` content the compiler prefers when relevant.

Do not treat `generated` content as truth. AI drafts copy; humans (or trusted records) own facts. The authoritative type catalog, full tag value sets, and `ContentItem` migration delta live in `docs/plans_to_implement/SEMANTIC_LAYER_ONTOLOGY.md`.

### Storage stays flat (conceptual grouping ≠ DB shape)

Conceptually it is convenient to picture a content item as nested groups — `semantic_tags: {...}`, `truth: {...}`, `scope: {...}`, `performance: {...}`. **That nesting is documentation only.** The existing `ContentItem` table stores these fields **flat** (`type`, `content`, `tone`, `status`, `source`, `brand_id`, `product_id`, `proof_source`, `is_pinned`, `structured_payload`, `tags`, …), and V1 keeps them flat. Do not introduce nested sub-objects into the table or a new content table to mirror the conceptual grouping — that would be an unnecessary schema rewrite. Map the conceptual groups onto the existing flat columns:

```text
semantic_tags.*  -> persuasion_role, emotion, awareness_stage, specificity_level, channel (flat columns / tags)
truth.*          -> truth_level (or status+source), compliance_sensitivity, proof_source
scope.*          -> brand_id, product_id, source_campaign_id
performance.*    -> performance JSON column (null until analytics)
type-specific    -> structured_payload JSON (composites only)
```

The nested view is fine in prose and API responses; the storage contract is the flat `ContentItem` columns plus `structured_payload` for composite-only fields.

## 6. Recipes

Recipes should be data, not hardcoded branching spread through the compiler.

Recipes are not visual templates. Recipes are persuasion strategies and messaging choreography. They determine the conversion flow: what proof is needed, how deep objection handling should be, how direct the CTA should be, how the emotional sequence progresses, and how trust is built for the specific buyer context.

This is a key differentiation layer for Swift Sites. Generic AI site builders mostly generate plausible pages. Swift Sites should select and compile campaign recipes based on marketing context.

Initial location:

```text
ssr_python/campaign/recipes/problem_aware_lead_gen.yaml
```

Example:

```yaml
id: problem_aware_lead_gen
name: Problem-Aware Lead Generation
description: Converts problem-aware visitors into booked calls or qualified leads.
applies_when:
  conversion_goal: consultation_booking
  awareness_stage: problem_aware
  traffic_source: linkedin
  industry: saas
  audience_sophistication: informed
  brand_style: modern_minimalist
  sales_cycle: consultative
matching:
  buying_motivation:
    - productivity
    - roi
  decision_driver:
    - trust
    - speed
  trust_requirement: high
  emotional_intensity: medium
  persuasion_style:
    - logic_led
    - authority_led
  cta_style: consultative
  proof_depth: strong
  objection_depth: high
required_content_types:
  - pain_point
  - promise
  - proof
  - cta
optional_content_types:
  - objection
  - testimonial
  - faq
section_sequence:
  - purpose: problem_aware_hero
    required_content_types:
      headline: promise
      subheadline: pain_point
      primary_cta: cta
  - purpose: problem_cost
    required_content_types:
      pain_points: pain_point
  - purpose: proof_points
    required_content_types:
      items: proof
  - purpose: objection_handling
    optional_content_types:
      items: objection
  - purpose: final_cta
    required_content_types:
      headline: promise
      primary_cta: cta
```

The recipe tells the compiler which semantic sections are expected and in what order. The campaign can provide matching section data; missing optional sections can use safe defaults; missing required sections should produce validation errors.

Recipe variation dimensions:

- `industry`: SaaS, ecommerce, local service, healthcare, education, real estate, creator brand, agency, etc.
- `awareness_stage`: unaware, problem-aware, solution-aware, product-aware, most-aware.
- `traffic_source`: organic search, paid search, Meta ads, LinkedIn, email, referral, retargeting, influencer, direct.
- `audience_sophistication`: low, medium, high, expert. More sophisticated audiences need less education and more specificity.
- `brand_style`: premium, playful, technical, editorial, minimalist, luxury, trustworthy, bold, warm, etc.
- `sales_cycle`: impulse, transactional, consultative, enterprise, recurring/subscription, seasonal.

These dimensions should influence recipe selection and section behavior:

```text
Industry -> expected proof, claims, compliance, vocabulary, product patterns
Funnel stage -> education depth, objection depth, urgency, CTA directness
Traffic source -> landing message match, hook style, above-fold context
Audience sophistication -> jargon tolerance, proof specificity, explanation length
Brand style -> tone, pacing, visual density, CTA personality
Sales cycle -> form depth, trust requirements, demo vs purchase vs nurture flow
```

Examples:

```text
SaaS + problem-aware + LinkedIn + high sophistication + technical + consultative
= concise insight-led hero, strong proof, integration/security details, book-demo CTA.

Ecommerce + product-aware + Meta ads + low sophistication + playful + transactional
= visual product hero, benefit bullets, urgency, reviews, buy-now CTA.

Healthcare + solution-aware + paid search + medium sophistication + trustworthy + consultative
= careful claims, credentials, process clarity, FAQs, appointment CTA.
```

Phase 1 can start with one or two recipes, but the schema should support these dimensions immediately so the recipe engine grows without a redesign.

V1 recipe attributes:

- `id`
- `name`
- `description`
- `applies_when.conversion_goal`
- `applies_when.awareness_stage`
- `applies_when.traffic_source`
- `applies_when.industry`
- `applies_when.audience_sophistication`
- `applies_when.brand_style`
- `applies_when.sales_cycle`
- `matching.buying_motivation`
- `matching.decision_driver`
- `matching.trust_requirement`
- `matching.emotional_intensity`
- `matching.persuasion_style`
- `matching.cta_style`
- `matching.proof_depth`
- `matching.objection_depth`
- `required_content_types`
- `optional_content_types`
- `section_sequence`

> Value sets: the allowed values for `conversion_goal`, `awareness_stage`, `traffic_source`, `sales_cycle`, `audience_sophistication`, `brand_style`, `industry`, `buying_motivation`, `decision_driver`, `trust_requirement`, `emotional_intensity`, `persuasion_style`, `cta_style`, `proof_depth`, and `objection_depth` are defined once in `docs/plans_to_implement/SEMANTIC_LAYER_ONTOLOGY.md` §10 and are the single source of truth. Recipe files, validators, and the scorer must read from that vocabulary — do not re-list or fork the enums in code. Note `conversion_goal` is the refined 14-value vocabulary; the simpler user-facing `Campaign.goal` (6 values) is derived into it per the ontology doc §4.

Recipe matching should be explainable. The system should be able to return a short reason such as:

```text
Selected SaaS LinkedIn Demo Booking because conversion_goal=consultation_booking, awareness_stage=problem_aware,
traffic_source=linkedin, sales_cycle=consultative, and available proof depth is strong.
```

V1 recipe scoring can be deterministic:

```text
exact conversion_goal match         +30
exact awareness_stage match         +25
exact traffic_source match          +15
exact industry match                +15
exact sales_cycle match             +10
brand_style match                    +5
audience_sophistication match        +5
required content types available    +20
missing required content type       -50
```

The scorer does not need ML initially. It should rank recipe candidates using structured campaign context and content-type availability.

## 6.1 Section-Purpose Library

Recipes should reference semantic section purposes. A section-purpose library maps purpose to required content types and allowed renderer components.

Initial location:

```text
ssr_python/campaign/section_purposes.yaml
```

Example:

```yaml
- purpose: proof_points
  required_content_types:
    - proof
  preferred_persuasion_roles:
    - authority
    - trust_building
    - social_validation
  allowed_components:
    - layout-row
    - layout-column
    - columnsgrid
    - badge
    - heading
    - paragraph
    - icon
  analytics_role: trust_section
```

This gives the deterministic compiler a stable bridge:

```text
Recipe section purpose
  -> required content types
  -> resolved content values
  -> allowed renderer component tree
```

## 6.2 Campaign Knowledge Graph

Swift Sites should build a campaign knowledge graph conceptually, but should not start with a graph database.

V1 should use:

```text
SQLAlchemy models for durable source records
YAML files for recipes and section-purpose definitions
plain Python dict/list graph structures for in-memory campaign graph construction, scoring, and explanations
```

The graph should connect:

```text
Brand -> Product
Brand -> ContentItem
Brand -> MediaAsset
Brand -> Campaign
Campaign -> Product
Campaign -> ContentItem
Campaign -> Recipe
Recipe -> SectionPurpose
SectionPurpose -> ContentItem
Output -> Campaign
Output -> Recipe
OutputSection -> ContentItem
AnalyticsEvent -> Campaign/Recipe/Section/ContentItem
```

Do not introduce Neo4j, RDF/OWL, external graph libraries, or a dedicated graph database in V1. The relational database should remain the source of truth. Plain Python graph snapshots should be the in-memory intelligence layer built from existing records when selecting recipes, explaining choices, compiling outputs, or analyzing performance.

Recommended V1 graph module:

```text
ssr_python/campaign/graph.py
```

Responsibilities:

```python
build_campaign_graph(campaign, brand, products, content_items, media_assets, typed_content, recipes)
score_recipe_candidates(graph, campaign_id)
explain_recipe_match(graph, recipe_id)
find_content_for_section(graph, section_purpose)
```

Graph implementation rules:

- Build graph snapshots per compile/generation request; do not treat them as persistent storage.
- Use stable node IDs such as `campaign:<id>`, `brand:<id>`, `product:<id>`, `content:<id>`, `recipe:<id>`, and `section_purpose:<purpose>`.
- Store node attributes for scoring context, but keep canonical data in SQL/YAML.
- Keep recipe scoring deterministic in V1.
- Return explainable scores and selected edges so the UI/API can show why a recipe was chosen.
- Avoid graph algorithms that make selection opaque unless their output can be explained.
- Keep graph helpers behind `campaign/graph.py`; do not spread graph construction across routes, compilers, or templates.

V1 knowledge graph goal:

```text
Given campaign context and available typed content, select the best recipe,
explain why it was selected, resolve content into semantic sections,
and preserve IDs for future analytics.
```

## 7. Compiler Output Contract

The compiler output must be valid input for `render_yaml_structure()`.

Minimum output:

```yaml
- name: site
  properties:
    theme:
      colors:
        primary: "#111827"
        text: "#374151"
        secondary: "#6b7280"
        accent: "#6366f1"
        background: "#ffffff"
  components:
    - name: page
      slug: summer-launch
      title: Summer Launch Campaign
      properties:
        appearance:
          background:
            color: "#ffffff"
            opacity: 100
      components:
        - name: layout-row
          properties:
            layout:
              tag: section
          components:
            - name: layout-column
              components:
                - name: eyebrow
                  properties:
                    text: Swift Sites
                - name: heading
                  properties:
                    text: Build landing pages, emails, and ads from one structured campaign source.
                    level: 1
                - name: paragraph
                  properties:
                    text: Agencies spend hours duplicating the same campaign message across pages, emails, and ads.
                - name: button
                  properties:
                    text: Generate Campaign
                    action:
                      type: link
                      href: "#lead"
```

Compiler output should prefer existing primitive components:

- `layout-row`
- `layout-column`
- `columnsgrid`
- `heading`
- `paragraph`
- `eyebrow`
- `button`
- `accordion`
- `image`
- `badge`
- `icon`
- `form`

Do not invent virtual components like `hero_split`, `feature_grid`, or `faq_accordion` unless they are compiled away before rendering.

## 8. AI Direction

AI should operate before the renderer.

Current AI assets to reuse:

- `ssr_python/rag/agent/query_analyzer.py`
- `ssr_python/rag/agent/planner_agent.py`
- `ssr_python/rag/agent/builder_agent.py`
- `ssr_python/rag/agent/stitcher.py`
- `ssr_python/rag/agent/yaml_fixer.py`
- `ssr_python/rag/agent/model_backend.py`
- `ssr_python/rag/retrieval/`
- `ssr_python/rag/indexing/`

Future AI pipeline:

```text
Business truth
  -> campaign context extraction
  -> structured campaign graph draft
  -> typed-content generation (draft Content Library items)
  -> recipe recommendation
  -> campaign YAML validation
  -> repair if invalid
  -> deterministic compile to renderer YAML
  -> existing preview/review
```

Rules:

- AI should not generate final HTML.
- AI should not bypass campaign validation.
- AI may draft campaign YAML, typed content (`truth_level: generated`), and section intent.
- AI may adapt verified truth into channel-specific copy variants.
- AI must not invent pricing, availability, testimonials, customer counts, product claims, or proof when records already exist (these are `verified`/`approved` content).
- Deterministic code should resolve typed content and compile renderer YAML.
- Existing RAG page generation should remain available until campaign generation is good enough to replace or wrap it.

## 9. Repository Shape For This Codebase

Do not create a new top-level `app/` package. Add the campaign layer inside `ssr_python/`.

Recommended first structure:

```text
ssr_python/
  campaign/
    __init__.py
    schema.py              # lightweight validation helpers or dataclasses
    validators.py          # validate_campaign(), validate_content_refs()
    content.py             # normalize existing records into typed, tagged content (the "atom" view)
    compiler.py            # compile_campaign_to_page_yaml()
    content_refs.py        # resolve refs such as content.promises[0]
    recipes.py             # load_recipe(), select_recipe()
    graph.py               # optional graph builder/scorer boundary
    section_builders.py    # purpose -> renderer-compatible component trees
    section_purposes.yaml  # semantic section purpose -> content-type/component rules
    recipes/
      problem_aware_lead_gen.yaml
    examples/
      basic_lead_gen_campaign.yaml
      basic_lead_gen_page.yaml

ssr_python/tests/
  test_campaign_schema.py
  test_campaign_content.py
  test_campaign_content_refs.py
  test_campaign_recipes.py
  test_campaign_graph.py
  test_campaign_compiler.py
```

Naming note: `content.py`/`content_refs.py` replace the earlier `atoms.py`/`atom_refs.py`. The functions normalize and resolve **typed Content Library items**, not a separate atom type. If you prefer to keep `atoms.py` as a filename, treat it as an internal alias for "typed-content normalization" — but the public concept is typed content, not atoms.

Later, after the compiler is stable:

```text
ssr_python/
  campaign/
    channels/
      email.py
      ads.py
      social.py
    analytics/
      events.py
      performance.py
  rag/
    agent/
      campaign_agent.py
      campaign_prompts/
```

## 10. Implementation Phases

### Phase 1 - Document and Lock Renderer Contract

Goal:

Make the current renderer contract explicit before adding a higher-level format.

Tasks:

- Add or update docs showing the current `name`/`properties`/`components` YAML shape.
- Confirm `render_yaml_structure()` accepts the compiled page YAML.
- Keep the renderer output contract stable while allowing the editor/source data model to change.
- Update `example_templates/`, test fixtures, RAG syntax references, and default YAML templates to the chosen source model.
- Add focused tests for a small renderer-compatible compiled page.

Do not:

- Rename existing renderer output fields unless the renderer itself is intentionally refactored.
- Change component macro interfaces.
- Put campaign fields into visual component templates.

### Phase 2 - Add Campaign Schema And Validation

Goal:

Introduce a campaign YAML format that is validated before compilation.

Tasks:

- Add `ssr_python/campaign/schema.py`.
- Add `ssr_python/campaign/validators.py`.
- Validate required keys: `campaign`, `content`, `landing_page`.
- Validate campaign identity fields: `id`, `name`, `product`, `audience`, `conversion_goal`, `awareness_stage`.
- Validate campaign context fields: `industry`, `traffic_source`, `audience_sophistication`, `brand_style`, `sales_cycle` when present.
- Validate `landing_page.recipe`, `slug`, `title`, and `sections`.
- Validate allowed section purposes.
- Validate content reference syntax and resolution (`content.<type>[...]`).
- Validate typed-content objects when using explicit content YAML.
- Validate recipe files for required matching, content-type, and section fields.
- Validate section-purpose definitions.

Dependency note:

- `requirements.txt` currently does not include Pydantic or jsonschema.
- For the first pass, prefer simple Python validation using existing dependencies.
- Add a new dependency only if the schema grows enough to justify it.

### Phase 3 - Build Deterministic Campaign Compiler

Goal:

Convert valid campaign YAML into existing renderer-compatible YAML.

Tasks:

- Add `compile_campaign_to_page_yaml(campaign_doc)`.
- Add `normalize_campaign_content(...)` to derive V1 typed content from current brand/product/campaign/content/media data.
- Load and apply a recipe.
- Score recipe candidates from campaign context and content-type availability.
- Resolve content references.
- Map semantic purposes to renderer component trees.
- Preserve `campaign_id`, `recipe_id`, `section_id`, and content usage metadata where possible.
- Output a top-level `site` containing one `page`.
- Use existing component names and properties.
- Write the compiled example to `ssr_python/campaign/examples/basic_lead_gen_page.yaml`.

Compiler flow:

```text
basic_lead_gen_campaign.yaml
  -> validate campaign
  -> normalize typed content
  -> load recipe
  -> score/select recipe
  -> resolve content refs
  -> build renderer components
  -> validate renderer YAML by rendering it
```

### Phase 4 - Add A Developer-Facing Compile Entry Point

Goal:

Make the compiler easy to test without changing the editor UI yet.

Options:

- CLI module: `python -m campaign.compiler path/to/campaign.yaml`
- Flask API: `POST /api/campaign/compile`

Recommended order:

1. Add pure Python compiler.
2. Add tests.
3. Add typed-content normalization and recipe scoring tests.
4. Add a small CLI or debug route.
5. Only then add editor UI integration.

### Phase 4.1 - Add V1 Campaign Context Fields

Goal:

Make current campaign records recipe-ready without overbuilding the UI.

Tasks:

- Add campaign fields: `traffic_source`, `audience_sophistication`, `sales_cycle`, and `recipe_id`.
- Prefer `Brand.industry` and `Brand.default_style` as fallbacks for `industry` and `brand_style`.
- Add Campaign Studio controls for traffic source, audience sophistication, and sales cycle.
- Keep all fields optional at first, with safe fallbacks.
- Update campaign serializers, create/update APIs, and tests.

V1 field options:

```text
traffic_source:
  organic_search, paid_search, meta_ads, linkedin, email, referral,
  retargeting, influencer, direct

audience_sophistication:
  low, medium, high, expert

sales_cycle:
  impulse, transactional, consultative, enterprise, subscription, seasonal
```

This makes recipe matching practical with current product data. Without these fields, recipes can only match on goal, awareness stage, brand industry, and rough style.

### Phase 5 - Integrate With Existing Chat/RAG

Goal:

Let AI produce campaign YAML drafts while preserving the current page-generation flow.

Tasks:

- Add a campaign intent or mode to `query_analyzer.py`.
- Add campaign prompt templates near the existing RAG agent code.
- Reuse `model_backend.py` and `yaml_fixer.py`.
- Validate and repair campaign YAML before compilation.
- Return compiled renderer YAML to the existing frontend action flow as `ACTION: create`.
- Keep legacy `create_page` behavior available behind config or fallback routing.

### Phase 6 - Add Multi-Channel Outputs

Goal:

Use the same campaign content for non-website assets.

Tasks:

- Add channel specs under `ssr_python/campaign/channels/`.
- Generate email sequence copy from typed content.
- Generate Meta ad variants from pain points, promises, and objections.
- Generate LinkedIn posts from the campaign promise/proof.
- Treat external platforms as destinations, not systems Swift Sites replaces.
- Validate each channel with strict channel-specific fields.

Do this only after landing page compilation is stable.

### Phase 7 - Analytics Feedback

Goal:

Use performance data to improve recipes and variants.

Current foundation:

- Site/page persistence exists in `models.py`.
- Form submission management exists in `routes/submissions.py`.
- Publish/version flows exist in `routes/site.py`.

Future tasks:

- Add event model(s) for section impressions and CTA clicks.
- Track `campaign_id`, `recipe_id`, `section_id`, `content_id`, output channel, and traffic source.
- Store conversion metrics per recipe and purpose.
- Feed performance summaries back into campaign recommendations.

Add stable IDs as early as possible, even before full analytics exists. Every compiled section and content usage should be traceable so future analytics can answer which recipes and content items performed best.

### Phase 8 - Graph/Ranking Upgrade

Goal:

Improve recipe and content recommendations after the deterministic V1 is stable.

Tasks:

- Keep SQL/YAML as the source of truth.
- Use plain Python graph snapshots for traversal and explanation helpers.
- Build graph snapshots inside `ssr_python/campaign/graph.py`.
- Use graph scoring to explain recipe selection and content selection.
- Do not introduce a graph database until SQL queries and in-memory graph construction are proven insufficient.

## 11. Minimal Viable Refactor

Smallest useful milestone:

```text
campaign YAML -> compiler -> current renderer YAML -> render_yaml_structure()
```

No UI changes are required for the first milestone.

Minimum files:

```text
ssr_python/campaign/__init__.py
ssr_python/campaign/schema.py
ssr_python/campaign/validators.py
ssr_python/campaign/content.py
ssr_python/campaign/content_refs.py
ssr_python/campaign/recipes.py
ssr_python/campaign/graph.py
ssr_python/campaign/section_builders.py
ssr_python/campaign/section_purposes.yaml
ssr_python/campaign/compiler.py
ssr_python/campaign/recipes/problem_aware_lead_gen.yaml
ssr_python/campaign/examples/basic_lead_gen_campaign.yaml
ssr_python/campaign/examples/basic_lead_gen_page.yaml
ssr_python/tests/test_campaign_schema.py
ssr_python/tests/test_campaign_content.py
ssr_python/tests/test_campaign_content_refs.py
ssr_python/tests/test_campaign_recipes.py
ssr_python/tests/test_campaign_graph.py
ssr_python/tests/test_campaign_compiler.py
```

Acceptance criteria:

- `basic_lead_gen_campaign.yaml` validates.
- Invalid campaign YAML returns clear validation errors.
- Existing campaign/brand/product/content data can normalize into V1 typed content.
- Content refs such as `content.promises[0]` and `content.calls_to_action.primary` resolve correctly.
- Recipe candidates can be scored from campaign context and content-type availability.
- Recipe selection returns an explainable reason.
- The compiler emits a top-level list of `name`/`properties`/`components` dictionaries.
- Compiled sections preserve stable IDs for future analytics where the renderer contract permits.
- The compiled YAML can be passed to `render_yaml_structure()` without modifying the renderer.
- Existing renderer, route, RAG, image, dashboard, and YAML validation tests keep passing.

## 12. First Codex Task

Implement the first deterministic campaign compiler.

Scope:

- No frontend UI changes.
- No database migration.
- No AI prompt changes.
- No renderer changes unless a test exposes an existing renderer bug.

Implementation details:

- Use `PyYAML`, already present in `requirements.txt`.
- Keep schema validation explicit and readable.
- Use plain dict/list structures to match the existing renderer.
- Store recipes as YAML data.
- Keep section builders small and deterministic.
- Add tests for valid input, invalid input, content ref resolution, and renderer compatibility.

Example test expectations:

- Missing `campaign.id` fails.
- Unknown section purpose fails.
- Unknown content ref fails.
- Valid campaign compiles to a list whose first item is `{"name": "site", ...}`.
- Compiled output contains a `page`.
- Compiled output contains a hero heading from `content.promises[0]`.
- `render_yaml_structure(compiled, TOKENS, COMPONENT_DEFAULTS)` returns HTML containing the headline.

## 13. Guardrails

When implementing this direction:

1. Keep campaign YAML above the renderer, not inside the renderer.
2. Backward compatibility for existing saved user sites is not required yet.
3. Do not introduce virtual component names into renderer output.
4. Do not mix AI behavior into Jinja component macros.
5. Prefer deterministic compiler logic over unconstrained AI output.
6. Treat AI output as draft data that must validate.
7. Separate human-owned truth from AI-owned adaptation.
8. Do not let AI invent prices, availability, testimonials, customer counts, product claims, or compliance-sensitive proof.
9. Keep preview, export, and publish behavior working against the new source model.
10. Convert repository-owned examples and fixtures instead of preserving old formats indefinitely.
11. Add tests before wiring campaign output into chat or UI.
12. Keep recipes configurable.
13. Design recipes around industry, awareness stage, traffic source, audience sophistication, brand style, and sales cycle.
14. Keep examples realistic and renderer-compatible after composition/compilation.

## 14. Product Reminder

Build toward:

> Create campaigns once. Publish everywhere.

The campaign is the source of truth. The website remains the first output because the renderer is already strong. The campaign compiler should make that renderer more strategic, not less reliable.
