# Site Composition Model Plan

## 1. Purpose

Swift Sites currently stores each page as a full independent YAML document in `SitePage.yaml_content`. That makes common components such as navigation, announcement bars, footers, and shared campaign CTAs drift across pages.

The clean direction is a site composition model:

```text
site-level shared YAML + page-specific YAML -> composed renderer YAML -> render/publish
```

This keeps shared structure in one place while preserving the existing renderer contract.

## 2. Current Implementation

Current models:

- `Site` stores site metadata and JSON settings.
- `SitePage` stores a full renderable YAML document in `yaml_content`.
- `PublishedPage` stores rendered HTML per page.
- `SiteVersion` and `SiteVersionPage` snapshot page YAML at publish time.

Current page creation copies theme/titlebar from the homepage once via `generate_page_yaml_from_homepage()`. After that, pages are independent.

Problem:

- Header/footer/titlebar changes on one page do not propagate.
- Campaign-generated multi-page sites would duplicate common YAML.
- Homepage becomes an accidental source of truth.
- Version snapshots do not capture shared site-level structure separately.

## 3. Product Constraint

There are no production users yet, so backward compatibility for existing saved customer sites is not required.

We should choose the clean long-term model and migrate repository-owned assets:

- `example_templates/`
- test fixtures
- RAG references
- default page YAML
- generated examples

Do not keep long-lived compatibility shims only to preserve old local/dev YAML examples.

## 4. Target Model

Source data should be split into site-level and page-level parts.

```text
Site
  settings
  theme
  campaign metadata later

SiteSharedBlock
  header
  footer
  announcement_bar
  reusable campaign CTA later

SitePage
  slug
  title
  body YAML only

PageSharedBlockOverride
  inherit / hidden / custom per shared block

Composer
  produces renderer-compatible YAML
```

The renderer should still receive the current component shape:

```yaml
- name: site
  properties:
    theme: ...
  header:
    - name: titlebar
      properties: ...
  components:
    - name: page
      slug: home
      title: Home
      components:
        - name: heading
          properties:
            text: Page-specific content
  footer:
    - name: layout-row
      components: ...
```

## 5. Proposed Data Model

### Site

Keep `Site` as the owner of metadata, settings, and all site-scoped source objects.

Recommended additions:

```python
theme = db.Column(db.Text, nullable=True)          # JSON or YAML serialized theme
campaign_id = db.Column(db.String(36), nullable=True, index=True)
source_schema_version = db.Column(db.Integer, nullable=False, default=2)
```

Theme can initially remain inside shared/composed YAML if that is faster. Long term, site theme should be first-class because it applies to all pages and campaign outputs.

### SiteSharedBlock

Stores shared component arrays once per site.

```python
class SiteSharedBlock(db.Model):
    __tablename__ = "site_shared_blocks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey("sites.id"), nullable=False, index=True)
    key = db.Column(db.String(50), nullable=False)  # header, footer, announcement_bar
    label = db.Column(db.String(255), nullable=False)
    yaml_content = db.Column(db.Text, nullable=False, default="[]")
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("site_id", "key", name="uq_site_shared_block_key"),
    )
```

`yaml_content` is a YAML list of renderer components, not a full site document.

Example:

```yaml
- name: titlebar
  properties:
    branding:
      title: Swift Sites
    navigation:
      links:
        - label: Home
          href: /home
        - label: Pricing
          href: /pricing
```

### SitePage

Change page source from full site YAML to page body YAML.

Recommended eventual shape:

```python
class SitePage(db.Model):
    ...
    body_yaml_content = db.Column(db.Text, nullable=False, default="[]")
```

The page body should be a YAML list of components rendered inside the page:

```yaml
- name: layout-row
  properties:
    layout:
      tag: section
  components:
    - name: heading
      properties:
        text: Campaign headline
```

If we want to avoid carrying two columns, rename `yaml_content` to mean body YAML during the breaking migration. Since backward compatibility is not required, this is acceptable if tests and examples are updated in the same phase.

### PageSharedBlockOverride

Allows pages to hide or customize shared blocks.

```python
class PageSharedBlockOverride(db.Model):
    __tablename__ = "page_shared_block_overrides"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = db.Column(db.String(36), db.ForeignKey("site_pages.id"), nullable=False, index=True)
    block_key = db.Column(db.String(50), nullable=False)
    mode = db.Column(db.String(20), nullable=False, default="inherit")
    custom_yaml_content = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("page_id", "block_key", name="uq_page_shared_block_override"),
    )
```

Allowed modes:

```text
inherit -> use SiteSharedBlock
hidden  -> omit the shared block on this page
custom  -> use custom_yaml_content for this page
```

## 6. Versioning Model

Current versioning snapshots pages only. Shared blocks must also be snapshotted.

Add:

```python
class SiteVersionSharedBlock(db.Model):
    __tablename__ = "site_version_shared_blocks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = db.Column(db.String(36), db.ForeignKey("site_versions.id"), nullable=False, index=True)
    key = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    yaml_content = db.Column(db.Text, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
```

Also update `SiteVersionPage` to snapshot page body YAML under the new meaning of page source.

Publish version snapshot should capture:

- site metadata relevant to rendering
- site settings
- theme
- shared blocks
- page body YAML
- page shared-block overrides

## 7. Composer Service

Add:

```text
ssr_python/site_composer.py
```

Core API:

```python
def compose_page_yaml(site, page):
    """Return renderer-compatible YAML structure for one page."""
```

Responsibilities:

1. Load site theme.
2. Load enabled shared blocks ordered by `sort_order`.
3. Apply page overrides.
4. Parse page body YAML.
5. Build one renderer-compatible `site` wrapper with one `page`.
6. Return a Python list suitable for `render_yaml_structure()`.

Output shape:

```python
[
    {
        "name": "site",
        "properties": {"theme": theme},
        "header": header_components,
        "components": [
            {
                "name": "page",
                "slug": page.slug,
                "title": page.title,
                "properties": page_properties,
                "components": body_components,
            }
        ],
        "footer": footer_components,
    }
]
```

Do not put composition logic inside `renderer.py`. The renderer should stay responsible for rendering a fully composed structure.

## 8. Render And Publish Flow

### Editor Preview

Current:

```text
editor YAML -> POST /render -> render_yaml_structure()
```

Target:

```text
page body editor YAML
  -> compose with site shared blocks
  -> POST /render or local compose endpoint
  -> render_yaml_structure()
```

For first implementation, preview can call a backend endpoint:

```text
POST /api/sites/<site_id>/pages/<page_id>/render
```

That endpoint composes the saved/draft page body with shared blocks and returns rendered HTML.

### Publish

Current:

```python
structure = yaml.safe_load(sp.yaml_content)
html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
```

Target:

```python
structure = compose_page_yaml(site, sp)
html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
```

Published output remains `PublishedPage.rendered_html`.

## 9. API Surface

Add shared block endpoints:

```text
GET  /api/sites/<site_id>/shared-blocks
PUT  /api/sites/<site_id>/shared-blocks/<key>
POST /api/sites/<site_id>/shared-blocks
DELETE /api/sites/<site_id>/shared-blocks/<key>
```

Add page override endpoints:

```text
GET /api/sites/<site_id>/pages/<page_id>/shared-block-overrides
PUT /api/sites/<site_id>/pages/<page_id>/shared-block-overrides/<key>
```

Optional compose/debug endpoint:

```text
GET /api/sites/<site_id>/pages/<page_id>/composed-yaml
```

This is useful for debugging and tests.

## 10. Campaign Compiler Fit

The campaign compiler should produce site-level and page-level sources separately.

Campaign output should map to:

```text
campaign.site.theme          -> Site.theme
campaign.shared.header       -> SiteSharedBlock(key="header")
campaign.shared.footer       -> SiteSharedBlock(key="footer")
campaign.pages[].body        -> SitePage.body_yaml_content
campaign.pages[].overrides   -> PageSharedBlockOverride
```

The campaign compiler should not generate full duplicated page YAML for every page.

This makes multi-page campaigns clean:

```text
landing page
thank-you page
pricing page
lead magnet page
```

All can share campaign navigation, footer, theme, trust strip, and final CTA without duplication.

## 11. Example Template Migration

Because backward compatibility is not required, update examples instead of supporting old source shapes forever.

Convert templates from full page documents to source bundles where useful:

```text
example_templates/
  campaign_source/
    saas_lead_gen/
      site.yaml
      shared_blocks/
        header.yaml
        footer.yaml
      pages/
        home.yaml
        pricing.yaml
```

For RAG, keep compiled renderer-compatible examples too if needed:

```text
example_templates_compiled/
  saas_lead_gen_home.yaml
```

Recommended rule:

- Source examples teach the campaign/site composer.
- Compiled examples teach the renderer and component syntax.

## 12. Implementation Phases

### Phase 1 - Renderer Support For Site Header/Footer

Tasks:

- Add `site.header` and `site.footer` rendering in the site macro.
- Add default empty arrays for site header/footer.
- Ensure path map and component tree understand `header` and `footer`.
- Add renderer tests.

### Phase 2 - Data Model

Tasks:

- Add `SiteSharedBlock`.
- Add `PageSharedBlockOverride`.
- Add `SiteVersionSharedBlock`.
- Decide whether `SitePage.yaml_content` is renamed semantically to body YAML or replaced by `body_yaml_content`.
- Update migrations/bootstrap logic.

### Phase 3 - Composer

Tasks:

- Add `site_composer.py`.
- Compose one page with shared blocks.
- Add tests for inherit, hidden, and custom override modes.
- Add debug endpoint for composed YAML.

### Phase 4 - Publish And Preview Integration

Tasks:

- Update publish route to use composer.
- Add page render endpoint for composed preview.
- Update editor save/load assumptions from full YAML to body YAML.
- Ensure export/fullscreen use composed HTML.

### Phase 5 - Example And RAG Migration

Tasks:

- Convert `example_templates/`.
- Update `COMPONENT_SYNTAX_REFERENCE.md`.
- Update RAG chunking if source examples are split into shared blocks/pages.
- Regenerate or adapt tests that validate all templates.

### Phase 6 - Campaign Compiler Integration

Tasks:

- Make campaign compiler emit `Site`, `SiteSharedBlock`, and `SitePage` source records.
- Compile campaign pages through `site_composer.py`.
- Add campaign tests for multi-page shared blocks.

## 13. Acceptance Criteria

- Header/footer YAML is stored once per site.
- A page can inherit, hide, or customize a shared block.
- Publishing composes each page before rendering.
- Version snapshots include shared blocks.
- Changing a shared header updates all inheriting pages on next preview/publish.
- No page stores duplicated titlebar/footer YAML unless it explicitly overrides.
- Campaign-generated sites use shared blocks instead of duplicated page YAML.
- Repository examples and tests are migrated to the new source model.

## 14. Non-Goals

- Do not implement analytics in this phase.
- Do not add channel outputs before the composer is stable.
- Do not put campaign fields into renderer component YAML.
- Do not keep old example formats around as first-class formats.

