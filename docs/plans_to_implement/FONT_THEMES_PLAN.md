# Plan: Google Fonts in Theme Dropdowns

## Context

The themes panel has 3 font `<select>` dropdowns (Main Headings, Sub Headings, Content) using `FONT_OPTIONS` — 9 web-safe system fonts. Replace these with 31 Google Fonts organized by category using `<optgroup>`, with dynamic font loading and preview text.

**What stays the same:**
- 3 dropdowns layout (`renderFontDropdowns()`)
- `selectedFonts` state object
- Font anchors in `applyTheme()` (`&font-heading-main`, etc.)
- YAML anchor/alias pattern for `typography.fontFamily`

**What changes:**
- `FONT_OPTIONS` → `FONT_CATALOG` (31 Google Fonts with categories)
- Plain `<option>` list → `<optgroup>` grouped by category
- New `loadGoogleFont()` utility for dynamic font loading
- Font preview text below each dropdown
- Fonts loaded into both parent window and preview iframe

---

## Part 1: `FONT_CATALOG` — Replace `FONT_OPTIONS`

**File: `ssr_python/static/js/themesPanel.js`**

Replace `FONT_OPTIONS` (lines 71–81) with:

```javascript
const FONT_CATALOG = [
    // === DISPLAY ===
    { value: "'Playfair Display', serif",    label: 'Playfair Display',    category: 'Display',      gfontName: 'Playfair Display',    weights: '400;700;900' },
    { value: "'Bebas Neue', sans-serif",     label: 'Bebas Neue',          category: 'Display',      gfontName: 'Bebas Neue',          weights: '400' },
    { value: "'Abril Fatface', serif",       label: 'Abril Fatface',       category: 'Display',      gfontName: 'Abril Fatface',       weights: '400' },
    { value: "'Lobster', cursive",           label: 'Lobster',             category: 'Display',      gfontName: 'Lobster',             weights: '400' },
    { value: "'Oswald', sans-serif",         label: 'Oswald',              category: 'Display',      gfontName: 'Oswald',              weights: '400;700' },
    // === PROFESSIONAL ===
    { value: "'Inter', sans-serif",          label: 'Inter',               category: 'Professional', gfontName: 'Inter',               weights: '300;400;500;600;700' },
    { value: "'Roboto', sans-serif",         label: 'Roboto',              category: 'Professional', gfontName: 'Roboto',              weights: '300;400;500;700' },
    { value: "'Open Sans', sans-serif",      label: 'Open Sans',           category: 'Professional', gfontName: 'Open Sans',           weights: '300;400;600;700' },
    { value: "'Lato', sans-serif",           label: 'Lato',                category: 'Professional', gfontName: 'Lato',                weights: '300;400;700;900' },
    { value: "'Montserrat', sans-serif",     label: 'Montserrat',          category: 'Professional', gfontName: 'Montserrat',          weights: '300;400;500;600;700' },
    { value: "'Poppins', sans-serif",        label: 'Poppins',             category: 'Professional', gfontName: 'Poppins',             weights: '300;400;500;600;700' },
    { value: "'Nunito Sans', sans-serif",    label: 'Nunito Sans',         category: 'Professional', gfontName: 'Nunito Sans',         weights: '300;400;600;700' },
    { value: "'Source Sans 3', sans-serif",  label: 'Source Sans 3',       category: 'Professional', gfontName: 'Source Sans 3',       weights: '300;400;600;700' },
    { value: "'Raleway', sans-serif",        label: 'Raleway',             category: 'Professional', gfontName: 'Raleway',             weights: '300;400;500;600;700' },
    { value: "'Work Sans', sans-serif",      label: 'Work Sans',           category: 'Professional', gfontName: 'Work Sans',           weights: '300;400;500;600;700' },
    { value: "'Noto Sans', sans-serif",      label: 'Noto Sans',           category: 'Professional', gfontName: 'Noto Sans',           weights: '300;400;500;700' },
    { value: "'PT Sans', sans-serif",        label: 'PT Sans',             category: 'Professional', gfontName: 'PT Sans',             weights: '400;700' },
    { value: "'Rubik', sans-serif",          label: 'Rubik',               category: 'Professional', gfontName: 'Rubik',               weights: '300;400;500;700' },
    { value: "'DM Sans', sans-serif",        label: 'DM Sans',             category: 'Professional', gfontName: 'DM Sans',             weights: '400;500;700' },
    { value: "'Manrope', sans-serif",        label: 'Manrope',             category: 'Professional', gfontName: 'Manrope',             weights: '300;400;500;600;700' },
    // === MODERN ===
    { value: "'Space Grotesk', sans-serif",      label: 'Space Grotesk',      category: 'Modern', gfontName: 'Space Grotesk',      weights: '300;400;500;600;700' },
    { value: "'Outfit', sans-serif",             label: 'Outfit',             category: 'Modern', gfontName: 'Outfit',             weights: '300;400;500;600;700' },
    { value: "'Sora', sans-serif",               label: 'Sora',               category: 'Modern', gfontName: 'Sora',               weights: '300;400;500;600;700' },
    { value: "'Plus Jakarta Sans', sans-serif",  label: 'Plus Jakarta Sans',  category: 'Modern', gfontName: 'Plus Jakarta Sans',  weights: '300;400;500;600;700' },
    { value: "'IBM Plex Sans', sans-serif",      label: 'IBM Plex Sans',      category: 'Modern', gfontName: 'IBM Plex Sans',      weights: '300;400;500;600;700' },
    // === RETRO ===
    { value: "'Merriweather', serif",        label: 'Merriweather',        category: 'Retro', gfontName: 'Merriweather',        weights: '300;400;700;900' },
    { value: "'Lora', serif",                label: 'Lora',                category: 'Retro', gfontName: 'Lora',                weights: '400;500;600;700' },
    { value: "'Libre Baskerville', serif",   label: 'Libre Baskerville',   category: 'Retro', gfontName: 'Libre Baskerville',   weights: '400;700' },
    // === CALLIGRAPHY ===
    { value: "'Dancing Script', cursive",    label: 'Dancing Script',      category: 'Calligraphy', gfontName: 'Dancing Script', weights: '400;700' },
    { value: "'Great Vibes', cursive",       label: 'Great Vibes',         category: 'Calligraphy', gfontName: 'Great Vibes',    weights: '400' },
    { value: "'Sacramento', cursive",        label: 'Sacramento',          category: 'Calligraphy', gfontName: 'Sacramento',     weights: '400' },
];
```

