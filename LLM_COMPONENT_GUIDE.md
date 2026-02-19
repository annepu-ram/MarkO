# Swift Sites LLM Component Guide

Concise guide for LLMs to generate website YAML using Swift Sites components.

---

## ⚡ CRITICAL QUICK REFERENCE

### Component Structure Rule
```yaml
- name: component-name
  properties:           # ← All configuration HERE
    spacing: {...}
    typography: {...}
    appearance: {...}
  components: [...]     # ← Arrays at COMPONENT LEVEL
```

### Special Array Properties (NEVER inside properties)
| Component | Array Property | Location |
|-----------|----------------|----------|
| accordion | `items:` | Component level (same as `properties:`) |
| tabs | `tabs:` | Component level (same as `properties:`) |
| carousel | `slides:` | Component level (same as `properties:`) |
| columnsgrid | `columns:` | Component level (same as `properties:`) |
| ticker | `columns:` | Component level (data containers like columnsgrid) |
| containers | `components:` | Component level (same as `properties:`) |

### Valid Design Tokens
| Property | Valid Values |
|----------|-------------|
| **Spacing** | `none`, `xxs`, `xs`, `sm`, `md`, `lg`, `xl`, `xxl`, `xxxl`, `auto` |
| **Typography sizes** | `xxs`, `xs`, `sm`, `md`, `lg`, `xl`, `xxl`, `xxxl`, `auto` |
| **Font weights** | `light`, `regular`, `medium`, `semibold`, `bold`, `extrabold` |
| **Shadow** | `none`, `soft`, `medium`, `elevated`, `dramatic`, `retro` |
| **Border radius** | `none`, `xs`, `sm`, `md`, `lg`, `xl`, `xxl`, `pill` |
| **Hover effects** | `none`, `zoom`, `lift` |
| **Width modes** | `fit`, `25`, `50`, `75`, `stretch` |
| **⚠️ Width mode location** | `layout.widthMode: "50"` (NOT `appearance`!) |
| **⚠️ Theme property order** | `theme:` MUST be the FIRST property in page (defines anchors before aliases) |

### Container Components (can nest other components)
`page`, `layout-row`, `layout-column`, `columnsgrid`, `form`, `image`, `gif`, `video-background`

---

## Quick Start

```yaml
- name: page
  properties:
    appearance: { background: { color: '#ffffff' } }
  components:
    - name: heading
      properties:
        text: Hello World
        level: 1
```

**Key Rules:**
- YAML is the source of truth
- Every component has: `name`, `properties`, optional `components`
- Container components: `page`, `layout-row`, `layout-column`, `columnsgrid`, `form`, `image`, `gif`, `video-background`
- Special array properties (`items`, `tabs`, `slides`, `columns`) are at **component level**, NOT inside `properties`

## Critical YAML Structure Rules

**⚠️ MOST COMMON MISTAKES TO AVOID:**

1. **Array properties belong at component level** (same indentation as `properties:`):
   - `columns:` for `columnsgrid`
   - `tabs:` for `tabs` component
   - `items:` for `accordion` component
   - `slides:` for `carousel` component
   - `components:` for container components

2. **All other properties belong INSIDE `properties:`**:
   - `spacing:` ✅ INSIDE properties
   - `typography:` ✅ INSIDE properties
   - `appearance:` ✅ INSIDE properties
   - `layout:` ✅ INSIDE properties
   - `behavior:` ✅ INSIDE properties

3. **Correct component structure pattern:**
```yaml
- name: component-name
  properties:           # ← All configuration properties go here
    spacing: { ... }
    typography: { ... }
    appearance: { ... }
  components: [...]     # ← Array of nested components (component level)
  # OR
  items: [...]          # ← For accordion (component level)
  # OR
  tabs: [...]           # ← For tabs (component level)
  # OR
  slides: [...]         # ← For carousel (component level)
  # OR
  columns: [...]        # ← For columnsgrid (component level)
```

## Design Tokens

### Spacing Scale (8px Grid)

| Token | Desktop | Use Case |
|-------|---------|----------|
| `none` | 0 | Reset margins, no spacing |
| `xxs` | 4px | Tight icon gaps |
| `xs` | 8px | Inline elements, tight groups |
| `sm` | 16px | Component padding (buttons, cards) |
| `md` | 24px | Default gap between elements |
| `lg` | 32px | Section padding |
| `xl` | 48px | Large section separation |
| `xxl` | 64px | Hero section padding |
| `xxxl` | 96px | Page section breaks |
| `auto` | auto | Automatic spacing |

### Typography Sizes

| Token | Use Case | Recommended For |
|-------|----------|-----------------|
| `xxs` | Fine print, legal text | Caption (footnotes), metadata |
| `xs` | Captions, labels, helper text | Eyebrow, Caption |
| `sm` | Secondary body text | Paragraph (secondary), descriptions |
| `md` | Body text (default) | Paragraph, Button text |
| `lg` | H4 headings, emphasized text | Heading level 4, blockquote |
| `xl` | H3 headings, section titles | Heading level 3 |
| `xxl` | H2 headings, major sections | Heading level 2 |
| `xxxl` | H1 hero headlines, page titles | Heading level 1, Hero text |
| `auto` | Inherit from parent | Special cases |

### Font Weights

| Token | Value | Use Case |
|-------|-------|----------|
| `light` | 300 | Delicate, elegant text |
| `regular` | 400 | Body text (default) |
| `medium` | 500 | Slightly emphasized text |
| `semibold` | 600 | Subheadings, labels, eyebrows |
| `bold` | 700 | Headlines, CTAs, emphasis |
| `extrabold` | 800 | Hero text, high impact |

### Letter Spacing

| Token | Value | Use Case |
|-------|-------|----------|
| `normal` | 0 | Body text (default) |
| `tight` | -0.025em | Large headlines (xl/xxl/xxxl sizes) |
| `wide` | 0.025em | Small text readability (xs/xxs) |
| `wider` | 0.05em | **ALWAYS use for UPPERCASE text** |

**Important:** All caps text (like eyebrows with `transform: uppercase`) should use `wider` letter spacing for readability.

### Border Radius

| Token | Use Case |
|-------|----------|
| `none` | Square corners |
| `sm` | Subtle rounding (inputs, small cards) |
| `md` | Standard rounding (cards, buttons) |
| `lg` | Prominent rounding (hero images, modals) |
| `pill` | Fully rounded (pills, tags, circular buttons) |

### Shadow Scale

| Token | Style | Use Case |
|-------|-------|----------|
| `none` | No shadow | Flat design, default |
| `soft` | Subtle ambient shadow | Cards, subtle depth |
| `medium` | Standard lifted shadow | Buttons, containers |
| `elevated` | Prominent depth | Modals, popups |
| `dramatic` | Heavy emphasis | Hero elements, CTAs |
| `retro` | Hard-edge brutalist (4px 4px 0 0) | Neo-brutalism, playful UI |

**Shadow Color (`appearance.shadowColor`):** Optional hex color to tint the shadow. Sets a `--shadow-rgb` CSS variable that overrides the default shadow color. When omitted, shadows use their default gray/black tones.

```yaml
appearance:
  shadow: medium
  shadowColor: '#6366f1'    # Purple-tinted shadow
```

