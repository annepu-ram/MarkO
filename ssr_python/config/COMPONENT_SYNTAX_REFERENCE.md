# SwiftSites Component Syntax Reference

> **Version:** 3.0 | **Last Updated:** March 2026

This is the single authoritative reference for every SwiftSites component.
If a property is omitted from your YAML, the default value shown in each component section is used automatically — only set what you need to change.

**Critical rules (embedded in every section below):**
1. Structure: `- name: component_name` then `properties:` for settings, NEVER use `- component_name:` inline shorthand
2. Array properties (`items`, `tabs`, `slides`, `columns`) go at COMPONENT level, NOT inside `properties:`
3. NEVER use `typography.fontFamily` — fonts are controlled exclusively by `site.properties.theme.fonts`
4. `opacity`: 0 = fully transparent/invisible, 100 = fully opaque (matches CSS opacity semantics)
5. `layout.widthMode` is a STRING ("50", not 50). Only valid on direct children of layout-row.
6. Color defaults: headings → `*color-primary`, paragraphs/body → `*color-text`. Only set colors when overriding (e.g., inverted/dark sections need `*color-background` for ALL text)

<!-- section_type: component | component_name: site | category: layout -->
## Component: site

Root wrapper that defines the global theme (fonts, colors). Every page YAML starts with this.
Structure: `- name: site` then `properties:` — NEVER use `- site:` inline format.
Has one special property group: `theme`. Contains `page` components as children.

### Syntax
```yaml
- name: site
  properties:
    theme:
      fonts:
        heading: &font-heading "'Inter', sans-serif"    # Google font family string
        content: &font-content "'Inter', sans-serif"    # Google font family string
      colors:
        primary: &color-primary '#1a1a1a'               # Heading/branding color
        text: &color-text '#374151'                      # Body/paragraph text color
        secondary: &color-secondary '#6b7280'           # Support/highlight color
        accent: &color-accent '#3b82f6'                 # CTA buttons only
        background: &color-background '#ffffff'          # Page base background
  components:
    - name: page
      ...
```

### Key Notes
- `&font-heading` / `&color-primary` / `&color-text` are YAML anchors — define here, reference elsewhere with `*font-heading` / `*color-primary` / `*color-text`
- NEVER use `typography.fontFamily` on any component — theme fonts apply automatically
- Only ONE site component per YAML document

### Theme Presets by Business Type

Choose the theme that best matches the business, service, style, or mood. Use the listed colors and fonts. You may adjust colors slightly to match a specific brand, but keep the contrast ratios and 60-30-10 rule.

| Preset | Primary | Text | Secondary | Accent | Background | Heading Font | Content Font | Best for |
|--------|---------|------|-----------|--------|------------|-------------|-------------|----------|
| Modern Minimalist | #1E3A5F | #4B5563 | #C5D4E3 | #0052CC | #E8EDF2 | Inter | Inter | SaaS, consulting, legal, healthcare, corporate, B2B, education, real estate, startup |
| Glassmorphism | #1A365D | #334E68 | #B0D4E8 | #3182CE | #D6EBF5 | Inter | Inter | Tech startups, fintech, dashboards, luxury, hospitality, hotel, resort, portfolio, software |
| Retro Vintage | #0D0D0D | #2D2D00 | #FFD600 | #FF0000 | #FFEB3B | Bebas Neue | Merriweather | Entertainment, gaming, food & beverage, restaurants, bars, breweries, pizza, festivals, music |
| Neubrutalism | #1A1A1A | #3D3D3D | #C8C4BB | #FF4D00 | #E5E2DD | Space Grotesk | IBM Plex Sans | Creative agencies, art galleries, indie brands, fashion, design studios, photography |
| Claymorphism | #4A1942 | #5A3058 | #F5B0D0 | #FF1493 | #FFD6E6 | Poppins | Nunito Sans | Education, kids, wellness, fitness, food delivery, mobile apps, toy stores, childcare, gym |
| Aurora Gradient | #1A2035 | #384860 | #C8D8F0 | #EC4899 | #E6F0FA | Sora | Inter | AI products, SaaS, luxury ecommerce, travel, resort, wellness, tech startups |
| Monochrome Dark | #F5F5F5 | #C8C8C8 | #1F1F1F | #DC143C | #0F0F0F | Space Grotesk | Inter | Photography, luxury, automotive, fine dining, fashion, nightlife, music, portfolio |

If user specifies a style keyword (e.g., "retro", "dark mode", "playful"), match that style preset directly.
If user specifies a business type (e.g., "bakery", "law firm"), pick the preset whose "Best for" list is the closest match.

<!-- section_type: component | component_name: page | category: layout -->
## Component: page

Container for all page content. Lives inside `site.components`.
Structure: `- name: page` then `properties:` — NEVER use `- page:` inline format.

### Syntax
```yaml
- name: page
  slug: home                                         # URL slug for this page
  title: My Page Title                               # Page title
  properties:
    spacing:
      paddingBlock: none                             # Spacing token: none|xxs|xs|sm|md|lg|xl|xxl|xxxl
      paddingInline: none                            # Spacing token
    appearance:
      background:
        color: *color-background                     # Theme alias or hex color
        # Theme alias: *color-primary | *color-text | *color-secondary | *color-accent | *color-background
        opacity: 100                            # 0=invisible, 100=opaque (default: 100)
        image: ''                                    # Background image URL (optional)
  components:
    - name: layout-row
      ...
```

### Key Notes
- `slug` and `title` are at component level (sibling of `properties:`), not inside `properties:`
- Use `*color-background` for the page background to match the theme

<!-- section_type: component | component_name: layout-row | category: layout -->
## Component: layout-row

Flex row container — the primary section wrapper. Children sit side-by-side (nowrap) or stack responsively (wrap).
Structure: `- name: layout-row` then `properties:` — NEVER use `- layout-row:` inline format.
NEVER use `typography.fontFamily`. Theme fonts apply automatically.

### Syntax
```yaml
- name: layout-row
  properties:
    layout:
      tag: section                         # section|div|main|article (default: section)
      horizontalAlign: space-evenly        # center|space-between|left|space-around|right|space-evenly (default: space-evenly)
      verticalAlign: stretch               # top|center|bottom|stretch|baseline (default: stretch)
      wrap: wrap                           # wrap (responsive stacking) | nowrap (side-by-side forced) (default: wrap)
      gap: sm                              # Spacing token: none|xxs|xs|sm|md|lg|xl|xxl|xxxl (default: sm)
    spacing:
      marginBlock: none                    # Spacing token (default: none)
      marginInline: none                   # Spacing token (default: none)
      paddingBlock: sm                     # Spacing token (default: sm)
      paddingInline: sm                    # Spacing token (default: sm)
    appearance:
      background:
        color: *color-background           # Theme alias or hex: *color-primary|*color-text|*color-secondary|*color-accent|*color-background
        opacity: 0                    # 0=transparent (default), 100=opaque
        image: ''                          # Background image URL
      border:
        width: 0                           # Border width in px (default: 0)
        style: solid                       # solid|dashed|dotted (default: solid)
        color: *color-primary             # Border color (default: *color-primary)
      radius: none                         # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # Shadow tint color — only with retro shadow
      blur: false                          # Glassmorphism backdrop blur (default: false)
  components:
    - name: layout-column
      properties:
        layout:
          widthMode: "50"                  # STRING: "fit"|"16"|"25"|"33"|"50"|"66"|"75"|"83"|"stretch"
      ...
```

