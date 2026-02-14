# Image Component: Responsive Height Enhancement

## Problem

When the image component's `maxHeight` property is left empty (default value 0), the image does not responsively increase its height. The container stays at the `minHeight` value (default 12.5rem).

## Root Cause

In `_image.html`, the `<img>` element is absolutely positioned (`position: absolute; inset: 0`) inside `.image-wrapper`. This removes the image from the document flow, so it does not contribute to the container's height. The `<figure>` container only grows to its `min-height` because nothing pushes it taller.

When `maxHeight` is empty/0, no `max-height` CSS is output (correct behavior), but the container still cannot grow beyond `min-height` since the image is out of flow.

## Relevant Files

| File | Location | Role |
|------|----------|------|
| `ssr_python/templates/components/media/_image.html` | Lines 23-24, 36-39, 81-87 | Image macro with min/max height logic |
| `ssr_python/static/css/components.css` | Lines 1298-1302 | `.image-container` styles |

## Current Behavior

```
┌──────────────────────────┐
│  <figure> (min-height)   │  ← Only grows to min-height
│  ┌────────────────────┐  │
│  │ <img> absolute pos │  │  ← Doesn't push container height
│  └────────────────────┘  │
└──────────────────────────┘
```

## Proposed Fix

Add `flex-grow: 1` to the `<figure>` element's inline styles when `max_height_raw` is 0/empty. This allows the container to expand and fill its parent's available space.

### Changes

**File: `ssr_python/templates/components/media/_image.html`**

In the inline styles for the `<figure>` element, conditionally add `flex-grow: 1;` when no max-height is set:

```jinja2
{# When no max-height is set, allow container to grow to fill available space #}
{% if not max_height_raw or max_height_raw == 0 %}
    flex-grow: 1;
{% endif %}
```

## Expected Behavior After Fix

```
┌──────────────────────────┐
│  <figure> (flex-grow: 1) │  ← Grows to fill parent
│  ┌────────────────────┐  │
│  │ <img> absolute pos │  │  ← Fills expanded container
│  └────────────────────┘  │
└──────────────────────────┘
```

## Testing

1. Add an image component inside a layout-column
2. Leave `maxHeight` empty (default)
3. Verify the image grows to fill the available vertical space
4. Set `maxHeight` to a specific value and verify it constrains correctly
5. Verify `minHeight` still works as a floor

---

**Status:** Planned
**Created:** February 13, 2026
