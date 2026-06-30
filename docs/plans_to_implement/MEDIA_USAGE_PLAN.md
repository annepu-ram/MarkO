# Media Usage Plan (sourcing-first, hybrid)

## Context
Media (images) is half of every hero/ad/social asset. Judged against how a marketer actually works, the
earlier model got *attachment* right (brand→product→campaign→content layering) but under-served **sourcing**:
it made "curate a per-campaign set" the entry point and treated finding images as a manual pre-step. A
marketer's first campaign has an empty library, so "curate first" means a chore or a page full of grey
placeholders. The dominant need is "find me a hero of X" (sourcing), then "swap this one image right here."
Curation is a *light override*, not the entry point.

Companion to [CAMPAIGN_ENGINE_NORTH_STAR.md](CAMPAIGN_ENGINE_NORTH_STAR.md) and
[BRAND_FIELDS_USAGE_PLAN.md](BRAND_FIELDS_USAGE_PLAN.md).

## Decisions
- **Hybrid sourcing:** prefer **owned** media (brand-tagged / product / campaign-curated) → **fall back to
  auto-sourced stock** for slots with no owned match.
- **Light brand library:** keep media org-scoped, but add an optional `brand_id` **tag** + picker/loader
  filter (not a hard re-scope).
- **AI image generation:** a **future** third sourcing layer (owned → stock → generated); out of scope now.

## Principle: media has a SOURCING axis, not just an attachment axis
The layering answers "what's attached where." Marketers also ask "do I *own* a photo, or must I *find/make*
one?" Every image slot should be filled with something real by walking a fallback ladder:

```
OWNED      brand-tagged media · product shots · campaign-curated   ← use first (trust, brand fit)
   ↓ (no match)
SOURCED    auto stock search by section concept (Pexels/Pixabay)   ← fills the gap, kills placeholders
   ↓ (future)
GENERATED  text-to-image for bespoke visuals                       ← noted, not built now
```

Same "one core, many renderings" idea as typed content — an image chosen once travels to the page section,
the ad, the social post.

| Attachment layer | Media | Status today | Plan |
|---|---|---|---|
| **Brand** | logo, favicon, **brand photos** | logo/favicon fields unused; no photo library | resolve media_id → URL; add optional `brand_id` tag + filter |
| **Product** | product shots | `default_media_id` unused | resolve media_id → URL |
| **Campaign** | hero / lifestyle / offer visual | NO link | curated set as a **light override** (`CampaignMedia`) |
| **Content** | testimonial headshot, case-study photo | text-only | optional image slot (largest change; only if needed for reuse) |

## Verified state today
- Org-scoped `MediaAsset` (models.py:605-639); stock search `/api/images/search` (routes/images.py) exists
  but is **frontend-only** (imagesPanel.js) — **never called during generation**.
- Main pipeline IS media-aware but **reuse-only**: `_load_org_media_images()` (routes/chat.py:68-89) →
  `_build_image_context()` (rag_agent.py:210-232) → builder embeds URLs.
- Campaign `generate-page` passes `selected_images`; **`generate_section_yaml` (campaign/section_rag.py) is
  media-blind**; `regenerate_section` (routes/campaign.py:770) **hardcodes `selected_images=[]`**.
- `Brand.logo_media_id`/`Product.default_media_id` exist but are **never resolved** (only `_url` strings used).
- Campaign Studio preview is **read-only** — image swap requires the full editor (campaignStudio.js:1005-1011, 1082-1084).

## Plan (priority order — marketer value first)
1. **Auto-source stock by concept (hybrid) — headline change.** The planner already assigns images per
   section; have it also emit a short **image query** per section (e.g. "bright modern dental clinic, wide").
   At generation, fill each slot: use owned/curated media first; for unfilled slots, call `/api/images/search`
   with the section query, pick by orientation, and embed the result. Kills placeholder pages for new
   campaigns and improves relevance even when a library exists. *Benefits the plain site generator too.*
   - Reuse `/api/images/search` (routes/images.py) and `_build_image_context()` (rag_agent.py:210-232).
   - Decide auto-persist of fetched stock to the library vs. transient use (lean: persist on publish so the
     live page doesn't depend on a hotlink).
2. **Inline image swap in Campaign Studio — #1 post-gen action.** Let a marketer click an image in the studio
   preview and swap it (brand library / stock search / regenerate) without jumping to `/editor`. Removes the
   read-only context-switch (campaignStudio.js preview + a lightweight picker reusing imagesPanel.js search).
3. **Light brand photo library.** Add optional `brand_id` tag on `MediaAsset` + a brand filter in the media
   picker and the generation loader, so "upload once, reuse across this brand's campaigns" works. Owned brand
   media ranks first in the sourcing ladder. (Not a hard scope change — org-wide remains the default.)
4. **Plumbing fixes (low risk, do alongside #1):**
   - Add `image_context`/`selected_images` to `generate_section_yaml` + thread into
     `campaign/prompts/section_builder_user.j2`.
   - Fix `regenerate_section` to pass the campaign's images, not `[]`.
   - Resolve `Brand.logo_media_id` / `Product.default_media_id` → URL in `to_generation_context()`.
5. **Curation = light override (demoted).** Per-campaign curation (`CampaignMedia` link, mirroring
   `CampaignProduct` at models.py:858-873) becomes an optional "pin the hero / drop this one" override on top
   of the sourcing ladder — not the entry point.
6. **Generated media (future).** Text-to-image as a third ladder rung for bespoke visuals; provider + cost/
   latency TBD. Documented, not scheduled.

## Reuse (don't reinvent)
- `/api/images/search` (routes/images.py) — already proxies Pexels/Pixabay; call it server-side during generation.
- `_build_image_context()` (rag_agent.py:210-232) — formats images for prompts; reuse for the section path.
- `_load_org_media_images()` (routes/chat.py:68-89) — generalize to accept a filter (org → brand-tagged / campaign-curated).
- `imagesPanel.js` search/select — reuse for the Campaign Studio inline picker.
- `CampaignProduct` / `CampaignCollection` (models.py:858-889) — join pattern for an optional `CampaignMedia`.

## Files implicated (future build)
- `rag/agent/planner_agent.py` — emit a per-section image query.
- `rag/agent/rag_agent.py` / `builder_agent.py` — hybrid fill: owned-first, stock-fallback; reuse `_build_image_context`.
- `routes/images.py` — server-side stock search call during generation (currently frontend-only).
- `campaign/section_rag.py` + `campaign/prompts/section_builder_user.j2` — accept/surface images.
- `routes/campaign.py` — fix `regenerate_section`; campaign-scoped media loading.
- `static/js/campaignStudio.js` (+ reuse `imagesPanel.js`) — inline swap.
- `models.py` — optional `MediaAsset.brand_id` tag; resolve `logo_media_id`/`default_media_id`; optional `CampaignMedia`.
- `routes/media.py` — brand filter on `/api/media`.

## Verification (when built)
- Unit: brand-new campaign (empty library) generates a page where image components carry **real stock URLs**,
  not `placehold.co`; `generate_section_yaml` with owned media prefers it; `regenerate_section` keeps images.
- Manual: tag images to a brand → they rank first; generate a campaign with no owned hero → stock auto-fills
  by concept/orientation; swap a hero inline in Campaign Studio without opening the full editor.