### Key Notes
- **Every direct child MUST have `layout.widthMode`** — without it, children default to `stretch` (100% width) causing overflow
- For split layouts (hero, two-column): use `wrap: nowrap` with children having `widthMode: "50"` or similar
- **NEVER mix `widthMode: "stretch"` with fixed widths** like `"50"` on sibling children — `stretch` takes 100% width causing overflow. All siblings should use compatible widths (e.g., `"50"` + `"50"`, or `"33"` + `"66"`).
- Padding: use `spacing.paddingBlock` / `spacing.paddingInline` — NEVER use `appearance.padding` on layout-row.
- Omit properties that match defaults — only set what you change. Don't include `border.width: 0`, `shadow: none`, `blur: false`, `shadowColor: ''`, etc.
- `opacity: 0` is the default — row backgrounds are transparent by default. Set `opacity: 100` to see the background color.
- Alternate section types for visual rhythm (Standard → Inverted → Highlight). See Theme System section.

| Section Type | Background | Text Color |
|-------------|-----------|------------|
| Standard | `*color-background` | `*color-primary` |
| Inverted | `*color-primary` | `*color-background` |
| Highlight | `*color-secondary` | `*color-primary` |
| CTA Banner | `*color-accent` | `*color-background` |

#### Common layout-row Mistakes
```yaml
# WRONG — stretch + fixed width siblings cause overflow
- name: layout-row
  components:
  - name: image
    properties: { layout: { widthMode: stretch } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }

# CORRECT — matching widths + nowrap for split layout
- name: layout-row
  properties: { layout: { wrap: nowrap } }
  components:
  - name: image
    properties: { layout: { widthMode: "50" } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }

# WRONG — padding under appearance
spacing: { marginBlock: none }
appearance: { padding: { block: lg, inline: md } }

# CORRECT — all spacing together
spacing: { marginBlock: none, paddingBlock: lg, paddingInline: md }
```

<!-- section_type: component | component_name: layout-column | category: layout -->
## Component: layout-column

Flex column container — groups children vertically. Typically used inside layout-row.
Structure: `- name: layout-column` then `properties:` — NEVER use `- layout-column:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: layout-column
  properties:
    layout:
      tag: section                         # section|div|main|article (default: section)
      horizontalAlign: center              # left|center|right (default: center)
      verticalAlign: space-between          # top|center|bottom|space-between|space-around|space-evenly (default: space-between)
      wrap: nowrap                         # wrap|nowrap (default: nowrap)
      gap: none                            # Spacing token (default: none)
      widthMode: stretch                   # STRING: "fit"|"16"|"25"|"33"|"50"|"66"|"75"|"83"|"stretch" (default: stretch)
    spacing:
      marginBlock: none                    # Spacing token (default: none)
      marginInline: none                   # Spacing token (default: none)
      paddingBlock: sm                     # Spacing token (default: sm)
      paddingInline: sm                    # Spacing token (default: sm)
    appearance:
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # 0=transparent (default), 100=opaque
        image: ''                          # Background image URL
      border:
        width: 0                           # (default: 0)
        style: solid                       # solid|dashed|dotted (default: solid)
        color: *color-primary            # Default: *color-primary (auto-resolves to theme)
      radius: none                         # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # Shadow tint color
      blur: false                          # Glassmorphism backdrop blur (default: false)
  components:
    - name: heading
      ...
```

### Key Notes
- `layout.widthMode` is ONLY effective when this is a direct child of `layout-row`
- `widthMode` is a STRING — use `"50"` not `50`
- Valid widthMode values: `"fit"`, `"16"`, `"25"`, `"33"`, `"50"`, `"66"`, `"75"`, `"83"`, `"stretch"`
- When inside a `layout-row`, ALWAYS set `layout.widthMode` to a specific value (`"50"`, `"33"`, etc.) — never leave as default `stretch` if siblings have fixed widths
- Padding: use `spacing.paddingBlock` / `spacing.paddingInline` — NEVER `appearance.padding`
- Omit default properties — don't set `opacity: 0`, `border.width: 0`, `shadow: none`, `blur: false` explicitly

<!-- section_type: component | component_name: columnsgrid | category: layout -->
## Component: columnsgrid

CSS Grid layout for card grids. Uses `columns:` array at COMPONENT level (not inside properties).
Structure: `- name: columnsgrid` then `properties:` + `columns:` — NEVER use `- columnsgrid:` inline format.
`columns:` is an array property — place at COMPONENT level, NOT inside `properties:`.

### Syntax
```yaml
- name: columnsgrid
  properties:
    layout:
      columns: 3                           # Number of columns (default: 2)
      gap: md                              # Spacing token (default: md)
      verticalAlign: stretch               # stretch|top|center|bottom (default: stretch)
    responsive:
      breakpoints:
        md: 2                              # Columns at medium viewport (default: 2)
        sm: 1                              # Columns at small viewport (default: 1)
    appearance:
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # Shadow tint color
      columnBackground: *color-background # Default: *color-background (auto-resolves to theme). Uniform bg for all columns
      columnOpacity: 0               # 0=transparent (default), 100=opaque
      columnBlur: false                    # Glassmorphism blur on columns (default: false)
      columnRadius: none                   # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      columnBorder:
        width: 0                           # (default: 0)
        color: '#e5e7eb'                   # (default: '#e5e7eb')
    spacing:
      marginBlock: none                    # Spacing token (default: none)
      marginInline: none                   # Spacing token (default: none)
      paddingBlock: sm                     # Spacing token (default: sm)
      paddingInline: sm                    # Spacing token (default: sm)
  columns:                                 # ARRAY AT COMPONENT LEVEL — NOT inside properties
    # IMPORTANT: Keep column structure CONSISTENT — every column must have the same component types in the same order
    # IMPORTANT: Do NOT place text directly over images — text may be invisible. Place text above/below images instead
    - components:                          # Each column is a data container with components
        - name: heading
          properties: { text: Card 1 }
        - name: paragraph
          properties: { text: Description }
    - components:
        - name: heading
          properties: { text: Card 2 }
```

### Key Notes
- `columns:` array goes at component level (sibling of `properties:`), never inside `properties:`
- Each column entry has `components:` — no `name: layout-column` needed
- `columnBackground`, `columnOpacity`, `columnRadius`, `columnBorder` apply uniformly to ALL columns
- For individual column styling, nest a `layout-column` with its own `appearance` inside a column
- Do NOT wrap every column's content in `layout-column` by default — columns are already containers. Use `columnBackground`, `columnRadius`, `columnBorder` for uniform styling instead.
- Keep the component structure CONSISTENT across all columns — each column should have the same types of components in the same order (e.g., if one column has image → heading → paragraph, all columns should follow that pattern).
- Do NOT place text directly over images — the text may not be visible depending on the image. Place text above or below images instead.

#### Common columnsgrid Mistake
```yaml
# UNNECESSARY — layout-column wrapper adds extra DOM nesting
- name: columnsgrid
  columns:
  - components:
    - name: layout-column
      components:
        - name: heading
          properties: { text: Card 1 }

# PREFERRED — direct components in column, use columnBackground for styling
- name: columnsgrid
  properties:
    appearance: { columnBackground: *color-background, columnRadius: md }
  columns:
  - components:
    - name: heading
      properties: { text: Card 1 }
```

<!-- section_type: component | component_name: form | category: layout -->
## Component: form

Form container that wraps form field components (textbox, textarea, dropdown, checkbox, radio, calendar).
Structure: `- name: form` then `properties:` — NEVER use `- form:` inline format.

