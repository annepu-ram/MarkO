"""
Site & Page CRUD API — All endpoints org-scoped via guards.

Pre-auth stub: g.current_org_id and g.current_role are set by @before_request
until real auth is implemented in Phase 7.
"""
import secrets
from datetime import datetime
from flask import Blueprint, current_app, g, jsonify, request, abort
from extensions import db, TOKENS, COMPONENT_DEFAULTS
from models import (
    Organization, Site, SitePage, SiteSharedBlock, PageSharedBlockOverride,
    PublishedPage, SectionItem, SiteVersion, SiteVersionPage, SiteVersionSharedBlock,
)
from guards import (
    get_site_or_404, get_page_or_404, get_version_or_404,
    validate_site_slug, generate_default_page_yaml, generate_page_yaml_from_homepage,
    site_has_unpublished_changes, require_role,
    validate_site_settings,
)
from renderer import render_yaml_structure
from site_composer import compose_page_yaml, dump_composed_yaml, CompositionError
import uuid
import yaml

site_bp = Blueprint('site', __name__)

ALLOWED_SHARED_BLOCK_KEYS = {'announcement_bar', 'header', 'footer'}
ALLOWED_OVERRIDE_MODES = {'inherit', 'hidden', 'custom'}


def _serialize_shared_block(block):
    return {
        'id': block.id,
        'site_id': block.site_id,
        'key': block.key,
        'label': block.label,
        'yaml_content': block.yaml_content,
        'enabled': block.enabled,
        'sort_order': block.sort_order,
        'updated_at': block.updated_at.isoformat() if block.updated_at else None,
    }


def _serialize_override(override):
    return {
        'id': override.id,
        'page_id': override.page_id,
        'block_key': override.block_key,
        'mode': override.mode,
        'custom_yaml_content': override.custom_yaml_content,
        'updated_at': override.updated_at.isoformat() if override.updated_at else None,
    }


def _validate_component_list_yaml(yaml_content, field_name='yaml_content'):
    try:
        parsed = yaml.safe_load(yaml_content or '[]')
    except yaml.YAMLError as exc:
        return False, f'{field_name} is not valid YAML: {exc}'
    if parsed is None:
        parsed = []
    if not isinstance(parsed, list):
        return False, f'{field_name} must be a YAML list of components.'
    return True, None


def _parse_component_list_yaml(yaml_content, field_name='yaml_content'):
    try:
        parsed = yaml.safe_load(yaml_content or '[]')
    except yaml.YAMLError as exc:
        raise ValueError(f'{field_name} is not valid YAML: {exc}') from exc
    if parsed is None:
        return []
    if not isinstance(parsed, list):
        raise ValueError(f'{field_name} must be a YAML list of components.')
    return parsed


# =============================================================================
# Pre-Auth Stub (Phases 2-5) — replaced by @require_auth in Phase 7
# =============================================================================

@site_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'  # Full access during development


# =============================================================================
# Utility: UUID generation (used by pageManager.js)
# =============================================================================

@site_bp.route('/api/site/generate-id')
def generate_site_id():
    """Generate a UUID v4 for a new site."""
    return jsonify({'id': str(uuid.uuid4())})


# =============================================================================
# Site-Level CRUD
# =============================================================================

@site_bp.route('/api/sites', methods=['GET'])
def list_sites():
    """List all sites for the current organization with section classification."""
    sites = Site.query.filter_by(org_id=g.current_org_id).order_by(Site.updated_at.desc()).all()
    result = []
    for s in sites:
        has_changes = site_has_unpublished_changes(s)

        if s.status == 'draft' or s.published_at is None:
            sections = ['development']
        elif has_changes:
            sections = ['development', 'published']
        else:
            sections = ['published']

        version_count = SiteVersion.query.filter_by(site_id=s.id).count()

        result.append({
            'id': s.id,
            'brand_id': s.brand_id,
            'name': s.name,
            'slug': s.slug,
            'status': s.status,
            'sections': sections,
            'current_version': s.current_version,
            'version_count': version_count,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None,
            'published_at': s.published_at.isoformat() if s.published_at else None,
            'page_count': len(s.source_pages),
            'has_settings': bool(s.settings),
        })
    return jsonify(result)


