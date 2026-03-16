# Panorama Display Component — Implementation Plan (COMPLETED)

## Context

The `panorama-display` component is a **single panorama image viewer** — a wide image inside a horizontally scrollable container with `overflow-x: auto`. The user scrolls left/right to explore the panorama.

**What it is:** A single wide image (e.g. 3000px+ wide cityscape) displayed at natural height inside a 100%-width container with horizontal scroll.
**What it is NOT:** A multi-item carousel/showcase with child components.

**Component name:** `panorama-display`
**Width:** Always 100% of parent container (fixed)
**Height:** Determined by the actual image height (natural aspect ratio)
**Scrolling:** `overflow-x: auto` on the container, image displayed at natural width
**Allowed parents:** `page` or `layout-column` only

---

## Requirements

- **Single image** — one `source.url` + `source.altText` (same pattern as `image` component)
- **Width:** Always 100% of parent (fixed)
- **Height:** Determined by the actual image height (natural aspect ratio)
- **Scrolling:** `overflow-x: auto` on the container, image displayed at natural width
- **Initial position:** Property to set where the image starts — `left`, `center`, or `right`
- **Arrows:** Left/right arrow buttons for step-based scrolling
- **Drag/swipe:** Mouse drag and touch swipe support
- **Auto-scroll:** Optional continuous scroll (default false)
- **Container styling:** Border, shadow, radius via `build_styles()`

---

## Files Modified (8 files)

| # | File | Action |
|---|------|--------|
| 1 | `templates/components/interactive/_panorama_display.html` | Created |
| 2 | `templates/components/_assembly.html` | Edited — added include |
| 3 | `templates/components/_dispatcher.html` | Edited — added route |
| 4 | `config/component_defaults.yaml` | Edited — added panorama-display defaults |
| 5 | `static/css/components.css` | Edited — added panorama-display CSS |
| 6 | `static/js/swift-sites-runtime.js` | Edited — added init/cleanup/initialPosition |
| 7 | `config/component_schemas.yaml` | Edited — added panorama-display schema |
| 8 | `static/js/componentTree.js` | Edited — added icon mapping |

---

## Implementation Details

### Jinja2 Template

Simple single-image viewer with arrows:
- No `items` array, no child rendering, no gap
- Single `<img>` inside `pd-track` with `max-width: none`
- `build_styles()` handles container appearance (border, shadow, radius, margin)
- Data attributes for JS behavior: `data-initial-position`, `data-auto-scroll`, etc.

### Defaults (`component_defaults.yaml`)

```yaml
panorama-display:
  source:
    url: https://placehold.co/2400x600/e2e8f0/475569?text=Panorama+Image
    altText: Panorama image
  behavior:
    autoScroll: false
    autoScrollSpeed: 30
    stepDistance: 300
    pauseOnHover: true
    initialPosition: left
  spacing:
    marginBlock: md
    marginInline: none
  appearance:
    border:
      width: 0
      style: solid
      color: '#e5e7eb'
    radius: none
    shadow: none
    shadowColor: ''
```

### CSS

- `.panorama-display` — `width: 100%; position: relative; overflow: hidden;`
- `.pd-track` — `overflow-x: auto; scroll-behavior: smooth;` with hidden scrollbar
- `.pd-image` — `display: block; height: auto; max-width: none;` (allows natural width to exceed container)
- `.pd-arrow` — absolute positioned circular buttons with fade via `.pd-arrow-hidden`
- `.is-dragging` — disables smooth scroll during drag
- `.is-auto-scrolling` — disables smooth scroll during auto-scroll

### Runtime JS

- `initPanoramaDisplays()` — iterates all `.panorama-display` elements
- `_initPanoramaDisplay(el)` — arrow clicks, drag, touch, auto-scroll, **initialPosition**
- `initialPosition` logic waits for `img.onload` to set `scrollLeft` to 0 (left), `maxScroll/2` (center), or `maxScroll` (right)
- `cleanupPanoramaDisplays()` — cancels all animation frames

### Schema

Groups: source (url, altText), behavior (initialPosition, stepDistance, autoScroll, autoScrollSpeed, pauseOnHover), spacing (marginBlock, marginInline), appearance (border.*, radius, shadow, shadowColor)

No custom renderer needed — this is a leaf component with no children.

---

## Example YAML

```yaml
- name: panorama-display
  properties:
    source:
      url: https://placehold.co/3000x600/e2e8f0/475569?text=Wide+Panorama+Image
      altText: City skyline panorama
    behavior:
      initialPosition: center
      autoScroll: false
      stepDistance: 300
    spacing:
      marginBlock: lg
    appearance:
      shadow: soft
      shadowColor: '#1e293b'
      radius: md
```

---

## Status: COMPLETED
