import { registerComponentPath, resetComponentPathMap, queueComponentInitialization, consumeComponentInitializationQueue } from '../core/state.js';
import { deepClone, deepMerge, getNestedValue, deleteNestedValue } from '../utils/object.js';
import { toRem, resolveSpacingValue, resolveLetterSpacing, resolveLineHeight, resolveTypographySize, resolveFontWeight } from '../utils/styles.js';
import { escapeHtml, escapeHtmlWithLineBreaks } from '../utils/strings.js';

// --- UTILITY FUNCTIONS ---
// =================================================================================================

/**
 * @function hexToRgba
 * @description Converts hex color (#RRGGBB) and transparency percentage (0-100) to rgba format.
 * @param {string} hex - Hex color string (e.g., '#3b82f6')
 * @param {number} transparencyPercent - Transparency percentage from 0 (transparent) to 100 (opaque)
 * @returns {string} RGBA color string (e.g., 'rgba(59,130,246,0.5)')
 */
function hexToRgba(hex, transparencyPercent) {
    // Remove # if present
    hex = hex.replace('#', '');

    // Convert hex to RGB
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    // Convert transparency percent (0-100) to alpha (0-1)
    const alpha = transparencyPercent / 100;

    return `rgba(${r},${g},${b},${alpha})`;
}

// --- COMPONENT RENDERING ---
// =================================================================================================

const FLEX_ALIGN_MAP = {
    start: 'flex-start',
    center: 'center',
    end: 'flex-end',
    stretch: 'stretch',
};

const TEXT_COMPONENTS_WITH_WIDTH_MODE = new Set(['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote', 'image', 'gif']);
const WIDTH_MODE_RULES = {
    fit: {
        component: 'width: auto;',
        flex: ['width: auto;', 'flex: 0 1 auto;'],
    },
    '25': {
        component: 'width: 25%;',
        flex: ['width: 25%;', 'flex: 0 1 25%;', 'max-width: 25%;'],
    },
    '50': {
        component: 'width: 50%;',
        flex: ['width: 50%;', 'flex: 0 1 50%;', 'max-width: 50%;'],
    },
    '75': {
        component: 'width: 75%;',
        flex: ['width: 75%;', 'flex: 0 1 75%;', 'max-width: 75%;'],
    },
    stretch: {
        component: 'width: 100%;',
        flex: ['width: 100%;', 'flex: 1 1 100%;', 'max-width: 100%;'],
    },
};

function getWidthModeRule(mode) {
    return WIDTH_MODE_RULES[mode] || WIDTH_MODE_RULES.stretch;
}


const BORDER_RADIUS_MAP = {
    none: '0',
    sm: '0.4rem',
    md: '0.8rem',
    lg: '1.6rem',
    pill: '9999px',
};
const canUseSpacingValue = (value) => value !== null && value !== undefined && value !== 'undefined' && value !== '';


function buildStyleString(parts = []) {
    return parts
        .filter(Boolean)
        .map(part => {
            const trimmed = part.trim();
            if (!trimmed) {
                return '';
            }
            return trimmed.endsWith(';') ? trimmed : `${trimmed};`;
        })
        .filter(Boolean)
        .join(' ');
}

function normalizeDimensionValue(value) {
    if (value === undefined || value === null || value === '') {
        return null;
    }
    if (typeof value === 'number') {
        return `${value}px`;
    }
    if (typeof value === 'string') {
        const trimmed = value.trim();
        if (!trimmed) {
            return null;
        }
        const numeric = parseFloat(trimmed);
        if (!Number.isNaN(numeric) && `${numeric}` === trimmed) {
            return `${numeric}px`;
        }
        return trimmed;
    }
    return null;
}

function mapFlexAlign(value) {
    return FLEX_ALIGN_MAP[value] || value;
}

function resolveBorderRadiusToken(token) {
    if (token === undefined || token === null || token === '') {
        return null;
    }
    if (BORDER_RADIUS_MAP[token] !== undefined) {
        return BORDER_RADIUS_MAP[token];
    }
    if (typeof token === 'number') {
        return `${token}px`;
    }
    const trimmed = String(token).trim();
    if (!trimmed) {
        return null;
    }
    if (/^d+(?:.d+)?$/.test(trimmed)) {
        return `${trimmed}px`;
    }
    return trimmed;
}

const getAlignmentClass = (alignment) => {
    switch (alignment) {
        case 'left':
            return 'titlebar-left';
        case 'center':
            return 'titlebar-center';
        case 'right':
            return 'titlebar-right';
        default:
            return ''; // Default or no alignment class
    }
};
/**
 * Renders the entire YAML structure into HTML.
 * @param {Array} structure The YAML structure.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {{html: string}} The rendered HTML.
 */
export function renderYamlStructure(structure, mode = 'preview') {
    if (mode === 'preview') {
        resetComponentPathMap();
    }
    if (!structure || !Array.isArray(structure) || structure.length !== 1 || structure[0].name !== 'page') {
        return {
            html: `<div style="text-align: center; color: #6b7280; padding: 5rem;">
                <h3>Your website must start with a single 'page' component at the root.</h3>
                <p>
- name: page<br>
&nbsp;&nbsp;properties:<br>
&nbsp;&nbsp;&nbsp;&nbsp;backgroundColor: '#ffffff'<br>
&nbsp;&nbsp;components:<br>
&nbsp;&nbsp;&nbsp;&nbsp;- name: heading<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;properties:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;level: 2<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;text: 'Welcome!'
                </p>
            </div>`
        };
    }
    const pageComponent = structure[0];
    const html = renderComponent(pageComponent, [0], mode);
    return {
        html
    };
}
/**
 * Renders a list of components into HTML.
 * @param {Array} components The list of components to render.
 * @param {Array} basePath The base path for the components.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML.
 */
export function renderComponentsList(components, basePath, mode) {
    let html = '';
    
    components.forEach((component, index) => {
        const componentPath = [...basePath, index];
        html += renderComponent(component, componentPath, mode);
    });
    return html;
}

function getComponentDepth(path = []) {
    if (!Array.isArray(path) || path.length === 0) {
        return 0;
    }
    const numericSegments = path.filter(segment => typeof segment === 'number');
    if (numericSegments.length === 0) {
        return 0;
    }
    return Math.max(numericSegments.length - 1, 0);
}

function wrapComponentWithChrome(componentId, label, contentHTML, depth = 0) {
    const safeLabel = escapeHtml(label || 'component');

    // Chrome elements to inject as first children
    const chromeHTML = `<span class="chrome-label">${safeLabel}</span><button type="button" class="chrome-delete" data-component-id="${componentId}" aria-label="Delete ${safeLabel}">&#10006;</button>`;

    // Inject chrome into component HTML (no wrapper needed!)
    return injectChromeIntoComponent(contentHTML, chromeHTML, componentId);
}

function injectChromeIntoComponent(componentHTML, chromeHTML, componentId) {
    // Find opening tag (e.g., <h2>, <p>, <section>, etc.)
    const match = componentHTML.match(/^(<[a-zA-Z][a-zA-Z0-9]*\s*[^>]*>)/);

    if (!match) {
        // Fallback: wrap in div if no tag found (e.g., for self-closing tags)
        return `<div class="chrome-target" data-component-id="${componentId}" style="position: relative;">${chromeHTML}${componentHTML}</div>`;
    }

    const openingTag = match[1];
    const restOfHTML = componentHTML.slice(openingTag.length);

    // Add chrome-target class to opening tag
    let modifiedTag = openingTag;
    if (modifiedTag.includes('class="')) {
        // Add to existing class
        modifiedTag = modifiedTag.replace(/class="([^"]*)"/, 'class="$1 chrome-target"');
    } else {
        // Add new class attribute before closing >
        modifiedTag = modifiedTag.replace(/>$/, ' class="chrome-target">');
    }

    // Add data-component-id attribute
    modifiedTag = modifiedTag.replace(/>$/, ` data-component-id="${componentId}">`);

    // Ensure position: relative in style
    if (modifiedTag.includes('style="')) {
        // Add to existing style - check if it already has position
        if (modifiedTag.includes('position:')) {
            // Already has position, don't override
            modifiedTag = modifiedTag.replace(/style="([^"]*)"/, 'style="$1"');
        } else {
            // Add position: relative
            modifiedTag = modifiedTag.replace(/style="([^"]*)"/, 'style="$1 position: relative;"');
        }
    } else {
        // Add new style attribute
        modifiedTag = modifiedTag.replace(/>$/, ' style="position: relative;">');
    }

    // Inject chrome as first children
    return modifiedTag + chromeHTML + restOfHTML;
}

/**
 * @function wrapFormElementWithChrome
 * @description Wraps form elements (button, input, textarea, etc.) in a container with chrome UI.
 * For form elements, we need a wrapper div because pseudo-elements don't work well directly on form controls.
 * @param {string} componentId - The unique component ID
 * @param {string} label - The label for the chrome UI
 * @param {string} formElementHTML - The HTML of the form element (e.g., <button>Click</button>)
 * @returns {string} The wrapped HTML with chrome container
 */
function wrapFormElementWithChrome(componentId, label, formElementHTML) {
    const safeLabel = escapeHtml(label || 'component');

    // Chrome elements to inject as first children of wrapper
    const chromeHTML = `<span class="chrome-label">${safeLabel}</span><button type="button" class="chrome-delete" data-component-id="${componentId}" aria-label="Delete ${safeLabel}">&#10006;</button>`;

    // Wrap form element in a container div with chrome styling
    // Use inline-flex to contain the form element and allow chrome UI positioning
    // padding: 0.4rem provides visual spacing around the form element
    return `<div class="chrome-target form-element-wrapper" data-component-id="${componentId}" style="display: inline-flex; align-items: center; padding: 0.4rem; position: relative; box-sizing: border-box; cursor: pointer; overflow: hidden;">${chromeHTML}${formElementHTML}</div>`;
}

