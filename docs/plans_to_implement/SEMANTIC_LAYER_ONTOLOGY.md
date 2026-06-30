# Semantic Marketing Layer — Ontology & Mapping Contract (V1)

## 0. Purpose

Swift Sites is building a **semantic marketing layer**: a structured representation of marketing *meaning* that sits above every output channel (landing page first, then email/ads/social). You author meaning once; channels are projections of it.

The layer has two halves:

1. **Atoms** — reusable units of marketing meaning, each tagged with where it fits.
2. **Recipes** — strategy blueprints that say "for this buyer context, arrange these kinds of atoms in this order."

This document locks the V1 ontology (dimensions + allowed values), maps every dimension to a real Brand/Campaign field, and defines the inference and intake rules. **It is a design contract only — no code, models, or migrations are implemented by this document.**

This supersedes the looser atom/recipe sketch in `swift_sites_codex_implementation_brief.md` §5–6 where they differ. The brief's architecture, phasing, and "humans own truth / AI owns adaptation" principle still stand.

---

## 1. Design Rules Applied To The Proposed Ontology

The proposed ontology is adopted for V1 with three corrections:

1. **Casing normalized.** All enum values are `snake_case`. `ROI → roi`, `CTA → cta`, `FAQ → faq`. Mixed casing causes silent lookup failures.
2. **No duplicate goal field.** `Campaign.goal` (6 simple values) stays as the user's pick. `conversion_goal` (14 refined values) is **derived**, not asked. See §4.
3. **No duplicate awareness field.** `awareness_stage` reuses the existing `CampaignBrief.awareness_level` column. We extend its allowed values; we do not add a second field.

Everything else in the proposed schema is accepted unchanged.

---

## 2. The Three Tiers Of Dimensions

Every recipe dimension falls into one of three tiers. This is the central architectural insight: **the marketer is asked for very little; most dimensions are already stored or inferred.**

| Tier | Meaning | Dimensions |
|------|---------|------------|
| **DIRECT** | Already stored on Brand/Campaign today | industry, awareness_stage, brand_style, cta_style, compliance_sensitivity |
| **NEW FIELD** | Must be added (small, optional, safe defaults) | traffic_source, sales_cycle, audience_sophistication, conversion_goal (derived store) |
| **INFERRED** | Never asked — computed by rules | buying_motivation, decision_driver, trust_requirement, emotional_intensity, persuasion_style, proof_depth, objection_depth |

The marketer answers ~4 new things. The other ~7 strategic dimensions are inferred.

---

## 3. Dimension → Field Mapping Table

### Recipe dimensions

| Dimension | Tier | Source field / derivation |
|-----------|------|---------------------------|
| `industry` | DIRECT | `Brand.industry` (fallback: campaign brief) |
| `conversion_goal` | NEW (derived) | from `Campaign.goal` + `sales_cycle` (§4) |
| `awareness_stage` | DIRECT | `CampaignBrief.awareness_level` |
| `traffic_source` | NEW | `Campaign.traffic_source` (new, optional) |
| `sales_cycle` | NEW | `Campaign.sales_cycle` (new, optional) |
| `buying_motivation` | INFERRED | rules from industry + goal + brand (§5) |
| `decision_driver` | INFERRED | rules from goal + sales_cycle + decision facts |
| `audience_sophistication` | NEW | `Campaign.audience_sophistication` (new, optional) |
| `trust_requirement` | INFERRED | rules from industry + sales_cycle (§5) |
| `emotional_intensity` | INFERRED | rules from buying_motivation + brand_style |
| `persuasion_style` | INFERRED | rules from awareness_stage + decision_driver |
| `cta_style` | DIRECT | `Brand.cta_style` (fallback: derived from goal) |
| `proof_depth` | INFERRED | rules from trust_requirement + available proof atoms |
| `objection_depth` | INFERRED | rules from sales_cycle + available objection atoms |
| `brand_style` | DIRECT | `Brand.default_style` / `Brand.tone` |
| `section_sequence` | RECIPE-OWNED | declared in the recipe file, not a campaign field |

### Atom dimensions

| Dimension | Source / derivation |
|-----------|---------------------|
| `type` | structural — set when the atom is created |
| `content` | the actual text/value |
| `persuasion_role` | inferred from `type` + content, AI-suggested |
| `emotion` | AI-suggested from content + brand tone |
| `awareness_stage` | inherited from campaign or AI-tagged |
| `industry` | inherited from `Brand.industry` |
| `audience` | free tags from `CampaignBrief.target_audience` + `Brand.target_audience` |
| `buying_motivation` | inherited from recipe context |
| `decision_driver` | inherited from recipe context |
| `proof_type` | only for proof/testimonial/statistic/guarantee atoms |
| `specificity_level` | AI-scored (generic → quantified) |
| `truth_level` | by source (§6) — **the anti-hallucination control** |
| `source` | provenance — where the atom came from |
| `compliance_sensitivity` | inherited from `Brand.compliance_notes` + industry |
| `performance` | numeric metadata, all null until analytics exists |

