# Content Tab UX Refactor Plan

## Summary

Refactor the Content tab into a cleaner CMS-style library with optional flat folders, grouped content types, better field order/help text, content-type-specific writing guidance, composite primitive slot editing, and an AI Enhance action that formats typed content into the recommended structure for the selected content type. Keep search global across all folders.

This refactor also preserves the core Swift Sites rendering contract: primitive and composite content items are source assets, sections are the renderable units, and sites/pages are powered by section YAML. Content is compiled into section YAML; the renderer renders YAML.

## Key Changes

### Content Organization

- Add flat optional folders for Content Library:
  - New `ContentFolder` model: `id`, `org_id`, `name`, `description`, `sort_order`, timestamps.
  - Add nullable `folder_id` to `ContentItem`.
  - No nesting and no multi-folder membership in V1.
- Add folder APIs:
  - `GET /api/content/folders`
  - `POST /api/content/folders`
  - `PATCH /api/content/folders/<id>`
  - `DELETE /api/content/folders/<id>`
- Update `GET /api/content`:
  - Add optional `folder_id` filter.
  - Search remains global when no folder is selected.
  - Search is folder-scoped only when a folder filter is active.
- Add UI:
  - Folder rail with `All content`, `Unfiled`, then folders.
  - Add/edit/delete folder controls.
  - Content cards show folder name when useful.
  - Add content form includes optional `Folder`.

### Add Content Form

- Reorder fields as:
  1. `Channel`
  2. `Content type`
  3. `Status`
  4. `Brand`
  5. `Product`
  6. `Source`
  7. `Folder`
  8. `Title`
  9. `Content`
  10. `Tags`
  11. `Expiry`
  12. `Quality score`
  13. Proof fields only when relevant
- Add concise helper text for each metadata field.
- Keep Quality score optional and advanced:
  - Helper: "Optional. Use only when you have a clear editorial or performance confidence score."
  - Do not require it.
  - Do not auto-populate it yet.

### Composite Primitive Slot UX

Composite content can always be created directly. Reusable primitives are optional accelerators, not prerequisites.

- Selecting a composite content type shows dynamic primitive slot fields.
- Slot fields are the source of truth for composite-specific content.
- The main `Content` textarea remains summary/fallback/search text.
- If `Content` is empty, derive it from the strongest slot on save.
- Each compatible slot supports:
  - `Insert reusable content`
  - `Promote to reusable content`
  - `Detach source` when the value was copied from a primitive.
- Insert reusable content copies the primitive value into the slot and stores `field_sources` metadata.
- Promote to reusable content copies the slot value into a new standalone primitive item and stores `derived_from` metadata.
- Promotion does not remove or replace the slot value in the composite.
- AI generation can use both standalone primitives and composite slot values.

Compatible insertion rules:

```text
headline slot -> title, headline, subheadline, tagline
paragraph slot -> paragraph, benefit, value_proposition
button_label slot -> cta_label
quote slot -> quote
stat slot -> stat
image_ref slot -> image_ref
question slot -> question
answer slot -> answer
```

### Content To Section To Site Contract

Swift Sites should use this pipeline:

```text
Primitive ContentItem
Composite ContentItem
        |
        v
Section compiler
        |
        v
SectionItem YAML
        |
        v
SitePage body YAML / composed page YAML
        |
        v
renderer.py
```

- `ContentItem` records are source assets.
- Primitive content items provide reusable single-purpose atoms, such as headlines, paragraphs, CTA labels, quotes, stats, and proof notes.
- Composite content items provide structured content groups, such as CTAs, FAQs, testimonials, offers, comparisons, and value propositions.
- A section is the first renderable unit.
- Each section stores or produces renderer-compatible YAML component code.
- Sites and pages are composed from ordered section YAML blocks.
- The renderer remains YAML-only and should not need to know whether text came from a primitive item, a composite slot, or AI enhancement.

Recommended V1 storage model:

- Keep `SectionItem.content_refs` as provenance and regeneration inputs.
- Add `SectionItem.yaml_content` as the current renderer-compatible YAML artifact for the section.
- Optionally add `SectionItem.generation_metadata` later for compiler version, source slot mapping, prompt metadata, or regeneration notes.
- Section preview should render from `yaml_content` when present.
- Regeneration should rebuild `yaml_content` from current `content_refs` and their `structured_payload` values.
- Page insertion should copy or reference the section YAML into `SitePage.body_yaml_content` / composed page YAML, depending on the chosen page-editing UX.

Renderer-compatible section YAML should remain a component list, for example:

```yaml
- name: layout-row
  properties:
    layout:
      tag: section
      wrap: wrap
  components:
    - name: layout-column
      components:
        - name: heading
          properties:
            text: Create campaigns once. Publish everywhere.
            level: 2
        - name: paragraph
          properties:
            text: Turn campaign truth into synchronized landing pages, emails, and ads.
        - name: button
          properties:
            text: Book a demo
            action:
              type: link
              href: "#demo"
```

The YAML artifact is the boundary between CMS content modeling and the site renderer.

### Content Type Guidance

- Extend `campaign/content_type_catalog.py` with:
  - `content_prompt`
  - `example_format`
  - `proof_sensitive`
  - `page_usable`
  - `channel_affinity`
  - `fields` or `slot_schema` for composite primitive slots
