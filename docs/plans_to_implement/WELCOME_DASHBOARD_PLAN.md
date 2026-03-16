# Welcome Dashboard — Separate Page with Sites & Submissions

## Context

The app needs a **separate dashboard/welcome page** at `GET /` — the first screen users see when they open the app. The current editor moves to `GET /editor/<site_id>`. The dashboard has its own sidebar with two views: **Sites** (list/create/delete sites with version history) and **Submissions** (view/manage form data with CSV export). Clicking Edit or Create on the dashboard navigates to the editor.

**Goal:** Separate dashboard page with Sites (two sections: In Development / Published, version rollback) and Submissions views. Version history via `SiteVersion` + `SiteVersionPage` tables. Access role-gated.

---

## Architecture: Separate Dashboard Page

```
┌─ Dashboard (GET /) ──────────────────────────────────────────┐
│ [Swift Sites Logo]                              Default Admin │
├──────────┬───────────────────────────────────────────────────┤
│          │                                                    │
│ 🌐 Sites │  IN DEVELOPMENT              [+ Create New Site]  │
│          │  ┌─────────────┐ ┌─────────────┐                  │
│ 📋 Subs  │  │ My Bakery   │ │ Portfolio   │                  │
│          │  │ Published ● │ │ Draft ○     │                  │
│          │  │ 3 pages     │ │ 1 page      │                  │
│          │  │ [Edit][Ver] │ │ [Edit]      │                  │
│          │  └─────────────┘ └─────────────┘                  │
│          │                                                    │
│          │  PUBLISHED                                         │
│          │  ┌─────────────┐ ┌─────────────┐                  │
│          │  │ My Bakery   │ │ Blog        │                  │
│          │  │ v3 · Feb 25 │ │ v2 · Feb 20 │                  │
│          │  │ [View Live] │ │ [View Live] │                  │
│          │  └─────────────┘ └─────────────┘                  │
└──────────┴───────────────────────────────────────────────────┘

Dashboard sidebar: 200px wide with text labels + icons
Main area: Card grid for Sites view, table for Submissions view
Edit button → window.location.href = '/editor/<site_id>'
```

---

## Route Changes

| Before | After |
|--------|-------|
| `GET /` → editor (index.html) | `GET /` → dashboard (dashboard.html) |
| — | `GET /editor/<site_id>` → editor (index.html with site loaded) |
| `GET /preview-frame` (unchanged) | `GET /preview-frame` (unchanged) |

---

## Section Logic (Timestamp-Based)

- **Draft-only** sites (never published) → **In Development** only
- **Published** sites where `max(SitePage.updated_at) > site.published_at` → **Both sections** (being actively edited)
- **Published** sites where `max(SitePage.updated_at) <= site.published_at` → **Published** only (no edits since publish)

---

## Role-Based Access

| Feature | viewer | editor | admin/owner |
|---------|--------|--------|-------------|
| Sites: view list | yes | yes | yes |
| Sites: edit/create | no | yes | yes |
| Sites: delete | no | no | yes |
| Sites: publish/unpublish | no | yes | yes |
| Sites: rollback version | no | yes | yes |
| Submissions: view | no | yes | yes |
| Submissions: mark read/spam | no | yes | yes |
| Submissions: delete | no | no | yes |

Pre-auth stub defaults to `'owner'` (full access).

---

## Data Model Changes

### New Table: `SiteVersion` — Snapshot at each publish

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| site_id | FK → sites.id | Indexed |
| version_number | Integer | Auto-increment per site |
| label | String(255) nullable | User-defined: "Initial launch" |
| published_at | DateTime | When published |
| published_by | FK → users.id nullable | Who published |

Relationship: `pages` → SiteVersionPage (cascade delete)
Constraint: UniqueConstraint(site_id, version_number)

### New Table: `SiteVersionPage` — Per-page YAML snapshot

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| version_id | FK → site_versions.id | Indexed |
| slug | String(255) | Page slug |
| title | String(255) | Page title |
| yaml_content | Text | YAML at publish time |
| sort_order | Integer | Page order |
| is_homepage | Boolean | Homepage flag |

### Modified: `Site` — Add version tracking

- `current_version` = Integer nullable (version_number of live version)
- `versions` = relationship → SiteVersion (cascade delete, order by desc)

---

## New API Endpoints

### Version Endpoints (in `routes/site.py`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/sites/<id>/versions` | List version history (newest first) |
| `POST` | `/api/sites/<id>/versions/<vid>/rollback` | Restore draft YAML from version |
| `PATCH` | `/api/sites/<id>/versions/<vid>` | Update version label |

**Rollback flow:** Delete current SitePages → copy SiteVersionPages as new SitePages → update `site.updated_at`

