# Plan: Multipage Site Support with PostgreSQL

## Context

The app currently supports a single page — one YAML document in the editor, one render in the preview iframe, one sessionStorage key. This plan adds multipage support where an entire site has **one UUID** and pages are **numbered 1, 2, 3...**. All site and page data is persisted in **PostgreSQL**, with a REST API for CRUD operations. The client calls the API to save/load pages and shows a **save confirmation dialog** before switching pages.

---

## Data Model

### PostgreSQL Schema

```sql
-- Sites table
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL DEFAULT 'Untitled Site',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pages table
CREATE TABLE pages (
    id SERIAL PRIMARY KEY,
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'New Page',
    yaml_content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(site_id, page_number)
);

CREATE INDEX idx_pages_site_id ON pages(site_id);
```

### API JSON Shapes

**Site object:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "My Website",
    "created_at": "2026-02-16T10:30:00Z",
    "updated_at": "2026-02-16T12:45:00Z",
    "pages": [
        { "page_number": 1, "title": "Home" },
        { "page_number": 2, "title": "About" },
        { "page_number": 3, "title": "Contact" }
    ]
}
```

**Page object:**
```json
{
    "page_number": 1,
    "title": "Home",
    "yaml_content": "- name: page\n  properties:\n    ...",
    "updated_at": "2026-02-16T12:45:00Z"
}
```

### Per-Page YAML (unchanged format)

Each page is the existing single-page format — no structural changes:

```yaml
- name: page
  properties:
    theme:
      fonts:
        headingMain: &font-heading-main "'Inter', sans-serif"
      colors:
        primary: &color-primary '#1e293b'
    appearance:
      background:
        color: *color-background
  components:
    - name: titlebar
      ...
    - name: heading
      ...
