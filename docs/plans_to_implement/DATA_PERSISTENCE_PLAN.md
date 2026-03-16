# Data Persistence & Publishing Architecture

## Context

Swift Sites currently has **zero server-side persistence**. All site data lives in browser `sessionStorage` (tab-scoped, lost on close). This plan introduces a scalable, elegant solution that:

1. **Persists data during editing** — autosave, survive browser close, load from any device
2. **Persists data when published** — visitors can view rendered pages at stable URLs
3. **Supports multipage sites** — each page has its own API path/route
4. **Multi-tenant from day one** — organization-based tenancy, multiple users per org
5. **Future form submissions** — published pages with forms submit data to secure, tenant-isolated endpoints

## Current State

| Layer | Current | After |
|-------|---------|-------|
| Editor storage | `sessionStorage` (tab-scoped) | SQLite via autosave API |
| Server state | Stateless (render-only) | Stateful (CRUD + render) |
| Publishing | Manual HTML export download | One-click publish to live URL |
| Multipage | YAML structure exists, switching not wired | Full page routing |
| Database | None | SQLite + SQLAlchemy |
| Tenancy | Single-user | Organization-based multi-tenant |
| Forms | Static HTML | Secure per-site form submission endpoints |

---

## Database Schema — Multi-Tenant (Organization-Based)

### Entity Relationship Diagram

```
organizations ──┬── org_members ── users
                │
                └── sites ──┬── site_pages        (source YAML, per-page)
                            ├── published_pages   (rendered HTML cache)
                            ├── site_images
                            └── form_submissions
```

**Tenancy chain:** `organization → site → (site_pages, published_pages, images, form_submissions)`
All data is scoped through the organization. No cross-org data access.

---

### `users` — User Accounts

```python
class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email         = db.Column(db.String(255), nullable=False, unique=True)
    name          = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active     = db.Column(db.Boolean, nullable=False, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = db.relationship('OrgMember', backref='user', cascade='all, delete-orphan')
```

---

### `organizations` — Tenants / Workspaces

```python
class Organization(db.Model):
    __tablename__ = 'organizations'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = db.Column(db.String(255), nullable=False)
    slug          = db.Column(db.String(100), nullable=False, unique=True)
    plan          = db.Column(db.String(20), nullable=False, default='free')  # free | pro | enterprise
    is_active     = db.Column(db.Boolean, nullable=False, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship('OrgMember', backref='organization', cascade='all, delete-orphan')
    sites   = db.relationship('Site', backref='organization', cascade='all, delete-orphan')
```

- Every user gets a **personal organization** on signup (invisible until they invite someone)
- `plan` column for future billing tiers

---

### `org_members` — User ↔ Organization Membership

```python
class OrgMember(db.Model):
    __tablename__ = 'org_members'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id        = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    role          = db.Column(db.String(20), nullable=False, default='editor')
    joined_at     = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('org_id', 'user_id', name='uq_org_user'),
    )
```

**Roles:**
| Role | Permissions |
|------|------------|
| `owner` | Full access. Manage members, billing, delete org. |
| `admin` | Manage sites, publish, manage members (except owner). |
| `editor` | Create/edit sites, publish. Cannot manage members. |
| `viewer` | Read-only access to sites. |

---

### `sites` — Source of Truth (Org-Scoped)

Site metadata and relationships. Source YAML is stored per-page in `site_pages`.

```python
class Site(db.Model):
    __tablename__ = 'sites'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id        = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    created_by    = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name          = db.Column(db.String(255), nullable=False, default='Untitled Site')
    slug          = db.Column(db.String(255), nullable=False)
    status        = db.Column(db.String(20), nullable=False, default='draft')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at  = db.Column(db.DateTime, nullable=True)
    form_secret   = db.Column(db.String(64), nullable=True)

    source_pages    = db.relationship('SitePage', backref='site', cascade='all, delete-orphan',
                                       order_by='SitePage.sort_order')
    published_pages = db.relationship('PublishedPage', backref='site', cascade='all, delete-orphan')
    images          = db.relationship('SiteImage', backref='site', cascade='all, delete-orphan')
    submissions     = db.relationship('FormSubmission', backref='site', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('org_id', 'slug', name='uq_org_site_slug'),
    )
```

**Key changes from single-user design:**
- `org_id` replaces `user_id` — sites belong to organizations, not users
- `created_by` tracks who created the site (audit trail, not ownership)
- Slug is unique **per organization** (not globally) — two orgs can both have "my-store"

---

### `site_pages` — Source YAML (Per-Page)

Each page is stored as its own database row with a **complete renderable YAML document** (including the site wrapper). Theme anchors are document-scoped within each page's YAML, so per-page storage preserves all YAML anchor/alias functionality.

```python
class SitePage(db.Model):
    __tablename__ = 'site_pages'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id       = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    slug          = db.Column(db.String(255), nullable=False)
    title         = db.Column(db.String(255), nullable=False, default='Untitled Page')
    yaml_content  = db.Column(db.Text, nullable=False, default='')
    sort_order    = db.Column(db.Integer, nullable=False, default=0)
    is_homepage   = db.Column(db.Boolean, nullable=False, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'slug', name='uq_site_source_page_slug'),
    )
```

**Per-page YAML structure:** Each page's `yaml_content` stores a complete renderable document:
```yaml
- name: site
  id: "93a00415-..."
  components:
    - name: page
      id: page-1
      slug: home
      title: "My Page"
      properties:
        theme:
          fonts:
            heading: &font-heading "'Inter', sans-serif"
            content: &font-content "'Inter', sans-serif"
          colors:
            primary: &color-primary "#1e293b"
            ...
      components:
        - name: heading
          ...
```

---

### `published_pages` — Pre-Rendered HTML Cache

```python
class PublishedPage(db.Model):
    __tablename__ = 'published_pages'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id       = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    slug          = db.Column(db.String(255), nullable=False)
    title         = db.Column(db.String(255), nullable=False)
    rendered_html = db.Column(db.Text, nullable=False)
    sort_order    = db.Column(db.Integer, default=0)
    rendered_at   = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'slug', name='uq_site_page_slug'),
    )
```

---

### `site_images` — Stored Images (Scoped via Site → Org)

