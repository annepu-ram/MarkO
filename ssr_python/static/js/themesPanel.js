/**
 * Themes Panel - Manage page-level fonts and color themes
 * Uses native YAML anchors via eemeli/yaml Document API
 */

import { getYamlStructureFromEditor, updateYamlEditor } from './yamlUtils.js';
import { parseDocument, YAML } from './yamlWrapper.js';
import { renderPreview } from './ssr_app.js';
import { historyManager } from './historyManager.js';

// WCAG 2.1 Accessible Color Themes - organized by category
// All themes meet 4.5:1 contrast ratio for Primary (text) on Background
// Color Distribution: Background (60%), Primary (30% - TEXT), Secondary (10% - UI), Accent (CTAs only)
const COLOR_THEMES = [
    // === TIMELESS & CLASSIC ===
    { name: 'Warm Ivory', category: 'Classic', colors: { background: '#FDF8F0', primary: '#2D2420', secondary: '#E8DED0', accent: '#B8510D' }},
    { name: 'Slate Professional', category: 'Classic', colors: { background: '#E8EDF2', primary: '#1E3A5F', secondary: '#C5D4E3', accent: '#0052CC' }},
    { name: 'Champagne Luxe', category: 'Classic', colors: { background: '#F5F0E6', primary: '#1C1810', secondary: '#E0D8C8', accent: '#996515' }},
    { name: 'Bauhaus Primary', category: 'Classic', colors: { background: '#FFFBE6', primary: '#0D0D0D', secondary: '#F5E6B8', accent: '#DD0100' }},
    { name: 'Concrete Raw', category: 'Classic', colors: { background: '#E5E2DD', primary: '#1A1A1A', secondary: '#C8C4BB', accent: '#FF4D00' }},
    { name: 'Midnight Prestige', category: 'Classic', colors: { background: '#1A1A2E', primary: '#F5F5F5', secondary: '#2D2D45', accent: '#D4AF37' }},

    // === RETRO & NOSTALGIC ===
    { name: 'Atomic Cream', category: 'Retro', colors: { background: '#FFF5D6', primary: '#1A3A3A', secondary: '#E8DEB0', accent: '#008B8B' }},
    { name: 'Synthwave Dark', category: 'Retro', colors: { background: '#1A0A2E', primary: '#F5E6FA', secondary: '#2E1650', accent: '#FF00FF' }},
    { name: 'Grunge Ochre', category: 'Retro', colors: { background: '#DED5B8', primary: '#2C2416', secondary: '#C4B898', accent: '#8B0000' }},
    { name: 'Sepia Vintage', category: 'Retro', colors: { background: '#F5E6D3', primary: '#3D2B1F', secondary: '#E0CDB5', accent: '#8B4513' }},
    { name: 'Vaporwave Pink', category: 'Retro', colors: { background: '#FFD6E8', primary: '#2D1B4E', secondary: '#F0B8D4', accent: '#9B59B6' }},
    { name: 'Art Deco Noir', category: 'Retro', colors: { background: '#0F0F0F', primary: '#F5F0E6', secondary: '#2A2520', accent: '#D4AF37' }},
    { name: 'Pop Art Yellow', category: 'Retro', colors: { background: '#FFEB3B', primary: '#0D0D0D', secondary: '#FFD600', accent: '#FF0000' }},

    // === FUTURISTIC & TECH ===
    { name: 'Cyberpunk Neon', category: 'Tech', colors: { background: '#0D0A14', primary: '#F0E6FA', secondary: '#1E1428', accent: '#FF0080' }},
    { name: 'Solarpunk Leaf', category: 'Tech', colors: { background: '#E6F5E0', primary: '#1A3A1A', secondary: '#C8E8B8', accent: '#2E8B57' }},
    { name: 'Glass Azure', category: 'Tech', colors: { background: '#D6EBF5', primary: '#1A365D', secondary: '#B0D4E8', accent: '#3182CE' }},
    { name: 'Soft Lavender', category: 'Tech', colors: { background: '#E8E0F0', primary: '#2D1B4E', secondary: '#D0C0E0', accent: '#6C63FF' }},
    { name: 'Terminal Green', category: 'Tech', colors: { background: '#0A1A0A', primary: '#E8FCE8', secondary: '#142814', accent: '#00FF41' }},
    { name: 'Nebula Purple', category: 'Tech', colors: { background: '#14101E', primary: '#E8E0F8', secondary: '#251D38', accent: '#9D4EDD' }},
    { name: 'Holographic', category: 'Tech', colors: { background: '#E6F0FA', primary: '#1A2035', secondary: '#C8D8F0', accent: '#EC4899' }},

    // === NATURE & ORGANIC ===
    { name: 'Sage Garden', category: 'Nature', colors: { background: '#E0EBD8', primary: '#1A3318', secondary: '#C0D8B0', accent: '#228B22' }},
    { name: 'Terracotta', category: 'Nature', colors: { background: '#F5E0D0', primary: '#3D2B1F', secondary: '#E8C8B0', accent: '#C2703B' }},
    { name: 'Deep Ocean', category: 'Nature', colors: { background: '#D0E8F0', primary: '#1A3A4A', secondary: '#A8D0E0', accent: '#0077B6' }},
    { name: 'Moss Forest', category: 'Nature', colors: { background: '#D8E8D0', primary: '#1E3E1E', secondary: '#B8D0A8', accent: '#2E7D32' }},
    { name: 'Desert Sunset', category: 'Nature', colors: { background: '#FFE8D6', primary: '#4A2C17', secondary: '#F5D0B0', accent: '#D2691E' }},
    { name: 'Coral Reef', category: 'Nature', colors: { background: '#FFE6E0', primary: '#2D1A1A', secondary: '#F5C8C0', accent: '#FF6B35' }},
    { name: 'Lavender Field', category: 'Nature', colors: { background: '#E8E0F0', primary: '#2D2040', secondary: '#D0C0E0', accent: '#7C3AED' }},

    // === EMOTIONAL MOODS ===
    { name: 'Cinema Noir', category: 'Mood', colors: { background: '#0F0F0F', primary: '#F5F5F5', secondary: '#1F1F1F', accent: '#DC143C' }},
    { name: 'Bubblegum', category: 'Mood', colors: { background: '#FFD6E6', primary: '#4A1942', secondary: '#F5B0D0', accent: '#FF1493' }},
    { name: 'Fire & Ice', category: 'Mood', colors: { background: '#1A0A0A', primary: '#E8F0FA', secondary: '#2D1414', accent: '#FF4500' }},
    { name: 'Zen Stone', category: 'Mood', colors: { background: '#E8E6E0', primary: '#3D3D35', secondary: '#D0CEC5', accent: '#708090' }},
    { name: 'Ivy League', category: 'Mood', colors: { background: '#E6EBE0', primary: '#1A2E28', secondary: '#C8D8C0', accent: '#00356B' }},
    { name: 'Gothic Rose', category: 'Mood', colors: { background: '#1A0F0F', primary: '#F5E6E6', secondary: '#2D1818', accent: '#C41E3A' }},
    { name: 'Hygge Warm', category: 'Mood', colors: { background: '#FFF5E6', primary: '#2D3436', secondary: '#F0E0C8', accent: '#D35400' }},
    { name: 'Neon Street', category: 'Mood', colors: { background: '#1A1A1A', primary: '#F5F5F5', secondary: '#2D2D2D', accent: '#FFEA00' }},
    { name: 'Digital Realm', category: 'Mood', colors: { background: '#0A0A1A', primary: '#E6E6FF', secondary: '#14142D', accent: '#00FFFF' }},
];

