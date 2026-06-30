"""Compose site-scoped source records into renderer-compatible YAML."""
import copy
import json
import yaml

DEFAULT_PAGE_PROPERTIES = {
    'appearance': {
        'background': {
            'color': '$color-background',
            'opacity': 100,
        }
    }
}


class CompositionError(ValueError):
    """Raised when source YAML cannot be composed into renderer YAML."""


def _parse_yaml_list(yaml_text, label):
    """Parse a YAML string that must resolve to a list."""
    if yaml_text is None or str(yaml_text).strip() == '':
        return []
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise CompositionError(f'{label} is not valid YAML: {exc}') from exc
    if parsed is None:
        return []
    if not isinstance(parsed, list):
        raise CompositionError(f'{label} must be a YAML list of components.')
    return parsed


def _parse_mapping(text, label):
    """Parse JSON or YAML text into a mapping."""
    if not text or not str(text).strip():
        return {}
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise CompositionError(f'{label} is not valid JSON/YAML: {exc}') from exc
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise CompositionError(f'{label} must be an object.')
    return parsed


def _legacy_extract(page):
    """Extract page body/theme/properties from current full-document page YAML."""
    parsed = _parse_yaml_list(page.yaml_content, f'page "{page.slug}" YAML')
    result = {
        'theme': {},
        'page_properties': copy.deepcopy(DEFAULT_PAGE_PROPERTIES),
        'body_components': parsed,
        'header': [],
        'footer': [],
    }

    if not parsed:
        result['body_components'] = []
        return result

    first = parsed[0]
    if not isinstance(first, dict):
        return result

    if first.get('name') == 'site':
        site_props = first.get('properties') or {}
        result['theme'] = copy.deepcopy(site_props.get('theme') or {})
        result['header'] = copy.deepcopy(first.get('header') or [])
        result['footer'] = copy.deepcopy(first.get('footer') or [])
        pages = first.get('components') or []
        page_component = pages[0] if pages and isinstance(pages[0], dict) else {}
        result['page_properties'] = copy.deepcopy(
            page_component.get('properties') or result['page_properties']
        )
        result['body_components'] = copy.deepcopy(page_component.get('components') or [])
        return result

    if first.get('name') == 'page':
        result['page_properties'] = copy.deepcopy(first.get('properties') or result['page_properties'])
        result['body_components'] = copy.deepcopy(first.get('components') or [])
        return result

    return result


def _load_theme(site, legacy):
    if getattr(site, 'theme', None):
        theme_data = _parse_mapping(site.theme, 'site theme')
        if 'theme' in theme_data and isinstance(theme_data['theme'], dict):
            return theme_data['theme']
        return theme_data
    return legacy.get('theme') or {}


def _load_page_body(page, legacy):
    body_text = getattr(page, 'body_yaml_content', None)
    if body_text and body_text.strip():
        return _parse_yaml_list(body_text, f'page "{page.slug}" body YAML')
    return legacy.get('body_components') or []


def _override_map(page):
    overrides = {}
    for override in getattr(page, 'shared_block_overrides', []) or []:
        overrides[override.block_key] = override
    return overrides


def _apply_override(block_key, components, overrides):
    override = overrides.get(block_key)
    if not override:
        return components
    if override.mode == 'hidden':
        return []
    if override.mode == 'custom':
        return _parse_yaml_list(
            override.custom_yaml_content,
            f'custom shared block "{block_key}" YAML',
        )
    if override.mode == 'inherit':
        return components
    raise CompositionError(f'Unknown shared block override mode "{override.mode}" for "{block_key}".')


def _shared_components(site, page, legacy):
    """Return (header_components, footer_components)."""
    overrides = _override_map(page)
    header = []
    footer = []

    blocks = [
        block for block in (getattr(site, 'shared_blocks', []) or [])
        if getattr(block, 'enabled', True)
    ]
    blocks.sort(key=lambda b: (b.sort_order or 0, b.key))

    if blocks:
        for block in blocks:
            components = _parse_yaml_list(block.yaml_content, f'shared block "{block.key}" YAML')
            components = _apply_override(block.key, components, overrides)
            if block.key in ('announcement_bar', 'header'):
                header.extend(components)
            elif block.key == 'footer':
                footer.extend(components)
        return header, footer

    return (
        _apply_override('header', copy.deepcopy(legacy.get('header') or []), overrides),
        _apply_override('footer', copy.deepcopy(legacy.get('footer') or []), overrides),
    )


def compose_page_yaml(site, page):
    """Return renderer-compatible YAML structure for one site page."""
    legacy = _legacy_extract(page)
    theme = _load_theme(site, legacy)
    body_components = _load_page_body(page, legacy)
    header_components, footer_components = _shared_components(site, page, legacy)

    page_properties = copy.deepcopy(legacy.get('page_properties') or DEFAULT_PAGE_PROPERTIES)

    composed_site = {
        'name': 'site',
        'properties': {'theme': theme} if theme else {},
        'components': [{
            'name': 'page',
            'slug': page.slug,
            'title': page.title,
            'properties': page_properties,
            'components': body_components,
        }],
    }
    if header_components:
        composed_site['header'] = header_components
    if footer_components:
        composed_site['footer'] = footer_components

    return [composed_site]


def dump_composed_yaml(site, page):
    """Return composed YAML text for debugging and tests."""
    return yaml.dump(compose_page_yaml(site, page), sort_keys=False, allow_unicode=True)