---

## 4. Goal Strategy — Option A (Adopted)

`Campaign.goal` stays the **simple, user-facing** pick (6 values, unchanged):
`leads, sales, signups, calls, traffic, inform`.

`conversion_goal` is the **refined, internal** value (14 values) the recipe engine matches on. It is *derived*, never asked:

```
goal      + sales_cycle        → conversion_goal
─────────────────────────────────────────────────
calls     + consultative       → consultation_booking
calls     + enterprise         → demo_booking
leads     + (any)              → lead_generation
sales     + impulse            → purchase
sales     + recurring          → trial_signup  (or repeat_purchase if existing customer)
signups   + (any)              → newsletter_signup
traffic   + (any)              → community_join (or app_install if app context)
inform    + (any)              → newsletter_signup (lowest-commitment default)
```

Unmapped combinations fall back to the closest of: `lead_generation`, `purchase`, `newsletter_signup`. The derivation table lives in the recipe layer and is fully testable.

**Net effect:** zero new questions in Campaign Studio for goal. The richness comes for free from goal + sales_cycle.

---

## 5. Inference Rules (Dimensions We Never Ask For)

These are deterministic rules, applied in order. They are the difference between "a form with 16 fields" and "a smart system."

### trust_requirement
```
industry in {healthcare, finance, legal} → critical
sales_cycle in {enterprise}              → critical
sales_cycle in {high_consideration, consultative} → high
conversion_goal in {purchase} AND price high → high
else                                     → medium  (default; never auto-low for paid goals)
```

### compliance_sensitivity (atom-level, also gates AI)
```
industry in {finance, legal} → regulated
industry in {healthcare}     → regulated
Brand.compliance_notes present → at least high
else → none
```

### buying_motivation (pick up to 2)
```
industry in {fashion, creator, fitness} → identity_expression, aspiration
industry in {saas, agency}              → productivity, rational_evaluation
industry in {healthcare}                → trust_safety, fear_avoidance
industry in {ecommerce}                 → convenience, trend_following
goal == sales                           → + convenience
```

### decision_driver (pick up to 3)
```
sales_cycle == impulse        → price, novelty, social_proof
sales_cycle == consultative   → trust, roi, authority
sales_cycle == enterprise     → roi, risk_reduction, authority
industry == fashion           → aesthetics, exclusivity, social_proof
industry == saas              → roi, speed, trust
```

### emotional_intensity
```
buying_motivation includes {aspiration, identity_expression} → high
industry in {finance, legal, healthcare}                     → low
else                                                         → medium
```

### persuasion_style (pick up to 3)
```
awareness_stage in {unaware, problem_aware} → education_led, curiosity_led
awareness_stage in {most_aware}             → urgency_led, authority_led
decision_driver includes authority          → + authority_led
decision_driver includes emotional_relief   → + emotion_led
trust_requirement in {high, critical}       → + logic_led
```

### proof_depth
```
trust_requirement == critical → extensive
trust_requirement == high     → strong
available proof atoms == 0    → minimal (and flag: "add proof")
else                          → moderate
```

### objection_depth
```
sales_cycle in {enterprise, high_consideration} → high
sales_cycle == consultative                     → medium
available objection atoms == 0                  → low
else                                            → medium
```

All inference rules are pure functions of stored values → fully unit-testable, no AI involved.

---

## 6. Truth Levels — The Anti-Hallucination Control

`truth_level` is assigned by **provenance**, and it governs what AI may touch:

| truth_level | Meaning | Assigned when | AI may rewrite? |
|-------------|---------|---------------|-----------------|
| `verified` | Human-confirmed fact | From `Brand.required_claims`, `CampaignOffer.proof_points`, `Product` fields, prices | **No** — use verbatim |
| `approved` | Human-approved AI rewrite | Marketer clicked "keep" | No — reuse as-is |
| `inferred` | AI extracted from a source, unconfirmed | website crawl, doc import (later) | Yes, but flag for review |
| `generated` | AI-created messaging | AI drafted headline/hook | Yes |
| `experimental` | Under A/B test | variant testing (later) | Yes |

**Hard rules (from existing Brand fields):**
- Atoms of type `proof, testimonial, statistic, guarantee, offer` with a price/number must be `verified` or `approved` — AI may **never** generate them from nothing.
- `Brand.forbidden_words` and `Brand.forbidden_claims` are hard filters: AI output containing them is rejected before it becomes an atom.
- `Brand.required_claims` become `verified` atoms the compiler prefers when relevant.