### Syntax
```yaml
- name: form
  properties:
    layout:
      style: vertical                      # vertical|inline|horizontal (default: vertical)
    submit:
      buttonText: Submit                   # Submit button text (default: Submit)
      show: true                           # Show submit button (default: true)
    appearance:
      background:
        color: *color-background           # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # 0=transparent (default), 100=opaque
      border:
        width: 0                           # (default: 0)
        color: '#e5e7eb'                   # (default: '#e5e7eb')
      radius: none                         # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # Shadow tint color
    spacing:
      paddingBlock: md                     # Spacing token (default: md)
      paddingInline: md                    # Spacing token (default: md)
      marginBlock: none                    # Spacing token (default: none)
  components:
    - name: textbox
      properties: { label: { text: Name }, field: { placeholder: Your name } }
    - name: textarea
      properties: { label: { text: Message }, field: { placeholder: Your message } }
```

<!-- section_type: component | component_name: heading | category: text -->
## Component: heading

Text component for titles (h1-h6).
Structure: `- name: heading` then `properties:` — NEVER use `- heading:` inline format.
NEVER use `typography.fontFamily` — fonts come from `site.properties.theme.fonts`.
Omitted properties use defaults — only set what you change.

### Syntax
```yaml
- name: heading
  properties:
    text: |                                # Supports multiline with YAML | syntax
      Elevate your message
      with a bold statement
    level: 2                               # 1-6 for h1-h6 (default: 2)
    typography:
      size: xl                             # xxs|xs|sm|md|lg|xl|xxl|xxxl (default: xl)
      weight: bold                         # thin|extralight|light|regular|medium|semibold|bold|extrabold|black (default: bold)
      lineHeight: "1.2"                    # String number (default: "1.2")
      transform: none                      # none|uppercase|lowercase|capitalize (default: none)
      letterSpacing: normal                # tighter|tight|normal|wide|wider|widest (default: normal)
      fontStyle: normal                    # normal|italic (default: normal)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
      align: center                        # left|center|right (default: center)
      color: *color-primary                # Default: *color-primary (auto-resolves to theme). Use *color-background on dark bg only
    appearance:
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # 0=transparent (default), 100=opaque
      radius: none                         # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      textShadow: none                     # none|soft|strong (default: none) — diffused halo for text legibility over images
    spacing:
      marginBlock: md                      # Spacing token (default: md)
      marginInline: none                   # Spacing token (default: none)
      paddingBlock: none                   # Spacing token (default: none)
      paddingInline: none                  # Spacing token (default: none)
    layout:
      widthMode: fit                       # STRING: "fit"|"16"|"25"|"33"|"50"|"66"|"75"|"83"|"stretch" (default: fit)
                                           # Only effective as direct child of layout-row
```

### Key Notes
- `text` supports multiline with YAML `|` block scalar syntax
- Inside layout-row, set `layout.widthMode` to control width (STRING, not number)
- Color defaults auto-resolve to theme: heading text defaults to `*color-primary`, paragraph/body text to `*color-text`, background to `*color-background`
- Only override colors for inverted sections (e.g., `*color-background` for text on dark bg)

<!-- section_type: component | component_name: paragraph | category: text -->
## Component: paragraph

Body text component for descriptions and content.
Structure: `- name: paragraph` then `properties:` — NEVER use `- paragraph:` inline format.
NEVER use `typography.fontFamily`. Omitted properties use defaults.

### Syntax
```yaml
- name: paragraph
  properties:
    text: |                                # Supports multiline with YAML | syntax
      Tell your story across multiple lines.
      Continue the narrative here.
    typography:
      size: md                             # xxs|xs|sm|md|lg|xl|xxl|xxxl (default: md)
      weight: regular                      # thin|...|black (default: regular)
      align: left                          # left|center|right (default: left)
      color: *color-text                   # Default: *color-text (auto-resolves to theme). Use *color-background on dark bg only
      lineHeight: "1.6"                    # (default: "1.6")
      transform: none                      # none|uppercase|lowercase|capitalize (default: none)
      letterSpacing: normal                # tighter|tight|normal|wide|wider|widest (default: normal)
      fontStyle: normal                    # normal|italic (default: normal)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
    spacing:
      marginBlock: none                    # Spacing token (default: none)
      marginInline: none                   # Spacing token (default: none)
      paddingBlock: sm                     # Spacing token (default: sm)
      paddingInline: none                  # Spacing token (default: none)
    layout:
      widthMode: fit                       # STRING (default: fit)
    appearance:
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # 0=transparent (default), 100=opaque
      radius: none                         # (default: none)
      textShadow: none                     # none|soft|strong (default: none) — diffused halo for text legibility over images
```

### Key Notes
- Text color defaults to `*color-text` (auto-resolves to theme) — only override for inverted sections
- Never use `*color-background` for text when the section background is also `*color-background` — text becomes invisible

<!-- section_type: component | component_name: eyebrow | category: text -->
## Component: eyebrow

Small uppercase label above headings. Typically used for section categories.
Structure: `- name: eyebrow` then `properties:` — NEVER use `- eyebrow:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: eyebrow
  properties:
    text: Featured insight                 # Supports multiline with |
    typography:
      size: xs                             # (default: xs)
      weight: semibold                     # (default: semibold)
      align: left                          # left|center|right (default: left)
      color: *color-accent                 # Default: *color-accent (auto-resolves to theme). Use *color-background on dark bg only
      lineHeight: "1.4"                    # (default: "1.4")
      transform: uppercase                 # (default: uppercase)
      letterSpacing: wide                  # (default: wide)
      fontStyle: normal                    # (default: normal)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
    spacing:
      marginBlock: none                    # (default: none)
      marginInline: none                   # (default: none)
      paddingBlock: sm                     # (default: sm)
      paddingInline: none                  # (default: none)
    layout:
      widthMode: fit                       # STRING (default: fit)
    appearance:
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # (default: 0)
      radius: none                         # (default: none)
```

### Key Notes
- Text color defaults to `*color-accent` (auto-resolves to theme) — draws attention to category labels above headings
- On inverted (dark bg) sections, override with `*color-background`

<!-- section_type: component | component_name: caption | category: text -->
## Component: caption

Small secondary text for photo credits, descriptions, supporting info.
Structure: `- name: caption` then `properties:` — NEVER use `- caption:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: caption
  properties:
    text: Photo by Jane Doe                # Supports multiline with |
    typography:
      size: sm                             # (default: sm)
      weight: regular                      # (default: regular)
      align: center                        # (default: center)
      color: *color-secondary              # Default: *color-secondary (auto-resolves to theme). Use *color-background on dark bg only
      lineHeight: "1.4"                    # (default: "1.4")
      transform: none                      # (default: none)
      letterSpacing: normal                # (default: normal)
      fontStyle: normal                    # (default: normal)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
    spacing:
      marginBlock: xs                      # (default: xs)
      marginInline: none                   # (default: none)
      paddingBlock: none                   # (default: none)
      paddingInline: none                  # (default: none)
    layout:
      widthMode: fit                       # STRING (default: fit)
    appearance:
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # (default: 0)
      radius: none                         # (default: none)
```

### Key Notes
- Text color defaults to `*color-secondary` (auto-resolves to theme) — subtle supporting text
- On inverted (dark bg) sections, override with `*color-background`

<!-- section_type: component | component_name: blockquote | category: text -->
## Component: blockquote

