# Plan: `grouped-images` Component

## Context

New **collage/scatter-style image container** where multiple images can be freely positioned, overlapping each other. Images scale proportionally since all positions/sizes use percentages. Max 5 images for simplicity.

## Design Decisions

- **Max 5 images**: Fixed limit. The custom editor shows 5 slots; empty URL = image not rendered.
- **Image height**: Natural aspect ratio (`height: auto`). Only `width` (as %) controls size.
- **Z-index**: Determined by array order. Image 1 = furthest back, Image 5 = most forward.
- **Mobile**: Keep overlapping layout at all sizes (no responsive stacking).

## YAML Structure

```yaml
- name: grouped-images
  properties:
    container:
      minHeight: 400        # px
      aspectRatio: auto      # auto, 16/9, 4/3, 1/1, 3/2
      overflow: hidden       # hidden (clip) or visible (bleed)
    appearance:
      background:
        color: '#f3f4f6'
        transparency: 100
      cornerStyle: md
      shadow: none
    spacing:
      marginBlock: md
      marginInline: none
    layout:
      widthMode: stretch
  images:
    - url: 'https://...'      # Image 1 (back-most, z-index: 1)
      altText: 'Photo 1'
      top: 5
      left: 5
      width: 55
      rotation: -3
      cornerStyle: sm
      shadow: md
      filter: none
      fit: cover
    - url: 'https://...'      # Image 2 (z-index: 2)
      top: 15
      left: 35
      width: 45
      rotation: 2
    - url: 'https://...'      # Image 3 (front-most, z-index: 3)
      top: 40
      left: 20
      width: 50
      rotation: -1
    # Max 5 images. Empty url = not rendered.
```

## Files to Modify

### 1. `ssr_python/templates/macros/_components.html`

**Dispatcher:** Add `grouped-images` route in `render_component()`.

**Macro:** `render_grouped_images()`:
- Outer `<div class="grouped-images chrome-target">` with `position: relative; min-height; aspect-ratio; overflow`
- Loop through `images` array (max 5), skip entries with empty/missing `url`
- Each image: `<div class="grouped-images__item" style="position: absolute; top: X%; left: Y%; width: Z%; z-index: {{ loop.index }}; transform: rotate(Ndeg);">`
- `<img>` with `object-fit`, `--base-filter` CSS var, lazy loading, `border-radius` from token
- Shadow from token on the wrapper div
- Empty placeholder when no images have URLs

### 2. `component_defaults.yaml`

Add `grouped-images` entry with 3 pre-filled images (out of max 5).

### 3. `component_schemas.yaml`

Groups: `images` (custom renderer `groupedImagesEditor`, target: `component`), `container`, `appearance`, `layout`, `spacing`.

### 4. `ssr_python/static/js/customRenderers.js`

New `renderGroupedImagesEditor` - **simplified with 5 fixed slots**:
- Renders 5 collapsible sections ("Image 1 (back)" through "Image 5 (front)")
- Each section has: URL input, altText, top %, left %, width %, rotation, cornerStyle select, shadow select, filter select, fit select
- Collapsed by default showing just the URL (or "Empty" if no URL)
- No add/remove buttons needed - just 5 fixed slots
- `serialize()` returns array of up to 5 image objects, filtering out entries with empty URLs
- Uses existing `createElement`, `createInput` helpers
- Register as `groupedImagesEditor` in exports

### 5. `ssr_python/static/css/components.css`

```css
.grouped-images { position: relative; width: 100%; box-sizing: border-box; }
.grouped-images__item { position: absolute; transition: transform 0.3s, box-shadow 0.3s; overflow: hidden; }
.grouped-images__item img { display: block; width: 100%; height: auto; border-radius: inherit; }
.grouped-images__item:hover { z-index: 100 !important; filter: brightness(1.05); }
.grouped-images__placeholder { /* dashed border placeholder */ }
```

No mobile override - overlapping layout preserved at all sizes.

### 6. `ssr_python/static/js/propertiesPanel.js`

Add component icon (`'icon-image'`), category (`'Media'`), section icon entries.

### 7. `LLM_COMPONENT_GUIDE.md`

Add grouped-images docs for AI chat generation.

## Files NOT Changed

- **`renderer.py`** - `images` array has no nested `components`; `deepcopy` preserves it as-is.
- **`pathMapBuilder.js`** - Individual images aren't selectable; the container is the unit.
- **`preview_bridge.js`** / **`component_interactions.js`** - No runtime JS needed.

## Implementation Order

1. Macro + dispatcher + defaults + CSS (renders correctly)
2. Schema + custom renderer + panel metadata (editable via properties panel)
3. LLM guide (AI-generatable)

## Verification

1. Add `grouped-images` to YAML editor with 3 images
2. Verify positions, rotation, shadows, corner radius render correctly
3. Verify z-index follows array order (first = back, last = front)
4. Resize viewport - images scale proportionally
5. Select component - properties panel shows 5 fixed slots
6. Edit image positions via panel - changes apply after re-render
7. Add 4th and 5th images via empty slots
8. Test overflow hidden vs visible