**Components supporting shadow + shadowColor:** layout-row, layout-column, columnsgrid, image, gif, video, button, accordion, tabs, carousel, form, blockquote

### Text Alignment

`left`, `center`, `right`, `justify`

## Width Mode Property (Text & Media Components)

**Applies to:** `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`, `link`, `image`, `gif`

**Property path:** `layout.widthMode`

| Value | Description | Behavior |
|-------|-------------|----------|
| `fit` | Fit to content (default for text/buttons) | Component shrinks to its natural content width |
| `25` | 25% width | Component takes 25% of parent container width |
| `50` | 50% width | Component takes 50% of parent container width |
| `75` | 75% width | Component takes 75% of parent container width |
| `stretch` | Full width (default for media/containers) | Component stretches to fill available width |

**Example:**
```yaml
- name: heading
  properties:
    text: Centered Title
    layout: { widthMode: fit }  # Title only as wide as text
    typography: { align: center }
```

**⚠️ Important:** Width mode works differently based on parent container:
- In `layout-row`: Uses flex-grow proportions (handles gap automatically)
- In `layout-column`: Uses explicit percentage widths (centered by default)

## Horizontal and Vertical Align Properties (Layout Containers)

**Applies to:** `layout-row`, `layout-column`

### layout-row (horizontal flex)

| Property | CSS Property | Description |
|----------|--------------|-------------|
| `layout.horizontalAlign` | `justify-content` | Controls horizontal distribution of children |
| `layout.verticalAlign` | `align-items` | Controls vertical alignment of children |

**Horizontal Align Values (layout-row):**
| Value | CSS | Description |
|-------|-----|-------------|
| `left` | flex-start | Align children to start |
| `center` | center | Center children horizontally |
| `right` | flex-end | Align children to end |
| `stretch` | stretch | Stretch to fill (default) |

**Vertical Align Values (layout-row):**
| Value | CSS | Description |
|-------|-----|-------------|
| `top` | flex-start | Align children to top |
| `center` | center | Center children vertically |
| `bottom` | flex-end | Align children to bottom |
| `stretch` | stretch | Stretch children to fill height (default) |
| `baseline` | baseline | Align children by text baseline |

### layout-column (vertical flex)

| Property | CSS Property | Description |
|----------|--------------|-------------|
| `layout.horizontalAlign` | `align-items` | Controls horizontal alignment of children |
| `layout.verticalAlign` | `justify-content` | Controls vertical distribution of children |

**Horizontal Align Values (layout-column):**
| Value | CSS | Description |
|-------|-----|-------------|
| `left` | flex-start | Align children to left |
| `center` | center | Center children horizontally (default) |
| `right` | flex-end | Align children to right |
| `stretch` | stretch | Stretch children to fill width |

**Vertical Align Values (layout-column):**
| Value | CSS | Description |
|-------|-----|-------------|
| `top` | flex-start | Pack children to top |
| `center` | center | Center children vertically |
| `bottom` | flex-end | Pack children to bottom |
| `space-between` | space-between | Distribute with space between (default) |
| `space-around` | space-around | Distribute with space around |
| `space-evenly` | space-evenly | Distribute with equal space |

**⚠️ Note:** Use `horizontalAlign` and `verticalAlign` — do NOT use the old `align` property (it is ignored).

**Examples:**
```yaml
# Row with children centered both ways
- name: layout-row
  properties:
    layout: { horizontalAlign: center, verticalAlign: center }
  components: [...]

# Column with left-aligned children
- name: layout-column
  properties:
    layout: { horizontalAlign: left }
  components:
    - name: heading
      properties:
        text: Left-Aligned Heading
        layout: { widthMode: fit }
```

**⚠️ Note:** If `horizontalAlign: stretch` is used on layout-column, `widthMode` will be overridden (children stretch to full width regardless of widthMode setting).

## Component Reference (35 Total)

### Layout & Containers (5)

**page** - Root element
```yaml
- name: page
  properties:
    theme:                        # ⚠️ theme MUST come FIRST (defines anchors used below)
      colors:
        background: &color-background '#ffffff'
        primary: &color-primary '#1e293b'
        secondary: &color-secondary '#475569'
        accent: &color-accent '#2563eb'
      fonts:
        heading: &font-heading "'Inter', sans-serif"
        content: &font-content "'Inter', sans-serif"
    spacing: { paddingBlock: md, paddingInline: md }
    appearance: { background: { color: *color-background, transparency: 100 } }
  components: [...]
```

**⚠️ CRITICAL:** `theme` must be the FIRST property inside `properties` because it defines YAML anchors (`&color-primary`) that other properties reference via aliases (`*color-primary`). YAML anchors must be defined before they are used.

**layout-row** - Horizontal flex
```yaml
- name: layout-row
  properties:
    layout: { tag: section, horizontalAlign: center, verticalAlign: center, wrap: wrap, gap: sm }
    spacing: { paddingBlock: md, marginBlock: lg }
    appearance: { background: { color: '#ffffff' }, border: { width: 1, style: solid, color: '#e5e7eb' }, radius: md, shadow: none, shadowColor: '', blur: false }
  components: [...]
```

**Backdrop Blur (`appearance.blur`):** Boolean checkbox. When `true`, applies `backdrop-filter: blur(10px)` for a frosted-glass effect. Automatically makes the background 50% transparent if currently opaque, so the blur is visible through the chosen background color. Works with any background color. If the transparency slider is already > 0, that value is kept.

**Wrap Property:**
| Value | Behavior |
|-------|----------|
| `wrap` | Children wrap to next line when space insufficient |
| `nowrap` | Children stay on single line, may squeeze or overflow |

**Gap Property (layout-row and layout-column):**
| Value | Size |
|-------|------|
| `none` | No gap |
| `xxs` | Extra extra small |
| `xs` | Extra small |
| `sm` | Small (default for layout-row) |
| `md` | Medium |
| `lg` | Large |
| `xl` | Extra large |
| `xxl` | Extra extra large |
| `xxxl` | Extra extra extra large |

**Note:** `layout-row` defaults to `gap: sm` so children have spacing between them. Use `gap: none` to remove spacing, or increase to `md`, `lg`, etc. for more space. Use `wrap: wrap` to allow children to wrap to the next line when they exceed the row width. Children with `widthMode` (25%, 50%, etc.) will respect their width and wrap correctly. For distribution-style spacing, use `horizontalAlign` with values like `space-between`, `space-evenly`, or `space-around`.

**⚠️ CRITICAL: Preventing Horizontal Overflow in layout-row**

By default, media and container components have `widthMode: stretch` which renders as `flex: 1 0 100%` (100% basis, no shrink), while text and button components default to `widthMode: fit`. When multiple media/container children are placed in a `layout-row` without explicit width modes, **each child tries to be 100% wide, causing horizontal overflow and scrollbars**.

**Rule:** Always set explicit `widthMode` on children of a `layout-row` to prevent overflow. Divide 100% by the number of side-by-side children.

| Children Count | widthMode per child | Use case |
|----------------|---------------------|----------|
| 2 side-by-side | `50` each | Split screen, two-column layouts |
| 3 side-by-side | `33` each | Three-column cards, stats rows |
| 4 side-by-side | `25` each | Four-column grids, award rows |
| Variable size  | `fit` each | Navigation items, tags, badges |
| Stacked (vertical) | `stretch` + `wrap: wrap` | Full-width rows that wrap |

