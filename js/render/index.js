import { registerComponentPath, resetComponentPathMap, queueComponentInitialization, consumeComponentInitializationQueue } from '../core/state.js';
import { deepClone, deepMerge, getNestedValue, deleteNestedValue } from '../utils/object.js';
import { toRem, resolveSpacingValue, resolveLetterSpacing, resolveLineHeight, resolveTypographySize, resolveFontWeight } from '../utils/styles.js';
import { escapeHtml, escapeHtmlWithLineBreaks } from '../utils/strings.js';
// --- COMPONENT RENDERING ---
// =================================================================================================

const FLEX_ALIGN_MAP = {
    start: 'flex-start',
    center: 'center',
    end: 'flex-end',
    stretch: 'stretch',
};

const FLEX_JUSTIFY_MAP = {
    start: 'flex-start',
    center: 'center',
    end: 'flex-end',
    'space-between': 'space-between',
    'space-around': 'space-around',
    'space-evenly': 'space-evenly',
};

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

function mapFlexJustify(value) {
    return FLEX_JUSTIFY_MAP[value] || value;
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
    resetComponentPathMap();
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
        case 'section':
            return renderSectionComponent(component, path, mode);
        case 'stack':
            return renderStackComponent(component, path, mode);
        case 'columnsgrid':
            return renderColumnsGrid(component, path, mode);
        case 'accordion':
            return renderAccordion(component, path, mode);
        case 'tabs':
            return renderTabs(component, path, mode);
        case 'image':
            return renderImageComponent(component, path, mode);
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
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">carousel</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
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
        return `<div class="rendered-component" data-component-id="${componentId}" style="${styles}" >
                    <div class="component-label">form</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    <form>${contentHTML}</form>
                </div>`;
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
            contentHTML = '<div class="page-placeholder" style="text-align: center; color: #6b7280; padding: 5rem; border: 2px dashed #ccc;">Write YAML in the editor above or click components from the sidebar</div>';
        }
        return `<div class="rendered-component" data-component-id="${componentId}" style="${styles} width: 100%; height: 100%;" >
                    <div class="component-label">page</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }
    // For export mode, we'll handle this differently, perhaps with a style tag
    return `<div style="${styles} width: 100%; height: 100%;">${contentHTML}</div>`;
}



function renderStackComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const directionValue = getNestedValue(properties, ['layout', 'direction']) || 'column';
    const direction = directionValue === 'row' ? 'row' : 'column';
    const align = getNestedValue(properties, ['layout', 'align']);
    const justify = getNestedValue(properties, ['layout', 'justify']);
    const wrapValue = getNestedValue(properties, ['layout', 'wrap']);
    const wrap = wrapValue ? wrapValue : null;
    const gapToken = getNestedValue(properties, ['layout', 'gap']) ?? getNestedValue(properties, ['spacing', 'gap']);
    const resolvedGap = resolveSpacingValue(gapToken);

    const outerProperties = deepClone(properties);
    const maxWidth = getNestedValue(outerProperties, ['layout', 'maxWidth']);
    const explicitWidth = getNestedValue(outerProperties, ['layout', 'width']);
    deleteNestedValue(outerProperties, ['layout', 'maxWidth']);
    deleteNestedValue(outerProperties, ['layout', 'width']);

    const outerStyleAttr = buildStyleString([generateRemainingStyles(outerProperties, 'stack')]);

    const innerStyleParts = ['display: flex;', `flex-direction: ${direction};`];
    if (resolvedGap) {
        innerStyleParts.push(`gap: ${resolvedGap};`);
    }
    if (align) {
        innerStyleParts.push(`align-items: ${mapFlexAlign(align)};`);
    }
    if (justify) {
        innerStyleParts.push(`justify-content: ${mapFlexJustify(justify)};`);
    }
    if (wrap && wrap !== 'nowrap') {
        innerStyleParts.push(`flex-wrap: ${wrap};`);
    }
    const normalizedMaxWidth = normalizeDimensionValue(maxWidth);
    if (normalizedMaxWidth) {
        innerStyleParts.push(`max-width: ${normalizedMaxWidth};`);
        innerStyleParts.push('margin-left: auto;');
        innerStyleParts.push('margin-right: auto;');
    }
    const normalizedWidth = normalizeDimensionValue(explicitWidth);
    if (normalizedWidth) {
        innerStyleParts.push(`width: ${normalizedWidth};`);
    }
    const innerStyleAttr = buildStyleString(innerStyleParts);

    const collapseBreakpoint = getNestedValue(properties, ['responsive', 'collapseBreakpoint']);
    const collapseAttr = collapseBreakpoint ? ` data-stack-collapse="${collapseBreakpoint}"` : '';
    const dividerSetting = getNestedValue(properties, ['appearance', 'divider']) || 'none';
    const dividerClass = dividerSetting && dividerSetting !== 'none' ? ` stack--divider-${dividerSetting}` : '';

    const componentsPath = [...path, 'components'];
    let contentHTML = '';
    components.forEach((child, index) => {
        const childPath = [...componentsPath, index];
        const rendered = renderComponent(child, childPath, mode);
        if (rendered) {
            contentHTML += `<div class="stack__item">${rendered}</div>`;
        }
    });
    if (mode === 'preview' && !contentHTML) {
        contentHTML = '<div class="stack-placeholder">Drop components here...</div>';
    }

    const contentWrapper = innerStyleAttr
        ? `<div class="stack__content" style="${innerStyleAttr}">${contentHTML}</div>`
        : `<div class="stack__content">${contentHTML}</div>`;

    const stackMarkup = `<div class="stack${dividerClass}" style="${outerStyleAttr}"${collapseAttr}>
            ${contentWrapper}
        </div>`;

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">stack</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${stackMarkup}
                </div>`;
    }

    return stackMarkup;
}

function renderSectionComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const tagCandidate = (getNestedValue(properties, ['layout', 'tag']) || 'section').toString().trim();
    const tag = tagCandidate.match(/^[a-zA-Z][a-zA-Z0-9-]*$/) ? tagCandidate : 'section';
    const direction = getNestedValue(properties, ['layout', 'direction']) || 'column';
    const align = getNestedValue(properties, ['layout', 'align']);
    const justify = getNestedValue(properties, ['layout', 'justify']);
    const wrap = getNestedValue(properties, ['layout', 'wrap']);
    const gapToken = getNestedValue(properties, ['layout', 'gap']) ?? getNestedValue(properties, ['spacing', 'gap']);
    const resolvedGap = resolveSpacingValue(gapToken);

    const outerProperties = deepClone(properties);
    const maxWidth = getNestedValue(outerProperties, ['layout', 'maxWidth']);
    const explicitWidth = getNestedValue(outerProperties, ['layout', 'width']);
    deleteNestedValue(outerProperties, ['layout', 'maxWidth']);
    deleteNestedValue(outerProperties, ['layout', 'width']);

    const outerStyleAttr = buildStyleString([generateRemainingStyles(outerProperties, 'section')]);

    const innerStyleParts = ['display: flex;', `flex-direction: ${direction};`];
    if (resolvedGap) {
        innerStyleParts.push(`gap: ${resolvedGap};`);
    }
    if (align) {
        innerStyleParts.push(`align-items: ${mapFlexAlign(align)};`);
    }
    if (justify) {
        innerStyleParts.push(`justify-content: ${mapFlexJustify(justify)};`);
    }
    if (wrap) {
        innerStyleParts.push(`flex-wrap: ${wrap === true ? 'wrap' : wrap};`);
    }

    const normalizedMaxWidth = normalizeDimensionValue(maxWidth);
    if (normalizedMaxWidth) {
        innerStyleParts.push(`max-width: ${normalizedMaxWidth};`);
        innerStyleParts.push('margin-left: auto;');
        innerStyleParts.push('margin-right: auto;');
    }
    const normalizedWidth = normalizeDimensionValue(explicitWidth);
    if (normalizedWidth) {
        innerStyleParts.push(`width: ${normalizedWidth};`);
    }
    const innerStyleAttr = buildStyleString(innerStyleParts);

    const componentsPath = [...path, 'components'];
    let innerHTML = renderComponentsList(components, componentsPath, mode);
    if (mode === 'preview' && components.length === 0) {
        innerHTML = '<div class="section-placeholder">Drop components here...</div>';
    }

    const innerWrapper = innerStyleAttr
        ? `<div class="section__content" style="${innerStyleAttr}">${innerHTML}</div>`
        : `<div class="section__content">${innerHTML}</div>`;

    const sectionMarkup = `<${tag} class="section" style="${outerStyleAttr}">
            ${innerWrapper}
        </${tag}>`;

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">section</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${sectionMarkup}
                </div>`;
    }

    return sectionMarkup;
}
/**
 * @function renderImageComponent
 * @description Renders an image component.
 * @param {object} component - The image component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the image.
 * @calledBy {renderComponent}
 * @calls {generateRemainingStyles|toRem|renderComponentsList|registerComponentPath}
 */
function renderImageComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const src = getNestedValue(properties, ['source', 'url']);
    const alt = getNestedValue(properties, ['source', 'altText']);
    const height = getNestedValue(properties, ['presentation', 'height']);
    const link = properties.link;
    const styles = generateRemainingStyles(properties);
    let imageHTML = `<img src="${src || 'https://via.placeholder.com'}" alt="${alt || ''}" style="width: 100%; height: ${toRem(height) || 'auto'}; object-fit: cover;">`;
    if (link) {
        imageHTML = `<a href="${link}">${imageHTML}</a>`;
    }
    let nestedComponentsHTML = '';
    if (components.length > 0) {
        const componentsPath = [...path, 'components'];
        nestedComponentsHTML = renderComponentsList(components, componentsPath, mode);
    }
    const contentHTML = `<div class="image-component-container" style="${styles}">
        ${imageHTML}
        <div class="image-nested-components">
            ${nestedComponentsHTML}
        </div>
    </div>`;
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return `<div class="rendered-component" data-component-id="${componentId}" >
                    <div class="component-label">image</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }
    return contentHTML;
}

