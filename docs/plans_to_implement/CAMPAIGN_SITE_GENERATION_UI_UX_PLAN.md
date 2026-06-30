# Campaign-Based Site Generation UI/UX Plan

## 1. UX Principle

Swift Sites should have near-zero learning curve for a new marketer.

The UI should feel like a campaign launch workspace, not a developer tool, CMS admin, or YAML editor. A marketer should understand the first action in less than five seconds.

Use marketer-facing language:

- Campaign
- Offer
- Audience
- Message
- Landing Page
- Brand
- Products
- Launch
- Campaign Results

Avoid exposing implementation language in the primary UI:

- YAML
- renderer
- compiler
- content atoms
- recipes
- shared blocks
- schema validation

Those concepts can remain in code, advanced panels, diagnostics, and implementation docs. They should not drive the first-time user experience.

## 2. Product Direction

Swift Sites is wrapping campaigns, CMS, and AI into one package.

Marketer-facing product frame:

- Campaigns: plan the offer, audience, message, landing page, channels, and launch.
- Brands: manage multiple brand profiles, voice, visuals, logos, and reusable brand content.
- Products: manage products/services in a separate catalog tab. Products can be tagged to one or more brands.
- Media: manage reusable assets across brands, products, campaigns, websites, and pages.
- Content Library: save reusable messages, testimonials, proof, and boilerplate.
- AI Assistant: turns campaign intent into editable messages, pages, and recommendations.

Internal product frame:

- Campaigns provide strategy and source intent.
- CMS stores reusable brands, products, content, media, pages, and shared site sections.
- AI generates structured campaign data, page drafts, copy variants, repairs, and suggestions.
- Renderer YAML remains the compiled output for preview and publish.
- Products and brands are reusable CMS records. Campaigns select from them instead of copying everything into one-off page text.

## 3. Marketer Behavior Inputs

This UX should be designed around how marketers actually work, especially small teams and operators who need to ship campaigns without learning a site builder.

Behavior assumptions:

- Marketers are outcome-first. They start with "I need leads", "I need to promote this offer", or "I need to launch this product", not "I need a page schema".
- They work under deadline pressure. The dashboard must show the next action immediately and avoid making users reconstruct where they left off.
- They reuse messages across channels. One offer often becomes a landing page, ad, email, social post, and follow-up content.
- They need clear goals before production. Content Marketing Institute's 2025 B2B research notes that many marketers struggle with strategy effectiveness, unclear goals, limited resources, and lack of scalable content creation. This justifies starting with campaign goal, audience, offer, and messages before page editing.
- They are adopting AI, but generic AI output is not enough. HubSpot's 2026 State of Marketing positions AI as baseline and emphasizes brand trust and human-led marketing. This justifies AI drafts with marketer review, "keep" controls, and brand/content library reuse.
- They care about personalization and data, but data is often fragmented. Salesforce's 10th State of Marketing reports that marketers recognize the shift toward personalized two-way engagement, while satisfaction with data usage remains low. This justifies a single campaign object that connects messages, pages, future channels, and future results.
- They scan interfaces. Nielsen Norman Group usability heuristics support using familiar user language, visible options, recognition over recall, and plain-language error recovery. This justifies replacing internal labels like YAML, compiler, atoms, recipes, and schema with Campaign, Messages, Landing Page, Brand, Products, and Results.
- They judge tools by launch confidence. The last step should read like a campaign launch checklist, not a technical validation log.

UX implications:

- Lead with the job to be done, not the object model.
- Show recommended next actions instead of blank dashboards.
- Make AI produce suggestions that users can accept, edit, keep, or regenerate.
- Keep advanced controls available, but do not make them part of the first-run path.
- Keep campaign, content, pages, and future results connected in one place.
- Use progressive disclosure: simple first, detail only when the user asks for it.

Research references:

- [Content Marketing Institute, B2B Content Marketing Benchmarks, Budgets, and Trends: Outlook for 2025](https://contentmarketinginstitute.com/b2b-research/b2b-content-marketing-trends-research-2025)
- [HubSpot, 2026 State of Marketing Report](https://www.hubspot.com/state-of-marketing)
- [Salesforce, Tenth Edition State of Marketing](https://www.salesforce.com/marketing/resources/state-of-marketing-report/)
- [Nielsen Norman Group, Jakob's Ten Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)

## 4. Guided Flow Decision

Decision: replace the current guided flow. Do not preserve a legacy path for compatibility.

Backward compatibility is not required because there are no active app users depending on the old creation flow. The current `guidedFlow.js` can be mined for useful questions and option lists, but the UI pattern should be retired.

What to keep conceptually:

- Business description prompt
- Industry choices
- Style choices
- Purpose/goal choices
- Section labels that map cleanly to landing page structure

What to remove as the product direction:

- Chat-embedded multi-step website wizard
- Page-first setup
- Manual section picking as the central task
- `/api/chat/guided` as the primary generation route
- Any "legacy quick website" surface in production

Replacement direction:

- Primary creation path becomes Campaign Studio.
- Chat can trigger campaign creation, but it should hand off to Campaign Studio.
- Old examples and templates should be migrated to the campaign/site composition model instead of supporting old shapes indefinitely.

## 5. Dashboard Order

The dashboard should answer one question: "What should I do next?"

Do not lead with technical site/page management. Lead with campaign outcomes.

Standard top menu:

1. Home
2. Brand
3. Content
4. Media
5. Campaign
6. Products
7. Websites

Top menu styling should use icon over text so a new marketer can recognize sections quickly. Results are not a top-level menu item; they belong inside Campaign as campaign-level performance tabs, cards, or detail sections.

Recommended dashboard order:

1. Start A Campaign
2. Continue Your Work
3. Live Campaigns
4. Websites And Pages
5. Content Library
6. Brands
7. Media
8. Products
9. Settings

Why this order:

- New marketers need a visible starting point before they understand the product.
- Returning marketers need resumable work and next actions before browsing inventory.
- Live campaigns should expose results inline after work has shipped.
- Content, brands, media, and products are supporting Marketing CMS infrastructure, but they need first-class homes because campaigns reuse them.
- Settings belongs in account/admin utility, not the main top menu.

### 5.1 Start A Campaign

This is the first visual block on the dashboard.

Primary CTA:

- `Start a campaign`

Fast-start cards:

- Promote a product or service
- Capture leads
- Announce an offer
- Build a landing page
- Sell products (available when Products are configured)

Each card should use plain language and one sentence of helper text. The user should not need to know page types, section names, or schemas.

### 5.2 Continue Your Work

Show drafts that need action.

Each item should show:

- campaign name
- status
- next action
- last edited time
- primary button

Example next actions:

- Finish offer
- Review messages
- Preview landing page
- Add header and footer
- Launch campaign

The button should say the action, not `Open`.

### 5.3 Live Campaigns

Show campaigns that are published or ready to monitor.

Each item should show:

- campaign name
- published site/page
- current state
- primary CTA

Initial CTAs:

- Edit campaign
- Duplicate
- View page

Future CTA:

- View results

### 5.4 Websites And Pages

This is an operational section, not the main mental model.

Show:

- site name
- pages
- publish status
- last updated

Primary actions:

- Edit site
- Add page
- Preview

### 5.5 Products

Products should be a separate dashboard area, not a subsection under Brand.

Show shortcuts:

- Add product
- Import products
- Product collections
- Products missing images
- Products missing brand tags

Each product can be tagged to one or more brands. This supports multi-brand stores, agency accounts, product families, and cross-brand promotions.

### 5.6 Brands

The current Brand tab should become Brands.

Show shortcuts:

- Add brand
- Brand profiles
- Logos and colors
- Voice and tone
- Header and footer
- Saved brand messages

Each campaign should select one primary brand. Products selected for that campaign can come from that brand or from products tagged to multiple brands.

### 5.7 Media

Media should be a reusable asset library, not a website-only upload browser.

Show shortcuts:

- Brand assets
- Product images
- Campaign assets
- Website/page assets
- Unused media
- Media missing alt text

### 5.8 Campaign Results

Results are future scope, but they should live inside Campaign rather than the top menu. Live campaign cards can surface the most important metric, and each campaign detail view should reserve a familiar Results area.

Future cards:

- Visitors
- Leads
- Sales
- Conversion rate
- Best campaign
- Recommended next action

Until analytics exists, this campaign-level area can be hidden or shown as "Results coming soon" behind a feature flag.

## 6. Campaign Studio Order

Campaign Studio should follow the way a marketer thinks about launching a campaign.

Recommended workspace order:

1. What Are You Promoting?
2. Who Is It For?
3. What Should They Do?
4. Offer And Proof
5. Messages
6. Landing Page
7. Brand, Products, Media, And Site Sections
8. Review
9. Launch
10. Future: Campaign Results

This order should replace the old guided flow sequence.

Why this order:

- Promotion context comes first because it anchors every later decision.
- Audience comes before copy because message quality depends on who the campaign is for.
- Conversion goal comes before layout because page structure should serve the action.
- Offer/proof comes before messages because strong landing pages need substance before polish.
- Messages come before page editing because reusable claims, CTAs, and proof should power the page and future channels.
- Landing page comes before brand/site sections because marketers want to see the campaign take shape quickly.
- Review and launch come last because they are confidence-building steps.

### 6.1 What Are You Promoting?

This is the campaign brief.

Ask only what is needed:

- brand
- campaign name
- product, service, collection, or offer
- short description
- source material, if available
- destination site, if one already exists

Primary action:

- `Create campaign plan`

AI should infer as much as possible and ask follow-up questions only when required.

Brand behavior:

- If one brand exists, preselect it.
- If multiple brands exist, show a simple brand selector.
- If no brand exists, allow inline brand creation with only brand name required.

Product behavior:

- If the goal is sales, show product and collection selectors.
- Products can be tagged to one or more brands.
- If selected products belong to multiple brands, ask the marketer which brand voice and visual identity should lead the campaign.

### 6.2 Who Is It For?

Audience is a marketer-friendly step and should come before page structure.

Fields:

- target audience
- problem or desire
- awareness level
- buying stage
- location or segment, if relevant

Use selectable suggestions generated by AI. Do not start with a blank strategy form.

### 6.3 What Should They Do?

This step defines the conversion goal.

Goal choices:

- Get leads
- Book calls
- Sell products
- Promote an offer
- Collect signups
- Drive traffic
- Share information

For the first implementation, ecommerce goals can be visible as future or disabled if product/catalog support is not ready.

### 6.4 Offer And Proof

This step turns vague campaign intent into something publishable.

Fields:

- offer
- primary CTA
- secondary CTA
- benefits
- proof points
- objections
- FAQs

AI should draft these, and the user should review/edit them in plain cards.

### 6.5 Messages

This is the marketer-facing label for internal content atoms.

Group messages by practical use:

- Headlines
- Subheadlines
- Benefits
- Proof
- Objection answers
- FAQs
- CTAs
- Testimonials

Each message item should support:

- edit
- keep
- regenerate
- use on page

Use `keep` instead of `lock` in the primary UI. It is easier for non-technical users to understand.

### 6.6 Landing Page

The page step should show the generated landing page as soon as possible.

Default layout:

1. Hero with offer
2. Trust or proof strip
3. Benefits
4. How it works
5. Offer details
6. Testimonials or proof
7. FAQ
8. Final CTA

The user should edit by clicking visible page sections in preview or selecting simple section names. Do not make the user choose YAML components first.

Useful controls:

- Regenerate section
- Rewrite shorter
- Rewrite stronger
- Change CTA
- Add proof
- Move section
- Hide section

Raw YAML should be available only in an advanced/debug view.

#### Technical Notes

**Responsive preview:** The existing toolbar supports Desktop/Tablet/Mobile viewport switching. Generation should produce mobile-friendly layouts by default (single-column hero, stacked benefits, full-width CTAs).

**Autosave:** Campaign Studio must autosave field state on blur/change, similar to the existing page editor autosave (PUT to page endpoint). "Continue Your Work" on the dashboard depends on this.

**Multi-page support:** Campaigns commonly need more than one page. V1 should support at minimum:

- Landing page (primary)
- Thank-you / confirmation page (post-conversion)

The Campaign model links to a Site (which already supports multiple SitePages). Each campaign page maps to a SitePage record.

### 6.7 Brand, Products, Media, And Site Sections

This is the marketer-facing area for reusable CMS assets that influence the generated page.

It spans four storage layers with different scopes.

#### Layer 1: Site Sections (exists today)

These are stored in the `SiteSharedBlock` model with per-page override support (inherit/hidden/custom).

Show common sections:

- Header
- Footer
- Announcement bar
- Trust strip
- Global CTA
- Newsletter signup
- Product promo strip

Behavior:

- Store these once at the site level.
- Let the user show/hide them per page.
- Let the user override them per page when needed.
- Preview and publish using composed renderer-compatible YAML.

No backend changes needed. Surface these in Campaign Studio with marketer-friendly labels.

#### Layer 2: Brands (new, org-level, multi-brand)

Stored as first-class `Brand` records. An organization can have many brands.

Fields:

- business name
- tagline
- logo URL
- brand colors (primary, secondary, accent, background)
- brand fonts (heading family, body family)
- tone of voice (formal / casual / playful / authoritative)

Usage: AI generation prompts receive brand kit as context. Style themes are filtered or customized based on brand colors. Exported pages use brand fonts and colors by default.

Campaign rule:

- A campaign selects one primary brand.
- The selected brand controls voice, visual identity, default logo, default fonts, and default shared site sections.

#### Layer 3: Products (new, org-level)

Products live in a separate Products tab and can be tagged to one or more brands.

Product fields:

- name
- short description
- long description
- product type
- price
- availability
- product images
- tags
- brand tags
- collections

Campaign rule:

- Sales campaigns select products or collections.
- Product data should be treated as factual CMS data.
- AI should not invent prices, availability, or product claims when product records exist.

#### Layer 4: Content Library And Media (new, org-level)

Stored in a new `ContentItem` model with category + content + org_id. Reusable across campaigns.

Content types:

- Testimonials
- Case studies / credentials
- About us boilerplate
- Terms and privacy text
- Saved headlines and CTAs
- Media assets (linked to existing SiteImage)

Behavior:

- Messages marked "keep" in any campaign can be saved to the content library.
- Content library items can be pulled into new campaigns without regeneration.
- AI generation references library items when they match the audience/offer.
- Content can be global, brand-specific, product-specific, or campaign-sourced.
- Media assets can be assigned to brands, products, campaigns, websites, and pages.

### 6.8 Review

Review should read like a launch checklist.

Checklist:

- Campaign goal is clear
- Audience is selected
- Offer is complete
- Messages are ready
- Landing page is generated
- Header and footer are set
- Page preview works
- Publish destination is selected

Do not show technical validation errors first. Translate them into user tasks when possible.

Examples:

- "Add a headline to the hero section"
- "Choose a CTA for the final section"
- "Footer is missing contact text"

### 6.9 Launch

Launch should be a simple publishing step.

Actions:

- Publish page
- Copy preview link
- Duplicate campaign
- Future: create email/ad/social outputs

The publish flow should use the existing site/page/version system and the site composition model behind the scenes.

## 7. Chat Integration

Chat should support marketers without becoming the whole product surface.

### 7.1 Routing Behavior

- If the user asks to build a marketing site, create a campaign draft.
- If the user asks for copy, add or revise Messages.
- If the user asks to change a page section, edit that section and preserve kept messages.
- If the user asks to create a new page, ask which campaign goal it supports.

Chat should hand users into the right Campaign Studio step instead of trapping them in a chat-only wizard.

### 7.2 Chat → Campaign Studio Handoff Protocol

1. User types something like "build me a landing page for my yoga studio".
2. `QueryAnalyzer` detects `create_page` intent (existing logic).
3. Instead of starting the guided flow, chat responds with a message and a CTA button: "I'll set up a campaign for your yoga studio. [Open Campaign Studio →]"
4. Backend creates a draft Campaign record with:
   - `name`: inferred from message (e.g., "Yoga Studio Launch")
   - `product_or_service`: extracted entity
   - `description`: user's original message
   - `status`: draft
5. Frontend navigates to `/campaign-studio/<new_campaign_id>`.
6. Campaign Studio Step 1 loads with pre-filled fields from the draft.

### 7.3 In-Context Chat Within Campaign Studio

Each Campaign Studio step should have a contextual "Help me" action that opens a scoped chat panel:

- Chat receives the current campaign state as context (not just YAML).
- Scoped to the active step. Examples:
  - On Messages step: "Write 3 more headlines for this audience"
  - On Offer step: "Suggest proof points for a SaaS product"
  - On Landing Page step: "Make the hero section more urgent"
- Responses update campaign fields directly (with user confirmation).

### 7.4 Existing Chat Preservation

For users already in the page editor (not Campaign Studio), the current chat behavior remains:

- `modify` intent → edit YAML in place
- `add` intent → insert component
- `explain` intent → answer question
- `create_section` intent → generate and insert a section

These do not require Campaign Studio and continue to work as-is.

## 8. Ecommerce Future Scope

Swift Sites should support ecommerce through specific CMS and page types. Do not model ecommerce as just another generic landing page section.

Key principles for future ecommerce:

- Product data lives in CMS/catalog records (Product, Variant, Collection models).
- Products are managed in a separate Products dashboard tab.
- Products can be tagged to one or more brands.
- Campaign messages describe offer and positioning.
- Product Collection Pages have dedicated controls (grid, filters, sort, cards).
- The Campaign Studio gains a "Sell products" goal with a product-specific flow.

Detailed ecommerce and CMS specifications are covered in [MULTI_BRAND_CMS_PRODUCTS_PLAN.md](MULTI_BRAND_CMS_PRODUCTS_PLAN.md).

## 9. Campaign Performance Future Scope

Campaign performance is future scope, but the UI should reserve a clear Results area inside Campaign.

Key principles for future analytics:

- Campaign IDs are carried through generated sites and pages (already supported via `campaign_id` on Site).
- Future metrics: visitors, leads, sales, CTA clicks, form submissions, conversion rate, best message, channel performance.
- The Campaign Results area connects performance back to campaign strategy, messages, and page sections.

Detailed analytics specifications will be documented separately when this scope enters active development.

## 10. Internal Mapping

The UI should use marketer labels while the implementation keeps structured models.

```text
UI: Campaign
Internal: Campaign schema/model

UI: Campaign Plan
Internal: Strategy fields

UI: Brands
Internal: Brand records scoped to org

UI: Messages
Internal: Content atoms

UI: Landing Page
Internal: Page purpose + page recipe + page body YAML

UI: Brand And Site Sections
Internal: Brand + Site shared blocks + page overrides

UI: Website
Internal: Site + SitePage + published versions

UI: Products
Internal: Product + ProductBrand + ProductCollection records

UI: Media
Internal: MediaAsset records and assignment tables

UI: Campaign Results
Internal: Future campaign analytics/performance records
```

The UI should not make renderer YAML the source of truth for campaign intent. Renderer YAML is the compiled output.

## 11. Campaign Data Model

The following schema defines how campaign state is stored. The existing `campaign_id` field on the Site model provides the link between campaigns and their generated sites.

```text
Campaign
  id              UUID (PK)
  org_id          FK → Organization
  name            VARCHAR(200)
  status          ENUM: draft / active / paused / completed
  goal            ENUM: leads / calls / sales / signups / traffic / inform
  site_id         FK → Site (nullable, linked after page generation)
  created_at      TIMESTAMP
  updated_at      TIMESTAMP

CampaignBrief
  id              UUID (PK)
  campaign_id     FK → Campaign (unique, 1:1)
  product_or_service   TEXT
  description          TEXT
  target_audience      TEXT
  problem_or_desire    TEXT
  awareness_level      ENUM: unaware / problem_aware / solution_aware / product_aware / most_aware
  buying_stage         ENUM: research / consideration / decision / retention
  location_or_segment  VARCHAR(200), nullable

CampaignOffer
  id              UUID (PK)
  campaign_id     FK → Campaign (unique, 1:1)
  offer           TEXT
  primary_cta     VARCHAR(200)
  secondary_cta   VARCHAR(200), nullable
  benefits        JSON array of strings
  proof_points    JSON array of strings
  objections      JSON array of strings
  faqs            JSON array of {question, answer} objects

CampaignMessage
  id              UUID (PK)
  campaign_id     FK → Campaign
  category        ENUM: headline / subheadline / benefit / proof / objection / faq / cta / testimonial
  content         TEXT
  is_kept         BOOLEAN (default false) — kept messages survive regeneration
  used_in_section VARCHAR(100), nullable — section placement reference
  sort_order      INTEGER
  created_at      TIMESTAMP
```

Relationships:

- Campaign 1:1 CampaignBrief
- Campaign 1:1 CampaignOffer
- Campaign 1:many CampaignMessage
- Campaign 1:1 Site (via site_id, created during page generation)
- Site 1:many SitePage (existing)

Multi-brand/product additions:

```text
Campaign
  brand_id        FK -> Brand, nullable

CampaignProduct
  campaign_id     FK -> Campaign
  product_id      FK -> Product
  role            promoted / upsell / proof / comparison
  sort_order      INTEGER

CampaignCollection
  campaign_id     FK -> Campaign
  collection_id   FK -> ProductCollection
  role            promoted / related
  sort_order      INTEGER
```

Additional relationships:

- Campaign many:1 Brand (primary brand)
- Campaign many:many Product through CampaignProduct
- Campaign many:many ProductCollection through CampaignCollection

Product and brand details are specified in [MULTI_BRAND_CMS_PRODUCTS_PLAN.md](MULTI_BRAND_CMS_PRODUCTS_PLAN.md).

## 12. Campaign Compiler

The campaign compiler transforms structured campaign data into builder-agent-compatible input. It replaces the free-text `business_context` dict that the guided flow currently passes to the planner.

### Input

- CampaignBrief (audience, awareness, product)
- Selected Brand (voice, colors, fonts, logo, tone)
- Selected Products or Collections (for sales/product campaigns)
- CampaignOffer (offer, CTAs, benefits, proof, FAQs)
- CampaignMessages (kept messages, grouped by category)
- Selected style/theme (from styler agent or user choice)
- Assigned media (from org-level MediaAsset records)

### Output

A section outline compatible with `BuilderAgent.build_section()`, where each section carries structured content fields instead of free-text descriptions.

### Section Mapping Rules

```text
Hero Section
  ← headline messages (category: headline, first 1-2 kept)
  ← offer text
  ← primary CTA
  ← hero image assignment
  ← subheadline messages (category: subheadline)

Trust / Proof Strip
  ← proof_points (first 3-5 items)
  ← testimonial messages (if available, short quotes)

Benefits Section
  ← benefits array → columnsgrid with icon + heading + paragraph per benefit
  ← benefit messages (category: benefit)

How It Works
  ← derived from description + awareness_level
  ← 3-5 steps inferred from product/service type

Offer Details
  ← full offer text
  ← secondary CTA
  ← objection answers (category: objection)

Testimonials
  ← testimonial messages (category: testimonial)
  ← proof_points (longer-form items)

FAQ
  ← faqs array → accordion component
  ← faq messages (category: faq)

Final CTA
  ← primary CTA (repeated)
  ← headline messages (urgency variant)
  ← offer summary (1 line)
```

### Integration with Builder Agent

The campaign compiler produces a `business_content` dict per section (same interface the guided flow uses today). The builder agent's existing logic for "when business_content is present, use exact values" applies without modification.

Key difference from current guided flow: campaign compiler pulls from structured, validated fields rather than raw user text collected in a chat wizard.

## 13. Suggested Implementation Changes

New UI files:

- `ssr_python/static/js/campaignStudio.js`
- `ssr_python/static/css/campaign-studio.css`
- `ssr_python/templates/campaign_studio.html`

New route/module candidates:

- `ssr_python/routes/campaign.py`
- `ssr_python/routes/brand.py`
- `ssr_python/routes/product.py`
- `ssr_python/routes/media.py`
- `ssr_python/campaign/schema.py`
- `ssr_python/campaign/validators.py`
- `ssr_python/campaign/compiler.py`
- `ssr_python/campaign/recipes/`

Guided flow replacement:

- Stop expanding `ssr_python/static/js/guidedFlow.js`.
- Replace current guided creation entry points with Campaign Studio.
- Move reusable options into campaign intake config.
- Replace `/api/chat/guided` with campaign draft and campaign generation APIs when ready.
- Migrate example templates to the new campaign/site composition direction.

## 14. UX Acceptance Criteria

The first Campaign Studio implementation should be considered complete when:

- A new marketer can start from the dashboard without reading documentation.
- The dashboard clearly shows the next action for drafts and live campaigns.
- The primary CTA is campaign creation, not raw site/page creation.
- The campaign workspace uses marketer labels and hides implementation terms.
- AI drafts a campaign plan, messages, and one landing page.
- Campaigns can select a primary brand.
- Sales/product campaigns can select products or collections.
- Products can be tagged to one or more brands.
- Header, footer, and reusable site sections are visible in plain language.
- Preview and publish use composed renderer-compatible YAML behind the scenes.
- The old guided flow is replaced, not kept as a product path.

### Measurable Proxies

- Time to first campaign draft: under 3 minutes from dashboard load.
- Screens to publish: maximum 9 distinct screens from "Start a Campaign" to "Publish".
- AI generation quality: generated page renders without YAML parse errors on first attempt in more than 90% of generations.
- No implementation language in primary UI: a grep audit of Campaign Studio HTML/JS finds zero instances of "YAML", "renderer", "compiler", "atoms", "schema", or "recipe" in user-visible strings.
- All guided flow entry points redirect to Campaign Studio with no dead paths.
- Autosave: campaign state persists across browser refresh at every step.

## 15. Phased Implementation Plan

### Phase 1: Campaign Model and API (Backend Only)

Scope:

- SQLAlchemy models: Campaign, CampaignBrief, CampaignOffer, CampaignMessage
- Alembic migration
- CRUD routes: `ssr_python/routes/campaign.py`
  - POST /api/campaigns (create draft)
  - GET /api/campaigns (list for org)
  - GET /api/campaigns/<id> (full campaign with brief, offer, messages)
  - PATCH /api/campaigns/<id> (update fields)
  - DELETE /api/campaigns/<id>
  - POST /api/campaigns/<id>/messages (add/regenerate messages)
  - PATCH /api/campaigns/<id>/messages/<msg_id> (edit, keep, reorder)
- Campaign compiler module: `ssr_python/campaign/compiler.py`
- Tests for models, routes, and compiler

Exit criteria: API is functional, compiler produces valid builder-agent input from test campaign data.

### Phase 2: Campaign Studio UI (Steps 1-5)

Scope:

- Flask route: GET /campaign-studio/<campaign_id>
- Template: `campaign_studio.html` (step-based layout)
- JavaScript: `campaignStudio.js` (step navigation, field autosave, AI draft triggers)
- CSS: `campaign-studio.css`
- Steps implemented: What Are You Promoting, Who Is It For, What Should They Do, Offer And Proof, Messages
- AI drafting for offer fields and messages (extend RAG agent with campaign context)
- "Keep" toggle on messages

Exit criteria: User can complete steps 1-5, all fields persist, AI generates offer and messages from brief.

### Phase 3: Landing Page Integration (Step 6)

Scope:

- Campaign compiler feeds builder agent (replaces guided flow business_context)
- Page preview renders in iframe (existing renderer)
- Section-level controls: regenerate, rewrite shorter/stronger, move, hide
- Campaign links to Site/SitePage on first generation
- Thank-you page generation (optional second page)

Exit criteria: Completing step 6 produces a rendered, publishable landing page from campaign data.

### Phase 4: Dashboard Pivot

Scope:

- New dashboard layout: Start A Campaign, Continue Your Work, Live Campaigns, Websites And Pages, Products, Brands, Media
- Campaign status badges and next-action buttons
- Retire guided flow entry points (redirect to Campaign Studio)
- Remove `/api/chat/guided` as primary creation path
- Chat handoff protocol (create_page intent → draft campaign → navigate)

Exit criteria: Dashboard leads with campaigns. No user path reaches the old guided wizard.

### Phase 5: Multi-Brand CMS, Products, Media, And Content Library

Scope:

- Multi-brand `Brand` model with colors, fonts, tone, logo, and voice
- Products tab and product-brand tagging model
- Org-level MediaAsset model
- ContentItem model for reusable messages/testimonials with optional brand/product scope
- Brands UI in dashboard
- Products UI in dashboard
- Content Library panel with save-from-campaign and pull-into-campaign actions
- AI generation uses selected brand, products, media, and content as prompt context

Exit criteria: Multiple brands persist org-wide. Products can be tagged to brands. Campaigns can select a brand and product context. Kept messages can be saved to and reused from global, brand, or product library scope.