**⚠️ CRITICAL: Where to set widthMode**

**ALL components MUST use `layout.widthMode`** - the rendering engine ONLY reads this property path.

| Component Type | Correct Path | ❌ WRONG Path |
|----------------|--------------|---------------|
| layout-column | `layout.widthMode: "50"` | ~~`appearance.widthMode: 50`~~ |
| layout-row | `layout.widthMode: "50"` | ~~`appearance.widthMode: 50`~~ |
| image, gif | `layout.widthMode: "50"` | ~~`appearance.widthMode: 50`~~ |
| text components | `layout.widthMode: "50"` | ~~`appearance.widthMode: 50`~~ |

**Why:** The Jinja2 rendering engine in `_components.html` only reads `properties.layout.widthMode` (line 1455). If widthMode is under `appearance`, it defaults to `'stretch'` which causes 100% width and horizontal overflow in rows.

**Examples:**
```yaml
# ✅ CORRECT: 3 cards side-by-side (33% each)
- name: layout-row
  properties:
    layout: { horizontalAlign: space-evenly }
  components:
    - name: layout-column
      properties:
        layout: { widthMode: "33" }
      components: [...]
    - name: layout-column
      properties:
        layout: { widthMode: "33" }
      components: [...]
    - name: layout-column
      properties:
        layout: { widthMode: "33" }
      components: [...]

# ✅ CORRECT: 2 columns split screen
- name: layout-row
  properties:
    layout: { horizontalAlign: space-evenly }
  components:
    - name: layout-column
      properties:
        layout: { widthMode: "50" }
      components: [...]
    - name: image
      properties:
        layout: { widthMode: "50" }

# ❌ WRONG: No widthMode — causes horizontal overflow!
- name: layout-row
  properties:
    layout: { horizontalAlign: space-evenly }
  components:
    - name: layout-column
      components: [...]    # defaults to stretch (100%) → overflow
    - name: layout-column
      components: [...]    # defaults to stretch (100%) → overflow
```

**Valid widthMode values (all as strings in YAML):** `"fit"`, `"16"`, `"25"`, `"33"`, `"50"`, `"66"`, `"75"`, `"83"`, `"stretch"`. Always quote numeric values in YAML (e.g., `widthMode: "50"` not `widthMode: 50`).

**layout-column** - Vertical flex
```yaml
- name: layout-column
  properties:
    layout: { tag: section, horizontalAlign: center }
    spacing: { paddingBlock: md, marginBlock: lg }
    appearance: { blur: false }
  components: [...]
```

Layout-column also supports `appearance.blur` (same behavior as layout-row).

**columnsgrid** - Responsive grid
```yaml
- name: columnsgrid
  properties:                                    # ← Configuration
    layout: { columns: 3, gap: lg, verticalAlign: center }
    responsive: { breakpoints: { md: 2, sm: 1 } }
    spacing: { marginBlock: lg }
    appearance:
      columnBackground: '#ffffff'                # Background color for all columns
      columnTransparency: 0                      # Column transparency 0-100%
      columnBlur: false                          # Backdrop blur on columns (auto-applies 50% transparency when true)
      columnRadius: none                         # Column border radius (none, xs, sm, md, lg, xl, xxl, pill)
  columns:                                       # ← AT COMPONENT LEVEL (not inside properties)
    - components: [...]
    - components: [...]
    - components: [...]
```

**Column Appearance:** Columnsgrid columns support uniform appearance settings applied to all columns. These follow the same pattern as the ticker component's column properties.

**form** - Form wrapper
```yaml
- name: form
  properties:
    layout: { direction: column }
    submit: { show: true, buttonText: Submit }
  components: [...]
```

### Text (5)

**heading** - h1-h6
```yaml
- name: heading
  properties:
    text: Title
    level: 1
    typography: { size: xl, weight: bold, color: '#000000', align: center }
    spacing: { marginBlock: md }
```

**paragraph** - Body text (supports multiline with `|`)
```yaml
- name: paragraph
  properties:
    text: |
      Multi-line text
      supported here
    typography: { size: md, color: '#333333' }
    layout: { widthMode: stretch }  # fit, 25, 50, 75, or stretch
    spacing: { marginBlock: md }
    appearance: { background: { color: '#ffffff', transparency: 100 } }
```

**eyebrow** - Small label
```yaml
- name: eyebrow
  properties:
    text: NEW FEATURE
    typography: { size: xs, weight: semibold, transform: uppercase }
```

**caption** - Image caption
```yaml
- name: caption
  properties:
    text: Photo by John
    typography: { size: xs, color: '#888888' }
```

**blockquote** - Quote
```yaml
- name: blockquote
  properties:
    quote: Great quote here
    cite: Jane Doe
    typography: { size: xl, weight: medium, color: '#111827' }
    appearance: { border: { accentColor: '#6366f1' }, background: { color: '#ffffff' }, shadow: none, shadowColor: '' }
```

**Accent Color System:** The `accentColor` property flows through a CSS variable (`--blockquote-border`) to style:
1. Left border (5px solid)
2. Background gradient (8% tint)
3. Quotation marks (::before/::after decorative quotes)
4. Citation text color

Changing `accentColor` updates all four elements automatically.

### Media (5)

**image** - Display image with optional overlay content
```yaml
- name: image
  properties:
    source: { url: 'https://...jpg', altText: 'Description' }
    appearance:
      minHeight: 200             # Minimum height in pixels
      fit: cover                 # cover, contain, fill, none
      aspectRatio: '16/9'        # auto, 16/9, 4/3, 1/1, 3/2, 21/9, 9/16
      objectPosition: center     # center, top, bottom, left, right, top left, etc.
      cornerStyle: md            # none, xs, sm, md, lg, xl, xxl, pill
      filter: none               # none, grayscale, sepia, blur, brighten, darken, saturate
      shadow: medium             # none, soft, medium, elevated, dramatic, retro
      shadowColor: ''            # hex color to tint shadow (e.g. '#6366f1'), empty = default
      hoverEffect: zoom          # none, zoom, lift
      lazy: true                 # Lazy loading
      overlay:
        enabled: false
        color: 'rgba(0,0,0,0.5)'
        opacity: 50
    layout: { widthMode: stretch, horizontalAlign: center }
  components: [...]              # Optional overlay content (text, buttons)
```

**gif** - Animated GIF
```yaml
- name: gif
  properties:
    source: { url: 'https://...gif', altText: 'Animation' }
    appearance:
      fit: cover                 # cover, contain, fill, none
      aspectRatio: auto          # auto, 16/9, 4/3, 1/1, etc.
      objectPosition: center     # center, top, bottom, left, right
      cornerStyle: none          # none, xs, sm, md, lg, xl, xxl, pill
      filter: none               # none, grayscale, sepia, blur, brighten, darken, saturate
      shadow: none               # none, soft, medium, elevated, dramatic, retro
      shadowColor: ''            # hex color to tint shadow, empty = default
      overlay:
        enabled: false
        color: 'rgba(0,0,0,0.5)'
        opacity: 50
    layout: { widthMode: stretch }
```

