# Swift Sites LLM Component Guide

Concise guide for LLMs to generate website YAML using Swift Sites components.

## Quick Start

```yaml
- name: page
  properties:
    background: { color: '#ffffff' }
  components:
    - name: heading
      properties:
        text: Hello World
        level: 1
```

**Key Rules:**
- YAML is the source of truth
- Every component has: `name`, `properties`, optional `components`
- Container components: `page`, `layout-row`, `layout-column`, `columnsgrid`, `form`, `image`, `gif`
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

### Text Alignment

`left`, `center`, `right`, `justify`

## Width Mode Property (Text & Media Components)

**Applies to:** `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`, `link`, `image`, `gif`

**Property path:** `layout.widthMode`

| Value | Description | Behavior |
|-------|-------------|----------|
| `fit` | Fit to content | Component shrinks to its natural content width |
| `25` | 25% width | Component takes 25% of parent container width |
| `50` | 50% width | Component takes 50% of parent container width |
| `75` | 75% width | Component takes 75% of parent container width |
| `stretch` | Full width (default) | Component stretches to fill available width |

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

## Align Property (Layout Containers)

**Applies to:** `layout-row`, `layout-column`

**Property path:** `layout.align`

### For layout-row (horizontal flex)
Controls **vertical alignment** of children (cross-axis):

| Value | Description |
|-------|-------------|
| `start` | Align children to top |
| `center` | Align children vertically centered |
| `end` | Align children to bottom |
| `stretch` | Stretch children to fill row height (default) |

### For layout-column (vertical flex)
Controls **horizontal alignment** of children (cross-axis):

| Value | Description |
|-------|-------------|
| `start` | Align children to left |
| `center` | Align children horizontally centered (default) |
| `end` | Align children to right |
| `stretch` | Stretch children to fill column width |

**Example:**
```yaml
- name: layout-column
  properties:
    layout: { align: center, gap: md }  # Children centered horizontally
  components:
    - name: heading
      properties:
        text: Centered Heading
        layout: { widthMode: fit }  # Only as wide as text, centered
```

**⚠️ Note:** If `align: stretch` is used on layout-column, `widthMode` will be overridden (children stretch to full width regardless of widthMode setting).

## Component Reference (27 Total)

### Layout & Containers (5)

**page** - Root element
```yaml
- name: page
  properties:
    background: { color: '#ffffff', transparency: 100 }
    layout: { padding: { top: md, right: md, bottom: md, left: md } }
  components: [...]
```

**layout-row** - Horizontal flex
```yaml
- name: layout-row
  properties:
    layout: { tag: section, align: center, gap: md, wrap: nowrap }
    spacing: { paddingBlock: md, marginBlock: lg }
    background: { color: '#ffffff' }
    appearance: { border: { width: 1, style: solid, color: '#e5e7eb' }, radius: md }
  components: [...]
```

**layout-column** - Vertical flex
```yaml
- name: layout-column
  properties:
    layout: { tag: section, align: start, gap: md }
    spacing: { paddingBlock: md, marginBlock: lg }
  components: [...]
```

**columnsgrid** - Responsive grid
```yaml
- name: columnsgrid
  properties:                                    # ← Configuration
    layout: { columns: 3, gap: lg, align: center }
    responsive: { breakpoints: { md: 2, sm: 1 } }
    spacing: { marginBlock: lg }
  columns:                                       # ← AT COMPONENT LEVEL (not inside properties)
    - components: [...]
    - components: [...]
    - components: [...]
```

**form** - Form wrapper
```yaml
- name: form
  properties:
    layout: { direction: column, gap: md }
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
    appearance: { border: { accentColor: '#2563eb' }, background: { color: '#f9f9f9' } }
```

### Media (4)

**image** - Display image
```yaml
- name: image
  properties:
    source: { url: 'https://...jpg', altText: 'Description' }
    presentation: { height: 400px, fit: cover, cornerStyle: md }
    layout: { widthMode: stretch }
  components: [...]  # Optional overlay text
```

**gif** - Animated GIF
```yaml
- name: gif
  properties:
    source: { url: 'https://...gif' }
    presentation: { fit: cover }
```

