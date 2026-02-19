# Marketing Components - Development & Testing Plan

## Overview

This document is the implementation blueprint for 7 new marketing-specific components and the enhancement of the existing `br` (divider) component. All implementations follow the existing SSR architecture: Jinja2 macros, `build_styles()` utility, YAML-driven defaults and schemas, and `swift-sites-runtime.js` for interactivity.

### Component Summary

| # | Component | Status | File Location | Runtime JS | Text Props |
|---|-----------|--------|---------------|-----------|------------|
| 1 | br (divider) | Enhance | `ui/_br.html` | No | No |
| 2 | icon | New | `marketing/_icon.html` | No | size, color (direct) |
| 3 | badge | New | `marketing/_badge.html` | No | typography.size, typography.color |
| 4 | rating | New | `marketing/_rating.html` | No | typography.size, typography.color |
| 5 | progress-bar | New | `marketing/_progress_bar.html` | No | No |
| 6 | counter-up | New | `marketing/_counter_up.html` | Yes (IntersectionObserver) | typography.size, typography.weight, typography.color |
| 7 | countdown | New | `marketing/_countdown.html` | Yes (setInterval) | typography.size, typography.weight, typography.color |
| 8 | lottie-animation | New | `marketing/_lottie_animation.html` | Yes (lottie-web CDN) | No |

---

## Architecture Notes

### New Directory

```
ssr_python/templates/components/marketing/
    _icon.html
    _badge.html
    _rating.html
    _progress_bar.html
    _counter_up.html
    _countdown.html
    _lottie_animation.html
```

### Files to Create

| File | Description |
|------|-------------|
| `templates/components/marketing/_icon.html` | Icon component macro |
| `templates/components/marketing/_badge.html` | Badge component macro |
| `templates/components/marketing/_rating.html` | Rating component macro |
| `templates/components/marketing/_progress_bar.html` | Progress bar component macro |
| `templates/components/marketing/_counter_up.html` | Counter-up component macro |
| `templates/components/marketing/_countdown.html` | Countdown component macro |
| `templates/components/marketing/_lottie_animation.html` | Lottie animation component macro |

### Files to Modify (Append-Only Unless Noted)

| File | Change Type | Description |
|------|-------------|-------------|
| `templates/components/ui/_br.html` | **Enhance** | Add type, orientation, thickness, color properties |
| `templates/components/_assembly.html` | Append | Add 7 `{% include %}` lines for marketing/ before dispatcher |
| `templates/components/_dispatcher.html` | Append | Add 7 `{% elif %}` branches before `{% else %}` block |
| `config/component_defaults.yaml` | Update + Append | Update `br` defaults, append 7 new component defaults |
| `config/component_schemas.yaml` | Update + Append | Update `br` schema, append 7 new component schemas |
| `static/css/components.css` | Append | Add CSS for br enhancement + 7 new components |
| `static/js/swift-sites-runtime.js` | Append | Add 3 init methods + update `init()` and `reset()` |
| `static/icon-sprite.svg` | Append | Add ~20 new SVG `<symbol>` elements |
| `static/js/componentTree.js` | Append | Add 7 icon mappings to `iconMap` |
| `static/js/propertiesPanel.js` | Append | Add 7 icon mappings to `componentIcons` |

### Files NOT Modified

- `renderer.py` - no changes needed
- `tokens.yaml` - uses existing token values
- `config/schema_tokens.yaml` - uses existing token groups (typographySizes, fontWeights, spacingScale, etc.)
- All other existing component templates

---

## 1. BR (Divider) - Enhance Existing

### Purpose & Usage

Enhanced visual separator between sections. Supports line styles (solid, dashed, dotted) and decorative shapes (wave, slant) with configurable thickness, color, and orientation. Replaces the current minimal `br` which only has a `size` spacer property.

### YAML Usage

```yaml
# Simple horizontal line
- name: br
  properties:
    type: solid
    color: '#e5e7eb'
    thickness: 2

# Wave separator between sections
- name: br
  properties:
    type: wave
    color: '#3b82f6'
    thickness: 3
    size: md

# Vertical divider in a row
- name: br
  properties:
    type: dashed
    orientation: vertical
    color: '#d1d5db'
    thickness: 1

# Backward compatible (existing YAML still works)
- name: br
  properties:
    size: lg
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `type` | select | `solid` | solid, dashed, dotted, wave, slant | Line style |
| `orientation` | select | `horizontal` | horizontal, vertical | Direction |
| `thickness` | number | `2` | 1-10 | Line thickness in px |
| `color` | color | `#e5e7eb` | Any hex color | Line/shape color |
| `size` | select (token) | `md` | spacingScale tokens | Vertical spacing (existing) |

### Jinja2 Macro

**File:** `ssr_python/templates/components/ui/_br.html`

```jinja2
{% macro render_br(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set div_type = properties.type | default('solid') %}
    {% set orientation = properties.orientation | default('horizontal') %}
    {% set thickness = properties.thickness | default(2) %}
    {% set color = properties.color | default('#e5e7eb') %}
    {% set size = properties.size | default('md') %}
    {% set spacing_value = (tokens.spacing[size]) if tokens and tokens.spacing and (size in tokens.spacing) else '2rem' %}

    {% if div_type == 'wave' %}
        <div class="comp-br comp-br--wave chrome-target"
             data-component-id="{{ component_id }}"
             style="width: 100%; overflow: hidden; line-height: 0; margin: {{ spacing_value }} 0; position: relative;">
            <svg viewBox="0 0 1200 40" preserveAspectRatio="none"
                 style="width: 100%; height: {{ thickness * 10 }}px; display: block;">
                <path d="M0,20 C200,0 400,40 600,20 C800,0 1000,40 1200,20"
                      fill="none" stroke="{{ color }}" stroke-width="{{ thickness }}"/>
            </svg>
        </div>
    {% elif div_type == 'slant' %}
        <div class="comp-br comp-br--slant chrome-target"
             data-component-id="{{ component_id }}"
             style="width: 100%; overflow: hidden; line-height: 0; margin: {{ spacing_value }} 0; position: relative;">
            <svg viewBox="0 0 1200 40" preserveAspectRatio="none"
                 style="width: 100%; height: {{ thickness * 10 }}px; display: block;">
                <polygon points="0,40 1200,0 1200,40" fill="{{ color }}"/>
            </svg>
        </div>
    {% elif orientation == 'vertical' %}
        <div class="comp-br comp-br--vertical chrome-target"
             data-component-id="{{ component_id }}"
             style="border: none; border-left: {{ thickness }}px {{ div_type }} {{ color }}; height: 100%; min-height: 3rem; width: 0; display: inline-block; margin: 0 0.5rem; position: relative;">
        </div>
    {% else %}
        <div class="comp-br chrome-target"
             data-component-id="{{ component_id }}"
             style="height: {{ spacing_value }}; width: 100%; border-bottom: {{ thickness }}px {{ div_type }} {{ color }}; margin: 0.5rem 0; position: relative;">
        </div>
    {% endif %}
{% endmacro %}
```

### Defaults Block