Styled quote block with optional citation.
Structure: `- name: blockquote` then `properties:` — NEVER use `- blockquote:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: blockquote
  properties:
    quote: |                               # The quote text (supports multiline with |)
      Design is intelligence made visible.
    cite: Alina Wheeler                    # Attribution/citation (default: '')
    typography:
      size: xl                             # (default: xl)
      weight: medium                       # (default: medium)
      align: center                        # (default: center)
      color: *color-text                   # Default: *color-text (auto-resolves to theme). Use *color-background on dark bg only
      lineHeight: "1.6"                    # (default: "1.6")
      transform: none                      # (default: none)
      letterSpacing: normal                # (default: normal)
      fontStyle: italic                    # (default: italic)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
    spacing:
      marginBlock: lg                      # (default: lg)
      marginInline: none                   # (default: none)
      paddingBlock: md                     # (default: md)
      paddingInline: md                    # (default: md)
    appearance:
      border:
        accentColor: *color-accent         # Default: *color-accent (auto-resolves to theme)
      background:
        color: *color-background         # Default: *color-background (auto-resolves to theme)
        opacity: 0                    # (default: 0)
      radius: none                         # (default: none)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # (default: '')
    layout:
      widthMode: fit                       # STRING (default: fit)
```

### Key Notes
- Uses `quote:` not `text:` for the quote content
- `cite:` for attribution text (optional)
- `appearance.border.accentColor` controls the left accent bar — different from regular `border`
- Quote text defaults to `*color-text`, accent bar to `*color-accent` (both auto-resolve to theme). Use `*color-background` on dark bg sections

<!-- section_type: component | component_name: link | category: text -->
## Component: link

Inline hyperlink with optional arrow indicator.
Structure: `- name: link` then `properties:` — NEVER use `- link:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: link
  properties:
    text: Click Me                         # Link text (default: 'Click Me')
    href: '#'                              # URL or anchor (default: '#')
    appearance:
      underline: true                      # Show underline (default: true)
      showArrow: false                     # Show arrow icon (default: false)
    typography:
      size: md                             # (default: md)
      weight: regular                      # (default: regular)
      align: left                          # (default: left)
      color: *color-accent                 # USE *color-accent (light bg) or *color-background (dark bg)
      lineHeight: "1.5"                    # (default: "1.5")
      transform: none                      # (default: none)
      letterSpacing: normal                # (default: normal)
      fontStyle: normal                    # (default: normal)
      textDecoration: none                 # none|underline|line-through|underline line-through (default: none)
    spacing:
      marginBlock: xs                      # (default: xs)
      marginInline: xs                     # (default: xs)
      paddingBlock: none                   # Spacing token (default: none)
      paddingInline: none                  # Spacing token (default: none)
    layout:
      widthMode: fit                       # STRING (default: fit)
```

<!-- section_type: component | component_name: image | category: media -->
## Component: image

Image component that can also act as a container (children overlay the image).
Structure: `- name: image` then `properties:` — NEVER use `- image:` inline format.

### Syntax
```yaml
- name: image
  properties:
    source:
      url: https://example.com/photo.jpg   # Image URL (required for display)
      altText: Descriptive alt text         # Accessibility alt text (default: 'Placeholder image')
    appearance:
      minHeight: 12.5                      # Minimum height in rem (default: 12.5)
      maxHeight: 0                         # Maximum height in rem, 0=none (default: 0)
      fit: cover                           # cover|contain|fill|none (default: cover)
      cornerStyle: none                    # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      objectPosition: center               # center|top|bottom|left|right (default: center)
      filter: none                         # none|grayscale|sepia|blur|brightness|contrast|saturate (default: none)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # Shadow tint color (default: '')
      hoverEffect: none                    # none|zoom|lift|brighten|darken (default: none)
      lazy: true                           # Lazy loading (default: true)
      overlay:
        enabled: false                     # Enable dark overlay for text readability (default: false)
        color: rgba(0,0,0,0.5)            # Overlay color (default: rgba(0,0,0,0.5))
        opacity: 0.5                       # Overlay opacity (default: 0.5)
    spacing:
      marginBlock: sm                      # (default: sm)
      marginInline: none                   # (default: none)
      paddingBlock: none                   # Spacing token (default: none)
      paddingInline: none                  # Spacing token (default: none)
    layout:
      widthMode: stretch                   # STRING (default: stretch)
      horizontalAlign: center              # left|center|right (default: center)
  components:                              # Optional: overlay children (for hero sections)
    - name: layout-column
      properties:
        layout: { horizontalAlign: center }
        spacing: { paddingBlock: xl }
      components:
        - name: heading
          properties: { text: Hero Title, typography: { color: *color-background } }
```

### Key Notes
- Images can be containers — add `components:` for overlay content (hero pattern)
- For hero sections: use `overlay.enabled: true` + child text components with white color
- `minHeight` is in rem (12.5rem = 200px). Set higher for hero images (e.g., 37.5 = 600px)
- `maxHeight: 0` means no max height constraint
- Inside layout-row with siblings: set `layout.widthMode` to a specific value (e.g., `"50"`), NOT `stretch` — stretch causes overflow when siblings have fixed widths
- Image `appearance.padding` is image-specific — layout containers (layout-row, layout-column) use `spacing.paddingBlock/paddingInline` instead

#### Common image-in-row Mistake
```yaml
# WRONG — image stretch + column "50" = overflow
- name: layout-row
  components:
  - name: image
    properties: { layout: { widthMode: stretch } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }

# CORRECT — both children have matching widths
- name: layout-row
  properties: { layout: { wrap: nowrap } }
  components:
  - name: image
    properties: { layout: { widthMode: "50" }, appearance: { minHeight: 25, fit: cover } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }
```

<!-- section_type: component | component_name: video | category: media -->
## Component: video

Embedded video player (YouTube, Vimeo, or direct URLs).
Structure: `- name: video` then `properties:` — NEVER use `- video:` inline format.

### Syntax
```yaml
- name: video
  properties:
    source:
      url: https://www.youtube.com/watch?v=ID  # Video URL (YouTube, Vimeo, or direct)
    appearance:
      aspectRatio: '16/9'                  # Aspect ratio string (default: '16/9')
      height: 400                          # Height in px (default: 400)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # (default: '')
    playback:
      controls: true                       # Show player controls (default: true)
      autoplay: false                      # Auto-play on load (default: false)
      muted: false                         # Start muted (default: false)
      loop: false                          # Loop playback (default: false)
    poster:
      url: ''                              # Poster/thumbnail image URL (default: '')
    spacing:
      marginBlock: md                      # (default: md)
      marginInline: none                   # (default: none)
    layout:
      widthMode: stretch                   # STRING (default: stretch)
```

<!-- section_type: component | component_name: gif | category: media -->
## Component: gif

Animated GIF component. Same property structure as image.
Structure: `- name: gif` then `properties:` — NEVER use `- gif:` inline format.

### Syntax
```yaml
- name: gif
  properties:
    source:
      url: https://media.giphy.com/media/.../giphy.gif  # GIF URL
      altText: Animated GIF                # Alt text (default: 'Animated GIF')
    appearance:
      minHeight: 12.5                      # Min height in rem (default: 12.5)
      maxHeight: 0                         # Max height in rem, 0=none (default: 0)
      fit: cover                           # cover|contain|fill|none (default: cover)
      cornerStyle: none                    # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      objectPosition: center               # center|top|bottom|left|right (default: center)
      filter: none                         # none|grayscale|sepia|blur|brightness|contrast|saturate (default: none)
      shadow: none                         # (default: none)
      shadowColor: ''                      # (default: '')
      hoverEffect: none                    # none|zoom|lift|brighten|darken (default: none)
      lazy: true                           # (default: true)
      overlay:
        enabled: false                     # (default: false)
        color: rgba(0,0,0,0.5)            # (default: rgba(0,0,0,0.5))
        opacity: 0.5                       # (default: 0.5)
    spacing:
      marginBlock: sm                      # (default: sm)
      marginInline: none                   # (default: none)
      paddingBlock: none                   # (default: none)
      paddingInline: none                  # (default: none)
    layout:
      widthMode: stretch                   # STRING (default: stretch)
```