- Update the Content textarea when type changes:
  - Dynamic placeholder.
  - Short guidance panel below textarea.
  - Show the recommended format for the selected type.
- Replace "Use suggested format" with an `Enhance format` button.
- `Enhance format` behavior:
  - If content exists, AI rewrites/formats the typed content into the selected type's recommended structure.
  - If the selected type is composite, AI can parse rough content into slot fields.
  - If content is empty, show a validation message: "Add rough content first, then enhance the format."
  - Preserve the user's meaning and known facts.
  - Do not invent proof, testimonials, pricing, guarantees, customer names, or metrics.
- Example CTA guidance:
  ```text
  Headline: Ready to get started?
  Paragraph: Short supporting reason to act now.
  Button: Book a demo
  ```
- Example FAQ guidance:
  ```text
  Question: What happens after I submit the form?
  Answer: We review your details and contact you with next steps.
  ```

### AI Enhance For Content

- Add a dedicated endpoint:
  - `POST /api/chat/enhance-content`
  - Protected with the same AI request token and editor role checks.
- Request shape:
  ```json
  {
    "mode": "format",
    "channel": "landing_page",
    "content_type": "cta",
    "brand_id": "...",
    "product_id": "...",
    "title": "...",
    "content": "...",
    "tags": "launch, demo"
  }
  ```
- Response shape for primitive content:
  ```json
  {
    "content": "formatted content text"
  }
  ```
- Response shape for composite content:
  ```json
  {
    "content": "summary or fallback text",
    "structured_payload": {
      "headline": "Ready to get started?",
      "paragraph": "Short supporting reason to act now.",
      "button_label": "Book a demo"
    }
  }
  ```
- Prompt rules:
  - Format typed content into the selected content type's `example_format`.
  - For composite types, map the result into known slot fields.
  - Preserve truth and user intent.
  - Use brand/product context only for tone and terminology.
  - Never invent claims, proof, prices, testimonials, metrics, or permission notes.

### Section Generation From Content

Add a section generation path that turns primitives and composites into YAML-backed sections:

- Add `POST /api/sections/from-content`.
- Request shape:
  ```json
  {
    "section_type": "cta",
    "name": "Final CTA",
    "content_refs": ["..."],
    "brand_id": "..."
  }
  ```
- Response shape:
  ```json
  {
    "section": {
      "id": "...",
      "section_type": "cta",
      "content_refs": ["..."],
      "yaml_content": "- name: layout-row\n  ..."
    }
  }
  ```
- Add `POST /api/sections/<id>/regenerate-yaml` to rebuild the section YAML from its current content references.
- Add a deterministic compiler module, for example `campaign/content_to_section.py`, that maps:
  - primitive `headline` to heading components
  - primitive `paragraph`, `benefit`, and `value_proposition` to paragraph/card components
  - primitive `cta_label` or composite CTA `button_label` to button components
  - composite `cta` to heading + paragraph + button
  - composite `faq` to accordion items
  - composite `testimonial` to quote/testimonial components
  - composite `offer` to offer block components
- The compiler should prefer known `structured_payload` slots and fall back to `content`.
- Generated section YAML must pass the same validation used for page/shared-block YAML.

## Test Plan

- Backend:
  - Folder CRUD works and is org-scoped.
  - Content can be created with and without `folder_id`.
  - Invalid `folder_id` is rejected.
  - `GET /api/content?folder_id=...` filters correctly.
  - Search works globally when no folder is selected.
  - `/api/content/options` returns guidance metadata and composite slot schemas.
  - Composite content can be created without standalone primitive records.
  - Composite slot values are saved into `structured_payload`.
  - Primitive and composite content can generate a `SectionItem`.
  - Generated sections store renderer-compatible `yaml_content`.
  - Section preview renders from section YAML.
  - Regenerating a section updates `yaml_content` from current content refs.
  - CTA, FAQ, testimonial, offer, and value proposition composites compile from structured slots into section YAML.
  - Section YAML can be inserted into or composed into a site page body.
  - Inserting a primitive into a compatible composite slot copies the value.
  - Inserted primitive values store `field_sources` metadata.
  - Promoting a composite slot creates a standalone primitive item.
  - Promoted primitive items store `derived_from` metadata.
  - AI context building exposes composite slot values as derived atoms.
  - `/api/chat/enhance-content` formats existing content and rejects empty content.
- Frontend/static:
  - `node --check ssr_python/static/js/dashboard-v2.js`.
  - Content form field order matches the spec.
  - Channel change updates content type options.
  - Content type change updates textarea guidance and composite slot fields.
  - `Enhance format` updates the Content textarea for primitives.
  - `Enhance format` updates composite slot fields for composite types.
  - Compatible composite slots can insert reusable primitive content.
  - Composite slots can be promoted into standalone primitive content.
  - Proof fields appear only for proof-sensitive types.
  - Quality score remains optional.
- Existing focused tests:
  - `python -m pytest tests/test_brand.py tests/test_sections.py -q`.

## Assumptions

- Use flat optional folders for V1.
- Keep global search across all folders unless a folder filter is active.
- Keep Quality score optional and advanced.
- Composite-first creation is the default UX.
- Primitive-first workflows remain available but optional.
- V1 keeps the model simple with inline slots and copy-based reuse.
- No graph model or live-linked primitive references in V1.
- No backward compatibility constraints.
- Do not introduce nested folders, multi-folder membership, or structured per-type DB fields in this pass.