**video** - YouTube/Vimeo embed
```yaml
- name: video
  properties:
    source: { url: 'https://www.youtube.com/watch?v=VIDEO_ID' }
    appearance:
      aspectRatio: '16/9'        # 16/9, 4/3, 1/1, 21/9
      height: 400                # Height in pixels
    playback:
      controls: true
      autoplay: false
      muted: false
      loop: false
    poster: { url: '' }          # Poster image URL
    spacing: { marginBlock: md }
```

**video-background** - Full-width video background with overlay content
```yaml
- name: video-background
  properties:
    source:
      url: 'https://example.com/video.mp4'  # Direct MP4/WebM URL
      poster: ''                 # Fallback image while loading
    appearance:
      aspectRatio: '16/9'
      minHeight: 400
      objectFit: cover           # cover, contain, fill
      objectPosition: center     # center, top, bottom, left, right
      overlay:
        enabled: true
        color: 'rgba(0,0,0,0.4)'
        opacity: 40
    playback:
      autoplay: true
      loop: true
      muted: true                # Required for autoplay
      playsinline: true          # Important for mobile
    content:
      verticalAlign: center      # start, center, end
      horizontalAlign: center    # left, center, right
      padding: md
    layout: { widthMode: stretch }
  components:                    # Overlay content (headings, buttons, etc.)
    - name: heading
      properties:
        text: Hero Title
        typography: { color: '#ffffff', size: xxxl, align: center }
    - name: button
      properties:
        text: Learn More
```

**br** - Divider / visual separator
```yaml
- name: br
  properties:
    type: solid                  # solid, dashed, dotted, wave, slant
    orientation: horizontal      # horizontal, vertical
    thickness: 2                 # Line thickness in px (1-10)
    color: '#e5e7eb'             # Line color (hex)
    size: md                     # Spacing above/below (spacing token)
    invert: false                # Flip vertically (top↔bottom)
    mirror: false                # Flip horizontally (left↔right)
```

**Divider types:**
| Type | Rendering | Use Case |
|------|-----------|----------|
| `solid` | CSS border-bottom (default) | Standard section divider |
| `dashed` | CSS dashed border | Subtle separation |
| `dotted` | CSS dotted border | Light visual break |
| `wave` | SVG filled wave shape | Decorative section transitions |
| `slant` | SVG diagonal polygon | Angled section transitions |

**Wave divider:** Renders as a filled wave shape (not just a stroke line). The filled area extends downward from the wave curve, creating a smooth section transition effect.

**Invert & Mirror:**
| Property | Effect | Use Case |
|----------|--------|----------|
| `invert: true` | Flips vertically (`scaleY(-1)`) | Wave/slant fill faces upward instead of down. For solid/dashed/dotted, moves line from bottom to top edge. |
| `mirror: true` | Flips horizontally (`scaleX(-1)`) | Reverses slant direction (left-to-right ↔ right-to-left). Mirrors wave pattern. |

Both can be combined for a full 180-degree rotation.

**Examples:**
```yaml
# Wave transition between sections (fill faces up)
- name: br
  properties:
    type: wave
    thickness: 5
    color: '#6366f1'
    invert: true

# Slant going right-to-left
- name: br
  properties:
    type: slant
    thickness: 4
    color: '#f8fafc'
    mirror: true
```

**Orientation:** Use `vertical` inside a `layout-row` to create a vertical separator between items. Vertical dividers render as `border-left`.

**Backward compatible:** Existing YAML with only `size` still works (defaults to solid horizontal, no invert/mirror).

### Navigation (3)

**titlebar** - Header/navbar with sticky scroll behavior
```yaml
- name: titlebar
  properties:
    branding: { showLogo: true, logoUrl: 'https://...png', title: 'Website' }
    navigation:
      links:
        - label: Home
          href: '#home'
        - label: About
          href: '#about'
    layout: { alignment: left, height: 60 }
    scroll:
      shrinkPercentage: 70        # Shrink TO 70% of original size when scrolled (0-100)
    appearance:
      background: { color: '#ffffff' }
      border: { width: 1, color: '#e5e7eb' }
      focus: { background: '#f0f0f0', color: '#111827' }  # Focus state styling for accessibility
```

**Titlebar scroll behavior:**
- Titlebar becomes sticky on scroll (uses clone-based approach)
- Logo and title shrink by `shrinkPercentage` when scrolled (default: 30%)
- Menu items do NOT shrink - only logo and title

**link** - Hyperlink
```yaml
- name: link
  properties:
    text: Click here
    href: https://example.com
    appearance: { color: '#2563eb', underline: true, showArrow: true }
```

**hamburger** - Mobile menu
```yaml
- name: hamburger
  properties:
    label: Menu
    links: [{ label: Home, href: '#' }]
```

### Interactive (3)

**accordion** - Expandable sections (supports nested components!)
```yaml
- name: accordion
  properties:                                    # ← Configuration properties
    behavior: { allowMultipleOpen: false }
    typography:
      title: { size: lg, weight: semibold, color: '#000000' }
      content: { size: md, weight: regular, color: '#000000' }
    appearance:
      titleBackground: { color: '#ffffff' }
      contentBackground: { color: '#ffffff', transparency: 100 }
      border: { width: 1, style: solid, color: '#d1d5db', position: bottom }
      radius: sm
    spacing: { marginBlock: md }
  items:                                         # ← AT COMPONENT LEVEL (not inside properties)
    - title: Question 1
      components:                                # ← Nested components for content
        - name: paragraph
          properties: { text: Answer 1 with formatting support. }
    - title: Question 2
      components:
        - name: paragraph
          properties: { text: Answer with formatting and components }
        - name: button
          properties: { text: Learn More }
```

**Accordion items use nested components for content.** Add paragraph, image, button, or any other component inside `components:` array.

**⚠️ CRITICAL:** `items:` must be at the same indentation level as `properties:`, NOT inside it!

**tabs** - Tabbed interface
```yaml
- name: tabs
  properties:                                    # ← Configuration properties
    layout: { orientation: horizontal, widthMode: stretch }
    typography:
      label:
        size: md
        weight: semibold
        active: { color: '#000000' }
        inactive: { color: '#6b7280' }
    appearance:
      tab:
        background: { active: '#ffffff', inactive: '#f5f5f5' }
        border: { width: 2, style: solid, position: lower }
      content:
        background: { color: '#ffffff', transparency: 100 }
        border: { color: '#e5e7eb', width: 1, style: solid }
        padding: { block: lg, inline: lg }
    spacing: { marginBlock: lg }
  tabs:                                          # ← AT COMPONENT LEVEL (not inside properties)
    - title: Tab 1
      components:
        - name: paragraph
          properties: { text: Tab 1 content }
    - title: Tab 2
      components:
        - name: paragraph
          properties: { text: Tab 2 content }
```

**⚠️ CRITICAL:** `tabs:` must be at the same indentation level as `properties:`, NOT inside it!