### Submission Endpoints (new `routes/submissions.py` blueprint)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/submissions` | List org submissions (filter: site_id, all/unread/spam, paginated) |
| `PATCH` | `/api/submissions/<id>` | Update is_read / is_spam |
| `DELETE` | `/api/submissions/<id>` | Delete submission |
| `GET` | `/api/submissions/export` | CSV download |

### Modified Endpoints

- `GET /api/sites` — add `sections` array, `version_count` to each site
- `POST /api/sites/<id>/publish` — also creates SiteVersion + SiteVersionPage rows, sets `current_version`

---

## Implementation Steps (10 Steps)

### Step 1: Data model — `models.py`
- Add `SiteVersion` and `SiteVersionPage` models
- Add `current_version` column + `versions` relationship to `Site`
- Delete SQLite DB → `db.create_all()` recreates tables

### Step 2: Guards + helpers — `guards.py`
- `site_has_unpublished_changes(site)` — `max(SitePage.updated_at) > site.published_at`
- `get_version_or_404(site_id, version_id)` guard

### Step 3: Version endpoints — `routes/site.py`
- Modify `list_sites()`: add `sections`, `version_count`
- Modify `publish_site()`: create version snapshot, set `current_version`
- Add 3 version endpoints (list, rollback, label)

### Step 4: Submission endpoints — `routes/submissions.py` (new)
- New `submissions_bp` blueprint
- 4 endpoints: list, update, delete, CSV export
- Register in `routes/__init__.py`

### Step 5: Route changes — `routes/views.py`
- `GET /` → `dashboard.html`
- `GET /editor/<site_id>` → `index.html` with `site_id`
- Add `before_request` for org stub

### Step 6: Dashboard HTML — `templates/dashboard.html` (new)
- Header (logo + user info)
- Sidebar (200px, Sites + Submissions nav buttons)
- Main content area
- Loads `style.css` + `dashboard.css` + `dashboard.js`

### Step 7: Dashboard JS — `static/js/dashboard.js` (new)
- Standalone ES module (no editor imports)
- Sites view: fetch, group into sections, render card grid
- Site actions: Edit → `/editor/<id>`, Delete, Publish, Versions toggle
- Version history: inline list with rollback + confirmation
- Create site: modal → `POST /api/sites` → navigate to editor
- Submissions view: filter tabs, expandable rows, CSV export

### Step 8: Dashboard CSS — `static/css/dashboard.css` (new)
- Dashboard layout (200px sidebar + flex content)
- Nav buttons, site card grid, status badges
- Version history, submissions table, filter tabs
- Create site modal, empty states
- Uses existing CSS variables from `style.css`

### Step 9: Editor modifications — `index.html` + `main.js`
- `index.html`: `window.SITE_ID`, `window.USER_ROLE`, **"Back to Dashboard" chevron-left link** in header brand (navigates to `/`)
- `main.js`: Load site from API when `SITE_ID` set, skip sessionStorage
- `style.css`: `.back-to-dashboard` styling (28px icon button with hover state)

### Step 10: Tests — `tests/test_dashboard.py` (new)
- Dashboard route, editor route
- Version creation, rollback, label update
- Submission list, filter, delete, CSV

---

## Files Summary

| Action | File | Changes |
|--------|------|---------|
| **Modify** | `ssr_python/models.py` | +SiteVersion, +SiteVersionPage, +current_version on Site |
| **Modify** | `ssr_python/guards.py` | +site_has_unpublished_changes(), +get_version_or_404() |
| **Modify** | `ssr_python/routes/site.py` | Modify list/publish, +version endpoints |
| **Create** | `ssr_python/routes/submissions.py` | Submission list, update, delete, CSV |
| **Modify** | `ssr_python/routes/__init__.py` | Register submissions_bp |
| **Modify** | `ssr_python/routes/views.py` | Dashboard at /, editor at /editor/<id> |
| **Create** | `ssr_python/templates/dashboard.html` | Dashboard page template |
| **Create** | `ssr_python/static/js/dashboard.js` | Dashboard client-side logic |
| **Create** | `ssr_python/static/css/dashboard.css` | Dashboard styles |
| **Modify** | `ssr_python/templates/index.html` | +window.SITE_ID, +back-to-dashboard link |
| **Modify** | `ssr_python/static/js/main.js` | Auto-load site from SITE_ID |
| **Create** | `ssr_python/tests/test_dashboard.py` | Dashboard + version + submission tests |

Database: delete `instance/swift_sites.db` → `db.create_all()` rebuilds.

---

## Verification

1. `python -m pytest ssr_python/tests/ -v` — all tests pass
2. Delete DB, restart → `GET /` shows dashboard with empty state
3. Create site → navigates to `/editor/<id>`, editor loads site
4. Back to Dashboard → site in "In Development"
5. Publish → site in "Published" only
6. Edit page → site in BOTH sections
7. Publish again → v2 created, back to "Published" only
8. Version history → v1 + v2 shown, rollback v1 → YAML restored
9. Submissions view → form data, filters, CSV export
