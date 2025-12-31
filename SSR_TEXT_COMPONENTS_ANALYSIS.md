# SSR Text Components - Feature Completeness Analysis

## Text Components Overview

### Components in Both CSR and SSR:
1. **heading** - h1-h6 elements
2. **paragraph** - p elements
3. **eyebrow** - styled p elements (labels)
4. **caption** - small elements (captions)
5. **blockquote** - blockquote with cite
6. **link** - anchor elements with styling

---

## Feature Comparison

### 1. **HEADING Component**

#### CSR Implementation (`js/render/index.js:1090-1094`):
```javascript
if (componentType === 'heading') {
    const level = Math.min(6, Math.max(1, parseInt(componentProps.level, 10) || 2));
    const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Heading');
    return `<h${level}${attrSegment}>${textContent}</h${level}>`;
}
```
- ✅ Level support (1-6)
- ✅ Multiline text support (`escapeHtmlWithLineBreaks`)
- ✅ Width mode support (TEXT_COMPONENTS_WITH_WIDTH_MODE)
- ✅ All typography/spacing/appearance properties via `generateRemainingStyles`

#### SSR Implementation (`ssr_python/templates/macros/_components.html:218`):
```jinja2
{% if name == 'heading' %}
    <h{{ properties.level | default(2) }} class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>{{ properties.text | default('') }}</h{{ properties.level | default(2) }}>
```
- ✅ Level support (1-6)
- ❌ **MISSING**: Multiline text support (no `| replace('\n', '<br>')`)
- ❌ **MISSING**: Width mode support (not implemented in `build_styles`)
- ✅ Typography/spacing/appearance properties via `build_styles`

---

### 2. **PARAGRAPH Component**

#### CSR Implementation (`js/render/index.js:1096-1099`):
```javascript
if (componentType === 'paragraph') {
    const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Paragraph');
    return `<p${attrSegment}>${textContent}</p>`;
}
```
- ✅ Multiline text support
- ✅ Width mode support
- ✅ All typography/spacing/appearance properties

#### SSR Implementation (`ssr_python/templates/macros/_components.html:220`):
```jinja2
{% elif name == 'paragraph' %}
    <p class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>{{ properties.text | default('') | replace('\n', '<br>') | safe }}</p>
```
- ✅ Multiline text support (`| replace('\n', '<br>')`)
- ❌ **MISSING**: Width mode support
- ✅ Typography/spacing/appearance properties

---

### 3. **EYEBROW Component**

#### CSR Implementation (`js/render/index.js:1100-1103`):
```javascript
if (componentType === 'eyebrow') {
    const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Label');
    return `<p${attrSegment}>${textContent}</p>`;
}
```
- ✅ Multiline text support
- ✅ Width mode support
- ✅ All typography/spacing/appearance properties

#### SSR Implementation (`ssr_python/templates/macros/_components.html:222`):
```jinja2
{% elif name == 'eyebrow' %}
    <p class="text-eyebrow chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>{{ properties.text | default('') }}</p>
```
- ❌ **MISSING**: Multiline text support
- ❌ **MISSING**: Width mode support
- ✅ Typography/spacing/appearance properties
- ✅ CSS class `text-eyebrow` applied

---

### 4. **CAPTION Component**

#### CSR Implementation (`js/render/index.js:1104-1107`):
```javascript
if (componentType === 'caption') {
    const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Caption');
    return `<p${attrSegment}>${textContent}</p>`;
}
```
- ✅ Multiline text support
- ✅ Width mode support
- ✅ All typography/spacing/appearance properties
- Uses `<p>` element (not `<small>`)

#### SSR Implementation (`ssr_python/templates/macros/_components.html:224`):
```jinja2
{% elif name == 'caption' %}
    <small class="text-caption chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>{{ properties.text | default('') }}</small>
```
- ❌ **MISSING**: Multiline text support
- ❌ **MISSING**: Width mode support
- ✅ Typography/spacing/appearance properties
- ✅ CSS class `text-caption` applied
- ⚠️ **DIFFERENT HTML TAG**: Uses `<small>` instead of `<p>` (minor semantic difference)

---

### 5. **BLOCKQUOTE Component**

#### CSR Implementation (`js/render/index.js:1108-1112`):
```javascript
if (componentType === 'blockquote') {
    const quoteContent = escapeHtmlWithLineBreaks(componentProps.quote || componentProps.text || 'Quote');
    const citation = componentProps.cite ? '<figcaption class="blockquote-citation">&mdash; ' + escapeHtml(componentProps.cite) + '</figcaption>' : '';
    return '<figure' + attrSegment + '><blockquote>' + quoteContent + '</blockquote>' + citation + '</figure>';
}
```
- ✅ Multiline text support
- ✅ Width mode support
- ✅ Supports both `quote` and `text` properties
- ✅ Citation support with `<figcaption>` and em dash
- ✅ Wrapped in `<figure>` element
- ✅ Accent border color via `--blockquote-border` CSS variable