```python
class SiteImage(db.Model):
    __tablename__ = 'site_images'

    id             = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id        = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=True, index=True)
    filename       = db.Column(db.String(255), nullable=False)
    original_name  = db.Column(db.String(255))
    mime_type      = db.Column(db.String(100))
    file_size      = db.Column(db.Integer)
    width          = db.Column(db.Integer, nullable=True)
    height         = db.Column(db.Integer, nullable=True)
    source         = db.Column(db.String(20))           # 'upload', 'pexels', 'pixabay', 'external'
    source_url     = db.Column(db.Text, nullable=True)  # Original CDN URL (for attribution + dedup)
    photographer   = db.Column(db.String(255), nullable=True)
    alt_text       = db.Column(db.String(500), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### `form_submissions` — Published Form Data (Future)

```python
class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'

    id            = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id       = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    page_slug     = db.Column(db.String(255), nullable=False)
    form_name     = db.Column(db.String(255), nullable=False)  # From YAML form component name/id
    data          = db.Column(db.Text, nullable=False)         # JSON blob of submitted field values
    submitted_at  = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address    = db.Column(db.String(45), nullable=True)    # IPv4/IPv6 for spam detection
    user_agent    = db.Column(db.String(500), nullable=True)
    is_spam       = db.Column(db.Boolean, nullable=False, default=False)
    is_read       = db.Column(db.Boolean, nullable=False, default=False)
```

**Form submission flow:**
1. Published page contains a `<form>` component rendered from YAML
2. Form `action` points to: `POST /s/:site-slug/forms/:form-name/submit`
3. Server validates and stores data as JSON blob
4. Site owner views submissions in dashboard (future UI)

**Tenant isolation:** submissions scoped by `site_id → org_id`

---

### Tenant Isolation Strategy

Tenant isolation prevents one organization's users from accessing, modifying, or even detecting the existence of another organization's data. It operates at three layers: **identity verification**, **query scoping**, and **role-based permissions**.

---

#### Layer 1: Authentication Middleware — Session-Derived Identity

The user's identity and active organization are **never** taken from URL parameters, request body, or headers. They are derived exclusively from the server-side session, which is set during login and stored server-side (signed cookie).

```python
# middleware.py — runs before every /api/* request

from flask import g, session, abort
from functools import wraps

def require_auth(f):
    """Decorator for all /api/* routes. Sets g.current_user and g.current_org_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(401)  # Not logged in

        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            abort(401)

        # current_org_id is set in session by the org switcher UI (Phase 8)
        # or defaults to user's personal org
        org_id = session.get('current_org_id')
        if not org_id:
            abort(403)

        # CRITICAL: Verify the user actually belongs to this org
        membership = OrgMember.query.filter_by(
            user_id=user_id, org_id=org_id
        ).first()
        if not membership:
            abort(403)  # User does NOT belong to this org

        g.current_user = user
        g.current_org_id = org_id
        g.current_role = membership.role

        return f(*args, **kwargs)
    return decorated
```

**Why this blocks identity spoofing:**

| Attack | Why It Fails |
|--------|-------------|
| Send fake `email` in request body | Email is never used for authorization. Identity comes from `session['user_id']`, which is set only during login. |
| Send fake `org_id` in request body | `g.current_org_id` comes from `session['current_org_id']`, not from request body. The server ignores any `org_id` in the request payload. |
| Tamper with session cookie | Flask sessions are cryptographically signed with `SECRET_KEY`. Any tampering invalidates the signature → 401. |
| Set `current_org_id` to an org the user doesn't belong to | Membership check (`OrgMember.query.filter_by(user_id, org_id)`) catches this. Even if a user somehow sets a different `org_id` in session, no `OrgMember` row exists → 403. |

---

#### Layer 2: Query Scoping — IDOR Protection on Every Endpoint

Every query that fetches a site (or site-child data) **must** filter by `org_id` from the session. This prevents Insecure Direct Object Reference (IDOR) attacks where an attacker guesses or enumerates UUIDs.

```python
# guards.py — reusable IDOR protection helpers

from flask import g, abort

def get_site_or_404(site_id):
    """Fetch a site and verify the current user's org owns it.
    Returns 404 (not 403) to avoid revealing that the site exists in another org."""
    site = Site.query.filter_by(id=site_id, org_id=g.current_org_id).first()
    if not site:
        abort(404)
    return site

def get_submission_or_404(site_id, submission_id):
    """Fetch a form submission through the site ownership chain."""
    site = get_site_or_404(site_id)  # Verifies org ownership first
    submission = FormSubmission.query.filter_by(id=submission_id, site_id=site.id).first()
    if not submission:
        abort(404)
    return site, submission
```

**Applied to every CRUD endpoint:**

```python
# All queries MUST scope by org via the guard helpers:
site = get_site_or_404(site_id)                      # CORRECT — double-filters by (id, org_id)
site = Site.query.get(site_id)                        # WRONG — returns any org's site
sites = Site.query.filter_by(org_id=g.current_org_id) # CORRECT — list scoped to org
sites = Site.query.all()                              # WRONG — returns all orgs' sites
```

**Why 404 instead of 403:** Returning 403 ("forbidden") reveals that the resource exists but belongs to someone else. Returning 404 ("not found") gives no information — the attacker can't distinguish "wrong org" from "doesn't exist."

**Cascade chain:** `Organization → Site → (SitePage, PublishedPage, SiteImage, FormSubmission)`

Child resources (pages, images, submissions) don't need their own `org_id` columns. Since access always goes through `get_site_or_404()` first, org ownership is verified on the site, and child queries filter by `site_id`.

---

#### Layer 3: Role-Based Permissions (RBAC)

After identity and org ownership are verified, the user's **role within the org** determines what actions they can perform.

```python
# guards.py — role enforcement

ROLE_HIERARCHY = {'owner': 4, 'admin': 3, 'editor': 2, 'viewer': 1}

def require_role(minimum_role):
    """Decorator to enforce minimum role for an endpoint."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_level = ROLE_HIERARCHY.get(g.current_role, 0)
            required_level = ROLE_HIERARCHY.get(minimum_role, 0)
            if user_level < required_level:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator
```

**Per-endpoint role requirements:**

| Endpoint | Minimum Role | Why |
|----------|-------------|-----|
| `GET /api/sites` | `viewer` | Read-only listing |
| `GET /api/sites/:id` | `viewer` | Read-only site load |
| `POST /api/sites` | `editor` | Creating content |
| `PUT /api/sites/:id` | `editor` | Editing content |
| `PATCH /api/sites/:id` | `editor` | Updating metadata |
| `DELETE /api/sites/:id` | `admin` | Destructive — requires elevated access |
| `POST /api/sites/:id/publish` | `editor` | Publishing content |
| `POST /api/sites/:id/unpublish` | `editor` | Unpublishing content |
| `GET /api/sites/:id/submissions` | `editor` | Viewing form data |
| `PATCH /api/sites/:id/submissions/:sub_id` | `editor` | Managing submissions |
| `DELETE /api/sites/:id/submissions/:sub_id` | `admin` | Destructive |
| `POST /api/orgs/:id/members` | `admin` | Member management |
| `PATCH /api/orgs/:id/members/:user_id` | `admin` | Role changes |
| `DELETE /api/orgs/:id/members/:user_id` | `admin` | Member removal |
| `DELETE /api/orgs/:id` | `owner` | Org deletion — only owner |

**Usage pattern (all three layers combined):**

```python
@site_bp.route('/api/sites/<site_id>', methods=['DELETE'])
@require_auth          # Layer 1: Verify identity, set g.current_org_id
@require_role('admin') # Layer 3: Must be admin or owner
def delete_site(site_id):
    site = get_site_or_404(site_id)  # Layer 2: Verify org ownership, prevent IDOR
    db.session.delete(site)          # Cascade deletes pages, images, submissions
    db.session.commit()
    return jsonify({'ok': True})