/**
 * Renders a simple component.
 * @param {object} component The component to render.
 * @param {Array} path The path to the component in the YAML structure.
 * @param {string} mode The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML.
 */
export function renderSimpleComponent(component, path, mode) {
    const { name, properties = {} } = component;
    const styles = generateRemainingStyles(properties, name);
    const componentHTML = generateComponentInnerHTML(name, properties, '', styles, mode);
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        if (name === 'titlebar') {
            const idMatch = componentHTML.match(/id="([^"]+)"/);
            if (idMatch && idMatch[1]) {
                registerComponentForInitialization('titlebar', idMatch[1], properties);
            }
        }
        
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">${name}</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${componentHTML}
                </div>`;
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
    
    let contentHTML = `<div class="row">`;
    
    for (let i = 0; i < columnCount; i++) {
        const columnComponents = columns[i] ? columns[i].components || [] : [];
        const columnPath = [...path, 'columns', i, 'components'];
        
        contentHTML += `<div class="col-sm" style="position: relative;">`;
        
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
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">columnsgrid</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }
    
    return contentHTML;
}
/**
 * @function renderAccordion
 * @description Renders an accordion component.
 * @param {object} component - The accordion component object.
 * @param {Array} path - The path to the component in the YAML structure.
 * @param {string} mode - The rendering mode ('preview' or 'export').
 * @returns {string} The rendered HTML for the accordion.
 * @calledBy {renderComponent}
 * @calls {renderComponentsList|registerComponentPath}
 */
function renderAccordion(component, path, mode) {
    const { properties = {}, content } = component;
    const title = properties.title || 'Click to expand';
    
    let contentHTML = '';
    if (content && content.components) {
        const contentPath = [...path, 'content', 'components'];
        contentHTML = renderComponentsList(content.components, contentPath, mode);
    }
    const accordionHTML = `<details class="accordion">
        <summary class="accordion-summary">${title}</summary>
        <div class="card">
            <div class="card-body">${contentHTML}</div>
        </div>
    </details>`;
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">accordion</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${accordionHTML}
                </div>`;
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
    
    let tabsHTML = `<div class="tabs">`;
    tabs.forEach((tab, i) => {
        const tabId = `${tabsId}_${i}`;
        const tabTitle = tab.title || `Tab ${i + 1}`;
        const tabComponents = tab.components || [];
        const tabPath = [...path, 'tabs', i, 'components'];
        
        tabsHTML += `<input type="radio" name="${tabsId}" id="${tabId}" ${i === 0 ? 'checked' : ''} />`;
        tabsHTML += `<label for="${tabId}">${tabTitle}</label>`;
        
        const tabContent = renderComponentsList(tabComponents, tabPath, mode);
        tabsHTML += `<div class="content"><div>${tabContent}</div></div>`;
    });
    
    tabsHTML += `</div>`;
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">tabs</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${tabsHTML}
                </div>`;
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
            return '<h' + level + attrSegment + '>' + textContent + '</h' + level + '>';  ;
    }
    
    if (componentType === 'paragraph') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Paragraph');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }
    if (componentType === 'eyebrow') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Label');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }
    if (componentType === 'caption') {
        const textContent = escapeHtmlWithLineBreaks(componentProps.text || 'Caption');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }
    if (componentType === 'blockquote') {
        const quoteContent = escapeHtmlWithLineBreaks(componentProps.quote || componentProps.text || 'Quote');
        const citation = componentProps.cite ? '<figcaption class="blockquote-citation">&mdash; ' + escapeHtml(componentProps.cite) + '</figcaption>' : '';
        return '<figure' + attrSegment + '><blockquote>' + quoteContent + '</blockquote>' + citation + '</figure>';
    }
    const finalAttrs = attributeString;
    if (componentType === 'image') {
        return '<img src="' + (componentProps.src || 'https://via.placeholder.com/150') + '" alt="' + (componentProps.alt || '') + '" style="width: 100%; height: ' + (toRem(componentProps.height) || 'auto') + '; object-fit: cover;">';
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
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><input type="text" id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" value="' + (componentProps.value || '') + '" ' + finalAttrs + ' /></div>';
    } else if (componentType === 'textarea') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><textarea id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" rows="' + (componentProps.rows || 3) + '" ' + finalAttrs + '>' + (componentProps.value || '') + '</textarea></div>';
    } else if (componentType === 'button') {
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
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><select id="' + id + '" ' + finalAttrs + '>' + optionHTML + '</select></div>';
    } else if (componentType === 'calendar') {
        return generateCalendarHTML(componentProps);
    } else if (componentType === 'checkbox') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + finalAttrs + ' style="' + labelStyles + '"><input type="checkbox" id="' + id + '"' + (componentProps.checked ? ' checked' : '') + ' /><span>' + (componentProps.text || 'Check me') + '</span></label></div>';
    } else if (componentType === 'radio') {
        const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');
        return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + finalAttrs + ' style="' + labelStyles + '"><input type="radio" id="' + id + '" name="' + (componentProps.name || 'radio1') + '" value="' + (componentProps.value || 'option1') + '" /><span>' + (componentProps.text || 'Select me') + '</span></label></div>';
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
    const contentMarkup = sections.join('\n');

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
    if (backgroundImage) {
        styles += `background-image: url('${backgroundImage}');`;
        styles += 'background-size: cover;';
        styles += 'background-position: center;';
    } else if (backgroundColor) {
        styles += `background-color: ${backgroundColor};`;
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
            if (resolved !== null) {
                styles += `margin-${side}: ${resolved};`;
            }
        }
    } else if (props.margin) {
        styles += `margin: ${toRem(props.margin)};`;
    }
    const paddingGroup = spacingGroup.padding || layout.padding;
    if (paddingGroup && typeof paddingGroup === 'object') {
        for (const side of Object.keys(paddingGroup)) {
            const resolved = resolveSpacingValue(paddingGroup[side]);
            if (resolved !== null) {
                styles += `padding-${side}: ${resolved};`;
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
    const borderRadius = borderGroup.radius ?? props.borderRadius;
    if (borderRadius) {
        const radiusValue = typeof borderRadius === 'number' ? `${borderRadius}px` : toRem(borderRadius);
        styles += `border-radius: ${radiusValue};`;
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








