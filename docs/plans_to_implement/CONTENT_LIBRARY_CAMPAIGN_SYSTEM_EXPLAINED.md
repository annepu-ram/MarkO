# Content Library And Campaign System Explained

## 1. Validation Verdict

The existing direction is correct: Swift Sites should treat the Content Library as the marketing CMS brain, not as a folder of saved snippets.

The plan needed one major refinement: it should describe the full marketing engine, not only how AI selects stored content for landing pages. A strong online marketing engine needs a content lifecycle:

1. Capture brand, product, proof, offer, media, and customer context.
2. Let AI generate and improve content from that context.
3. Let marketers approve, edit, tag, and reuse the best content.
4. Deploy approved content into campaigns, pages, forms, ads, email, and future ecommerce surfaces.
5. Track what performs.
6. Feed winning content back into the library so future campaigns get smarter.

This document is still a design and planning artifact. It does not require implementation changes by itself.

## 2. Product Thesis

Swift Sites should become an online marketing engine powered by a Marketing CMS.

The website builder is only one output. The real product is the system that turns brand knowledge, product data, offers, proof, and AI-generated copy into campaigns that can be launched, measured, and improved.

Core belief: content is king.

That means content cannot be treated as disposable text generated once for a page. Content must be structured, reusable, searchable, performance-aware, brand-safe, and AI-accessible.

### Standard Top Menu Decision

Use one fixed top menu across design snapshots and product implementation:

1. Home
2. Brand
3. Content
4. Media
5. Campaign
6. Products
7. Websites

Content Library belongs under `Content`, not inside `Brand`.

Results and performance reporting belong inside `Campaign`. They should appear as campaign-level tabs, cards, or detail sections, not as a top-level menu item.

Settings belongs in the account/admin utility area, not in the primary marketer workflow.

## 3. What The Content Library Is

The Content Library is the central CMS for marketing assets.

It stores:

- Reusable copy
- Offers and promotions
- Testimonials and social proof
- Product claims, features, specs, and comparisons
- FAQs and objection handlers
- Brand stories, values, mission, milestones, and team bios
- Forms and lead magnets
- Media references and content-media pairings
- AI-generated variants and human-approved winners

It is not only a library. It is the memory layer of the marketing engine.

## 4. What This Replaces

| Old Model | Target Model |
|-----------|--------------|
| Single `OrgBrandKit` | Multi-brand CMS with brand-specific libraries |
| Text-only `CampaignMessage` | Structured marketing content assets and variants |
| Site-scoped images | Org-level media assets assignable to brands, products, campaigns, and pages |
| AI writes from scratch | AI writes from brand, product, proof, offer, and performance context |
| One-off landing page copy | Reusable content that can power pages, ads, email, social, and ecommerce |
| No performance memory | Winners and losers feed future recommendations |

## 5. Marketing CMS Object Model

The current implementation can start with `ContentItem`, but the long-term model should distinguish content records from content variants and usage.

### 5.1 Content Asset

`ContentAsset` is the durable CMS record.

```text
ContentAsset
  id
  org_id
  brand_id nullable
  product_id nullable
  campaign_id nullable
  type
  subtype
  title
  status              draft / approved / active / archived / expired
  lifecycle_stage     ideation / reviewed / in_use / retired
  source              manual / ai / campaign / import / performance_winner
  owner_user_id nullable
  tone
  audience_segment
  buying_stage
  funnel_stage        awareness / consideration / decision / retention
  target_channels     landing_page / email / ad / social / sms / ecommerce
  tags JSON
  metadata JSON
  created_at
  updated_at
```

Rules:

- `brand_id = null` means global reusable content.
- `product_id = null` means not tied to a product.
- Only approved or active content should be used automatically in launched campaigns.
- Draft content can be used inside AI ideation and review flows, but not silently published.

### 5.2 Content Variant

`ContentVariant` stores the actual copy or structured payload.

```text
ContentVariant
  id
  content_asset_id
  variant_label
  body
  structured_payload JSON
  status              draft / approved / rejected / archived
  generated_by        human / ai
  model_name nullable
  prompt_snapshot nullable
  quality_score nullable
  performance_score nullable
  is_primary
  created_at
  updated_at
```

Why variants matter:

- A headline can have 10 AI-generated versions.
- The marketer can approve 2.
- Campaigns can A/B test approved variants.
- Future AI can learn which angle performs best.

### 5.3 Content Usage

Every place content is used should be recorded.

```text
ContentUsage
  id
  content_asset_id
  content_variant_id nullable
  campaign_id nullable
  site_id nullable
  page_id nullable
  section_key nullable
  channel
  placement
  usage_mode          pinned / pool / ai_selected / manually_inserted
  created_at
```

This answers:

- Where is this testimonial used?
- Which campaigns used this offer?
- Which headline appeared on the published page?
- Can this asset be safely archived?

### 5.4 Content Performance

Performance data is future scope, but the model should be planned now.