```

---

## Part 1: Python Dependencies

**File: `ssr_python/requirements.txt`** — Add:

```
psycopg2-binary>=2.9.0,<3.0
```

Uses `psycopg2-binary` (no build tools needed) for PostgreSQL connectivity. No ORM — direct SQL with parameterized queries for simplicity.

---

## Part 2: Database Module — `db.py`

**File: `ssr_python/db.py`** (new file)

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    """Get a PostgreSQL connection using env vars."""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('DB_NAME', 'swift_sites'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', ''),
    )

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sites (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL DEFAULT 'Untitled Site',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS pages (
                    id SERIAL PRIMARY KEY,
                    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
                    page_number INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL DEFAULT 'New Page',
                    yaml_content TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(site_id, page_number)
                );
                CREATE INDEX IF NOT EXISTS idx_pages_site_id ON pages(site_id);
            """)
        conn.commit()
    finally:
        conn.close()

# ── Site CRUD ──

def create_site(name='Untitled Site'):
    """Create a new site with page 1. Returns site dict."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO sites (name) VALUES (%s) RETURNING id, name, created_at, updated_at",
                (name,)
            )
            site = dict(cur.fetchone())
            # Create default page 1
            cur.execute(
                "INSERT INTO pages (site_id, page_number, title, yaml_content) VALUES (%s, 1, 'Home', '')",
                (str(site['id']),)
            )
        conn.commit()
        site['pages'] = [{'page_number': 1, 'title': 'Home'}]
        return site
    finally:
        conn.close()

def get_site(site_id):
    """Get site with page list (without YAML content). Returns dict or None."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, created_at, updated_at FROM sites WHERE id = %s", (str(site_id),))
            site = cur.fetchone()
            if not site:
                return None
            site = dict(site)
            cur.execute(
                "SELECT page_number, title FROM pages WHERE site_id = %s ORDER BY page_number",
                (str(site_id),)
            )
            site['pages'] = [dict(row) for row in cur.fetchall()]
        return site
    finally:
        conn.close()

def list_sites():
    """List all sites (id, name, page count, updated_at)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.id, s.name, s.updated_at, COUNT(p.id) as page_count
                FROM sites s LEFT JOIN pages p ON s.id = p.site_id
                GROUP BY s.id ORDER BY s.updated_at DESC
            """)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def delete_site(site_id):
    """Delete a site and all its pages (CASCADE)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sites WHERE id = %s", (str(site_id),))
        conn.commit()
    finally:
        conn.close()

def rename_site(site_id, new_name):
    """Rename a site."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sites SET name = %s, updated_at = NOW() WHERE id = %s",
                (new_name, str(site_id))
            )
        conn.commit()
    finally:
        conn.close()

# ── Page CRUD ──

def get_page(site_id, page_number):
    """Get a single page with YAML content. Returns dict or None."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT page_number, title, yaml_content, updated_at FROM pages WHERE site_id = %s AND page_number = %s",
                (str(site_id), page_number)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def save_page(site_id, page_number, yaml_content, title=None):
    """Save (upsert) a page's YAML content. Optionally update title."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if title is not None:
                cur.execute("""
                    INSERT INTO pages (site_id, page_number, title, yaml_content)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (site_id, page_number)
                    DO UPDATE SET yaml_content = EXCLUDED.yaml_content, title = EXCLUDED.title, updated_at = NOW()
                """, (str(site_id), page_number, title, yaml_content))
            else:
                cur.execute("""
                    INSERT INTO pages (site_id, page_number, yaml_content)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (site_id, page_number)
                    DO UPDATE SET yaml_content = EXCLUDED.yaml_content, updated_at = NOW()
                """, (str(site_id), page_number, yaml_content))
            # Also touch the site's updated_at
            cur.execute("UPDATE sites SET updated_at = NOW() WHERE id = %s", (str(site_id),))
        conn.commit()
    finally:
        conn.close()

def add_page(site_id, title='New Page'):
    """Add a new page with the next sequential number. Returns new page_number."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(page_number), 0) + 1 FROM pages WHERE site_id = %s",
                (str(site_id),)
            )
            new_number = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO pages (site_id, page_number, title, yaml_content) VALUES (%s, %s, %s, %s)",
                (str(site_id), new_number, title, '')
            )
            cur.execute("UPDATE sites SET updated_at = NOW() WHERE id = %s", (str(site_id),))
        conn.commit()
        return new_number
    finally:
        conn.close()

def delete_page(site_id, page_number):
    """Delete a page. Returns False if it's the last page."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pages WHERE site_id = %s", (str(site_id),))
            count = cur.fetchone()[0]
            if count <= 1:
                return False
            cur.execute(
                "DELETE FROM pages WHERE site_id = %s AND page_number = %s",
                (str(site_id), page_number)
            )
            cur.execute("UPDATE sites SET updated_at = NOW() WHERE id = %s", (str(site_id),))
        conn.commit()
        return True
    finally:
        conn.close()

def rename_page(site_id, page_number, new_title):
    """Rename a page."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE pages SET title = %s, updated_at = NOW() WHERE site_id = %s AND page_number = %s",
                (new_title, str(site_id), page_number)
            )
        conn.commit()
    finally:
        conn.close()
```

---

## Part 3: Flask API Routes — `routes/sites.py`

**File: `ssr_python/routes/sites.py`** (new file)

