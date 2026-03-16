# Page-Level YAML with Homepage-as-Theme-Source

## Context

The original plan to split site-level YAML (theme, header, footer) into a separate `Site.yaml_config` column creates a fundamental problem: YAML anchors (`&color-primary`) and aliases (`*color-primary`) are document-scoped. Storing them in separate documents breaks alias resolution, which is critical for LLM-generated YAML and the themes panel.

**Revised approach:** Keep each page as a self-contained YAML document (theme + page content including titlebar and footer components). The **homepage** serves as the theme source for new pages, but each page can customize its own theme independently.

**Note:** Site-level `header:` and `footer:` arrays have been removed. Titlebar and footer components are now regular components inside `page.components` — they appear in the component tree and are editable like any other component.

---

## Architecture

```
┌──────────────────────────────────────┐
│ Site                                 │
│  - name, slug, status                │
│  - settings (JSON Text)              │  ← SEO, branding, social (extensible)
│  - NO yaml_config                    │
└──────────┬───────────────────────────┘
           │ 1:N
┌──────────┴───────────────────────────┐
│ SitePage                             │
│  - slug, title, sort_order           │
│  - is_homepage (bool) ← already exists│
│  - yaml_content (complete document)  │  ← Full YAML: site wrapper + theme +
│                                      │     titlebar + footer + page content
└──────────────────────────────────────┘
```

### What each page's `yaml_content` looks like (complete, self-renderable)

```yaml
- name: site
  properties:
    theme:
      fonts:
        heading: &font-heading "'Lora', serif"
        content: &font-content "'Inter', sans-serif"
      colors:
        primary: &color-primary "#3d2c29"
        secondary: &color-secondary "#d63031"
        accent: &color-accent "#e17055"
        background: &color-background "#faf7f2"
  header:
    - name: titlebar
      properties:
        branding:
          title: My Bookstore
        appearance:
          background:
            color: *color-primary
  footer:
    - name: layout-row
      properties:
        appearance:
          background:
            color: *color-primary
      components:
        - name: paragraph
          properties:
            text: "© 2026 My Bookstore"
            typography:
              color: *color-background
  components:
    - name: page
      slug: home
      title: Home
      properties:
        appearance:
          background:
            color: *color-background
      components:
        - name: heading
          properties:
            text: Welcome
            typography:
              color: *color-primary
```

Anchors and aliases work perfectly — everything is in one document.

---

## Homepage as Theme Source

The `is_homepage` flag (already exists in DB) identifies which page's theme is the "standard" for the site.

### When creating a new page

1. Server reads the homepage's `yaml_content`
2. Extracts the theme, header, and footer from it
3. Creates the new page with an empty page body but copies the homepage's theme/header/footer
4. The new page inherits the standard look but can diverge immediately

```python
def create_page_from_homepage(site_id, slug, title):
    homepage = SitePage.query.filter_by(site_id=site_id, is_homepage=True).first()

    if homepage and homepage.yaml_content:
        # Parse homepage YAML, extract site wrapper (theme, header, footer)
        structure = yaml.safe_load(homepage.yaml_content)
        site_node = structure[0] if structure else {}

        theme = site_node.get('properties', {}).get('theme', DEFAULT_THEME)
        header = site_node.get('header', [])
        footer = site_node.get('footer', [])

        # Build new page YAML with homepage's theme/header/footer
        new_page_yaml = build_page_yaml(theme, header, footer, slug, title)
    else:
        new_page_yaml = generate_default_page_yaml(slug, title)

    page = SitePage(site_id=site_id, slug=slug, title=title, yaml_content=new_page_yaml)
    ...
```

### Per-page theme customization

Each page has its own full YAML document. Changing the theme on one page only affects that page. Pages start identical (cloned from homepage) and can diverge freely.

### "Sync theme from homepage" (optional future feature)

A button/action that reads the homepage's current theme and applies it to all other pages. This is a convenience feature, not required for the core architecture.

---

## Site-Level Properties (Settings as JSON)

The `Site` model stores identity + a JSON settings blob. NOT YAML — settings are simple key-value pairs consumed by Python (publishing) and JavaScript (settings panel), never by the rendering engine.

**Why JSON instead of individual columns:**
- Adding new setting categories doesn't require DB migrations
- Simple and flat — easy for LLMs to generate
- Native to both Python (`json.loads/dumps`) and JavaScript (`JSON.parse/stringify`)
- Matches existing pattern: `FormSubmission.data` already uses `db.Text` with `json.dumps()`