@site_bp.route('/api/sites', methods=['POST'])
def create_site():
    """Create a new site with a default homepage.

    Request JSON: { name: str, slug: str }
    Response: { id, name, slug, pages: [{id, slug, title, yaml_content}] }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip().lower()

    if not name:
        return jsonify({'error': 'Site name is required.'}), 400

    valid, error = validate_site_slug(slug)
    if not valid:
        return jsonify({'error': error}), 400

    # Check slug uniqueness within org
    existing = Site.query.filter_by(org_id=g.current_org_id, slug=slug).first()
    if existing:
        return jsonify({'error': f'A site with slug "{slug}" already exists in your organization.'}), 409

    # Create site
    site = Site(
        org_id=g.current_org_id,
        name=name,
        slug=slug,
    )
    db.session.add(site)
    db.session.flush()  # Get site.id before creating page

    # Create default homepage
    yaml_content = generate_default_page_yaml(
        slug='home',
        title=name,
    )
    homepage = SitePage(
        site_id=site.id,
        slug='home',
        title=name,
        yaml_content=yaml_content,
        sort_order=0,
        is_homepage=True,
    )
    db.session.add(homepage)
    db.session.commit()

    return jsonify({
        'id': site.id,
        'brand_id': site.brand_id,
        'name': site.name,
        'slug': site.slug,
        'pages': [{
            'id': homepage.id,
            'slug': homepage.slug,
            'title': homepage.title,
            'yaml_content': homepage.yaml_content,
            'sort_order': homepage.sort_order,
            'is_homepage': homepage.is_homepage,
        }],
    }), 201


@site_bp.route('/api/sites/<site_id>', methods=['GET'])
def get_site(site_id):
    """Load site metadata + page list (not YAML content).

    Response: { id, name, slug, status, pages: [{id, slug, title, sort_order, is_homepage}] }
    """
    site = get_site_or_404(site_id)
    pages = SitePage.query.filter_by(site_id=site.id).order_by(SitePage.sort_order).all()

    return jsonify({
        'id': site.id,
        'name': site.name,
        'slug': site.slug,
        'status': site.status,
        'settings': site.get_settings(),
        'updated_at': site.updated_at.isoformat() if site.updated_at else None,
        'published_at': site.published_at.isoformat() if site.published_at else None,
        'pages': [
            {
                'id': p.id,
                'slug': p.slug,
                'title': p.title,
                'sort_order': p.sort_order,
                'is_homepage': p.is_homepage,
            }
            for p in pages
        ],
    })


@site_bp.route('/api/sites/<site_id>', methods=['PATCH'])
def update_site(site_id):
    """Update site metadata (name, slug).

    Request JSON: { name?, slug? }
    Response: { ok: true }
    """
    site = get_site_or_404(site_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return jsonify({'error': 'Site name cannot be empty.'}), 400
        site.name = name

    if 'slug' in data:
        new_slug = (data['slug'] or '').strip().lower()
        valid, error = validate_site_slug(new_slug)
        if not valid:
            return jsonify({'error': error}), 400
        # Check uniqueness within org (excluding self)
        existing = Site.query.filter(
            Site.org_id == g.current_org_id,
            Site.slug == new_slug,
            Site.id != site.id,
        ).first()
        if existing:
            return jsonify({'error': f'A site with slug "{new_slug}" already exists.'}), 409
        site.slug = new_slug

    db.session.commit()
    return jsonify({'ok': True})


@site_bp.route('/api/sites/<site_id>', methods=['DELETE'])
def delete_site(site_id):
    """Delete site + cascade (pages, published pages, images, submissions).

    Response: { ok: true }
    """
    site = get_site_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Page-Level CRUD
# =============================================================================

@site_bp.route('/api/sites/<site_id>/pages', methods=['GET'])
def list_pages(site_id):
    """List all source pages for a site.

    Response: [{ id, slug, title, sort_order, is_homepage }]
    """
    site = get_site_or_404(site_id)
    pages = SitePage.query.filter_by(site_id=site.id).order_by(SitePage.sort_order).all()
    return jsonify([
        {
            'id': p.id,
            'slug': p.slug,
            'title': p.title,
            'sort_order': p.sort_order,
            'is_homepage': p.is_homepage,
        }
        for p in pages
    ])


@site_bp.route('/api/sites/<site_id>/pages', methods=['POST'])
def create_page(site_id):
    """Create a new page with default YAML.

    Request JSON: { title: str, slug: str }
    Response: { id, slug, title, yaml_content, sort_order, is_homepage }
    """
    site = get_site_or_404(site_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    title = (data.get('title') or '').strip()
    slug = (data.get('slug') or '').strip().lower()

    if not title:
        return jsonify({'error': 'Page title is required.'}), 400
    if not slug:
        return jsonify({'error': 'Page slug is required.'}), 400

    # Check slug uniqueness within site
    existing = SitePage.query.filter_by(site_id=site.id, slug=slug).first()
    if existing:
        return jsonify({'error': f'A page with slug "{slug}" already exists in this site.'}), 409

    # Determine sort order (append at end)
    max_order = db.session.query(db.func.max(SitePage.sort_order)).filter_by(site_id=site.id).scalar() or 0
    sort_order = max_order + 1

    # Copy theme + titlebar from homepage if available
    homepage = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
    if homepage and homepage.yaml_content:
        yaml_content = generate_page_yaml_from_homepage(
            homepage.yaml_content, slug=slug, title=title
        )
    else:
        yaml_content = generate_default_page_yaml(slug=slug, title=title)

    page = SitePage(
        site_id=site.id,
        slug=slug,
        title=title,
        yaml_content=yaml_content,
        sort_order=sort_order,
        is_homepage=False,
    )
    db.session.add(page)
    db.session.commit()

    return jsonify({
        'id': page.id,
        'slug': page.slug,
        'title': page.title,
        'yaml_content': page.yaml_content,
        'sort_order': page.sort_order,
        'is_homepage': page.is_homepage,
    }), 201


@site_bp.route('/api/sites/<site_id>/pages/<page_id>', methods=['GET'])
def get_page(site_id, page_id):
    """Load a page's YAML content for editing.

    Response: { id, slug, title, yaml_content, sort_order, is_homepage }
    """
    site, page = get_page_or_404(site_id, page_id)
    return jsonify({
        'id': page.id,
        'slug': page.slug,
        'title': page.title,
        'yaml_content': page.yaml_content,
        'sort_order': page.sort_order,
        'is_homepage': page.is_homepage,
    })


@site_bp.route('/api/sites/<site_id>/pages/<page_id>', methods=['PUT'])
def save_page(site_id, page_id):
    """Autosave page YAML content.

    Request JSON: { yaml_content: str }
    Response: { ok: true, updated_at: str }
    """
    site, page = get_page_or_404(site_id, page_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    yaml_content = data.get('yaml_content')
    if yaml_content is None:
        return jsonify({'error': 'yaml_content is required.'}), 400

    page.yaml_content = yaml_content
    page.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'ok': True,
        'updated_at': page.updated_at.isoformat(),
    })


@site_bp.route('/api/sites/<site_id>/pages/<page_id>/sections', methods=['POST'])
@require_role('editor')
def append_section_to_page(site_id, page_id):
    """Append a YAML-backed SectionItem to a page body."""
    site, page = get_page_or_404(site_id, page_id)
    data = request.get_json(silent=True) or {}
    section_id = (data.get('section_id') or '').strip()
    if not section_id:
        return jsonify({'error': 'section_id is required.'}), 400

    section = SectionItem.query.filter_by(id=section_id, org_id=g.current_org_id).first()
    if not section:
        abort(404)
    if section.brand_id and getattr(site, 'brand_id', None) and section.brand_id != site.brand_id:
        return jsonify({'error': 'Section brand does not match this site.'}), 400
    if not section.yaml_content:
        return jsonify({'error': 'Section does not have yaml_content. Regenerate section YAML first.'}), 400

    try:
        existing = _parse_component_list_yaml(page.body_yaml_content or '[]', 'body_yaml_content')
        section_components = _parse_component_list_yaml(section.yaml_content, 'section yaml_content')
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    page.body_yaml_content = yaml.dump(
        existing + section_components,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    page.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'ok': True,
        'page_id': page.id,
        'section_id': section.id,
        'body_yaml_content': page.body_yaml_content,
        'updated_at': page.updated_at.isoformat(),
    })


@site_bp.route('/api/sites/<site_id>/pages/<page_id>', methods=['PATCH'])
def update_page(site_id, page_id):
    """Update page metadata (title, slug, sort_order).

    Request JSON: { title?, slug?, sort_order? }
    Response: { ok: true }
    """
    site, page = get_page_or_404(site_id, page_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if 'title' in data:
        title = (data['title'] or '').strip()
        if not title:
            return jsonify({'error': 'Page title cannot be empty.'}), 400
        page.title = title

    if 'slug' in data:
        new_slug = (data['slug'] or '').strip().lower()
        if not new_slug:
            return jsonify({'error': 'Page slug cannot be empty.'}), 400
        # Check uniqueness within site (excluding self)
        existing = SitePage.query.filter(
            SitePage.site_id == site.id,
            SitePage.slug == new_slug,
            SitePage.id != page.id,
        ).first()
        if existing:
            return jsonify({'error': f'A page with slug "{new_slug}" already exists in this site.'}), 409
        page.slug = new_slug

    if 'sort_order' in data:
        page.sort_order = int(data['sort_order'])

    db.session.commit()
    return jsonify({'ok': True})


@site_bp.route('/api/sites/<site_id>/pages/<page_id>', methods=['DELETE'])
def delete_page(site_id, page_id):
    """Delete a page from the site.

    Response: { ok: true }
    """
    site, page = get_page_or_404(site_id, page_id)

    # Prevent deleting the last page
    page_count = SitePage.query.filter_by(site_id=site.id).count()
    if page_count <= 1:
        return jsonify({'error': 'Cannot delete the last page. A site must have at least one page.'}), 400

    db.session.delete(page)
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Site Shared Blocks & Page Overrides
# =============================================================================

@site_bp.route('/api/sites/<site_id>/shared-blocks', methods=['GET'])
def list_shared_blocks(site_id):
    """List shared component blocks for a site."""
    site = get_site_or_404(site_id)
    blocks = SiteSharedBlock.query.filter_by(site_id=site.id) \
        .order_by(SiteSharedBlock.sort_order, SiteSharedBlock.key).all()
    return jsonify([_serialize_shared_block(block) for block in blocks])


@site_bp.route('/api/sites/<site_id>/shared-blocks', methods=['POST'])
@require_role('editor')
def create_shared_block(site_id):
    """Create a shared site block such as header/footer."""
    site = get_site_or_404(site_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    key = (data.get('key') or '').strip()
    if key not in ALLOWED_SHARED_BLOCK_KEYS:
        return jsonify({'error': f'Invalid shared block key "{key}".'}), 400

    existing = SiteSharedBlock.query.filter_by(site_id=site.id, key=key).first()
    if existing:
        return jsonify({'error': f'Shared block "{key}" already exists.'}), 409

    yaml_content = data.get('yaml_content', '[]')
    valid, error = _validate_component_list_yaml(yaml_content)
    if not valid:
        return jsonify({'error': error}), 400

    block = SiteSharedBlock(
        site_id=site.id,
        key=key,
        label=(data.get('label') or key.replace('_', ' ').title()).strip(),
        yaml_content=yaml_content,
        enabled=bool(data.get('enabled', True)),
        sort_order=int(data.get('sort_order') or 0),
    )
    db.session.add(block)
    site.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_shared_block(block)), 201


@site_bp.route('/api/sites/<site_id>/shared-blocks/<key>', methods=['PUT'])
@require_role('editor')
def upsert_shared_block(site_id, key):
    """Create or replace a site's shared block."""
    site = get_site_or_404(site_id)
    key = (key or '').strip()
    if key not in ALLOWED_SHARED_BLOCK_KEYS:
        return jsonify({'error': f'Invalid shared block key "{key}".'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    yaml_content = data.get('yaml_content', '[]')
    valid, error = _validate_component_list_yaml(yaml_content)
    if not valid:
        return jsonify({'error': error}), 400

    block = SiteSharedBlock.query.filter_by(site_id=site.id, key=key).first()
    created = block is None
    if block is None:
        block = SiteSharedBlock(site_id=site.id, key=key)
        db.session.add(block)

    block.label = (data.get('label') or key.replace('_', ' ').title()).strip()
    block.yaml_content = yaml_content
    block.enabled = bool(data.get('enabled', True))
    block.sort_order = int(data.get('sort_order') or 0)
    block.updated_at = datetime.utcnow()
    site.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_shared_block(block)), 201 if created else 200


@site_bp.route('/api/sites/<site_id>/shared-blocks/<key>', methods=['DELETE'])
@require_role('editor')
def delete_shared_block(site_id, key):
    """Delete a shared block."""
    site = get_site_or_404(site_id)
    block = SiteSharedBlock.query.filter_by(site_id=site.id, key=key).first()
    if not block:
        return jsonify({'error': 'Shared block not found.'}), 404
    db.session.delete(block)
    site.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


@site_bp.route('/api/sites/<site_id>/pages/<page_id>/shared-block-overrides', methods=['GET'])
def list_shared_block_overrides(site_id, page_id):
    """List shared block overrides for a page."""
    site, page = get_page_or_404(site_id, page_id)
    overrides = PageSharedBlockOverride.query.filter_by(page_id=page.id).all()
    return jsonify([_serialize_override(override) for override in overrides])


@site_bp.route('/api/sites/<site_id>/pages/<page_id>/shared-block-overrides/<key>', methods=['PUT'])
@require_role('editor')
def upsert_shared_block_override(site_id, page_id, key):
    """Create or replace a page-level shared block override."""
    site, page = get_page_or_404(site_id, page_id)
    key = (key or '').strip()
    if key not in ALLOWED_SHARED_BLOCK_KEYS:
        return jsonify({'error': f'Invalid shared block key "{key}".'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    mode = (data.get('mode') or 'inherit').strip()
    if mode not in ALLOWED_OVERRIDE_MODES:
        return jsonify({'error': f'Invalid override mode "{mode}".'}), 400

    custom_yaml_content = data.get('custom_yaml_content')
    if mode == 'custom':
        valid, error = _validate_component_list_yaml(custom_yaml_content or '[]', 'custom_yaml_content')
        if not valid:
            return jsonify({'error': error}), 400

    override = PageSharedBlockOverride.query.filter_by(page_id=page.id, block_key=key).first()
    created = override is None
    if override is None:
        override = PageSharedBlockOverride(page_id=page.id, block_key=key)
        db.session.add(override)

    override.mode = mode
    override.custom_yaml_content = custom_yaml_content if mode == 'custom' else None
    override.updated_at = datetime.utcnow()
    page.updated_at = datetime.utcnow()
    site.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_override(override)), 201 if created else 200


@site_bp.route('/api/sites/<site_id>/pages/<page_id>/composed-yaml', methods=['GET'])
def get_composed_page_yaml(site_id, page_id):
    """Return composed renderer-compatible YAML for debugging."""
    site, page = get_page_or_404(site_id, page_id)
    try:
        return current_app.response_class(
            dump_composed_yaml(site, page),
            mimetype='application/x-yaml',
        )
    except CompositionError as exc:
        return jsonify({'error': str(exc)}), 400


@site_bp.route('/api/sites/<site_id>/pages/<page_id>/render', methods=['POST'])
def render_composed_page(site_id, page_id):
    """Render a page through the site composer.

    Optional JSON body: { body_yaml_content: str } for unsaved preview drafts.
    """
    site, page = get_page_or_404(site_id, page_id)
    data = request.get_json(silent=True) or {}
    original_body = page.body_yaml_content
    if 'body_yaml_content' in data:
        page.body_yaml_content = data.get('body_yaml_content') or ''
    try:
        structure = compose_page_yaml(site, page)
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        return html, 200, {'Content-Type': 'text/html'}
    except CompositionError as exc:
        return jsonify({'error': str(exc)}), 400
    finally:
        page.body_yaml_content = original_body


# =============================================================================
# Publish / Unpublish
# =============================================================================

@site_bp.route('/api/sites/<site_id>/publish', methods=['POST'])
def publish_site(site_id):
    """Publish a site: render each page to HTML, store in published_pages.

    Checks global slug uniqueness (across all orgs) before publishing.
    Response: { ok, url, pages: [{slug, url}] }
    """
    site = get_site_or_404(site_id)

    # Global slug uniqueness check — published slugs become subdomains
    conflict = Site.query.filter(
        Site.slug == site.slug,
        Site.status == 'published',
        Site.id != site.id,
    ).first()
    if conflict:
        return jsonify({
            'error': f'The slug "{site.slug}" is already taken by another published site. '
                     f'Please change your site slug and try again.'
        }), 409

    # Generate form_secret on first publish
    if not site.form_secret:
        site.form_secret = secrets.token_hex(32)

    # Delete old published pages
    PublishedPage.query.filter_by(site_id=site.id).delete()

    # Render each source page
    source_pages = SitePage.query.filter_by(site_id=site.id).order_by(SitePage.sort_order).all()
    published_info = []

    for sp in source_pages:
        try:
            structure = compose_page_yaml(site, sp)
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        except Exception as e:
            current_app.logger.error(f'Publish error rendering page {sp.slug}: {e}')
            db.session.rollback()
            return jsonify({
                'error': f'Failed to render page "{sp.title}" ({sp.slug}). Fix YAML errors and try again.'
            }), 400

        published = PublishedPage(
            site_id=site.id,
            slug=sp.slug,
            title=sp.title,
            rendered_html=html,
            sort_order=sp.sort_order,
        )
        db.session.add(published)
        published_info.append({'slug': sp.slug, 'title': sp.title})

    # Create version snapshot
    max_version = db.session.query(db.func.max(SiteVersion.version_number)) \
        .filter_by(site_id=site.id).scalar() or 0
    version = SiteVersion(
        site_id=site.id,
        version_number=max_version + 1,
    )
    db.session.add(version)
    db.session.flush()

    shared_blocks = SiteSharedBlock.query.filter_by(site_id=site.id) \
        .order_by(SiteSharedBlock.sort_order, SiteSharedBlock.key).all()
    for block in shared_blocks:
        version_block = SiteVersionSharedBlock(
            version_id=version.id,
            key=block.key,
            label=block.label,
            yaml_content=block.yaml_content,
            enabled=block.enabled,
            sort_order=block.sort_order,
        )
        db.session.add(version_block)

    for sp in source_pages:
        vp = SiteVersionPage(
            version_id=version.id,
            slug=sp.slug,
            title=sp.title,
            yaml_content=sp.yaml_content,
            body_yaml_content=sp.body_yaml_content,
            sort_order=sp.sort_order,
            is_homepage=sp.is_homepage,
        )
        db.session.add(vp)

    site.status = 'published'
    site.current_version = version.version_number
    site.published_at = datetime.utcnow()
    db.session.commit()

    # Build response URLs
    mode = current_app.config.get('PUBLISHED_MODE', 'path')
    domain = current_app.config.get('PLATFORM_DOMAIN', 'localhost')
    if mode == 'path' or domain == 'localhost':
        base_url = f'/s/{site.slug}'
    else:
        base_url = f'https://{site.slug}.{domain}'

    return jsonify({
        'ok': True,
        'url': base_url,
        'pages': [
            {'slug': p['slug'], 'title': p['title'], 'url': f'{base_url}/{p["slug"]}'}
            for p in published_info
        ],
    })


@site_bp.route('/api/sites/<site_id>/unpublish', methods=['POST'])
def unpublish_site(site_id):
    """Unpublish a site: remove published pages, set status to draft.

    Response: { ok: true }
    """
    site = get_site_or_404(site_id)
    PublishedPage.query.filter_by(site_id=site.id).delete()
    site.status = 'draft'
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Version History
# =============================================================================

@site_bp.route('/api/sites/<site_id>/versions', methods=['GET'])
def list_versions(site_id):
    """List all published versions for a site (newest first)."""
    site = get_site_or_404(site_id)
    versions = SiteVersion.query.filter_by(site_id=site.id) \
        .order_by(SiteVersion.version_number.desc()).all()
    return jsonify([
        {
            'id': v.id,
            'version_number': v.version_number,
            'label': v.label,
            'published_at': v.published_at.isoformat() if v.published_at else None,
            'page_count': len(v.pages),
            'is_current': v.version_number == site.current_version,
        }
        for v in versions
    ])


@site_bp.route('/api/sites/<site_id>/versions/<version_id>/rollback', methods=['POST'])
@require_role('editor')
def rollback_version(site_id, version_id):
    """Rollback draft YAML to a specific version. Does NOT re-publish."""
    site, version = get_version_or_404(site_id, version_id)

    # Delete current source pages
    SitePage.query.filter_by(site_id=site.id).delete()
    SiteSharedBlock.query.filter_by(site_id=site.id).delete()

    for vb in version.shared_blocks:
        restored_block = SiteSharedBlock(
            site_id=site.id,
            key=vb.key,
            label=vb.label,
            yaml_content=vb.yaml_content,
            enabled=vb.enabled,
            sort_order=vb.sort_order,
        )
        db.session.add(restored_block)

    # Copy version pages into source_pages
    restored_pages = []
    for vp in version.pages:
        new_page = SitePage(
            site_id=site.id,
            slug=vp.slug,
            title=vp.title,
            yaml_content=vp.yaml_content,
            body_yaml_content=vp.body_yaml_content,
            sort_order=vp.sort_order,
            is_homepage=vp.is_homepage,
        )
        db.session.add(new_page)
        db.session.flush()
        restored_pages.append({
            'id': new_page.id,
            'slug': new_page.slug,
            'title': new_page.title,
        })

    site.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'ok': True,
        'restored_version': version.version_number,
        'pages': restored_pages,
    })