```python
from flask import Blueprint, request, jsonify
import traceback
from flask import current_app

sites_bp = Blueprint('sites', __name__)

# ── Site endpoints ──

@sites_bp.route('/api/sites', methods=['GET'])
def list_all_sites():
    """List all sites."""
    try:
        from db import list_sites
        sites = list_sites()
        return jsonify(sites)
    except Exception as e:
        current_app.logger.error(f"List sites error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to load sites.'}), 500

@sites_bp.route('/api/sites', methods=['POST'])
def create_new_site():
    """Create a new site with page 1."""
    try:
        from db import create_site
        data = request.get_json(silent=True) or {}
        name = data.get('name', 'Untitled Site')
        site = create_site(name)
        return jsonify(site), 201
    except Exception as e:
        current_app.logger.error(f"Create site error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create site.'}), 500

@sites_bp.route('/api/sites/<site_id>', methods=['GET'])
def get_site_detail(site_id):
    """Get site with page list."""
    try:
        from db import get_site
        site = get_site(site_id)
        if not site:
            return jsonify({'error': 'Site not found.'}), 404
        return jsonify(site)
    except Exception as e:
        current_app.logger.error(f"Get site error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to load site.'}), 500

@sites_bp.route('/api/sites/<site_id>', methods=['DELETE'])
def delete_site_endpoint(site_id):
    """Delete a site and all pages."""
    try:
        from db import delete_site
        delete_site(site_id)
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error(f"Delete site error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to delete site.'}), 500

@sites_bp.route('/api/sites/<site_id>/rename', methods=['PUT'])
def rename_site_endpoint(site_id):
    """Rename a site."""
    try:
        from db import rename_site
        data = request.get_json(silent=True) or {}
        rename_site(site_id, data.get('name', 'Untitled Site'))
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error(f"Rename site error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to rename site.'}), 500

# ── Page endpoints ──

@sites_bp.route('/api/sites/<site_id>/pages/<int:page_number>', methods=['GET'])
def get_page_endpoint(site_id, page_number):
    """Get a page's YAML content."""
    try:
        from db import get_page
        page = get_page(site_id, page_number)
        if not page:
            return jsonify({'error': 'Page not found.'}), 404
        return jsonify(page)
    except Exception as e:
        current_app.logger.error(f"Get page error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to load page.'}), 500

@sites_bp.route('/api/sites/<site_id>/pages/<int:page_number>', methods=['PUT'])
def save_page_endpoint(site_id, page_number):
    """Save a page's YAML content (and optionally title)."""
    try:
        from db import save_page
        data = request.get_json(silent=True) or {}
        yaml_content = data.get('yaml_content', '')
        title = data.get('title')  # None if not provided
        save_page(site_id, page_number, yaml_content, title)
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error(f"Save page error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to save page.'}), 500

@sites_bp.route('/api/sites/<site_id>/pages', methods=['POST'])
def add_page_endpoint(site_id):
    """Add a new page to the site."""
    try:
        from db import add_page
        data = request.get_json(silent=True) or {}
        title = data.get('title', 'New Page')
        new_number = add_page(site_id, title)
        return jsonify({'page_number': new_number, 'title': title}), 201
    except Exception as e:
        current_app.logger.error(f"Add page error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to add page.'}), 500

@sites_bp.route('/api/sites/<site_id>/pages/<int:page_number>', methods=['DELETE'])
def delete_page_endpoint(site_id, page_number):
    """Delete a page."""
    try:
        from db import delete_page
        ok = delete_page(site_id, page_number)
        if not ok:
            return jsonify({'error': 'Cannot delete the last page.'}), 400
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error(f"Delete page error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to delete page.'}), 500

@sites_bp.route('/api/sites/<site_id>/pages/<int:page_number>/rename', methods=['PUT'])
def rename_page_endpoint(site_id, page_number):
    """Rename a page."""
    try:
        from db import rename_page
        data = request.get_json(silent=True) or {}
        rename_page(site_id, page_number, data.get('title', 'Untitled'))
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error(f"Rename page error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to rename page.'}), 500
```

### Register blueprint

**File: `ssr_python/routes/__init__.py`** — Add:

```python
from routes.sites import sites_bp

def register_blueprints(app):
    # ... existing blueprints ...
    app.register_blueprint(sites_bp)
```

---

## Part 4: Initialize DB on App Startup

**File: `ssr_python/app.py`** — In `create_app()`, after `load_shared_data(app)`:

```python
# Initialize database tables
from db import init_db
try:
    init_db()
    app.logger.info("Database tables initialized")
except Exception as e:
    app.logger.warning(f"Database not available: {e}")
```

### Environment variables

**File: `ssr_python/.env.example`** — Add:

```
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=swift_sites
DB_USER=postgres
DB_PASSWORD=
```

### Config update

**File: `ssr_python/config.py`** — Add DB config:

```python
class Config:
    # ... existing ...
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'swift_sites')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
```

---

## Part 5: Client-Side Site Service — `siteService.js`

**File: `ssr_python/static/js/siteService.js`** (new file)

Thin async wrapper around the REST API:

