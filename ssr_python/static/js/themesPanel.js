/**
 * Themes Panel - Manage site-level fonts and color themes
 * Theme is stored at site.properties.theme (anchors defined before all content).
 * Falls back to page.properties.theme for backward compat with old YAML.
 * Uses native YAML anchors via eemeli/yaml Document API.
 */

import { getYamlStructureFromEditor, updateYamlEditor } from './yamlUtils.js';
import { parseDocument, YAML } from './yamlWrapper.js';
import { renderPreview } from './ssr_app.js';
import { historyManager } from './historyManager.js';

// WCAG 2.1 Accessible Color Themes - organized by category
// All themes meet 4.5:1 contrast ratio for text colors on Background
// Color Distribution: Background (60%), Primary (headings 30%), Text (body), Secondary (10% - UI), Accent (CTAs only)
const COLOR_THEMES = [
    // === TIMELESS & CLASSIC ===
    { name: 'Warm Ivory', category: 'Classic', colors: { background: '#FDF8F0', primary: '#2D2420', text: '#4A4440', secondary: '#E8DED0', accent: '#B8510D' }},
    { name: 'Slate Professional', category: 'Classic', colors: { background: '#E8EDF2', primary: '#1E3A5F', text: '#374151', secondary: '#C5D4E3', accent: '#0052CC' }},
    { name: 'Champagne Luxe', category: 'Classic', colors: { background: '#F5F0E6', primary: '#1C1810', text: '#3D3830', secondary: '#E0D8C8', accent: '#996515' }},
    { name: 'Bauhaus Primary', category: 'Classic', colors: { background: '#FFFBE6', primary: '#0D0D0D', text: '#2D2D2D', secondary: '#F5E6B8', accent: '#DD0100' }},
    { name: 'Concrete Raw', category: 'Classic', colors: { background: '#E5E2DD', primary: '#1A1A1A', text: '#3D3D3D', secondary: '#C8C4BB', accent: '#FF4D00' }},
    { name: 'Midnight Prestige', category: 'Classic', colors: { background: '#1A1A2E', primary: '#F5F5F5', text: '#C8C8D8', secondary: '#2D2D45', accent: '#D4AF37' }},

    // === RETRO & NOSTALGIC ===
    { name: 'Atomic Cream', category: 'Retro', colors: { background: '#FFF5D6', primary: '#1A3A3A', text: '#3D4A4A', secondary: '#E8DEB0', accent: '#008B8B' }},
    { name: 'Synthwave Dark', category: 'Retro', colors: { background: '#1A0A2E', primary: '#F5E6FA', text: '#C8B8D8', secondary: '#2E1650', accent: '#FF00FF' }},
    { name: 'Grunge Ochre', category: 'Retro', colors: { background: '#DED5B8', primary: '#2C2416', text: '#4A4030', secondary: '#C4B898', accent: '#8B0000' }},
    { name: 'Sepia Vintage', category: 'Retro', colors: { background: '#F5E6D3', primary: '#3D2B1F', text: '#5A4838', secondary: '#E0CDB5', accent: '#8B4513' }},
    { name: 'Vaporwave Pink', category: 'Retro', colors: { background: '#FFD6E8', primary: '#2D1B4E', text: '#4A3860', secondary: '#F0B8D4', accent: '#9B59B6' }},
    { name: 'Art Deco Noir', category: 'Retro', colors: { background: '#0F0F0F', primary: '#F5F0E6', text: '#C8C4B8', secondary: '#2A2520', accent: '#D4AF37' }},
    { name: 'Pop Art Yellow', category: 'Retro', colors: { background: '#FFEB3B', primary: '#0D0D0D', text: '#2D2D00', secondary: '#FFD600', accent: '#FF0000' }},

    // === FUTURISTIC & TECH ===
    { name: 'Cyberpunk Neon', category: 'Tech', colors: { background: '#0D0A14', primary: '#F0E6FA', text: '#B8A8D0', secondary: '#1E1428', accent: '#FF0080' }},
    { name: 'Solarpunk Leaf', category: 'Tech', colors: { background: '#E6F5E0', primary: '#1A3A1A', text: '#3A5A3A', secondary: '#C8E8B8', accent: '#2E8B57' }},
    { name: 'Glass Azure', category: 'Tech', colors: { background: '#D6EBF5', primary: '#1A365D', text: '#334E68', secondary: '#B0D4E8', accent: '#3182CE' }},
    { name: 'Soft Lavender', category: 'Tech', colors: { background: '#E8E0F0', primary: '#2D1B4E', text: '#4A3868', secondary: '#D0C0E0', accent: '#6C63FF' }},
    { name: 'Terminal Green', category: 'Tech', colors: { background: '#0A1A0A', primary: '#E8FCE8', text: '#A8D8A8', secondary: '#142814', accent: '#00FF41' }},
    { name: 'Nebula Purple', category: 'Tech', colors: { background: '#14101E', primary: '#E8E0F8', text: '#B0A8C8', secondary: '#251D38', accent: '#9D4EDD' }},
    { name: 'Holographic', category: 'Tech', colors: { background: '#E6F0FA', primary: '#1A2035', text: '#384860', secondary: '#C8D8F0', accent: '#EC4899' }},

    // === NATURE & ORGANIC ===
    { name: 'Sage Garden', category: 'Nature', colors: { background: '#E0EBD8', primary: '#1A3318', text: '#3A5338', secondary: '#C0D8B0', accent: '#228B22' }},
    { name: 'Terracotta', category: 'Nature', colors: { background: '#F5E0D0', primary: '#3D2B1F', text: '#5A4838', secondary: '#E8C8B0', accent: '#C2703B' }},
    { name: 'Deep Ocean', category: 'Nature', colors: { background: '#D0E8F0', primary: '#1A3A4A', text: '#385868', secondary: '#A8D0E0', accent: '#0077B6' }},
    { name: 'Moss Forest', category: 'Nature', colors: { background: '#D8E8D0', primary: '#1E3E1E', text: '#3A5A3A', secondary: '#B8D0A8', accent: '#2E7D32' }},
    { name: 'Desert Sunset', category: 'Nature', colors: { background: '#FFE8D6', primary: '#4A2C17', text: '#5A4030', secondary: '#F5D0B0', accent: '#D2691E' }},
    { name: 'Coral Reef', category: 'Nature', colors: { background: '#FFE6E0', primary: '#2D1A1A', text: '#4A3838', secondary: '#F5C8C0', accent: '#FF6B35' }},
    { name: 'Lavender Field', category: 'Nature', colors: { background: '#E8E0F0', primary: '#2D2040', text: '#4A3860', secondary: '#D0C0E0', accent: '#7C3AED' }},

    // === EMOTIONAL MOODS ===
    { name: 'Cinema Noir', category: 'Mood', colors: { background: '#0F0F0F', primary: '#F5F5F5', text: '#C8C8C8', secondary: '#1F1F1F', accent: '#DC143C' }},
    { name: 'Bubblegum', category: 'Mood', colors: { background: '#FFD6E6', primary: '#4A1942', text: '#5A3058', secondary: '#F5B0D0', accent: '#FF1493' }},
    { name: 'Fire & Ice', category: 'Mood', colors: { background: '#1A0A0A', primary: '#E8F0FA', text: '#B8C0D0', secondary: '#2D1414', accent: '#FF4500' }},
    { name: 'Zen Stone', category: 'Mood', colors: { background: '#E8E6E0', primary: '#3D3D35', text: '#5A5A50', secondary: '#D0CEC5', accent: '#708090' }},
    { name: 'Ivy League', category: 'Mood', colors: { background: '#E6EBE0', primary: '#1A2E28', text: '#384840', secondary: '#C8D8C0', accent: '#00356B' }},
    { name: 'Gothic Rose', category: 'Mood', colors: { background: '#1A0F0F', primary: '#F5E6E6', text: '#C8B8B8', secondary: '#2D1818', accent: '#C41E3A' }},
    { name: 'Hygge Warm', category: 'Mood', colors: { background: '#FFF5E6', primary: '#2D3436', text: '#4A5050', secondary: '#F0E0C8', accent: '#D35400' }},
    { name: 'Neon Street', category: 'Mood', colors: { background: '#1A1A1A', primary: '#F5F5F5', text: '#C8C8C8', secondary: '#2D2D2D', accent: '#FFEA00' }},
    { name: 'Digital Realm', category: 'Mood', colors: { background: '#0A0A1A', primary: '#E6E6FF', text: '#B0B0D8', secondary: '#14142D', accent: '#00FFFF' }},
];

