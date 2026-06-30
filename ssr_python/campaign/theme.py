"""
Brand -> renderer theme translation (single source of truth).

The renderer/themes system uses 5 theme colors (primary, text, secondary,
accent, background) and 2 fonts (heading, content). The Brand model stores
`color_text` and `font_body`; this module maps those to the theme contract
(`colors.text`, `fonts.content`) so brand identity flows into any rendered
output — content previews and campaign-driven site renders alike.
"""

# Mirrors renderer.DEFAULT_THEME_COLORS (kept local to avoid import cycles).
_DEFAULT_COLORS = {
    'primary': '#111827',
    'text': '#374151',
    'secondary': '#6b7280',
    'accent': '#6366f1',
    'background': '#ffffff',
}
_DEFAULT_FONTS = {
    'heading': "'Inter', sans-serif",
    'content': "'Inter', sans-serif",
}


def _clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def brand_to_theme(brand):
    """Build a renderer-compatible theme dict from a Brand (or None).

    Returns: { 'colors': {primary, text, secondary, accent, background},
               'fonts': {heading, content} }
    Empty/missing brand fields fall back to renderer defaults. A None brand
    yields the full default theme.
    """
    colors = dict(_DEFAULT_COLORS)
    fonts = dict(_DEFAULT_FONTS)

    if brand is not None:
        mapping = {
            'primary': _clean(getattr(brand, 'color_primary', None)),
            'text': _clean(getattr(brand, 'color_text', None)),
            'secondary': _clean(getattr(brand, 'color_secondary', None)),
            'accent': _clean(getattr(brand, 'color_accent', None)),
            'background': _clean(getattr(brand, 'color_background', None)),
        }
        for key, val in mapping.items():
            if val:
                colors[key] = val

        heading = _clean(getattr(brand, 'font_heading', None))
        body = _clean(getattr(brand, 'font_body', None))  # font_body -> content
        if heading:
            fonts['heading'] = heading
        if body:
            fonts['content'] = body

    return {'colors': colors, 'fonts': fonts}


def merge_brand_theme(existing_theme, brand):
    """Overlay a brand's colors/fonts onto an existing theme dict.

    Brand colors/fonts win; any other keys in `existing_theme` are preserved.
    Used by site render paths so editing a brand propagates on next render.
    Returns a new dict (does not mutate the input).
    """
    if brand is None:
        return dict(existing_theme or {})

    result = dict(existing_theme or {})
    brand_theme = brand_to_theme(brand)

    result_colors = dict(result.get('colors') or {})
    result_colors.update(brand_theme['colors'])
    result['colors'] = result_colors

    result_fonts = dict(result.get('fonts') or {})
    result_fonts.update(brand_theme['fonts'])
    result['fonts'] = result_fonts

    return result