```python
class Site(db.Model):
    # Existing
    id, org_id, name, slug, status, current_version, ...

    # New: single JSON settings column
    settings = db.Column(db.Text, nullable=True)  # JSON blob

    def get_settings(self):
        """Parse settings JSON, merge with defaults for missing keys."""
        from guards import DEFAULT_SITE_SETTINGS
        stored = json.loads(self.settings) if self.settings else {}
        result = {}
        for category, defaults in DEFAULT_SITE_SETTINGS.items():
            result[category] = {**defaults, **(stored.get(category, {}))}
        return result

    def set_settings(self, settings_dict):
        self.settings = json.dumps(settings_dict)
```

**Settings schema (kept minimal for LLM-friendliness):**
```python
DEFAULT_SITE_SETTINGS = {
    "seo": {
        "titleTemplate": "{pageTitle} | {siteName}",
        "metaDescription": "",       # AI-generatable
        "ogImage": "",
        "ogTitle": "",               # AI-generatable
    },
    "branding": {
        "faviconUrl": "",
        "siteName": "",        # Display name, falls back to site.name
    },
    "social": {
        "twitterHandle": "",   # e.g. "@swiftsites"
        "facebookPage": "",
        "defaultShareImage": "",
    },
}
```

These are injected into the rendered HTML at publish/serve time, not part of the YAML document.

---

## Pros and Cons

### Pros

| Benefit | Why it matters |
|---------|---------------|
| **Anchors/aliases work perfectly** | Each page is a complete YAML document — `&color-primary` and `*color-primary` coexist naturally |
| **LLM generation is simple** | LLMs generate complete page YAML with aliases. No assembly logic, no special formats |
| **No assembly needed** | Each page renders independently — `yaml.safe_load(page.yaml_content)` → `render_yaml_structure()` |
| **No splitting needed** | Save the editor YAML directly to DB. No extraction, no string manipulation |
| **Per-page flexibility** | Each page can have a completely different theme, header, or footer |
| **Simple implementation** | Barely changes from current architecture. No new `assembler.py`, no path translation |
| **Backward compatible** | The current YAML format, renderer, editor, themes panel all work as-is |
| **Independent rendering** | Each page is self-contained. Preview, publish, export all work without fetching other data |

### Cons

| Drawback | Impact | Mitigation |
|----------|--------|------------|
| **Header/footer duplicated per page** | Storage: ~1-2 KB × N pages | Negligible for <100 pages. Acceptable trade-off for simplicity |
| **Header/footer changes don't propagate** | Changing nav links on homepage doesn't auto-update other pages | "Sync from homepage" action (future). Or accept per-page independence |
| **Theme changes don't propagate** | Changing theme on homepage doesn't update existing pages | "Sync theme" action (future). New pages inherit from homepage |
| **Data duplication** | Theme, header, footer repeated in every page's yaml_content | ~2-5 KB per page. For a 50-page site: ~250 KB total. Acceptable |
| **Consistency risk** | Pages can drift apart (different headers, themes) | This is actually a feature (per-page customization). "Sync" action for when consistency is desired |

---

## Comparison with Split-Storage Approach

| Aspect | Page-Level (this plan) | Split Storage (previous plan) |
|--------|----------------------|-------------------------------|
| **Alias support** | Works naturally | Broken (separate documents) or requires complex string assembly |
| **Implementation effort** | Minimal (current arch works) | Large (new assembler, path translation, 12+ files) |
| **LLM compatibility** | Perfect (generates complete YAML) | Complex (no aliases, or raw text fragments) |
| **Theme propagation** | Manual (sync action) | Automatic (single source) |
| **Header/footer sync** | Manual (sync action) | Automatic (single source) |
| **Storage efficiency** | Duplicated (~2-5 KB/page) | Optimized (single copy) |
| **Rendering** | Direct (no assembly) | Requires assembly step |
| **Editor complexity** | No change | Path translation between assembled/editor paths |
| **Risk of breaking** | Very low | High (many moving parts) |

**Verdict:** The page-level approach is dramatically simpler, preserves aliases, and the trade-off (header/footer duplication + manual sync) is acceptable for most sites. The "sync from homepage" feature can be added later as a convenience.

---

## Site Settings Enhancement — Full Implementation Plan

### Overview

Add a site settings system (SEO, branding, social) accessible from both the editor sidebar and dashboard. SEO fields are AI-generatable via a "Generate with AI" button and through the AI chat. Published pages get full HTML documents with proper `<head>` section.

---

### Phase 1: Backend — Model, Guards, API