**video** - YouTube embed
```yaml
- name: video
  properties:
    source: { url: 'https://www.youtube.com/embed/VIDEO_ID' }
    playback: { controls: true, autoplay: false, muted: false }
```

**br** - Vertical break
```yaml
- name: br
  properties:
    size: md
```

### Navigation (3)

**titlebar** - Header/navbar
```yaml
- name: titlebar
  properties:
    branding: { showLogo: true, logoUrl: 'https://...png', title: 'Website' }
    navigation:
      links:
        - label: Home
          href: '#home'
    layout: { alignment: left, height: 60 }
    appearance: { background: { color: '#ffffff' }, border: { width: 1, color: '#e5e7eb' } }
```

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

**accordion** - Expandable sections
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
      content: |
        Answer 1 with multiline support.
        Use pipe operator for multiline text.
    - title: Question 2
      content: Answer 2
```

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
    behavior: { autoplay: true, delay: 4000, loop: true }
    navigation: { showArrows: true, showDots: true }
    spacing: { marginBlock: lg }
  slides:                                        # ← AT COMPONENT LEVEL (not inside properties)
    - components:
        - name: image
          properties:
            source: { url: 'https://...jpg', altText: 'Slide 1' }
            presentation: { height: 500px, fit: cover, cornerStyle: lg }
    - components:
        - name: image
          properties:
            source: { url: 'https://...jpg', altText: 'Slide 2' }
            presentation: { height: 500px, fit: cover, cornerStyle: lg }
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

## Quick Patterns

### Hero Section
```yaml
- name: image
  properties:
    source: { url: 'https://...jpg', altText: Background }
    presentation: { height: 600px, fit: cover }
    layout: { widthMode: stretch }
  components:
    - name: layout-column
      properties: { layout: { align: center }, spacing: { paddingBlock: xl } }
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
          properties: { source: { url: '...' }, presentation: { height: 200px, fit: cover } }
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
  properties: { layout: { columns: 3, gap: md } }
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
          properties: { source: { url: '...' }, presentation: { height: 300px, fit: cover } }
        - name: heading
          properties: { text: Name, level: 3, typography: { align: center, weight: bold } }
        - name: eyebrow
          properties: { text: ROLE, typography: { color: '#2563eb' } }
        - name: paragraph
          properties: { text: Bio, typography: { align: center, size: sm } }
    - components: [...]
    - components: [...]
```

### Statistics Section
```yaml
- name: columnsgrid
  properties: { layout: { columns: 4, gap: lg }, responsive: { breakpoints: { md: 2, sm: 1 } } }
  columns:
    - components:
        - name: heading
          properties: { text: "10,000+", level: 3, typography: { size: xxxl, weight: bold, color: '#2563eb' } }
        - name: paragraph
          properties: { text: Active Users, typography: { align: center, size: sm } }
    - components:
        - name: heading
          properties: { text: "99.9%", level: 3, typography: { size: xxxl, weight: bold, color: '#2563eb' } }
        - name: paragraph
          properties: { text: Uptime }
    - components: [...]
    - components: [...]
```

### Newsletter Signup
```yaml
- name: layout-row
  properties:
    layout: { align: center, gap: lg }
    spacing: { paddingBlock: xl, paddingInline: lg }
    background: { color: '#f0f4f8' }
    appearance: { radius: md }
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

### Before/After Comparison
```yaml
- name: layout-row
  properties:
    layout: { gap: lg, align: center }
    spacing: { paddingBlock: lg }
  components:
    - name: layout-column
      properties: { layout: { align: center } }
      components:
        - name: heading
          properties: { text: Before, level: 3, typography: { color: '#ef4444', weight: bold } }
        - name: paragraph
          properties: { text: "✗ Manual entry" }
        - name: paragraph
          properties: { text: "✗ Error-prone" }
        - name: image
          properties: { source: { url: '...' }, presentation: { height: 200px, fit: cover } }
    - name: layout-column
      properties: { layout: { align: center } }
      components:
        - name: heading
          properties: { text: After, level: 3, typography: { color: '#10b981', weight: bold } }
        - name: paragraph
          properties: { text: "✓ Automated" }
        - name: paragraph
          properties: { text: "✓ 99% accurate" }
        - name: image
          properties: { source: { url: '...' }, presentation: { height: 200px, fit: cover } }
```