/**
 * @function wrapFormElementForExport
 * @description Wraps form elements in export mode without chrome UI.
 * The wrapper div maintains consistent flex layout behavior between preview and export.
 * @param {string} formElementHTML - The HTML of the form element
 * @returns {string} The wrapped HTML without chrome UI
 */
function wrapFormElementForExport(formElementHTML) {
    // Same wrapper structure as preview but without chrome label/delete button
    // This ensures consistent width behavior in flex containers
    return `<div class="form-element-wrapper" style="display: inline-flex; align-items: center; padding: 0.4rem; position: relative; box-sizing: border-box; overflow: hidden;">${formElementHTML}</div>`;
}

/**
 * Renders a single component into HTML.
 * @param {object} component The component to render.
 * @param {Array} path The path to the component in the YAML structure.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML.
 */
export function renderComponent(component, path, mode) {
    if (!component || !component.name) return '';
    const { name, properties = {} } = component;
    switch (name) {
        case 'page':
            return renderPageComponent(component, path, mode);
        case 'layout-row':
            return renderLayoutContainer(component, path, mode, { orientation: 'row', label: 'layout-row' });
        case 'layout-column':
            return renderLayoutContainer(component, path, mode, { orientation: 'column', label: 'layout-column' });
        case 'section': {
            const legacyOrientation = (getNestedValue(component.properties || {}, ['layout', 'direction']) || 'column') === 'row' ? 'row' : 'column';
            return renderLayoutContainer(component, path, mode, { orientation: legacyOrientation, label: 'section' });
        }
        case 'stack':
            return renderLayoutContainer(component, path, mode, { orientation: 'column', label: 'stack' });
        case 'columnsgrid':
            return renderColumnsGrid(component, path, mode);
        case 'accordion':
            return renderAccordion(component, path, mode);
        case 'tabs':
            return renderTabs(component, path, mode);
        case 'form':
            return renderFormComponent(component, path, mode);
        case 'carousel':
            return renderCarousel(component, path, mode);
        default:
            return renderSimpleComponent(component, path, mode);
    }
}
/**
 * @function renderCarousel
/**
 * @description Renders a carousel component.
 * @param {object} component - The carousel component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the carousel.
 * @calledBy {renderComponent}
 * @calls {generateRemainingStyles|renderComponentsList|registerComponentPath|registerComponentForInitialization}
 */
function renderCarousel(component, path, mode) {
    const { properties = {}, slides = [] } = component;
    const { height } = properties;
    const styles = generateRemainingStyles(properties);
    const carouselId = `carousel_${path.join('_')}`;
    let slidesHTML = '';
    for (let i = 0; i < slides.length; i++) {
        const slideComponents = slides[i] ? slides[i].components || [] : [];
        const slidePath = [...path, 'slides', i, 'components'];
        const slideContent = renderComponentsList(slideComponents, slidePath, mode);
        slidesHTML += `<div class="carousel-slide">${slideContent}</div>`;
    }
    const contentHTML = `
        <div id="${carouselId}" class="carousel-container" style="${styles}">
            <div class="carousel-slides">
                ${slidesHTML}
            </div>
            <div class="carousel-controls">
                <button class="prev">&#10094;</button>
                <button class="next">&#10095;</button>
            </div>
            <div class="carousel-dots">
                ${slides.map((_, i) => `<span data-slide-to="${i}"></span>`).join('')}
            </div>
        </div>
    `;
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        registerComponentForInitialization('carousel', carouselId, properties);
        return wrapComponentWithChrome(componentId, 'carousel', contentHTML, getComponentDepth(path));
    }
    return contentHTML;
}
/**
 * @function renderFormComponent
 * @description Renders a form component.
 * @param {object} component - The form component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the form.
 * @calledBy {renderComponent}
 * @calls {renderComponentsList|generateRemainingStyles|registerComponentPath}
 */
function renderFormComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const componentsPath = [...path, 'components'];
    let contentHTML = renderComponentsList(components, componentsPath, mode);
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        if (components.length === 0) {
            contentHTML = '<div class="group-placeholder" style="text-align: center; color: #6b7280; padding: 5rem; border: 2px dashed #ccc;">Drop form elements here</div>';
        }
        const styles = generateRemainingStyles(properties);
        const formHTML = `<form style="${styles}">${contentHTML}</form>`;
        return wrapComponentWithChrome(componentId, 'form', formHTML, getComponentDepth(path));
    }
    // For export mode
    const styles = generateRemainingStyles(properties);
    return `<form style="${styles}">${contentHTML}</form>`;
}
/**
 * @function renderPageComponent
 * @description Renders the main page component.
 * @param {object} component - The page component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the page.
 * @calledBy {renderComponent}
 * @calls {renderComponentsList|generateRemainingStyles|registerComponentPath}
 */
function renderPageComponent(component, path, mode) {
    const {
        properties = {},
        components = []
    } = component;
    const componentsPath = [...path, 'components'];
    let contentHTML = renderComponentsList(components, componentsPath, mode);
    const styles = generateRemainingStyles(properties);

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        if (components.length === 0) {
            contentHTML = '<div class="page-placeholder" style="text-align: center; color: #6b7280; padding: 5rem; border: 2px dashed #ccc;">Click components from the sidebar to get started</div>';
        }

        // Page component: NO delete button, uses pseudo-element for label via chrome-target-page class
        const pageHTML = `<div class="chrome-target-page" data-component-id="${componentId}" style="${styles} display: flex; flex-direction: column; width: 100%; position: relative;">${contentHTML}</div>`;
        return pageHTML;
    }

    // Export mode - also use flex container for parity
    return `<div style="${styles} width: 100%; display: flex; flex-direction: column;">${contentHTML}</div>`;
}



