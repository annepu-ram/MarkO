"""
Guards — IDOR protection helpers, role enforcement, slug validation, default YAML template.

All site/page queries MUST go through these helpers to enforce org-scoped access.
Before auth exists (Phases 2-5), g.current_org_id is set by a pre-auth stub in routes/site.py.
"""
import re
import yaml
from functools import wraps
from flask import g, abort
from extensions import db
from models import Site, SitePage, SiteSharedBlock, FormSubmission, SiteVersion, Campaign


# =============================================================================
# IDOR Guards — every site/page query must use these
# =============================================================================

def get_site_or_404(site_id):
    """Fetch a site and verify the current user's org owns it.
    Returns 404 (not 403) to avoid revealing that the site exists in another org."""
    site = Site.query.filter_by(id=site_id, org_id=g.current_org_id).first()
    if not site:
        abort(404)
    return site


def get_page_or_404(site_id, page_id):
    """Fetch a page through the site ownership chain."""
    site = get_site_or_404(site_id)
    page = SitePage.query.filter_by(id=page_id, site_id=site.id).first()
    if not page:
        abort(404)
    return site, page


def get_submission_or_404(site_id, submission_id):
    """Fetch a form submission through the site ownership chain."""
    site = get_site_or_404(site_id)
    submission = FormSubmission.query.filter_by(id=submission_id, site_id=site.id).first()
    if not submission:
        abort(404)
    return site, submission


def get_version_or_404(site_id, version_id):
    """Fetch a site version through the site ownership chain."""
    site = get_site_or_404(site_id)
    version = SiteVersion.query.filter_by(id=version_id, site_id=site.id).first()
    if not version:
        abort(404)
    return site, version


def get_campaign_or_404(campaign_id):
    """Fetch a campaign and verify org ownership."""
    campaign = Campaign.query.filter_by(id=campaign_id, org_id=g.current_org_id).first()
    if not campaign:
        abort(404)
    return campaign


def site_has_unpublished_changes(site):
    """Check if any SitePage was edited after the last publish.

    Returns True if the site has been published AND any page has been
    updated since the last publish timestamp."""
    if site.status != 'published' or not site.published_at:
        return False
    latest_page_edit = db.session.query(db.func.max(SitePage.updated_at)) \
        .filter_by(site_id=site.id).scalar()
    latest_shared_edit = db.session.query(db.func.max(SiteSharedBlock.updated_at)) \
        .filter_by(site_id=site.id).scalar()
    latest_edit = max(
        [dt for dt in (latest_page_edit, latest_shared_edit) if dt is not None],
        default=None,
    )
    return latest_edit is not None and latest_edit > site.published_at


# =============================================================================
# Role Enforcement (RBAC)
# =============================================================================

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


# =============================================================================
# Slug Validation
# =============================================================================

RESERVED_SLUGS = {
    'www', 'api', 'app', 'admin', 'mail', 'ftp', 'cdn', 'static',
    'blog', 'help', 'docs', 'status', 'login', 'signup', 'dashboard',
}


def validate_site_slug(slug):
    """Validate slug is a valid DNS subdomain label.
    Returns (is_valid, error_message)."""
    if not slug:
        return False, 'Slug is required.'
    if not re.match(r'^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$', slug):
        return False, 'Slug must be 3-63 lowercase letters, numbers, or hyphens. Cannot start/end with a hyphen.'
    if slug in RESERVED_SLUGS:
        return False, f'"{slug}" is reserved. Please choose a different slug.'
    return True, None


# =============================================================================
# Default Page YAML Template
# =============================================================================

DEFAULT_PAGE_YAML_TEMPLATE = """\
- name: site
  properties:
    theme:
      fonts:
        heading: &font-heading "'Inter', sans-serif"
        content: &font-content "'Inter', sans-serif"
      colors:
        primary: &color-primary "#1e293b"
        secondary: &color-secondary "#64748b"
        accent: &color-accent "#3b82f6"
        background: &color-background "#ffffff"
  components:
    - name: page
      slug: "{slug}"
      title: "{title}"
      properties:
        appearance:
          background:
            color: *color-background
            opacity: 100
      components: []
"""


def generate_default_page_yaml(slug, title):
    """Generate the default YAML for a new page (complete renderable document with site wrapper)."""
    return DEFAULT_PAGE_YAML_TEMPLATE.format(
        slug=slug,
        title=title,
    )


def generate_page_yaml_from_homepage(homepage_yaml, slug, title):
    """Generate new page YAML based on homepage — copies theme + titlebar."""
    try:
        structure = yaml.safe_load(homepage_yaml)
        if not structure or not isinstance(structure, list):
            return generate_default_page_yaml(slug, title)

        site = structure[0]
        theme = (site.get('properties') or {}).get('theme', {})
        page = (site.get('components') or [{}])[0]
        page_components = page.get('components') or []

        # Extract titlebar if first component
        titlebar = None
        if page_components and page_components[0].get('name') == 'titlebar':
            titlebar = page_components[0]

        # Build new structure
        new_site = {
            'name': 'site',
            'properties': {'theme': theme} if theme else {},
            'components': [{
                'name': 'page',
                'slug': slug,
                'title': title,
                'properties': {
                    'appearance': {
                        'background': {
                            'color': theme.get('colors', {}).get('background', '#ffffff'),
                            'opacity': 100
                        }
                    }
                },
                'components': [titlebar] if titlebar else []
            }]
        }

        return yaml.dump([new_site], default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception:
        return generate_default_page_yaml(slug, title)


# =============================================================================
# Default Site Settings (JSON)
# =============================================================================

DEFAULT_SITE_SETTINGS = {
    'seo': {
        'titleTemplate': '{pageTitle} | {siteName}',
        'metaDescription': '',
        'ogImage': '',
        'ogTitle': '',
    },
    'branding': {
        'faviconUrl': '',
        'siteName': '',
    },
    'social': {
        'twitterHandle': '',
        'facebookPage': '',
        'defaultShareImage': '',
    },
}


def validate_site_settings(settings):
    """Validate settings dict shape. Returns (is_valid, error_message).
    Only allows known categories and string values."""
    if not isinstance(settings, dict):
        return False, 'Settings must be an object.'

    for category, values in settings.items():
        if category not in DEFAULT_SITE_SETTINGS:
            return False, f'Unknown settings category: "{category}"'
        if not isinstance(values, dict):
            return False, f'Settings category "{category}" must be an object.'
        allowed_keys = set(DEFAULT_SITE_SETTINGS[category].keys())
        for key in values:
            if key not in allowed_keys:
                return False, f'Unknown setting: "{category}.{key}"'
            if not isinstance(values[key], str):
                return False, f'Setting "{category}.{key}" must be a string.'
    return True, None