// Shared theme color config — single source of truth for color keys, anchor names, and labels
export const THEME_COLOR_CONFIG = [
    { key: 'primary', anchor: 'color-primary', label: 'Primary (Headings)' },
    { key: 'text', anchor: 'color-text', label: 'Text (Body)' },
    { key: 'secondary', anchor: 'color-secondary', label: 'Secondary' },
    { key: 'accent', anchor: 'color-accent', label: 'Accent' },
    { key: 'background', anchor: 'color-background', label: 'Background' },
];

// Shared theme font config — single source of truth for font keys, anchor names, and labels
export const THEME_FONT_CONFIG = [
    { key: 'heading', anchor: 'font-heading', label: 'Headings' },
    { key: 'content', anchor: 'font-content', label: 'Content' },
];

// Google Fonts catalog organized by category
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

// Current selected state
let selectedThemeIndex = 0;
let selectedTheme = { ...COLOR_THEMES[0].colors };
let selectedFonts = {
    heading: "'Inter', sans-serif",
    content: "'Inter', sans-serif"
};

/**
 * Dynamically load a Google Font into a document <head>
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
        try {
            loadGoogleFont(iframe.contentDocument, entry.gfontName, entry.weights);
        } catch (e) {
            // Cross-origin iframe, will use LOAD_FONTS message instead
        }
    }
}

/**
 * Get current theme from site or page component.
 * Prefers site.properties.theme (new format), falls back to page-level (backward compat).
 * Returns the same { fonts, colors } object regardless of source.
 */
