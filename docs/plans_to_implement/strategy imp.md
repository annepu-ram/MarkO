Stepping out of code-archaeology mode. Here's the thing a marketer needs to hear, and it dissolves most of your doubt:

Your campaign form is content. You don't have a gap — you have a naming problem.
Look at what the campaign form already captures (verified in the code): the brief (audience, problem, awareness stage) + the offer (the offer itself, CTAs, benefits, proof points, objections, FAQs) + messages (AI-drafted headlines, benefits, proof, etc. that the marketer "keeps"). That is the copy a page is built from. The generate-page flow compiles exactly this into the page — it never reads the Content Library to do it.

So the premise "without content how can a campaign generate sections?" — the campaign carries its own content inside the brief/offer/messages. The separate Content Library is not a prerequisite. It's a reuse drawer.

How a marketer actually thinks (and how the entities should map)
Marketer's mental step	App entity	Created when
"Here's my business / who we are"	Brand	Once, up front
"I want to promote this thing to these people"	Campaign (brief + offer)	Each promotion
"Write me the copy"	Campaign messages (AI)	Inside the campaign
"Make the page/site"	Site / Page	Generated from the campaign
"Save the lines that worked so I don't rewrite them next time"	Content Library	By-product, later
"Reuse a whole block I like"	Section	Power-user, later
A marketer does not sit down and write 25 disconnected "content atoms" (headline, benefit, proof…) and then assemble them. Nobody works that way. Content-first is an engineer's data model leaking into the UX.

Direct answers to your three questions
1. Should we make users create content before a campaign? → No. That's backwards and will kill adoption. Campaign-first. The campaign form collects everything needed to generate a page. The Content Library should start empty and fill up automatically as campaigns run.

2. Upload a campaign doc → AI creates content? → Yes, but frame it as an accelerator, not a separate path. The doc shouldn't create "content items." It should pre-fill the campaign brief and offer (parse the doc → populate audience, offer, benefits, proof, FAQs), then AI drafts the messages. Same destination, faster on-ramp. This is the single highest-value UX add you could make.

3. The flow, nailed:


BRAND  (identity + voice — set once)
  │
  ▼
CAMPAIGN  ← marketer fills offer/audience  OR  uploads a brief → AI prefills
  │         AI drafts messages (the copy)
  ▼
PAGE / SITE  (generated — uses Brand for look, Campaign for words)
  │
  ├──► winning messages auto-save to → CONTENT LIBRARY  (reuse drawer)
  └──► liked blocks save as → SECTIONS                  (reuse drawer)
                                   │
                                   └─► feed BACK into the *next* campaign
Content Library and Sections are outputs that become inputs to future campaigns — not gates in front of the first one.

The one change that fixes the confusion
Right now the gap is purely that saving campaign messages → Content Library is a manual step (save-from-campaign must be explicitly called), and Sections demand pre-existing content. So the two forms feel disconnected. Bridge it by making the Library auto-populate from kept campaign messages. Then:

New users live entirely in Brand → Campaign → Site and never touch the Library.
The Library quietly fills with their proven copy.
Returning users get "reuse what worked" suggestions in their next campaign — the reuse layer pays off without ever being a prerequisite.
Two things I can do next, your call:

Reframe the UI/labels so "content" stops reading as a required first step (e.g. Library framed as "Saved & proven," Sections as "Saved blocks").
Spec the brief-doc upload → campaign prefill flow (your question #2), which is the biggest accelerator.


_type_catalog.py
Now I can see exactly what you're weighing. The content form has 26 content types across 7 families, many with dynamic slot schemas (e.g. testimonial → quote/author/role/company/rating; faq → question/answer; cta → headline/paragraph/button_label/link). The campaign form has fixed fields: brief (audience, problem, awareness) + offer (offer, CTAs, benefits[], proof_points[], objections[], faqs[]) + messages.

Short answer: No — don't merge the dynamic content form into the campaign form.
They look similar but serve two different mental modes, and merging them breaks the thing that makes the campaign form good.

Why they're different jobs
Campaign form	Content form
Marketer's mindset	"Here's my situation — go make me a page"	"Let me author/polish this one asset"
Input style	Fast, strategic, fill-in-the-blanks	Precise, structured, slot-by-slot
Output	A whole page/site (AI fills the gaps)	One reusable, exact-worded item
Speed expectation	5 minutes, then magic	As long as it takes to get it right
If you drop the 26-type dynamic slot UI into the campaign form, you turn a 5-minute strategic brief into a data-entry marathon. A marketer launching a promo does not want to fill out a comparison slot schema with subject/alternative/differentiator/proof_note. That kills the campaign's entire value proposition ("tell me roughly, I'll generate").

But notice — the campaign form is already a simplified content form
This is the key realization. Look at the campaign offer: benefits[], proof_points[], objections[], faqs[]. Those map almost 1:1 to content types benefit, proof, objection, faq. The campaign form is already capturing typed content — it just uses a curated, flattened subset instead of the full 26-type/slot machinery.

So you don't have a "should we merge" problem. You have a "these two forms should share one data model, not one UI" opportunity.

What to actually do
Keep two surfaces, unify the model underneath:

Campaign form stays a fast brief. Its benefits/proof/objections/FAQs become typed content items with slots under the hood — when the marketer types a benefit, it's stored as a benefit content item (with slots), not as a loose string. Same data the library uses.

Content form stays the precision/reuse tool. It's where you author or refine a single typed asset with full slot control — and where campaign-generated items land for editing/reuse.

The campaign "borrows" content types it needs — not all 26. A campaign only ever needs the ~8 page-relevant types (headline, benefit, proof, testimonial, offer, faq, cta, about). The channel-asset types (ad_copy, email_subject, social_post, seo_meta) and niche ones don't belong in a landing-page brief at all.

Net effect: one content model, two right-sized doors into it. The campaign form feels effortless; the library stays powerful; nothing is duplicated; and content flows both ways (campaign → library, library → campaign) because they're the same typed objects.

The one trap to avoid
Don't build "dynamic slot forms inside the campaign." Build "the campaign's offer fields write typed content items." The slot schema is a library/editing concern; the campaign should stay strategic and let AI expand brief inputs into full slotted content.

Want me to spec this as a plan? Two natural pieces:

Unify the model: campaign offer fields (benefits/proof/objections/faqs) persist as typed ContentItems with slots instead of loose JSON arrays — so campaign and library share one source of truth.
Right-size the type list: define the page-relevant subset the campaign uses, vs. the full catalog the library exposes.
Or if this was just to settle the direction, we can fold it into the broader brand→content→campaign flow decision and move on.


---

# Campaign categories = recipes

Open question: if campaigns become the typed-content engine, "don't we need more variety of campaigns?" — i.e. more campaign categories. Decision below (direction only, no build yet).

## What exists today (verified)
- Campaign `goal` — DB enum, 6 values: leads, calls, sales, signups, traffic, inform (models.py:770). The only "category" the form surfaces.
- Recipe engine — a real, deterministic, scored selector (campaign/recipes.py) that, per campaign context, picks a recipe declaring `required_content_types`, `optional_content_types`, and a `section_sequence` (e.g. campaign/recipes/problem_aware_lead_gen.yaml). Only 2 recipe files exist (problem_aware_lead_gen, local_impulse_offer).
- So there are two competing "category" systems: the `goal` enum (used in the form) and recipes (rich engine, barely populated).

## Decision
1. Recipes are the categorization spine. A "campaign category" = a recipe. Variety comes from adding recipes, not from enlarging the campaign form or the `goal` enum.
2. `goal` becomes an input dimension the recipe scorer reads (alongside awareness_stage, industry, traffic_source, etc.) — NOT a parallel taxonomy. One spine, not two.
3. Recipes bridge to the unified content model. Each recipe's required/optional_content_types define exactly which subset of the 26 content types that campaign collects and generates — this keeps the campaign form a fast brief while still producing typed, slotted content.
4. Selection is auto + override. The form stays a brief; the recipe engine auto-selects the best recipe with an explainable reason (recipes.py `_explain`); the marketer can override. No mandatory "pick a category" gate.

## Candidate recipe library (future build)
Lead generation ✅, Local impulse offer ✅, + Product launch / announcement, Webinar / event registration, E-commerce sale / seasonal promo, Free trial / SaaS signup, Waitlist / coming soon, Newsletter / audience building. Each = one recipe declaring its content-type set + section sequence.

## Deferred to a later build plan (explicitly NOT now)
- Authoring the new recipe YAML files + section purposes.
- Wiring `goal` into build_recipe_context as a scored dimension and resolving the goal-vs-recipe overlap.
- Unifying campaign offer fields (benefits/proof/objections/faqs) into typed ContentItems with slots.
- Auto-populating the Content Library from kept campaign messages.

---

# Should we expand campaign goals? (refinement)

Follow-up: "should we not expand on campaign goals?" Answer: expand the goal's MEANING/mapping, not the length of the user-facing list.

## What exists today (verified — corrects an earlier assumption)
The goal→recipe bridge already exists; it is NOT a missing wire:
- User-facing `goal` — 6 plain intents: leads, calls, sales, signups, traffic, inform (models.py:770; USER_GOALS in campaign/vocabulary.py:139).
- Refined `conversion_goal` — 14 precise intents: purchase, lead_generation, demo_booking, consultation_booking, appointment_booking, trial_signup, webinar_registration, newsletter_signup, app_install, donation, community_join, repeat_purchase, retention, upsell (CONVERSION_GOAL, vocabulary.py:21-26).
- `derive_conversion_goal(goal, sales_cycle)` maps the 6 → the 14, using sales_cycle to disambiguate (e.g. calls+enterprise→demo_booking else consultation_booking; sales+impulse→purchase, sales+recurring→trial_signup) (vocabulary.py:142-171).
- `page_compiler.py` calls it before scoring: if conversion_goal is absent but goal is present, it derives one, then `build_recipe_context` feeds it to `select_recipe` (page_compiler.py:61-73).
- `conversion_goal` is the highest-weighted scoring dimension at 30 pts (recipes.py:21) — so goal is the DOMINANT recipe signal, transmitted via the refined value.

## Decision
1. Keep the user-facing `goal` list SHORT and human (~6-8). Do NOT expand it toward the 14 conversion_goals — that would rebuild the recipe taxonomy in a second place (the exact "two competing category systems" we are killing).
2. Expand the MAPPING, not the list. Variety/precision belongs in `conversion_goal` + recipe `applies_when`, reached through `derive_conversion_goal`. Grow that vocabulary and the derivation rules as new recipes need finer intents.
3. Optionally add at most 1-2 plain goals if a common campaign type has no honest home (candidates: `book` for calls/consultations, `register` for events/webinars) — only if the mapping can't express it cleanly via sales_cycle/awareness.
4. The derivation currently leans on `sales_cycle` to disambiguate; as recipes grow, `derive_conversion_goal` may need more context inputs (awareness_stage, traffic_source) to pick the right refined goal. That is a mapping enhancement, not a form change.

## Net
Marketer picks from a handful of plain goals; `derive_conversion_goal` translates to the precise signal the recipe scorer already weights at 30; recipes carry the fine granularity. One spine, short form, rich engine.

## Deferred (with the recipe-library build)
- Extend `derive_conversion_goal` rules + CONVERSION_GOAL vocabulary to cover new recipes (e.g. webinar_registration already exists but is unmapped from any user goal).
- Decide whether to add `book`/`register` to USER_GOALS, or keep 6 and disambiguate purely via sales_cycle/awareness.