<!-- section_type: component | component_name: video-background | category: media -->
## Component: video-background

Full-width video with overlay content — used for cinematic hero sections.
Structure: `- name: video-background` then `properties:` — NEVER use `- video-background:` inline format.
Can contain child components that overlay the video.

### Syntax
```yaml
- name: video-background
  properties:
    source:
      url: ''                              # Video URL (required)
      poster: ''                           # Poster/fallback image URL
    appearance:
      aspectRatio: '16/9'                  # (default: '16/9')
      minHeight: 25                        # Min height in rem (default: 25)
      fit: cover                            # cover|contain|fill|none (default: cover)
      objectPosition: center               # center|top|bottom (default: center)
      overlay:
        enabled: true                      # Enable dark overlay (default: true)
        color: 'rgba(0,0,0,0.4)'          # Overlay color (default: 'rgba(0,0,0,0.4)')
        opacity: 40                        # Overlay opacity 0-100 (default: 40)
    playback:
      autoplay: true                       # (default: true)
      loop: true                           # (default: true)
      muted: true                          # Must be true for autoplay (default: true)
      playsinline: true                    # (default: true)
    content:
      verticalAlign: center                # center|top|bottom (default: center)
      horizontalAlign: center              # center|left|right (default: center)
      padding: md                          # Spacing token (default: md)
    spacing:
      marginBlock: none                    # (default: none)
      marginInline: none                   # (default: none)
    layout:
      widthMode: stretch                   # STRING (default: stretch)
  components:                              # Overlay content
    - name: heading
      properties: { text: Hero Title, typography: { color: *color-background, size: xxxl } }
    - name: button
      properties: { text: Get Started }
```

<!-- section_type: component | component_name: button | category: ui -->
## Component: button

Clickable button with configurable action.
Structure: `- name: button` then `properties:` — NEVER use `- button:` inline format.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: button
  properties:
    text: Click Me                         # Button label (default: 'Click Me')
    action:
      type: link                           # inlineScript|link|submit (default: inlineScript)
      value: https://example.com           # URL for link, JS for inlineScript (default: 'alert("Clicked!")')
    appearance:
      background:
        color: *color-accent               # Default: *color-background. CTA: *color-accent, Regular: *color-secondary
        opacity: 100                  # 0=transparent, 100=opaque (default: 100)
      border:
        width: 1                           # (default: 1)
        style: solid                       # solid|dashed|dotted (default: solid)
        color: '#1d4ed8'                   # (default: '#1d4ed8')
      radius: sm                           # none|xs|sm|md|lg|xl|xxl|pill (default: sm)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # (default: '')
      iconPlacement: none                  # none|left|right (default: none)
    typography:
      size: md                             # (default: md)
      weight: semibold                     # (default: semibold)
      align: center                        # (default: center)
      color: *color-background             # Default: *color-background (auto-resolves to theme). Light text on colored button bg
      lineHeight: "1.5"                    # (default: "1.5")
      transform: none                      # (default: none)
      letterSpacing: normal                # (default: normal)
    spacing:
      marginBlock: sm                      # (default: sm)
      marginInline: xs                     # (default: xs)
      paddingBlock: sm                     # Spacing token (default: sm)
      paddingInline: md                    # Spacing token (default: md)
    layout:
      widthMode: fit                       # STRING (default: fit)
```

### Key Notes
- For CTA buttons: use `*color-accent` background with white text
- For secondary buttons: use `*color-secondary` background with `*color-primary` text
- `action.type: link` navigates to `action.value` URL
- `action.type: submitForm` submits the parent form

<!-- section_type: component | component_name: titlebar | category: ui -->
## Component: titlebar

Sticky navigation header with logo, title, nav links, and optional hamburger menu.
Structure: `- name: titlebar` then `properties:` — NEVER use `- titlebar:` inline format.

### Syntax
```yaml
- name: titlebar
  properties:
    branding:
      showLogo: true                       # Show logo image (default: true)
      logoUrl: https://placehold.co/50x40?text=Add+Image  # Logo image URL
      title: Website Title                 # Site title text (default: 'Website Title')
    navigation:
      links:                               # Array of nav links
        - label: Home                      # Link text
          href: '#home'                    # URL or anchor
        - label: About
          href: '#about'
        - label: Contact
          href: '#contact'
    layout:
      alignment: left                      # left|center|right (default: left)
      height: 60                           # Height in px (default: 60)
    scroll:
      shrinkPercentage: 70                 # Shrink to this % on scroll (default: 70)
    appearance:
      background:
        color: *color-background           # Default: *color-background (auto-resolves to theme)
        opacity: 100                  # (default: 100)
      border:
        width: 1                           # (default: 1)
        style: solid                       # (default: solid)
        color: '#dddddd'                   # (default: '#dddddd')
      focus:
        background: '#f0f0f0'              # Hover/focus bg (default: '#f0f0f0')
        color: *color-primary            # Default: *color-primary (auto-resolves to theme)
    typography:
      title:
        size: 24                           # Title font size in px (default: 24)
        weight: bold                       # (default: bold)
        color: *color-primary              # Default: *color-primary (auto-resolves to theme)
      menu:
        size: 16                           # Menu font size in px (default: 16)
        weight: medium                     # (default: medium)
        color: *color-primary              # Default: *color-primary (auto-resolves to theme)
```

<!-- section_type: component | component_name: hamburger | category: ui -->
## Component: hamburger

Mobile menu toggle. Typically used alongside titlebar for responsive navigation.
Structure: `- name: hamburger` then `properties:`.

### Syntax
```yaml
- name: hamburger
  properties:
    label: Menu                            # Button label (default: 'Menu')
    links:                                 # Array of menu links
      - label: Home
        href: '#home'
      - label: About
        href: '#about'
```

<!-- section_type: component | component_name: br | category: ui -->
## Component: br

Horizontal or vertical divider/separator line.
Structure: `- name: br` then `properties:` — NEVER use `- br:` inline format.

### Syntax
```yaml
- name: br
  properties:
    size: md                               # Spacing token for length (default: md)
    type: solid                            # solid|dashed|dotted|wave|slant (default: solid)
    orientation: horizontal                # horizontal|vertical (default: horizontal)
    thickness: 2                           # Line thickness in px (default: 2)
    color: '#e5e7eb'                       # Theme alias or hex (default: '#e5e7eb')
    invert: false                          # Flip decorative pattern (default: false)
    mirror: false                          # Mirror decorative pattern (default: false)
```

### Section Breaker Usage
Use `type: wave` or `type: slant` as full-width decorative section breakers between page sections.
- Set `color` to match the background of the section BELOW the divider for seamless blending
- Use `invert: true` to flip the shape vertically (useful at the bottom of a colored section)
- Use `mirror: true` to flip left-right direction (alternate slant angles)
- Set `thickness: 4-6` for prominent section transitions (thickness controls SVG height in multiples of 10px)
- Place directly between layout-row/layout-column sections at the page level

```yaml
# Example: wave transition from white section to dark section
- name: br
  properties:
    type: wave
    color: '#1e293b'
    thickness: 5

# Example: inverted wave at bottom of colored section
- name: br
  properties:
    type: wave
    color: '#0f172a'
    thickness: 5
    invert: true

# Example: slant with alternating direction
- name: br
  properties:
    type: slant
    color: '#f8fafc'
    thickness: 4
    mirror: true