function renderLayoutContainer(component, path, mode, options = {}) {
    const {
        orientation = 'column',
        label = 'layout',
    } = options;

    const props = component.properties || {};
    const components = Array.isArray(component.components) ? component.components : [];

    const layoutGroup = props.layout || {};
    const tagCandidate = (layoutGroup.tag || 'section').toString().trim();
    const tag = /^[a-zA-Z][a-zA-Z0-9-]*$/.test(tagCandidate) ? tagCandidate : 'section';

    const defaultAlign = orientation === 'row' ? 'center' : 'stretch';
    const alignValue = layoutGroup.align || defaultAlign;

    const gapToken = layoutGroup.gap ?? getNestedValue(props, ['spacing', 'gap']);
    const resolvedGap = resolveSpacingValue(gapToken);

    const spacingGroup = props.spacing || {};
    const paddingBlockToken = spacingGroup.paddingBlock;
    const paddingInlineToken = spacingGroup.paddingInline;
    const paddingTopToken = getNestedValue(spacingGroup, ['padding', 'top']);
    const paddingBottomToken = getNestedValue(spacingGroup, ['padding', 'bottom']);
    const paddingLeftToken = getNestedValue(spacingGroup, ['padding', 'left']);
    const paddingRightToken = getNestedValue(spacingGroup, ['padding', 'right']);

    const marginBlockToken = spacingGroup.marginBlock;
    const marginInlineToken = spacingGroup.marginInline;
    const marginTopToken = getNestedValue(spacingGroup, ['margin', 'top']);
    const marginBottomToken = getNestedValue(spacingGroup, ['margin', 'bottom']);
    const marginLeftToken = getNestedValue(spacingGroup, ['margin', 'left']);
    const marginRightToken = getNestedValue(spacingGroup, ['margin', 'right']);

    const sizeGroup = props.size || {};
    const minWidthToken = sizeGroup.minWidth ?? layoutGroup.minWidth;
    const maxWidthToken = sizeGroup.maxWidth ?? layoutGroup.maxWidth;
    const minHeightToken = sizeGroup.minHeight ?? layoutGroup.minHeight;
    const maxHeightToken = sizeGroup.maxHeight ?? layoutGroup.maxHeight;
    const explicitWidthToken = layoutGroup.width;

    const outerStyleParts = ['width: 100%;', 'position: relative;', 'box-sizing: border-box;'];

    const applyPaddingPair = (valueToken, fallbackA, fallbackB, propertyA, propertyB) => {
        if (valueToken !== undefined) {
            const resolved = resolveSpacingValue(valueToken);
            if (canUseSpacingValue(resolved) && resolved !== 'auto') {
                outerStyleParts.push(`${propertyA}: ${resolved};`, `${propertyB}: ${resolved};`);
            }
        } else {
            const first = resolveSpacingValue(fallbackA);
            const second = resolveSpacingValue(fallbackB);
            if (canUseSpacingValue(first) && first !== 'auto') {
                outerStyleParts.push(`${propertyA}: ${first};`);
            }
            if (canUseSpacingValue(second) && second !== 'auto') {
                outerStyleParts.push(`${propertyB}: ${second};`);
            }
        }
    };

    applyPaddingPair(paddingBlockToken, paddingTopToken, paddingBottomToken, 'padding-top', 'padding-bottom');
    applyPaddingPair(paddingInlineToken, paddingLeftToken, paddingRightToken, 'padding-left', 'padding-right');

    let inlineMarginSpecified = false;

    if (marginBlockToken !== undefined) {
        const resolved = resolveSpacingValue(marginBlockToken);
        if (canUseSpacingValue(resolved)) {
            outerStyleParts.push(`margin-top: ${resolved};`, `margin-bottom: ${resolved};`);
        }
    } else {
        const top = resolveSpacingValue(marginTopToken);
        const bottom = resolveSpacingValue(marginBottomToken);
        if (canUseSpacingValue(top)) {
            outerStyleParts.push(`margin-top: ${top};`);
        }
        if (canUseSpacingValue(bottom)) {
            outerStyleParts.push(`margin-bottom: ${bottom};`);
        }
    }

    if (marginInlineToken !== undefined) {
        const resolved = resolveSpacingValue(marginInlineToken);
        if (canUseSpacingValue(resolved)) {
            inlineMarginSpecified = true;
            outerStyleParts.push(`margin-left: ${resolved};`, `margin-right: ${resolved};`);
        }
    } else {
        const left = resolveSpacingValue(marginLeftToken);
        const right = resolveSpacingValue(marginRightToken);
        if (canUseSpacingValue(left)) {
            inlineMarginSpecified = true;
            outerStyleParts.push(`margin-left: ${left};`);
        }
        if (canUseSpacingValue(right)) {
            inlineMarginSpecified = true;
            outerStyleParts.push(`margin-right: ${right};`);
        }
    }

    const normalizeSizeValue = value => {
        if (value === undefined || value === null || value === '') {
            return null;
        }
        const normalized = normalizeDimensionValue(value);
        if (!normalized || normalized === 'auto') {
            return normalized === 'auto' ? 'auto' : null;
        }
        return normalized;
    };

    const minWidthValue = normalizeSizeValue(minWidthToken);
    if (minWidthValue && minWidthValue !== 'auto') {
        outerStyleParts.push(`min-width: ${minWidthValue};`);
    }

    const maxWidthValue = normalizeSizeValue(maxWidthToken);
    if (maxWidthValue && maxWidthValue !== 'auto') {
        outerStyleParts.push(`max-width: ${maxWidthValue};`);
        if (!inlineMarginSpecified) {
            outerStyleParts.push('margin-left: auto;', 'margin-right: auto;');
            inlineMarginSpecified = true;
        }
    }

    const minHeightValue = normalizeSizeValue(minHeightToken);
    if (minHeightValue && minHeightValue !== 'auto') {
        outerStyleParts.push(`min-height: ${minHeightValue};`);
    }

    const maxHeightValue = normalizeSizeValue(maxHeightToken);
    if (maxHeightValue && maxHeightValue !== 'auto') {
        outerStyleParts.push(`max-height: ${maxHeightValue};`);
    }

    const explicitWidthValue = normalizeSizeValue(explicitWidthToken);
    if (explicitWidthValue && explicitWidthValue !== 'auto') {
        outerStyleParts.push(`width: ${explicitWidthValue};`);
    }

    const backgroundGroup = props.background || {};
    if (backgroundGroup.color) {
        outerStyleParts.push(`background-color: ${backgroundGroup.color};`);
    }
    const backgroundImage = (backgroundGroup.image || '').toString().trim();
    if (backgroundImage) {
        const safeUrl = backgroundImage.replace(/"/g, '"');
        outerStyleParts.push(`background-image: url("${safeUrl}");`, 'background-size: cover;', 'background-repeat: no-repeat;', 'background-position: center;');
    }

    const borderGroup = getNestedValue(props, ['appearance', 'border']) || props.border || {};
    const borderWidthRaw = borderGroup.width;
    const borderStyleValue = borderGroup.style || 'none';
    const borderColorValue = borderGroup.color || 'transparent';
    const borderWidthValue = borderWidthRaw !== undefined ? normalizeDimensionValue(borderWidthRaw) : null;
    const borderWidthNumber = borderWidthValue ? parseFloat(borderWidthValue) : 0;
    if (borderStyleValue === 'none' || !borderWidthValue || Number.isNaN(borderWidthNumber) || borderWidthNumber === 0) {
        outerStyleParts.push('border: none;');
    } else {
        outerStyleParts.push(`border: ${borderWidthValue} ${borderStyleValue} ${borderColorValue};`);
    }

    const radiusToken = getNestedValue(props, ['appearance', 'radius']) ?? getNestedValue(props, ['border', 'radius']);
    const radiusValue = resolveBorderRadiusToken(radiusToken);
    if (radiusValue) {
        outerStyleParts.push(`border-radius: ${radiusValue};`);
    }

    const shadowValueRaw = getNestedValue(props, ['appearance', 'shadow']);
    const shadowValue = shadowValueRaw && shadowValueRaw.toString().trim();
    if (shadowValue && shadowValue.toLowerCase() !== 'none') {
        outerStyleParts.push(`box-shadow: ${shadowValue};`);
    }

    const textColor = getNestedValue(props, ['typography', 'color']);
    if (textColor) {
        outerStyleParts.push(`color: ${textColor};`);
    }

    const contentStyleParts = ['display: flex;', `flex-direction: ${orientation};`];
    if (resolvedGap && resolvedGap !== 'auto') {
        contentStyleParts.push(`gap: ${resolvedGap};`);
    }
    if (alignValue) {
        contentStyleParts.push(`align-items: ${mapFlexAlign(alignValue)};`);
    }
    // Default to nowrap - users can explicitly enable wrapping via layout.wrap property
    let flexWrapValue = 'nowrap';
    const wrapOverride = layoutGroup.wrap;
    if (wrapOverride !== undefined && wrapOverride !== null && wrapOverride !== '') {
        flexWrapValue = wrapOverride === true ? 'wrap' : String(wrapOverride);
    }
    if (flexWrapValue) {
        contentStyleParts.push(`flex-wrap: ${flexWrapValue};`);
    }

    const componentsPath = [...path, 'components'];
    const innerHTML = renderComponentsList(components, componentsPath, mode);

    const baseClass = orientation === 'row' ? 'layout-row' : 'layout-column';
    const outerStyleAttr = buildStyleString(outerStyleParts);
    const innerStyleAttr = buildStyleString(contentStyleParts);

    const contentWrapper = innerStyleAttr
        ? `<div class="${baseClass}__content" style="${innerStyleAttr}">${innerHTML}</div>`
        : `<div class="${baseClass}__content">${innerHTML}</div>`;

    const layoutMarkup = `<${tag} class="${baseClass}" style="${outerStyleAttr}">
            ${contentWrapper}
        </${tag}>`;

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        const depth = getComponentDepth(path);
        return wrapComponentWithChrome(componentId, label, layoutMarkup, depth);
    }

    return layoutMarkup;
}
/**
 * Renders a simple component.
 * @param {object} component The component to render.
 * @param {Array} path The path to the component in the YAML structure.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML.
 */
export function renderSimpleComponent(component, path, mode) {
    const { name, properties = {}, components = [] } = component;
    const styles = generateRemainingStyles(properties, name);
    let componentHTML = generateComponentInnerHTML(name, properties, '', styles, mode);

    // Handle nested components for image and gif (for overlays/captions)
    if ((name === 'image' || name === 'gif') && components.length > 0) {
        const componentsPath = [...path, 'components'];
        const nestedHTML = renderComponentsList(components, componentsPath, mode);
        // Inject nested components before closing div
        componentHTML = componentHTML.replace('</div>', `<div class="image-nested-components">${nestedHTML}</div></div>`);
    }

    // Form elements need special wrapper to maintain consistent flex layout behavior
    const formElements = ['button', 'input', 'textarea', 'dropdown', 'checkbox', 'radio'];
    if (formElements.includes(name)) {
        if (mode === 'preview') {
            const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            registerComponentPath(componentId, path);
            // Preview mode: wrap with chrome UI (label + delete button)
            return wrapFormElementWithChrome(componentId, name, componentHTML);
        } else {
            // Export mode: wrap without chrome UI for consistent width behavior
            return wrapFormElementForExport(componentHTML);
        }
    }

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        if (name === 'titlebar') {
            const idMatch = componentHTML.match(/id="([^"]+)"/);
            if (idMatch && idMatch[1]) {
                registerComponentForInitialization('titlebar', idMatch[1], properties);
            }
        }
        const depth = getComponentDepth(path);

        // CHANGE: No wrapper styles needed - component gets all styles directly
        // Just inject chrome into component HTML
        return wrapComponentWithChrome(componentId, name, componentHTML, depth);
    }

    return componentHTML;
}
/**
 * @function renderColumnsGrid
 * @description Renders a columns grid component.
 * @param {object} component - The columns grid component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the columns grid.
 * @calledBy {renderComponent}
 * @calls {renderComponentsList|registerComponentPath}
 */