**`ssr_python/models.py`** — Add `settings` column:
- `settings = db.Column(db.Text, nullable=True)` — JSON blob
- `get_settings()` — parse JSON, merge with `DEFAULT_SITE_SETTINGS` for missing keys
- `set_settings(dict)` — serialize to JSON

**`ssr_python/app.py`** — Auto-migration:
- `_run_migrations()` — `ALTER TABLE sites ADD COLUMN settings TEXT` if column missing
- Called from `create_app()` after `db.create_all()`

**`ssr_python/guards.py`** — Defaults + validation:
- `DEFAULT_SITE_SETTINGS` constant (seo, branding, social categories)
- `validate_site_settings(settings)` — checks known categories, known keys, string values

**`ssr_python/routes/site.py`** — Settings API:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sites/<id>/settings` | GET | Returns settings merged with defaults |
| `/api/sites/<id>/settings` | PUT | Validates and saves (partial merge supported) |

Also update `get_site()` to include `settings`, `list_sites()` to include `has_settings` flag.

---

### Phase 2: Published Pages — Full HTML Documents

**`ssr_python/routes/published.py`** — Wrap with document:
- `_build_html_document(body_html, site, page)` — wraps body in full HTML with `<head>`
- Title template interpolation at serve time: `{pageTitle} | {siteName}`
- Meta tags: description, og:title, og:type, og:description, og:image, twitter:card, favicon
- CSS/JS via `<link>`/`<script src>` tags pointing to static files
- Update `_serve_page()` to call `_build_html_document()`

---

### Phase 3: Export — SEO in Standalone HTML

**`ssr_python/static/js/main.js`** — Update `buildStandaloneHtml`:
- Add optional `seoMeta` parameter
- Inject description, og tags, twitter card, favicon into `<head>`
- In `exportCode` action: fetch site settings via API, pass to builder

---

### Phase 4: Editor UI — Settings Panel

**`ssr_python/templates/index.html`**:
- Settings icon button in sidebar nav (uses existing `#icon-settings` from sprite)
- `#settingsPanel` markup with panel-header, panel-content, panel-footer

**`ssr_python/static/js/settingsPanel.js`** (new file):
- `renderSettingsPanel()` — loads settings from API, renders grouped form:
  - **SEO section:** title template, meta description, og title, og image URL + "Generate with AI" button
  - **Branding section:** site display name, favicon URL (with preview thumbnail)
  - **Social section:** Twitter handle, Facebook page URL, default share image
- Save button in panel footer calls `PUT /api/sites/<id>/settings`

**`ssr_python/static/js/siteManager.js`** — Add exports:
- `getSiteSettings(siteId)` → `GET /api/sites/<id>/settings`
- `updateSiteSettings(siteId, settings)` → `PUT /api/sites/<id>/settings`

**`ssr_python/static/js/main.js`** — Import and expose `renderSettingsPanel` on window

**`ssr_python/static/js/events.js`** — Add settings panel toggle callback

**`ssr_python/static/css/style.css`** — Settings panel styles

---

### Phase 5: Dashboard UI — Settings Modal

**`ssr_python/static/js/dashboard.js`**:
- "Settings" button on site card actions (both dev and published sections)
- `showSettingsModal(siteId)` — modal overlay following existing create-site pattern
- Loads settings via `apiFetch`, renders form fields, Save/Cancel

---

### Phase 6: AI-Generated SEO

**6.1 "Generate with AI" button in Settings Panel:**
1. Button click → read current page YAML from editor
2. Send to `POST /api/chat` with focused prompt asking for `{metaDescription, ogTitle}` JSON
3. Parse JSON from LLM response
4. Pre-fill SEO fields in form (user reviews/edits before saving)

**6.2 AI Chat integration — new `settings` ACTION:**
- `ssr_python/llm_service.py` — Add `settings` to recognized ACTION types
- When user asks "generate SEO for my site": LLM returns `<!-- ACTION: settings -->` + JSON block
- `static/js/chat.js` — Handle `settings` action, call `updateSiteSettings()`, refresh panel

---

### Phase 7: Tests

**`ssr_python/tests/test_settings.py`** (new):
- `test_get_settings_returns_defaults`
- `test_update_settings_persists` (PUT + GET round-trip)
- `test_partial_update_preserves_other_categories`
- `test_rejects_unknown_category` (400)
- `test_rejects_unknown_key` (400)
- `test_settings_404_for_wrong_site` (IDOR check)

---

### Files Summary