### Features with Image
```yaml
- name: layout-row
  properties:
    layout: { gap: xl, align: center }
    spacing: { paddingBlock: xl }
  components:
    - name: image
      properties: { source: { url: '...' }, presentation: { height: 400px, fit: cover } }
    - name: layout-column
      components:
        - name: heading
          properties: { text: Why Choose Us, level: 3, typography: { weight: bold, size: lg } }
        - name: paragraph
          properties: { text: Description, spacing: { marginBlock: md } }
        - name: layout-column
          properties: { layout: { gap: md } }
          components:
            - name: layout-row
              properties: { layout: { gap: md, align: start } }
              components:
                - name: paragraph
                  properties: { text: "✓", typography: { size: lg, weight: bold, color: '#10b981' } }
                - name: layout-column
                  components:
                    - name: heading
                      properties: { text: Feature 1, level: 4, typography: { weight: semibold } }
                    - name: paragraph
                      properties: { text: Feature description, typography: { size: sm, color: '#666' } }
```

### CTA Banners (3 Variants)

**Blue Offer:**
```yaml
- name: layout-row
  properties:
    layout: { gap: md, align: center }
    spacing: { paddingBlock: lg }
    background: { color: '#2563eb' }
    appearance: { radius: md }
  components:
    - name: heading
      properties: { text: Limited Time, level: 3, typography: { color: '#fff', weight: bold } }
    - name: paragraph
      properties: { text: Get 50% off, typography: { color: '#e0e7ff' } }
    - name: button
      properties: { text: Claim Offer, appearance: { background: { color: '#fff' } }, typography: { color: '#2563eb' } }
```

**Warning/Alert:**
```yaml
- name: layout-row
  properties:
    layout: { gap: md, align: center }
    spacing: { paddingBlock: lg }
    background: { color: '#fbbf24' }
    appearance: { radius: md, border: { width: 2, color: '#f59e0b' } }
  components:
    - name: heading
      properties: { text: Important Notice, level: 3, typography: { color: '#78350f', weight: bold } }
    - name: paragraph
      properties: { text: Spots filling fast, typography: { color: '#92400e' } }
    - name: button
      properties: { text: Reserve Now, appearance: { background: { color: '#78350f' } } }
```

**Success/Confirmation:**
```yaml
- name: layout-row
  properties:
    layout: { gap: md, align: center }
    spacing: { paddingBlock: lg }
    background: { color: '#d1fae5' }
    appearance: { radius: md, border: { width: 1, color: '#6ee7b7' } }
  components:
    - name: paragraph
      properties: { text: "✓ Ready to go", typography: { color: '#065f46', weight: semibold } }
    - name: button
      properties: { text: Get Started, appearance: { background: { color: '#059669' } } }
```

### Footer CTA
```yaml
- name: layout-row
  properties:
    layout: { gap: md, align: center, wrap: wrap }
    spacing: { paddingBlock: xl }
    background: { color: '#1f2937' }
  components:
    - name: layout-column
      components:
        - name: heading
          properties: { text: Ready to Start?, level: 2, typography: { color: '#fff', weight: bold, size: xl } }
        - name: paragraph
          properties: { text: Join thousands today, typography: { color: '#d1d5db' } }
    - name: layout-row
      properties: { layout: { gap: md, align: center } }
      components:
        - name: button
          properties: { text: Free Trial, appearance: { background: { color: '#2563eb' } } }
        - name: button
          properties: { text: Schedule Demo, appearance: { background: { color: '#fff' } }, typography: { color: '#1f2937' } }
```

