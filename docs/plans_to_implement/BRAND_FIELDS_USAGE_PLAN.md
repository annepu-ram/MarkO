# Brand Fields Usage Plan

## Context
Brands carry many fields — identity, theme, voice, and a strategy/guardrails set (words to use / not use,
required & forbidden claims, voice examples, compliance notes). Audit question: are these actually used when
generating campaigns and content, or do they just sit in the DB? Finding: **partially used as soft hints,
never enforced, and inconsistently injected.** This plan defines how each brand field SHOULD be used.

Part of the campaign-engine roadmap ([CAMPAIGN_ENGINE_NORTH_STAR.md](CAMPAIGN_ENGINE_NORTH_STAR.md), Phase 1b).

## Current usage (verified)
All fields are exposed via `Brand.to_generation_context()` (models.py:369-449).

| Brand field group | Fields | Reaches generation today? |
|---|---|---|
| Identity | name, tagline, description, industry, logo_url | ✅ page + brand prompts |
| Theme | colors, fonts, default_style | ✅ theme → renderer (`brand_to_theme`) |
| Voice | tone, voice_guidelines | ✅ brand prompts + `_build_brand_guidance` |
| Strategy text | target_audience, brand_promise, positioning, image_style, cta_style, primary_market, locale | ✅ via `_build_brand_guidance` (compiler.py:171-185) |
| **Guardrails** | **forbidden_words, forbidden_claims, required_claims, voice_examples, voice_anti_examples, compliance_notes** | ⚠️ rendered as soft hints in some paths; **never enforced** |

**Paths:**
- `brand_styler`/`brand_wording` durable prompts → get full context (section_rag.py:25,68).
- Campaign `generate-page` → `_build_brand_guidance` renders "Never use these words / Hard compliance rules"
  into the description (compiler.py:155-202).
- `section_builder` (content→section) → gets the visual `brand_style_prompt`, content, theme — NOT raw
  guardrails. **By design this is OK** (see principle below).
- Campaign messages (`/compile`) → deterministic echo of user input, no LLM.
- AI content drafts (`routes/chat.py`) → generate **without** a guardrail enforcement pass.
- **No path validates output** against forbidden/required/compliance rules.

## Design principle: enforce guardrails at the CONTENT gate, not the section
The `section_builder` reuses content, it does not invent it
(`campaign/prompts/section_builder_system.j2`: "Use only the selected content facts… omit instead of
inventing"). So if content is born compliant, sections inherit it — no need to re-enforce at the section
stage. Guardrails are a **content-creation** concern.

## Plan
1. **Inject guardrails into every content-CREATION path** — reuse `_build_brand_guidance(gen_ctx)`
   (already renders forbidden/required/voice/compliance into clean LLM instructions) in AI content drafting
   and any future campaign-message generation.
2. **Add a content-creation enforcement pass** — mirror the YAML generate→check→repair loop
   `_extract_validate_and_repair_body_yaml` (section_rag.py:215), but for brand voice/compliance:
   - `forbidden_words` / `forbidden_claims` → scan; on hit, auto-regenerate with a stricter instruction or
     flag for review.
   - `required_claims` → verify presence; warn if missing.
   - `compliance_notes` → surface as a reviewer checklist on the asset.
   - `voice_examples` / `voice_anti_examples` → few-shot the content prompt (good vs bad voice).
3. **Sections trust the content** — no full re-enforcement; at most an OPTIONAL lightweight forbidden-word
   scan on the small connective microcopy the section builder adds (headings/button labels).
4. **One gate, all channels** — content is the shared core, so cleaning it once means page + (future)
   email/ad/social inherit compliant, on-brand copy. This makes brand guardrails a real campaign-engine
   differentiator rather than dormant DB fields.

## Files implicated (for the future build)
- `campaign/compiler.py` — `_build_brand_guidance` (reuse as the renderer).
- `routes/chat.py` — content-draft generation (inject + enforce here).
- `campaign/section_rag.py` — pattern to mirror for the compliance pass; optional microcopy scan.
- `models.py` `Brand.to_generation_context` / `STRATEGY_LIST_FIELDS` — source of the guardrail values.

## Verification (when built)
- Unit: a brand with `forbidden_words=["cheap"]` → generated content never contains "cheap" (or is flagged);
  `required_claims` present in output; `voice_anti_examples` style absent.
- Manual: create a guardrail-heavy brand, generate content + a campaign page, confirm rules are honored and
  compliance notes surface for review.
