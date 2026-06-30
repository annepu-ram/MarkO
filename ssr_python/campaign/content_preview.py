"""
Render a single Content Library item to a renderer-compatible structure.

Maps a ContentItem's category to renderer components (reusing section_builders
primitives), then wraps them in a `site > page > layout-row > layout-column`
shell with a theme applied — so the preview reflects the owning brand's colors
and fonts.
"""

from campaign.section_builders import _heading, _paragraph, _eyebrow, _button, _row


def _payload(item):
    """Return the item's slots as a dict (handles model or dict)."""
    if hasattr(item, 'get_slots'):
        try:
            return item.get_slots() or {}
        except Exception:
            return {}
    if isinstance(item, dict):
        sp = item.get('slots')
        if isinstance(sp, dict):
            return sp
    return {}


def _field(item, name, default=None):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def content_item_to_components(item):
    """Map one content item to a list of renderer components.

    `item` may be a ContentItem model or a plain dict with the same fields.
    """
    category = (_field(item, 'category') or '').strip()
    title = _field(item, 'title')
    content = _field(item, 'content') or ''
    payload = _payload(item)

    comps = []

    if category in ('headline',):
        comps.append(_heading(content, level=1))

    elif category in ('subheadline',):
        comps.append(_heading(content, level=2))

    elif category in ('tagline', 'eyebrow'):
        comps.append(_eyebrow(content))

    elif category in ('cta',):
        href = payload.get('link') or payload.get('href') or '#lead'
        headline = payload.get('headline')
        paragraph = payload.get('paragraph')
        button_label = payload.get('button_label') or payload.get('cta_label') or content
        if headline or paragraph:
            if headline:
                comps.append(_heading(headline, level=2))
            if paragraph:
                comps.append(_paragraph(paragraph))
            if button_label:
                comps.append(_button(button_label, href=href))
        else:
            comps.append(_button(button_label, href=href))

    elif category in ('value_proposition',):
        headline = payload.get('headline') or title
        paragraph = payload.get('paragraph') or content
        if headline:
            comps.append(_heading(headline, level=1))
        comps.append(_paragraph(paragraph))

    elif category in ('offer', 'promotion', 'announcement'):
        headline = payload.get('headline') or title
        details = payload.get('details') or content
        if headline:
            comps.append(_heading(headline, level=2))
        comps.append(_paragraph(details))
        code = payload.get('code')
        if code:
            comps.append({'name': 'badge', 'properties': {'text': f'Code: {code}'}})

    elif category in ('testimonial',):
        quote = payload.get('quote') or content
        comps.append({'name': 'blockquote', 'properties': {'quote': quote}})
        author = payload.get('author')
        if author:
            role = payload.get('author_role') or payload.get('company')
            byline = f'— {author}' + (f', {role}' if role else '')
            comps.append(_paragraph(byline))

    elif category in ('faq', 'objection'):
        q = payload.get('question') or payload.get('concern') or title or 'Question'
        a = payload.get('answer') or payload.get('response') or content
        # accordion: `items` is a component-level sibling of `properties`
        comps.append({
            'name': 'accordion', 'properties': {},
            'items': [{'title': str(q),
                       'components': [{'name': 'paragraph', 'properties': {'text': str(a)}}]}],
        })

    elif category in ('proof', 'product_spec', 'comparison', 'case_study'):
        if title:
            comps.append(_heading(title, level=2))
        comps.append(_paragraph(content))

    elif category in ('product_feature', 'benefit'):
        headline = payload.get('headline') or title
        paragraph = payload.get('paragraph') or content
        if headline:
            comps.append(_heading(headline, level=3))
        comps.append(_paragraph(paragraph))

    else:
        # paragraph / boilerplate / about / guarantee / ad_copy / email_subject /
        # social_post / seo_meta / form / unknown -> title + paragraph fallback
        if title:
            comps.append(_heading(title, level=2))
        comps.append(_paragraph(content))

    return comps


def build_preview_structure(item, theme):
    """Wrap a content item's components in a renderer-ready site>page shell.

    `theme` is a {'colors': {...}, 'fonts': {...}} dict (from brand_to_theme).
    Returns a list suitable for render_yaml_structure().
    """
    components = content_item_to_components(item)
    section = _row(components, section_id='content_preview')
    # section_id is bookkeeping only; strip for a clean render payload.
    section.pop('section_id', None)

    background = (theme.get('colors') or {}).get('background', '#ffffff')
    title = _field(item, 'title') or 'Content preview'

    return [{
        'name': 'site',
        'properties': {'theme': theme},
        'components': [{
            'name': 'page',
            'slug': 'content-preview',
            'title': title,
            'properties': {
                'appearance': {
                    'background': {'color': background, 'opacity': 100}
                }
            },
            'components': [section],
        }],
    }]


def build_section_preview_structure(items, theme, *, title='Section preview'):
    """Wrap an ordered list of content items into a renderer-ready site>page shell.

    Each item is rendered with the SAME `content_item_to_components()` path used
    for single-item preview, then concatenated into one centered column. This
    guarantees a section renders identically to how its items render alone, and
    re-renders live from current content values + the given brand `theme`.

    `items` is an ordered list of ContentItem models or plain dicts.
    `theme` is a {'colors': {...}, 'fonts': {...}} dict (from brand_to_theme).
    Returns a list suitable for render_yaml_structure().
    """
    components = []
    for item in items or []:
        components.extend(content_item_to_components(item))

    if not components:
        # Friendly empty state so an empty / all-deleted section never 500s.
        components = [_paragraph('This section has no content yet. Add content items to see a preview.')]

    section = _row(components, section_id='section_preview')
    section.pop('section_id', None)

    background = (theme.get('colors') or {}).get('background', '#ffffff')

    return [{
        'name': 'site',
        'properties': {'theme': theme},
        'components': [{
            'name': 'page',
            'slug': 'section-preview',
            'title': title,
            'properties': {
                'appearance': {
                    'background': {'color': background, 'opacity': 100}
                }
            },
            'components': [section],
        }],
    }]
