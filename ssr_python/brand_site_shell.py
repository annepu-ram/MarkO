"""Deterministic brand-owned site shell generation."""
import json
import re

import yaml

from extensions import db
from models import Brand, SectionItem, Site, SitePage, SiteSharedBlock


DEFAULT_COLORS = {
    'primary': '#111827',
    'text': '#374151',
    'secondary': '#6b7280',
    'accent': '#6366f1',
    'background': '#ffffff',
}

DEFAULT_FONTS = {
    'heading': "'Inter', sans-serif",
    'content': "'Inter', sans-serif",
}


def _slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', (value or '').lower()).strip('-') or 'site'


def _unique_site_slug(org_id, base_slug, existing_site_id=None):
    base = _slugify(base_slug)
    slug = base
    counter = 2
    while True:
        query = Site.query.filter_by(org_id=org_id, slug=slug)
        if existing_site_id:
            query = query.filter(Site.id != existing_site_id)
        if not query.first():
            return slug
        slug = f'{base}-{counter}'
        counter += 1


def brand_to_site_theme(brand):
    """Return the renderer theme mapping consumed by site_composer."""
    colors = dict(DEFAULT_COLORS)
    for key, value in {
        'primary': brand.color_primary,
        'text': brand.color_text,
        'secondary': brand.color_secondary,
        'accent': brand.color_accent,
        'background': brand.color_background,
    }.items():
        if value:
            colors[key] = value

    fonts = dict(DEFAULT_FONTS)
    if brand.font_heading:
        fonts['heading'] = brand.font_heading
    if brand.font_body:
        fonts['content'] = brand.font_body

    return {
        'fonts': fonts,
        'colors': colors,
    }


def _dump_component_list(components):
    return yaml.dump(components, sort_keys=False, allow_unicode=True)


def _header_components(brand):
    nav_items = ['Home', 'Content', 'Contact']
    if brand.industry:
        nav_items[1] = brand.industry.replace('_', ' ').title()
    return [{
        'name': 'titlebar',
        'properties': {
            'branding': {
                'title': brand.name,
                **({'logo': brand.logo_url} if brand.logo_url else {}),
            },
            'navigation': {
                'items': nav_items,
            },
            'cta': {
                'label': brand.cta_style or 'Contact us',
                'href': '#contact',
            },
        },
    }]


def _footer_components(brand):
    text = brand.tagline or brand.brand_promise or f'{brand.name}.'
    social_links = brand.get_social_links() if hasattr(brand, 'get_social_links') else {}
    link_components = []
    for key, url in social_links.items():
        if not url:
            continue
        label = 'X' if key == 'x' else key.replace('_', ' ').title()
        link_components.append({
            'name': 'link',
            'properties': {
                'text': label,
                'href': url,
            },
        })

    info_components = [
        {'name': 'heading', 'properties': {'text': brand.name}},
        {'name': 'paragraph', 'properties': {'text': text}},
    ]
    if brand.website_url:
        info_components.append({
            'name': 'link',
            'properties': {
                'text': 'Website',
                'href': brand.website_url,
            },
        })
    if link_components:
        info_components.extend(link_components)

    return [{
        'name': 'layout-row',
        'properties': {
            'tag': 'footer',
        },
        'components': [{
            'name': 'layout-column',
            'components': info_components,
        }],
    }]


def _homepage_body_components(brand):
    heading = brand.name
    paragraph = brand.tagline or brand.description or brand.brand_promise or 'Add sections from the content library to build this page.'
    return [{
        'name': 'layout-row',
        'components': [{
            'name': 'layout-column',
            'components': [
                {'name': 'heading', 'properties': {'text': heading}},
                {'name': 'paragraph', 'properties': {'text': paragraph}},
            ],
        }],
    }]


def _settings_for_brand(brand):
    title = brand.name
    description = brand.description or brand.tagline or brand.brand_promise or f'{brand.name} website.'
    social_links = brand.get_social_links() if hasattr(brand, 'get_social_links') else {}
    return {
        'seo': {
            'titleTemplate': f'{title} | {{page_title}}',
            'metaDescription': description[:300],
        },
        'branding': {
            'siteName': brand.name,
            'faviconUrl': '',
        },
        'social': {
            'twitterHandle': social_links.get('x', ''),
            'facebookPage': social_links.get('facebook', ''),
            'links': social_links,
        },
    }


def ensure_brand_site(brand_id, *, org_id, regenerate=False):
    """Create or refresh the one primary site shell for a brand.

    Regeneration updates only site-level shell state: theme, settings, shared
    header/footer. Existing page body YAML is preserved.
    """
    brand = Brand.query.filter_by(id=brand_id, org_id=org_id).first()
    if not brand:
        return None

    site = Site.query.filter_by(org_id=org_id, brand_id=brand.id).first()
    created = False
    if not site:
        site = Site(
            org_id=org_id,
            brand_id=brand.id,
            name=brand.name,
            slug=_unique_site_slug(org_id, brand.slug or brand.name),
        )
        db.session.add(site)
        db.session.flush()
        created = True
    elif regenerate:
        site.name = brand.name
        site.slug = _unique_site_slug(org_id, site.slug or brand.slug or brand.name, existing_site_id=site.id)

    if created or regenerate:
        site.theme = json.dumps(brand_to_site_theme(brand))
        site.set_settings(_settings_for_brand(brand))
        _upsert_shared_block(site, 'header', 'Header', _header_components(brand), 0)
        _upsert_shared_block(site, 'footer', 'Footer', _footer_components(brand), 100)
        _upsert_footer_section(brand)

    homepage = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
    if not homepage:
        homepage = SitePage(
            site_id=site.id,
            slug='home',
            title='Home',
            yaml_content='- name: site\n  components: []\n',
            body_yaml_content=_dump_component_list(_homepage_body_components(brand)),
            sort_order=0,
            is_homepage=True,
        )
        db.session.add(homepage)

    return site


def _upsert_shared_block(site, key, label, components, sort_order):
    block = SiteSharedBlock.query.filter_by(site_id=site.id, key=key).first()
    if not block:
        block = SiteSharedBlock(site_id=site.id, key=key, label=label, sort_order=sort_order)
        db.session.add(block)
    block.label = label
    block.sort_order = sort_order
    block.enabled = True
    block.yaml_content = _dump_component_list(components)
    return block


def _upsert_footer_section(brand):
    section = SectionItem.query.filter_by(
        org_id=brand.org_id,
        brand_id=brand.id,
        section_type='footer',
    ).first()
    if not section:
        section = SectionItem(
            org_id=brand.org_id,
            brand_id=brand.id,
            section_type='footer',
            status='active',
        )
        db.session.add(section)
    section.name = f'{brand.name} Footer'
    section.description = 'Brand site footer generated from brand identity and social links.'
    section.status = 'active'
    section.yaml_content = _dump_component_list(_footer_components(brand))
    section.set_content_refs([])
    section.set_tags(['brand-site-shell', 'footer'])
    section.set_generation_metadata({
        'compiler': 'brand_footer_section.v1',
        'brand_id': brand.id,
        'source': 'brand_site_shell',
        'uses': ['brand.name', 'brand.tagline', 'brand.website_url', 'brand.social_links'],
    })
    return section