**carousel** - Image slideshow
```yaml
- name: carousel
  properties:                                    # ← Configuration properties
    behavior:
      autoplay: true
      delay: 4000
      loop: true
      pauseOnHover: true
      swipeEnabled: true
      swipeThreshold: 50
      keyboardNavigation: true
    animation:
      effect: slide                              # slide, fade
      duration: 500
    navigation:
      showArrows: true
      arrowStyle: default                        # default, minimal, bold
      arrowPosition: inside                      # inside, outside
      showDots: true
    indicators:
      style: dots                                # dots, dashes, numbers
      position: bottom                           # bottom, top
    accessibility:
      showPauseButton: true
      ariaLabel: "Image carousel"
    appearance:
      shadow: none                               # none, soft, medium, elevated, dramatic, retro
      shadowColor: ''                            # hex color to tint shadow, empty = default
    spacing: { marginBlock: lg }
  slides:                                        # ← AT COMPONENT LEVEL (not inside properties)
    - components:
        - name: image
          properties:
            source: { url: 'https://...jpg', altText: 'Slide 1' }
            appearance: { fit: cover, cornerStyle: lg, aspectRatio: '16/9' }
    - components:
        - name: image
          properties:
            source: { url: 'https://...jpg', altText: 'Slide 2' }
            appearance: { fit: cover, cornerStyle: lg, aspectRatio: '16/9' }
```

**⚠️ CRITICAL:** `slides:` must be at the same indentation level as `properties:`, NOT inside it!

### Form Fields (7)

**button**
```yaml
- name: button
  properties:
    text: Click Me
    action: { type: link, value: https://example.com }
    appearance: { background: { color: '#2563eb' }, padding: { block: sm, inline: md } }
    typography: { color: '#ffffff', weight: semibold }
```

**textbox**
```yaml
- name: textbox
  properties:
    label: { text: Email, show: true }
    field: { placeholder: your@email.com, required: true }
    appearance: { border: { width: 1, color: '#ccc' }, background: { color: '#fff' } }
```

**textarea**
```yaml
- name: textarea
  properties:
    label: { text: Message, show: true }
    field: { placeholder: Type here, rows: 5, required: false }
```

**dropdown**
```yaml
- name: dropdown
  properties:
    label: { text: Choose, show: true }
    field: { options: "Option 1\nOption 2\nOption 3", selected: Option 1 }
```

**checkbox**
```yaml
- name: checkbox
  properties:
    label: { text: Agree }
    field: { text: I agree, checked: false, required: false }
    appearance: { color: '#2563eb' }
```

**radio**
```yaml
- name: radio
  properties:
    label: { text: Select }
    field: { text: Option, groupName: color, value: red, checked: false }
```

**calendar**
```yaml
- name: calendar
  properties:
    display: { month: 8, year: 2024 }
```

### Marketing (7)

**icon** - Google Material Icons icon
```yaml
- name: icon
  properties:
    name: star                   # Any valid Material Icons name (snake_case)
    size: md                     # typographySizes token (xxs-xxxl)
    color: '#111827'             # Icon color (hex)
```