export function getCurrentTheme() {
    const structure = getYamlStructureFromEditor();
    if (!structure || !Array.isArray(structure) || structure.length === 0) {
        return null;
    }

    const site = structure[0];

    // Prefer site-level theme (new format)
    if (site.properties?.theme) return site.properties.theme;

    // Fallback: page-level theme (backward compat for old YAML)
    const page = site.components?.[0];
    if (page?.properties?.theme) return page.properties.theme;

    return null;
}

/**
 * Render the themes panel
 * @param {boolean} loadFromYaml - Whether to load theme from YAML (default: true)
 */
export function renderThemesPanel(loadFromYaml = true) {
    const container = document.getElementById('themesContent');
    if (!container) return;

    // Only load from YAML on initial render, not after user selection
    if (loadFromYaml) {
        const currentTheme = getCurrentTheme();
        if (currentTheme) {
            if (currentTheme.fonts) {
                selectedFonts = { ...selectedFonts, ...currentTheme.fonts };
                // Load Google Fonts for current theme fonts
                Object.values(selectedFonts).forEach(fontValue => ensureFontLoaded(fontValue));
            }
            if (currentTheme.colors) {
                selectedTheme = { ...selectedTheme, ...currentTheme.colors };
                // Try to match to a preset
                const matchedIndex = COLOR_THEMES.findIndex(t =>
                    t.colors.primary.toLowerCase() === selectedTheme.primary?.toLowerCase()
                );
                if (matchedIndex >= 0) {
                    selectedThemeIndex = matchedIndex;
                }
            }
        }
    }

    container.innerHTML = `
        <!-- Fonts Section -->
        <div class="theme-section">
            <div class="theme-section-title">Fonts</div>
            ${renderFontDropdowns()}
        </div>

        <!-- Color Themes Section -->
        <div class="theme-section">
            <div class="theme-section-title">Color Theme</div>

            <!-- Selected Theme (Editable) -->
            <div class="theme-selected-box">
                <div class="theme-selected-name">${COLOR_THEMES[selectedThemeIndex].name}</div>
                <div class="theme-selected-colors">
                    ${renderEditableSwatches()}
                </div>
            </div>

            <!-- Theme List - Grouped by Category -->
            <div class="theme-list">
                ${renderThemesByCategory()}
            </div>
        </div>

    `;

    // Render apply button in the panel footer (outside scrollable content)
    const footer = document.getElementById('themesFooter');
    if (footer) {
        footer.innerHTML = `<button class="theme-apply-btn" id="applyThemeBtn">Apply</button>`;
    }

    // Attach event handlers
    attachThemePanelEvents(container, footer);
}