This is exactly the "humans own truth, AI owns adaptation" principle, made enforceable.

---

## 7. Atom Generation Flow (Requirement 1)

> "Based on brand and campaign attributes, atoms/content using the media is generated."

```
INPUTS
  Brand    → promise, differentiators, proof, tone, voice_examples,
             forbidden_*, required_claims, industry, compliance_notes
  Campaign → brief (problem, audience, awareness), offer (benefits,
             proof_points, objections, CTAs), kept messages
  Media    → alt_text, tags  → visual_asset atoms

PROCESS
  1. Normalize existing records into atoms (no AI):
        problem_or_desire      → pain_point   (truth: verified)
        offer.benefits[]       → benefit/promise
        offer.proof_points[]   → proof        (truth: verified)
        offer.objections[]     → objection
        primary_cta            → cta
        Brand.required_claims  → proof/brand_claim (truth: verified)
        MediaAsset (tagged)    → visual_asset
  2. AI drafts the GAPS the recipe needs but records don't cover
        (headlines, hooks, mechanism_explanation, CTA variants)
        → truth_level: generated
  3. Tag every atom with inferred dimensions (§5) + brand industry/audience
  4. Apply truth + forbidden filters before any atom is stored
```

The compiler then fills the recipe's section_sequence from this atom pool, preferring higher truth_level atoms for proof/claims.

---

## 8. Dynamic Intake — "Ask For Rough Content Facts" (Requirement 2)

> "Based on the campaign attributes, ask for rough content facts."

The campaign's coordinates select a recipe; the recipe's `required_atom_types` (minus what records already provide) become the **questions to ask**. The intake form is generated, not fixed.

```
campaign coordinates → select recipe → recipe.required_atom_types
   → subtract atom types we already have from records
   → remaining REQUIRED types become intake questions
   → only ask for types AI is NOT allowed to invent (verified-truth types)
```

Question phrasing is keyed by atom type:

| Required atom type | Question asked |
|--------------------|----------------|
| `pain_point` | "What problem does this solve for them?" |
| `proof` / `testimonial` | "What proof can you show? (results, numbers, customers)" — *required, AI can't fake* |
| `objection` | "What are the top 1–2 reasons people hesitate?" |
| `offer` | "What exactly is the offer / price / discount?" — *required* |
| `urgency` | "Is there a deadline or limited quantity?" |
| `guarantee` | "Any guarantee or risk reversal?" |

AI-craftable types (`promise`, `headline`, `hook`, `cta` wording) are **not** asked — AI drafts them from the verified facts. This keeps intake short and focused only on truth the system must not invent.

---

## 9. Worked End-To-End Example

### Campaign as entered by the marketer
```
Brand: Swift Sites   (industry: saas, default_style: technical, tone: confident)
Campaign.goal: calls
Campaign.sales_cycle: consultative      (new field)
Campaign.traffic_source: linkedin       (new field)
Campaign.audience_sophistication: informed   (new field)
CampaignBrief.awareness_level: problem_aware
```

### Step 1 — Derive + infer (no questions asked)
```
conversion_goal = consultation_booking   (calls + consultative)
trust_requirement = high                 (consultative)
buying_motivation = productivity, rational_evaluation   (saas)
decision_driver = trust, roi, authority  (consultative + saas)
emotional_intensity = medium             (saas, not finance)
persuasion_style = education_led, curiosity_led, logic_led
                                         (problem_aware + high trust)
proof_depth = strong                     (high trust)
objection_depth = medium                 (consultative)
cta_style = consultative                 (Brand.cta_style or derived)
```

### Step 2 — Select recipe
```
Best match: saas_linkedin_problem_aware_demo
Reason: conversion_goal=consultation_booking (+30), awareness=problem_aware (+25),
        traffic=linkedin (+15), industry=saas (+15), sales_cycle=consultative (+10),
        proof_depth available=strong (+20)
section_sequence:
  insight_led_hero → problem_cost → mechanism_explanation
  → proof_points → objection_handling → demo_cta
```

### Step 3 — Dynamic intake (only the gaps AI can't invent)
Records already provide: product, audience, awareness.
Recipe requires `proof`, `objection`. Those are verified-truth types not yet supplied → **ask:**
```
Q1: "What proof can you show? (results, numbers, customers)"
Q2: "Top 1–2 reasons prospects hesitate before booking?"
```
Promise, hero headline, CTA wording: NOT asked — AI drafts them.

### Step 4 — Atoms (mix of verified + generated)
```
pain_point   "Agencies rebuild the same message across pages, emails, ads"  verified
promise      "Build every campaign asset from one source"                   generated
proof        "Used to ship 40% faster" (from Q1)                            verified
objection    "Will AI output be reliable?" (from Q2)                        verified
cta          "Book a Strategy Call"                                          generated (cta_style: consultative)
```