```yaml
br:
  type: solid
  orientation: horizontal
  thickness: 2
  color: '#e5e7eb'
  size: md
```

### Schema Block

```yaml
br:
  groups:
  - id: display
    label: Display
    fields:
    - path: type
      type: select
      label: Style
      options:
      - value: solid
        label: Solid
      - value: dashed
        label: Dashed
      - value: dotted
        label: Dotted
      - value: wave
        label: Wave
      - value: slant
        label: Slant
    - path: orientation
      type: select
      label: Orientation
      options:
      - value: horizontal
        label: Horizontal
      - value: vertical
        label: Vertical
    - path: thickness
      type: number
      label: Thickness (px)
      min: 1
      max: 10
    - path: color
      type: color
      label: Color
    - path: size
      type: select
      label: Spacing
      tokens: spacingScale
```

### CSS Rules

```css
/* --- BR / Divider Enhancement --- */
.comp-br {
    position: relative;
    box-sizing: border-box;
}

.comp-br--wave svg,
.comp-br--slant svg {
    display: block;
}
```

---

## 2. Icon - New Component

### Purpose & Usage

Lightweight vector symbols from the SVG sprite. Used in bulleted lists, pricing cards, social media links, feature highlights, and as decorative accents alongside text.

### YAML Usage

```yaml
# Standalone icon
- name: icon
  properties:
    name: fire
    size: xl
    color: '#ef4444'

# Icon in a row with text
- name: layout-row
  properties:
    layout:
      wrap: nowrap
      gap: sm
  components:
    - name: icon
      properties:
        name: checkmark
        size: md
        color: '#059669'
        layout:
          widthMode: fit
    - name: paragraph
      properties:
        text: Feature included
        layout:
          widthMode: stretch
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `name` | select | `star` | star, heart, checkmark, fire, user, chevron-right, chevron-left, arrow-right, arrow-left, phone, mail, map-pin, clock, tag, search, settings, eye, globe, download, upload | Icon name from SVG sprite |
| `size` | select (token) | `md` | typographySizes tokens (xxs-xxxl, auto) | Icon dimensions, same scale as text |
| `color` | color | `#111827` | Any hex color | Icon stroke/fill color |
| `spacing.marginBlock` | select (token) | `xs` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `xs` | spacingScale tokens | Horizontal margin |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_icon.html`

```jinja2
{% macro render_icon(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set icon_name = properties.name | default('star') %}
    {% set size = properties.size | default('md') %}
    {% set color = properties.color | default('#111827') %}
    {% set base_styles = build_styles(component, tokens) %}

    {# Use typography_sizes tokens for icon sizing, same scale as text components #}
    {% set size_value = tokens.typography_sizes[size] if tokens and tokens.typography_sizes and size in tokens.typography_sizes else '1.8rem' %}

    <span class="comp-icon chrome-target"
          data-component-id="{{ component_id }}"
          style="{{ base_styles }} display: inline-flex; align-items: center; justify-content: center; color: {{ color }}; width: {{ size_value }}; height: {{ size_value }};">
        <svg aria-hidden="true"
             style="width: 100%; height: 100%; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;">
            <use href="#icon-{{ icon_name }}"></use>
        </svg>
    </span>
{% endmacro %}
```

### Defaults Block

```yaml
icon:
  name: star
  size: md
  color: '#111827'
  spacing:
    marginBlock: xs
    marginInline: xs
```

### Schema Block

```yaml
icon:
  groups:
  - id: content
    label: Icon
    fields:
    - path: name
      type: select
      label: Icon
      options:
      - star
      - heart
      - checkmark
      - fire
      - user
      - chevron-right
      - chevron-left
      - arrow-right
      - arrow-left
      - phone
      - mail
      - map-pin
      - clock
      - tag
      - search
      - settings
      - eye
      - globe
      - download
      - upload
    - path: size
      type: select
      label: Size
      tokens: typographySizes
    - path: color
      type: color
      label: Color
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Icon Component --- */
.comp-icon {
    position: relative;
    box-sizing: border-box;
    line-height: 0;
}

.comp-icon svg {
    display: block;
}
```

---

## 3. Badge - New Component

### Purpose & Usage

Small, high-contrast labels for status or highlights. Used over image components ("Sale"), next to headings ("New"), in product cards ("Low Stock"), or as notification indicators.

### YAML Usage

```yaml
# Sale badge
- name: badge
  properties:
    text: 50% Off
    variant: danger
    pill: true
    typography:
      size: xs
      color: '#ffffff'

# Info badge next to heading
- name: layout-row
  properties:
    layout:
      wrap: nowrap
      gap: sm
      verticalAlign: center
  components:
    - name: heading
      properties:
        text: Premium Plan
        layout:
          widthMode: fit
    - name: badge
      properties:
        text: Popular
        variant: info
        pill: true
        layout:
          widthMode: fit
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `text` | text | `Badge` | Any string | Badge label text |
| `variant` | select | `info` | success, danger, warning, info | Color variant |
| `pill` | checkbox | `false` | true, false | Fully rounded corners |
| `typography.size` | select (token) | `xs` | typographySizes tokens | Font size |
| `typography.color` | color | `#ffffff` | Any hex color | Text color override |
| `spacing.marginBlock` | select (token) | `xs` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `xs` | spacingScale tokens | Horizontal margin |

**Variant Color Map (hardcoded in macro):**

| Variant | Background | Default Text |
|---------|-----------|--------------|
| success | `#059669` (green) | `#ffffff` |
| danger | `#dc2626` (red) | `#ffffff` |
| warning | `#d97706` (amber) | `#ffffff` |
| info | `#2563eb` (blue) | `#ffffff` |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_badge.html`

```jinja2
{% macro render_badge(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set text = properties.text | default('Badge') %}
    {% set variant = properties.variant | default('info') %}
    {% set pill = properties.pill | default(false) %}
    {% set base_styles = build_styles(component, tokens) %}

    {# Variant color mapping #}
    {% set variant_colors = {
        'success': {'bg': '#059669', 'text': '#ffffff'},
        'danger':  {'bg': '#dc2626', 'text': '#ffffff'},
        'warning': {'bg': '#d97706', 'text': '#ffffff'},
        'info':    {'bg': '#2563eb', 'text': '#ffffff'}
    } %}
    {% set colors = variant_colors[variant] | default(variant_colors['info']) %}

    {# Use typography color if explicitly set, otherwise use variant default #}
    {% set typo = properties.typography | default({}) %}
    {% set text_color = typo.color if typo.color else colors.text %}
    {% set bg_color = colors.bg %}
    {% set pill_radius = '9999px' if pill else '0.3rem' %}

    <span class="badge badge-{{ variant }} chrome-target"
          data-component-id="{{ component_id }}"
          style="{{ base_styles }} display: inline-block; background-color: {{ bg_color }}; color: {{ text_color }}; border-radius: {{ pill_radius }}; padding: 0.25em 0.65em; font-weight: 600; line-height: 1; white-space: nowrap; vertical-align: baseline;">
        {{ text }}
    </span>
{% endmacro %}
```

### Defaults Block

```yaml
badge:
  text: Badge
  variant: info
  pill: false
  typography:
    size: xs
    color: '#ffffff'
  spacing:
    marginBlock: xs
    marginInline: xs
```

### Schema Block

```yaml
badge:
  groups:
  - id: content
    label: Content
    fields:
    - path: text
      type: text
      label: Badge Text
    - path: variant
      type: select
      label: Variant
      options:
      - value: success
        label: Success (Green)
      - value: danger
        label: Danger (Red)
      - value: warning
        label: Warning (Amber)
      - value: info
        label: Info (Blue)
    - path: pill
      type: checkbox
      label: Pill Shape
  - id: typography
    label: Typography
    fields:
    - path: typography.size
      type: select
      label: Font Size
      tokens: typographySizes
    - path: typography.color
      type: color
      label: Text Color
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Badge Component --- */
.badge {
    position: relative;
    box-sizing: border-box;
    text-align: center;
    letter-spacing: 0.025em;
}
```

---

## 4. Rating - New Component

### Purpose & Usage

Displays trust/quality levels using star or heart icons. Used inside review cards, product headers, testimonial sections, and feature comparison tables.

### YAML Usage

```yaml
# 4-star rating with count
- name: rating
  properties:
    value: 4
    iconType: star
    showCount: true
    color: '#f59e0b'
    typography:
      size: lg
      color: '#6b7280'

# Heart rating without count
- name: rating
  properties:
    value: 3
    iconType: heart
    showCount: false
    color: '#ef4444'
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `value` | number | `4` | 0-5 | Number of filled icons |
| `iconType` | select | `star` | star, heart | Icon shape |
| `showCount` | checkbox | `false` | true, false | Show "N/5" text |
| `color` | color | `#f59e0b` | Any hex color | Filled icon color |
| `typography.size` | select (token) | `md` | typographySizes tokens | Icon and count text size |
| `typography.color` | color | `#6b7280` | Any hex color | Count text color |
| `spacing.marginBlock` | select (token) | `xs` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `none` | spacingScale tokens | Horizontal margin |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_rating.html`

```jinja2
{% macro render_rating(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set value = properties.value | default(0) | int %}
    {% set max_value = 5 %}
    {% set icon_type = properties.iconType | default('star') %}
    {% set show_count = properties.showCount | default(false) %}
    {% set icon_color = properties.color | default('#f59e0b') %}
    {% set base_styles = build_styles(component, tokens) %}

    {# Icon sizing from typography.size token #}
    {% set typo = properties.typography | default({}) %}
    {% set size_token = typo.size | default('md') %}
    {% set icon_size = tokens.typography_sizes[size_token] if tokens and tokens.typography_sizes and size_token in tokens.typography_sizes else '1.8rem' %}
    {% set count_color = typo.color | default('#6b7280') %}

    <div class="rating chrome-target"
         data-component-id="{{ component_id }}"
         style="{{ base_styles }} display: inline-flex; align-items: center; gap: 0.15em;">
        {% for i in range(max_value) %}
            {% set filled = (i < value) %}
            <svg class="rating-icon" aria-hidden="true"
                 style="width: {{ icon_size }}; height: {{ icon_size }}; flex-shrink: 0;
                        color: {{ icon_color if filled else '#d1d5db' }};
                        fill: {{ 'currentColor' if filled else 'none' }};
                        stroke: currentColor; stroke-width: 2;
                        stroke-linecap: round; stroke-linejoin: round;">
                <use href="#icon-{{ icon_type }}"></use>
            </svg>
        {% endfor %}
        {% if show_count %}
            <span class="rating-count"
                  style="margin-left: 0.35em; font-size: {{ icon_size }}; color: {{ count_color }}; line-height: 1;">
                {{ value }}/{{ max_value }}
            </span>
        {% endif %}
    </div>
{% endmacro %}
```

### Defaults Block

```yaml
rating:
  value: 4
  iconType: star
  showCount: false
  color: '#f59e0b'
  typography:
    size: md
    color: '#6b7280'
  spacing:
    marginBlock: xs
    marginInline: none
```

### Schema Block

```yaml
rating:
  groups:
  - id: content
    label: Rating
    fields:
    - path: value
      type: number
      label: Value
      min: 0
      max: 5
    - path: iconType
      type: select
      label: Icon Type
      options:
      - value: star
        label: Stars
      - value: heart
        label: Hearts
    - path: showCount
      type: checkbox
      label: Show Count Text
    - path: color
      type: color
      label: Icon Color
  - id: typography
    label: Count Typography
    fields:
    - path: typography.size
      type: select
      label: Size
      tokens: typographySizes
    - path: typography.color
      type: color
      label: Count Text Color
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Rating Component --- */
.rating {
    position: relative;
    box-sizing: border-box;
}

.rating-icon {
    transition: transform 0.15s ease;
}

.rating-count {
    font-variant-numeric: tabular-nums;
}
```

---

## 5. Progress Bar - New Component

### Purpose & Usage

Visualizes completion percentages, stock levels, loading states, or onboarding progress. Used in "Limited Stock" product cards, multi-step forms, funding goals, and skill displays.

### YAML Usage

```yaml
# Basic progress bar
- name: progress-bar
  properties:
    percent: 75
    thickness: medium
    color: '#3b82f6'

# Limited stock indicator with gradient
- name: progress-bar
  properties:
    percent: 15
    thickness: small
    colorGradient: true
    appearance:
      radius: pill

# Fundraising goal
- name: progress-bar
  properties:
    percent: 82
    thickness: large
    color: '#059669'
    trackColor: '#d1fae5'
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `percent` | number | `50` | 0-100 | Fill percentage |
| `thickness` | select | `medium` | small, medium, large | Bar height |
| `color` | color | `#3b82f6` | Any hex color | Fill color |
| `trackColor` | color | `#e5e7eb` | Any hex color | Background track color |
| `colorGradient` | checkbox | `false` | true, false | Use red-amber-green gradient |
| `appearance.radius` | select (token) | `pill` | borderRadiusScale tokens | Corner rounding |
| `spacing.marginBlock` | select (token) | `sm` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `none` | spacingScale tokens | Horizontal margin |

**Thickness Map:**

| Value | Height |
|-------|--------|
| small | 0.5rem (8px) |
| medium | 1rem (16px) |
| large | 1.5rem (24px) |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_progress_bar.html`

```jinja2
{% macro render_progress_bar(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set percent = properties.percent | default(0) | int %}
    {% set thickness = properties.thickness | default('medium') %}
    {% set color = properties.color | default('#3b82f6') %}
    {% set track_color = properties.trackColor | default('#e5e7eb') %}
    {% set color_gradient = properties.colorGradient | default(false) %}
    {% set base_styles = build_styles(component, tokens) %}

    {# Thickness mapping #}
    {% set thickness_map = {'small': '0.5rem', 'medium': '1rem', 'large': '1.5rem'} %}
    {% set height = thickness_map[thickness] | default('1rem') %}

    {# Radius from appearance #}
    {% set appearance = properties.appearance | default({}) %}
    {% set radius = appearance.radius | default('pill') %}
    {% set radius_value = tokens.border_radius[radius] if tokens and tokens.border_radius and radius in tokens.border_radius else '9999px' %}

    {# Bar fill style #}
    {% if color_gradient %}
        {% set fill_bg = 'linear-gradient(to right, #ef4444, #f59e0b, #22c55e)' %}
    {% else %}
        {% set fill_bg = color %}
    {% endif %}

    {# Clamp percent 0-100 #}
    {% set clamped = [0, [percent, 100] | min] | max %}

    <div class="progress-bar chrome-target"
         data-component-id="{{ component_id }}"
         role="progressbar"
         aria-valuenow="{{ clamped }}"
         aria-valuemin="0"
         aria-valuemax="100"
         aria-label="Progress: {{ clamped }}%"
         style="{{ base_styles }} width: 100%; height: {{ height }}; background-color: {{ track_color }}; border-radius: {{ radius_value }}; overflow: hidden;">
        <div class="progress-bar__fill"
             style="width: {{ clamped }}%; height: 100%; background: {{ fill_bg }}; border-radius: {{ radius_value }}; transition: width 0.6s ease;">
        </div>
    </div>
{% endmacro %}
```

### Defaults Block

```yaml
progress-bar:
  percent: 50
  thickness: medium
  color: '#3b82f6'
  trackColor: '#e5e7eb'
  colorGradient: false
  appearance:
    radius: pill
  spacing:
    marginBlock: sm
    marginInline: none
```

### Schema Block

```yaml
progress-bar:
  groups:
  - id: content
    label: Progress
    fields:
    - path: percent
      type: number
      label: Percent
      min: 0
      max: 100
    - path: thickness
      type: select
      label: Thickness
      options:
      - value: small
        label: Small
      - value: medium
        label: Medium
      - value: large
        label: Large
    - path: color
      type: color
      label: Bar Color
    - path: trackColor
      type: color
      label: Track Color
    - path: colorGradient
      type: checkbox
      label: Color Gradient
  - id: appearance
    label: Appearance
    fields:
    - path: appearance.radius
      type: select
      label: Border Radius
      tokens: borderRadiusScale
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Progress Bar Component --- */
.progress-bar {
    position: relative;
    box-sizing: border-box;
}

.progress-bar__fill {
    transition: width 0.6s ease;
}
```

---

## 6. Counter-Up - New Component

### Purpose & Usage

Numbers that animate from zero to a target value when they scroll into the viewport. Used in "Total Users", "Money Saved", "Projects Completed" marketing statistics sections.

### YAML Usage

```yaml
# Revenue counter
- name: counter-up
  properties:
    endValue: 2500
    duration: 2000
    prefix: '$'
    suffix: 'k'
    typography:
      size: xxxl
      weight: bold
      color: '#111827'

# User count
- name: counter-up
  properties:
    endValue: 50000
    duration: 3000
    suffix: '+'
    typography:
      size: xxl
      weight: extrabold
      color: '#3b82f6'
      align: center
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `endValue` | number | `100` | 0-1000000 | Target number to count to |
| `duration` | number | `2000` | 500-10000 | Animation duration in ms |
| `prefix` | text | `` | Any string | Text before number (e.g., "$") |
| `suffix` | text | `` | Any string | Text after number (e.g., "k", "+") |
| `typography.size` | select (token) | `xxxl` | typographySizes tokens | Font size |
| `typography.weight` | select (token) | `bold` | fontWeights tokens | Font weight |
| `typography.color` | color | `#111827` | Any hex color | Text color |
| `typography.align` | select (token) | `center` | alignmentHorizontal tokens | Text alignment |
| `spacing.marginBlock` | select (token) | `sm` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `none` | spacingScale tokens | Horizontal margin |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_counter_up.html`

```jinja2
{% macro render_counter_up(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set end_value = properties.endValue | default(0) %}
    {% set duration = properties.duration | default(2000) %}
    {% set prefix = properties.prefix | default('') %}
    {% set suffix = properties.suffix | default('') %}
    {% set base_styles = build_styles(component, tokens) %}

    <div class="counter-up chrome-target"
         data-component-id="{{ component_id }}"
         data-end-value="{{ end_value }}"
         data-duration="{{ duration }}"
         data-prefix="{{ prefix }}"
         data-suffix="{{ suffix }}"
         style="{{ base_styles }} display: inline-block;">
        <span class="counter-up__value">{{ prefix }}0{{ suffix }}</span>
    </div>
{% endmacro %}
```

### Defaults Block

```yaml
counter-up:
  endValue: 100
  duration: 2000
  prefix: ''
  suffix: ''
  typography:
    size: xxxl
    weight: bold
    color: '#111827'
    align: center
  spacing:
    marginBlock: sm
    marginInline: none
```

### Schema Block

```yaml
counter-up:
  groups:
  - id: content
    label: Counter
    fields:
    - path: endValue
      type: number
      label: End Value
      min: 0
      max: 1000000
    - path: duration
      type: number
      label: Duration (ms)
      min: 500
      max: 10000
    - path: prefix
      type: text
      label: Prefix
    - path: suffix
      type: text
      label: Suffix
  - id: typography
    label: Typography
    fields:
    - path: typography.size
      type: select
      label: Font Size
      tokens: typographySizes
    - path: typography.weight
      type: select
      label: Weight
      tokens: fontWeights
    - path: typography.color
      type: color
      label: Text Color
    - path: typography.align
      type: select
      label: Alignment
      tokens: alignmentHorizontal
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Counter-Up Component --- */
.counter-up {
    position: relative;
    box-sizing: border-box;
}

.counter-up__value {
    font-variant-numeric: tabular-nums;
}
```

### Runtime JavaScript

Add to `swift-sites-runtime.js`:

```javascript
/**
 * Initialize all counter-up components
 */
initCounterUps: function() {
    document.querySelectorAll('.counter-up').forEach(function(counter) {
        this._initCounterUp(counter);
    }.bind(this));
},

_initCounterUp: function(element) {
    if (!element || element.dataset.ssInitialized === 'true') return;
    element.dataset.ssInitialized = 'true';

    var endValue = parseInt(element.dataset.endValue, 10) || 0;
    var duration = parseInt(element.dataset.duration, 10) || 2000;
    var prefix = element.dataset.prefix || '';
    var suffix = element.dataset.suffix || '';
    var valueEl = element.querySelector('.counter-up__value');

    if (!valueEl) return;

    var animated = false;

    function animateCount() {
        if (animated) return;
        animated = true;

        var startTime = performance.now();

        function step(currentTime) {
            var elapsed = currentTime - startTime;
            var progress = Math.min(elapsed / duration, 1);

            // Ease-out cubic
            var easedProgress = 1 - Math.pow(1 - progress, 3);
            var currentValue = Math.round(easedProgress * endValue);

            valueEl.textContent = prefix + currentValue.toLocaleString() + suffix;

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }

        requestAnimationFrame(step);
    }

    // Use IntersectionObserver to trigger on viewport entry
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    animateCount();
                    observer.unobserve(element);
                }
            });
        }, { threshold: 0.3 });

        observer.observe(element);
    } else {
        // Fallback: animate immediately
        animateCount();
    }
},
```

---

## 7. Countdown - New Component

### Purpose & Usage

Urgency timer for flash sales, product drops, event countdowns, and limited-time offers. Displays days, hours, minutes, and seconds with live ticking.

### YAML Usage

```yaml
# Flash sale countdown
- name: countdown
  properties:
    targetDate: '2026-12-31T23:59:59'
    format: 'DD:HH:MM:SS'
    expiredText: 'Sale has ended!'
    typography:
      size: xxl
      weight: bold
      color: '#dc2626'

# Event timer (hours only)
- name: countdown
  properties:
    targetDate: '2026-03-15T09:00:00'
    format: 'HH:MM:SS'
    expiredText: 'Event is live!'
    typography:
      size: xl
      weight: semibold
      color: '#111827'
      align: center
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `targetDate` | text | `2026-12-31T23:59:59` | ISO 8601 datetime | Target date/time |
| `format` | select | `DD:HH:MM:SS` | DD:HH:MM:SS, HH:MM:SS, MM:SS | Display format |
| `expiredText` | text | `Expired` | Any string | Text shown when timer reaches zero |
| `typography.size` | select (token) | `xxl` | typographySizes tokens | Font size |
| `typography.weight` | select (token) | `bold` | fontWeights tokens | Font weight |
| `typography.color` | color | `#111827` | Any hex color | Text color |
| `typography.align` | select (token) | `center` | alignmentHorizontal tokens | Alignment |
| `spacing.marginBlock` | select (token) | `md` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `none` | spacingScale tokens | Horizontal margin |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_countdown.html`

```jinja2
{% macro render_countdown(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set target_date = properties.targetDate | default('') %}
    {% set format = properties.format | default('DD:HH:MM:SS') %}
    {% set expired_text = properties.expiredText | default('Expired') %}
    {% set base_styles = build_styles(component, tokens) %}

    <div class="countdown chrome-target"
         data-component-id="{{ component_id }}"
         data-target-date="{{ target_date }}"
         data-format="{{ format }}"
         data-expired-text="{{ expired_text }}"
         style="{{ base_styles }} display: inline-flex; gap: 0.5em; align-items: baseline;">
        {% if 'DD' in format %}
            <span class="countdown__segment">
                <span class="countdown__value" data-unit="days">00</span>
                <span class="countdown__label">Days</span>
            </span>
            <span class="countdown__separator">:</span>
        {% endif %}
        {% if 'HH' in format %}
            <span class="countdown__segment">
                <span class="countdown__value" data-unit="hours">00</span>
                <span class="countdown__label">Hours</span>
            </span>
            <span class="countdown__separator">:</span>
        {% endif %}
        {% if 'MM' in format %}
            <span class="countdown__segment">
                <span class="countdown__value" data-unit="minutes">00</span>
                <span class="countdown__label">Min</span>
            </span>
            <span class="countdown__separator">:</span>
        {% endif %}
        <span class="countdown__segment">
            <span class="countdown__value" data-unit="seconds">00</span>
            <span class="countdown__label">Sec</span>
        </span>
    </div>
{% endmacro %}
```

### Defaults Block

```yaml
countdown:
  targetDate: '2026-12-31T23:59:59'
  format: 'DD:HH:MM:SS'
  expiredText: Expired
  typography:
    size: xxl
    weight: bold
    color: '#111827'
    align: center
  spacing:
    marginBlock: md
    marginInline: none
```

### Schema Block

```yaml
countdown:
  groups:
  - id: content
    label: Countdown
    fields:
    - path: targetDate
      type: text
      label: Target Date (ISO 8601)
    - path: format
      type: select
      label: Format
      options:
      - value: 'DD:HH:MM:SS'
        label: Days + Hours + Min + Sec
      - value: 'HH:MM:SS'
        label: Hours + Min + Sec
      - value: 'MM:SS'
        label: Min + Sec
    - path: expiredText
      type: text
      label: Expired Text
  - id: typography
    label: Typography
    fields:
    - path: typography.size
      type: select
      label: Font Size
      tokens: typographySizes
    - path: typography.weight
      type: select
      label: Weight
      tokens: fontWeights
    - path: typography.color
      type: color
      label: Text Color
    - path: typography.align
      type: select
      label: Alignment
      tokens: alignmentHorizontal
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Countdown Component --- */
.countdown {
    position: relative;
    box-sizing: border-box;
}

.countdown__segment {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
}

.countdown__value {
    font-variant-numeric: tabular-nums;
    line-height: 1;
}

.countdown__label {
    font-size: 0.4em;
    opacity: 0.7;
    text-align: center;
    margin-top: 0.2em;
}

.countdown__separator {
    align-self: flex-start;
    line-height: 1;
    opacity: 0.5;
}

.countdown__expired {
    opacity: 0.6;
    font-style: italic;
}
```

### Runtime JavaScript

Add to `swift-sites-runtime.js`:

```javascript
/**
 * Initialize all countdown components
 */
initCountdowns: function() {
    document.querySelectorAll('.countdown').forEach(function(countdown) {
        this._initCountdown(countdown);
    }.bind(this));
},

_initCountdown: function(element) {
    if (!element || element.dataset.ssInitialized === 'true') return;
    element.dataset.ssInitialized = 'true';

    var targetDate = new Date(element.dataset.targetDate);
    var expiredText = element.dataset.expiredText || 'Expired';
    var format = element.dataset.format || 'DD:HH:MM:SS';

    if (isNaN(targetDate.getTime())) return;

    function update() {
        var now = new Date();
        var diff = targetDate - now;

        if (diff <= 0) {
            element.innerHTML = '<span class="countdown__expired">' + expiredText + '</span>';
            clearInterval(element._countdownInterval);
            return;
        }

        var days = Math.floor(diff / (1000 * 60 * 60 * 24));
        diff -= days * (1000 * 60 * 60 * 24);
        var hours = Math.floor(diff / (1000 * 60 * 60));
        diff -= hours * (1000 * 60 * 60);
        var minutes = Math.floor(diff / (1000 * 60));
        diff -= minutes * (1000 * 60);
        var seconds = Math.floor(diff / 1000);

        function pad(n) { return String(n).padStart(2, '0'); }

        var daysEl = element.querySelector('[data-unit="days"]');
        var hoursEl = element.querySelector('[data-unit="hours"]');
        var minutesEl = element.querySelector('[data-unit="minutes"]');
        var secondsEl = element.querySelector('[data-unit="seconds"]');

        if (daysEl) daysEl.textContent = pad(days);
        if (hoursEl) hoursEl.textContent = format.indexOf('DD') !== -1 ? pad(hours) : pad(days * 24 + hours);
        if (minutesEl) minutesEl.textContent = pad(minutes);
        if (secondsEl) secondsEl.textContent = pad(seconds);
    }

    update();
    element._countdownInterval = setInterval(update, 1000);
},
```

---

## 8. Lottie Animation - New Component

### Purpose & Usage

High-quality, lightweight vector animations rendered from JSON files. More professional than GIF with smaller file sizes. Used for success states (checkmark animation), hero section accents, loading states, and interactive micro-animations.

### YAML Usage

```yaml
# Auto-playing looped animation
- name: lottie-animation
  properties:
    src: 'https://assets1.lottiefiles.com/packages/lf20_UJNc2t.json'
    loop: true
    autoplay: true
    trigger: none
    width: 300
    height: 300

# Scroll-triggered animation
- name: lottie-animation
  properties:
    src: 'https://assets.lottiefiles.com/packages/lf20_xxx.json'
    loop: false
    autoplay: true
    trigger: scroll
    width: 200
    height: 200

# Hover-triggered animation
- name: lottie-animation
  properties:
    src: 'https://assets.lottiefiles.com/packages/lf20_yyy.json'
    loop: false
    autoplay: false
    trigger: hover
    width: 80
    height: 80
```

### Properties Table

| Property | Type | Default | Valid Values | Description |
|----------|------|---------|--------------|-------------|
| `src` | text | `` | URL to .json file | Lottie animation JSON URL |
| `loop` | checkbox | `true` | true, false | Loop animation |
| `autoplay` | checkbox | `true` | true, false | Auto-start animation |
| `trigger` | select | `none` | none, scroll, hover | What triggers playback |
| `width` | number | `300` | 50-1000 | Width in px |
| `height` | number | `300` | 50-1000 | Height in px |
| `spacing.marginBlock` | select (token) | `sm` | spacingScale tokens | Vertical margin |
| `spacing.marginInline` | select (token) | `none` | spacingScale tokens | Horizontal margin |

### Jinja2 Macro

**File:** `ssr_python/templates/components/marketing/_lottie_animation.html`

```jinja2
{% macro render_lottie_animation(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set src = properties.src | default('') %}
    {% set loop_anim = properties.loop | default(true) %}
    {% set autoplay = properties.autoplay | default(true) %}
    {% set trigger = properties.trigger | default('none') %}
    {% set width = properties.width | default(300) %}
    {% set height = properties.height | default(300) %}
    {% set base_styles = build_styles(component, tokens) %}

    <div class="lottie-animation chrome-target"
         data-component-id="{{ component_id }}"
         data-src="{{ src }}"
         data-loop="{{ 'true' if loop_anim else 'false' }}"
         data-autoplay="{{ 'true' if autoplay else 'false' }}"
         data-trigger="{{ trigger }}"
         style="{{ base_styles }} display: inline-block; width: {{ width }}px; height: {{ height }}px;">
        {% if not src %}
            <div class="lottie-placeholder"
                 style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; border: 2px dashed #d1d5db; border-radius: 0.5rem; color: #9ca3af; font-size: 0.875rem; text-align: center; padding: 1rem;">
                Lottie Animation<br>Set a JSON URL
            </div>
        {% endif %}
    </div>
{% endmacro %}
```

### Defaults Block

```yaml
lottie-animation:
  src: ''
  loop: true
  autoplay: true
  trigger: none
  width: 300
  height: 300
  spacing:
    marginBlock: sm
    marginInline: none
```

### Schema Block

```yaml
lottie-animation:
  groups:
  - id: content
    label: Animation
    fields:
    - path: src
      type: text
      label: Lottie JSON URL
    - path: loop
      type: checkbox
      label: Loop
    - path: autoplay
      type: checkbox
      label: Autoplay
    - path: trigger
      type: select
      label: Trigger
      options:
      - value: none
        label: None (auto)
      - value: scroll
        label: On Scroll Into View
      - value: hover
        label: On Hover
    - path: width
      type: number
      label: Width (px)
      min: 50
      max: 1000
    - path: height
      type: number
      label: Height (px)
      min: 50
      max: 1000
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
```

### CSS Rules

```css
/* --- Lottie Animation Component --- */
.lottie-animation {
    position: relative;
    box-sizing: border-box;
    overflow: hidden;
}

.lottie-animation svg {
    width: 100% !important;
    height: 100% !important;
}

.lottie-placeholder {
    box-sizing: border-box;
}
```

### Runtime JavaScript

Add to `swift-sites-runtime.js`. The lottie-web library is loaded lazily from CDN only when a lottie component exists on the page.

```javascript
/**
 * Initialize all Lottie animation components.
 * Lazily loads lottie-web from CDN if not already present.
 */
initLottieAnimations: function() {
    var self = this;
    var lottieElements = document.querySelectorAll('.lottie-animation[data-src]');
    if (lottieElements.length === 0) return;

    // Filter to only elements with a non-empty src
    var pending = [];
    lottieElements.forEach(function(el) {
        if (el.dataset.src && el.dataset.src.trim() !== '') {
            pending.push(el);
        }
    });
    if (pending.length === 0) return;

    // Lazily load lottie-web from CDN if not already loaded
    if (typeof lottie === 'undefined' && !self._lottieLoading) {
        self._lottieLoading = true;
        var script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js';
        script.onload = function() {
            self._lottieLoading = false;
            pending.forEach(function(el) { self._initLottieAnimation(el); });
        };
        script.onerror = function() {
            self._lottieLoading = false;
            console.warn('[SwiftSites] Failed to load lottie-web from CDN');
        };
        document.head.appendChild(script);
    } else if (typeof lottie !== 'undefined') {
        pending.forEach(function(el) { self._initLottieAnimation(el); });
    }
    // If _lottieLoading is true, library is being fetched and will init on load
},

_initLottieAnimation: function(element) {
    if (!element || element.dataset.ssInitialized === 'true') return;
    var src = element.dataset.src;
    if (!src || src.trim() === '') return;
    element.dataset.ssInitialized = 'true';

    var shouldLoop = element.dataset.loop === 'true';
    var shouldAutoplay = element.dataset.autoplay === 'true';
    var trigger = element.dataset.trigger || 'none';

    // Clear placeholder if present
    var placeholder = element.querySelector('.lottie-placeholder');
    if (placeholder) placeholder.remove();

    var anim = lottie.loadAnimation({
        container: element,
        renderer: 'svg',
        loop: shouldLoop,
        autoplay: trigger === 'none' && shouldAutoplay,
        path: src
    });

    // Store reference for potential cleanup
    element._lottieAnim = anim;

    if (trigger === 'scroll') {
        anim.pause();
        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        anim.play();
                        observer.unobserve(element);
                    }
                });
            }, { threshold: 0.3 });
            observer.observe(element);
        } else {
            anim.play(); // Fallback
        }
    } else if (trigger === 'hover') {
        anim.pause();
        element.addEventListener('mouseenter', function() { anim.play(); });
        element.addEventListener('mouseleave', function() {
            anim.pause();
            anim.goToAndStop(0, true);
        });
    }
},
```

---

## SVG Icons

Add these `<symbol>` elements to `ssr_python/static/icon-sprite.svg` before the closing `</svg>` tag.

These icons follow the Lucide icon style (24x24 viewBox, stroke-based, 2px stroke width) consistent with existing icons in the sprite.

```xml
<!-- Marketing component icons -->
<symbol id="icon-star" viewBox="0 0 24 24">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-star-filled" viewBox="0 0 24 24">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-heart" viewBox="0 0 24 24">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-heart-filled" viewBox="0 0 24 24">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-checkmark" viewBox="0 0 24 24">
    <path d="M20 6 9 17l-5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-fire" viewBox="0 0 24 24">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-user" viewBox="0 0 24 24">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="12" cy="7" r="4" fill="none" stroke="currentColor" stroke-width="2"/>
</symbol>

<symbol id="icon-chevron-right" viewBox="0 0 24 24">
    <path d="m9 18 6-6-6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-chevron-left" viewBox="0 0 24 24">
    <path d="m15 18-6-6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-arrow-right" viewBox="0 0 24 24">
    <path d="M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="m12 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-arrow-left" viewBox="0 0 24 24">
    <path d="m12 19-7-7 7-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M19 12H5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-phone" viewBox="0 0 24 24">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-mail" viewBox="0 0 24 24">
    <rect width="20" height="16" x="2" y="4" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-map-pin" viewBox="0 0 24 24">
    <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="12" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
</symbol>

<symbol id="icon-clock" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
    <polyline points="12 6 12 12 16 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-tag" viewBox="0 0 24 24">
    <path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>
</symbol>

<symbol id="icon-crosshair" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
    <line x1="22" x2="18" y1="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="6" x2="2" y1="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="12" x2="12" y1="2" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="12" x2="12" y1="18" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</symbol>

<symbol id="icon-play-circle" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
    <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" stroke="none"/>
</symbol>

<symbol id="icon-bar-chart" viewBox="0 0 24 24">
    <line x1="12" x2="12" y1="20" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="18" x2="18" y1="20" y2="4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="6" x2="6" y1="20" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</symbol>

<symbol id="icon-hash" viewBox="0 0 24 24">
    <line x1="4" x2="20" y1="9" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="4" x2="20" y1="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="10" x2="8" y1="3" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <line x1="16" x2="14" y1="3" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</symbol>

<symbol id="icon-minus" viewBox="0 0 24 24">
    <path d="M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</symbol>

<symbol id="icon-eye" viewBox="0 0 24 24">
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
</symbol>

<symbol id="icon-globe" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="M2 12h20" fill="none" stroke="currentColor" stroke-width="2"/>
</symbol>

<symbol id="icon-download" viewBox="0 0 24 24">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline points="7 10 12 15 17 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="12" x2="12" y1="15" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</symbol>

<symbol id="icon-upload" viewBox="0 0 24 24">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline points="17 8 12 3 7 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="12" x2="12" y1="3" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</symbol>
```

---

## Integration Checklist

### 1. Assembly Manifest (`_assembly.html`)

Add before line 34 (`{#- 3. Dispatcher LAST -#}`):

```jinja2
{#- 2b. Marketing component macros -#}
{% include "components/marketing/_icon.html" %}
{% include "components/marketing/_badge.html" %}
{% include "components/marketing/_rating.html" %}
{% include "components/marketing/_progress_bar.html" %}
{% include "components/marketing/_counter_up.html" %}
{% include "components/marketing/_countdown.html" %}
{% include "components/marketing/_lottie_animation.html" %}
```

### 2. Dispatcher (`_dispatcher.html`)

Add before `{% else %}` block (before line 58):

```jinja2
    {% elif name == 'icon' %}
        {{ render_icon(component, tokens, path, component_id) }}
    {% elif name == 'badge' %}
        {{ render_badge(component, tokens, path, component_id) }}
    {% elif name == 'rating' %}
        {{ render_rating(component, tokens, path, component_id) }}
    {% elif name == 'progress-bar' %}
        {{ render_progress_bar(component, tokens, path, component_id) }}
    {% elif name == 'counter-up' %}
        {{ render_counter_up(component, tokens, path, component_id) }}
    {% elif name == 'countdown' %}
        {{ render_countdown(component, tokens, path, component_id) }}
    {% elif name == 'lottie-animation' %}
        {{ render_lottie_animation(component, tokens, path, component_id) }}
```

### 3. Component Tree Icons (`componentTree.js`)

Add to `iconMap` object:

```javascript
'icon': 'icon-star',
'badge': 'icon-tag',
'rating': 'icon-star-filled',
'progress-bar': 'icon-bar-chart',
'counter-up': 'icon-hash',
'countdown': 'icon-clock',
'lottie-animation': 'icon-play-circle',
```

### 4. Properties Panel Icons (`propertiesPanel.js`)

Add to `componentIcons` object:

```javascript
icon: 'icon-star',
badge: 'icon-tag',
rating: 'icon-star-filled',
'progress-bar': 'icon-bar-chart',
'counter-up': 'icon-hash',
countdown: 'icon-clock',
'lottie-animation': 'icon-play-circle',
```

### 5. Runtime Init (`swift-sites-runtime.js`)

Update `init()` method:

```javascript
init: function() {
    this.initCarousels();
    this.initTabs();
    this.initAccordions();
    this.initTitlebars();
    this.initCounterUps();       // NEW
    this.initCountdowns();        // NEW
    this.initLottieAnimations();  // NEW
},
```

Update `reset()` method to clean up countdown intervals:

```javascript
reset: function() {
    // Clean up countdown intervals before re-init
    document.querySelectorAll('.countdown').forEach(function(el) {
        if (el._countdownInterval) {
            clearInterval(el._countdownInterval);
            el._countdownInterval = null;
        }
    });

    // Clean up lottie animations
    document.querySelectorAll('.lottie-animation').forEach(function(el) {
        if (el._lottieAnim) {
            el._lottieAnim.destroy();
            el._lottieAnim = null;
        }
    });

    document.querySelectorAll('[data-ss-initialized]').forEach(function(el) {
        delete el.dataset.ssInitialized;
    });
    this._titlebarScrollHandlerAttached = false;
    this.cleanupTitlebarClones();
}
```

---

## Testing Plan

### Test YAML

Paste this YAML in the editor to test all 8 components simultaneously:

```yaml
- name: page
  properties:
    appearance:
      background:
        color: '#ffffff'
  components:
    - name: heading
      properties:
        text: Marketing Components Test Page
        typography:
          size: xxl
          weight: bold

    # 1. Enhanced BR / Divider
    - name: br
      properties:
        type: solid
        thickness: 2
        color: '#e5e7eb'
        size: md

    - name: br
      properties:
        type: wave
        thickness: 3
        color: '#3b82f6'
        size: sm

    - name: br
      properties:
        type: slant
        thickness: 2
        color: '#111827'
        size: sm

    # 2. Icon
    - name: layout-row
      properties:
        layout:
          gap: md
          wrap: wrap
      components:
        - name: icon
          properties:
            name: fire
            size: xl
            color: '#ef4444'
            layout:
              widthMode: fit
        - name: icon
          properties:
            name: checkmark
            size: lg
            color: '#059669'
            layout:
              widthMode: fit
        - name: icon
          properties:
            name: heart
            size: lg
            color: '#ec4899'
            layout:
              widthMode: fit
        - name: icon
          properties:
            name: star
            size: lg
            color: '#f59e0b'
            layout:
              widthMode: fit

    - name: br
      properties:
        type: dashed
        thickness: 1
        color: '#d1d5db'

    # 3. Badge variants
    - name: layout-row
      properties:
        layout:
          gap: sm
          wrap: wrap
      components:
        - name: badge
          properties:
            text: New
            variant: info
            pill: true
            layout:
              widthMode: fit
        - name: badge
          properties:
            text: Sale
            variant: danger
            pill: true
            layout:
              widthMode: fit
        - name: badge
          properties:
            text: In Stock
            variant: success
            pill: false
            layout:
              widthMode: fit
        - name: badge
          properties:
            text: Limited
            variant: warning
            pill: true
            layout:
              widthMode: fit

    - name: br
      properties:
        type: solid
        thickness: 1

    # 4. Rating
    - name: rating
      properties:
        value: 4
        iconType: star
        showCount: true
        color: '#f59e0b'
        typography:
          size: lg
          color: '#6b7280'

    - name: rating
      properties:
        value: 3
        iconType: heart
        showCount: false
        color: '#ef4444'

    - name: br

    # 5. Progress Bar
    - name: progress-bar
      properties:
        percent: 75
        thickness: medium
        color: '#3b82f6'

    - name: progress-bar
      properties:
        percent: 30
        thickness: small
        colorGradient: true

    - name: br

    # 6. Counter-Up
    - name: layout-row
      properties:
        layout:
          gap: lg
          wrap: wrap
      components:
        - name: layout-column
          properties:
            layout:
              widthMode: '33'
          components:
            - name: counter-up
              properties:
                endValue: 2500
                prefix: '$'
                suffix: 'k'
                typography:
                  size: xxxl
                  weight: bold
                  color: '#111827'
                  align: center
            - name: paragraph
              properties:
                text: Revenue
                typography:
                  align: center
                  size: sm
                  color: '#6b7280'
        - name: layout-column
          properties:
            layout:
              widthMode: '33'
          components:
            - name: counter-up
              properties:
                endValue: 50000
                suffix: '+'
                typography:
                  size: xxxl
                  weight: bold
                  color: '#3b82f6'
                  align: center
            - name: paragraph
              properties:
                text: Users
                typography:
                  align: center
                  size: sm
                  color: '#6b7280'
        - name: layout-column
          properties:
            layout:
              widthMode: '33'
          components:
            - name: counter-up
              properties:
                endValue: 99
                suffix: '%'
                duration: 1500
                typography:
                  size: xxxl
                  weight: bold
                  color: '#059669'
                  align: center
            - name: paragraph
              properties:
                text: Uptime
                typography:
                  align: center
                  size: sm
                  color: '#6b7280'

    - name: br

    # 7. Countdown
    - name: countdown
      properties:
        targetDate: '2026-12-31T23:59:59'
        format: 'DD:HH:MM:SS'
        expiredText: 'Happy New Year!'
        typography:
          size: xxl
          weight: bold
          color: '#dc2626'
          align: center

    - name: br

    # 8. Lottie Animation (placeholder - no src)
    - name: lottie-animation
      properties:
        src: ''
        width: 200
        height: 200
```

### Manual Verification Steps

#### For ALL components:
1. Paste test YAML in editor - preview renders without console errors
2. Click each component in preview - selection highlights correctly
3. Properties panel shows appropriate fields for each component
4. Change property values in panel - preview re-renders with updated values
5. Component tree shows correct icon for each component type

#### BR (Divider) specific:
- [ ] Solid, dashed, dotted lines render correctly
- [ ] Wave SVG renders with configurable color and thickness
- [ ] Slant SVG renders with configurable color and thickness
- [ ] Backward compatibility: YAML with only `size: lg` still renders
- [ ] Thickness slider changes line width
- [ ] Color picker changes line/shape color

#### Icon specific:
- [ ] All icon options render from SVG sprite
- [ ] Size scales match text component sizes (xxs through xxxl)
- [ ] Color changes icon stroke color
- [ ] Icons work inside layout-row with widthMode: fit

#### Badge specific:
- [ ] All 4 variants render with correct background colors
- [ ] Pill toggle switches between rounded and sharp corners
- [ ] Typography size changes badge text size
- [ ] Typography color overrides default white text

#### Rating specific:
- [ ] Stars render filled/unfilled correctly based on value
- [ ] Hearts render filled/unfilled correctly when iconType=heart
- [ ] showCount toggle shows/hides "N/5" text
- [ ] Icon color changes filled icon color
- [ ] Typography size scales both icons and count text

#### Progress Bar specific:
- [ ] Percent value maps to fill width (0-100%)
- [ ] Thickness options change bar height
- [ ] Color changes fill color
- [ ] Track color changes background
- [ ] Color gradient checkbox enables red-amber-green gradient
- [ ] ARIA attributes present (role, aria-valuenow, etc.)

#### Counter-Up specific:
- [ ] Numbers animate from 0 to endValue when scrolled into view
- [ ] Animation uses ease-out cubic easing
- [ ] Prefix and suffix display correctly ($, k, +, %)
- [ ] Duration changes animation speed
- [ ] Numbers use tabular-nums for stable width
- [ ] Animation only triggers once per page load

#### Countdown specific:
- [ ] Timer ticks every second with correct values
- [ ] Format DD:HH:MM:SS shows all segments
- [ ] Format HH:MM:SS hides days, rolls hours
- [ ] Format MM:SS shows only minutes and seconds
- [ ] expiredText displays when timer reaches zero
- [ ] Labels (Days, Hours, Min, Sec) show below values
- [ ] Timer cleans up on content re-render (no stale intervals)

#### Lottie Animation specific:
- [ ] Placeholder shows when src is empty
- [ ] lottie-web loads from CDN on first use (check Network tab)
- [ ] Animation plays with valid JSON URL
- [ ] Loop toggle controls animation repeat
- [ ] Trigger "scroll" starts animation when scrolled into view
- [ ] Trigger "hover" starts on mouse enter, resets on leave
- [ ] Animation cleans up on content re-render

### Automated Tests

Run existing test suite to ensure no regressions:

```bash
cd ssr_python
python -m pytest tests/ -v
```

All 30 existing tests should pass. No new automated tests are required for this phase (components are tested manually via YAML preview).

---

## Implementation Order

| Step | Component | Rationale |
|------|-----------|-----------|
| 1 | BR enhancement | Modify existing component first, ensures backward compatibility |
| 2 | SVG icons | Add all icons to sprite - needed by icon, rating, and component tree |
| 3 | Icon | Foundation component, simple, validates SVG sprite integration |
| 4 | Badge | Simple inline component, validates typography token usage |
| 5 | Rating | Uses icon SVG symbols, validates icon rendering pattern |
| 6 | Progress bar | Pure CSS, no dependencies, validates ARIA patterns |
| 7 | Counter-up | First JS runtime component, validates IntersectionObserver pattern |
| 8 | Countdown | JS runtime with setInterval, validates cleanup in reset() |
| 9 | Lottie animation | External library, most complex JS, validates CDN lazy loading |
| 10 | Integration | Assembly, dispatcher, tree icons, panel icons - wire everything up |