**Any valid [Google Material Icons](https://fonts.google.com/icons) name works** (~2700 icons available). Icon names use snake_case.

**Common icons:** `star`, `favorite`, `check_circle`, `shopping_cart`, `home`, `search`, `settings`, `person`, `mail`, `phone`, `location_on`, `schedule`, `visibility`, `language`, `lock`, `download`, `play_circle`, `arrow_forward`, `chevron_right`, `local_fire_department`, `bar_chart`, `cloud`, `shield`, `palette`, `bolt`, `group`, `thumb_up`, `sell`

**badge** - Colored inline label
```yaml
- name: badge
  properties:
    text: "NEW"                  # Badge text
    variant: info                # info (blue), success (green), warning (amber), danger (red)
    pill: true                   # true = fully rounded, false = slight rounding
    typography:
      color: '#ffffff'           # Override text color (optional, default white)
```

**Variant colors:**
| Variant | Background | Use Case |
|---------|-----------|----------|
| `info` | #2563eb (blue) | General info, categories |
| `success` | #059669 (green) | Positive status, online |
| `warning` | #d97706 (amber) | Attention, popular, deals |
| `danger` | #dc2626 (red) | Urgent, sale, limited |

**rating** - Star/heart rating display (supports half values)
```yaml
- name: rating
  properties:
    value: 3.5                   # Rating value (0-5, step 0.5)
    iconType: star               # star or heart
    showCount: true              # Show "3.5/5" text after icons
    color: '#f59e0b'             # Filled icon color (unfilled = #d1d5db)
    typography:
      size: md                   # Icon size (typographySizes token)
      color: '#6b7280'           # Count text color
```

**Half-star support:** Use decimal values like `3.5`, `4.5`, etc. The fractional part (>= 0.5) renders a half-filled icon (left half filled, right half outline). Integer values render fully filled/empty icons as before.

**Examples:**
| Value | Renders |
|-------|---------|
| `5` | 5 filled |
| `4.5` | 4 filled + 1 half |
| `3` | 3 filled + 2 empty |
| `2.5` | 2 filled + 1 half + 2 empty |
| `0` | 5 empty |

**progress-bar** - Horizontal completion bar
```yaml
- name: progress-bar
  properties:
    percent: 75                  # Progress 0-100 (clamped)
    thickness: medium            # small (0.5rem), medium (1rem), large (1.5rem)
    color: '#3b82f6'             # Fill bar color
    trackColor: '#e5e7eb'        # Background track color
    colorGradient: false         # true = red→amber→green gradient (overrides color)
    appearance:
      radius: pill               # Corner radius (borderRadiusScale token)
```

**counter-up** - Animated number counter (viewport-triggered)
```yaml
- name: counter-up
  properties:
    endValue: 12500              # Target number to count to
    duration: 2000               # Animation duration in ms
    prefix: "$"                  # Text before number (e.g. "$", "#")
    suffix: "+"                  # Text after number (e.g. "+", "%", "M")
    typography:
      size: xxxl                 # typographySizes token
      weight: extrabold          # fontWeights token
      color: '#111827'           # Text color
      align: center              # Alignment
```

**Runtime:** Uses IntersectionObserver to trigger animation when scrolled into view. Ease-out cubic easing. Numbers display with locale formatting (e.g., 12,500). Uses `tabular-nums` for stable digit widths.

**countdown** - Live countdown timer
```yaml
- name: countdown
  properties:
    targetDate: '2026-12-31T23:59:59'  # ISO 8601 date string
    format: 'DD:HH:MM:SS'       # DD:HH:MM:SS, HH:MM:SS, or MM:SS
    expiredText: 'Offer ended!'  # Shown when timer reaches zero
    typography:
      size: xxl                  # typographySizes token
      weight: bold               # fontWeights token
      color: '#ffffff'           # Text color
      align: center              # Alignment
```

**Format options:**
| Format | Segments Shown |
|--------|---------------|
| `DD:HH:MM:SS` | Days, Hours, Min, Sec |
| `HH:MM:SS` | Hours, Min, Sec |
| `MM:SS` | Min, Sec |

**Runtime:** Ticks every second via `setInterval`. When expired, replaces content with `expiredText`. Intervals cleaned up in `SwiftSites.reset()`.

## Quick Patterns

### Hero Section
```yaml
- name: image
  properties:
    source: { url: 'https://...jpg', altText: Background }
    appearance: { minHeight: 600, fit: cover }
    layout: { widthMode: stretch }
  components:
    - name: layout-column
      properties: { layout: { horizontalAlign: center }, spacing: { paddingBlock: xl } }
      components:
        - name: heading
          properties: { text: Welcome, level: 1, typography: { color: '#fff', size: xxxl, weight: bold } }
        - name: paragraph
          properties: { text: Tagline, typography: { color: '#fff' }, spacing: { marginBlock: md } }
        - name: button
          properties: { text: Get Started, appearance: { background: { color: '#2563eb' } } }
```

### 3-Column Card Grid
```yaml
- name: columnsgrid
  properties:
    layout: { columns: 3, gap: lg }
    responsive: { breakpoints: { md: 2, sm: 1 } }
  columns:
    - components:
        - name: image
          properties: { source: { url: '...' }, appearance: { minHeight: 200, fit: cover } }
        - name: heading
          properties: { text: Feature 1, level: 3 }
        - name: paragraph
          properties: { text: Description }
    - components: [...]
    - components: [...]
```

### Pricing Table
```yaml
- name: columnsgrid
  properties: { layout: { columns: 3, gap: lg } }
  columns:
    - components:
        - name: heading
          properties: { text: Starter, level: 3, typography: { align: center } }
        - name: paragraph
          properties: { text: $29/mo, typography: { align: center, size: lg, weight: bold, color: '#2563eb' } }
        - name: paragraph
          properties: { text: "✓ Feature 1\n✓ Feature 2\n✓ Feature 3" }
        - name: button
          properties: { text: Get Started }
    - components: [...]
    - components: [...]
```

### Team Grid
```yaml
- name: columnsgrid
  properties: { layout: { columns: 3, gap: lg }, responsive: { breakpoints: { md: 2, sm: 1 } } }
  columns:
    - components:
        - name: image
          properties: { source: { url: '...' }, appearance: { minHeight: 300, fit: cover } }
        - name: heading
          properties: { text: Name, level: 3, typography: { align: center, weight: bold } }
        - name: eyebrow
          properties: { text: ROLE, typography: { color: '#2563eb' } }
        - name: paragraph
          properties: { text: Bio, typography: { align: center, size: sm } }
    - components: [...]
    - components: [...]
```

### Statistics Section (with animated counters)
```yaml
- name: layout-row
  properties:
    layout: { horizontalAlign: center, wrap: wrap }
    spacing: { paddingBlock: xxl }
  components:
    - name: layout-column
      properties: { layout: { horizontalAlign: center, widthMode: "25" } }
      components:
        - name: counter-up
          properties: { endValue: 10000, suffix: "+", typography: { size: xxxl, weight: bold, color: '#2563eb', align: center } }
        - name: paragraph
          properties: { text: Active Users, typography: { align: center, size: sm } }
    - name: layout-column
      properties: { layout: { horizontalAlign: center, widthMode: "25" } }
      components:
        - name: counter-up
          properties: { endValue: 99, suffix: "%", typography: { size: xxxl, weight: bold, color: '#2563eb', align: center } }
        - name: paragraph
          properties: { text: Uptime, typography: { align: center, size: sm } }
    # ... more columns
```

### Newsletter Signup
```yaml
- name: layout-row
  properties:
    layout: { horizontalAlign: center, verticalAlign: center, gap: lg }
    spacing: { paddingBlock: xl, paddingInline: lg }
    appearance: { background: { color: '#f0f4f8' }, radius: md }
  components:
    - name: layout-column
      components:
        - name: heading
          properties: { text: Stay Updated, level: 3, typography: { weight: bold } }
        - name: paragraph
          properties: { text: Get latest updates, typography: { size: sm } }
    - name: form
      properties: { layout: { direction: row }, submit: { show: false } }
      components:
        - name: textbox
          properties: { label: { show: false }, field: { placeholder: your@email.com } }
        - name: button
          properties: { text: Subscribe }
    - name: paragraph
      properties: { text: No spam, unsubscribe anytime, typography: { size: xs, color: '#999' } }
```

### More Pattern Ideas

**Before/After Comparison:** Use Team Grid pattern with 2 columns. Add red `#ef4444` for "Before" heading, green `#10b981` for "After". Use ✗ and ✓ symbols in paragraphs.

**Features with Image:** Use Hero Section pattern. Replace overlay content with a layout-row containing image + layout-column with feature list.

**CTA Banner Variants:** Use Footer CTA pattern, change colors:
- **Warning:** Yellow bg `#fbbf24`, brown text `#78350f`
- **Success:** Green bg `#d1fae5`, dark green text `#065f46`
- **Info:** Blue bg `#2563eb`, white text `#fff`

### Footer CTA
```yaml
- name: layout-row
  properties:
    layout: { horizontalAlign: center, verticalAlign: center, wrap: wrap }
    spacing: { paddingBlock: xl }
    appearance: { background: { color: '#1f2937' } }
  components:
    - name: layout-column
      components:
        - name: heading
          properties: { text: Ready to Start?, level: 2, typography: { color: '#fff', weight: bold, size: xl } }
        - name: paragraph
          properties: { text: Join thousands today, typography: { color: '#d1d5db' } }
    - name: layout-row
      properties: { layout: { horizontalAlign: center, verticalAlign: center } }
      components:
        - name: button
          properties: { text: Free Trial, appearance: { background: { color: '#2563eb' } } }
        - name: button
          properties: { text: Schedule Demo, appearance: { background: { color: '#fff' } }, typography: { color: '#1f2937' } }
```

### Product Card with Badge & Rating
```yaml
- name: layout-column
  properties:
    appearance: { background: { color: '#ffffff' }, radius: lg, shadow: medium }
    spacing: { paddingBlock: lg, paddingInline: lg }
  components:
    - name: layout-row
      properties: { layout: { horizontalAlign: left, wrap: nowrap, gap: sm } }
      components:
        - name: heading
          properties: { text: "Premium Widget", level: 3, layout: { widthMode: fit } }
        - name: badge
          properties: { text: "SALE", variant: danger, pill: true, layout: { widthMode: fit } }
    - name: rating
      properties: { value: 4.5, iconType: star, showCount: true, color: '#f59e0b' }
    - name: paragraph
      properties: { text: "High-quality widget with premium features." }
    - name: progress-bar
      properties: { percent: 15, thickness: small, color: '#ef4444', trackColor: '#fee2e2' }
    - name: caption
      properties: { text: "Only 15% left in stock!", typography: { size: xs, color: '#ef4444' } }
```

### Launch Countdown Banner
```yaml
- name: layout-column
  properties:
    appearance: { background: { type: gradient, gradient: { colorStart: '#1e1b4b', colorEnd: '#6366f1', direction: to right } } }
    spacing: { paddingBlock: xl }
    layout: { horizontalAlign: center }
  components:
    - name: badge
      properties: { text: "COMING SOON", variant: warning, pill: true }
    - name: heading
      properties: { text: "Product Launch", level: 2, typography: { color: '#fff', size: xxl, align: center } }
    - name: countdown
      properties:
        targetDate: '2026-12-31T23:59:59'
        format: 'DD:HH:MM:SS'
        expiredText: 'We are live!'
        typography: { size: xxl, weight: bold, color: '#ffffff', align: center }
```

### Feature Row with Icons
```yaml
- name: layout-row
  properties: { layout: { horizontalAlign: center, wrap: wrap } }
  components:
    - name: layout-column
      properties: { layout: { horizontalAlign: center, widthMode: "33" } }
      components:
        - name: icon
          properties: { name: fire, size: xxl, color: '#6366f1' }
        - name: heading
          properties: { text: "Fast", level: 3, typography: { align: center } }
        - name: paragraph
          properties: { text: "Lightning quick performance", typography: { align: center, size: sm } }
    # ... repeat for more features
```

## Common Mistakes & Fixes

> **📌 See Quick Reference Card at top of document for structure rules and valid tokens.**

**❌ WRONG - items inside properties:**
```yaml
- name: accordion
  properties:
    items:                 # ← WRONG! Will cause iteration error
      - title: Q1
        components: [...]
```

**✅ CORRECT - items at component level:**
```yaml
- name: accordion
  properties:
    behavior: { allowMultipleOpen: false }
  items:                   # ← CORRECT! At component level
    - title: Q1
      components:          # ← Use nested components for content
        - name: paragraph
          properties: { text: Answer 1 }
    - title: Q2
      components:
        - name: paragraph
          properties: { text: Rich answer with formatting }
        - name: image
          properties: { source: { url: 'https://example.com/img.jpg' } }
```

**Accordion uses nested components for content.** Each item has a `title` and `components` array.

**❌ WRONG - spacing outside properties:**
```yaml
- name: heading
  properties:
    text: Title
    typography: { size: xl }
  spacing: { marginBlock: md }  # ← WRONG! Outside properties
```

**✅ CORRECT - spacing inside properties:**
```yaml
- name: heading
  properties:
    text: Title
    typography: { size: xl }
    spacing: { marginBlock: md }  # ← CORRECT! Inside properties
```

**❌ WRONG - duplicate layout property:**
```yaml
- name: form
  properties:
    layout: { direction: column }
    spacing: { marginBlock: lg }
    layout: { widthMode: 75 }      # ← WRONG! Duplicate key
```

**✅ CORRECT - merged layout property:**
```yaml
- name: form
  properties:
    layout: { direction: column, widthMode: 75 }  # ← CORRECT! Merged
    spacing: { marginBlock: lg }
```

## Complete Examples

See `example_templates/` folder:
- `bookstore_template.yaml` - Full bookstore website
- `freshchoice_template.yaml` - Patisserie/bakery website
- `marketing_components_template.yaml` - SaaS landing page showcasing all marketing components

See `example_templates/tests/` for per-component test files:
- `br_divider_test.yaml` - All divider types, orientations, thickness
- `icon_test.yaml` - Icon sizes, all available icons, colors
- `badge_test.yaml` - Variants, pill shape, real-world usage
- `rating_test.yaml` - Star/heart, value scale, showCount, sizes
- `progress_bar_test.yaml` - Percent values, thickness, gradient, custom colors
- `counter_up_test.yaml` - Prefix/suffix, duration, animated counters
- `countdown_test.yaml` - Format options, expired state, launch countdown

## Key Principles

1. **Always use design tokens** for consistency (colors, spacing, sizes) - Invalid values will throw validation errors
2. **Mobile-first responsive design**: Use columnsgrid with responsive breakpoints
3. **Semantic HTML**: Use proper heading levels (h1 once, h2 for sections, h3 for subsections)
4. **Accessibility**: Always include altText on images, label form fields
5. **Width modes for text components**: 
   - `fit` - Fits content width
   - `25` - 25% width
   - `50` - 50% width
   - `75` - 75% width
   - `stretch` - Full width (100%)
6. **Transparency**: Values 0-100 are converted to hex alpha (0 = fully transparent, 100 = fully opaque)
7. **Color palette**: Primary (#2563eb), Secondary (#7a9b7f), Text (#333), Muted (#666), Light (#f0f0f0)

## Common Property Patterns

```yaml
# Spacing (all components)
spacing:
  marginBlock: md      # top + bottom margin
  marginInline: lg     # left + right margin
  paddingBlock: sm     # top + bottom padding
  paddingInline: md    # left + right padding

# Typography (text components)
typography:
  size: md             # token
  weight: bold         # token
  color: '#000000'     # hex
  align: center        # token
  lineHeight: "1.5"    # CSS value

# Appearance (containers)
appearance:
  background: 
    color: '#ffffff'      # hex color (required)
    transparency: 100     # 0-100 (0=transparent, 100=opaque) - converts to hex alpha
  border: { width: 1, style: solid, color: '#ccc' }
  radius: md              # token: none, sm, md, lg, pill
  shadow: medium            # token: none, soft, medium, elevated, dramatic, retro
  shadowColor: '#6366f1'   # hex color to tint shadow (sets --shadow-rgb CSS variable)
  padding:
    block: md             # top + bottom padding (token)
    inline: md            # left + right padding (token)

# Layout (containers)
layout:
  tag: section            # semantic HTML
  horizontalAlign: center # flexbox alignment or distribution (center, left, right, space-between, space-evenly, space-around)
  verticalAlign: center   # flexbox vertical alignment (layout-row: align-items, layout-column: justify-content)
  wrap: wrap              # flex-wrap (wrap or nowrap)
  gap: sm                 # spacing between children (none, xxs, xs, sm, md, lg, xl, xxl, xxxl)
```

---

## Property Validation

**Never use empty strings for property values.** An empty string (`""` or `''`) is invalid for all properties. If you don't want to set a property, omit it entirely — the default from `component_defaults.yaml` will apply. Empty strings are treated as "not specified" by the rendering engine and will be replaced with defaults.

```yaml
# WRONG - empty strings
level: ""
horizontalAlign: ""
type: ""

# CORRECT - omit the property or use a valid value
level: 2
horizontalAlign: center
type: solid
```

**Token-based properties are validated:**
- Invalid spacing values (e.g., `huge` instead of `lg`) will throw errors
- Invalid typography sizes will be rejected
- Invalid font weights will be rejected
- Border radius must be from token list or valid CSS value

**Error format:**
```
Component 'heading' at [0]: Invalid value 'huge' for property 'spacing.marginBlock'. 
Must be one of: none, xs, sm, md, lg, xl, xxl, xxxl, auto
```

## Transparency & Gradients

**Transparency:** Values 0-100 → hex alpha. `0` = transparent, `100` = opaque (default).
```yaml
appearance: { background: { color: '#2563eb', transparency: 50 } }  # 50% transparent
```

**Gradients:** Set `type: 'gradient'` with `colorStart`, `colorEnd`, `direction`.
```yaml
appearance:
  background:
    type: 'gradient'
    color: '#ff6b6b'        # Fallback
    gradient:
      colorStart: '#ff6b6b'
      colorEnd: '#4ecdc4'
      direction: 'to right'  # to right, to bottom, to bottom right, to top right
```

## Themes (Color & Font)

Page-level themes allow consistent colors and typography across all components using YAML anchors and aliases. Themes define reusable values that are referenced throughout the page.

### The 60-30-10 Color Distribution Rule

A professional color palette follows the 60-30-10 distribution for visual harmony:

| Color | Coverage | Role | Usage |
|-------|----------|------|-------|
| **Background** | 60% | Neutral base | Page backgrounds, card backgrounds, content areas |
| **Primary** | 30% | Text & branding | **Headings, body text**, brand elements, navigation |
| **Secondary** | 10% | Support color | Section highlights, borders, regular buttons, UI elements |
| **Accent** | CTAs only | High-visibility | **Call-to-action buttons ONLY**, critical links |

**⚠️ Important Color Rules:**
1. **Primary color is for TEXT** - Use it for headings, important text, and brand typography
2. **Secondary color is for UI** - Section backgrounds, borders, regular buttons
3. **Accent is ONLY for CTAs** - Reserve for "Buy Now", "Sign Up", "Get Started" buttons
4. **Never use accent for decoration** - It loses impact if overused

### Theme Structure

Themes are defined at the page level under `properties.theme`. **`theme` must always be the FIRST property** inside `properties` because it defines YAML anchors that all other properties reference:

```yaml
- name: page
  properties:
    theme:                          # ⚠️ MUST be first — defines anchors
      colors:
        background: &color-background '#F5FAF0'  # 60% - Page base
        primary: &color-primary '#1A3A1A'        # 30% - Text color
        secondary: &color-secondary '#E0EBD8'   # 10% - UI elements
        accent: &color-accent '#2E8B57'          # CTAs only
      fonts:
        heading: &font-heading "'Playfair Display', serif"
        content: &font-content "'Inter', sans-serif"
    appearance:
      background: { color: *color-background }
  components: [...]
```

### Using Theme Colors Correctly

**Standard section (light background):**
```yaml
- name: layout-column
  properties:
    appearance: { background: { color: *color-background } }
  components:
    - name: heading
      properties:
        text: Our Services
        typography: { color: *color-primary }   # Primary = text
    - name: paragraph
      properties:
        text: Description text...
        typography: { color: *color-primary }   # Primary = text
    - name: button
      properties:
        text: Learn More
        appearance: { background: { color: *color-secondary } }  # Secondary = regular button
        typography: { color: *color-primary }
    - name: button
      properties:
        text: Get Started Now            # CTA button!
        appearance: { background: { color: *color-accent } }     # Accent = CTA only
        typography: { color: *color-background }
```

### Creating Visual Interest: Inverted Sections

**⚡ Key technique:** Swap background and primary colors to create eye-catching sections:

```yaml
# INVERTED SECTION - Primary becomes background, background becomes text
- name: layout-column
  properties:
    appearance: { background: { color: *color-primary } }  # Dark background
    spacing: { paddingBlock: xl }
  components:
    - name: heading
      properties:
        text: Why Choose Us?
        typography: { color: *color-background }   # Light text on dark
    - name: paragraph
      properties:
        text: We deliver excellence...
        typography: { color: *color-background }   # Light text on dark
    - name: button
      properties:
        text: Contact Us
        appearance: { background: { color: *color-background } }  # Light button
        typography: { color: *color-primary }      # Dark text
```

### Section Color Patterns

Use these patterns to create visual rhythm:

| Section Type | Background | Text Color | Button (Regular) | CTA Button |
|--------------|------------|------------|------------------|------------|
| **Standard** | `*color-background` | `*color-primary` | `*color-secondary` bg | `*color-accent` bg |
| **Inverted** | `*color-primary` | `*color-background` | `*color-background` bg | `*color-accent` bg |
| **Highlight** | `*color-secondary` | `*color-primary` | `*color-primary` bg | `*color-accent` bg |
| **CTA Banner** | `*color-accent` | `*color-background` | `*color-background` bg | - |

**Applying Section Color Patterns:** Use the table above. For each section, set `appearance.background.color` and `typography.color` using the appropriate `*color-*` alias. Alternate Standard → Inverted → Highlight sections for visual rhythm.

## Ticker Component

Horizontally scrolling strip of content. Uses `columns:` array like columnsgrid.

### Structure
```yaml
- name: ticker
  properties:
    behavior:
      direction: left        # left, right
      mode: continuous       # continuous, step
      speed: 40              # px/sec (continuous only)
      pauseOnHover: true
      pauseDuration: 3000    # ms (step only)
    layout:
      width: "280"           # pixel-based column width (120, 200, 280, 360, 480)
    spacing:
      gap: lg                # gap between columns
      marginBlock: md
    appearance:
      columnBackground: '#ffffff'  # uniform background for all columns
      columnTransparency: 100      # 0=transparent, 100=opaque
      columnRadius: lg             # border radius token (none, xs, sm, md, lg, xl, xxl, pill)
      columnBorder:
        width: 1                   # border width in px (0=no border)
        style: solid               # solid, dashed, none
        color: '#e5e7eb'           # border color
  columns:                   # ← component level, NOT inside properties
    - components:
        - name: heading
          properties:
            text: Card Title
        - name: paragraph
          properties:
            text: Card content
    - components:
        - name: heading
          properties:
            text: Card Title 2
```

### layout.width (default: fit to content)
Pixel-based widths with CSS `clamp()` for responsive sizing:
- No width or `"fit"` → content-sized columns (default)
- `"120"` → 120px max (compact: logos, badges)
- `"200"` → 200px max (small text cards)
- `"280"` → 280px max (standard cards)
- `"360"` → 360px max (featured cards)
- `"480"` → 480px max (hero cards)

### Column Styling (ticker-level, applied uniformly)
- `columnBackground` — background color for all columns (default: `'#ffffff'`)
- `columnTransparency` — 0 = fully transparent, 100 = fully opaque (default: `0`)
- `columnRadius` — border radius token: none, xs, sm, md, lg, xl, xxl, pill (default: `none`)
- `columnBorder.width` — border width in px, 0 = no border (default: `0`)
- `columnBorder.style` — solid, dashed, none (default: `solid`)
- `columnBorder.color` — border color (default: `'#000000'`)

### Card-Style Columns
For cards with their own individual background/radius/shadow, nest a `layout-column` inside each column:
```yaml
columns:
  - components:
      - name: layout-column
        properties:
          layout:
            horizontalAlign: center
            gap: sm
          spacing:
            paddingBlock: md
            paddingInline: md
          appearance:
            background:
              color: '#ffffff'
              transparency: 100
            radius: lg
            shadow: md
        components:
          - name: heading
            properties:
              text: Card Title
```

---

## SSR Implementation Notes

- Components are rendered server-side with Python/Flask
- Default properties from `component_defaults.yaml` are merged automatically
- Only non-default values need to be specified in YAML
- Properties panel shows complete values (defaults + custom)

### Component widthMode Defaults

**Text and Form Components** (default `widthMode: fit`):
- `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`, `link`
- `button`, `textbox`, `textarea`
- These components shrink to fit their content width by default
- Use explicit `widthMode: stretch` or percentage values when full width is needed

**Media and Container Components** (default `widthMode: stretch`):
- `image`, `gif`, `video`, `video-background`
- `layout-column`, `accordion`, `tabs`, `carousel`
- These components stretch to fill their parent container by default
- Use explicit `widthMode: fit` or percentage values to constrain width

**Rationale:** This aligns with Figma's auto-sizing behavior where text/buttons naturally fit content while media/containers fill available space. This reduces YAML verbosity and matches designer expectations.

---

**Version:** 1.9 | **Last Updated:** February 2026

> **⚠️ Common Error:** "Iteration Error" usually means array properties (`items`, `tabs`, `slides`, `columns`) are inside `properties:` instead of at component level. See Quick Reference Card at top.