/**
 * Render themes grouped by category
 */
function renderThemesByCategory() {
    // Get unique categories in order
    const categories = [...new Set(COLOR_THEMES.map(t => t.category))];

    return categories.map(category => `
        <div class="theme-category">
            <div class="theme-category-label">${category}</div>
            ${COLOR_THEMES
                .map((theme, index) => ({ theme, index }))
                .filter(({ theme }) => theme.category === category)
                .map(({ theme, index }) => `
                    <div class="theme-row ${index === selectedThemeIndex ? 'selected' : ''}" data-theme-index="${index}">
                        <div class="theme-row-colors">
                            <div class="theme-row-pill" style="background: ${theme.colors.background}; border: 1px solid #ddd;"></div>
                            <div class="theme-row-pill" style="background: ${theme.colors.primary}"></div>
                            <div class="theme-row-pill" style="background: ${theme.colors.text}"></div>
                            <div class="theme-row-pill" style="background: ${theme.colors.secondary}"></div>
                            <div class="theme-row-pill" style="background: ${theme.colors.accent}"></div>
                        </div>
                        <span class="theme-row-name">${theme.name}</span>
                    </div>
                `).join('')}
        </div>
    `).join('');
}

/**
 * Render font dropdown rows with <optgroup> categories and preview text
 */