### Step 5 — Compile → renderer YAML
Recipe section `insight_led_hero` pulls `promise` (headline) + `pain_point` (subheadline) + `cta` (button) → emits `layout-row > layout-column > heading/paragraph/button` in the existing renderer shape. Done deterministically.

---

## 10. Finalized V1 Value Sets (Authoritative)

> Snake_case everywhere. These are the locked enums for V1.

**industry:** saas, ecommerce, fashion, healthcare, education, finance, legal, real_estate, hospitality, fitness, local_services, agency, creator, nonprofit, marketplace, other

**conversion_goal (derived):** purchase, lead_generation, demo_booking, consultation_booking, appointment_booking, trial_signup, webinar_registration, newsletter_signup, app_install, donation, community_join, repeat_purchase, retention, upsell

**awareness_stage:** unaware, problem_aware, solution_aware, product_aware, most_aware, onboarding, retention, reactivation, expansion

**traffic_source:** organic_search, paid_search, meta_ads, instagram, linkedin, youtube, tiktok, x_twitter, email, referral, influencer, affiliate, direct, retargeting, outbound, community, webinar

**sales_cycle:** impulse, transactional, consultative, high_consideration, enterprise, recurring, seasonal

**buying_motivation:** rational_evaluation, identity_expression, aspiration, transformation, convenience, productivity, trust_safety, social_status, trend_following, belonging, fear_avoidance, curiosity, entertainment, luxury_desire

**decision_driver:** price, roi, convenience, speed, trust, aesthetics, novelty, exclusivity, social_proof, authority, emotional_relief, risk_reduction, quality, personalization

**audience_sophistication:** beginner, aware, informed, expert

**trust_requirement:** low, medium, high, critical

**emotional_intensity:** low, medium, high

**persuasion_style:** authority_led, emotion_led, logic_led, aspiration_led, transformation_led, urgency_led, education_led, community_led, curiosity_led, fear_reduction

**cta_style:** passive, soft, consultative, direct, urgent

**proof_depth:** minimal, moderate, strong, extensive

**objection_depth:** low, medium, high, complex

**brand_style:** modern, minimalist, premium, luxury, playful, bold, warm, trustworthy, technical, editorial, corporate, futuristic, community_driven

**atom type:** pain_point, promise, proof, objection, objection_response, cta, feature, benefit, offer, differentiator, transformation, guarantee, urgency, faq, testimonial, statistic, comparison, narrative

**persuasion_role:** authority, trust_building, pain_agitation, aspiration, transformation, social_validation, urgency, fear_reduction, objection_resolution, mechanism_explanation, identity_alignment, emotional_connection, reassurance, curiosity, exclusivity, simplicity

**emotion (multi):** trust, fear, aspiration, relief, excitement, curiosity, confidence, urgency, belonging, exclusivity, pride, frustration, anxiety, hope, empowerment

**proof_type:** testimonial, case_study, metric, customer_count, review, rating, certification, credential, media_mention, integration, founder_story, before_after, guarantee

**specificity_level:** generic, semi_specific, specific, quantified

**truth_level:** verified, approved, inferred, generated, experimental

**source:** human_input, website_crawl, uploaded_document, crm, analytics, ai_generated, imported_campaign, sales_call, support_conversation, review_platform

**compliance_sensitivity:** none, moderate, high, regulated

---

## 11. What Changes In The Data Model (For A Later Phase)

Design note only — not implemented here.

**New Campaign fields (all optional, safe defaults):**
- `traffic_source` (enum, nullable)
- `sales_cycle` (enum, nullable)
- `audience_sophistication` (enum, nullable)
- `conversion_goal` (enum, nullable — stored after derivation for traceability)
- `recipe_id` (string, nullable — which recipe was selected)

**Reused as-is:** `CampaignBrief.awareness_level`, `Brand.industry`, `Brand.default_style`, `Brand.tone`, `Brand.cta_style`, `Brand.compliance_notes`, `Brand.required_claims`, `Brand.forbidden_words`, `Brand.forbidden_claims`, `Brand.voice_examples`.

**Atoms:** V1 normalizes from existing records in-memory at compile time (per the brief). A durable atom/variant table is a later phase once the deterministic compiler proves out.

---

## 12. Acceptance Of This Contract

This ontology is considered locked for V1 when:
- All enum value sets in §10 are treated as the single source of truth across recipes, atoms, and intake.
- The dimension→field mapping (§3) is the basis for the compiler's input gathering.
- Inference rules (§5) and goal derivation (§4) are implemented as pure, tested functions.
- Truth-level rules (§6) gate every AI-generated atom.
- Dynamic intake (§8) asks only for verified-truth gaps, never for AI-craftable copy.

Downstream work (compiler, recipes, section-purpose library, intake UI) builds against this contract.
