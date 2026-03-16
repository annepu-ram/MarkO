"""
Published Site Routes — Serves pre-rendered HTML to visitors.

Dual-mode routing:
  - Path-based (local dev): /s/:site-slug/:page-slug
  - Subdomain (production):  :site-slug.swiftsites.com/:page-slug

These routes are PUBLIC — no auth required. Only sites with status='published' are served.
"""
import hmac
import hashlib
import json
import time
from collections import defaultdict
from flask import Blueprint, request, jsonify, redirect, current_app
from models import Site, PublishedPage, FormSubmission
from extensions import db

published_bp = Blueprint('published', __name__)


# =============================================================================
# Rate Limiter (in-memory, simple)
# =============================================================================

_rate_limits = defaultdict(list)


def _check_rate_limit(ip, site_id, max_per_minute=10):
    """Simple in-memory rate limiter. Returns True if allowed."""
    key = f'{ip}:{site_id}'
    now = time.time()
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < 60]
    if len(_rate_limits[key]) >= max_per_minute:
        return False
    _rate_limits[key].append(now)
    return True


# =============================================================================
# Helper: Derive form token
# =============================================================================

def _derive_form_token(form_secret, site_slug, form_name):
    """Derive a per-form token from the site's secret."""
    return hmac.new(
        form_secret.encode(),
        f'{site_slug}:{form_name}'.encode(),
        hashlib.sha256,
    ).hexdigest()[:32]


# =============================================================================
# Path-Based Routes (local dev: /s/:slug/:page)
# =============================================================================

@published_bp.route('/s/<site_slug>', defaults={'page_slug': None})
@published_bp.route('/s/<site_slug>/<page_slug>')
def serve_path(site_slug, page_slug):
    """Serve published page via path-based URL."""
    return _serve_page(site_slug, page_slug)


@published_bp.route('/s/<site_slug>/forms/<form_name>/submit', methods=['POST'])
def submit_form_path(site_slug, form_name):
    """Handle form submission via path-based URL."""
    return _handle_form_submission(site_slug, form_name)


# =============================================================================
# Shared Handlers
# =============================================================================

def _serve_page(site_slug, page_slug):
    """Serve pre-rendered HTML from published_pages wrapped in a full document."""
    site = Site.query.filter_by(slug=site_slug, status='published').first()
    if not site:
        return '<h1>404 — Site not found</h1>', 404

    if page_slug is None:
        # Redirect to homepage
        home = PublishedPage.query.filter_by(site_id=site.id).order_by(
            PublishedPage.sort_order
        ).first()
        if not home:
            return '<h1>404 — No pages found</h1>', 404
        return redirect(f'/s/{site_slug}/{home.slug}')

    page = PublishedPage.query.filter_by(
        site_id=site.id, slug=page_slug
    ).first()
    if not page:
        return '<h1>404 — Page not found</h1>', 404

    full_html = _build_html_document(page.rendered_html, site, page)
    return full_html, 200, {'Content-Type': 'text/html'}


# =============================================================================
# HTML Document Builder — wraps body HTML with <head>, meta tags, CSS/JS
# =============================================================================

def _escape_attr(s):
    """Escape string for use in HTML attribute values."""
    return (s or '').replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def _escape_html(s):
    """Escape string for use in HTML text content."""
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _build_html_document(body_html, site, page):
    """Wrap body-only HTML in a full HTML document with <head> and meta tags."""
    settings = site.get_settings()
    seo = settings.get('seo', {})
    branding = settings.get('branding', {})
    social = settings.get('social', {})

    # Resolve title
    site_name = branding.get('siteName') or site.name
    title_template = seo.get('titleTemplate') or '{pageTitle} | {siteName}'
    page_title = title_template.replace('{pageTitle}', page.title).replace('{siteName}', site_name)

    # Build meta tags
    meta_tags = []

    description = seo.get('metaDescription', '')
    if description:
        meta_tags.append(f'    <meta name="description" content="{_escape_attr(description)}">')

    # Open Graph
    og_title = seo.get('ogTitle') or page_title
    meta_tags.append(f'    <meta property="og:title" content="{_escape_attr(og_title)}">')
    meta_tags.append('    <meta property="og:type" content="website">')
    if description:
        meta_tags.append(f'    <meta property="og:description" content="{_escape_attr(description)}">')

    og_image = seo.get('ogImage') or social.get('defaultShareImage', '')
    if og_image:
        meta_tags.append(f'    <meta property="og:image" content="{_escape_attr(og_image)}">')

    # Twitter Card
    twitter_handle = social.get('twitterHandle', '')
    if twitter_handle:
        meta_tags.append('    <meta name="twitter:card" content="summary_large_image">')
        meta_tags.append(f'    <meta name="twitter:site" content="{_escape_attr(twitter_handle)}">')

    # Favicon
    favicon_url = branding.get('faviconUrl', '')
    favicon_link = f'    <link rel="icon" href="{_escape_attr(favicon_url)}">' if favicon_url else ''

    meta_block = '\n'.join(meta_tags)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_escape_html(page_title)}</title>
{favicon_link}
{meta_block}
    <link rel="stylesheet" href="/static/css/tokens.css">
    <link rel="stylesheet" href="/static/css/components.css">
</head>
<body>
    {body_html}
    <script src="/static/js/swift-sites-runtime.js"></script>
    <script>document.addEventListener('DOMContentLoaded',function(){{if(window.SwiftSites)SwiftSites.init();}});</script>
</body>
</html>'''


def _handle_form_submission(site_slug, form_name):
    """5-layer anti-bot form submission handler."""
    site = Site.query.filter_by(slug=site_slug, status='published').first()
    if not site:
        return jsonify({'error': 'Site not found'}), 404

    # Layer 5: Rate limiting
    if not _check_rate_limit(request.remote_addr, site.id):
        return jsonify({'error': 'Too many submissions'}), 429

    # Layer 5: Honeypot
    if request.form.get('_website', ''):
        _save_submission(site, form_name, request.form, is_spam=True)
        return jsonify({'ok': True}), 200  # Silent accept

    # Layer 2: Form token
    form_token = request.form.get('_form_token', '')
    if not site.form_secret:
        return jsonify({'error': 'Invalid submission'}), 403
    expected_token = _derive_form_token(site.form_secret, site.slug, form_name)
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
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(challenge, expected_challenge):
        return jsonify({'error': 'Invalid submission'}), 403

    # All checks passed
    _save_submission(site, form_name, request.form, is_spam=False)
    return jsonify({'ok': True}), 200


def _save_submission(site, form_name, form_data, is_spam=False):
    """Store form submission in the database."""
    # Extract user fields (exclude internal _-prefixed fields)
    fields = {k: v for k, v in form_data.items() if not k.startswith('_')}

    # Determine page_slug from Referer header
    page_slug = ''
    referer = request.headers.get('Referer', '')
    if referer:
        parts = referer.rstrip('/').split('/')
        if parts:
            page_slug = parts[-1]

    submission = FormSubmission(
        site_id=site.id,
        page_slug=page_slug,
        form_name=form_name,
        data=json.dumps(fields),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500],
        is_spam=is_spam,
    )
    db.session.add(submission)
    db.session.commit()