```text
ContentPerformance
  id
  content_asset_id
  content_variant_id nullable
  campaign_id nullable
  channel
  impressions
  clicks
  conversions
  leads
  revenue
  conversion_rate
  sample_size
  measured_at
```

Performance data should not be shown as false certainty. Low-sample winners should be marked as directional, not proven.

## 6. Content Types And Structured Schemas

Each content type needs its own fields. Generic text blobs are not enough for a marketing CMS.

### 6.1 Copy

Subtypes:

- headline
- subheadline
- tagline
- benefit
- CTA
- description
- ad copy
- email subject
- social caption

Structured fields:

- tone
- character_count
- target_section
- audience_segment
- buying_stage
- angle, such as speed, trust, savings, luxury, scarcity, proof, or convenience

### 6.2 Offers And Promotions

Subtypes:

- discount
- bundle
- free trial
- limited time
- seasonal
- launch offer
- win-back offer

Structured fields:

- code
- discount_type
- discount_value
- starts_at
- expires_at
- conditions
- min_purchase
- product_ids
- collection_ids
- redemption_url

Rules:

- Expired offers must not be used automatically.
- AI must not invent promo codes, discounts, prices, or expiry dates.
- Countdown sections should only render if `expires_at` exists.

### 6.3 Social Proof

Subtypes:

- testimonial
- review
- case study
- press mention
- partner logo
- statistic
- customer quote

Structured fields:

- author_name
- author_role
- company
- location
- rating
- quote_permission_status
- metric_before
- metric_after
- media_id
- proof_context

Rules:

- AI must never invent customer quotes.
- AI can summarize or reframe approved proof only if the original source is preserved.
- Legal or claim-sensitive proof should require approval before publish.

### 6.4 Forms And Lead Magnets

Subtypes:

- contact
- booking
- quiz
- calculator
- signup
- download
- waitlist

Structured fields:

- fields[]
- submit_label
- success_message
- redirect_url
- downloadable_asset_id
- consent_text
- destination

Why this matters:

- Lead generation campaigns need real fields, not generated guesses.
- Forms should be reusable and measurable.
- Future ecommerce checkout or product inquiry pages can reuse the same pattern.

### 6.5 Product Content

Subtypes:

- feature
- spec
- comparison
- how it works
- use case
- bundle
- compatibility
- guarantee

Structured fields:

- product_id
- feature_list[]
- specs[]
- comparison_items[]
- steps[]
- claims[]
- media_ids[]

Rules:

- Product pages and ecommerce-style product grids should use product records as source data.
- AI can improve wording, but it must not invent specs, prices, guarantees, availability, or compatibility.

### 6.6 FAQ And Objection Handlers

Subtypes:

- faq_pair
- objection_handler
- policy
- pricing objection
- shipping objection
- risk reversal

Structured fields:

- question
- answer
- concern
- response
- category
- related_product_ids
- related_offer_ids

### 6.7 Brand Story And Authority

Subtypes:

- mission
- founder story
- team bio
- milestone
- award
- certification
- values
- origin story

Structured fields:

- person_name
- role
- date
- issuer
- media_id
- authority_level
- display_context

## 7. AI Content System

AI should be a content producer, editor, strategist, and librarian. It should not be only a page generator.

### 7.1 AI Content Jobs

```text
AIContentJob
  id
  org_id
  brand_id nullable
  product_id nullable
  campaign_id nullable
  job_type
  input_context JSON
  prompt_snapshot
  output_status
  created_assets[]
  created_variants[]
  created_at
```

Job types:

- generate campaign messages
- generate headline variants
- generate ad copy
- generate email copy
- generate product benefits from product data
- rewrite in brand voice
- summarize proof into short snippets
- create FAQ suggestions from objections
- turn long copy into social posts
- improve weak content
- localize or segment content

### 7.2 AI Guardrails

AI must:

- Use approved brand tone and voice guidelines.
- Prefer approved content over draft content.
- Never invent testimonials, prices, product specs, promo codes, dates, or compliance claims.
- Mark generated claims that need human review.
- Preserve source links for generated summaries.
- Explain why it selected a content item when asked.

### 7.3 AI Content Quality Scoring

AI should help marketers judge quality before publish.

Recommended scoring dimensions:

- clarity
- specificity
- relevance to audience
- offer strength
- proof strength
- CTA clarity
- brand voice match
- risk of unsupported claims
- section fit

Scores should guide editing, not block publishing unless a hard rule is violated.

## 8. Campaign Content Flow

Campaign Studio should consume the Marketing CMS without exposing CMS complexity.

Flow:

```text
1. Marketer starts a campaign.
2. Campaign selects brand, products, audience, offer, and goal.
3. AI retrieves matching approved content from the library.
4. AI generates missing content from brand/product/campaign context.
5. Marketer reviews suggestions.
6. Marketer pins key content or leaves sections in pool mode.
7. Landing page is generated.
8. Marketer edits, keeps, rejects, or creates variants.
9. Approved content and winning variants are saved back to the library.
10. Future performance data ranks content for future campaigns.
```

Priority order during generation:

