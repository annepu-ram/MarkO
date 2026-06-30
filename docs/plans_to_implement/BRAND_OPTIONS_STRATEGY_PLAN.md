# Brand Options And Strategy Plan

## 1. Purpose

The Brand section should help a marketer define enough identity and direction before starting campaigns.

This plan separates quick preset improvements from deeper brand strategy modeling.

Do not worry about backward compatibility. The app is not in production, so the implementation can update models, forms, examples, and tests directly.

## 2. Product Decision

Implement this in two phases:

1. Phase 1: Expand simple brand presets only.
2. Phase 2: Add brand strategy fields and wire them into campaign/content AI context.

Reason for the split:

- Presets improve UX quickly with low risk.
- Strategy fields are more valuable, but they need data model, UI, prompt, campaign, and content-library integration to be useful.
- Adding strategy fields without AI wiring would create form clutter without improving campaign quality.

## 3. Phase 1: Tones, Fonts, And Themes

Phase 1 should only update preset options and validation.

No new brand strategy fields in this phase.

### 3.1 Add Tone Options

Current tones:

- `authoritative`
- `bold`
- `friendly`
- `minimal`
- `playful`
- `professional`
- `warm`

Add:

- `confident`
- `premium`
- `empathetic`
- `educational`
- `energetic`
- `trustworthy`
- `aspirational`
- `technical`
- `witty`
- `calm`

Implementation notes:

- Update `Brand.VALID_TONES`.
- Update `OrgBrandKit.VALID_TONES` if the legacy org kit path still exists in code.
- Ensure `/api/brands/options` returns the expanded list.
- Keep labels generated from values unless a custom label map is introduced.

### 3.2 Add Font Options

Current font set is useful but slightly narrow.

Add:

| Font | Recommended Use |
|------|-----------------|
| Geist | Modern SaaS and product UI |
| Instrument Sans | Contemporary brand systems |
| Onest | Approachable digital products |
| Public Sans | Civic, nonprofit, trustworthy organizations |
| Source Sans 3 | Readable broad-use content |
| Work Sans | Startups, services, portfolios |
| Mulish | Soft SaaS and service brands |
| Nunito Sans | Friendly consumer brands |
| Rubik | Modern ecommerce and apps |
| Urbanist | Fashion, creator, modern lifestyle |
| Archivo | Strong editorial and product launches |
| Fraunces | Expressive editorial and lifestyle headings |
| Newsreader | Premium editorial content |
| Libre Baskerville | Trust, education, legal, heritage |

Implementation notes:

- Update `FONT_OPTIONS` in `ssr_python/cms_options.py`.
- Keep option shape as `{value, label, use}`.
- Do not over-expand beyond this list in Phase 1; too many font choices increase decision fatigue.

### 3.3 Add Theme Options

Current themes are broad visual styles. Add more marketing-purpose presets.

Add:

| Theme Value | Label |
|-------------|-------|
| `clean_b2b_saas` | Clean B2B SaaS |
| `conversion_landing_page` | Conversion Landing Page |
| `premium_ecommerce` | Premium Ecommerce |
| `marketplace_retail` | Marketplace Retail |
| `creator_personal_brand` | Creator Personal Brand |
| `course_expert` | Course Expert |
| `local_service` | Local Service |
| `health_wellness` | Health And Wellness |
| `fintech_trust` | Fintech Trust |
| `nonprofit_civic` | Nonprofit Civic |
| `event_launch` | Event Launch |
| `high_contrast_editorial` | High Contrast Editorial |
| `playful_family` | Playful Family |
| `technical_docs` | Technical Docs |

Implementation notes:

- Update `THEME_OPTIONS` in `ssr_python/cms_options.py`.
- Ensure `Brand.default_style` validation accepts the new values.
- Make sure the Add Brand and Edit Brand forms show these values automatically through `/api/brands/options`.

### 3.4 Phase 1 Acceptance Criteria

- Add Brand modal shows the expanded tone/font/theme options.
- Edit Brand panel shows the expanded tone/font/theme options.
- Invalid tone/theme values are still rejected by API validation.
- Existing brand create/update tests pass.
- `node --check ssr_python/static/js/dashboard-v2.js` passes.
- Focused brand tests pass.

## 4. Phase 2: Brand Strategy Fields

Phase 2 should add structured brand strategy fields that improve AI output quality and content governance.

These fields should not be added as passive form fields. They must be included in campaign and content generation context.

### 4.1 Recommended Fields

Add to `Brand`:

```text
target_audience
brand_promise
differentiators
positioning_statement
competitors
forbidden_words
forbidden_claims
required_claims
compliance_notes
image_style
cta_style
primary_market
locale
voice_examples
voice_anti_examples
```

Recommended storage:

- Use text fields for simple long-form notes.
- Use JSON/text helpers for list-like fields:
  - `differentiators`
  - `competitors`
  - `forbidden_words`
  - `forbidden_claims`
  - `required_claims`
  - `voice_examples`
  - `voice_anti_examples`

### 4.2 UI Placement

Add a `Brand Strategy` section inside Brand.

Suggested UI order:

1. Audience
2. Promise
3. Differentiators
4. Voice examples
5. Forbidden words/claims
6. Compliance notes
7. Image style and CTA style
8. Market/locale

Keep the Add Brand modal lightweight. For first brand creation, collect:

- Name
- Tagline
- Industry
- Tone
- Theme
- Fonts/colors

Then show a clear next action: `Complete brand strategy`.

### 4.3 AI And Campaign Wiring

Phase 2 must update:

- `Brand.to_generation_context()`
- Campaign page generation context
- Campaign message generation
- Content Library AI creation/rewrite flows
- Product/ecommerce copy guardrails later

Strategy rules:

- AI should prefer required claims when relevant.
- AI must avoid forbidden words and forbidden claims.
- AI should use voice examples as positive references.
- AI should use anti-examples as negative references.
- Compliance notes should be treated as hard constraints.

### 4.4 Content Library Integration

Brand strategy should affect Content Library behavior:

- Generated content should store the brand used as context.
- AI rewrites should preserve brand promise and forbidden-claim rules.
- Proof/testimonial summaries must preserve source and permission status.
- Brand-specific reusable content should be filterable from the Content tab.

### 4.5 Phase 2 Acceptance Criteria

- Brand strategy fields persist through API create/update.
- Brand strategy fields render in Brand UI.
- Campaign generation receives strategy context.
- Content Library generation/rewrite receives strategy context.
- Tests cover persistence and generation context.
- AI prompts do not expose internal database labels to marketers.

## 5. Implementation Order

1. Implement Phase 1 preset expansion.
2. Run focused brand/dashboard checks.
3. Add Phase 2 model fields and migrations.
4. Add Brand Strategy UI.
5. Wire strategy into `to_generation_context()`.
6. Update campaign/content AI prompts.
7. Add tests for persistence, validation, and prompt context.

## 6. Non-Goals

- Do not implement analytics in this plan.
- Do not add ecommerce product strategy fields here.
- Do not create a separate brand strategy wizard unless the Brand section becomes too dense.
- Do not add a very large font/theme library; keep marketer choice constrained.
