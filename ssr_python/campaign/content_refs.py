"""
Content reference resolution.

Resolves the reference strings used in `landing_page.sections[].content_refs`:

    campaign.<field>                  -> a scalar from the campaign block
    content.<group>[<index>]          -> the indexed item of a content group
    content.<group>                   -> all items of a content group (list)
    content.calls_to_action.primary   -> the primary/secondary CTA
    content.<group>.<key>             -> keyed lookup within a group object

Group names are the campaign-YAML shorthand keys (promises, pain_points,
calls_to_action, ...). They map to normalized content types via vocabulary.
Resolution returns the resolved value(s) as plain strings/dicts/lists, or raises
ContentRefError when a ref cannot resolve.
"""

import re
from campaign import vocabulary as V
from campaign.content import group_by_type

_INDEX_RE = re.compile(r'^([a-z_]+)\[(\d+)\]$')


class ContentRefError(Exception):
    pass


def resolve_ref(ref, campaign_block, content_items):
    """Resolve a single content_ref string. Returns str | dict | list.

    Raises ContentRefError if the ref is malformed or cannot be resolved.
    """
    if not isinstance(ref, str) or not ref.strip():
        raise ContentRefError('Empty content reference.')
    ref = ref.strip()

    if ref.startswith('campaign.'):
        return _resolve_campaign(ref, campaign_block)
    if ref.startswith('content.'):
        return _resolve_content(ref, content_items)
    raise ContentRefError(f'Reference "{ref}" must start with "campaign." or "content.".')


def resolve_refs(refs, campaign_block, content_items):
    """Resolve a {slot: ref} mapping into {slot: value}. Raises on first failure."""
    resolved = {}
    for slot, ref in (refs or {}).items():
        resolved[slot] = resolve_ref(ref, campaign_block, content_items)
    return resolved


def try_resolve_refs(refs, campaign_block, content_items):
    """Best-effort resolution. Returns (resolved, missing) without raising.

    `missing` is a {slot: reason} map for refs that could not resolve — useful
    for optional section slots and for surfacing "add proof" style guidance.
    """
    resolved, missing = {}, {}
    for slot, ref in (refs or {}).items():
        try:
            resolved[slot] = resolve_ref(ref, campaign_block, content_items)
        except ContentRefError as e:
            missing[slot] = str(e)
    return resolved, missing


# --- internals ----------------------------------------------------------------

def _resolve_campaign(ref, campaign_block):
    field = ref[len('campaign.'):]
    if not field or '.' in field or '[' in field:
        raise ContentRefError(f'Unsupported campaign reference "{ref}".')
    if not isinstance(campaign_block, dict) or field not in campaign_block:
        raise ContentRefError(f'campaign has no field "{field}".')
    return campaign_block[field]


def _resolve_content(ref, content_items):
    expr = ref[len('content.'):]
    grouped = group_by_type(content_items)

    # content.<group>[<index>]
    m = _INDEX_RE.match(expr)
    if m:
        group, index = m.group(1), int(m.group(2))
        items = _items_for_group(group, grouped)
        if index >= len(items):
            raise ContentRefError(
                f'content.{group}[{index}] out of range (have {len(items)}).'
            )
        return _value_of(items[index])

    # content.calls_to_action.primary / .secondary  (keyed CTA)
    if '.' in expr:
        group, key = expr.split('.', 1)
        items = _items_for_group(group, grouped)
        if group == 'calls_to_action':
            for it in items:
                if (it.get('slots') or {}).get('role') == key:
                    return _value_of(it)
            # fallback: primary == first, secondary == second
            order = {'primary': 0, 'secondary': 1}
            idx = order.get(key)
            if idx is not None and idx < len(items):
                return _value_of(items[idx])
            raise ContentRefError(f'content.calls_to_action.{key} not found.')
        # keyed lookup inside an object-group's slots
        for it in items:
            payload = it.get('slots') or {}
            if key in payload:
                return payload[key]
        raise ContentRefError(f'content.{group}.{key} not found.')

    # content.<group>  -> list of all values in the group
    items = _items_for_group(expr, grouped)
    if not items:
        raise ContentRefError(f'content.{expr} resolved to no items.')
    return [_value_of(it) for it in items]


def _items_for_group(group, grouped):
    """Map a campaign-YAML group name (e.g. 'promises') to normalized items.

    Falls back to treating `group` as a content type directly (e.g. 'promise').
    """
    ctype = V.GROUP_KEY_TO_TYPE.get(group, group)
    return grouped.get(ctype, [])


def _value_of(item):
    """Return the display value of a normalized item.

    Object-group items (objection/faq) return their slots so
    downstream builders can render both parts.
    """
    payload = item.get('slots') or {}
    if item['type'] == 'objection' and ('concern' in payload or 'response' in payload):
        return {'concern': payload.get('concern') or item['content'],
                'response': payload.get('response')}
    if item['type'] == 'faq' and ('question' in payload or 'answer' in payload):
        return {'question': payload.get('question') or item['content'],
                'answer': payload.get('answer')}
    return item['content']