1. Pinned campaign content.
2. Campaign-specific kept messages.
3. Active offers tied to selected brand/product.
4. Product-specific facts, features, specs, images, and proof.
5. Brand-specific proof, story, voice, and approved copy.
6. Global approved content.
7. AI-generated fallback.

## 9. Pinned Content And Pool Content

Pinned content:

- Is locked to a specific campaign section.
- Renders exactly unless the user edits it.
- Survives page regeneration.
- Is ideal for hero headlines, legal copy, main offer text, and high-value testimonials.

Pool content:

- Is available for AI to choose from.
- Can rotate during regeneration.
- Is useful for testimonials, benefits, FAQs, and supporting proof.

The best workflow is hybrid: pin the most important content, let AI choose supporting material.

## 10. Content Library UX

The UI should feel like a marketer's working library, not a CMS database.

Primary tabs:

1. All
2. Copy
3. Offers
4. Proof
5. Products
6. FAQs
7. Forms
8. Brand Story
9. AI Drafts
10. Winners

Core filters:

- Brand
- Product
- Campaign
- Channel
- Funnel stage
- Status
- Tone
- Tag
- Performance
- Expiry

Content card fields:

- title
- short body preview
- type and subtype
- brand/product tags
- status
- source
- last used
- performance signal
- actions: use, edit, generate variants, archive

## 11. Campaign UX

Campaign Studio should include a content step that shows:

- AI-found library matches
- AI-generated missing content
- pinned section slots
- pool content candidates
- content quality warnings
- approval status
- generated variants

Marketer-facing labels:

- Use this
- Pin to section
- Generate alternatives
- Save to library
- Approve
- Needs review
- Replace

Avoid implementation labels:

- schema
- vector search
- compiler
- YAML
- payload
- embedding

## 12. Online Marketing Engine Loop

The final system should operate as a loop:

```text
Marketing CMS
  stores brand, product, proof, offers, copy, forms, and media
        |
        v
AI Content Engine
  creates, improves, scores, repurposes, and selects content
        |
        v
Campaign Studio
  combines goal, audience, offer, content, and page structure
        |
        v
Launch Outputs
  landing pages first; later ads, email, social, ecommerce pages
        |
        v
Results
  views, clicks, leads, conversions, revenue, content performance
        |
        v
Learning Layer
  promotes winners, archives weak assets, suggests improvements
        |
        v
Marketing CMS
```

This is the difference between a page generator and a marketing operating system.

## 13. Ecommerce Implications

Future ecommerce support should reuse the same content engine.

Product listing and product showcase pages need:

- product records
- product media
- feature content
- product FAQs
- reviews and proof
- offer badges
- filters and sort
- collection metadata
- comparison copy

AI can generate product page sections, but product facts must come from the product catalog and approved product content.

## 14. Implementation Phases

### Phase 1: Strengthen Current Content Library

- Keep the current simple `ContentItem` path working.
- Add brand/product filters everywhere content is shown.
- Add statuses: draft, approved, active, archived.
- Add AI draft category or source field.
- Add content source tracking.
- Add "Save to library" from campaign messages with brand and product context.

### Phase 2: Structured Content Types

- Add structured payload support.
- Add typed forms for offers, proof, FAQs, product content, and forms.
- Add validation rules per type.
- Add expiry handling for promotions.
- Add proof permission status.

### Phase 3: AI Content Studio

- Add AI generation actions inside the Content Library.
- Generate variants from brand/product/campaign context.
- Rewrite content in brand voice.
- Create missing campaign content before page generation.
- Save generated outputs as drafts until approved.

### Phase 4: Campaign Content Mapping

- Add campaign content pool.
- Add section-level pinned content.
- Record content usage.
- Let page regeneration preserve pinned content.
- Let AI explain why a content item was selected.

### Phase 5: Marketing Performance Loop

- Track usage across pages and campaigns.
- Add content performance records.
- Promote winning variants.
- Suggest underperforming content rewrites.
- Add future Campaign Results subtab integration.

### Phase 6: Multi-Channel Expansion

- Repurpose approved campaign content into email, ad, social, and SMS drafts.
- Keep each channel output linked to the original content asset.
- Add channel-specific performance tracking.

## 15. Success Criteria

The system is working when:

- A new marketer can launch a campaign without understanding CMS internals.
- AI uses brand/product/proof context before generating generic text.
- Approved content can be reused across multiple campaigns.
- Expired or unapproved content does not silently appear in live campaigns.
- Testimonials, prices, discounts, and product claims are never invented.
- Marketers can see where a content asset is used.
- Campaign winners become future content recommendations.
- The Content Library becomes more valuable after every campaign.

## 16. Final Summary

The Content Library should be the Marketing CMS that powers Swift Sites.

Campaigns are the operating workflow. AI is the content accelerator. Landing pages are the first output. Future ads, emails, social posts, and ecommerce pages should use the same content memory.

The target product is not "AI writes a website." The target product is "Swift Sites helps marketers build, reuse, launch, measure, and improve content across campaigns."