### FAQ Section with Accordion
```yaml
- name: layout-column
  properties:
    layout: { align: center, gap: md }
    spacing: { paddingBlock: xl, paddingInline: md }
  components:
    - name: heading
      properties:
        text: Frequently Asked Questions
        level: 2
        typography: { align: center, color: '#1f2937', size: xxl, weight: bold }
        spacing: { marginBlock: md }
    - name: accordion
      properties:                                # ← All config INSIDE properties
        behavior: { allowMultipleOpen: false }
        typography:
          title: { size: lg, weight: semibold, color: '#1f2937' }
          content: { size: md, weight: regular, color: '#4b5563' }
        appearance:
          titleBackground: { color: '#ffffff' }
          contentBackground: { color: '#ffffff', transparency: 100 }
          border: { width: 1, style: solid, color: '#e5e7eb', position: bottom }
          radius: sm
          padding: { block: md, inline: md }
        spacing: { marginBlock: lg }
        layout: { widthMode: 75 }
      items:                                     # ← items AT COMPONENT LEVEL
        - title: What is your refund policy?
          content: |
            We offer a 30-day money-back guarantee.
            If you're not satisfied, we'll refund you fully.
        - title: How do I get started?
          content: |
            Simply sign up for a free trial and follow
            our onboarding guide. No credit card required.
        - title: Do you offer support?
          content: We provide 24/7 email support and live chat during business hours.
```

### Tabbed Content Section
```yaml
- name: layout-column
  properties:
    layout: { align: center, gap: md }
    spacing: { paddingBlock: xl, paddingInline: md }
  components:
    - name: heading
      properties:
        text: Our Services
        level: 2
        typography: { align: center, color: '#1f2937', size: xxl, weight: bold }
        spacing: { marginBlock: md }
    - name: tabs
      properties:                                # ← All config INSIDE properties
        layout: { orientation: horizontal, widthMode: stretch }
        typography:
          label:
            size: md
            weight: semibold
            active: { color: '#2563eb' }
            inactive: { color: '#6b7280' }
        appearance:
          tab:
            background: { active: '#ffffff', inactive: '#f9fafb' }
            border: { width: 2, style: solid, position: lower }
          content:
            background: { color: '#ffffff', transparency: 100 }
            border: { color: '#e5e7eb', width: 1, style: solid }
            padding: { block: lg, inline: lg }
        spacing: { marginBlock: lg }
      tabs:                                      # ← tabs AT COMPONENT LEVEL
        - title: Design
          components:
            - name: heading
              properties: { text: Custom Design Services, level: 3 }
            - name: paragraph
              properties:
                text: |
                  We create beautiful, user-friendly designs tailored to your brand.
                  Our team of expert designers will work with you every step of the way.
        - title: Development
          components:
            - name: heading
              properties: { text: Full-Stack Development, level: 3 }
            - name: paragraph
              properties: { text: From frontend to backend, we build robust applications. }
        - title: Marketing
          components:
            - name: heading
              properties: { text: Digital Marketing, level: 3 }
            - name: paragraph
              properties: { text: Grow your business with our proven marketing strategies. }
```

### Image Carousel Gallery
```yaml
- name: layout-column
  properties:
    layout: { align: center, gap: md }
    spacing: { paddingBlock: xl, paddingInline: md }
    background: { color: '#ffffff', transparency: 100 }
  components:
    - name: heading
      properties:
        text: Our Work
        level: 2
        typography: { align: center, color: '#1f2937', size: xxl, weight: bold }
        spacing: { marginBlock: md }
    - name: carousel
      properties:                                # ← All config INSIDE properties
        behavior: { autoplay: true, delay: 4000, loop: true }
        navigation: { showArrows: true, showDots: true }
        spacing: { marginBlock: lg }
      slides:                                    # ← slides AT COMPONENT LEVEL
        - components:
            - name: image
              properties:
                source: { url: 'https://...jpg', altText: 'Project 1' }
                presentation: { height: 500px, fit: cover, cornerStyle: lg }
        - components:
            - name: image
              properties:
                source: { url: 'https://...jpg', altText: 'Project 2' }
                presentation: { height: 500px, fit: cover, cornerStyle: lg }
        - components:
            - name: image
              properties:
                source: { url: 'https://...jpg', altText: 'Project 3' }
                presentation: { height: 500px, fit: cover, cornerStyle: lg }
```

## YAML Structure Summary

### Component-Level vs Properties-Level

