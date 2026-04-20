# SwiftSites Common YAML Mistakes and Quick Patterns

> Reference for validation and future builder prompt injection.

## Quick Patterns

Ready-to-use patterns for common website sections.

### Hero Section (Image Background with Overlay)
```yaml
- name: image
  properties:
    source: { url: 'https://example.com/hero.jpg', altText: Hero background }
    appearance: { minHeight: 37.5, fit: cover, overlay: { enabled: true, color: 'rgba(0,0,0,0.4)', opacity: 0.4 } }
    layout: { widthMode: stretch }
  components:
    - name: layout-column
      properties:
        layout: { horizontalAlign: center }
        spacing: { paddingBlock: xxl }
      components:
        - name: eyebrow
          properties: { text: Welcome to Our Site, typography: { color: *color-background, align: center } }
        - name: heading
          properties: { text: Your Bold Headline, level: 1, typography: { color: *color-background, size: xxxl, weight: bold, align: center } }
        - name: paragraph
          properties: { text: Supporting description text, typography: { color: *color-background, align: center } }
        - name: button
          properties: { text: Get Started, appearance: { background: { color: *color-accent } }, typography: { color: *color-background } }
```

### Hero Section (Split — Text Left, Image Right)
```yaml
- name: layout-row
  properties:
    layout: { wrap: nowrap, verticalAlign: center }
    spacing: { paddingBlock: xxl }
  components:
    - name: layout-column
      properties:
        layout: { widthMode: "50", horizontalAlign: left }
        spacing: { paddingInline: lg }
      components:
        - name: eyebrow
          properties: { text: About Us }
        - name: heading
          properties: { text: Bold Headline, level: 1, typography: { size: xxxl, align: left } }
        - name: paragraph
          properties: { text: Description text, typography: { align: left } }
        - name: button
          properties: { text: Learn More }
    - name: image
      properties:
        source: { url: 'https://example.com/photo.jpg', altText: Feature }
        layout: { widthMode: "50" }
        appearance: { cornerStyle: lg, minHeight: 25 }
```

### 3-Column Card Grid
```yaml
- name: columnsgrid
  properties:
    layout: { columns: 3, gap: lg }
    responsive: { breakpoints: { md: 2, sm: 1 } }
    appearance: { columnRadius: md, columnBackground: *color-background, columnOpacity: 100 }
  columns:
    - components:
        - name: image
          properties: { source: { url: '...' }, appearance: { minHeight: 12.5, fit: cover } }
        - name: heading
          properties: { text: Feature 1, level: 3 }
        - name: paragraph
          properties: { text: Description }
    - components: [...]
    - components: [...]
```

### Statistics Bar
```yaml
- name: layout-row
  properties:
    layout: { horizontalAlign: center, wrap: wrap }
    appearance: { background: { color: *color-primary, opacity: 100 } }
    spacing: { paddingBlock: xxl }
  components:
    - name: layout-column
      properties: { layout: { horizontalAlign: center, widthMode: "25" } }
      components:
        - name: counter-up
          properties: { endValue: 10000, suffix: "+", typography: { size: xxxl, weight: bold, color: *color-background, align: center } }
        - name: paragraph
          properties: { text: Happy Customers, typography: { align: center, size: sm, color: *color-background } }
```

### FAQ Accordion
```yaml
- name: accordion
  properties:
    behavior: { allowMultipleOpen: false }
    appearance: { radius: md, border: { width: 1, color: '#e5e7eb' } }
  items:
    - title: What is your return policy?
      components:
        - name: paragraph
          properties: { text: We accept returns within 30 days... }
    - title: How long does shipping take?
      components:
        - name: paragraph
          properties: { text: Standard shipping takes 3-5 business days... }
```

### Testimonial Carousel
```yaml
- name: carousel
  properties:
    behavior: { autoplay: true, delay: 5000 }
    animation: { effect: fade }
  slides:
    - components:
        - name: blockquote
          properties: { quote: "Amazing service!", cite: "Jane D." }
        - name: rating
          properties: { value: 5, iconType: star }
```