```javascript
/**
 * Site & Page API client
 * All methods return Promises. Errors throw.
 */
export const siteService = {
    // ── Sites ──

    async listSites() {
        const res = await fetch('/api/sites');
        if (!res.ok) throw new Error('Failed to list sites');
        return res.json();
    },

    async createSite(name = 'Untitled Site') {
        const res = await fetch('/api/sites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!res.ok) throw new Error('Failed to create site');
        return res.json();
    },

    async getSite(siteId) {
        const res = await fetch(`/api/sites/${siteId}`);
        if (!res.ok) throw new Error('Failed to load site');
        return res.json();
    },

    async deleteSite(siteId) {
        const res = await fetch(`/api/sites/${siteId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete site');
        return res.json();
    },

    async renameSite(siteId, name) {
        const res = await fetch(`/api/sites/${siteId}/rename`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!res.ok) throw new Error('Failed to rename site');
        return res.json();
    },

    // ── Pages ──

    async getPage(siteId, pageNumber) {
        const res = await fetch(`/api/sites/${siteId}/pages/${pageNumber}`);
        if (!res.ok) throw new Error('Failed to load page');
        return res.json();
    },

    async savePage(siteId, pageNumber, yamlContent, title = undefined) {
        const body = { yaml_content: yamlContent };
        if (title !== undefined) body.title = title;
        const res = await fetch(`/api/sites/${siteId}/pages/${pageNumber}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error('Failed to save page');
        return res.json();
    },

    async addPage(siteId, title = 'New Page') {
        const res = await fetch(`/api/sites/${siteId}/pages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        if (!res.ok) throw new Error('Failed to add page');
        return res.json();
    },

    async deletePage(siteId, pageNumber) {
        const res = await fetch(`/api/sites/${siteId}/pages/${pageNumber}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete page');
        return res.json();
    },

    async renamePage(siteId, pageNumber, title) {
        const res = await fetch(`/api/sites/${siteId}/pages/${pageNumber}/rename`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        if (!res.ok) throw new Error('Failed to rename page');
        return res.json();
    },
};
```

---

## Part 6: Update `yamlStorage.js` — Hybrid Storage (API + sessionStorage cache)

**File: `ssr_python/static/js/yamlStorage.js`**

sessionStorage is now used as a **write-through cache** for the active page's YAML (for fast debounced saves), with periodic flushes to PostgreSQL. The site manifest comes from the API.

```javascript
import { siteService } from './siteService.js';

const SESSION_SITE_ID = 'swift_sites_current_site_id';
const SESSION_PAGE_NUM = 'swift_sites_current_page_number';
const SESSION_DIRTY = 'swift_sites_dirty';  // '1' if editor has unsaved changes

export const yamlStorage = {
    // ── Current session state (in-memory + sessionStorage) ──

    _siteId: null,
    _activePageNumber: 1,

    /** Get current site ID (from sessionStorage or null) */
    getSiteId() {
        if (this._siteId) return this._siteId;
        this._siteId = sessionStorage.getItem(SESSION_SITE_ID);
        return this._siteId;
    },

    setSiteId(siteId) {
        this._siteId = siteId;
        sessionStorage.setItem(SESSION_SITE_ID, siteId);
    },

    getActivePageNumber() {
        if (this._activePageNumber) return this._activePageNumber;
        const stored = sessionStorage.getItem(SESSION_PAGE_NUM);
        this._activePageNumber = stored ? parseInt(stored, 10) : 1;
        return this._activePageNumber;
    },

    setActivePageNumber(pageNumber) {
        this._activePageNumber = pageNumber;
        sessionStorage.setItem(SESSION_PAGE_NUM, String(pageNumber));
    },

    // ── Dirty flag (unsaved changes in editor) ──

    markDirty() {
        sessionStorage.setItem(SESSION_DIRTY, '1');
    },

    markClean() {
        sessionStorage.removeItem(SESSION_DIRTY);
    },

    isDirty() {
        return sessionStorage.getItem(SESSION_DIRTY) === '1';
    },

    // ── API wrappers ──

    /** Save current page to PostgreSQL */
    async saveCurrentPage(yamlContent) {
        const siteId = this.getSiteId();
        const pageNumber = this.getActivePageNumber();
        if (!siteId) return;
        await siteService.savePage(siteId, pageNumber, yamlContent);
        this.markClean();
    },

    /** Load a page from PostgreSQL */
    async loadPage(pageNumber) {
        const siteId = this.getSiteId();
        if (!siteId) return '';
        const page = await siteService.getPage(siteId, pageNumber);
        return page ? page.yaml_content : '';
    },

    /** Get site with page list from PostgreSQL */
    async getSite() {
        const siteId = this.getSiteId();
        if (!siteId) return null;
        return siteService.getSite(siteId);
    },

    /** Create a new site */
    async createSite(name) {
        const site = await siteService.createSite(name);
        this.setSiteId(site.id);
        this.setActivePageNumber(1);
        return site;
    },

    // ── Backward-compat shims (called by existing code) ──

    /** Sync save — marks dirty, actual DB save happens on explicit save or page switch */
    save(yamlContent) {
        this.markDirty();
        // Store in sessionStorage as fast local cache
        sessionStorage.setItem('swift_sites_yaml_cache', yamlContent);
    },

    /** Sync load from local cache */
    load() {
        return sessionStorage.getItem('swift_sites_yaml_cache') || '';
    },

    hasContent() {
        return !!this.load();
    },

    clear() {
        sessionStorage.removeItem('swift_sites_yaml_cache');
        sessionStorage.removeItem(SESSION_SITE_ID);
        sessionStorage.removeItem(SESSION_PAGE_NUM);
        sessionStorage.removeItem(SESSION_DIRTY);
    },
};
```

---

## Part 7: Pages Sidebar Panel — HTML

**File: `ssr_python/templates/index.html`**

### 7A. Add sidebar button (after images button)

```html
<button class="sidebar-btn" data-panel="pages" title="Pages">
    <svg class="sidebar-icon" aria-hidden="true"><use href="#icon-file-text"></use></svg>
</button>
```

### 7B. Add sidebar panel (after imagesPanel)

```html
<!-- Pages Panel -->
<div class="sidebar-panel" id="pagesPanel">
    <div class="panel-header">
        <span class="panel-title">Pages</span>
        <button class="panel-close" onclick="window.closePanel()">
            <svg class="icon-close" aria-hidden="true"><use href="#icon-x"></use></svg>
        </button>
    </div>
    <div class="panel-content" id="pagesContent">
        <!-- Rendered by pagesPanel.js -->
    </div>
    <div class="panel-footer" id="pagesFooter">
        <!-- Add Page button rendered here -->
    </div>
</div>
```

---

## Part 8: Pages Panel JavaScript — `pagesPanel.js` (new file)

**File: `ssr_python/static/js/pagesPanel.js`**

```javascript
import { yamlStorage } from './yamlStorage.js';
import { siteService } from './siteService.js';

let onPageSwitch = null;  // Callback set by main.js
let cachedSite = null;    // Cached site data to avoid re-fetching

/**
 * Initialize pages panel with page-switch callback
 */
export function initPagesPanel(callback) {
    onPageSwitch = callback;
}

/**
 * Render the pages list (fetches from API)
 */
export async function renderPagesPanel() {
    const container = document.getElementById('pagesContent');
    const footer = document.getElementById('pagesFooter');
    if (!container) return;

    const siteId = yamlStorage.getSiteId();
    if (!siteId) {
        container.innerHTML = '<div class="pages-empty">No site loaded</div>';
        return;
    }

    try {
        cachedSite = await siteService.getSite(siteId);
    } catch (e) {
        container.innerHTML = '<div class="pages-empty">Failed to load site</div>';
        return;
    }

    const activePageNumber = yamlStorage.getActivePageNumber();
    const siteIdShort = cachedSite.id.substring(0, 8) + '...';

    container.innerHTML = `
        <div class="pages-site-id">
            <span class="pages-site-label">Site ID</span>
            <span class="pages-site-value" title="${cachedSite.id}">${siteIdShort}</span>
        </div>
        <div class="pages-list">
            ${cachedSite.pages.map(page => `
                <div class="pages-row ${page.page_number === activePageNumber ? 'active' : ''}"
                     data-page-number="${page.page_number}">
                    <span class="pages-row-number">${page.page_number}</span>
                    <span class="pages-row-title">${page.title}</span>
                    <button class="pages-row-save" data-save-page="${page.page_number}" title="Save page">
                        <svg class="icon-sm" aria-hidden="true"><use href="#icon-save"></use></svg>
                    </button>
                    ${cachedSite.pages.length > 1 ? `
                        <button class="pages-row-delete" data-delete-page="${page.page_number}" title="Delete page">
                            <svg class="icon-sm" aria-hidden="true"><use href="#icon-trash-2"></use></svg>
                        </button>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;

    if (footer) {
        footer.innerHTML = `<button class="pages-add-btn" id="addPageBtn">+ Add Page</button>`;
    }

    attachPagesPanelEvents(container, footer);
}

function attachPagesPanelEvents(container, footer) {
    const siteId = yamlStorage.getSiteId();

    // Page row clicks → confirm save, then switch
    container.querySelectorAll('.pages-row').forEach(row => {
        row.addEventListener('click', async (e) => {
            if (e.target.closest('.pages-row-delete') || e.target.closest('.pages-row-save')) return;
            const pageNumber = parseInt(row.dataset.pageNumber, 10);
            const activePageNumber = yamlStorage.getActivePageNumber();
            if (pageNumber === activePageNumber) return; // Already on this page

            // ── Save confirmation before switching ──
            if (yamlStorage.isDirty()) {
                const choice = confirm(
                    'You have unsaved changes on the current page.\n\n' +
                    'Click OK to save and switch, or Cancel to stay.'
                );
                if (!choice) return; // User cancelled — stay on current page

                // Save current page to DB
                const editor = document.getElementById('codeEditor');
                if (editor) {
                    await yamlStorage.saveCurrentPage(editor.value);
                }
            }

            if (onPageSwitch) onPageSwitch(pageNumber);
        });
    });

    // Explicit save button
    container.querySelectorAll('.pages-row-save').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const pageNumber = parseInt(btn.dataset.savePage, 10);
            const activePageNumber = yamlStorage.getActivePageNumber();
            if (pageNumber === activePageNumber) {
                const editor = document.getElementById('codeEditor');
                if (editor) {
                    await yamlStorage.saveCurrentPage(editor.value);
                    // Visual feedback
                    btn.style.color = 'var(--accent)';
                    setTimeout(() => { btn.style.color = ''; }, 1000);
                }
            }
        });
    });

    // Delete buttons
    container.querySelectorAll('.pages-row-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const pageNumber = parseInt(btn.dataset.deletePage, 10);
            if (!confirm(`Delete page ${pageNumber}? This cannot be undone.`)) return;

            try {
                await siteService.deletePage(siteId, pageNumber);
                // If deleted page was active, switch to first remaining
                if (pageNumber === yamlStorage.getActivePageNumber()) {
                    const site = await siteService.getSite(siteId);
                    const firstPage = site.pages[0].page_number;
                    if (onPageSwitch) onPageSwitch(firstPage);
                }
                await renderPagesPanel();
            } catch (err) {
                console.error('[Pages] Delete failed:', err);
            }
        });
    });

    // Rename on double-click
    container.querySelectorAll('.pages-row-title').forEach(titleEl => {
        titleEl.addEventListener('dblclick', async () => {
            const row = titleEl.closest('.pages-row');
            const pageNumber = parseInt(row.dataset.pageNumber, 10);
            const currentTitle = titleEl.textContent;
            const newTitle = prompt('Page title:', currentTitle);
            if (newTitle && newTitle !== currentTitle) {
                await siteService.renamePage(siteId, pageNumber, newTitle);
                await renderPagesPanel();
            }
        });
    });

    // Add Page button
    const addBtn = footer ? footer.querySelector('#addPageBtn') : null;
    if (addBtn) {
        addBtn.addEventListener('click', async () => {
            try {
                // Save current page first if dirty
                if (yamlStorage.isDirty()) {
                    const editor = document.getElementById('codeEditor');
                    if (editor) await yamlStorage.saveCurrentPage(editor.value);
                }

                const result = await siteService.addPage(siteId);
                // Save empty page YAML
                const emptyPage = "- name: page\n  properties:\n    appearance:\n      background:\n        color: '#ffffff'\n        transparency: 100\n  components: []\n";
                await siteService.savePage(siteId, result.page_number, emptyPage);

                if (onPageSwitch) onPageSwitch(result.page_number);
                await renderPagesPanel();
            } catch (err) {
                console.error('[Pages] Add page failed:', err);
            }
        });
    }
}
```

---

## Part 9: Page Switching Logic in `main.js`

**File: `ssr_python/static/js/main.js`**

### 9A. Import

```javascript
import { initPagesPanel, renderPagesPanel } from './pagesPanel.js';
import { siteService } from './siteService.js';
```

### 9B. Page switch handler

```javascript
async function switchToPage(pageNumber) {
    const currentPageNumber = yamlStorage.getActivePageNumber();
    if (pageNumber === currentPageNumber) return;

    // Switch active page
    yamlStorage.setActivePageNumber(pageNumber);
    yamlStorage.markClean();

    // Load new page from DB
    try {
        const yamlContent = await yamlStorage.loadPage(pageNumber);
        dom.editor.value = yamlContent;
        sessionStorage.setItem('swift_sites_yaml_cache', yamlContent);

        // Clear selection (new page has different components)
        selectionManager.clearSelection();
        clearPropertiesPanel();
        historyManager.clear();

        // Render the new page
        actions.handleEditorInput(yamlContent, { pushHistory: false });
        // Push initial state for undo
        historyManager.push(yamlContent);

        await renderPagesPanel();
    } catch (err) {
        console.error('[Main] Failed to switch page:', err);
    }
}
```

### 9C. App initialization — load or create site

In `DOMContentLoaded`, after metadata loading:

```javascript
// Initialize pages panel
initPagesPanel(switchToPage);
window.renderPagesPanel = renderPagesPanel;