function renderColumnsGrid(component, path, mode) {
    const { properties = {}, columns = [] } = component;
    const columnCount = parseInt(getNestedValue(properties, ['layout', 'columns'])) || 2;
    const gap = getNestedValue(properties, ['layout', 'gap']);

    // Resolve gap spacing
    const gapValue = gap ? resolveSpacingValue(gap) : '1rem';

    // Calculate column width accounting for gap
    // Formula: (100% - (gap × (n-1))) / n
    // This ensures columns + gaps = 100%
    const columnWidth = `calc((100% - (${gapValue} * ${columnCount - 1})) / ${columnCount})`;

    let contentHTML = `<div class="row" style="gap: ${gapValue};">`;

    for (let i = 0; i < columnCount; i++) {
        const columnComponents = columns[i] ? columns[i].components || [] : [];
        const columnPath = [...path, 'columns', i, 'components'];

        // Apply calculated width with flex properties for proper column sizing
        // Use calc() to account for gap spacing
        contentHTML += `<div class="col" style="position: relative; width: ${columnWidth}; flex: 0 0 ${columnWidth}; box-sizing: border-box;">`;

        if (mode === 'preview') {
            contentHTML += `<div class="column-label">Col ${i + 1}</div>`;
        }

        if (columnComponents.length > 0) {
            contentHTML += renderComponentsList(columnComponents, columnPath, mode);
        } else if (mode === 'preview') {
            contentHTML += '<div class="column-placeholder">Drop components here...</div>';
        }

        contentHTML += '</div>';
    }

    contentHTML += '</div>';
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return wrapComponentWithChrome(componentId, 'columnsgrid', contentHTML, getComponentDepth(path));
    }

    return contentHTML;
}
/**
 * @function renderAccordion
 * @description Renders an accordion component with simple title/content strings.
 * @param {object} component - The accordion component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the accordion.
 * @calledBy {renderComponent}
 * @calls {registerComponentPath}
 */