Update `selectedFonts` defaults to use Google Font values:

```javascript
let selectedFonts = {
    headingMain: "'Inter', sans-serif",
    headingLevel2: "'Inter', sans-serif",
    content: "'Inter', sans-serif"
};
```

---

## Part 2: Dynamic Google Fonts Loading

**File: `ssr_python/static/js/themesPanel.js`**

Add these utility functions:

```javascript
/**
 * Dynamically load a Google Font into a document <head>
 * @param {Document} doc - document to inject into (parent or iframe)
 * @param {string} fontFamily - e.g. "Playfair Display"
 * @param {string} weights - e.g. "400;700" (semicolon-separated)
 */
function loadGoogleFont(doc, fontFamily, weights = '400;700') {
    const id = 'gfont-' + fontFamily.replace(/\s+/g, '-').toLowerCase();
    if (doc.getElementById(id)) return;

    const link = doc.createElement('link');
    link.id = id;
    link.rel = 'stylesheet';
    link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontFamily)}:wght@${weights}&display=swap`;
    doc.head.appendChild(link);
}

/**
 * Load a font into both parent window and preview iframe
 */
function ensureFontLoaded(fontCssValue) {
    const entry = FONT_CATALOG.find(f => f.value === fontCssValue);
    if (!entry) return;

    loadGoogleFont(document, entry.gfontName, entry.weights);
    const iframe = document.getElementById('preview-frame');
    if (iframe && iframe.contentDocument) {
        loadGoogleFont(iframe.contentDocument, entry.gfontName, entry.weights);
    }
}
```

---

## Part 3: Update `renderFontDropdowns()` — `<optgroup>` + Preview Text

**File: `ssr_python/static/js/themesPanel.js`**

Replace the existing `renderFontDropdowns()` function:

```javascript
function renderFontDropdowns() {
    const fonts = [
        { key: 'headingMain', label: 'Main Headings' },
        { key: 'headingLevel2', label: 'Sub Headings' },
        { key: 'content', label: 'Content' }
    ];

    const categories = [...new Set(FONT_CATALOG.map(f => f.category))];

    return fonts.map(({ key, label }) => {
        const currentEntry = FONT_CATALOG.find(f => f.value === selectedFonts[key]);
        const previewFont = currentEntry ? currentEntry.label : '';

        return `
            <div class="theme-font-row">
                <span class="theme-font-label">${label}</span>
                <select class="theme-font-select" data-font-key="${key}">
                    ${categories.map(cat => `
                        <optgroup label="${cat}">
                            ${FONT_CATALOG
                                .filter(f => f.category === cat)
                                .map(opt => `
                                    <option value="${opt.value}" ${selectedFonts[key] === opt.value ? 'selected' : ''}>
                                        ${opt.label}
                                    </option>
                                `).join('')}
                        </optgroup>
                    `).join('')}
                </select>
                <div class="theme-font-preview" style="font-family: ${selectedFonts[key]}">
                    ${previewFont || 'The quick brown fox'}
                </div>
            </div>
        `;
    }).join('');
}
```

---

## Part 4: Update Event Handlers — Load Fonts on Change + Update Preview

**File: `ssr_python/static/js/themesPanel.js`**

Update the font dropdown change handler in `attachThemePanelEvents()`:

```javascript
// Font dropdown changes
container.querySelectorAll('.theme-font-select').forEach(select => {
    select.addEventListener('change', (e) => {
        const key = e.target.dataset.fontKey;
        selectedFonts[key] = e.target.value;
        ensureFontLoaded(e.target.value);

        // Update preview text below dropdown
        const previewEl = e.target.closest('.theme-font-row').querySelector('.theme-font-preview');
        if (previewEl) {
            previewEl.style.fontFamily = e.target.value;
            const entry = FONT_CATALOG.find(f => f.value === e.target.value);
            previewEl.textContent = entry ? entry.label : 'The quick brown fox';
        }
    });
});
```

---

## Part 5: Load Fonts from YAML on Panel Open

**File: `ssr_python/static/js/themesPanel.js`**

In `renderThemesPanel()`, after loading `selectedFonts` from YAML, load the Google Fonts:

```javascript
if (loadFromYaml) {
    const currentTheme = getCurrentTheme();
    if (currentTheme) {
        if (currentTheme.fonts) {
            selectedFonts = { ...selectedFonts, ...currentTheme.fonts };
            // Load Google Fonts for current theme fonts
            Object.values(selectedFonts).forEach(fontValue => ensureFontLoaded(fontValue));
        }
        // ... existing color loading code ...
    }
}
```

---

## Part 6: Load Fonts into Iframe

### 6A. Send font list to iframe after content update

**File: `ssr_python/static/js/ssr_app.js`** — After sending `UPDATE_CONTENT`, also send `LOAD_FONTS`:

```javascript
const structure = getYamlStructureFromEditor();
const themeFonts = structure?.[0]?.properties?.theme?.fonts;
if (themeFonts) {
    iframe.contentWindow.postMessage({
        type: 'LOAD_FONTS',
        fonts: Object.values(themeFonts)
    }, '*');
}
```

### 6B. Handle `LOAD_FONTS` in iframe

**File: `ssr_python/static/js/preview_bridge.js`** — Add to message handler switch:

```javascript
case 'LOAD_FONTS':
    if (data.fonts) {
        data.fonts.forEach(fontValue => {
            const match = fontValue.match(/'([^']+)'/);
            if (match) {
                const fontName = match[1];
                const id = 'gfont-' + fontName.replace(/\s+/g, '-').toLowerCase();
                if (!document.getElementById(id)) {
                    const link = document.createElement('link');
                    link.id = id;
                    link.rel = 'stylesheet';
                    link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontName)}:wght@300;400;500;600;700&display=swap`;
                    document.head.appendChild(link);
                }
            }
        });
    }
    break;
```

---

## Part 7: Font Preview CSS

**File: `ssr_python/static/css/style.css`** — Add after `.theme-font-select` styles:

```css
.theme-font-preview {
    font-size: 13px;
    color: var(--text-muted);
    padding: 4px 0 2px;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

---

## Part 8: Load Fonts in `applyTheme()` Before Render

**File: `ssr_python/static/js/themesPanel.js`**

In `applyTheme()`, before calling `renderPreview()`, load the selected fonts into the iframe:

```javascript
// Ensure fonts are loaded in iframe before render
Object.values(selectedFonts).forEach(fontValue => ensureFontLoaded(fontValue));
```

---

## Files Summary

| File | Change |
|------|--------|
| `static/js/themesPanel.js` | Replace `FONT_OPTIONS` with `FONT_CATALOG` (31 fonts). Add `loadGoogleFont()`, `ensureFontLoaded()`. Update `renderFontDropdowns()` with `<optgroup>` + preview text. Update font change handler. Load fonts from YAML. |
| `static/css/style.css` | Add `.theme-font-preview` styles |
| `static/js/ssr_app.js` | Send `LOAD_FONTS` message to iframe after content update |
| `static/js/preview_bridge.js` | Handle `LOAD_FONTS` message, inject Google Font `<link>` tags |

## What Does NOT Change

- `component_defaults.yaml` — Font values stored as plain CSS strings
- `component_schemas.yaml` — No font schema fields
- `_utilities.html` — `build_styles()` already handles `typography.fontFamily`
- YAML anchor/alias pattern — Same `&font-heading-main` / `*font-heading-main`
- `index.html` / `preview_frame.html` — No static font `<link>` tags (all dynamic)
- Color theme architecture — Completely untouched
- `applyTheme()` font anchor logic — Same hardcoded `setAnchorOnScalar()` calls (no config constant needed)

## Verification

1. Start Flask, load app
2. Open Themes panel — 3 font dropdowns with `<optgroup>` categories (Display, Professional, Modern, Retro, Calligraphy)
3. Change "Main Headings" to "Playfair Display" — Google Font loads, preview text updates with the font
4. Click Apply — YAML updates with font anchors, preview iframe loads the font and renders correctly
5. Refresh page — fonts reload from YAML theme, preview renders correctly
6. Verify color themes still work independently
7. `python -m pytest tests/ -v` — all 30 tests pass
