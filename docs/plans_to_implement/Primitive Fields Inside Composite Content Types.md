# Primitive Fields Inside Composite Content Types

## Summary

Use the standard CMS pattern: composites own their primitive fields inline. A `testimonial`, `cta`, `faq`, `offer`, or `value_proposition` should not point to separate saved `headline`, `paragraph`, or `button_label` rows in V1. Instead, those primitive pieces become typed fields inside the composite item's `structured_payload`.

This matches how major CMSs model reusable structured content: Contentful models entries from fields, Sanity uses object fields, Strapi uses components, and Prismic uses slices/custom type fields.

In Swift Sites, this content model is the source layer. Primitive and composite content items are converted into sections, and sections power sites. Each section is renderer-compatible YAML code; the existing renderer renders YAML, not CMS records directly.

Sources: [Contentful data model](https://www.contentful.com/developers/docs/concepts/data-model/), [Sanity object type](https://www.sanity.io/docs/studio/object-type), [Strapi components/content types](https://docs.strapi.io/cms/features/content-type-builder), [Prismic content modeling](https://prismic.io/docs/content-modeling).

## Key Design

- V1 will use **inline primitive slots** inside composite content.
- `structured_payload` becomes the source of truth for composite-specific fields.
- `content` remains the human-readable summary/body used for cards, search, previews, and fallback rendering.
- Standalone primitive content types stay available only for durable reusable atoms, such as reusable headlines, CTA labels, proof snippets, quotes, stats, and paragraphs.
- Do not build primitive-reference graphs in V1. References between content items can come later if reuse pressure is real.

Example storage:

```json
{
  "category": "cta",
  "title": "Book demo CTA",
  "content": "See how Swift Sites turns one campaign brief into landing pages, ads, and emails.",
  "structured_payload": {
    "headline": "Create campaigns once. Publish everywhere.",
    "paragraph": "Turn campaign truth into synchronized landing pages, emails, and ads.",
    "button_label": "Book a demo",
    "link": "#demo"
  }
}
```

## Composite-First Reuse Model

Composite-first is the default UX. A user should be able to create a CTA, FAQ, testimonial, offer, or value proposition directly without first creating separate primitive records. Primitive-first creation remains available for durable reusable atoms, such as approved taglines, reusable headlines, CTA labels, stats, quotes, or proof snippets.

V1 reuse works through inline slots and copy-based reuse:

- Composite primitive slots live inline in `structured_payload`.
- AI can reuse slot values as derived primitive atoms.
- Users can promote a composite slot into a standalone primitive item.
- Users can insert a standalone primitive into a compatible composite slot.
- Inserted primitive values are copied into the composite slot.
- V1 does not use live-linked primitive references.

Workflow:

```text
Create composite directly
  -> fill primitive slots inline
  -> AI can reuse those slots as derived atoms
  -> user can promote strong slots into standalone primitives
  -> user can insert standalone primitives into future composites
  -> composite/primitive content can compile into section YAML
  -> section YAML powers site pages
```

Inserted primitive source metadata should be stored inside the composite payload:

```json
{
  "structured_payload": {
    "headline": "Create campaigns once. Publish everywhere.",
    "paragraph": "Turn one campaign source into pages, emails, and ads.",
    "button_label": "Book a demo",
    "field_sources": {
      "headline": {
        "content_item_id": 18,
        "category": "headline",
        "mode": "copied"
      }
    }
  }
}
```

Promotion copies a slot into a new standalone primitive content item. It does not remove or replace the original composite slot value:

```json
{
  "category": "quote",
  "content": "Swift Sites cut our campaign setup time in half.",
  "source": "derived",
  "structured_payload": {
    "derived_from": {
      "content_item_id": 42,
      "field_path": "structured_payload.quote",
      "parent_category": "testimonial"
    }
  }
}
```

## Implementation Changes

- Extend `campaign/content_type_catalog.py` with a `fields` or `slot_schema` definition per composite type.
- Each slot should define:
  - `key`
  - `label`
  - `primitive_type`
  - `required`
  - `help_text`
  - optional `placeholder`
  - optional `max_length`
- Add slot schemas for the main composites:
  - `cta`: `headline`, `paragraph`, `button_label`, `link`
  - `faq`: `question`, `answer`
  - `testimonial`: `quote`, `author`, `author_role`, `company`, `rating`
  - `offer`: `headline`, `details`, `code`, `expiry_note`, `cta_label`
  - `value_proposition`: `headline`, `paragraph`, `supporting_points`
  - `benefit`: `headline`, `paragraph`
  - `feature`: `headline`, `paragraph`, `proof_note`
  - `objection`: `concern`, `response`
  - `comparison`: `subject`, `alternative`, `differentiator`, `proof_note`

## Section YAML Contract

The durable architecture should be:

```text
ContentItem.structured_payload
        |
        v
content-to-section compiler
        |
        v
SectionItem.yaml_content
        |
        v
SitePage.body_yaml_content / composed page YAML
        |
        v
renderer.py
```

Rules:

- `ContentItem` stores source content.
- `SectionItem` stores the renderable YAML artifact.
- `SectionItem.content_refs` remains useful as provenance and regeneration input.
- Section YAML must be a renderer-compatible component list.
- Page/site composition consumes section YAML.
- The renderer remains unaware of primitive/composite content types.

Recommended `SectionItem` additions:

```text
yaml_content TEXT
generation_metadata TEXT nullable
```

Example composite CTA:

```json
{
  "category": "cta",
  "content": "Turn campaign truth into synchronized landing pages, emails, and ads.",
  "structured_payload": {
    "headline": "Create campaigns once. Publish everywhere.",
    "paragraph": "Turn campaign truth into synchronized landing pages, emails, and ads.",
    "button_label": "Book a demo",
    "link": "#demo"
  }
}
```

compiles to section YAML:

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

This keeps source content editable and reusable while giving the site builder a concrete YAML artifact to compose and render.

## Content Form Behavior

- When the user selects a composite content type, show dynamic fields from the slot schema.
- Keep the main `Content` field, but treat it as summary/fallback text.
- If `Content` is empty, generate it from the strongest slot:
  - CTA: paragraph
  - FAQ: answer
  - Testimonial: quote
  - Offer: details
  - Value proposition: paragraph
- Replace "Use suggested format" with `Enhance format`.
- For composites, `Enhance format` should parse rough typed content into the dynamic slot fields.
- For primitives, `Enhance format` should improve the single text field only.

## API Behavior

- `/api/content/options` should return content type metadata including slot schemas.
- Create/update content should continue accepting `structured_payload`.
- Validation should require slot fields only when the selected composite marks them as required.
- Existing `content` search should continue working.
- Preview/render helpers should prefer `structured_payload` fields for known composites and fall back to `content`.
- Add or update section APIs so content can become renderable sections:
  - `POST /api/sections/from-content` creates a section from selected primitive/composite content.
  - `POST /api/sections/<id>/regenerate-yaml` rebuilds section YAML from current content refs.
  - Section preview renders `SectionItem.yaml_content` when present.
- Page/site APIs should compose ordered section YAML into page body YAML.

## Test Plan

- Catalog returns slot schemas for composite types.
- Creating a CTA stores headline, paragraph, button label, and link in `structured_payload`.
- Creating an FAQ stores question and answer in `structured_payload`.
- Creating composite content does not require standalone primitive records.
- Inserting a primitive into a compatible composite slot copies the value and stores `field_sources` metadata.
- Promoting a composite slot creates a standalone primitive and stores `derived_from` metadata.
- AI context building can expose composite slot values as derived primitive atoms.
- Content cards/previews display composite fields correctly.
- Search still finds composite content through `title` and `content`.
- Enhance format returns structured slot values for composite types.
- Primitive content types still work as simple reusable atoms.
- Primitive content can compile into section YAML.
- Composite CTA, FAQ, testimonial, offer, and value proposition records compile into section YAML using `structured_payload`.
- Generated section YAML renders through the existing renderer.
- Regenerating a section updates its YAML from current content refs.
- Site/page composition can consume generated section YAML.

## Assumptions

- V1 uses inline fields, not separate primitive child rows.
- Composite editor uses dynamic fields.
- Standalone primitive types are reserved for reusable campaign atoms.
- Do not require primitive-first creation.
- Do not auto-create primitive rows for every slot.
- Promotion copies, not moves.
- Insert reusable content copies, not live-links.
- Live linking is deferred to V2.
- No backward compatibility is required for old dev content.
- Section YAML is the render boundary between CMS content and sites.