#### SSR Implementation (`ssr_python/templates/macros/_components.html:226-233`):
```jinja2
{% elif name == 'blockquote' %}
    {% set style_str = styles %}
    {% if properties.appearance and properties.appearance.border and properties.appearance.border.accentColor %}
        {% set style_str = style_str ~ ' --blockquote-border: ' ~ properties.appearance.border.accentColor ~ ';' %}
    {% endif %}
    <blockquote class="text-blockquote chrome-target" data-component-id="{{ component_id }}"{% if style_str %} style="{{ style_str }} position: relative;"{% else %} style="position: relative;"{% endif %}>
        <p>"{{ properties.quote | default('') }}"</p>
        {% if properties.cite %}<cite class="blockquote-citation">{{ properties.cite }}</cite>{% endif %}
    </blockquote>
```
- ❌ **MISSING**: Multiline text support
- ❌ **MISSING**: Width mode support
- ✅ Accent border color via `--blockquote-border`
- ✅ Citation support with `<cite>`
- ⚠️ **DIFFERENT HTML STRUCTURE**: 
  - Missing `<figure>` wrapper
  - Uses `<cite>` instead of `<figcaption>`
  - Uses `<p>` wrapper inside blockquote
  - Adds quotation marks in template (may be redundant with CSS)
- ❌ **MISSING**: Fallback to `text` property (only uses `quote`)

---

### 6. **LINK Component**

#### CSR Implementation (`js/render/index.js:1386-1391`):
```javascript
else if (componentType === 'link') {
    let linkStyle = componentProps.underline ? 'text-decoration: underline;' : 'text-decoration: none;';
    const arrowHTML = componentProps.showArrow ? '&nbsp;?' : '';
    const sanitizedStyles = styleString.replace(/text-align:[^;]+;/g, '');
    return '<div style="text-align: ' + (componentProps.textAlign || 'left') + ';"><a href="' + (componentProps.href || '#') + '" style="' + linkStyle + ' ' + sanitizedStyles + '">' + (componentProps.text || 'Click Me') + arrowHTML + '</a></div>';
}
```
- ✅ `underline` property support
- ✅ `showArrow` property support
- ✅ `textAlign` property support
- ✅ Wrapped in `<div>` for alignment
- ✅ Width mode support
- ⚠️ Shows `?` for arrow (likely should be an icon)

#### SSR Implementation (`ssr_python/templates/macros/_components.html:235-236`):
```jinja2
{% elif name == 'link' %}
    {% set classes = ['link', 'chrome-target'] %}{% if properties.appearance and properties.appearance.showArrow %}{% set _ = classes.append('link-arrow') %}{% endif %}
    <a href="{{ properties.href | default('#') }}" class="{{ classes | join(' ') }}" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>{{ properties.text | default('') }}</a>
```
- ❌ **MISSING**: Width mode support
- ✅ `showArrow` property support (via CSS class `link-arrow`)
- ❌ **MISSING**: `underline` property support
- ❌ **MISSING**: `textAlign` property support (removed wrapper div)
- ⚠️ **DIFFERENT**: No wrapper div (affects layout)
- ⚠️ **DIFFERENT**: Arrow via CSS class instead of inline HTML

---

## Key Missing Features in SSR

### 1. Width Mode Support ⚠️ **HIGH PRIORITY**

**What it does:**
- Controls how text components behave in flex layouts
- Three modes: `fit`, `percentage`, `stretch`
- Affects flex-grow, flex-shrink, width

**Where it's missing:**
- All text components (heading, paragraph, eyebrow, caption, blockquote)
- Image and gif components

**CSR Implementation:**
```javascript
const TEXT_COMPONENTS_WITH_WIDTH_MODE = new Set(['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote', 'image', 'gif']);

const WIDTH_MODE_RULES = {
    fit: {
        component: 'width: auto;',
        flex: ['flex-grow: 0;', 'flex-shrink: 0;']
    },
    percentage: {
        component: '', // Width set via layout.width
        flex: ['flex-grow: 0;', 'flex-shrink: 1;']
    },
    stretch: {
        component: 'width: 100%;',
        flex: ['flex-grow: 1;', 'flex-shrink: 1;']
    }
};

// Applied in generateComponentInnerHTML:
if (TEXT_COMPONENTS_WITH_WIDTH_MODE.has(componentType)) {
    const widthMode = getNestedValue(componentProps, ['layout', 'widthMode']) || 'stretch';
    const widthRule = getWidthModeRule(widthMode);
    styleString = appendInlineStyle(styleString, 'display: inline-block; box-sizing: border-box;');
    styleString = appendInlineStyle(styleString, widthRule.component);
    if (Array.isArray(widthRule.flex)) {
        widthRule.flex.forEach(declaration => {
            if (declaration) {
                styleString = appendInlineStyle(styleString, declaration);
            }
        });
    }
}
```