```

<!-- section_type: component | component_name: tabs | category: interactive -->
## Component: tabs

Tabbed content container. Uses `tabs:` array at COMPONENT level.
Structure: `- name: tabs` then `properties:` + `tabs:` — NEVER use `- tabs:` inline format.
`tabs:` is an array property — place at COMPONENT level, NOT inside `properties:`.

### Syntax
```yaml
- name: tabs
  properties:
    layout:
      orientation: horizontal              # horizontal|vertical (default: horizontal)
      widthMode: stretch                   # STRING (default: stretch)
    typography:
      label:
        size: md                           # (default: md)
        weight: semibold                   # (default: semibold)
        active:
          color: *color-primary            # Default: *color-primary (auto-resolves to theme)
        inactive:
          color: *color-secondary        # Default: *color-secondary (auto-resolves to theme)
    appearance:
      tab:
        background:
          active: *color-background        # Default: *color-background (auto-resolves to theme)
          inactive: *color-background    # Default: *color-background (auto-resolves to theme)
        border:
          width: 2                         # (default: 2)
          style: solid                     # (default: solid)
          position: lower                  # lower|upper (default: lower)
      content:
        background:
          color: *color-background         # Default: *color-background (auto-resolves to theme)
          opacity: 100                # (default: 100)
        border:
          color: '#d1d5db'                 # (default: '#d1d5db')
          width: 1                         # (default: 1)
          style: solid                     # (default: solid)
        padding:
          block: md                        # Spacing token (default: md)
          inline: md                       # Spacing token (default: md)
      shadow: none                         # none|soft|medium|elevated|retro (default: none)
      shadowColor: ''                      # (default: '')
    spacing:
      marginBlock: md                      # (default: md)
      marginInline: none                   # (default: none)
  tabs:                                    # ARRAY AT COMPONENT LEVEL — NOT inside properties
    - title: Tab 1                         # Tab label text
      components:                          # Content for this tab
        - name: paragraph
          properties: { text: Tab 1 content }
    - title: Tab 2
      components:
        - name: paragraph
          properties: { text: Tab 2 content }
```

### Key Notes
- `tabs:` array is at component level (sibling of `properties:`), NEVER inside `properties:`
- Each tab has `title:` and `components:` — any component types can go inside

<!-- section_type: component | component_name: accordion | category: interactive -->
## Component: accordion

Expandable/collapsible content panels. Uses `items:` array at COMPONENT level.
Structure: `- name: accordion` then `properties:` + `items:` — NEVER use `- accordion:` inline format.
`items:` is an array property — place at COMPONENT level, NOT inside `properties:`.

### Syntax
```yaml
- name: accordion
  properties:
    behavior:
      allowMultipleOpen: false             # Allow multiple panels open (default: false)
    typography:
      title:
        size: lg                           # (default: lg)
        weight: semibold                   # (default: semibold)
        color: *color-primary              # Default: *color-primary (auto-resolves to theme)
      content:
        size: md                           # (default: md)
        weight: regular                    # (default: regular)
        color: *color-text                 # Default: *color-text (auto-resolves to theme)
    layout:
      widthMode: stretch                   # STRING (default: stretch)
    appearance:
      titleBackground:
        color: *color-background           # Default: *color-background (auto-resolves to theme)
      border:
        width: 1                           # (default: 1)
        style: solid                       # (default: solid)
        color: '#d1d5db'                   # (default: '#d1d5db')
        position: bottom                   # top|bottom|left|right|all (default: bottom)
      contentBackground:
        color: *color-background           # Default: *color-background (auto-resolves to theme)
        opacity: 100                  # (default: 100)
      radius: sm                           # (default: sm)
      shadow: none                         # (default: none)
      shadowColor: ''                      # (default: '')
    spacing:
      marginBlock: md                      # (default: md)
      marginInline: none                   # (default: none)
      paddingBlock: sm                     # (default: sm)
      paddingInline: sm                    # (default: sm)
  items:                                   # ARRAY AT COMPONENT LEVEL — NOT inside properties
    - title: First Question                # Panel header text
      components:                          # Panel content
        - name: paragraph
          properties: { text: Answer to the first question. }
    - title: Second Question
      components:
        - name: paragraph
          properties: { text: Answer to the second question. }
```

### Key Notes
- `items:` array is at component level, NEVER inside `properties:`
- Each item has `title:` (header text) and `components:` (panel content)
- Commonly used for FAQs

<!-- section_type: component | component_name: carousel | category: interactive -->
## Component: carousel

Sliding/fading content carousel. Uses `slides:` array at COMPONENT level.
Structure: `- name: carousel` then `properties:` + `slides:` — NEVER use `- carousel:` inline format.
`slides:` is an array property — place at COMPONENT level, NOT inside `properties:`.

### Syntax
```yaml
- name: carousel
  properties:
    behavior:
      autoplay: true                       # Auto-advance slides (default: true)
      delay: 3000                          # Auto-advance delay in ms (default: 3000)
      loop: true                           # Loop back to start (default: true)
      pauseOnHover: true                   # Pause on mouse hover (default: true)
      swipeEnabled: true                   # Touch swipe support (default: true)
      swipeThreshold: 50                   # Swipe distance threshold px (default: 50)
      keyboardNavigation: true             # Arrow key navigation (default: true)
    animation:
      effect: slide                        # slide|fade (default: slide)
      duration: 300                        # Transition duration in ms (default: 300)
    navigation:
      showArrows: true                     # Show prev/next arrows (default: true)
      showDots: true                       # Show dot indicators (default: true)
      arrowStyle: chevron                  # chevron|default (default: chevron)
      arrowPosition: inside                # inside|outside (default: inside)
    indicators:
      style: dots                          # dots|bars|numbers (default: dots)
      position: bottom                     # bottom|top (default: bottom)
    accessibility:
      showPauseButton: true                # Show pause/play button (default: true)
      ariaLabel: Image carousel            # Screen reader label (default: 'Image carousel')
    appearance:
      shadow: none                         # (default: none)
      shadowColor: ''                      # (default: '')
    spacing:
      marginBlock: lg                      # (default: lg)
      marginInline: none                   # (default: none)
  slides:                                  # ARRAY AT COMPONENT LEVEL — NOT inside properties
    - components:                          # Each slide contains components
        - name: image
          properties:
            source: { url: 'https://...', altText: Slide 1 }
            appearance: { fit: cover, cornerStyle: lg }
    - components:
        - name: image
          properties:
            source: { url: 'https://...', altText: Slide 2 }
```

### Key Notes
- `slides:` array is at component level, NEVER inside `properties:`
- Each slide has `components:` — any component types can go inside
- Use `animation.effect: fade` for crossfade transitions

<!-- section_type: component | component_name: ticker | category: interactive -->
## Component: ticker

Horizontally scrolling strip of content cards. Uses `columns:` array at COMPONENT level.
Structure: `- name: ticker` then `properties:` + `columns:` — NEVER use `- ticker:` inline format.
`columns:` is an array property — place at COMPONENT level, NOT inside `properties:`.
Ticker background is always transparent; only column backgrounds are configurable.

### Syntax
```yaml
- name: ticker
  properties:
    behavior:
      direction: left                      # left|right (default: left)
      speed: 25                            # Pixels per second for continuous mode (default: 25)
      mode: continuous                     # continuous|step (default: continuous)
      pauseOnHover: true                   # (default: true)
      pauseDuration: 3000                  # Pause between steps in ms (default: 3000)
    layout:
      widthMode: fit                       # fit|120|200|280|360|480 — uniform width for all columns in px (default: fit)
      gap: lg                              # Gap between columns. Spacing token (default: lg)
    spacing:
      marginBlock: md                      # (default: md)
      marginInline: none                   # (default: none)
    appearance:
      columnBackground: *color-background # Default: *color-background (auto-resolves to theme)
      columnOpacity: 0               # 0=transparent (default), 100=opaque
      columnRadius: none                   # none|xs|sm|md|lg|xl|xxl|pill (default: none)
      columnBorder:
        width: 0                           # (default: 0)
        style: solid                       # (default: solid)
        color: *color-primary            # Default: *color-primary (auto-resolves to theme)
  columns:                                 # ARRAY AT COMPONENT LEVEL — NOT inside properties
    - components:                          # Each column is a data container
        - name: heading
          properties: { text: Card 1, level: 4 }
        - name: paragraph
          properties: { text: Description }
    - components:
        - name: heading
          properties: { text: Card 2, level: 4 }