| File | Action | Change |
|------|--------|--------|
| `models.py` | Modify | Add `settings` Text column + `get_settings()`/`set_settings()` |
| `app.py` | Modify | Add `_run_migrations()` for ALTER TABLE |
| `guards.py` | Modify | Add `DEFAULT_SITE_SETTINGS` + `validate_site_settings()` |
| `routes/site.py` | Modify | Add GET/PUT `/api/sites/<id>/settings` endpoints |
| `routes/published.py` | Modify | Add `_build_html_document()`, update `_serve_page()` |
| `static/js/settingsPanel.js` | **New** | Settings panel UI (form, load, save, AI generate) |
| `static/js/siteManager.js` | Modify | Add `getSiteSettings()`, `updateSiteSettings()` |
| `static/js/main.js` | Modify | Import settingsPanel, update `buildStandaloneHtml` for SEO |
| `static/js/events.js` | Modify | Add settings panel toggle callback |
| `static/js/dashboard.js` | Modify | Add Settings button + modal |
| `static/css/style.css` | Modify | Settings panel styles |
| `templates/index.html` | Modify | Add settings sidebar button + panel markup |
| `llm_service.py` | Modify | Add `settings` action type |
| `static/js/chat.js` | Modify | Handle `settings` action from AI |
| `tests/test_settings.py` | **New** | Settings API tests |

**Unchanged:** `renderer.py`, templates/components/*, `preview_bridge.js`, `componentTree.js`, `pathMapBuilder.js`, `yamlUtils.js`, `themesPanel.js`

### Implementation Order

1. Model + migration + guards (backend foundation)
2. API endpoints + tests (verify backend works)
3. Published page HTML wrapper (most impactful user-facing change)
4. SiteManager API methods (client-side foundation)
5. Settings panel JS + CSS + HTML (editor UI)
6. Dashboard settings modal (dashboard UI)
7. Export SEO integration
8. AI generation — settings panel button + chat `settings` action type

---

### What doesn't change (page-level architecture)

- `renderer.py` — already renders complete YAML documents
- `main.js` — already loads full YAML into editor
- `ssr_app.js` — already sends full YAML to `/render`
- `themesPanel.js` — already modifies theme anchors in the editor
- `componentTree.js` — already builds tree from full structure
- `yamlUtils.js` — already handles anchors/aliases
- `pageManager.js` — already works with site-wrapped structure
- `preview_bridge.js` — no change

---

## New Page Creation Flow

```
User clicks "Add Page"
    ↓
Client: POST /api/sites/<id>/pages  { title: "Contact", slug: "contact" }
    ↓
Server:
    1. Find homepage: SitePage.query.filter_by(site_id=id, is_homepage=True).first()
    2. Parse homepage yaml_content
    3. Extract: theme, header, footer
    4. Build new page YAML:
       - Same site wrapper (theme, header, footer)
       - New page component (slug, title, empty components)
    5. Save to SitePage(yaml_content=new_yaml)
    ↓
Client: Load new page → editor shows complete YAML with inherited theme
```

---

## Sync Theme from Homepage (Future Feature)

```
User clicks "Sync Theme" on a page
    ↓
Client: POST /api/sites/<id>/pages/<page_id>/sync-theme
    ↓
Server:
    1. Read homepage's yaml_content → extract theme, header, footer
    2. Read target page's yaml_content → parse as Document
    3. Replace theme, header, footer in target page's Document
    4. Preserve page's own components (content)
    5. Save updated yaml_content
    ↓
Client: Reload page YAML → editor/preview update with synced theme
```

Could also be a bulk action: "Sync all pages to homepage theme"

---

## Verification

### Page-Level Architecture
1. Create a new site → homepage created with default theme
2. Edit homepage theme → only that page changes
3. Add a new page → inherits homepage's theme/titlebar/footer automatically
4. Edit the new page's theme → page diverges from homepage (independent)
5. LLM generates YAML with `*color-primary` → works perfectly
6. Export/publish any page → renders independently, no assembly needed

### Site Settings
7. Start server → existing sites load without errors (migration runs automatically)
8. `GET /api/sites/<id>/settings` → returns defaults for existing sites
9. `PUT /api/sites/<id>/settings` with SEO data → persists and round-trips
10. Visit `/s/<slug>/<page>` → full HTML document with DOCTYPE, head, meta tags, CSS
11. View page source → correct title, description, og tags, favicon
12. Open editor → Settings panel shows form, saves correctly
13. Dashboard → Settings button opens modal, saves correctly
14. Export → downloaded HTML includes SEO meta tags
15. Settings panel "Generate with AI" → pre-fills SEO fields from page content
16. AI chat "generate SEO for my site" → applies settings via `settings` action
17. `python -m pytest ssr_python/tests/ -v` → all tests pass