function renderFontDropdowns() {
    const categories = [...new Set(FONT_CATALOG.map(f => f.category))];

    return THEME_FONT_CONFIG.map(({ key, label }) => {
        const currentEntry = FONT_CATALOG.find(f => f.value === selectedFonts[key]);
        const previewFont = currentEntry ? currentEntry.label : 'The quick brown fox';

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
                <div class="theme-font-preview" style="font-family: ${selectedFonts[key]}">${previewFont}</div>
            </div>
        `;
    }).join('');
}

/**
 * Render editable color swatches
 */
function renderEditableSwatches() {
    const colors = [
         { key: 'background', label: 'Bg' },
        { key: 'primary', label: 'Pri' },
        { key: 'text', label: 'Txt' },
        { key: 'secondary', label: 'Sec' },
        { key: 'accent', label: 'Acc' }
    ];

    return colors.map(({ key, label }) => `
        <div class="theme-color-swatch-wrapper">
            <div class="theme-color-swatch" style="background: ${selectedTheme[key]}" data-color-key="${key}">
                <input type="color" value="${selectedTheme[key]}" data-color-key="${key}">
            </div>
            <div class="theme-color-label">${label}</div>
        </div>
    `).join('');
}

/**
 * Attach event handlers to theme panel elements
 */
function attachThemePanelEvents(container, footer) {
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

    // Theme row clicks
    container.querySelectorAll('.theme-row').forEach(row => {
        row.addEventListener('click', () => {
            const index = parseInt(row.dataset.themeIndex, 10);
            selectTheme(index);
        });
    });

    // Color swatch changes
    container.querySelectorAll('.theme-color-swatch input[type="color"]').forEach(input => {
        input.addEventListener('input', (e) => {
            const key = e.target.dataset.colorKey;
            selectedTheme[key] = e.target.value;
            // Update swatch background
            e.target.parentElement.style.background = e.target.value;
        });
    });

    // Apply button (rendered in footer, outside scrollable content)
    const applyBtn = footer ? footer.querySelector('#applyThemeBtn') : container.querySelector('#applyThemeBtn');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyTheme);
    }
}

/**
 * Select a theme from the list
 */
function selectTheme(index) {
    selectedThemeIndex = index;
    selectedTheme = { ...COLOR_THEMES[index].colors };

    // Re-render to update UI (skip loading from YAML to preserve user selection)
    renderThemesPanel(false);
}

/**
 * Apply theme to YAML using native Document API with anchors and aliases.
 * Sets theme at SITE level (site.properties.theme) so anchors are defined
 * before all page content — enabling aliases everywhere.
 */
export async function applyTheme() {
    console.log('[Themes] Applying theme at site level with native YAML anchors...');

    const editor = document.getElementById('codeEditor');
    if (!editor || !editor.value.trim()) {
        console.warn('[Themes] No YAML content in editor');
        return;
    }

    try {
        // Parse as Document to work with nodes directly
        const doc = parseDocument(editor.value);

        if (doc.errors && doc.errors.length > 0) {
            console.error('[Themes] YAML parse errors:', doc.errors);
            return;
        }

        // Get the site component (first item in array)
        const contents = doc.contents;
        if (!YAML.isSeq(contents) || contents.items.length === 0) {
            console.warn('[Themes] Invalid document structure - expected array');
            return;
        }

        const siteNode = contents.items[0];
        if (!YAML.isMap(siteNode)) {
            console.warn('[Themes] Root component is not a map');
            return;
        }

        // Ensure fonts are loaded before render
        Object.values(selectedFonts).forEach(fontValue => ensureFontLoaded(fontValue));

        // Create theme structure with anchored values
        const fontData = {};
        for (const fc of THEME_FONT_CONFIG) {
            fontData[fc.key] = selectedFonts[fc.key];
        }
        const themeData = {
            fonts: fontData,
            colors: {
                primary: selectedTheme.primary,
                text: selectedTheme.text,
                secondary: selectedTheme.secondary,
                accent: selectedTheme.accent,
                background: selectedTheme.background
            }
        };

        // Create theme node from data
        const themeNode = doc.createNode(themeData);

        // Set anchors on the color scalar values
        const colorsNode = themeNode.get('colors', true);
        if (YAML.isMap(colorsNode)) {
            for (const tc of THEME_COLOR_CONFIG) {
                setAnchorOnScalar(colorsNode, tc.key, tc.anchor);
            }
        }

        // Set anchors on font scalar values
        const fontsNode = themeNode.get('fonts', true);
        if (YAML.isMap(fontsNode)) {
            for (const fc of THEME_FONT_CONFIG) {
                setAnchorOnScalar(fontsNode, fc.key, fc.anchor);
            }
        }

        // Set theme on SITE properties (not page)
        let sitePropsNode = siteNode.get('properties', true);
        if (!sitePropsNode || !YAML.isMap(sitePropsNode)) {
            sitePropsNode = doc.createNode({});
            siteNode.set('properties', sitePropsNode);
        }
        sitePropsNode.set('theme', themeNode);

        // Reorder site node keys so 'properties' is before header/footer/components
        // This ensures YAML anchors (in properties.theme) appear before aliases
        reorderSiteKeys(siteNode);

        // Remove page-level theme from all pages (clean migration)
        const siteComponents = siteNode.get('components', true);
        if (YAML.isSeq(siteComponents)) {
            for (const pageNode of siteComponents.items) {
                if (YAML.isMap(pageNode)) {
                    const pageProps = pageNode.get('properties', true);
                    if (pageProps && YAML.isMap(pageProps) && pageProps.has('theme')) {
                        pageProps.delete('theme');
                    }
                }
            }
        }

        // Build map of color values to their anchor nodes for alias creation
        const colorToAnchorNode = new Map();
        if (YAML.isMap(colorsNode)) {
            for (const pair of colorsNode.items) {
                if (YAML.isPair(pair) && YAML.isScalar(pair.value)) {
                    const colorValue = normalizeColor(String(pair.value.value));
                    colorToAnchorNode.set(colorValue, pair.value);
                }
            }
        }

        // Walk all pages for alias replacement
        if (YAML.isSeq(siteComponents)) {
            for (const pageNode of siteComponents.items) {
                if (YAML.isMap(pageNode)) {
                    // Replace page background color alias too
                    const pageProps = pageNode.get('properties', true);
                    if (YAML.isMap(pageProps)) {
                        const pageBg = pageProps.get('appearance', true)?.get('background', true);
                        if (pageBg && YAML.isMap(pageBg)) {
                            replaceColorWithAliasInMap(doc, pageBg, 'color', colorToAnchorNode);
                        }
                    }
                    const pageComps = pageNode.get('components', true);
                    if (YAML.isSeq(pageComps)) walkAndReplaceWithAliases(doc, pageComps, colorToAnchorNode);
                }
            }
        }

        // Generate YAML string (anchors and aliases preserved automatically!)
        const yamlText = String(doc);

        // Update editor
        updateYamlEditor(yamlText);

        // Push to history
        historyManager.push(yamlText);

        // Trigger render with the new YAML content
        await renderPreview(yamlText);

        console.log('[Themes] Theme applied successfully at site level');

    } catch (error) {
        console.error('[Themes] Failed to apply theme:', error);
    }
}

/**
 * Reorder site node keys so 'properties' appears before components.
 * This ensures YAML anchors in properties.theme are defined before aliases.
 * @param {Map} siteNode - YAML Map node for the site component
 */
function reorderSiteKeys(siteNode) {
    if (!YAML.isMap(siteNode)) return;
    const items = siteNode.items;
    const propsIdx = items.findIndex(p =>
        YAML.isPair(p) && YAML.isScalar(p.key) && p.key.value === 'properties'
    );
    if (propsIdx < 0) return;

    // Find insert position: after 'name' and 'id', before everything else
    let insertAfter = -1;
    for (let i = 0; i < items.length; i++) {
        if (YAML.isPair(items[i]) && YAML.isScalar(items[i].key)) {
            const k = items[i].key.value;
            if (k === 'name' || k === 'id') insertAfter = i;
        }
    }
    const insertIdx = insertAfter + 1;
    if (propsIdx > insertIdx) {
        const [propsPair] = items.splice(propsIdx, 1);
        items.splice(insertIdx, 0, propsPair);
    }
}

/**
 * Set an anchor on a scalar value within a map node
 * @param {Map} mapNode - YAML Map node
 * @param {string} key - Key to find
 * @param {string} anchorName - Name for the anchor
 */
function setAnchorOnScalar(mapNode, key, anchorName) {
    const scalar = mapNode.get(key, true);
    if (YAML.isScalar(scalar)) {
        scalar.anchor = anchorName;
    }
}

/**
 * Recursively walk components and replace matching color values with aliases
 * @param {Document} doc - YAML Document
 * @param {Seq} seqNode - Sequence node containing components
 * @param {Map} colorToAnchorNode - Map of normalized color -> anchor node
 */
function walkAndReplaceWithAliases(doc, seqNode, colorToAnchorNode) {
    if (!YAML.isSeq(seqNode)) return;

    for (const item of seqNode.items) {
        if (!YAML.isMap(item)) continue;

        // Check properties for color values
        const props = item.get('properties', true);
        if (YAML.isMap(props)) {
            // typography.color
            replaceColorWithAlias(doc, props, ['typography', 'color'], colorToAnchorNode);
            // appearance.background.color (skip if gradient type)
            const appearance = props.get('appearance', true);
            if (YAML.isMap(appearance)) {
                const background = appearance.get('background', true);
                if (YAML.isMap(background)) {
                    const bgType = background.get('type', true);
                    // Only replace if not a gradient
                    if (!YAML.isScalar(bgType) || bgType.value !== 'gradient') {
                        replaceColorWithAliasInMap(doc, background, 'color', colorToAnchorNode);
                    }
                }
                // appearance.border.color
                const border = appearance.get('border', true);
                if (YAML.isMap(border)) {
                    replaceColorWithAliasInMap(doc, border, 'color', colorToAnchorNode);
                }
            }
            // background.color (page-level)
            const bgDirect = props.get('background', true);
            if (YAML.isMap(bgDirect)) {
                replaceColorWithAliasInMap(doc, bgDirect, 'color', colorToAnchorNode);
            }
        }

        // Recurse into nested components
        const components = item.get('components', true);
        if (YAML.isSeq(components)) {
            walkAndReplaceWithAliases(doc, components, colorToAnchorNode);
        }

        // Handle columns (layout-row, columnsgrid)
        const columns = item.get('columns', true);
        if (YAML.isSeq(columns)) {
            for (const col of columns.items) {
                if (YAML.isMap(col)) {
                    const colComponents = col.get('components', true);
                    if (YAML.isSeq(colComponents)) {
                        walkAndReplaceWithAliases(doc, colComponents, colorToAnchorNode);
                    }
                }
            }
        }

        // Handle tabs, items (accordion), slides (carousel)
        for (const containerKey of ['tabs', 'items', 'slides']) {
            const container = item.get(containerKey, true);
            if (YAML.isSeq(container)) {
                for (const entry of container.items) {
                    if (YAML.isMap(entry)) {
                        const entryComponents = entry.get('components', true);
                        if (YAML.isSeq(entryComponents)) {
                            walkAndReplaceWithAliases(doc, entryComponents, colorToAnchorNode);
                        }
                    }
                }
            }
        }
    }
}

/**
 * Replace a color value at a nested path with an alias if it matches
 * @param {Document} doc - YAML Document
 * @param {Map} startNode - Starting map node
 * @param {Array} path - Path segments to navigate
 * @param {Map} colorToAnchorNode - Color to anchor node map
 */
function replaceColorWithAlias(doc, startNode, path, colorToAnchorNode) {
    let current = startNode;

    // Navigate to parent of target
    for (let i = 0; i < path.length - 1; i++) {
        current = current.get(path[i], true);
        if (!YAML.isMap(current)) return;
    }

    // Replace at final key
    replaceColorWithAliasInMap(doc, current, path[path.length - 1], colorToAnchorNode);
}

/**
 * Replace a color value in a map with an alias if it matches
 * @param {Document} doc - YAML Document
 * @param {Map} mapNode - Map node containing the color
 * @param {string} key - Key of the color value
 * @param {Map} colorToAnchorNode - Color to anchor node map
 */
function replaceColorWithAliasInMap(doc, mapNode, key, colorToAnchorNode) {
    if (!YAML.isMap(mapNode)) return;

    const colorScalar = mapNode.get(key, true);
    if (!YAML.isScalar(colorScalar)) return;

    const colorValue = normalizeColor(String(colorScalar.value));
    const anchorNode = colorToAnchorNode.get(colorValue);

    if (anchorNode) {
        // Create alias to the anchored node
        const alias = doc.createAlias(anchorNode);
        mapNode.set(key, alias);
    }
}

/**
 * Normalize color value for comparison
 * Handles hex colors (3 or 6 digit), converts to lowercase
 */
function normalizeColor(color) {
    if (!color || typeof color !== 'string') return '';

    let normalized = color.trim().toLowerCase();

    // Expand 3-digit hex to 6-digit
    if (/^#[0-9a-f]{3}$/i.test(normalized)) {
        normalized = '#' + normalized[1] + normalized[1] + normalized[2] + normalized[2] + normalized[3] + normalized[3];
    }

    return normalized;
}