```

### Key Notes
- `columns:` array is at component level, NEVER inside `properties:`
- `layout.widthMode` applies to ALL columns uniformly — single value, not per-column
- For individual card styling, nest a `layout-column` inside each column entry
- Ticker background is always transparent — use `columnBackground` for card styling

<!-- section_type: component | component_name: panorama-display | category: interactive -->
## Component: panorama-display

Horizontally scrollable wide image with optional auto-scroll.
Structure: `- name: panorama-display` then `properties:`.

### Syntax
```yaml
- name: panorama-display
  properties:
    source:
      url: https://example.com/wide-image.jpg  # Wide panoramic image URL
      altText: Panorama image              # Alt text (default: 'Panorama image')
    behavior:
      autoScroll: false                    # Auto-scroll horizontally (default: false)
      autoScrollSpeed: 30                  # Auto-scroll speed px/sec (default: 30)
      stepDistance: 300                     # Manual scroll step in px (default: 300)
      pauseOnHover: true                   # (default: true)
      initialPosition: left                # left|center|right (default: left)
    spacing:
      marginBlock: md                      # (default: md)
      marginInline: none                   # (default: none)
    appearance:
      border:
        width: 0                           # (default: 0)
        style: solid                       # (default: solid)
        color: '#e5e7eb'                   # (default: '#e5e7eb')
      radius: none                         # (default: none)
      shadow: none                         # (default: none)
      shadowColor: ''                      # (default: '')
```

<!-- section_type: component | component_name: textbox | category: form -->
## Component: textbox

Single-line text input field. Use inside a `form` component.
Structure: `- name: textbox` then `properties:` — NEVER use `- textbox:` inline format.

### Syntax
```yaml
- name: textbox
  properties:
    label:
      text: Email                          # Label text (default: 'Label')
      show: true                           # Show label (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: ''                             # Form field name for submission (default: '')
      placeholder: your@email.com          # Placeholder text (default: 'Enter text...')
      initialValue: ''                     # Pre-filled value (default: '')
      validation: none                     # none|email|phone|zipCode|url|password|creditCard|lettersOnly|alphanumeric (default: none)
      helperText: ''                       # Help text below field (default: '')
      required: false                      # Required field (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      accentColor: '#3b82f6'               # Focus ring color (default: '#3b82f6')
```

<!-- section_type: component | component_name: textarea | category: form -->
## Component: textarea

Multi-line text input. Use inside a `form` component.
Structure: `- name: textarea` then `properties:`.

### Syntax
```yaml
- name: textarea
  properties:
    label:
      text: Message                        # (default: 'Label')
      show: true                           # (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: ''                             # (default: '')
      placeholder: Type your message...    # (default: 'Enter text...')
      rows: 4                              # Number of visible rows (default: 4)
      helperText: ''                       # (default: '')
      required: false                      # (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      accentColor: '#3b82f6'               # (default: '#3b82f6')
```

<!-- section_type: component | component_name: dropdown | category: form -->
## Component: dropdown

Select/dropdown field. Use inside a `form` component.
Structure: `- name: dropdown` then `properties:`.

### Syntax
```yaml
- name: dropdown
  properties:
    label:
      text: Choose                         # (default: 'Label')
      show: true                           # (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: ''                             # (default: '')
      placeholder: Choose an option        # (default: 'Choose an option')
      options: "Option 1\nOption 2\nOption 3"  # Newline-separated options string (default: "Option 1\nOption 2\nOption 3")
      helperText: ''                       # (default: '')
      required: false                      # (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      accentColor: '#3b82f6'               # (default: '#3b82f6')
```

### Key Notes
- `field.options` is a SINGLE STRING with options separated by `\n` (newlines), NOT a YAML array

<!-- section_type: component | component_name: checkbox | category: form -->
## Component: checkbox

Checkbox input field. Use inside a `form` component.
Structure: `- name: checkbox` then `properties:`.

### Syntax
```yaml
- name: checkbox
  properties:
    label:
      text: Select options                 # (default: 'Select options')
      show: true                           # (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: ''                             # (default: '')
      options: "Option 1\nOption 2\nOption 3"  # Newline-separated options (default: "Option 1\nOption 2\nOption 3")
      helperText: ''                       # (default: '')
      required: false                      # (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      color: '#2563eb'                     # Checkbox accent color (default: '#2563eb')
```

<!-- section_type: component | component_name: radio | category: form -->
## Component: radio

Radio button input field. Use inside a `form` component.
Structure: `- name: radio` then `properties:`.

### Syntax
```yaml
- name: radio
  properties:
    label:
      text: Choose one                     # (default: 'Choose one')
      show: true                           # (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: radio1                         # Group name — radios with same name are mutually exclusive (default: 'radio1')
      options: "Option 1\nOption 2\nOption 3"  # Newline-separated options (default: "Option 1\nOption 2\nOption 3")
      helperText: ''                       # (default: '')
      required: false                      # (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      color: '#2563eb'                     # Radio accent color (default: '#2563eb')
```

<!-- section_type: component | component_name: calendar | category: form -->
## Component: calendar

Date picker input field. Use inside a `form` component.
Structure: `- name: calendar` then `properties:`.

### Syntax
```yaml
- name: calendar
  properties:
    label:
      text: Date                           # (default: 'Date')
      show: true                           # (default: true)
      typography:
        weight: medium                     # (default: medium)
        color: *color-primary              # Theme alias or hex (default: '#374151')
    field:
      name: ''                             # (default: '')
      value: ''                            # Pre-selected date (default: '')
      min: ''                              # Minimum date (default: '')
      max: ''                              # Maximum date (default: '')
      helperText: ''                       # (default: '')
      required: false                      # (default: false)
    appearance:
      size: sm                             # sm|md|lg (default: sm)
      accentColor: '#3b82f6'               # (default: '#3b82f6')
```

<!-- section_type: component | component_name: icon | category: marketing -->
## Component: icon

Lucide Icons display (SVG-based). The component name is always `icon` — the icon name goes in `properties.name`.
Structure: `- name: icon` then `properties:` — NEVER use `- star:` or `- heart:` as component names.

### Syntax
```yaml
- name: icon
  properties:
    name: star                             # Lucide icon name in kebab-case (default: 'star')
    size: "36"                             # Icon size as STRING in px (default: "36")
    strokeWidth: "2"                       # SVG stroke width as STRING (default: "2")
    color: *color-primary                  # Default: *color-primary (auto-resolves to theme). Use *color-accent (features), *color-background (dark bg)