// Shared theme color config — single source of truth for color keys, anchor names, and labels
export const THEME_COLOR_CONFIG = [
    { key: 'primary', anchor: 'color-primary', label: 'Primary' },
    { key: 'secondary', anchor: 'color-secondary', label: 'Secondary' },
    { key: 'accent', anchor: 'color-accent', label: 'Accent' },
    { key: 'background', anchor: 'color-background', label: 'Background' },
];

// Font options
const FONT_OPTIONS = [
    { value: 'Georgia, serif', label: 'Georgia' },
    { value: '"Times New Roman", serif', label: 'Times New Roman' },
    { value: 'Palatino, serif', label: 'Palatino' },
    { value: 'Arial, sans-serif', label: 'Arial' },
    { value: 'Helvetica, sans-serif', label: 'Helvetica' },
    { value: 'Verdana, sans-serif', label: 'Verdana' },
    { value: '"Trebuchet MS", sans-serif', label: 'Trebuchet MS' },
    { value: '"Courier New", monospace', label: 'Courier New' },
    { value: 'system-ui, sans-serif', label: 'System UI' },
];

// Current selected state
let selectedThemeIndex = 0;
let selectedTheme = { ...COLOR_THEMES[0].colors };
let selectedFonts = {
    headingMain: 'Georgia, serif',
    headingLevel2: 'Helvetica, sans-serif',
    content: 'Arial, sans-serif'
};