function renderAccordion(component, path, mode) {
    const { properties = {} } = component;
    const items = properties.items || [];
    const allowMultipleOpen = getNestedValue(properties, ['behavior', 'allowMultipleOpen']) ?? false;

    // Typography properties
    const titleSize = resolveTypographySize(getNestedValue(properties, ['typography', 'title', 'size'])) || resolveTypographySize('lg');
    const titleWeight = resolveFontWeight(getNestedValue(properties, ['typography', 'title', 'weight'])) || resolveFontWeight('semibold');
    const titleColor = getNestedValue(properties, ['typography', 'title', 'color']) || '#111827';
    const contentSize = resolveTypographySize(getNestedValue(properties, ['typography', 'content', 'size'])) || resolveTypographySize('md');
    const contentWeight = resolveFontWeight(getNestedValue(properties, ['typography', 'content', 'weight'])) || resolveFontWeight('regular');
    const contentColor = getNestedValue(properties, ['typography', 'content', 'color']) || '#374151';

    // Layout properties
    const widthMode = getNestedValue(properties, ['layout', 'widthMode']) || 'stretch';
    const widthRule = getWidthModeRule(widthMode);

    // Appearance properties
    const borderRadius = BORDER_RADIUS_MAP[getNestedValue(properties, ['appearance', 'radius'])] || BORDER_RADIUS_MAP.sm;
    const paddingBlock = resolveSpacingValue(getNestedValue(properties, ['appearance', 'padding', 'block'])) || resolveSpacingValue('sm');
    const paddingInline = resolveSpacingValue(getNestedValue(properties, ['appearance', 'padding', 'inline'])) || resolveSpacingValue('sm');

    // Shared border properties (applies to both title and content)
    const borderWidth = getNestedValue(properties, ['appearance', 'border', 'width']) ?? 1;
    const borderStyle = getNestedValue(properties, ['appearance', 'border', 'style']) || 'solid';
    const borderColor = getNestedValue(properties, ['appearance', 'border', 'color']) || '#d1d5db';
    const borderPosition = getNestedValue(properties, ['appearance', 'border', 'position']) || 'bottom';

    // Title background properties
    const titleBackgroundColor = getNestedValue(properties, ['appearance', 'titleBackground', 'color']) || '#f5f5f5';

    // Content background properties (NEW)
    const contentBackgroundColor = getNestedValue(properties, ['appearance', 'contentBackground', 'color']) || '#ffffff';
    const contentBackgroundTransparency = getNestedValue(properties, ['appearance', 'contentBackground', 'transparency']);
    let contentBgColor = contentBackgroundColor;
    if (contentBackgroundTransparency !== undefined && contentBackgroundColor.startsWith('#')) {
        contentBgColor = hexToRgba(contentBackgroundColor, contentBackgroundTransparency);
    }

    // Spacing properties
    const marginBlock = resolveSpacingValue(getNestedValue(properties, ['spacing', 'marginBlock'])) || resolveSpacingValue('md');
    const marginInline = resolveSpacingValue(getNestedValue(properties, ['spacing', 'marginInline'])) || resolveSpacingValue('none');

    // Fallback for empty accordion
    let accordionItems = items;
    if (items.length === 0) {
        accordionItems = [{ title: 'Click to expand', content: '' }];
    }

    const containerId = `accordion_container_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Build container styles (container should be transparent, background applies to items)
    const containerStyles = buildStyleString([
        widthRule.component,
        `border-radius: ${borderRadius};`,
        canUseSpacingValue(marginBlock) ? `margin-block: ${marginBlock};` : '',
        canUseSpacingValue(marginInline) ? `margin-inline: ${marginInline};` : '',
    ]);

    let accordionHTML = `<div id="${containerId}" class="accordion-container" data-allow-multiple="${allowMultipleOpen}" style="${containerStyles}">`;

    accordionItems.forEach((item, index) => {
        const itemId = `accordion_${containerId}_${index}`;
        const title = escapeHtml(item.title || `Item ${index + 1}`);

        // Only support simple string content
        const contentHTML = item.content ? escapeHtmlWithLineBreaks(item.content) : '';

        // Build item styles
        // Determine border style based on position (applies to both title and content)
        let borderStyleString = '';
        switch(borderPosition) {
            case 'top':
                borderStyleString = `border-top: ${borderWidth}px ${borderStyle} ${borderColor};`;
                break;
            case 'left':
                borderStyleString = `border-left: ${borderWidth}px ${borderStyle} ${borderColor};`;
                break;
            case 'right':
                borderStyleString = `border-right: ${borderWidth}px ${borderStyle} ${borderColor};`;
                break;
            case 'all':
                borderStyleString = `border: ${borderWidth}px ${borderStyle} ${borderColor};`;
                break;
            default: // 'bottom'
                borderStyleString = `border-bottom: ${borderWidth}px ${borderStyle} ${borderColor};`;
        }

        const summaryStyles = buildStyleString([
            `font-size: ${titleSize};`,
            `font-weight: ${titleWeight};`,
            `color: ${titleColor};`,
            `background-color: ${titleBackgroundColor};`,
            borderStyleString,
            canUseSpacingValue(paddingBlock) ? `padding-block: ${paddingBlock};` : '',
            canUseSpacingValue(paddingInline) ? `padding-inline: ${paddingInline};` : '',
            'cursor: pointer;',
            'transition: background-color 0.2s ease, border-color 0.2s ease;',
        ]);

        const contentStyles = buildStyleString([
            `font-size: ${contentSize};`,
            `font-weight: ${contentWeight};`,
            `color: ${contentColor};`,
            `background-color: ${contentBgColor};`,
            borderStyleString,
            canUseSpacingValue(paddingBlock) ? `padding-block: ${paddingBlock};` : '',
            canUseSpacingValue(paddingInline) ? `padding-inline: ${paddingInline};` : '',
        ]);

        accordionHTML += `
            <details class="accordion" data-accordion-id="${itemId}">
                <summary class="accordion-summary" style="${summaryStyles}">${title}</summary>
                <div class="card">
                    <div class="card-body" style="${contentStyles}">${contentHTML}</div>
                </div>
            </details>
        `;
    });

    accordionHTML += '</div>';

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        registerComponentForInitialization('accordion', containerId, { allowMultipleOpen });
        return wrapComponentWithChrome(componentId, 'accordion', accordionHTML, getComponentDepth(path));
    }

    return accordionHTML;
}
/**
 * @function renderTabs
 * @description Renders a tabs component.
 * @param {object} component - The tabs component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the tabs.
 * @calledBy {renderComponent}
 * @calls {renderComponentsList|registerComponentPath}
 */
function renderTabs(component, path, mode) {
    const { properties = {}, tabs = [] } = component;
    const tabsId = `tabs_${Math.random().toString(36).substr(2, 9)}`;

    // Read styling properties
    const widthMode = getNestedValue(properties, ['layout', 'widthMode']) || 'stretch';
    const widthRule = getWidthModeRule(widthMode);
    const orientation = getNestedValue(properties, ['layout', 'orientation']) || 'horizontal';

    // Typography
    const labelSize = resolveTypographySize(getNestedValue(properties, ['typography', 'label', 'size'])) || '1.6rem';
    const labelWeight = resolveFontWeight(getNestedValue(properties, ['typography', 'label', 'weight'])) || '600';
    const activeColor = getNestedValue(properties, ['typography', 'label', 'active', 'color']) || '#000000';
    const inactiveColor = getNestedValue(properties, ['typography', 'label', 'inactive', 'color']) || '#6b7280';

    // Appearance
    const activeBg = getNestedValue(properties, ['appearance', 'tab', 'background', 'active']) || '#ffffff';
    const inactiveBg = getNestedValue(properties, ['appearance', 'tab', 'background', 'inactive']) || '#f3f4f6';
    const tabBorderWidth = getNestedValue(properties, ['appearance', 'tab', 'border', 'width']) ?? 2;
    const borderPosition = getNestedValue(properties, ['appearance', 'tab', 'border', 'position']) || 'lower';
    const tabGap = resolveSpacingValue(getNestedValue(properties, ['appearance', 'tab', 'gap'])) || '0';

    const contentBg = getNestedValue(properties, ['appearance', 'content', 'background', 'color']) || '#ffffff';
    const contentTransparency = getNestedValue(properties, ['appearance', 'content', 'background', 'transparency']);

    // Handle content background transparency
    let contentBgColor = contentBg;
    if (contentTransparency !== undefined && contentBg.startsWith('#')) {
        contentBgColor = hexToRgba(contentBg, contentTransparency);
    }

    const contentBorderWidth = getNestedValue(properties, ['appearance', 'content', 'border', 'width']) ?? 1;
    const contentBorderColor = getNestedValue(properties, ['appearance', 'content', 'border', 'color']) || '#d1d5db';
    const contentPaddingBlock = resolveSpacingValue(getNestedValue(properties, ['appearance', 'content', 'padding', 'block'])) || '1.6rem';
    const contentPaddingInline = resolveSpacingValue(getNestedValue(properties, ['appearance', 'content', 'padding', 'inline'])) || '1.6rem';

    // Spacing
    const marginBlock = resolveSpacingValue(getNestedValue(properties, ['spacing', 'marginBlock'])) || '1.6rem';
    const marginInline = resolveSpacingValue(getNestedValue(properties, ['spacing', 'marginInline'])) || '0';

    // Build container styles
    const containerStyles = buildStyleString([
        widthRule.component,
        canUseSpacingValue(marginBlock) ? `margin-block: ${marginBlock};` : '',
        canUseSpacingValue(marginInline) ? `margin-inline: ${marginInline};` : '',
        canUseSpacingValue(tabGap) ? `gap: ${tabGap};` : '',
    ]);

    let tabsHTML = `<div class="tabs" data-orientation="${orientation}" style="${containerStyles}">`;

    tabs.forEach((tab, i) => {
        const tabId = `${tabsId}_${i}`;
        const tabTitle = escapeHtml(tab.title || `Tab ${i + 1}`);
        const tabComponents = tab.components || [];
        const tabPath = [...path, 'tabs', i, 'components'];

        // Radio input (hidden)
        tabsHTML += `<input type="radio" name="${tabsId}" id="${tabId}" ${i === 0 ? 'checked' : ''} />`;

        // Tab label with styling and CSS custom properties for active state
        // Build border based on position - border color uses typography colors
        let borderStyle = '';
        if (borderPosition === 'upper') {
            borderStyle = `border-top: ${tabBorderWidth}px solid ${inactiveColor};`;
        } else if (borderPosition === 'lower') {
            borderStyle = `border-bottom: ${tabBorderWidth}px solid ${inactiveColor};`;
        } else if (borderPosition === 'full') {
            borderStyle = `border: ${tabBorderWidth}px solid ${inactiveColor};`;
        }

        const labelStyles = buildStyleString([
            `font-size: ${labelSize};`,
            `font-weight: ${labelWeight};`,
            `color: ${inactiveColor};`,
            `background-color: ${inactiveBg};`,
            borderStyle,
            `--active-color: ${activeColor};`,
            `--active-bg: ${activeBg};`,
            `--border-width: ${tabBorderWidth}px;`,
            `--border-position: ${borderPosition};`,
        ]);
        tabsHTML += `<label for="${tabId}" style="${labelStyles}">${tabTitle}</label>`;

        // Content area with styling
        const contentStyles = buildStyleString([
            `background-color: ${contentBgColor};`,
            `border: ${contentBorderWidth}px solid ${contentBorderColor};`,
            `padding-block: ${contentPaddingBlock};`,
            `padding-inline: ${contentPaddingInline};`,
        ]);

        const tabContent = renderComponentsList(tabComponents, tabPath, mode);
        tabsHTML += `<div class="content" style="${contentStyles}"><div>${tabContent}</div></div>`;
    });

    tabsHTML += `</div>`;

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return wrapComponentWithChrome(componentId, 'tabs', tabsHTML, getComponentDepth(path));
    }

    return tabsHTML;
}
/**
 * Generates the inner HTML for a component.
 * @param {string} type The component type.
 * @param {object} props The component properties.
 * @param {string} classes The CSS classes for the component.
 * @param {string} styleAttr The inline styles for the component.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML.
 */
export function generateComponentInnerHTML(type, props, classes, styleAttr, mode) {
    let componentType = type;
    let componentProps = props || {};
    if (componentType === 'h1' || componentType === 'h2' || componentType === 'h3') {
        const level = parseInt(componentType.slice(1), 10) || 2;
        componentType = 'heading';
        componentProps = deepMerge({}, componentProps, { level, text: componentProps.text || componentProps.content });
    }
    let styleString = typeof styleAttr === 'string' ? styleAttr.trim() : '';
    const appendInlineStyle = (base, addition) => {
        const normalized = (base || '').trim();
        const additionValue = (addition || '').trim();
        if (!additionValue) {
            return normalized;
        }
        if (!normalized) {
            return additionValue;
        }
        return normalized.endsWith(';') ? normalized + ' ' + additionValue : normalized + '; ' + additionValue;
    };
    if (componentType === 'blockquote') {
        const borderColor = componentProps.pullBorderColor || '#6366f1';
        styleString = appendInlineStyle(styleString, `--blockquote-border: ${borderColor};`);
    }

    if (TEXT_COMPONENTS_WITH_WIDTH_MODE.has(componentType)) {
        const widthMode = getNestedValue(componentProps, ['layout', 'widthMode']) || 'stretch';
        const widthRule = getWidthModeRule(widthMode);

        // Apply component styles
        styleString = appendInlineStyle(styleString, 'display: inline-block; box-sizing: border-box;');
        styleString = appendInlineStyle(styleString, widthRule.component);

        // CHANGE: ALWAYS apply flex properties to component (both preview and export)
        // No wrappers means component gets all styles
        if (Array.isArray(widthRule.flex)) {
            widthRule.flex.forEach(declaration => {
                if (declaration) {
                    styleString = appendInlineStyle(styleString, declaration);
                }
            });
        }
    }
    const attributeParts = [];
    if (classes) {
        attributeParts.push(`class="${classes}"`);
    }
    attributeParts.push(`style="${styleString}"`);
    const attributeString = attributeParts.join(' ').trim();
    const attrSegment = attributeString ? ' ' + attributeString : '';
    if (componentType === 'heading') {
        const level = Math.min(6, Math.max(1, parseInt(componentProps.level, 10) || 2));
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Heading');
        return `<h${level}${attrSegment}>${textContent}</h${level}>`;
    }

    if (componentType === 'paragraph') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Paragraph');
        return `<p${attrSegment}>${textContent}</p>`;
    }
    if (componentType === 'eyebrow') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Label');
        return `<p${attrSegment}>${textContent}</p>`;
    }
    if (componentType === 'caption') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Caption');
        return `<p${attrSegment}>${textContent}</p>`;
    }
    if (componentType === 'blockquote') {
        const quoteContent = escapeHtmlWithLineBreaks(componentProps.quote || componentProps.text || 'Quote');
        const citation = componentProps.cite ? '<figcaption class="blockquote-citation">&mdash; ' + escapeHtml(componentProps.cite) + '</figcaption>' : '';
        return '<figure' + attrSegment + '><blockquote>' + quoteContent + '</blockquote>' + citation + '</figure>';
    }
    const finalAttrs = attributeString;

    if (componentType === 'image') {
        const src = getNestedValue(componentProps, ['source', 'url']) || 'https://via.placeholder.com/150';
        const alt = getNestedValue(componentProps, ['source', 'altText']) || '';
        const height = getNestedValue(componentProps, ['presentation', 'height']);
        const fit = getNestedValue(componentProps, ['presentation', 'fit']) || 'cover';
        const cornerStyle = getNestedValue(componentProps, ['presentation', 'cornerStyle']);

        let imgStyles = `width: 100%; height: ${toRem(height) || 'auto'}; object-fit: ${fit};`;

        // Apply cornerStyle to the <img> element
        if (cornerStyle) {
            const radius = resolveBorderRadiusToken(cornerStyle);
            if (radius) {
                imgStyles += ` border-radius: ${radius};`;
            }
        }

        const link = componentProps.link;
        let imageHTML = `<img src="${src}" alt="${alt}" style="${imgStyles}">`;

        if (link) {
            imageHTML = `<a href="${link}">${imageHTML}</a>`;
        }

        // Handle overlay
        const overlayEnabled = getNestedValue(componentProps, ['overlay', 'enabled']);
        if (overlayEnabled) {
            const overlayColor = getNestedValue(componentProps, ['overlay', 'color']) || 'rgba(0,0,0,0.5)';
            const overlayOpacity = getNestedValue(componentProps, ['overlay', 'opacity']) || '0.5';
            imageHTML += `<div class="image-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: ${overlayColor}; opacity: ${overlayOpacity}; pointer-events: none;"></div>`;
        }

        // Merge position: relative with existing styles
        const containerStyle = appendInlineStyle(styleString, 'position: relative;');
        const containerAttrs = attributeString.replace(/style="[^"]*"/, `style="${containerStyle}"`);
        return `<div ${containerAttrs}>${imageHTML}</div>`;
    } else if (componentType === 'gif') {
        const src = getNestedValue(componentProps, ['source', 'url']) || 'https://media.giphy.com/media/VseXoJs6vVmwU/giphy.gif';
        const alt = getNestedValue(componentProps, ['source', 'altText']) || 'animated gif';
        const fit = getNestedValue(componentProps, ['presentation', 'fit']) || 'cover';
        const cornerStyle = getNestedValue(componentProps, ['presentation', 'cornerStyle']);

        let imgStyles = `width: 100%; height: auto; object-fit: ${fit};`;

        // Apply cornerStyle to the <img> element
        if (cornerStyle) {
            const radius = resolveBorderRadiusToken(cornerStyle);
            if (radius) {
                imgStyles += ` border-radius: ${radius};`;
            }
        }

        const link = componentProps.link;
        let gifHTML = `<img src="${src}" alt="${alt}" style="${imgStyles}">`;

        if (link) {
            gifHTML = `<a href="${link}">${gifHTML}</a>`;
        }

        // Handle overlay
        const overlayEnabled = getNestedValue(componentProps, ['overlay', 'enabled']);
        if (overlayEnabled) {
            const overlayColor = getNestedValue(componentProps, ['overlay', 'color']) || 'rgba(0,0,0,0.5)';
            const overlayOpacity = getNestedValue(componentProps, ['overlay', 'opacity']) || '0.5';
            gifHTML += `<div class="image-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: ${overlayColor}; opacity: ${overlayOpacity}; pointer-events: none;"></div>`;
        }

        // Merge position: relative with existing styles
        const containerStyle = appendInlineStyle(styleString, 'position: relative;');
        const containerAttrs = attributeString.replace(/style="[^"]*"/, `style="${containerStyle}"`);
        return `<div ${containerAttrs}>${gifHTML}</div>`;
    } else if (componentType === 'video') {
        const videoUrl = getNestedValue(componentProps, ['source', 'url']) || '';
        const videoId = videoUrl.split('v=')[1];
        const embedUrl = videoId ? 'https://www.youtube.com/embed/' + videoId.split('&')[0] : '';
        return '<iframe ' + finalAttrs + ' src="' + embedUrl + '" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width: 100%; aspect-ratio: 16/9;"></iframe>';
    } else if (componentType === 'gif') {
        const gifUrl = getNestedValue(componentProps, ['source', 'url']);
        return '<img src="' + (gifUrl || 'https://media.giphy.com/media/VseXoJs6vVmwU/giphy.gif') + '" alt="gif" ' + finalAttrs + ' />';
    } else if (componentType === 'textbox') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');

        // Extract appearance properties
        const bgColor = getNestedValue(componentProps, ['appearance', 'background', 'color']) || '#ffffff';
        const bgTransparency = getNestedValue(componentProps, ['appearance', 'background', 'transparency']) ?? 100;
        let backgroundColor = bgColor;
        if (bgTransparency !== undefined && bgColor.startsWith('#')) {
            backgroundColor = hexToRgba(bgColor, bgTransparency);
        }
        const borderWidth = getNestedValue(componentProps, ['appearance', 'border', 'width']) ?? 1;
        const borderStyle = getNestedValue(componentProps, ['appearance', 'border', 'style']) || 'solid';
        const borderColor = getNestedValue(componentProps, ['appearance', 'border', 'color']) || '#cccccc';
        const borderRadius = resolveBorderRadiusToken(getNestedValue(componentProps, ['appearance', 'radius'])) || '0px';
        const textColor = getNestedValue(componentProps, ['typography', 'color']) || '#000000';
        const paddingBlock = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'block'])) || resolveSpacingValue('sm');
        const paddingInline = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'inline'])) || resolveSpacingValue('sm');

        // Build textbox styles - border hidden by default, shown on focus via CSS
        let textboxStyles = `background-color: ${backgroundColor};`;
        textboxStyles += `color: ${textColor};`;
        textboxStyles += `border: ${borderWidth}px ${borderStyle} transparent;`;
        textboxStyles += `border-radius: ${borderRadius};`;
        textboxStyles += `width: 100%;`;
        textboxStyles += `box-sizing: border-box;`;
        if (canUseSpacingValue(paddingBlock)) {
            textboxStyles += `padding-block: ${paddingBlock};`;
        }
        if (canUseSpacingValue(paddingInline)) {
            textboxStyles += `padding-inline: ${paddingInline};`;
        }
        textboxStyles += `transition: all 0.2s ease;`;
        textboxStyles += `--focus-border-color: ${borderColor};`;

        const inputAttrs = attributeString.replace(/style="[^"]*"/, `style="${textboxStyles}"`);
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><input type="text" id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" value="' + (componentProps.value || '') + '" ' + inputAttrs + ' /></div>';
    } else if (componentType === 'textarea') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');

        // Extract appearance properties
        const bgColor = getNestedValue(componentProps, ['appearance', 'background', 'color']) || '#ffffff';
        const bgTransparency = getNestedValue(componentProps, ['appearance', 'background', 'transparency']) ?? 100;
        let backgroundColor = bgColor;
        if (bgTransparency !== undefined && bgColor.startsWith('#')) {
            backgroundColor = hexToRgba(bgColor, bgTransparency);
        }
        const borderWidth = getNestedValue(componentProps, ['appearance', 'border', 'width']) ?? 1;
        const borderStyle = getNestedValue(componentProps, ['appearance', 'border', 'style']) || 'solid';
        const borderColor = getNestedValue(componentProps, ['appearance', 'border', 'color']) || '#cccccc';
        const borderRadius = resolveBorderRadiusToken(getNestedValue(componentProps, ['appearance', 'radius'])) || '0px';
        const textColor = getNestedValue(componentProps, ['typography', 'color']) || '#000000';
        const paddingBlock = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'block'])) || resolveSpacingValue('sm');
        const paddingInline = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'inline'])) || resolveSpacingValue('sm');

        // Build textarea styles - border hidden by default, shown on focus via CSS
        let textareaStyles = `background-color: ${backgroundColor};`;
        textareaStyles += `color: ${textColor};`;
        textareaStyles += `border: ${borderWidth}px ${borderStyle} transparent;`;
        textareaStyles += `border-radius: ${borderRadius};`;
        textareaStyles += `width: 100%;`;
        textareaStyles += `box-sizing: border-box;`;
        if (canUseSpacingValue(paddingBlock)) {
            textareaStyles += `padding-block: ${paddingBlock};`;
        }
        if (canUseSpacingValue(paddingInline)) {
            textareaStyles += `padding-inline: ${paddingInline};`;
        }
        textareaStyles += `font-family: inherit;`;
        textareaStyles += `transition: all 0.2s ease;`;
        textareaStyles += `--focus-border-color: ${borderColor};`;

        const textareaAttrs = attributeString.replace(/style="[^"]*"/, `style="${textareaStyles}"`);
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><textarea id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" rows="' + (componentProps.rows || 3) + '" ' + textareaAttrs + '>' + (componentProps.value || '') + '</textarea></div>';
    } else if (componentType === 'button') {
        // Extract appearance properties
        const bgColor = getNestedValue(componentProps, ['appearance', 'background', 'color']) || '#2563eb';
        const bgTransparency = getNestedValue(componentProps, ['appearance', 'background', 'transparency']) ?? 100;
        let backgroundColor = bgColor;
        if (bgTransparency !== undefined && bgColor.startsWith('#')) {
            backgroundColor = hexToRgba(bgColor, bgTransparency);
        }
        const borderWidth = getNestedValue(componentProps, ['appearance', 'border', 'width']) ?? 1;
        const borderStyle = getNestedValue(componentProps, ['appearance', 'border', 'style']) || 'solid';
        const borderColor = getNestedValue(componentProps, ['appearance', 'border', 'color']) || 'transparent';
        const borderRadius = resolveBorderRadiusToken(getNestedValue(componentProps, ['appearance', 'radius'])) || '4px';
        const paddingBlock = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'block'])) || resolveSpacingValue('sm');
        const paddingInline = resolveSpacingValue(getNestedValue(componentProps, ['appearance', 'padding', 'inline'])) || resolveSpacingValue('md');
        const marginBlock = resolveSpacingValue(getNestedValue(componentProps, ['spacing', 'marginBlock'])) || resolveSpacingValue('sm');
        const marginInline = resolveSpacingValue(getNestedValue(componentProps, ['spacing', 'marginInline'])) || resolveSpacingValue('xs');

        // Extract typography properties
        const textColor = getNestedValue(componentProps, ['typography', 'color']) || '#ffffff';
        const fontWeight = resolveFontWeight(getNestedValue(componentProps, ['typography', 'weight'])) || resolveFontWeight('semibold');

        // Build comprehensive button styles
        let buttonStyles = 'width: auto; flex: 0 0 auto;';
        buttonStyles += `background-color: ${backgroundColor};`;
        buttonStyles += `color: ${textColor};`;
        buttonStyles += `font-weight: ${fontWeight};`;
        buttonStyles += `border: ${borderWidth}px ${borderStyle} ${borderColor};`;
        buttonStyles += `border-radius: ${borderRadius};`;
        buttonStyles += `cursor: pointer;`;
        buttonStyles += `transition: all 0.2s ease;`;
        if (canUseSpacingValue(paddingBlock)) {
            buttonStyles += `padding-block: ${paddingBlock};`;
        }
        if (canUseSpacingValue(paddingInline)) {
            buttonStyles += `padding-inline: ${paddingInline};`;
        }
        if (canUseSpacingValue(marginBlock)) {
            buttonStyles += `margin-block: ${marginBlock};`;
        }
        if (canUseSpacingValue(marginInline)) {
            buttonStyles += `margin-inline: ${marginInline};`;
        }

        styleString = appendInlineStyle(styleString, buttonStyles);
        return '<button onclick="' + (componentProps.onclick || '') + '" ' + finalAttrs + '>' + (componentProps.text || 'Click Me') + '</button>';
    } else if (componentType === 'dropdown') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');
        const options = (componentProps.options || 'Option 1,Option 2,Option3').split(',');
        const optionHTML = options.map(opt => {
            const value = opt.trim();
            const selected = componentProps.selected === value ? ' selected' : '';
            return '<option value="' + value + '"' + selected + '>' + value + '</option>';
        }).join('');

        // Extract appearance properties
        const bgColor = getNestedValue(componentProps, ['appearance', 'background', 'color']) || '#ffffff';
        const bgTransparency = getNestedValue(componentProps, ['appearance', 'background', 'transparency']) ?? 100;
        let backgroundColor = bgColor;
        if (bgTransparency !== undefined && bgColor.startsWith('#')) {
            backgroundColor = hexToRgba(bgColor, bgTransparency);
        }
        const borderWidth = getNestedValue(componentProps, ['appearance', 'border', 'width']) ?? 1;
        const borderStyle = getNestedValue(componentProps, ['appearance', 'border', 'style']) || 'solid';
        const borderColor = getNestedValue(componentProps, ['appearance', 'border', 'color']) || '#cccccc';
        const borderRadius = resolveBorderRadiusToken(getNestedValue(componentProps, ['appearance', 'radius'])) || '0px';

        // Build dropdown styles
        let dropdownStyles = `background-color: ${backgroundColor};`;
        dropdownStyles += `border: ${borderWidth}px ${borderStyle} ${borderColor};`;
        dropdownStyles += `border-radius: ${borderRadius};`;
        dropdownStyles += `width: 100%;`;
        dropdownStyles += `box-sizing: border-box;`;
        dropdownStyles += `padding: 0.4rem;`;
        dropdownStyles += `cursor: pointer;`;
        dropdownStyles += `transition: all 0.2s ease;`;

        const selectAttrs = attributeString.replace(/style="[^"]*"/, `style="${dropdownStyles}"`);
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><select id="' + id + '" ' + selectAttrs + '>' + optionHTML + '</select></div>';
    } else if (componentType === 'calendar') {
        return generateCalendarHTML(componentProps);
    } else if (componentType === 'checkbox') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');

        // Extract appearance color
        const accentColor = getNestedValue(componentProps, ['appearance', 'color']) || '#2563eb';

        // Build checkbox styles with accent color via CSS variable
        let checkboxStyles = `--checkbox-color: ${accentColor};`;

        const checkboxAttrs = attributeString ? attributeString.replace(/style="[^"]*"/, `style="${checkboxStyles}"`) : `style="${checkboxStyles}"`;
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + checkboxAttrs + ' style="' + labelStyles + '"><input type="checkbox" id="' + id + '" class="styled-checkbox"' + (componentProps.checked ? ' checked' : '') + ' style="accent-color: ' + accentColor + ';" /><span>' + (componentProps.text || 'Check me') + '</span></label></div>';
    } else if (componentType === 'radio') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');

        // Extract appearance color
        const accentColor = getNestedValue(componentProps, ['appearance', 'color']) || '#2563eb';

        // Build radio styles with accent color via CSS variable
        let radioStyles = `--radio-color: ${accentColor};`;

        const radioAttrs = finalAttrs ? finalAttrs.replace(/style="[^"]*"/, `style="${radioStyles}"`) : `style="${radioStyles}"`;
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + radioAttrs + ' style="' + labelStyles + '"><input type="radio" id="' + id + '" name="' + (componentProps.name || 'radio1') + '" value="' + (componentProps.value || 'option1') + '" class="styled-radio" style="accent-color: ' + accentColor + ';" /><span>' + (componentProps.text || 'Select me') + '</span></label></div>';
    } else if (componentType === 'hamburger') {
        const links = componentProps.links || [];
        let menuHTML = '<div class="dropdown" ' + finalAttrs + '><button class="button primary">?</button><div class="menu">';
        links.forEach(link => {
            menuHTML += '<a href="' + (link.href || '#') + '" class="menu-item">' + escapeHtml(link.label || '') + '</a>';
        });
        menuHTML += '</div></div>';
        return menuHTML;
    } else if (componentType === 'br') {
        return mode === 'preview' ? '<div class="comp-br" style="height: 2rem; border-bottom: 1px dashed #ccc; margin: 1rem 0;"></div>' : '<br>';
    } else if (componentType === 'titlebar') {
        return generateTitlebarHTML(componentProps, classes, styleAttr, mode);
    } else if (componentType === 'link') {
        let linkStyle = componentProps.underline ? 'text-decoration: underline;' : 'text-decoration: none;';
        const arrowHTML = componentProps.showArrow ? '&nbsp;?' : '';
        const sanitizedStyles = styleString.replace(/text-align:[^;]+;/g, '');
        return '<div style="text-align: ' + (componentProps.textAlign || 'left') + ';"><a href="' + (componentProps.href || '#') + '" style="' + linkStyle + ' ' + sanitizedStyles + '">' + (componentProps.text || 'Click Me') + arrowHTML + '</a></div>';
    }
    return '<div style="color: #ef4444; font-style: italic;">Unknown component: ' + componentType + '</div>';
}
/**
 * @function generateTitlebarHTML
 * @description Generates the HTML for a titlebar component.
 * @param {object} props - The properties of the titlebar component.
 * @param {string} classes - Additional CSS classes for the titlebar.
 * @param {string} styleAttr - Inline style attributes for the titlebar.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the titlebar.
 * @calledBy {generateComponentInnerHTML}
 * @calls {getAlignmentClass}
 */
function generateTitlebarHTML(props, classes, styleAttr, mode) {
    const alignment = getNestedValue(props, ['layout', 'alignment']);
    const alignmentClass = getAlignmentClass(alignment);
    const isRightAligned = alignment === 'right';
    const logoUrl = getNestedValue(props, ['branding', 'logoUrl']);
    const showLogo = getNestedValue(props, ['branding', 'showLogo']);
    const titleText = getNestedValue(props, ['branding', 'title']);
    const links = getNestedValue(props, ['navigation', 'links']);
    const shouldRenderLogo = showLogo !== false && !!logoUrl;
    const logoHTML = shouldRenderLogo ? `<img src="${logoUrl}" alt="Logo" class="titlebar-logo" />` : '';
    const titleHTML = titleText ? `<h1 class="titlebar-title">${titleText}</h1>` : '';
    const brandFragments = [];
    if (isRightAligned) {
        if (titleHTML) {
            brandFragments.push(titleHTML);
        }
        if (logoHTML) {
            brandFragments.push(logoHTML);
        }
    } else {
        if (logoHTML) {
            brandFragments.push(logoHTML);
        }
        if (titleHTML) {
            brandFragments.push(titleHTML);
        }
    }
    const brandClass = `titlebar-brand${isRightAligned ? ' align-right' : ''}`;
    const brandContent = brandFragments.join('');
    const ensureRem = (value, fallback) => {
        const source = value ?? fallback;
        if (typeof source === 'number' && !Number.isNaN(source)) {
            return `${source / 10}rem`;
        }
        if (typeof source === 'string') {
            const trimmed = source.trim();
            if (!trimmed) {
                return ensureRem(fallback, undefined);
            }
            if (trimmed.endsWith('rem')) {
                return trimmed;
            }
            const numeric = parseFloat(trimmed);
            if (!Number.isNaN(numeric)) {
                return `${numeric / 10}rem`;
            }
        }
        if (fallback !== undefined && fallback !== value) {
            if (typeof fallback === 'number' && !Number.isNaN(fallback)) {
                return `${fallback / 10}rem`;
            }
            if (typeof fallback === 'string') {
                const trimmedFallback = fallback.trim();
                if (trimmedFallback.endsWith('rem')) {
                    return trimmedFallback;
                }
                const numericFallback = parseFloat(trimmedFallback);
                if (!Number.isNaN(numericFallback)) {
                    return `${numericFallback / 10}rem`;
                }
            }
        }
        return '0rem';
    };
    const baseHeightPx = (() => {
        const rawHeight = getNestedValue(props, ['layout', 'height']);
        if (typeof rawHeight === 'number' && !Number.isNaN(rawHeight)) {
            return rawHeight;
        }
        if (typeof rawHeight === 'string') {
            const trimmed = rawHeight.trim();
            if (trimmed.endsWith('rem')) {
                const remValue = parseFloat(trimmed);
                if (!Number.isNaN(remValue)) {
                    return remValue * 10;
                }
            }
            const parsed = parseFloat(trimmed);
            if (!Number.isNaN(parsed)) {
                return parsed;
            }
        }
        return 60;
    })();
    const titleFontSize = ensureRem(getNestedValue(props, ['typography', 'title', 'size']), 24);
    const menuFontSize = ensureRem(getNestedValue(props, ['typography', 'menu', 'size']), 16);
    const titleFontWeight = resolveFontWeight(getNestedValue(props, ['typography', 'title', 'weight']) || 'bold') || 700;
    const menuFontWeight = resolveFontWeight(getNestedValue(props, ['typography', 'menu', 'weight']) || 'medium') || 500;
    const titleColor = getNestedValue(props, ['typography', 'title', 'color']);
    const menuColor = getNestedValue(props, ['typography', 'menu', 'color']);
    const shrinkPercentRaw = getNestedValue(props, ['layout', 'shrinkPercent']) ?? 50;
    const shrinkPercentNumeric = typeof shrinkPercentRaw === 'number' ? shrinkPercentRaw : parseFloat(shrinkPercentRaw);
    const shrinkScale = (() => {
        if (Number.isNaN(shrinkPercentNumeric)) {
            return 0.5;
        }
        return Math.min(1, Math.max(0.1, shrinkPercentNumeric / 100));
    })();
    const baseHeightRem = ensureRem(baseHeightPx, 60);
    const titlebarId = `titlebar_${Date.now()}`;
    const hasStyle = typeof styleAttr === 'string' && styleAttr.trim().length > 0;
    const normalizedStyleAttr = hasStyle
        ? (styleAttr.trim().endsWith(';') ? styleAttr.trim() : `${styleAttr.trim()};`)
        : '';
    const styleFragments = [];
    if (normalizedStyleAttr) {
        styleFragments.push(normalizedStyleAttr);
    }
    styleFragments.push(`--base-height: ${baseHeightRem};`);
    styleFragments.push(`--title-font-size: ${titleFontSize};`);
    styleFragments.push(`--menu-font-size: ${menuFontSize};`);
    styleFragments.push(`--title-font-weight: ${titleFontWeight};`);
    styleFragments.push(`--menu-font-weight: ${menuFontWeight};`);
    styleFragments.push(`--shrink-scale: ${shrinkScale};`);
    if (titleColor) {
        styleFragments.push(`--titlebar-title-color: ${titleColor};`);
    }
    if (menuColor) {
        styleFragments.push(`--titlebar-link-color: ${menuColor};`);
    }
    const focusBg = getNestedValue(props, ['appearance', 'focus', 'background']);
    if (focusBg) {
        styleFragments.push(`--titlebar-link-hover-bg: ${focusBg};`);
    }
    const focusColor = getNestedValue(props, ['appearance', 'focus', 'color']);
    if (focusColor) {
        styleFragments.push(`--titlebar-link-hover-color: ${focusColor};`);
    }
    const combinedStyles = styleFragments.join(' ');
    const generateTitlebarLinks = (links) => {
        if (!links || !Array.isArray(links)) {
            return '';
        }
        return links.map(link => {
            const href = link.href || '#';
            const label = escapeHtml(link.label || '');
            return `<a href="${href}" class="titlebar-link">${label}</a>`;
        }).join('');
    };
    const linksHTML = generateTitlebarLinks(links);
    const navMarkup = `
            <div class="titlebar-nav">
                ${linksHTML}
            </div>`;
    const brandMarkup = `
            <div class="${brandClass}">
                ${brandContent}
            </div>`;
    const mobileMenuButton = `
            <button type="button" class="mobile-menu-button">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </button>`;
    const brandPositionAttr = isRightAligned ? 'right' : 'left';
    const sections = isRightAligned
        ? [navMarkup, mobileMenuButton, brandMarkup]
        : [brandMarkup, mobileMenuButton, navMarkup];
    const contentMarkup = sections.join('n');

    return `
        <nav class="titlebar ${alignmentClass} ${classes}" style="${combinedStyles}" data-base-height="${baseHeightPx}" data-logo-position="${brandPositionAttr}" id="${titlebarId}">
${contentMarkup}
        </nav>
    `;
}
/**
 * Generates inline styles for a component from its properties.
 * @param {object} props The component properties.
 * @param {string} componentName The name of the component.
 * @returns {string} The generated inline styles.
 */
function generateRemainingStyles(props = {}, componentName) {
    let styles = '';
    const appearance = props.appearance || {};
    const backgroundGroup = props.background || appearance.background || {};
    const backgroundImage = backgroundGroup.image || props.backgroundImage;
    const backgroundColor = backgroundGroup.color || props.backgroundColor;
    const transparency = backgroundGroup.transparency;

    if (backgroundImage) {
        styles += `background-image: url('${backgroundImage}');`;
        styles += 'background-size: cover;';
        styles += 'background-position: center;';
    } else if (backgroundColor) {
        // Check if we have a transparency value (0-100) to combine with hex color
        if (transparency !== undefined && backgroundColor.startsWith('#')) {
            const finalColor = hexToRgba(backgroundColor, transparency);
            styles += `background-color: ${finalColor};`;
        } else {
            styles += `background-color: ${backgroundColor};`;
        }
    }
    const typographyGroup = props.typography || {};
    const fontSize = resolveTypographySize(typographyGroup.size || props.fontSize);
    if (fontSize) {
        styles += `font-size: ${fontSize};`;
    }
    const fontWeight = resolveFontWeight(typographyGroup.weight || props.fontWeight);
    if (fontWeight) {
        styles += `font-weight: ${fontWeight};`;
    }
    const fontStyle = typographyGroup.fontStyle || props.fontStyle;
    if (fontStyle) {
        styles += `font-style: ${fontStyle};`;
    }
    const textTransform = typographyGroup.transform || props.transform;
    if (textTransform) {
        styles += `text-transform: ${textTransform};`;
    }
    const letterSpacingValue = resolveLetterSpacing(typographyGroup.letterSpacing || props.letterSpacing);
    if (letterSpacingValue) {
        styles += `letter-spacing: ${letterSpacingValue};`;
    }
    const lineHeightValue = resolveLineHeight(typographyGroup.lineHeight || props.lineHeight);
    if (lineHeightValue) {
        styles += `line-height: ${lineHeightValue};`;
    }
    const textAlign = typographyGroup.align || props.textAlign;
    if (textAlign) {
        styles += `text-align: ${textAlign};`;
    }
    const textColor = typographyGroup.color || props.color;
    if (textColor) {
        styles += `color: ${textColor};`;
    }
    const layout = props.layout || {};
    const spacingGroup = props.spacing || {};
    const marginGroup = spacingGroup.margin || layout.margin;
    if (marginGroup && typeof marginGroup === 'object') {
        for (const side of Object.keys(marginGroup)) {
            const resolved = resolveSpacingValue(marginGroup[side]);
            if (canUseSpacingValue(resolved)) {
                styles += `margin-${side}: ${resolved};`;
            }
        }
    } else if (props.margin) {
        styles += `margin: ${toRem(props.margin)};`;
    }

    // Check for appearance.padding (text components) first, then spacing.padding or layout.padding
    const appearancePaddingGroup = appearance.padding;
    const paddingGroup = appearancePaddingGroup || spacingGroup.padding || layout.padding;

    if (paddingGroup && typeof paddingGroup === 'object') {
        // Handle block/inline padding (logical properties)
        if ('block' in paddingGroup || 'inline' in paddingGroup) {
            const blockPadding = resolveSpacingValue(paddingGroup.block);
            if (canUseSpacingValue(blockPadding) && blockPadding !== 'auto') {
                styles += `padding-top: ${blockPadding}; padding-bottom: ${blockPadding};`;
            }
            const inlinePadding = resolveSpacingValue(paddingGroup.inline);
            if (canUseSpacingValue(inlinePadding) && inlinePadding !== 'auto') {
                styles += `padding-left: ${inlinePadding}; padding-right: ${inlinePadding};`;
            }
        } else {
            // Handle traditional side-based padding
            for (const side of Object.keys(paddingGroup)) {
                const resolved = resolveSpacingValue(paddingGroup[side]);
                if (canUseSpacingValue(resolved)) {
                    styles += `padding-${side}: ${resolved};`;
                }
            }
        }
    } else if (props.padding) {
        styles += `padding: ${toRem(props.padding)};`;
    }
    const borderGroup = props.border || appearance.border || {};
    const borderWidth = borderGroup.width ?? props.borderWidth;
    const borderStyleValue = borderGroup.style ?? props.borderStyle;
    const borderColorValue = borderGroup.color ?? props.borderColor;
    if (borderWidth !== undefined && borderWidth !== null) {
        const widthValue = typeof borderWidth === 'number' ? `${borderWidth}px` : toRem(borderWidth);
        const styleValue = borderStyleValue || 'solid';
        if (parseFloat(widthValue) > 0 && styleValue !== 'none') {
            styles += `border: ${widthValue} ${styleValue} ${borderColorValue || '#000000'};`;
        }
    }
    const borderRadius = borderGroup.radius ?? appearance.radius ?? props.borderRadius;
    if (borderRadius) {
        const radiusValue = resolveBorderRadiusToken(borderRadius);
        if (radiusValue) {
            styles += `border-radius: ${radiusValue};`;
        }
    }
    const shadowValue = appearance.shadow ?? props.shadow;
    if (shadowValue) {
        styles += `box-shadow: ${shadowValue};`;
    }
    const maxWidth = layout.maxWidth;
    if (maxWidth !== undefined && maxWidth !== null) {
        styles += `max-width: ${typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth};`;
    }
    const width = layout.width || props.width;
    if (width) {
        styles += `width: ${typeof width === 'number' ? `${width}px` : width};`;
    }
    const minHeightValue = layout.minHeight ?? props.minHeight;
    const normalizedMinHeight = normalizeDimensionValue(minHeightValue);
    if (normalizedMinHeight) {
        styles += `min-height: ${normalizedMinHeight};`;
    }
    return styles;
}
// =================================================================================================
/**
 * Registers a component for initialization after rendering.
 * @param {string} name The name of the component.
 * @param {string} id The ID of the component's DOM element.
 * @param {object} props The component's properties.
 */
export function registerComponentForInitialization(name, id, props = {}) {
    queueComponentInitialization({ name, id, props });
}
/**
 * Initializes all registered components.
 * @param {object} componentInitializers A map of component initializers.
 */
export function initializeAllComponents(componentInitializers) {
    const queue = consumeComponentInitializationQueue();
    queue.forEach(entry => {
        const element = document.getElementById(entry.id);
        if (element && componentInitializers && typeof componentInitializers[entry.name] === 'function') {
            try {
                componentInitializers[entry.name](element, entry.props || {});
            } catch (error) {
                console.error('Failed to initialize component', entry.name, error);
            }
        }
    });
}
/**
 * Computes inline styles from a component's properties.
 * @param {object} props The component's properties.
 * @returns {string} The generated inline styles.
 */
export function computeInlineStylesFromProperties(props = {}) {
    return generateRemainingStyles(props, 'page');
}
