@site_bp.route('/api/sites/<site_id>/versions/<version_id>', methods=['PATCH'])
@require_role('editor')
def update_version_label(site_id, version_id):
    """Update a version's label."""
    site, version = get_version_or_404(site_id, version_id)
    data = request.get_json(silent=True)
    if data and 'label' in data:
        version.label = (data['label'] or '').strip()[:255]
        db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Site Settings (SEO, Branding, Social)
# =============================================================================

@site_bp.route('/api/sites/<site_id>/settings', methods=['GET'])
def get_site_settings(site_id):
    """Get site settings merged with defaults.

    Response: { seo: {...}, branding: {...}, social: {...} }
    """
    site = get_site_or_404(site_id)
    return jsonify(site.get_settings())


@site_bp.route('/api/sites/<site_id>/settings', methods=['PUT'])
@require_role('editor')
def update_site_settings(site_id):
    """Update site settings (partial or full).

    Request JSON: { seo?: {...}, branding?: {...}, social?: {...} }
    Response: { ok: true, settings: {...} }
    """
    site = get_site_or_404(site_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    valid, error = validate_site_settings(data)
    if not valid:
        return jsonify({'error': error}), 400

    # Merge with existing settings (preserve unmodified categories)
    current = site.get_settings()
    for category, values in data.items():
        if category in current:
            current[category].update(values)
        else:
            current[category] = values

    site.set_settings(current)
    db.session.commit()

    return jsonify({'ok': True, 'settings': site.get_settings()})