```

### Key Notes
- Component is ALWAYS `- name: icon` — the icon name is `properties.name`, NOT the component name
- `size` and `strokeWidth` are STRINGS (e.g., `"36"`, `"2"`), not numbers
- Icon names use kebab-case (e.g., `map-pin`, `user-plus`, `bar-chart-2`)
- Common icons: `star`, `heart`, `check-circle`, `shopping-cart`, `home`, `search`, `settings`, `user`, `mail`, `phone`, `map-pin`, `clock`, `lock`, `play-circle`, `arrow-right`, `zap`, `users`, `utensils`, `graduation-cap`, `briefcase`, `plane`, `building`

<!-- section_type: component | component_name: badge | category: marketing -->
## Component: badge

Colored inline label/tag for status, categories, or highlights.
Structure: `- name: badge` then `properties:` — NEVER use `- badge:` inline format.

### Syntax
```yaml
- name: badge
  properties:
    text: NEW                              # Badge text (default: 'Badge')
    variant: info                          # info (blue) | success (green) | warning (amber) | danger (red) (default: info)
    pill: false                            # Pill shape (rounded) (default: false)
    typography:
      size: xxs                            # (default: xxs)
      color: ''                            # Override auto variant color (default: '' = auto from variant)
```

### Key Notes
- Variants: `info` = blue, `success` = green, `warning` = amber, `danger` = red
- `typography.color: ''` (empty) = auto-colored by variant. Set explicitly to override.

<!-- section_type: component | component_name: rating | category: marketing -->
## Component: rating

Star or heart rating display (supports half values like 3.5).
Structure: `- name: rating` then `properties:`.

### Syntax
```yaml
- name: rating
  properties:
    value: 3.5                             # Rating value, supports half steps (default: 3.5)
    iconType: star                         # star|heart (default: star)
    showCount: false                       # Show numeric value (default: false)
    color: '#f59e0b'                       # Star/heart fill color (default: '#f59e0b')
    typography:
      size: md                             # (default: md)
      color: *color-secondary             # Default: *color-secondary (auto-resolves to theme)
```

<!-- section_type: component | component_name: progress-bar | category: marketing -->
## Component: progress-bar

Horizontal completion/progress bar.
Structure: `- name: progress-bar` then `properties:`.

### Syntax
```yaml
- name: progress-bar
  properties:
    percent: 50                            # Fill percentage 0-100 (default: 50)
    thickness: medium                      # small|medium|large (default: medium)
    color: '#3b82f6'                       # Bar fill color. Theme alias: *color-accent | or hex (default: '#3b82f6')
    trackColor: '#e5e7eb'                  # Track background color (default: '#e5e7eb')
    colorGradient: false                   # true = red-amber-green gradient based on percent (default: false)
    appearance:
      radius: pill                         # none|xs|sm|md|lg|xl|xxl|pill (default: pill)
```

<!-- section_type: component | component_name: counter-up | category: marketing -->
## Component: counter-up

Animated number counter that counts up when scrolled into viewport.
Structure: `- name: counter-up` then `properties:`.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: counter-up
  properties:
    endValue: 100                          # Target number (default: 100)
    duration: 2000                         # Animation duration in ms (default: 2000)
    prefix: ''                             # Text before number, e.g., "$" (default: '')
    suffix: ''                             # Text after number, e.g., "+" (default: '')
    typography:
      size: xxl                            # xxs|xs|sm|md|lg|xl|xxl|xxxl (default: xxl)
      weight: bold                         # (default: bold)
      color: *color-primary                # Default: *color-primary (auto-resolves to theme). Use *color-background on dark bg only
      align: center                        # left|center|right (default: center)
```

<!-- section_type: component | component_name: countdown | category: marketing -->
## Component: countdown

Live countdown timer to a target date/time.
Structure: `- name: countdown` then `properties:`.
NEVER use `typography.fontFamily`.

### Syntax
```yaml
- name: countdown
  properties:
    targetDate: '2026-12-31T23:59:59'      # ISO 8601 date-time string (required)
    format: 'DD:HH:MM:SS'                 # DD:HH:MM:SS | HH:MM:SS | MM:SS (default: 'DD:HH:MM:SS')
    expiredText: Expired                   # Text shown when countdown reaches zero (default: 'Expired')
    typography:
      size: xl                             # (default: xl)
      weight: bold                         # (default: bold)
      color: *color-primary                # Default: *color-primary (auto-resolves to theme). Use *color-background on dark bg only
      align: center                        # left|center|right (default: center)
```

---

## Container Components — Child Key Reference

Each container component uses a specific key for its children. Using the wrong key is a **breaking error** — children will not render.

| Component | Container Key | Item has `title`? | Notes |
|-----------|---------------|-------------------|-------|
| `layout-row` | `components:` | No | NEVER use `columns:` |
| `layout-column` | `components:` | No | NEVER use `children:` |
| `tabs` | `tabs:` | Yes (required) | Each tab: `{title, components}` |
| `accordion` | `items:` | Yes (required) | Each item: `{title, components}` |
| `carousel` | `slides:` | No | Each slide: `{components}` |
| `columnsgrid` | `columns:` | No | Each column: `{components}`. Count in `properties.layout.columns` |
| `ticker` | `columns:` | No | Each column: `{components}`. Same pattern as columnsgrid |
| `form` | `components:` | No | Contains form field components |

### Correct Syntax Examples

```yaml
# TABS — `tabs:` array, each with required `title`
- name: tabs
  properties:
    layout: { widthMode: stretch }
  tabs:
    - title: "Tab 1"
      components:
        - name: paragraph
          properties: { text: "Tab 1 content" }
    - title: "Tab 2"
      components:
        - name: paragraph
          properties: { text: "Tab 2 content" }

# ACCORDION — `items:` array, each with required `title`
- name: accordion
  items:
    - title: "Question 1"
      components:
        - name: paragraph
          properties: { text: "Answer 1" }
    - title: "Question 2"
      content: "Simple text answer"

# CAROUSEL — `slides:` array, each with `components:` only
- name: carousel
  properties:
    behavior: { autoplay: true, delay: 3000 }
  slides:
    - components:
        - name: image
          properties: { source: { url: https://example.com/1.jpg } }
    - components:
        - name: image
          properties: { source: { url: https://example.com/2.jpg } }

# COLUMNSGRID — `columns:` array + count in properties.layout.columns
- name: columnsgrid
  properties:
    layout: { columns: 3, gap: md }
  columns:
    - components:
        - name: paragraph
          properties: { text: "Column 1" }
    - components:
        - name: paragraph
          properties: { text: "Column 2" }
    - components:
        - name: paragraph
          properties: { text: "Column 3" }

# TICKER — `columns:` array (same as columnsgrid)
- name: ticker
  properties:
    behavior: { direction: left, speed: 25 }
  columns:
    - components:
        - name: heading
          properties: { text: "Item 1" }
    - components:
        - name: heading
          properties: { text: "Item 2" }
```

### Common Container Mistakes

```yaml
# WRONG: tabs using `items:` (accordion pattern)
- name: tabs
  items:             # ❌ tabs uses `tabs:`, NOT `items:`
    - title: "Tab 1"

# WRONG: accordion using `tabs:`
- name: accordion
  tabs:              # ❌ accordion uses `items:`, NOT `tabs:`
    - title: "Item 1"

# WRONG: carousel using `items:`
- name: carousel
  items:             # ❌ carousel uses `slides:`, NOT `items:`

# WRONG: columnsgrid with `columns: 3` at root
- name: columnsgrid
  columns: 3         # ❌ overwrites columns array with integer
  components:        # ❌ should be `columns:` array
    - name: layout-column

# WRONG: layout-row using `columns:`
- name: layout-row
  columns:           # ❌ layout-row uses `components:`, NEVER `columns:`
    - name: button

# WRONG: missing `title` on tabs/accordion items
- name: tabs
  tabs:
    - components:    # ❌ missing `title:` — tab button will be blank
        - name: paragraph
```