/**
 * Get current theme from page component if it exists
 */
export function getCurrentTheme() {
    const structure = getYamlStructureFromEditor();
    if (!structure || !Array.isArray(structure) || structure.length === 0) {
        return null;
    }

    const page = structure[0];
    if (page && page.properties && page.properties.theme) {
        return page.properties.theme;
    }
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
 * Render font dropdown rows
 */
function renderFontDropdowns() {
    const fonts = [
        { key: 'headingMain', label: 'Main Headings' },
        { key: 'headingLevel2', label: 'Sub Headings' },
        { key: 'content', label: 'Content' }
    ];

    return fonts.map(({ key, label }) => `
        <div class="theme-font-row">
            <span class="theme-font-label">${label}</span>
            <select class="theme-font-select" data-font-key="${key}">
                ${FONT_OPTIONS.map(opt => `
                    <option value="${opt.value}" ${selectedFonts[key] === opt.value ? 'selected' : ''}>
                        ${opt.label}
                    </option>
                `).join('')}
            </select>
        </div>
    `).join('');
}

/**
 * Render editable color swatches
 */
function renderEditableSwatches() {
    const colors = [
         { key: 'background', label: 'Bg' },
        { key: 'primary', label: 'Pri' },
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
 * Apply theme to YAML using native Document API with anchors and aliases
 * This is a clean implementation using eemeli/yaml's native anchor support
 */
export async function applyTheme() {
    console.log('[Themes] Applying theme with native YAML anchors...');

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

        // Get the page component (first item in array)
        const contents = doc.contents;
        if (!YAML.isSeq(contents) || contents.items.length === 0) {
            console.warn('[Themes] Invalid document structure - expected array');
            return;
        }

        const pageNode = contents.items[0];
        if (!YAML.isMap(pageNode)) {
            console.warn('[Themes] Page component is not a map');
            return;
        }

        // Get or create properties map
        let propsNode = pageNode.get('properties', true);
        if (!propsNode || !YAML.isMap(propsNode)) {
            propsNode = doc.createNode({});
            pageNode.set('properties', propsNode);
        }

        // Create theme structure with anchored values
        const themeData = {
            fonts: {
                headingMain: selectedFonts.headingMain,
                headingLevel2: selectedFonts.headingLevel2,
                content: selectedFonts.content
            },
            colors: {
                primary: selectedTheme.primary,
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
            setAnchorOnScalar(fontsNode, 'headingMain', 'font-heading-main');
            setAnchorOnScalar(fontsNode, 'headingLevel2', 'font-heading-level2');
            setAnchorOnScalar(fontsNode, 'content', 'font-content');
        }

        // Set theme on page properties
        propsNode.set('theme', themeNode);

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

        // Walk components and replace matching colors with aliases
        const componentsNode = pageNode.get('components', true);
        if (YAML.isSeq(componentsNode)) {
            walkAndReplaceWithAliases(doc, componentsNode, colorToAnchorNode);
        }

        // Generate YAML string (anchors and aliases preserved automatically!)
        const yamlText = String(doc);

        // Update editor
        updateYamlEditor(yamlText);

        // Push to history
        historyManager.push(yamlText);

        // Trigger render with the new YAML content
        await renderPreview(yamlText);

        console.log('[Themes] Theme applied successfully with native YAML anchors');

    } catch (error) {
        console.error('[Themes] Failed to apply theme:', error);
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