```

---

#### Published Routes — Intentionally Public (No Auth)

Published site routes and form submission endpoints are **public** — they serve visitors, not org members. Both subdomain and path-based routes resolve to the same handler:

| Route (Subdomain) | Route (Path Fallback) | Auth | Isolation Mechanism |
|-------|------|------|-------------------|
| `GET my-store.swiftsites.com/:page` | `GET /s/my-store/:page` | None (public) | Only serves sites with `status='published'` |
| `POST my-store.swiftsites.com/forms/:name/submit` | `POST /s/my-store/forms/:name/submit` | None (public) | HMAC + honeypot + rate limiting (see Anti-Bot section) |

These routes do NOT use `g.current_org_id`. They query by site slug and enforce the `status='published'` filter to ensure only intentionally-published content is served. In subdomain mode, the slug is extracted from the `Host` header; in path mode, from the URL.

---

#### Attack Vector Analysis

| Attack | Layer | Defense | Result |
|--------|-------|---------|--------|
| Change `:id` in `/api/sites/:id` to another site's UUID | L2 | `get_site_or_404()` filters by `(id, org_id)` | 404 — site not found in attacker's org |
| Inject `org_id` in request body | L1 | `g.current_org_id` from session, body `org_id` ignored | No effect |
| Inject `email` in request body | L1 | Identity from `session['user_id']`, not request body | No effect |
| Tamper with session cookie | L1 | Flask signed cookies — tampering invalidates signature | 401 |
| Guess another site's UUID (enumeration) | L2 | UUIDs are 128-bit random — infeasible to enumerate. Even if guessed, org_id filter blocks access | 404 |
| Viewer tries to delete a site | L3 | `@require_role('admin')` on delete endpoint | 403 |
| Viewer tries to publish a site | L3 | `@require_role('editor')` on publish endpoint | 403 |
| Switch to org user doesn't belong to (via org switcher) | L1 | Membership check in `require_auth` — no `OrgMember` row → 403 | 403 |
| Access form submissions from another org's site | L2 | `get_submission_or_404()` chains through `get_site_or_404()` → org check | 404 |
| Access published page of draft site | Public | Query filters by `status='published'` | 404 |

---

### Why Organization-Based (Not User-Based)?

| Aspect | User-based | Organization-based |
|--------|-----------|-------------------|
| Collaboration | No sharing | Multiple users per org, role-based |
| Agency use case | Awkward | Agency creates org, invites team |
| Personal use | Direct ownership | Personal org auto-created on signup |
| Billing (future) | Per-user | Per-org (natural billing entity) |
| Schema migration | Would need org tables later | Ready from day one |

---

## API Endpoints

### Editor APIs (Site CRUD) — Authenticated, Org-Scoped

Every `/api/*` endpoint uses all three isolation layers: `@require_auth` (identity from session), `get_site_or_404()` (IDOR guard), and `@require_role()` (RBAC).

| Method | Endpoint | Min Role | IDOR Guard | Purpose | Request Body | Response |
|--------|----------|----------|-----------|---------|-------------|----------|
| `GET` | `/api/sites` | `viewer` | org-scoped list | List org's sites | — | `[{id, name, slug, status, updated_at, page_count}]` |
| `POST` | `/api/sites` | `editor` | new site gets `g.current_org_id` | Create new site + homepage | `{name, slug}` | `{id, name, slug, pages: [{id, slug, title, yaml_content}]}` |
| `GET` | `/api/sites/:id` | `viewer` | `get_site_or_404(id)` | Load site metadata + page list | — | `{id, name, slug, status, pages: [{id, slug, title, sort_order, is_homepage}]}` |
| `PATCH` | `/api/sites/:id` | `editor` | `get_site_or_404(id)` | Update metadata | `{name?, slug?}` | `{ok: true}` |
| `DELETE` | `/api/sites/:id` | `admin` | `get_site_or_404(id)` | Delete site + cascade | — | `{ok: true}` |
| `POST` | `/api/sites/:id/publish` | `editor` | `get_site_or_404(id)` + global slug check | Publish site | — | `{ok, url, pages: [{slug, url}]}` |
| `POST` | `/api/sites/:id/unpublish` | `editor` | `get_site_or_404(id)` | Unpublish site | — | `{ok: true}` |

### Page-Level CRUD — Per-Page YAML Storage

| Method | Endpoint | Min Role | IDOR Guard | Purpose | Request Body | Response |
|--------|----------|----------|-----------|---------|-------------|----------|
| `GET` | `/api/sites/:id/pages` | `viewer` | `get_site_or_404(id)` | List pages | — | `[{id, slug, title, sort_order, is_homepage}]` |
| `POST` | `/api/sites/:id/pages` | `editor` | `get_site_or_404(id)` | Create new page | `{title, slug}` | `{id, slug, title, yaml_content}` |
| `GET` | `/api/sites/:id/pages/:page_id` | `viewer` | `get_page_or_404(id, page_id)` | Load page YAML | — | `{id, slug, title, yaml_content}` |
| `PUT` | `/api/sites/:id/pages/:page_id` | `editor` | `get_page_or_404(id, page_id)` | Autosave page YAML | `{yaml_content}` | `{ok, updated_at}` |
| `PATCH` | `/api/sites/:id/pages/:page_id` | `editor` | `get_page_or_404(id, page_id)` | Update page metadata | `{title?, slug?, sort_order?}` | `{ok}` |
| `DELETE` | `/api/sites/:id/pages/:page_id` | `admin` | `get_page_or_404(id, page_id)` | Delete page | — | `{ok}` |

### Published Site Routes (Visitor-Facing — Public, No Auth)

Published sites use **subdomain routing** as the primary mode with **path-based fallback** for local development.

#### Primary: Subdomain Routing (Production)

Each published site gets its own subdomain: `<site-slug>.<platform-domain>`

| Method | URL | Purpose |
|--------|-----|---------|
| `GET` | `my-store.swiftsites.com` | Redirect to first page (home) |
| `GET` | `my-store.swiftsites.com/about` | Serve pre-rendered page HTML |
| `POST` | `my-store.swiftsites.com/forms/contact/submit` | Submit form data (JS challenge) |

#### Fallback: Path-Based Routing (Local Dev)

When DNS wildcards aren't available (local development on `localhost`), use path prefix:

| Method | URL | Purpose |
|--------|-----|---------|
| `GET` | `localhost:5000/s/my-store` | Redirect to first page (home) |
| `GET` | `localhost:5000/s/my-store/about` | Serve pre-rendered page HTML |
| `POST` | `localhost:5000/s/my-store/forms/contact/submit` | Submit form data (JS challenge) |

#### Route Resolution Logic

```python
# routes/published.py

def get_site_slug():
    """Determine site slug from subdomain or path prefix."""
    host = request.host.split(':')[0]  # Strip port
    platform_domain = current_app.config['PLATFORM_DOMAIN']  # e.g., 'swiftsites.com'

    if host.endswith('.' + platform_domain):
        # Subdomain mode: my-store.swiftsites.com → 'my-store'
        return host[: -(len(platform_domain) + 1)]
    return None  # Not a subdomain request — use path-based route

# Subdomain route (production)
@published_bp.route('/', defaults={'page_slug': None}, subdomain='<site_slug>')
@published_bp.route('/<page_slug>', subdomain='<site_slug>')
def serve_subdomain(site_slug, page_slug):
    return _serve_page(site_slug, page_slug)

# Path-based route (local dev fallback)
@published_bp.route('/s/<site_slug>', defaults={'page_slug': None})
@published_bp.route('/s/<site_slug>/<page_slug>')
def serve_path(site_slug, page_slug):
    return _serve_page(site_slug, page_slug)

def _serve_page(site_slug, page_slug):
    """Shared handler — serves pre-rendered HTML from published_pages."""
    site = Site.query.filter_by(slug=site_slug, status='published').first_or_404()
    if page_slug is None:
        # Redirect to first page (home)
        home = PublishedPage.query.filter_by(site_id=site.id).order_by(
            PublishedPage.sort_order
        ).first_or_404()
        page_slug = home.slug
    page = PublishedPage.query.filter_by(
        site_id=site.id, slug=page_slug
    ).first_or_404()
    return page.rendered_html, 200, {'Content-Type': 'text/html'}
```

#### Form Submission Routes (Dual Mode)

```python
# Subdomain mode (production)
@published_bp.route('/forms/<form_name>/submit', methods=['POST'], subdomain='<site_slug>')
def submit_form_subdomain(site_slug, form_name):
    return _handle_form_submission(site_slug, form_name)

# Path-based mode (local dev)
@published_bp.route('/s/<site_slug>/forms/<form_name>/submit', methods=['POST'])
def submit_form_path(site_slug, form_name):
    return _handle_form_submission(site_slug, form_name)
```

### Form Dashboard (Authenticated — Future)

All submission endpoints chain through `get_site_or_404()` to verify org ownership before accessing submission data.

| Method | Endpoint | Min Role | IDOR Guard | Purpose |
|--------|----------|----------|-----------|---------|
| `GET` | `/api/sites/:id/submissions` | `editor` | `get_site_or_404(id)` then filter by `site_id` | List submissions |
| `PATCH` | `/api/sites/:id/submissions/:sub_id` | `editor` | `get_submission_or_404(id, sub_id)` | Mark read/spam |
| `DELETE` | `/api/sites/:id/submissions/:sub_id` | `admin` | `get_submission_or_404(id, sub_id)` | Delete submission |

### Organization APIs (Future — When Auth Is Implemented)

Org endpoints verify the user belongs to the org AND has the required role. Org listing is scoped to the user's memberships — users only see orgs they belong to.

| Method | Endpoint | Min Role | IDOR Guard | Purpose |
|--------|----------|----------|-----------|---------|
| `GET` | `/api/orgs` | any member | List filtered by `OrgMember.user_id = g.current_user.id` | List user's organizations |
| `POST` | `/api/orgs` | any logged-in | User becomes `owner` of new org | Create organization |
| `POST` | `/api/orgs/:id/members` | `admin` | Verify `g.current_org_id == :id` + role check | Invite member |
| `PATCH` | `/api/orgs/:id/members/:user_id` | `admin` | Verify `g.current_org_id == :id` + cannot change owner role | Change role |
| `DELETE` | `/api/orgs/:id/members/:user_id` | `admin` | Cannot remove owner. Verify `g.current_org_id == :id` | Remove member |
| `DELETE` | `/api/orgs/:id` | `owner` | Only owner can delete. Cascades all sites, data | Delete organization |

---

## Key Flows

### 1. Create New Site

```
User clicks "New Site" in Sites panel
    → POST /api/sites { name: "My Store", slug: "my-store" }
    → Server: Create site row + first SitePage row (homepage with default YAML)
    → Response: { id, pages: [{id, slug, title, yaml_content}] }
    → Editor: Load first page's YAML into code editor
```

### 2. Autosave During Editing

```
Editor change → debounce 2 seconds
    → PUT /api/sites/:id/pages/:page_id { yaml_content: editor.value }
    → Server: Update SitePage.yaml_content and SitePage.updated_at
    → Response: { ok: true, updated_at }
    → UI: Show "Saved" indicator
```

### 2b. Page Switching

```
User clicks different page in Pages panel
    → Client: autosave current page (PUT to current page_id)
    → Client: GET /api/sites/:id/pages/:new_page_id
    → Client: set editor.value = response.yaml_content
    → Client: trigger re-render
```

### 2c. Add New Page

```
User clicks "Add Page" in Pages panel
    → POST /api/sites/:id/pages { title: "About", slug: "about" }
    → Server creates SitePage with default YAML template
    → Client: navigate to new page (same as page switch)
```

### 3. Publish Site

```
User clicks "Publish" button
    → POST /api/sites/:id/publish
    → Server:
        1. Verify org ownership via get_site_or_404()
        2. Check global slug uniqueness (reject 409 on conflict)
        3. For each SitePage (ordered by sort_order):
           a. Parse YAML, render to HTML
           b. Store in published_pages
        4. SET status = 'published'
    → Response: { ok, url, pages: [{slug, url}] }
```

### 4. Form Submission (Future — Bot-Protected)

```
Visitor fills form on published page → clicks Submit
    → JavaScript intercepts submit event:
        1. Read hidden _form_token from form
        2. Read _page_load_ts (set when page loaded via JS)
        3. Compute _challenge = HMAC-SHA256(_form_token + _page_load_ts, site_secret)
        4. Submit via fetch() with: fields + _form_token + _page_load_ts + _challenge
    → POST /forms/contact/submit (relative path — works on both subdomain and path mode)
      In subdomain mode: my-store.swiftsites.com/forms/contact/submit
      In path mode:      localhost:5000/s/my-store/forms/contact/submit
    → Server validates (ALL must pass):
        1. _form_token exists and matches site's published token
        2. _page_load_ts is within last 24 hours
        3. _challenge = HMAC-SHA256(_form_token + _page_load_ts, site_secret) matches
        4. Time since _page_load_ts > 3 seconds (humans can't fill forms instantly)
        5. Honeypot field "_website" is empty (bots fill hidden fields)
        6. Rate limit: max 10 submissions per IP per minute per site
    → If valid: store in form_submissions, return success
    → If invalid: return 403 (no details about which check failed)
```

---

## File Structure (New/Modified)

```
ssr_python/
├── app.py                     # MODIFIED — db.init_app(), create_tables(), uploads dir, bootstrap default org
├── config.py                  # MODIFIED — SQLALCHEMY_DATABASE_URI, UPLOAD_FOLDER
├── extensions.py              # MODIFIED — db = SQLAlchemy()
├── models.py                  # NEW — User, Organization, OrgMember, Site, PublishedPage, SiteImage, FormSubmission
├── guards.py                  # NEW — get_site_or_404(), get_page_or_404(), get_submission_or_404(), require_role(), validate_site_slug(), generate_default_page_yaml()
├── middleware.py              # NEW — @require_auth decorator, session-based identity (Phase 7)
├── routes/
│   ├── __init__.py            # MODIFIED — register published_bp, uploads_bp
│   ├── site.py                # MODIFIED — full site + page CRUD + publish/unpublish + IDOR guards + org scoping
│   ├── images.py              # MODIFIED — /api/images/upload endpoint
│   ├── uploads.py             # NEW — /uploads/<filename> serving route + /api/images/upload
│   └── published.py           # NEW — /s/:slug/:page routes + form submission endpoint
├── static/js/
│   ├── siteManager.js         # NEW — site CRUD client, page CRUD, autosave
│   ├── pageManager.js         # NEW — page switching, page list UI
│   ├── imagesPanel.js         # MODIFIED — upload handler → POST to server
│   └── main.js                # MODIFIED — integrate siteManager, autosave
├── instance/
│   ├── swift_sites.db         # NEW — SQLite database (gitignored)
│   └── uploads/               # NEW — stored image files (gitignored)
└── requirements.txt           # MODIFIED — add flask-sqlalchemy
```

---

## Implementation Phases

### Phase 1: Database Foundation
- Add `flask-sqlalchemy` to requirements.txt
- Create `models.py` with ALL models: User, Organization, OrgMember, Site, PublishedPage, SiteImage, FormSubmission
- Update `extensions.py` to initialize SQLAlchemy
- Update `config.py` with `SQLALCHEMY_DATABASE_URI`, `UPLOAD_FOLDER`
- Update `app.py` to call `db.init_app()`, create tables, create uploads dir
- Bootstrap default organization + default user on first run (before auth exists)
- Add `instance/` to `.gitignore`

### Phase 2: Site CRUD API
- Create `guards.py` with `get_site_or_404()`, `get_submission_or_404()`, `require_role()` helpers
- Add `set_default_org` pre-auth stub in `routes/site.py` (temporary until Phase 7)
- Expand `routes/site.py` with full CRUD endpoints — all using `get_site_or_404()` for IDOR protection
- `GET /api/sites` — list org's sites (scoped by `g.current_org_id`)
- `POST /api/sites` — create site with default YAML (assigns `g.current_org_id`)
- `GET /api/sites/:id` — load site via `get_site_or_404(id)`
- `PUT /api/sites/:id` — autosave YAML via `get_site_or_404(id)`
- `PATCH /api/sites/:id` — update metadata via `get_site_or_404(id)`
- `DELETE /api/sites/:id` — delete site + cascade via `get_site_or_404(id)`

### Phase 3: Client-Side Integration
- Create `siteManager.js` — client-side API wrapper
- Update `main.js` — replace `yamlStorage.save()` with autosave API
- Add Sites panel to sidebar

### Phase 4: Publish & Serve
- Server-side publish logic with image localization
- Global slug uniqueness check at publish time (reject 409 on conflict)
- Slug validation (DNS-safe: lowercase alphanumeric + hyphens, 3-63 chars, reserved slugs blocked)
- `routes/published.py` — dual-mode routing (subdomain primary + path fallback)
- Add `PLATFORM_DOMAIN` and `PUBLISHED_MODE` to config
- Form action URLs use relative paths (`/forms/:name/submit`) — work in both modes
- Publish/Unpublish buttons in editor

### Phase 5: Image Persistence (CDN During Dev, Save on Publish)
- `/api/images/upload` endpoint for user uploads
- `routes/uploads.py` — serve stored images
- `localize_images_in_html()` in publish flow

### Phase 6: Form Submissions (Future)
- `POST /s/:site-slug/forms/:form-name/submit` endpoint (public, bot-protected)
- Rate limiting + honeypot spam protection
- Submissions dashboard API — all endpoints chain through `get_site_or_404()` for org isolation

### Phase 7: Authentication (Future)
- Register, login, logout routes
- Password hashing (bcrypt/argon2)
- Create `middleware.py` with `@require_auth` decorator (see Tenant Isolation Strategy section)
- Replace `set_default_org` stub with `@require_auth` on all `/api/*` routes
- `@require_auth` sets `g.current_user`, `g.current_org_id`, `g.current_role` from server-side session
- Membership verification: confirm user belongs to active org via `OrgMember` table
- Personal org auto-created on signup (user becomes `owner`)
- Assign default org's data to first registered user

### Phase 8: Organization Management (Future)
- Org CRUD, invite members, role management
- Org switcher in UI

### Phase 9: Polish
- "Last saved" timestamp, duplicate site, confirm delete
- Published site 404 page
- Site slug validation (URL-safe, unique per org)

---

## Migration Path

**sessionStorage → DB autosave:**
- `yamlStorage.js` remains as fallback (offline/disconnected editing)
- On startup: if site ID in URL → load from DB; else if sessionStorage has content → offer to save as new site
- Autosave writes to both sessionStorage (instant) and DB (debounced)

**Phase 1 bootstrap (before auth exists):**
- Create a "default" organization and "default" user on first run
- All sites created during Phase 1–5 use this default org
- When auth is implemented later, default org is assigned to the first real user
- No data migration needed

**Pre-auth security assumptions (Phases 1–5):**
- **No tenant isolation exists** during Phases 1–5. The `@require_auth` decorator and `g.current_org_id` are not wired yet.
- All CRUD endpoints are **open** — anyone who can reach the server can list/edit/delete any site.
- This is acceptable because Phases 1–5 are **local development only** (the server runs on `localhost:5000`).
- The CRUD routes MUST be written with the `get_site_or_404()` pattern from day one, even though `g.current_org_id` is hardcoded to the default org. This ensures:
  - The query pattern is already correct when auth is added
  - No refactoring needed — just replace the hardcoded org_id with the session-derived value
- **Pre-auth stub for Phases 2–5:**

```python
# In routes/site.py — temporary stub until Phase 7 (Auth)
from flask import g

@site_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    from models import Organization
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
```

This stub will be replaced by `@require_auth` in Phase 7. The critical point: all route code uses `g.current_org_id` — never hardcoded org IDs — so the transition is seamless.

**Adding auth (Phase 7):**
- Replace the `set_default_org` stub with `@require_auth` middleware
- `@require_auth` sets `g.current_user`, `g.current_org_id`, `g.current_role` from session
- All site queries already filter by `org_id = g.current_org_id` — no code changes needed
- Existing data already has `org_id` set (to default org)
- Default org is assigned to the first real user who registers

---

## Design Decisions

### Why organization-based tenancy?
- Supports both solo users (personal org) and teams (shared org) with one schema
- Natural billing entity (charge per org, not per user)
- Clean data boundary — all isolation flows through `org_id`
- No schema migration needed when adding collaboration

### Why personal org on signup?
- Invisible to solo users — they just see "my sites"
- When they invite someone, the org becomes visible naturally
- Same query pattern regardless of solo vs team usage

### Why JSON blob for form submissions?
- Form fields defined in YAML can change anytime (no fixed schema)
- No DB migrations when form fields change
- JSON queryable in SQLite (json_extract) and PostgreSQL (jsonb)

### Why per-page YAML rows (not a full YAML blob)?
Theme anchors and aliases are document-scoped — they are defined **per-page** inside `page.properties.theme`. Each page's anchors are self-contained. Per-page storage:
- Enables independent autosave per page
- Allows page-level version history (future)
- Cleaner CRUD (load/save one page at a time)
- Consistent with how the editor works (one page loaded at a time)

### Why store complete renderable YAML (with site wrapper) per page?
- Each page is independently renderable — just `yaml.safe_load()` + `render_yaml_structure()`
- YAML anchors work correctly (document-scoped, all within the page's YAML)
- No need to reconstruct the site wrapper at render time
- The site wrapper is tiny (~3 lines of YAML), so duplication cost is negligible

### Why `is_homepage` flag instead of just sort_order=0?
- Explicit intent — renaming or reordering doesn't accidentally change the homepage
- Published site root redirect (`/s/my-store` → `/s/my-store/home`) uses `is_homepage=True`

### Why pre-rendered HTML (not on-demand)?
Performance (single DB read), reliability (frozen at publish time), simplicity.

### Why SQLite?
Zero setup, file-based, SQLAlchemy abstracts dialect for future PostgreSQL switch.

### URL scheme: Subdomain primary + path fallback

Published sites use subdomain routing as the primary production URL (`my-store.swiftsites.com`). Path-based fallback (`/s/my-store`) is available for local development where DNS wildcards aren't available.

**Why subdomains?**
- Each site gets its own origin — complete CSS/JS isolation between published sites
- Cleaner URLs for visitors (`my-store.swiftsites.com/about` vs `swiftsites.com/s/my-store/about`)
- Natural stepping stone to custom domains in the future
- Cookie isolation — each subdomain has its own cookie scope

**Why path fallback for local dev?**
- `localhost` doesn't support wildcard subdomains without `/etc/hosts` hacking
- `my-store.localhost:5000` doesn't resolve by default on most systems
- Path-based (`localhost:5000/s/my-store`) works out of the box with zero setup

**Mode detection:** The server checks the `Host` header against `PLATFORM_DOMAIN` config. If the host is a subdomain of the platform domain, subdomain mode is used. Otherwise, path-based routing applies.

### Published slug uniqueness — Global constraint at publish time

Site slugs are unique **per organization** in the database (`uq_org_site_slug`), so two orgs can both have a site named `my-store` during editing. But a published slug becomes a subdomain (`my-store.swiftsites.com`), which requires **global uniqueness among published sites**.

**Resolution:** The publish endpoint enforces global uniqueness at publish time:

```python
@site_bp.route('/api/sites/<site_id>/publish', methods=['POST'])
@require_auth
@require_role('editor')
def publish_site(site_id):
    site = get_site_or_404(site_id)

    # Check for slug collision with OTHER published sites (from any org)
    conflict = Site.query.filter(
        Site.slug == site.slug,
        Site.status == 'published',
        Site.id != site.id           # Exclude self (re-publish case)
    ).first()

    if conflict:
        return jsonify({
            'error': f'The subdomain "{site.slug}.swiftsites.com" is already taken by '
                     f'another published site. Please change your site slug and try again.'
        }), 409  # Conflict

    # ... proceed with publish
```

**Slug validation rules** (enforced at site creation and slug update):
- Lowercase alphanumeric + hyphens only (valid subdomain characters)
- 3–63 characters (DNS subdomain limits)
- Cannot start or end with a hyphen
- Reserved slugs blocked: `www`, `api`, `app`, `admin`, `mail`, `ftp`, `cdn`, `static`

```python
import re

RESERVED_SLUGS = {'www', 'api', 'app', 'admin', 'mail', 'ftp', 'cdn', 'static',
                  'blog', 'help', 'docs', 'status', 'login', 'signup', 'dashboard'}

def validate_site_slug(slug):
    """Validate slug is a valid subdomain label."""
    if not re.match(r'^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$', slug):
        return False, 'Slug must be 3-63 lowercase letters, numbers, or hyphens. Cannot start/end with a hyphen.'
    if slug in RESERVED_SLUGS:
        return False, f'"{slug}" is reserved. Please choose a different slug.'
    return True, None
```

**Why this approach works:**
- During editing, slugs are org-scoped — no friction for editors
- At publish time, the first org to claim a slug gets the subdomain
- If a conflict exists, the user is told to change their slug before publishing
- When a site is unpublished, its slug (subdomain) becomes available again
- Slug validation ensures DNS compatibility — the slug IS the subdomain label

---

## Image Persistence Strategy: CDN During Dev, Save on Publish

### Approach

Stock photos use CDN URLs throughout development. Images are only downloaded and saved locally **at publish time**. User-uploaded files go to server immediately (blob URLs are ephemeral).

**Key benefits:**
- Zero storage waste — only published images are saved
- Simpler dev workflow — no library management UI
- Faster stock selection — instant CDN reference
- No orphaned images

### How It Works

```
DURING DEVELOPMENT:
  Stock photos → CDN URLs in YAML (https://images.pexels.com/...)
  Uploaded files → Server upload → /uploads/UUID.ext in YAML

AT PUBLISH TIME:
  1. Render each page to HTML
  2. Scan HTML for external image URLs
  3. Download, validate, save to instance/uploads/
  4. Replace CDN URLs with /uploads/UUID.ext in rendered HTML
  5. Store final HTML (all-local URLs) in published_pages table
```

**Source YAML is NOT modified** — CDN URLs stay in YAML, only published HTML gets local paths.

### Validation & Security

- Upload: MIME type whitelist (jpeg, png, gif, webp, svg), max 10MB, UUID filenames
- Publish download: Only from known domains, validate content-type
- Serve route: Validates filename matches `<uuid-hex>.<ext>` pattern

---

## WebP Conversion for All Stored Images

All images stored on the server are converted to WebP format before saving. This applies to:

1. **User uploads** (`POST /api/images/upload`) — convert on upload
2. **CDN downloads at publish time** (`localize_images_in_html()`) — convert after download

**Why WebP?**
- 25-35% smaller than JPEG at equivalent quality
- Supports transparency (replaces PNG)
- Supports animation (replaces GIF)
- Universal browser support (all modern browsers since 2020)

**Conversion logic:**
```python
from PIL import Image
import io

def convert_to_webp(image_bytes, quality=85):
    """Convert any image to WebP format. Returns (webp_bytes, width, height)."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')
    output = io.BytesIO()
    img.save(output, format='webp', quality=quality)
    return output.getvalue(), img.width, img.height
```

**Exception: SVG files** — SVGs are vector format and should NOT be converted. They are stored as-is.

**Impact on `SiteImage` model:**
- `mime_type` will always be `image/webp` (except SVGs which stay `image/svg+xml`)
- `filename` will always end in `.webp` (except SVGs)
- `original_name` preserves the original filename for reference

---

## Form Submission Security — Anti-Bot Design

### Goal

Forms on published pages can ONLY be submitted through actual browser interaction. Direct `curl`/bot POST requests are rejected.

### 5-Layer Protection

```
Layer 1: JS-Only Submission     → Blocks bots that don't execute JavaScript
Layer 2: Form Token             → Blocks bots that don't fetch the actual page
Layer 3: HMAC Challenge         → Blocks bots that can't compute the challenge
Layer 4: Time-Based Validation  → Blocks bots that submit instantly
Layer 5: Honeypot + Rate Limit  → Catches remaining automated submissions
```

---

### Layer 1: JavaScript-Only Submission

Published forms submit via `fetch()`, NOT via standard `<form action="...">` POST.

```html
<!-- Published form HTML (rendered at publish time) -->
<!-- data-form-action uses relative path — works on both subdomain and path mode -->
<form id="form_contact" data-form-token="abc123" data-form-action="/forms/contact/submit">
    <input type="text" name="name" required>
    <input type="email" name="email" required>
    <textarea name="message"></textarea>

    <!-- Honeypot: hidden from humans, visible to bots -->
    <div style="position:absolute;left:-9999px;" aria-hidden="true">
        <input type="text" name="_website" tabindex="-1" autocomplete="off">
    </div>

    <button type="submit">Send</button>
</form>

<script>
(function() {
    const form = document.getElementById('form_contact');
    const pageLoadTs = Date.now();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const token = form.dataset.formToken;
        const challenge = await computeChallenge(token, pageLoadTs);

        formData.append('_form_token', token);
        formData.append('_page_load_ts', pageLoadTs);
        formData.append('_challenge', challenge);

        const resp = await fetch(form.dataset.formAction, {
            method: 'POST',
            body: formData
        });

        if (resp.ok) {
            form.innerHTML = '<p>Thank you! Your message has been sent.</p>';
        } else {
            alert('Submission failed. Please try again.');
        }
    });

    async function computeChallenge(token, ts) {
        // HMAC-SHA256 using Web Crypto API (available in all modern browsers)
        const key = await crypto.subtle.importKey(
            'raw',
            new TextEncoder().encode(token),
            { name: 'HMAC', hash: 'SHA-256' },
            false, ['sign']
        );
        const sig = await crypto.subtle.sign(
            'HMAC', key,
            new TextEncoder().encode(token + ':' + ts)
        );
        return Array.from(new Uint8Array(sig))
            .map(b => b.toString(16).padStart(2, '0')).join('');
    }
})();
</script>
```

**Why this blocks bots:**
- `<form>` has NO `action` attribute — standard HTML submission goes nowhere
- `data-form-action` is only read by JavaScript
- `fetch()` requires JavaScript execution
- Web Crypto API required for HMAC challenge — simple script bots can't compute it

---

### Layer 2: Form Token (Server-Generated)

At **publish time**, a unique form token is generated per form per site and embedded in the HTML:

```python
import hmac, hashlib, secrets

# During publish, generate a per-site secret (stored in DB)
site.form_secret = secrets.token_hex(32)  # 64-char hex string

# For each form, derive a token
form_token = hmac.new(
    site.form_secret.encode(),
    f'{site.slug}:{form_name}'.encode(),
    hashlib.sha256
).hexdigest()[:32]  # 32-char token embedded in HTML
```

**Server validates:** The submitted `_form_token` must match the expected token derived from the site's secret.

---

### Layer 3: HMAC Challenge

The client computes `HMAC-SHA256(form_token, form_token + ":" + page_load_timestamp)` using Web Crypto API. Server recomputes and compares.

**Why this works:**
- Even if a bot extracts the `form_token` from HTML, it needs to run the JS to compute the challenge
- The challenge changes with every page load (`pageLoadTs` is dynamic)
- Bots that just scrape HTML and POST can't produce valid challenges

---

### Layer 4: Time-Based Validation

Server checks `_page_load_ts`:
- **Minimum time:** 3 seconds between page load and submission (humans can't fill a form in <3s)
- **Maximum time:** 24 hours (token expires after a day)
- **Current time check:** `_page_load_ts` must be in the past, not the future

```python
now = int(time.time() * 1000)  # milliseconds
elapsed = now - int(page_load_ts)

if elapsed < 3000:        # Less than 3 seconds
    return 403             # Too fast — likely a bot
if elapsed > 86400000:     # More than 24 hours
    return 403             # Token expired
if int(page_load_ts) > now:
    return 403             # Timestamp in the future — tampered
```

---

### Layer 5: Honeypot + Rate Limiting

**Honeypot:** A hidden field named `_website` that's invisible to humans but filled by bots. If it has any value, reject silently.

**Rate limiting:** Max 10 submissions per IP per minute per site. Tracked in-memory (or Redis later).

```python
from collections import defaultdict
import time

# Simple in-memory rate limiter
rate_limits = defaultdict(list)  # key: f'{ip}:{site_id}'

def check_rate_limit(ip, site_id, max_per_minute=10):
    key = f'{ip}:{site_id}'
    now = time.time()
    # Remove entries older than 60 seconds
    rate_limits[key] = [t for t in rate_limits[key] if now - t < 60]
    if len(rate_limits[key]) >= max_per_minute:
        return False  # Rate limited
    rate_limits[key].append(now)
    return True
```

---

### Server-Side Validation (Complete Flow)

```python
@published_bp.route('/s/<site_slug>/forms/<form_name>/submit', methods=['POST'])
def submit_form(site_slug, form_name):
    site = Site.query.filter_by(slug=site_slug, status='published').first_or_404()

    # Layer 5: Rate limiting
    if not check_rate_limit(request.remote_addr, site.id):
        return jsonify({'error': 'Too many submissions'}), 429

    # Layer 5: Honeypot
    if request.form.get('_website', ''):
        # Silently accept but mark as spam (don't reveal detection)
        save_submission(site, form_name, request.form, is_spam=True)
        return jsonify({'ok': True}), 200

    # Layer 2: Form token
    form_token = request.form.get('_form_token', '')
    expected_token = derive_form_token(site.form_secret, site.slug, form_name)
    if not hmac.compare_digest(form_token, expected_token):
        return jsonify({'error': 'Invalid submission'}), 403

    # Layer 4: Time validation
    page_load_ts = request.form.get('_page_load_ts', '')
    try:
        ts = int(page_load_ts)
        now = int(time.time() * 1000)
        elapsed = now - ts
        if elapsed < 3000 or elapsed > 86400000 or ts > now:
            return jsonify({'error': 'Invalid submission'}), 403
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid submission'}), 403

    # Layer 3: HMAC challenge
    challenge = request.form.get('_challenge', '')
    expected_challenge = hmac.new(
        form_token.encode(),
        f'{form_token}:{page_load_ts}'.encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(challenge, expected_challenge):
        return jsonify({'error': 'Invalid submission'}), 403

    # All checks passed — save submission
    save_submission(site, form_name, request.form, is_spam=False)
    return jsonify({'ok': True}), 200
```

---

### What Each Layer Blocks

| Attack Type | L1 JS-Only | L2 Token | L3 HMAC | L4 Time | L5 Honeypot/Rate |
|-------------|:----------:|:--------:|:-------:|:-------:|:----------------:|
| curl/wget POST | X | X | X | | |
| Simple spam bot | X | X | X | | X |
| Bot that reads HTML | | | X | X | |
| Bot that runs basic JS | | | X | X | |
| Bot with full browser (headless) | | | | X | X |
| Brute force flood | | | | | X |

No single layer is unbreakable, but **combined** they block 99%+ of automated submissions. For the remaining edge cases (sophisticated headless browser bots), optional CAPTCHA (Cloudflare Turnstile) can be added as a future enhancement.

---

### Schema Addition: `form_secret` on Sites

```python
class Site(db.Model):
    ...
    form_secret   = db.Column(db.String(64), nullable=True)  # Generated at first publish
```

- Generated once at first publish, persists across re-publishes
- Used to derive per-form tokens via HMAC
- If compromised, regenerate by re-publishing (generates new secret + tokens)

---

## Published Site Routing — Infrastructure & Config

### Config Changes

```python
# config.py

class Config:
    # ...existing config...

    # Published site routing
    PLATFORM_DOMAIN = 'swiftsites.com'           # Production: subdomain parent domain
    PUBLISHED_MODE = 'auto'                       # 'subdomain', 'path', or 'auto'
    # 'auto' = subdomain if Host matches *.PLATFORM_DOMAIN, else path fallback

class DevelopmentConfig(Config):
    PLATFORM_DOMAIN = 'localhost'                 # No subdomain support on localhost
    PUBLISHED_MODE = 'path'                       # Force path-based in local dev

class ProductionConfig(Config):
    PLATFORM_DOMAIN = os.environ.get('PLATFORM_DOMAIN', 'swiftsites.com')
    PUBLISHED_MODE = 'auto'
    SERVER_NAME = os.environ.get('SERVER_NAME')   # Required for Flask subdomain routing
```

### Local Development (Path Mode)

No special setup needed. Published sites are accessed via `localhost:5000/s/my-store/about`.

### Production (Subdomain Mode)

**DNS:** Wildcard A record pointing all subdomains to the server:
```
*.swiftsites.com.  A  <server-ip>
swiftsites.com.    A  <server-ip>
```

**SSL/TLS:** Wildcard certificate for `*.swiftsites.com` (Let's Encrypt supports wildcard via DNS-01 challenge).

**Nginx (reverse proxy):**
```nginx
# Catch-all for published site subdomains
server {
    listen 443 ssl;
    server_name *.swiftsites.com;

    ssl_certificate     /etc/ssl/wildcard.swiftsites.com.pem;
    ssl_certificate_key /etc/ssl/wildcard.swiftsites.com.key;

    # Serve uploaded images directly (bypass Flask)
    location /uploads/ {
        alias /path/to/ssr_python/instance/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Main app (editor) on root domain
server {
    listen 443 ssl;
    server_name swiftsites.com;

    # ... same SSL + proxy config, serves the editor UI
}
```

### Flask `SERVER_NAME` Consideration

Flask's `SERVER_NAME` config enables subdomain-based routing but has a side effect: it restricts the app to only accept requests matching that domain. For production, set:
```
SERVER_NAME=swiftsites.com
```

For local dev, do NOT set `SERVER_NAME` — it would break `localhost` access. The `PUBLISHED_MODE = 'path'` setting in `DevelopmentConfig` ensures path-based routing is used instead.

### Future: Custom Domains

A future enhancement can allow users to map their own domain (e.g., `www.mybakery.com`) to their published site. This would require:
- A `custom_domain` column on the `sites` table
- DNS CNAME verification (`www.mybakery.com → CNAME → my-store.swiftsites.com`)
- Per-domain SSL certificates (via Let's Encrypt HTTP-01 challenge)
- Nginx config generation or a catch-all that queries the DB for domain → site mapping

This is out of scope for the current phases but the subdomain architecture is a natural stepping stone — the resolution logic already extracts site slugs from the `Host` header.

---

## Dependencies

```
# Add to requirements.txt
flask-sqlalchemy>=3.1.0,<4.0
Pillow>=10.0.0,<11.0
```

No other new dependencies needed. SQLite is built into Python. The `requests` library (already in requirements.txt) handles stock photo downloads at publish time. Pillow is used for WebP image conversion.