### Contact Form
```yaml
- name: form
  properties:
    submit: { buttonText: Send Message }
    appearance: { radius: md, shadow: soft, background: { color: *color-background, opacity: 100 } }
    spacing: { paddingBlock: lg, paddingInline: lg }
  components:
    - name: textbox
      properties: { label: { text: Name }, field: { placeholder: Your name, required: true } }
    - name: textbox
      properties: { label: { text: Email }, field: { placeholder: your@email.com, required: true, validation: email } }
    - name: textbox
      properties: { label: { text: Phone }, field: { placeholder: Your phone number } }
    - name: dropdown
      properties: { label: { text: Subject }, field: { options: "General Inquiry\nSupport\nFeedback" } }
    - name: textarea
      properties: { label: { text: Message }, field: { placeholder: Your message, rows: 5, required: true } }
```

### Pricing Table
```yaml
- name: columnsgrid
  properties: { layout: { columns: 3, gap: lg } }
  columns:
    - components:
        - name: heading
          properties: { text: Starter, level: 3, typography: { align: center } }
        - name: counter-up
          properties: { prefix: "$", endValue: 29, suffix: /mo, typography: { size: xxl, weight: bold, align: center } }
        - name: paragraph
          properties: { text: "Feature 1\nFeature 2\nFeature 3", typography: { align: center } }
        - name: button
          properties: { text: Get Started }
    - components: [...]
```

### Footer
```yaml
- name: layout-row
  properties:
    layout: { tag: footer, wrap: wrap }
    appearance: { background: { color: *color-primary, opacity: 100 } }
    spacing: { paddingBlock: xl, paddingInline: lg }
  components:
    - name: layout-column
      properties: { layout: { widthMode: "33", horizontalAlign: left } }
      components:
        - name: heading
          properties: { text: Company Name, level: 4, typography: { color: *color-background } }
        - name: paragraph
          properties: { text: "123 Street, City\nphone@email.com", typography: { color: *color-background, size: sm } }
    - name: layout-column
      properties: { layout: { widthMode: "33", horizontalAlign: left } }
      components:
        - name: heading
          properties: { text: Quick Links, level: 4, typography: { color: *color-background } }
        - name: link
          properties: { text: About Us, href: '#about', typography: { color: *color-background } }
        - name: link
          properties: { text: Services, href: '#services', typography: { color: *color-background } }
    - name: layout-column
      properties: { layout: { widthMode: "33", horizontalAlign: left } }
      components:
        - name: heading
          properties: { text: Follow Us, level: 4, typography: { color: *color-background } }
        - name: layout-row
          properties: { layout: { gap: sm, wrap: nowrap } }
          components:
            - name: icon
              properties: { name: facebook, color: *color-background }
            - name: icon
              properties: { name: instagram, color: *color-background }
            - name: icon
              properties: { name: youtube_activity, color: *color-background }
```

---

## Common YAML Mistakes and How to Fix Them

These are the most frequent errors when generating SwiftSites YAML. ALWAYS check your output against this list before finalizing.

### MISTAKE 1: Using `columns:` instead of `components:` on layout-row

layout-row children go under `components:`. Only columnsgrid and ticker use `columns:` for their children.

```yaml
# WRONG — layout-row does NOT use columns:
- name: layout-row
  properties:
    layout: { horizontalAlign: center }
  columns:
    - name: button
      properties: { text: Click }

# CORRECT — layout-row uses components:
- name: layout-row
  properties:
    layout: { horizontalAlign: center }
  components:
    - name: button
      properties: { text: Click }
```

### MISTAKE 2: widthMode as integer instead of string

`layout.widthMode` MUST be a quoted string. Integer values produce no CSS width.

```yaml
# WRONG — integer, no CSS generated
layout:
  widthMode: 50

# CORRECT — string token, generates flex: 0 0 50%
layout:
  widthMode: "50"
```

Valid widthMode values (all strings): `"fit"`, `"16"`, `"25"`, `"33"`, `"50"`, `"66"`, `"75"`, `"83"`, `"stretch"`

### MISTAKE 3: columnsgrid `columns:` count at component level instead of inside properties

The number of columns goes in `properties.layout.columns`. The `columns:` at component level is the array of children.

```yaml
# WRONG — columns: 3 at component level overwrites the children array
- name: columnsgrid
  columns: 3
  properties:
    layout: { gap: lg }
  components:
    - name: heading

# CORRECT — column count inside properties, children in columns: array
- name: columnsgrid
  properties:
    layout:
      columns: 3
      gap: lg
  columns:
    - components:
        - name: heading
          properties: { text: Card 1 }
```

### MISTAKE 4: columnsgrid children under `components:` instead of `columns:`

columnsgrid uses `columns:` array at component level for children, NOT `components:`.