// Load or create site
let siteId = yamlStorage.getSiteId();
if (siteId) {
    // Existing site — load active page
    try {
        const pageNumber = yamlStorage.getActivePageNumber();
        const yamlContent = await yamlStorage.loadPage(pageNumber);
        if (yamlContent) {
            dom.editor.value = yamlContent;
            sessionStorage.setItem('swift_sites_yaml_cache', yamlContent);
            await renderPreview(yamlContent);
        }
    } catch (err) {
        console.warn('[Main] Failed to load site, creating new one:', err);
        siteId = null;
    }
}
if (!siteId) {
    // New site — create in DB
    const site = await yamlStorage.createSite('My Website');
    console.log('[Main] Created new site:', site.id);
}

// Render pages panel
renderPagesPanel();
```

### 9D. Mark dirty on editor changes

In `handleEditorInput()`, add:

```javascript
yamlStorage.markDirty();
```

---

## Part 10: Save Icon for Sprite

**File: `ssr_python/static/icon-sprite.svg`** — Add save icon:

```xml
<symbol id="icon-save" viewBox="0 0 24 24">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
    <polyline points="17 21 17 13 7 13 7 21"></polyline>
    <polyline points="7 3 7 8 15 8"></polyline>
</symbol>
```

---

## Part 11: Pages Panel CSS

**File: `ssr_python/static/css/style.css`**

```css
/* Pages Panel */
.pages-site-id {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 8px;
    background: var(--bg-dark);
    border-radius: 6px;
    font-size: 11px;
}

