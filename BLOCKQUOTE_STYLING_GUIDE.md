# Blockquote Component - Enhanced Styling Guide

## Overview

The blockquote component now features enhanced visual styling with decorative quotation marks and a prominent left-side accent border.

---

## Visual Features

### 1. **Left Accent Border** 
- **Width:** 5px (up from 4px)
- **Color:** Customizable via `--blockquote-border` CSS variable
- **Default:** `#3b82f6` (blue)
- **Set via YAML:** `appearance.border.accentColor`

### 2. **Background Gradient**
- Subtle gradient fading from the accent color (8% opacity) to transparent
- Creates a visual connection between the border and content
- Rounded corners on the right side for polish

### 3. **Large Opening Quotation Mark**
- Positioned at top-left
- **Size:** 4rem (large and decorative)
- **Font:** Georgia serif for classic typography
- **Color:** Matches accent border with 30% opacity
- **Position:** Absolute, slightly outside the content area

### 4. **Closing Quotation Mark**
- Inline after the quote text
- **Size:** 1.5rem (smaller than opening)
- **Color:** Matches accent border with 50% opacity
- Provides visual balance

### 5. **Enhanced Citation**
- Colored to match accent border
- Semi-bold font weight (500)
- 85% opacity for subtle emphasis
- Em dash (—) prepended automatically

---

## CSS Implementation

**File:** `ssr_python/static/css/components.css`

```css
/* Blockquote Component - Enhanced Styling */
.text-blockquote {
    margin: 2rem 0;
    padding: 1.5rem 2rem 1.5rem 2.5rem;
    position: relative;
    border-left: 5px solid var(--blockquote-border, #3b82f6);
    background: linear-gradient(
        to right,
        color-mix(in srgb, var(--blockquote-border, #3b82f6) 8%, transparent),
        transparent 50%
    );
    border-radius: 0 8px 8px 0;
}

.text-blockquote blockquote {
    font-style: italic;
    margin: 0;
    padding: 0;
    position: relative;
    font-size: 1.1em;
    line-height: 1.6;
    color: inherit;
}

/* Large opening quotation mark */
.text-blockquote blockquote::before {
    content: '"';
    position: absolute;
    left: -1.5rem;
    top: -0.5rem;
    font-size: 4rem;
    line-height: 1;
    font-family: Georgia, serif;
    color: var(--blockquote-border, #3b82f6);
    opacity: 0.3;
    font-weight: bold;
}

/* Closing quotation mark */
.text-blockquote blockquote::after {
    content: '"';
    font-size: 1.5rem;
    line-height: 1;
    font-family: Georgia, serif;
    color: var(--blockquote-border, #3b82f6);
    opacity: 0.5;
    margin-left: 0.25rem;
    font-weight: bold;
}

.blockquote-citation {
    display: block;
    margin-top: 1rem;
    font-size: 0.95rem;
    font-style: normal;
    font-weight: 500;
    color: var(--blockquote-border, #3b82f6);
    opacity: 0.85;
}
```

---

## Usage in YAML

### Basic Blockquote

```yaml
- name: blockquote
  properties:
    quote: Design is intelligence made visible.
    cite: Alina Wheeler
```

**Result:**
- Blue accent border (default)
- Large decorative opening quotation mark
- Closing quotation mark after text
- Citation with em dash

---

### Custom Accent Color

```yaml
- name: blockquote
  properties:
    quote: The only way to do great work is to love what you do.
    cite: Steve Jobs
    appearance:
      border:
        accentColor: '#10b981'  # Green
```

**Result:**
- Green accent border
- Green quotation marks
- Green citation text

---

### With Background Color

```yaml
- name: blockquote
  properties:
    quote: Simplicity is the ultimate sophistication.
    cite: Leonardo da Vinci
    appearance:
      border:
        accentColor: '#f59e0b'  # Amber
      background:
        color: '#fffbeb'  # Light amber background
      padding:
        block: md
        inline: md
```

**Result:**
- Amber accent border
- Light amber background
- Amber quotation marks and citation
- Additional padding

---

### Multiline Quote

```yaml
- name: blockquote
  properties:
    quote: |
      Design is not just what it looks like and feels like.
      Design is how it works.
      
      It's not about being the best.
      It's about being better than you were yesterday.
    cite: Steve Jobs
    appearance:
      border:
        accentColor: '#6366f1'  # Indigo
```

