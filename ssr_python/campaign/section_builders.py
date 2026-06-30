"""
Section builders — turn a resolved section (purpose + resolved content values)
into a renderer-compatible component subtree.

Each builder returns a single `layout-row` component (a page section). The
compiler appends these into the page's `components` list. Builders emit only
existing renderer component names and set just the meaningful properties;
component defaults fill the rest at render time.

Bridge:  section purpose -> resolved content values -> renderer component tree.
"""


def _row(components, *, section_id=None, tag='section'):
    """A section-level layout-row wrapping a single centered column."""
    props = {'layout': {'tag': tag, 'wrap': 'wrap'},
             'spacing': {'paddingBlock': 'xxl', 'paddingInline': 'lg'}}
    row = {'name': 'layout-row', 'properties': props,
           'components': [{'name': 'layout-column',
                           'properties': {'layout': {'widthMode': '66', 'gap': 'md'}},
                           'components': components}]}
    if section_id:
        row['section_id'] = section_id
    return row


def _heading(text, level=2):
    return {'name': 'heading', 'properties': {'text': _as_text(text), 'level': level}}


def _paragraph(text):
    return {'name': 'paragraph', 'properties': {'text': _as_text(text)}}


def _eyebrow(text):
    return {'name': 'eyebrow', 'properties': {'text': _as_text(text)}}


def _button(text, href='#lead'):
    return {'name': 'button',
            'properties': {'text': _as_text(text),
                           'action': {'type': 'link', 'href': href}}}


def _as_text(value):
    """Coerce a resolved content value to a display string."""
    if value is None:
        return ''
    if isinstance(value, dict):
        # objection/faq structured value
        if 'concern' in value:
            return str(value.get('concern') or '')
        if 'question' in value:
            return str(value.get('question') or '')
        return str(value.get('content') or '')
    if isinstance(value, list):
        return ', '.join(str(v) for v in value)
    return str(value)


# --- purpose builders ---------------------------------------------------------

def _build_hero(resolved, section_id):
    comps = []
    if resolved.get('eyebrow'):
        comps.append(_eyebrow(resolved['eyebrow']))
    if resolved.get('headline'):
        comps.append(_heading(resolved['headline'], level=1))
    if resolved.get('subheadline'):
        comps.append(_paragraph(resolved['subheadline']))
    if resolved.get('primary_cta'):
        comps.append(_button(resolved['primary_cta']))
    return _row(comps, section_id=section_id)


def _build_problem_cost(resolved, section_id):
    comps = [_heading('The cost of the problem', level=2)]
    pains = resolved.get('pain_points')
    for pain in _as_list(pains):
        comps.append(_paragraph(pain))
    return _row(comps, section_id=section_id)


def _build_proof_points(resolved, section_id):
    comps = [_heading('Why teams trust us', level=2)]
    for item in _as_list(resolved.get('items')):
        comps.append(_paragraph(item))
    return _row(comps, section_id=section_id)


def _build_objection_handling(resolved, section_id):
    items = []
    for obj in _as_list(resolved.get('items')):
        if isinstance(obj, dict):
            title = obj.get('concern') or 'Common question'
            answer = obj.get('response') or ''
        else:
            title, answer = str(obj), ''
        items.append({'title': title,
                      'components': [{'name': 'paragraph',
                                      'properties': {'text': answer}}]})
    comps = [_heading('Common questions', level=2)]
    if items:
        # `items` is a component-level sibling of `properties` (renderer contract),
        # not nested inside properties.
        comps.append({'name': 'accordion', 'properties': {}, 'items': items})
    return _row(comps, section_id=section_id)


def _build_offer_highlight(resolved, section_id):
    offer = resolved.get('offer')
    comps = [_heading('Your offer', level=2)]
    comps.append(_paragraph(offer))
    return _row(comps, section_id=section_id)


def _build_final_cta(resolved, section_id):
    comps = []
    if resolved.get('headline'):
        comps.append(_heading(resolved['headline'], level=2))
    if resolved.get('primary_cta'):
        comps.append(_button(resolved['primary_cta']))
    return _row(comps, section_id=section_id)


def _build_generic(resolved, section_id):
    """Fallback: render whatever resolved slots exist, in a stable order."""
    comps = []
    for slot in ('eyebrow', 'headline', 'subheadline', 'heading'):
        if resolved.get(slot):
            level = 1 if slot == 'headline' else 2
            if slot in ('eyebrow',):
                comps.append(_eyebrow(resolved[slot]))
            else:
                comps.append(_heading(resolved[slot], level=level))
    for slot in ('items', 'pain_points', 'body', 'offer'):
        for v in _as_list(resolved.get(slot)):
            comps.append(_paragraph(v))
    if resolved.get('primary_cta'):
        comps.append(_button(resolved['primary_cta']))
    return _row(comps, section_id=section_id)


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


_BUILDERS = {
    'problem_aware_hero': _build_hero,
    'aspirational_hero': _build_hero,
    'problem_cost': _build_problem_cost,
    'proof_points': _build_proof_points,
    'objection_handling': _build_objection_handling,
    'offer_highlight': _build_offer_highlight,
    'final_cta': _build_final_cta,
}


def build_section(purpose, resolved, section_id=None):
    """Build a renderer component subtree for a section purpose + resolved content."""
    builder = _BUILDERS.get(purpose, _build_generic)
    return builder(resolved, section_id)