.pages-site-label {
    color: var(--text-muted);
    font-weight: 500;
}

.pages-site-value {
    color: var(--accent);
    font-family: monospace;
    cursor: help;
}

.pages-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.pages-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    border-left: 3px solid transparent;
}

.pages-row:hover {
    border-left-color: var(--accent);
    background: var(--bg-dark);
}

.pages-row.active {
    border-left-color: var(--accent);
    background: var(--accent-soft);
}

.pages-row-number {
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-dark);
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    flex-shrink: 0;
}

.pages-row.active .pages-row-number {
    background: var(--accent);
    color: white;
}

.pages-row-title {
    flex: 1;
    font-size: 13px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.pages-row.active .pages-row-title {
    color: var(--text);
    font-weight: 500;
}

.pages-row-save,
.pages-row-delete {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 2px;
    opacity: 0;
    transition: opacity 0.15s;
}

.pages-row:hover .pages-row-save,
.pages-row:hover .pages-row-delete {
    opacity: 0.6;
}

.pages-row-save:hover {
    color: var(--accent);
    opacity: 1 !important;
}

.pages-row-delete:hover {
    color: #ef4444;
    opacity: 1 !important;
}

.pages-add-btn {
    width: 100%;
    padding: 10px;
    background: var(--bg-dark);
    border: 1px dashed var(--border);
    border-radius: 6px;
    color: var(--text-muted);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.pages-add-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
}

.pages-empty {
    color: var(--text-muted);
    font-size: 13px;
    text-align: center;
    padding: 2rem 1rem;
}

.icon-sm {
    width: 14px;
    height: 14px;
    stroke: currentColor;
    fill: none;
    stroke-width: 2;
}
```

---

## Part 12: CSP Header Update for API Calls

**File: `ssr_python/app.py`** — The existing CSP already allows `connect-src 'self'` which covers fetch calls to `/api/*`. No change needed.

---

## REST API Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/sites` | List all sites |
| `POST` | `/api/sites` | Create new site (with page 1) |
| `GET` | `/api/sites/:id` | Get site + page list |
| `DELETE` | `/api/sites/:id` | Delete site + all pages |
| `PUT` | `/api/sites/:id/rename` | Rename site |
| `GET` | `/api/sites/:id/pages/:num` | Get page YAML |
| `PUT` | `/api/sites/:id/pages/:num` | Save page YAML |
| `POST` | `/api/sites/:id/pages` | Add new page |
| `DELETE` | `/api/sites/:id/pages/:num` | Delete page |
| `PUT` | `/api/sites/:id/pages/:num/rename` | Rename page |

---

## Files Summary

| File | Change |
|------|--------|
| `requirements.txt` | Add `psycopg2-binary>=2.9.0,<3.0` |
| `db.py` | **New** — PostgreSQL connection, schema init, site/page CRUD functions |
| `routes/sites.py` | **New** — Flask blueprint with 10 REST endpoints |
| `routes/__init__.py` | Register `sites_bp` blueprint |
| `app.py` | Call `init_db()` on startup |
| `config.py` | Add DB_* config vars |
| `.env.example` | Add DB_* env vars |
| `static/js/siteService.js` | **New** — Async API client for site/page endpoints |
| `static/js/yamlStorage.js` | Rewrite: API-backed with dirty flag + sessionStorage cache |
| `static/js/pagesPanel.js` | **New** — Pages panel UI with save confirmation on switch |
| `static/js/main.js` | `switchToPage()`, site init, dirty tracking, import pagesPanel |
| `templates/index.html` | Pages sidebar button + panel HTML |
| `static/css/style.css` | Pages panel CSS |
| `static/icon-sprite.svg` | Add `#icon-save` symbol |

## What Does NOT Change

- `renderer.py` — Still renders a single-page YAML array to HTML
- `routes/render.py` — Still receives YAML, returns HTML
- `preview_frame.html`, `preview_bridge.js` — No changes
- `ssr_app.js` — `renderPreview()` unchanged (one page at a time)
- `propertiesPanel.js`, `selectionManager.js` — Work on current page's components
- `component_schemas.yaml`, `component_defaults.yaml` — No changes
- `themesPanel.js` — Theme applies to current page only
- `historyManager.js` — Undo/redo is in-memory only (resets on page switch)

## Save Confirmation Flow

```
User clicks Page 2 row
        ↓
Is current page dirty? ──NO──→ Switch immediately
        │
       YES
        ↓
Show confirm dialog:
"You have unsaved changes on the current page.
 Click OK to save and switch, or Cancel to stay."
        ↓
    ┌───┴───┐
  Cancel    OK
    │        │
 Stay on   PUT /api/sites/:id/pages/:num (save YAML to DB)
 current       ↓
 page     Mark clean
              ↓
          GET /api/sites/:id/pages/:newNum (load new page)
              ↓
          Update editor + render preview
```

## Verification

1. **Setup:** Create PostgreSQL database `swift_sites`, set `.env` vars, `pip install psycopg2-binary`
2. **Start:** `python app.py` — tables auto-created, logs "Database tables initialized"
3. **New site:** On first load, site created in DB with page 1, site ID shown in Pages panel
4. **Edit page:** Type in editor — dirty flag set. Save icon appears on hover.
5. **Save:** Click save icon on page row — `PUT` to DB, visual feedback
6. **Add page:** Click "+ Add Page" — saves current page first if dirty, creates page 2 in DB
7. **Switch with unsaved changes:** Click page 1 — confirm dialog appears. OK saves + switches. Cancel stays.
8. **Switch without changes:** Click page 1 (clean) — switches immediately, no dialog
9. **Delete page:** Click trash on page 2 — confirm, `DELETE` in DB, switch to remaining page
10. **Rename:** Double-click title — prompt, `PUT` rename to DB
11. **Refresh:** F5 — site ID and active page restored from sessionStorage, YAML loaded from DB
12. **API test:** `curl http://localhost:5000/api/sites` returns JSON site list
13. `python -m pytest tests/ -v` — existing 30 tests pass (no renderer changes)