**Result:**
- Multiline text with proper line breaks
- Opening quotation mark at the top
- Closing quotation mark after the last line

---

## Color Palette Examples

### Professional Tones

| Color | Hex | Use Case |
|-------|-----|----------|
| Blue | `#3b82f6` | Default, trust, corporate |
| Green | `#10b981` | Success, growth, eco-friendly |
| Purple | `#8b5cf6` | Creative, luxury, innovation |
| Indigo | `#6366f1` | Modern, tech, professional |

### Warm Tones

| Color | Hex | Use Case |
|-------|-----|----------|
| Amber | `#f59e0b` | Warning, attention, energy |
| Orange | `#f97316` | Enthusiasm, creativity |
| Red | `#ef4444` | Urgent, important, passionate |
| Pink | `#ec4899` | Playful, friendly, modern |

### Cool Tones

| Color | Hex | Use Case |
|-------|-----|----------|
| Cyan | `#06b6d4` | Fresh, clean, tech |
| Teal | `#14b8a6` | Calm, balanced, healing |
| Sky Blue | `#0ea5e9` | Open, friendly, approachable |

---

## Browser Compatibility

All features use standard CSS:
- ✅ `::before` and `::after` pseudo-elements
- ✅ CSS custom properties (`var(--blockquote-border)`)
- ✅ `color-mix()` for gradient (modern browsers)
- ✅ Absolute positioning
- ✅ Linear gradients

**Fallback:** Browsers that don't support `color-mix()` will show the border without the gradient background, which is acceptable.

---

## Customization Options

### Adjust Quotation Mark Size

To change the opening quotation mark size, modify:
```css
.text-blockquote blockquote::before {
    font-size: 5rem;  /* Increase for larger mark */
}
```

### Remove Quotation Marks

To disable quotation marks entirely:
```css
.text-blockquote blockquote::before,
.text-blockquote blockquote::after {
    content: none;
}
```

### Change Border Width

To make the accent border thicker:
```css
.text-blockquote {
    border-left: 8px solid var(--blockquote-border, #3b82f6);
}
```

### Adjust Padding

To give more breathing room:
```css
.text-blockquote {
    padding: 2rem 2.5rem 2rem 3rem;
}
```

---

## Accessibility

- **Color contrast:** Accent colors should meet WCAG AA standards against backgrounds
- **Quotation marks:** Decorative only (not read by screen readers)
- **Semantic HTML:** Uses `<figure>` and `<blockquote>` elements
- **Citation:** Uses `<figcaption>` with em dash for proper attribution

---

## Examples in Context

### Testimonial

```yaml
- name: blockquote
  properties:
    quote: This tool transformed how we build websites. The flexibility and ease of use is unmatched.
    cite: Sarah Chen, Lead Designer at TechCorp
    typography:
      size: lg
      weight: medium
      align: left
    appearance:
      border:
        accentColor: '#10b981'
      background:
        color: '#f0fdf4'
      padding:
        block: lg
        inline: lg
    layout:
      widthMode: stretch
```

### Inspirational Quote

```yaml
- name: blockquote
  properties:
    quote: The future belongs to those who believe in the beauty of their dreams.
    cite: Eleanor Roosevelt
    typography:
      size: xl
      weight: semibold
      align: center
    appearance:
      border:
        accentColor: '#8b5cf6'
      padding:
        block: xl
        inline: lg
    layout:
      widthMode: stretch
```

### Pull Quote

```yaml
- name: blockquote
  properties:
    quote: Design is thinking made visual.
    cite: Saul Bass
    typography:
      size: xxl
      weight: bold
      align: center
    appearance:
      border:
        accentColor: '#f59e0b'
      padding:
        block: xl
        inline: xl
    layout:
      widthMode: fit
```

---

## Summary

The enhanced blockquote styling provides:
- ✅ Visual hierarchy with large decorative quotation marks
- ✅ Customizable accent border colors
- ✅ Subtle background gradient
- ✅ Styled citations
- ✅ Professional, polished appearance
- ✅ Responsive and accessible

**Status:** ✅ IMPLEMENTED

