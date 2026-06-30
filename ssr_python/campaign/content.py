"""
Content normalization — turn grouped shorthand (or an explicit typed list) into
a uniform list of typed content items.

This is the "atom view" the brief refers to: a transient, in-memory typed-content
representation. There is exactly one internal shape after normalization; grouped
strings never reach recipe matching, ref resolution, or the compiler.

A normalized content item is a plain dict:

    {
      "id": "content_promise_0",
      "type": "promise",
      "content": <str | dict>,        # str for primitives; dict for some composites
      "truth_level": "approved",
      "source": "human_input",
      "slots": {...},                  # schema-backed fields
      "tags": {...},                   # optional semantic tags
    }
"""

from campaign import vocabulary as V

# Group keys whose members are full objects (not bare strings).
_OBJECT_GROUPS = {'objections', 'faqs', 'testimonials'}

# Default truth level by content type when the source is free campaign-YAML text.
# Verified-truth types still require trusted provenance to be marked verified;
# here we default human-entered campaign YAML to "approved".
_DEFAULT_TRUTH = 'approved'


def normalize_campaign_content(content):
    """Normalize the campaign `content:` block into a flat list of typed items.

    Accepts:
      - grouped shorthand:  { "promises": [...], "calls_to_action": {...}, ... }
      - explicit typed list: [ { "type": ..., "content": ... }, ... ]

    Returns: list[dict] of typed content items.
    Raises: ValueError on an unknown group key or malformed item.
    """
    if isinstance(content, list):
        return _normalize_typed_list(content)
    if isinstance(content, dict):
        return _normalize_grouped(content)
    raise ValueError('content must be a grouped mapping or a list of typed items.')


def _normalize_typed_list(items):
    out = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or 'type' not in item or 'content' not in item:
            raise ValueError(f'content[{i}] must have "type" and "content".')
        ctype = item['type']
        if ctype not in V.CONTENT_TYPE:
            raise ValueError(f'content[{i}].type "{ctype}" is not a known content type.')
        out.append(_make_item(
            ctype, item['content'], len([x for x in out if x['type'] == ctype]),
            truth_level=item.get('truth_level', _DEFAULT_TRUTH),
            source=item.get('source', 'human_input'),
            slots=item.get('slots'),
            tags=item.get('tags'),
        ))
    return out


def _normalize_grouped(content):
    out = []
    for group_key, value in content.items():
        ctype = V.GROUP_KEY_TO_TYPE.get(group_key)
        if not ctype:
            raise ValueError(f'content has unknown group key "{group_key}".')

        if group_key == 'calls_to_action':
            # { primary: "...", secondary: "..." } -> cta items with style hints
            out.extend(_normalize_ctas(value))
            continue

        # List-valued groups
        members = value if isinstance(value, list) else [value]
        for idx, member in enumerate(members):
            if group_key in _OBJECT_GROUPS:
                content_val, payload = _split_object_member(group_key, member)
                out.append(_make_item(ctype, content_val, idx, slots=payload))
            else:
                out.append(_make_item(ctype, member, idx))
    return out


def _normalize_ctas(value):
    items = []
    if isinstance(value, dict):
        order = ['primary', 'secondary']
        keys = order + [k for k in value if k not in order]
        for i, key in enumerate(keys):
            if key not in value or value[key] in (None, ''):
                continue
            style = 'direct' if key == 'primary' else 'soft'
            items.append(_make_item(
                'cta', value[key], i,
                slots={'style': style, 'role': key},
            ))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            items.append(_make_item('cta', v, i, slots={'style': 'direct'}))
    elif value:
        items.append(_make_item('cta', value, 0, slots={'style': 'direct'}))
    return items


def _split_object_member(group_key, member):
    """Object-group members carry their own structured fields."""
    if not isinstance(member, dict):
        # tolerate a bare string for objection/faq/testimonial
        return member, {}
    if group_key == 'objections':
        return (member.get('concern') or member.get('content') or ''), {
            'concern': member.get('concern'),
            'response': member.get('response'),
        }
    if group_key == 'faqs':
        return (member.get('question') or member.get('content') or ''), {
            'question': member.get('question'),
            'answer': member.get('answer'),
        }
    if group_key == 'testimonials':
        return (member.get('quote') or member.get('content') or ''), {
            k: member.get(k) for k in
            ('author', 'author_role', 'company', 'rating', 'media_id', 'permission_status')
            if member.get(k) is not None
        }
    return member, {}


def _make_item(ctype, content, idx, *, truth_level=_DEFAULT_TRUTH,
               source='human_input', slots=None, tags=None):
    item = {
        'id': f'content_{ctype}_{idx}',
        'type': ctype,
        'content': content,
        'truth_level': truth_level,
        'source': source,
    }
    if slots:
        item['slots'] = {k: v for k, v in slots.items() if v is not None}
    if tags:
        item['tags'] = tags
    return item


# --- grouping helpers used by ref resolution / recipe matching ----------------

def group_by_type(items):
    """Return {type: [items...]} preserving order."""
    grouped = {}
    for item in items:
        grouped.setdefault(item['type'], []).append(item)
    return grouped


def available_types(items):
    """Set of content types present in the normalized list."""
    return {item['type'] for item in items}