**Component Structure Pattern:**
```yaml
- name: component-name
  properties:              # ← ALWAYS required for configuration
    spacing: { ... }       # ← Inside properties ✅
    typography: { ... }    # ← Inside properties ✅
    appearance: { ... }    # ← Inside properties ✅
    layout: { ... }        # ← Inside properties ✅
    behavior: { ... }      # ← Inside properties ✅
  components: [...]        # ← Component level ✅ (for containers)
```

**Components with Special Arrays:**
```yaml
# Accordion
- name: accordion
  properties: { behavior: {...}, typography: {...} }
  items: [...]             # ← Component level ✅

# Tabs
- name: tabs
  properties: { layout: {...}, typography: {...} }
  tabs: [...]              # ← Component level ✅

# Carousel
- name: carousel
  properties: { behavior: {...}, navigation: {...} }
  slides: [...]            # ← Component level ✅

# Columnsgrid
- name: columnsgrid
  properties: { layout: {...}, responsive: {...} }
  columns: [...]           # ← Component level ✅
```

### Common Mistakes & Fixes

**❌ WRONG - items inside properties:**
```yaml
- name: accordion
  properties:
    items:                 # ← WRONG! Will cause iteration error
      - title: Q1
        content: A1
```

**✅ CORRECT - items at component level:**
```yaml
- name: accordion
  properties:
    behavior: { allowMultipleOpen: false }
  items:                   # ← CORRECT! At component level
    - title: Q1
      content: A1
```

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
- `bakery_template.yaml` - Full bakery website with all components
- `hero_template.yaml` - Full landing page with all sections
- `restaurant_template.yaml` - Restaurant website

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
  shadow: "0 2px 8px rgba(0,0,0,0.1)"
  padding:
    block: md             # top + bottom padding (token)
    inline: md            # left + right padding (token)

# Layout (containers)
layout:
  tag: section         # semantic HTML
  align: center        # flexbox align
  gap: md              # spacing between children
  wrap: nowrap         # flex-wrap
```

---

## Property Validation

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

## Transparency System

**How transparency works:**
- Transparency values (0-100) are converted to hex alpha
- Appended to the color value automatically
- Example: `color: '#3b82f6', transparency: 50` → `#3b82f680` (80 = 50% in hex)
- Default transparency is `100` (fully opaque)
- `0` = fully transparent, `100` = fully opaque

**Transparency examples:**
```yaml
# Fully opaque white background
background: { color: '#ffffff', transparency: 100 }  # → #ffffffff

# 50% transparent blue background
background: { color: '#2563eb', transparency: 50 }   # → #2563eb80

# Fully transparent (invisible)
background: { color: '#000000', transparency: 0 }    # → #00000000
```

## SSR Implementation Notes

- Components are rendered server-side with Python/Flask
- Default properties from `component_defaults.yaml` are merged automatically
- Only non-default values need to be specified in YAML
- Properties panel shows complete values (defaults + custom)

---

## Validation & Error Prevention

**The renderer will throw errors for:**
1. `items` inside `properties` (should be at component level)
2. `tabs` inside `properties` (should be at component level)
3. `slides` inside `properties` (should be at component level)
4. `columns` inside `properties` (should be at component level)
5. `spacing` outside `properties` (should be inside)
6. Duplicate property keys (e.g., two `layout:` properties)
7. Invalid token values (e.g., `spacing: huge` instead of `lg`)

**Error message format:**
```
Iteration Error: 'builtin_function_or_method' object is not iterable

This usually means you're trying to iterate over a method/function instead of calling it.
```

**Solution:** Check that array properties (`items`, `tabs`, `slides`, `columns`) are at component level, not inside `properties`.

---

**Last Updated:** January 2025 | **Version:** 1.2 (SSR with Structure Fixes)

**Changelog v1.2:**
- ✅ Fixed accordion structure (`items` at component level)
- ✅ Fixed tabs structure (`tabs` at component level)
- ✅ Fixed carousel structure (`slides` at component level)
- ✅ Added critical YAML structure rules section
- ✅ Added common mistakes & fixes section
- ✅ Added comprehensive structure examples
- ✅ Added FAQ, Tabbed Content, and Carousel patterns
- ✅ Updated all component examples with correct indentation