```yaml
# WRONG — columnsgrid does NOT use components: for children
- name: columnsgrid
  properties:
    layout: { columns: 3 }
  components:
    - name: heading

# CORRECT — columnsgrid uses columns: array, each with components:
- name: columnsgrid
  properties:
    layout: { columns: 3 }
  columns:
    - components:
        - name: heading
          properties: { text: Card 1 }
    - components:
        - name: heading
          properties: { text: Card 2 }
```

### MISTAKE 5: Icon size as design token instead of numeric string

Icon `size` and `strokeWidth` are numeric strings, NOT design tokens like `xl` or `lg`.

```yaml
# WRONG — tokens don't work for icon size
- name: icon
  properties:
    name: star
    size: xl
    strokeWidth: bold

# CORRECT — numeric strings for size and strokeWidth
- name: icon
  properties:
    name: star
    size: "36"
    strokeWidth: "2"
```

Common icon sizes: `"20"` (small), `"24"` (default), `"36"` (medium), `"48"` (large), `"64"` (hero)

### MISTAKE 6: Padding under `appearance.padding` instead of `spacing`

Padding goes under `spacing.paddingBlock` / `spacing.paddingInline`, NOT `appearance.padding`.

```yaml
# WRONG — do NOT use appearance.padding
- name: layout-column
  properties:
    appearance:
      padding:
        block: lg
        inline: md

# CORRECT — padding is under spacing
- name: layout-column
  properties:
    spacing:
      paddingBlock: lg
      paddingInline: md
```

### MISTAKE 7: Array properties inside `properties:` instead of at component level

`items:` (accordion), `tabs:` (tabs), `slides:` (carousel), `columns:` (columnsgrid, ticker) MUST be at component level.

```yaml
# WRONG — tabs array inside properties
- name: tabs
  properties:
    tabs:
      - title: Tab 1
        components: [...]

# CORRECT — tabs array at component level
- name: tabs
  properties:
    layout: { widthMode: stretch }
  tabs:
    - title: Tab 1
      components:
        - name: paragraph
          properties: { text: Content }
```

### MISTAKE 8: Unquoted aspectRatio values

```yaml
# RISKY — YAML may interpret as division
aspectRatio: 16/9

# CORRECT — quoted string
aspectRatio: '16/9'
```

### MISTAKE 9: Icon names not matching Lucide Icons

Use exact Lucide icon names (kebab-case). Common wrong names and their corrections:

| Wrong | Correct |
|-------|---------|
| `shopping_cart` | `shopping-cart` |
| `location_on` | `map-pin` |
| `person` | `user` |
| `favorite` | `heart` |
| `check_circle` | `check-circle` |
| `bar_chart` | `bar-chart-2` |
| `person_add` | `user-plus` |
| `rocket_launch` | `rocket` |
| `bolt` | `zap` |
| `delete` | `trash-2` |

### MISTAKE 10: typography on layout-row or layout-column

Layout containers do NOT have a `typography` property. Set it on child text components.

```yaml
# WRONG — layout-row has no typography property
- name: layout-row
  properties:
    typography:
      color: '#ffffff'

# CORRECT — set typography on child text components
- name: layout-row
  components:
    - name: heading
      properties:
        typography:
          color: '#ffffff'
```

### MISTAKE 11: Mixing widthMode "stretch" with fixed-width siblings in layout-row

```yaml
# WRONG — stretch + "50" = overflow
- name: layout-row
  components:
  - name: image
    properties: { layout: { widthMode: stretch } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }

# CORRECT — compatible widths + nowrap
- name: layout-row
  properties: { layout: { wrap: nowrap } }
  components:
  - name: image
    properties: { layout: { widthMode: "50" } }
  - name: layout-column
    properties: { layout: { widthMode: "50" } }
```

### MISTAKE 12: Excessive default properties bloating YAML

Only set properties you want to CHANGE. Default values are applied automatically.

```yaml
# WRONG — all these are already defaults, don't include them
- name: layout-column
  properties:
    appearance:
      border: { width: 0, style: solid, color: *color-primary }
      radius: none
      shadow: none
      shadowColor: ''
      blur: false
      background: { color: *color-background, opacity: 0 }
    spacing: { marginBlock: none, marginInline: none }

# CORRECT — only set what you need
- name: layout-column
  properties:
    layout: { widthMode: "50", horizontalAlign: center }
```