**Impact:** Text components won't behave correctly in flex layouts (e.g., won't shrink/grow as expected)

---

### 2. Multiline Text Support ⚠️ **MEDIUM PRIORITY**

**What it does:**
- Converts newline characters to `<br>` tags
- Allows multiline text in YAML to display properly

**CSR Implementation:**
```javascript
// js/utils/strings.js
export function escapeHtmlWithLineBreaks(str) {
    if (typeof str !== 'string') return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\n/g, '<br>');
}
```

**Where it's missing:**
- heading (no `| replace('\n', '<br>')`)
- eyebrow (no multiline support)
- caption (no multiline support)
- blockquote (no multiline support)

**Where it's present:**
- paragraph ✅ (has `| replace('\n', '<br>')`)

**Impact:** YAML multiline text (using `|` or `>`) won't display correctly with line breaks

---

### 3. Link Component Features ⚠️ **LOW PRIORITY**

**Missing:**
- `underline` property (boolean to show/hide underline)
- `textAlign` property (alignment of link wrapper)
- Wrapper div for alignment control

**Impact:** Less control over link styling and alignment

---

### 4. Blockquote Structure Differences ⚠️ **LOW PRIORITY**

**CSR uses:**
- `<figure><blockquote>...</blockquote><figcaption>cite</figcaption></figure>`

**SSR uses:**
- `<blockquote><p>...</p><cite>cite</cite></blockquote>`

**Impact:** 
- Semantic HTML difference (figure is more semantic for quotations)
- CSS may need adjustment
- Quotation marks hardcoded in SSR (may conflict with CSS ::before/::after)

---

### 5. Caption HTML Tag Difference ⚠️ **VERY LOW PRIORITY**

**CSR:** `<p>` element
**SSR:** `<small>` element

**Impact:** Minimal - `<small>` is semantically appropriate for captions

---

## Recommendations

### Priority 1: Implement Width Mode Support
Add width mode logic to `build_styles` macro:
```jinja2
{# Width Mode Support for Text Components #}
{% if component.name in ['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote', 'image', 'gif'] %}
    {% set width_mode = props.layout.widthMode | default('stretch') if props.layout else 'stretch' %}
    {% set _ = styles.append('display: inline-block; box-sizing: border-box;') %}
    {% if width_mode == 'fit' %}
        {% set _ = styles.append('width: auto; flex-grow: 0; flex-shrink: 0;') %}
    {% elif width_mode == 'percentage' %}
        {% set _ = styles.append('flex-grow: 0; flex-shrink: 1;') %}
    {% elif width_mode == 'stretch' %}
        {% set _ = styles.append('width: 100%; flex-grow: 1; flex-shrink: 1;') %}
    {% endif %}
{% endif %}
```

### Priority 2: Add Multiline Text Support
Update text component macros to use `| replace('\n', '<br>') | safe`:
```jinja2
{# Heading #}
<h{{ properties.level | default(2) }}>{{ properties.text | default('') | replace('\n', '<br>') | safe }}</h{{ properties.level | default(2) }}>

{# Eyebrow #}
<p class="text-eyebrow">{{ properties.text | default('') | replace('\n', '<br>') | safe }}</p>

{# Caption #}
<small class="text-caption">{{ properties.text | default('') | replace('\n', '<br>') | safe }}</small>

{# Blockquote #}
<p>{{ properties.quote | default('') | replace('\n', '<br>') | safe }}</p>
```

### Priority 3: Fix Blockquote Structure
Match CSR structure:
```jinja2
<figure class="text-blockquote chrome-target" data-component-id="{{ component_id }}" style="{{ style_str }}">
    <blockquote>{{ properties.quote | default(properties.text) | default('') | replace('\n', '<br>') | safe }}</blockquote>
    {% if properties.cite %}<figcaption class="blockquote-citation">&mdash; {{ properties.cite }}</figcaption>{% endif %}
</figure>
```

### Priority 4: Enhance Link Component
Add missing properties:
```jinja2
{% set link_style = '' %}
{% if properties.underline %}{% set link_style = link_style ~ 'text-decoration: underline;' %}{% else %}{% set link_style = link_style ~ 'text-decoration: none;' %}{% endif %}
{% set text_align = properties.textAlign | default('left') %}
<div style="text-align: {{ text_align }};">
    <a href="{{ properties.href | default('#') }}" class="{{ classes | join(' ') }}" style="{{ styles }} {{ link_style }}">{{ properties.text | default('') }}</a>
</div>
```

---

## Summary

**Feature Completeness Score:** 65%

**Critical Missing Features:**
1. Width mode support (affects layout behavior)
2. Multiline text support (affects content display)

**Minor Missing Features:**
3. Link underline/textAlign properties
4. Blockquote semantic HTML structure
5. Blockquote text fallback

**Action Required:** Implement Priority 1 and 2 fixes to achieve feature parity with CSR implementation.

