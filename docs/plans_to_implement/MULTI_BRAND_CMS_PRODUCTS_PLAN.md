# Multi-Brand CMS And Products Plan

## 1. Product Decision

Swift Sites should support multiple brands inside one organization.

Products should be a separate dashboard tab. Products can be tagged to one or more brands.

This is the cleaner long-term model because Swift Sites is not only a single-business website generator. It is a campaign, CMS, AI, and future ecommerce workspace. Agencies, marketplace sellers, multi-brand stores, and operators with sub-brands should not be forced into one org-level brand kit.

## 2. UX Principle

Marketers should not need to understand CMS architecture.

Use simple UI labels:

- Home
- Brands
- Content
- Media
- Campaign
- Products
- Websites

Avoid making users think about database scope. The interface should naturally answer:

- Which brand is this campaign for?
- Which products are being promoted?
- Which images and saved copy can I reuse?
- Which campaign/page/result used this asset?

## 3. Dashboard Navigation

Recommended top navigation order:

1. Home
2. Brand
3. Content
4. Media
5. Campaign
6. Products
7. Websites

Why this order:

- Home gives new marketers a clear starting point.
- Brand comes first because brand context controls voice, visuals, trust, and reusable rules.
- Content is first-class because the Content Library is the Marketing CMS memory.
- Media supports brands, content, products, campaigns, and websites.
- Campaign is the primary activation workspace, including campaign results and performance learning.
- Products are a first-class ecommerce/CMS object, not a media detail.
- Websites are generated outputs and operational surfaces.
- Settings belongs in the account/admin utility area, not in the primary marketer workflow.

## 4. Brand Model

Replace the single `OrgBrandKit` concept with a first-class `Brand` model.

Recommended fields:

```text
Brand
  id                  UUID PK
  org_id              FK -> Organization
  name                VARCHAR
  slug                VARCHAR
  status              active / archived
  tagline             VARCHAR
  description         TEXT
  industry            VARCHAR
  website_url         VARCHAR
  logo_media_id       FK -> MediaAsset nullable
  favicon_media_id    FK -> MediaAsset nullable
  tone                VARCHAR
  voice_guidelines    TEXT
  color_primary       VARCHAR
  color_secondary     VARCHAR
  color_accent        VARCHAR
  color_background    VARCHAR
  font_heading        VARCHAR
  font_body           VARCHAR
  created_at          TIMESTAMP
  updated_at          TIMESTAMP
```

Rules:

- An org can have many brands.
- A brand can have many campaigns, products, media assets, and content items.
- One brand can be marked as default for new campaigns.
- Archived brands should not appear in primary creation flows, but historical campaigns should keep their brand links.

## 5. Product Model

Products should live in their own tab and own data model.

Recommended fields:

```text
Product
  id                  UUID PK
  org_id              FK -> Organization
  name                VARCHAR
  slug                VARCHAR
  status              draft / active / archived
  product_type        physical / digital / service / subscription
  short_description   TEXT
  description         TEXT
  sku                 VARCHAR nullable
  price               DECIMAL nullable
  compare_at_price    DECIMAL nullable
  currency            VARCHAR default USD
  availability        in_stock / out_of_stock / preorder / service_only
  default_media_id    FK -> MediaAsset nullable
  attributes          JSON
  tags                JSON
  created_at          TIMESTAMP
  updated_at          TIMESTAMP
```

Products can be tagged to different brands through a join table:

```text
ProductBrand
  product_id          FK -> Product
  brand_id            FK -> Brand
  role                primary / associated / reseller / compatible
  sort_order          INTEGER
  created_at          TIMESTAMP
```

UX rule:

- In the Product form, show a simple multi-select called `Brands`.
- If a product has multiple brands, allow one to be marked as `Primary` only when needed.
- Most users should not see the word `ProductBrand`.

## 6. Product Collections

Collections should be separate from brands.

Recommended fields:

```text
ProductCollection
  id                  UUID PK
  org_id              FK -> Organization
  name                VARCHAR
  slug                VARCHAR
  description         TEXT
  status              draft / active / archived
  brand_id            FK -> Brand nullable
  filter_config       JSON
  sort_order          INTEGER
  created_at          TIMESTAMP
  updated_at          TIMESTAMP

ProductCollectionItem
  collection_id       FK -> ProductCollection
  product_id          FK -> Product
  sort_order          INTEGER
```

Collection rules:

- A collection can be brand-specific or cross-brand.
- A product can appear in many collections.
- Campaigns should be able to promote a product, many products, or a collection.

## 7. Media Model

Media should become org-level, then assigned to brands/products/campaigns/sites.

Recommended replacement for site-only media:

```text
MediaAsset
  id                  UUID PK
  org_id              FK -> Organization
  filename            VARCHAR
  original_name       VARCHAR
  storage_path        VARCHAR
  mime_type           VARCHAR
  file_size           INTEGER
  width               INTEGER
  height              INTEGER
  orientation         landscape / portrait / square
  alt_text            VARCHAR
  source              upload / pexels / pixabay / generated
  source_url          TEXT
  license_label       VARCHAR
  photographer        VARCHAR
  focal_point_x       DECIMAL nullable
  focal_point_y       DECIMAL nullable
  tags                JSON
  created_at          TIMESTAMP
```

Use explicit assignment tables for reliable CMS relationships:

```text
BrandMediaAsset
  brand_id            FK -> Brand
  media_asset_id      FK -> MediaAsset
  role                logo / favicon / hero / gallery / background
  sort_order          INTEGER

ProductMediaAsset
  product_id          FK -> Product
  media_asset_id      FK -> MediaAsset
  role                primary / gallery / detail / lifestyle / packaging
  sort_order          INTEGER

CampaignMediaAsset
  campaign_id         FK -> Campaign
  media_asset_id      FK -> MediaAsset
  role                hero / proof / product / background / social
  sort_order          INTEGER
```

Avoid making media belong only to a site. A site can use media, but media should be reusable before a site exists.

## 8. Content Library Scope

Content should also support brand and product context.

Recommended fields to add to `ContentItem`:

```text
ContentItem
  org_id
  brand_id            FK -> Brand nullable
  product_id          FK -> Product nullable
  source_campaign_id  FK -> Campaign nullable
  category            headline / tagline / benefit / testimonial / case_study / about / cta / faq / boilerplate
  title
  content
  tone
  is_pinned
  created_at
  updated_at
```

Rules:

- `brand_id = null` means global reusable content.
- `product_id = null` means not product-specific.
- Campaign generation should prefer brand-specific and product-specific content over global content.

## 9. Campaign Links

Campaigns should select a primary brand and optionally selected products or collections.

Recommended additions:

```text
Campaign
  brand_id            FK -> Brand nullable

CampaignProduct
  campaign_id         FK -> Campaign
  product_id          FK -> Product
  role                promoted / upsell / proof / comparison
  sort_order          INTEGER

CampaignCollection
  campaign_id         FK -> Campaign
  collection_id       FK -> ProductCollection
  role                promoted / related
  sort_order          INTEGER
```

UX rule:

- Campaign Studio Step 1 should ask `Which brand is this for?`
- If the goal is `Sell products`, Step 1 should also ask `Which products or collection are you promoting?`
- If no brand exists, offer inline brand creation.
- If no products exist and the user chooses a sales goal, offer inline product creation or defer the sales goal.

## 10. Products Tab UX

The Products tab should be a working catalog manager, not just a list.

Primary views:

- Product list
- Product detail
- Collections
- Import

Product list controls:

- Search
- Brand filter
- Status filter
- Product type filter
- Tag filter
- Availability filter
- Sort

Product card/list fields:

- image
- product name
- brands
- price
- status
- availability
- last updated

Product actions:

- Edit
- Duplicate
- Create campaign
- Add to collection
- Archive

Product detail sections:

- Basics
- Brands
- Pricing
- Images
- Descriptions
- Attributes
- Collections
- Campaigns using this product

## 11. Brands Tab UX

The current Brand tab should become Brands.

Brand list:

- brand logo
- brand name
- tagline
- product count
- campaign count
- readiness status

Brand detail sections:

- Identity
- Voice
- Colors and fonts
- Logos and media
- Site sections
- Products
- Campaigns
- Saved content

Brand actions:

- Create campaign for this brand
- Add product
- Add media
- Duplicate brand
- Archive brand

## 12. Media Tab UX

The Media tab should show all org media first.

Filters:

- Brand
- Product
- Campaign
- Website
- Orientation
- Source
- Tag
- Search

Asset detail panel:

- preview
- alt text
- tags
- source/license
- assigned brands
- assigned products
- assigned campaigns
- assigned websites/pages

Media actions:

- Upload
- Search stock
- Assign to brand
- Assign to product
- Assign to campaign
- Replace usage
- Delete if unused

## 13. Campaign Studio Changes

Campaign Studio should consume CMS assets without exposing CMS complexity.

Step 1 should include:

- Brand selector
- Product/service/offer field
- Product selector when goal is sales
- Collection selector when goal is sales and collections exist

Landing Page step should use:

- selected brand logo/colors/fonts/tone
- selected product images and descriptions
- selected campaign media roles
- saved brand/product testimonials and proof

Messages step should support:

- Save to brand library
- Save to product library
- Pull from brand library
- Pull from product library

## 14. Generation Rules

Generation priority:

1. Campaign-specific kept messages and selected media
2. Selected product data and product media
3. Selected brand profile, content, and media
4. Global content library
5. AI-generated fallback content

The generator should not invent product prices, availability, or product claims when product records exist.

## 15. Implementation Phases

### Phase 1: Align Existing UI

- Rename dashboard Brand tab to Brands.
- Add Products tab shell.
- Fix Media tab response handling.
- Hide or gate product-selling campaign actions until products exist.
- Update copy so marketers understand Brands, Products, Media, Campaigns.

### Phase 2: Data Model

- Add `Brand`.
- Add `Product`, `ProductBrand`, `ProductCollection`, `ProductCollectionItem`.
- Add `MediaAsset` and assignment tables.
- Add `brand_id` to Campaign.
- Add campaign-product and campaign-collection links.
- Add brand/product fields to ContentItem.

Backward compatibility is not required. Prefer replacing `OrgBrandKit` and `SiteImage` with the cleaner model, then migrate repository-owned examples/tests.

### Phase 3: APIs

- `/api/brands`
- `/api/products`
- `/api/products/<id>/brands`
- `/api/collections`
- `/api/media`
- `/api/media/<id>/assignments`
- campaign update endpoints for selected brand/products/collections

### Phase 4: Campaign Studio Integration

- Add brand selector to Step 1.
- Add product/collection selector for sales campaigns.
- Pull brand/product/media/content context into generation.
- Let users save and reuse messages by brand/product.

### Phase 5: Ecommerce Page Generation

- Add Product Collection Page.
- Add product grid, filters, sort, empty state, and product card settings.
- Compile product page data into renderer-compatible YAML.
- Keep product records as CMS data, not static copied page text.
