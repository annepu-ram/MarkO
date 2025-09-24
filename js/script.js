// --- YAML-BASED WEBSITE BUILDER //---
// Load js-yaml from CDN - add to HTML: <script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>

// =================================================================================================
// --- INITIALIZATION ---
// =================================================================================================

document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    await loadComponentTemplates();
    initializeEventListeners();
    initializeComponentButtons();
    initializeResizer();
    
    const editor = document.getElementById('codeEditor');
    history.push(editor.value);
    parseYamlComponents(editor.value);
}

async function loadComponentTemplates() {
    try {
        const response = await fetch('component_defaults.yaml');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const yamlText = await response.text();
        componentTemplates = jsyaml.load(yamlText);
        isComponentTemplatesLoaded = true;
    } catch (error) {
        console.error('Failed to load component templates:', error);
    }
}

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

function initializeEventListeners() {
    const editor = document.getElementById('codeEditor');
    const debouncedParse = debounce(value => {
        history.push(value);
        parseYamlComponents(value);
    }, 500);

    editor.addEventListener('input', () => {
        debouncedParse(editor.value);
    });
    editor.addEventListener('keydown', handleKeyDown);

    document.getElementById('preview').addEventListener('click', handlePreviewClick);
    document.getElementById('exportBtn').addEventListener('click', exportCode);
    document.getElementById('clearBtn').addEventListener('click', clearCanvas);
    document.getElementById('fullscreenBtn').addEventListener('click', openFullscreen);
    document.getElementById('closeFullscreenBtn').addEventListener('click', closeFullscreen);
    document.getElementById('helpBtn').addEventListener('click', toggleHelpPanel);
}

// =================================================================================================
// --- STATE MANAGEMENT ---
// =================================================================================================

let componentTemplates = {};
let isComponentTemplatesLoaded = false;
let selectedComponentElement = null;
let componentIdToPathMap = {};
let yamlStructure = null;
let componentsToInitialize = [];

const TYPOGRAPHY_SIZE_MAP = {
    xxs: '1rem',
    xs: '1.2rem',
    sm: '1.4rem',
    md: '1.6rem',
    lg: '2rem',
    xl: '2.4rem',
    xxl: '3.2rem',
    xxxl: '3.6rem'
};

const FONT_WEIGHT_MAP = {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800
};

const LETTER_SPACING_MAP = {
    normal: 'normal',
    tight: '-0.015em',
    wide: '0.1em',
    wider: '0.15em'
};

const LINE_HEIGHT_MAP = {
    normal: 1.5,
    snug: 1.35,
    relaxed: 1.7,
    loose: 1.9
};

const SPACING_SCALE_MAP = {
    none: '0',
    xs: '0.4rem',
    sm: '0.8rem',
    md: '1.6rem',
    lg: '2.4rem',
    xl: '3.2rem'
};

const TEXT_VARIANTS = {
    paragraph: {
        body: {},
        lead: {
            typography: { size: 'lg', lineHeight: 1.75 },
            spacing: { margin: { top: 'sm', bottom: 'lg' } }
        },
        muted: {
            typography: { color: '#6b7280' }
        },
        note: {
            typography: { size: 'sm', color: '#6b7280', lineHeight: 1.5 }
        }
    }
};

const TEXT_COMPONENTS = new Set(['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote']);

const SPACING_OPTIONS = ['none', 'xs', 'sm', 'md', 'lg', 'xl'];


function deepClone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
}

function deepMerge(target = {}, ...sources) {
    for (const source of sources) {
        if (!source || typeof source !== 'object') continue;
        for (const key of Object.keys(source)) {
            const sourceValue = source[key];
            if (Array.isArray(sourceValue)) {
                target[key] = sourceValue.map(item => (typeof item === 'object' && item !== null) ? deepClone(item) : item);
            } else if (sourceValue && typeof sourceValue === 'object') {
                const base = target[key];
                target[key] = deepMerge((base && typeof base === 'object') ? base : {}, sourceValue);
            } else if (sourceValue !== undefined) {
                target[key] = sourceValue;
            }
        }
    }
    return target;
}

function cloneTemplate(template = {}) {
    return deepClone(template) || {};
}

function resolveComponentVariant(name, properties = {}) {
    const variants = TEXT_VARIANTS[name];
    if (!variants) {
        return properties;
    }
    const variantKeys = Object.keys(variants);
    if (variantKeys.length === 0) {
        return properties;
    }
    const defaultKey = variantKeys.includes('default') ? 'default' : variantKeys[0];
    const variantKey = properties.variant && variants[properties.variant] ? properties.variant : defaultKey;
    const base = variants.default && variantKey !== 'default' ? variants.default : {};
    const selected = variants[variantKey] || {};
    return deepMerge({}, base, selected, properties);
}


function resolveTypographySize(value) {
    if (!value) return null;
    if (TYPOGRAPHY_SIZE_MAP[value]) {
        return TYPOGRAPHY_SIZE_MAP[value];
    }
    return typeof value === 'number' ? toRem(value) : value;
}

function resolveFontWeight(value) {
    if (!value) return null;
    if (FONT_WEIGHT_MAP[value] !== undefined) {
        return FONT_WEIGHT_MAP[value];
    }
    return value;
}

function resolveLineHeight(value) {
    if (!value) return null;
    if (LINE_HEIGHT_MAP[value] !== undefined) {
        return LINE_HEIGHT_MAP[value];
    }
    return value;
}

function resolveLetterSpacing(value) {
    if (!value) return null;
    if (LETTER_SPACING_MAP[value] !== undefined) {
        return LETTER_SPACING_MAP[value];
    }
    return value;
}

function resolveSpacingValue(value) {
    if (value === undefined || value === null || value === '') {
        return null;
    }
    if (SPACING_SCALE_MAP[value] !== undefined) {
        return SPACING_SCALE_MAP[value];
    }
    if (value === 'auto') {
        return 'auto';
    }
    if (typeof value === 'number') {
        return toRem(value);
    }
    const numeric = parseFloat(value);
    if (!Number.isNaN(numeric) && String(value).trim() === `${numeric}`) {
        return toRem(numeric);
    }
    return value;
}

function escapeHtml(value) {
    if (typeof value !== 'string') return value;
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
const history = {
    undoStack: [],
    redoStack: [],
    maxSize: 50,

    push: function(state) {
        if (this.undoStack.length >= this.maxSize) {
            this.undoStack.shift();
        }
        this.undoStack.push(state);
        this.redoStack = [];
    },

    undo: function() {
        if (this.undoStack.length > 1) {
            const currentState = this.undoStack.pop();
            this.redoStack.push(currentState);
            return this.undoStack[this.undoStack.length - 1];
        }
        return null;
    },

    redo: function() {
        if (this.redoStack.length > 0) {
            const nextState = this.redoStack.pop();
            this.undoStack.push(nextState);
            return nextState;
        }
        return null;
    }
};

// =================================================================================================
// --- COMPONENT INITIALIZATION ---
// =================================================================================================

function registerComponentForInitialization(name, id, props = {}) {
    componentsToInitialize.push({ name, id, props });
}

function initializeAllComponents() {
    for (const comp of componentsToInitialize) {
        const element = document.getElementById(comp.id);
        if (element && componentInitializers[comp.name]) {
            componentInitializers[comp.name](element, comp.props);
        }
    }
    // Reset for the next render cycle
    componentsToInitialize = [];
}


// =================================================================================================
// --- EVENT HANDLERS ---
// =================================================================================================

function handlePreviewClick(event) {
    if (event.target.classList.contains('delete-component-btn')) {
        const componentId = event.target.dataset.componentId;
        deleteComponent(componentId);
        event.stopPropagation();
        return;
    }

    if (!isComponentTemplatesLoaded) return;

    const target = event.target.closest('.rendered-component');
    if (selectedComponentElement) {
        selectedComponentElement.style.borderStyle = 'solid';
        selectedComponentElement.style.borderColor = '#404A6B';
        selectedComponentElement.style.borderWidth = '1px';
    }
    if (!target) {
        selectedComponentElement = null;
        renderPropertiesPanel(null, null);
        return;
    }
    selectedComponentElement = target;
    selectedComponentElement.style.border = '2px solid #ef4444';
    
    const componentId = target.dataset.componentId;
    const path = componentIdToPathMap[componentId];
    
    if (!path) return;

    const component = getComponentByPath(yamlStructure, path);
    renderPropertiesPanel(component, componentId, path);
}

function handleKeyDown(event) {
    const editor = document.getElementById('codeEditor');
    const start = editor.selectionStart;
    const end = editor.selectionEnd;

    if (event.key === 'Tab') {
        event.preventDefault();

        if (start !== end) {
            const selectedText = editor.value.substring(start, end);
            const selectedLines = selectedText.split('\n');
            
            if (event.shiftKey) {
                // Remove indentation
                const newSelectedLines = selectedLines.map(line => {
                    if (line.startsWith('  ')) {
                        return line.substring(2);
                    }
                    return line;
                });
                const newSelectedText = newSelectedLines.join('\n');
                editor.value = editor.value.substring(0, start) + newSelectedText + editor.value.substring(end);
                editor.selectionStart = start;
                editor.selectionEnd = start + newSelectedText.length;
            } else {
                // Add indentation
                const newSelectedLines = selectedLines.map(line => '  ' + line);
                const newSelectedText = newSelectedLines.join('\n');
                editor.value = editor.value.substring(0, start) + newSelectedText + editor.value.substring(end);
                editor.selectionStart = start;
                editor.selectionEnd = start + newSelectedText.length;
            }
        } else {
            // Insert 2 spaces if no text is selected
            editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + 2;
        }
    } else if (event.ctrlKey && event.key === 'z') {
        event.preventDefault();
        const previousState = history.undo();
        if (previousState !== null) {
            editor.value = previousState;
            parseYamlComponents(editor.value);
        }
    } else if (event.ctrlKey && event.key === 'y') {
        event.preventDefault();
        const nextState = history.redo();
        if (nextState !== null) {
            editor.value = nextState;
            parseYamlComponents(editor.value);
        }
    }
}

// =================================================================================================
// --- YAML PROCESSING ---
// =================================================================================================

function parseYamlContent(yamlText) {
    try {
        if (typeof jsyaml === 'undefined') {
            throw new Error('js-yaml library not loaded');
        }
        // Trim whitespace before parsing
        const trimmedYamlText = yamlText.trim();
        return jsyaml.load(trimmedYamlText);
    } catch (error) {
        console.error('YAML parsing error:', error);
        return null;
    }
}

function generateYamlFromStructure(structure) {
    try {
        if (typeof jsyaml === 'undefined') {
            throw new Error('js-yaml library not loaded');
        }
        return jsyaml.dump(structure, {
            indent: 2,
            lineWidth: -1,
            noRefs: true,
            sortKeys: false
        });
    } catch (error) {
        console.error('YAML generation error:', error);
        return '';
    }
}

function getComponentByPath(structure, path) {
    if (!structure || !path || path.length === 0) return null;
    
    let current = structure;
    for (let i = 0; i < path.length; i++) {
        const key = path[i];
        if (current[key] === undefined) return null;
        current = current[key];
    }
    return current;
}

function updateComponentByPath(structure, path, newComponent) {
    if (!structure || !path || path.length === 0) return; 
    
    let current = structure;
    for (let i = 0; i < path.length - 1; i++) {
        const key = path[i];
        if (current[key] === undefined) return;
        current = current[key];
    }
    
    const lastKey = path[path.length - 1];
    if (current[lastKey] !== undefined) {
        current[lastKey] = { ...current[lastKey], ...newComponent };
    }
}

function deleteComponentByPath(structure, path) {
    let current = structure;
    for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]];
    }

    const lastKey = path[path.length - 1];
    if (Array.isArray(current) && typeof lastKey === 'number') {
        current.splice(lastKey, 1);
    } else if (typeof current === 'object' && current !== null) {
        delete current[lastKey];
    }
}

function deleteComponent(componentId) {
    const path = componentIdToPathMap[componentId];
    if (!path) return;

    deleteComponentByPath(yamlStructure, path);

    const newYaml = generateYamlFromStructure(yamlStructure);
    document.getElementById('codeEditor').value = newYaml;
    parseYamlComponents(newYaml);
    renderPropertiesPanel(null, null);
}

function insertYamlComponent(componentName) {
    if (!isComponentTemplatesLoaded) return;

    const editor = document.getElementById('codeEditor');
    const template = cloneTemplate(componentTemplates[componentName]);

    let newComponent;
    if (componentName === 'page') {
        newComponent = {
            name: 'page',
            properties: template || {},
            components: []
        };
        const newComponentYaml = jsyaml.dump([newComponent], {
            indent: 2,
            lineWidth: -1,
            noRefs: true,
            sortKeys: false
        });
        editor.value = newComponentYaml;
        parseYamlComponents(editor.value);
        editor.focus();
        return;
    } else if (componentName === 'tabs') {
        const properties = template || {};
        newComponent = {
            name: 'tabs',
            properties,
            tabs: [{ title: 'Tab Name', components: [] }]
        };
    } else if (componentName === 'carousel') {
        const { slides = [], ...properties } = template || {};
        newComponent = {
            name: 'carousel',
            properties,
            slides
        };
    } else if (componentName === 'accordion') {
        const properties = template || {};
        newComponent = {
            name: 'accordion',
            properties,
            content: {
                components: []
            }
        };
    } else if (componentName === 'form') {
        const properties = template || {};
        newComponent = {
            name: 'form',
            properties,
            components: []
        };
    } else if (componentName === 'image') {
        const properties = template || {};
        newComponent = {
            name: 'image',
            properties,
            components: []
        };
    } else {
        newComponent = {
            name: componentName,
            properties: template || {}
        };
    }

    let structure = parseYamlContent(editor.value);

    if (!structure || !Array.isArray(structure) || structure.length !== 1 || structure[0].name !== 'page') {
        structure = [{
            name: 'page',
            properties: {},
            components: [newComponent]
        }];
    } else {
        if (!Array.isArray(structure[0].components)) {
            structure[0].components = [];
        }
        structure[0].components.push(newComponent);
    }

    const newYaml = generateYamlFromStructure(structure);
    editor.value = newYaml;
    parseYamlComponents(newYaml);
    editor.focus();
}

// =================================================================================================
// --- COMPONENT RENDERING ---
// =================================================================================================

function renderYamlStructure(structure, mode = 'preview') {
    componentIdToPathMap = {};
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

function renderComponentsList(components, basePath, mode) {
    let html = '';
    
    components.forEach((component, index) => {
        const componentPath = [...basePath, index];
        html += renderComponent(component, componentPath, mode);
    });

    return html;
}

function renderComponent(component, path, mode) {
    if (!component || !component.name) return '';
    const {
        name,
        properties = {} 
    } = component;
    switch (name) {
        case 'page':
            return renderPageComponent(component, path, mode);
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
        componentIdToPathMap[componentId] = path;
        registerComponentForInitialization('carousel', carouselId, properties);

        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">carousel</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }

    return contentHTML;
}


function renderFormComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const componentsPath = [...path, 'components'];
    let contentHTML = renderComponentsList(components, componentsPath, mode);

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        componentIdToPathMap[componentId] = path;
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
        componentIdToPathMap[componentId] = path;

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

function renderImageComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const { src, alt, height, link } = properties;

    const styles = generateRemainingStyles(properties);
    let imageHTML = `<img src="${src || 'https://via.placeholder.com/150'}" alt="${alt || ''}" style="width: 100%; height: ${toRem(height) || 'auto'}; object-fit: cover;">`;

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
        componentIdToPathMap[componentId] = path;
        return `<div class="rendered-component" data-component-id="${componentId}" >
                    <div class="component-label">image</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }

    return contentHTML;
}

function renderSimpleComponent(component, path, mode) {
    const { name, properties = {} } = component;
    const resolvedProps = resolveComponentVariant(name, properties);
    const classes = generateMiniCssClasses(name, resolvedProps);
    const styles = generateRemainingStyles(resolvedProps, name);
    const componentHTML = generateComponentInnerHTML(name, resolvedProps, classes, styles, mode);

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        componentIdToPathMap[componentId] = path;

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

function renderColumnsGrid(component, path, mode) {
    const { properties = {}, columns = [] } = component;
    const columnCount = parseInt(properties.count) || 2;
    
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
        componentIdToPathMap[componentId] = path;
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">columnsgrid</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${contentHTML}
                </div>`;
    }
    
    return contentHTML;
}

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
        componentIdToPathMap[componentId] = path;
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">accordion</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${accordionHTML}
                </div>`;
    }
    
    return accordionHTML;
}

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
        componentIdToPathMap[componentId] = path;
        return `<div class="rendered-component" data-component-id="${componentId}">
                    <div class="component-label">tabs</div>
                    <div class="delete-component-btn" data-component-id="${componentId}">&#10006;</div>
                    ${tabsHTML}
                </div>`;
    }
    
    return tabsHTML;
}

function generateComponentInnerHTML(type, props, classes, styleAttr, mode) {
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
        const textContent = escapeHtml(componentProps.text || 'Heading');
        return '<h' + level + attrSegment + '>' + textContent + '</h' + level + '>';
    }

    if (componentType === 'paragraph') {
        const textContent = escapeHtml(componentProps.text || 'Paragraph');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }

    if (componentType === 'eyebrow') {
        const textContent = escapeHtml(componentProps.text || 'Label');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }

    if (componentType === 'caption') {
        const textContent = escapeHtml(componentProps.text || 'Caption');
        return '<p' + attrSegment + '>' + textContent + '</p>';
    }

    if (componentType === 'blockquote') {
        const quoteContent = escapeHtml(componentProps.quote || componentProps.text || 'Quote');
        const citation = componentProps.cite ? '<figcaption class="blockquote-citation">&mdash; ' + escapeHtml(componentProps.cite) + '</figcaption>' : '';
        return '<figure' + attrSegment + '><blockquote>' + quoteContent + '</blockquote>' + citation + '</figure>';
    }

    const finalAttrs = attributeString;
    const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    const labelStyles = generateRemainingStyles(componentProps.label_properties || {}, 'label');

    const componentGenerators = {
        image: () => '<img src="' + (componentProps.src || 'https://via.placeholder.com/150') + '" alt="' + (componentProps.alt || '') + '" style="width: 100%; height: ' + (toRem(componentProps.height) || 'auto') + '; object-fit: cover;">',
        video: () => {
            const videoId = (componentProps.src || '').split('v=')[1];
            const embedUrl = videoId ? 'https://www.youtube.com/embed/' + videoId.split('&')[0] : '';
            return '<iframe ' + finalAttrs + ' src="' + embedUrl + '" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width: 100%; aspect-ratio: 16/9;"></iframe>';
        },
        gif: () => '<img src="' + (componentProps.src || 'https://media.giphy.com/media/VseXoJs6vVmwU/giphy.gif') + '" alt="gif" ' + finalAttrs + ' />',
        textbox: () => '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><input type="text" id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" value="' + (componentProps.value || '') + '" ' + finalAttrs + ' /></div>',
        textarea: () => '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><textarea id="' + id + '" placeholder="' + (componentProps.placeholder || 'Enter text...') + '" rows="' + (componentProps.rows || 3) + '" ' + finalAttrs + '>' + (componentProps.value || '') + '</textarea></div>',
        button: () => '<button onclick="' + (componentProps.onclick || '') + '" ' + finalAttrs + '>' + (componentProps.text || 'Click Me') + '</button>',
        dropdown: () => {
            const options = (componentProps.options || 'Option 1,Option 2,Option3').split(',');
            const optionHTML = options.map(opt => {
                const value = opt.trim();
                const selected = componentProps.selected === value ? ' selected' : '';
                return '<option value="' + value + '"' + selected + '>' + value + '</option>';
            }).join('');
            return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label><select id="' + id + '" ' + finalAttrs + '>' + optionHTML + '</select></div>';
        },
        calendar: () => generateCalendarHTML(componentProps),
        checkbox: () => '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + finalAttrs + ' style="' + labelStyles + '"><input type="checkbox" id="' + id + '"' + (componentProps.checked ? ' checked' : '') + ' /><span>' + (componentProps.text || 'Check me') + '</span></label></div>',
        radio: () => '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" ' + finalAttrs + ' style="' + labelStyles + '"><input type="radio" id="' + id + '" name="' + (componentProps.name || 'radio1') + '" value="' + (componentProps.value || 'option1') + '" /><span>' + (componentProps.text || 'Select me') + '</span></label></div>',
        hamburger: () => {
            const items = (componentProps.items || 'Home,About,Services,Contact').split(',');
            let menuHTML = '<div class="dropdown" ' + finalAttrs + '><button class="button primary">?</button><div class="menu">';
            items.forEach(item => { menuHTML += '<a href="#" class="menu-item">' + item.trim() + '</a>'; });
            menuHTML += '</div></div>';
            return menuHTML;
        },
        br: () => mode === 'preview' ? '<div class="comp-br" style="height: 2rem; border-bottom: 1px dashed #ccc; margin: 1rem 0;"></div>' : '<br>',
        titlebar: () => generateTitlebarHTML(componentProps, classes, styleAttr, mode),
        link: () => {
            let linkStyle = componentProps.underline ? 'text-decoration: underline;' : 'text-decoration: none;';
            const arrowHTML = componentProps.showArrow ? '&nbsp;?' : '';
            const sanitizedStyles = styleString.replace(/text-align:[^;]+;/g, '');
            return '<div style="text-align: ' + (componentProps.textAlign || 'left') + ';"><a href="' + (componentProps.url || '#') + '" style="' + linkStyle + ' ' + sanitizedStyles + '">' + (componentProps.text || 'Click Me') + arrowHTML + '</a></div>';
        }
    };

    return componentGenerators[componentType] ? componentGenerators[componentType]() : '<div style="color: #ef4444; font-style: italic;">Unknown component: ' + componentType + '</div>';
}

function generateTitlebarHTML(props, classes, styleAttr, mode) {
    const alignmentClass = getAlignmentClass(props.alignment);
    const logoPosition = props.logoPosition === 'right' ? 'right' : 'left';
    const logoHTML = props.logo ? `<img src="${props.logo}" alt="Logo" class="titlebar-logo" />` : '';
    const titleHTML = props.title ? `<h1 class="titlebar-title">${props.title}</h1>` : '';
    const linksHTML = generateTitlebarLinks(props.links, props);
    const brandClass = `titlebar-brand ${logoPosition === 'right' ? 'logo-right' : 'logo-left'}`;

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
        const rawHeight = props.height;
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

    const titleFontSize = ensureRem(props.titleFontSize, 24);
    const menuFontSize = ensureRem(props.menuFontSize, 16);
    const shrinkPercentRaw = props.shrinkPercent ?? 50;
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
    styleFragments.push(`--shrink-scale: ${shrinkScale};`);
    const combinedStyles = styleFragments.join(' ');
    const brandContent = logoPosition === 'right' ? `${titleHTML}${logoHTML}` : `${logoHTML}${titleHTML}`;

    return `
        <nav class="titlebar ${alignmentClass} ${classes}" style="${combinedStyles}" data-base-height="${baseHeightPx}" data-logo-position="${logoPosition}" id="${titlebarId}">
            <div class="${brandClass}">
                ${brandContent}
            </div>
            <button type="button" class="mobile-menu-button">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </button>
            <div class="titlebar-nav">
                ${linksHTML}
            </div>
        </nav>
    `;
}

function generateMiniCssClasses(type, props) {
    const classes = [];
    if (type === 'button') {
        classes.push('button');
        if (props.variant) {
            classes.push(props.variant);
        }
    }

    if (TEXT_COMPONENTS.has(type)) {
        classes.push('text-' + type);
        const variantMap = TEXT_VARIANTS[type];
        if (variantMap) {
            const variant = props.variant && props.variant !== 'default' && variantMap[props.variant] ? props.variant : null;
            if (variant) {
                classes.push('text-' + type + '--' + variant);
            }
        }
    }

    if (type === 'blockquote') {
        classes.push('blockquote');
    }

    return classes.join(' ').trim();
}

function generateRemainingStyles(props = {}, componentName) {
    let styles = '';

    if (props.backgroundImage) {
        styles += "background-image: url('" + props.backgroundImage + "');";
        styles += 'background-size: cover;';
        styles += 'background-position: center;';
    } else if (props.backgroundColor) {
        if (typeof props.backgroundColor === 'object' && props.backgroundColor !== null) {
            styles += 'background-image: linear-gradient(' + props.backgroundColor.direction + ', ' + props.backgroundColor.start + ', ' + props.backgroundColor.end + ');';
        } else if (props.backgroundColor === 'transparent') {
            styles += 'background-color: transparent;';
        } else {
            styles += 'background-color: ' + props.backgroundColor + ';';
        }
    }

    const typography = props.typography || {};
    const fontSize = resolveTypographySize(typography.size || props.fontSize);
    if (fontSize) {
        styles += 'font-size: ' + fontSize + ';';
    }
    const fontWeight = resolveFontWeight(typography.weight || props.fontWeight);
    if (fontWeight) {
        styles += 'font-weight: ' + fontWeight + ';';
    }
    const fontStyle = typography.fontStyle || props.fontStyle;
    if (fontStyle) {
        styles += 'font-style: ' + fontStyle + ';';
    }
    const textTransform = typography.transform || props.transform;
    if (textTransform) {
        styles += 'text-transform: ' + textTransform + ';';
    }
    const letterSpacing = resolveLetterSpacing(typography.letterSpacing || props.letterSpacing);
    if (letterSpacing) {
        styles += 'letter-spacing: ' + letterSpacing + ';';
    }
    const lineHeight = resolveLineHeight(typography.lineHeight || props.lineHeight);
    if (lineHeight) {
        styles += 'line-height: ' + lineHeight + ';';
    }
    const textAlign = typography.align || props.textAlign;
    if (textAlign) {
        styles += 'text-align: ' + textAlign + ';';
    }
    const color = typography.color || props.color;
    if (color) {
        styles += 'color: ' + color + ';';
    }

    const spacing = props.spacing || {};
    if (spacing.margin && typeof spacing.margin === 'object') {
        for (const side in spacing.margin) {
            if (Object.prototype.hasOwnProperty.call(spacing.margin, side)) {
                const resolved = resolveSpacingValue(spacing.margin[side]);
                if (resolved !== null) {
                    styles += 'margin-' + side + ': ' + resolved + ';';
                }
            }
        }
    } else if (props.margin) {
        styles += 'margin: ' + toRem(props.margin) + ';';
    }

    if (spacing.padding && typeof spacing.padding === 'object') {
        for (const side in spacing.padding) {
            if (Object.prototype.hasOwnProperty.call(spacing.padding, side)) {
                const resolved = resolveSpacingValue(spacing.padding[side]);
                if (resolved !== null) {
                    styles += 'padding-' + side + ': ' + resolved + ';';
                }
            }
        }
    } else if (props.padding) {
        styles += 'padding: ' + toRem(props.padding) + ';';
    }

    if (props.borderWidth !== undefined && props.borderWidth !== null) {
        const borderWidthValue = toRem(props.borderWidth);
        const borderStyle = props.borderStyle || 'solid';
        if (parseFloat(borderWidthValue) > 0 && borderStyle !== 'none') {
            styles += 'border: ' + borderWidthValue + ' ' + borderStyle + ' ' + (props.borderColor || '#000000') + ';';
        }
    }
    if (props.borderRadius) {
        styles += 'border-radius: ' + toRem(props.borderRadius) + ';';
    }

    return styles;
}

// =================================================================================================
// --- PROPERTIES PANEL ---
// =================================================================================================

function renderPropertiesPanel(component, componentId, path) {
    const propertiesContent = document.getElementById('propertiesContent');
    const existingButton = document.querySelector('.btn-apply-props');
    if (existingButton) existingButton.remove();

    if (!component || !componentId) {
        propertiesContent.innerHTML = '<p style="color: #666; font-style: italic; font-size: 1.2rem; text-align: center; padding: 2rem 0;">Select a component to edit.</p>';
        return;
    }

    let propertiesHTML = '';
    const templateProps = cloneTemplate(componentTemplates[component.name] || {});
    const finalProps = deepMerge({}, templateProps, component.properties || {});
    const isTextComponent = TEXT_COMPONENTS.has(component.name);

    if (isTextComponent) {
        propertiesHTML += renderTextComponentProperties(component.name, finalProps);
    } else {
        for (const key in finalProps) {
            if (!Object.prototype.hasOwnProperty.call(finalProps, key)) continue;
            if (key === 'content' || key === 'columns' || key === 'tabs' || key === 'components' || key === 'slides' || key === 'backgroundImage' || key === 'label_properties' || key === 'variants') continue;
            if (typeof finalProps[key] === 'object' && finalProps[key] !== null && key !== 'backgroundColor') continue;

            const value = finalProps[key] === undefined ? '' : finalProps[key];
            propertiesHTML += renderProperty(key, value);
        }

        if (component.name === 'titlebar') {
            const links = Array.isArray(finalProps.links) ? finalProps.links : [];
            propertiesHTML += generateLinksEditor(links);
        }

        if (finalProps.label_properties) {
            propertiesHTML += '<h4>Label Properties</h4>';
            for (const key in finalProps.label_properties) {
                if (!Object.prototype.hasOwnProperty.call(finalProps.label_properties, key)) continue;
                const value = finalProps.label_properties[key] === undefined ? '' : finalProps.label_properties[key];
                propertiesHTML += renderProperty(key, value, 'label_properties');
            }
        }

        if (component.name === 'page') {
            propertiesHTML += renderProperty('backgroundImage', finalProps.backgroundImage || '');
        }
    }

    propertiesContent.innerHTML = propertiesHTML;

    const propertiesSection = document.getElementById('propertiesPanel');
    const applyButton = document.createElement('button');
    applyButton.className = 'btn btn-apply-props';
    applyButton.textContent = 'Apply Changes';
    applyButton.onclick = () => applyYamlComponentProperties(componentId, path);
    propertiesSection.appendChild(applyButton);
}
function renderProperty(key, value, propType = null) {
    const colorProperties = ['backgroundColor', 'color', 'borderColor', 'focusedButtonBackgroundColor', 'border_color'];
    const imageProperties = ['backgroundImage'];
    const selectProperties = {
        fontStyle: ['normal', 'italic'],
        fontWeight: ['normal', 'bold', 'lighter'],
        borderStyle: ['none', 'solid', 'dotted', 'dashed', 'double', 'groove', 'ridge', 'inset', 'outset'],
        textAlign: ['left', 'center', 'right'],
        logoPosition: ['left', 'right']
    };

    if (colorProperties.includes(key)) {
        return renderColorProperty(key, value, propType);
    } else if (imageProperties.includes(key)) {
        return renderImageProperty(key, value, propType);
    } else if (selectProperties[key]) {
        return renderSelectProperty(key, value, selectProperties[key], propType);
    } else if (key === 'underline' || key === 'showArrow' || key === 'parallax') {
        return renderParallaxProperty(key, value, propType);
    }
    else {
        return renderTextProperty(key, value, propType);
    }
}

function renderParallaxProperty(key, value, propType) {
    return `
        <div class="property-item">
            <label for="prop_${key}">${key}</label>
            <input type="checkbox" id="prop_${key}" data-key="${key}" ${value ? 'checked' : ''} ${propType ? `data-prop-type="${propType}"` : ''}>
        </div>
    `;
}

function renderImageProperty(key, value, propType) {
    return `<div class="property-item">
        <label for="prop_${key}">${key}</label>
        <input type="text" id="prop_${key}" data-key="${key}" value="${value}" ${propType ? `data-prop-type="${propType}"` : ''}>
    </div>`;
}

function renderTextProperty(key, value, propType) {
    return `<div class="property-item">
        <label for="prop_${key}">${key}</label>
        <input type="text" id="prop_${key}" data-key="${key}" value="${value}" ${propType ? `data-prop-type="${propType}"` : ''}>
    </div>`;
}

function renderColorProperty(key, value, propType) {
    const isGradient = typeof value === 'object' && value !== null && value.direction && value.start && value.end;
    const colorType = isGradient ? 'gradient' : (value === 'transparent' ? 'transparent' : 'solid');

    let solidColor = '#ffffff';
    if (!isGradient && value !== 'transparent') {
        solidColor = value;
    }

    if (typeof solidColor !== 'string' || !solidColor.match(/^#[0-9a-f]{6}$/i)) {
        solidColor = '#000000';
    }
    
    const gradientDir = isGradient ? value.direction : 'to right';
    const gradientStart = isGradient ? value.start : '#ff0000';
    const gradientEnd = isGradient ? value.end : '#0000ff';

    const options = key === 'backgroundColor' ? ['solid', 'gradient', 'transparent'] : ['solid', 'transparent'];
    const optionsHTML = options.map(opt => `<option value="${opt}" ${colorType === opt ? 'selected' : ''}>${opt.charAt(0).toUpperCase() + opt.slice(1)}</option>`).join('');

    return `
        <div class="property-item">
            <label for="prop_color_type_${key}">${key}</label>
            <select id="prop_color_type_${key}" data-key="color_type" onchange="toggleColorFields(this, '${key}')" ${propType ? `data-prop-type="${propType}"` : ''}>
                ${optionsHTML}
            </select>

            <div id="solid_color_fields_${key}" style="display: ${colorType === 'solid' ? 'block' : 'none'};">
                <div class="property-color-container">
                    <input type="text" id="prop_text_${key}" data-key="solid_color" value="${solidColor}" oninput="document.getElementById('prop_color_${key}').value = this.value;" ${propType ? `data-prop-type="${propType}"` : ''}>
                    <input type="color" id="prop_color_${key}" class="color-picker-input" value="${solidColor}" oninput="document.getElementById('prop_text_${key}').value = this.value;" ${propType ? `data-prop-type="${propType}"` : ''}>
                </div>
            </div>

            <div id="gradient_color_fields_${key}" style="display: ${colorType === 'gradient' ? 'block' : 'none'};">
                <label>Direction</label>
                <select id="prop_gradient_dir_${key}" data-key="gradient_direction" ${propType ? `data-prop-type="${propType}"` : ''}>
                    <option value="to top" ${gradientDir === 'to top' ? 'selected' : ''}>to top</option>
                    <option value="to bottom" ${gradientDir === 'to bottom' ? 'selected' : ''}>to bottom</option>
                    <option value="to left" ${gradientDir === 'to left' ? 'selected' : ''}>to left</option>
                    <option value="to right" ${gradientDir === 'to right' ? 'selected' : ''}>to right</option>
                    <option value="to top left" ${gradientDir === 'to top left' ? 'selected' : ''}>to top left</option>
                    <option value="to top right" ${gradientDir === 'to top right' ? 'selected' : ''}>to top right</option>
                    <option value="to bottom left" ${gradientDir === 'to bottom left' ? 'selected' : ''}>to bottom left</option>
                    <option value="to bottom right" ${gradientDir === 'to bottom right' ? 'selected' : ''}>to bottom right</option>
                </select>
                <label>Start Color</label>
                <input type="color" id="prop_gradient_start_${key}" data-key="gradient_start" value="${gradientStart}" ${propType ? `data-prop-type="${propType}"` : ''}>
                <label>End Color</label>
                <input type="color" id="prop_gradient_end_${key}" data-key="gradient_end" value="${gradientEnd}" ${propType ? `data-prop-type="${propType}"` : ''}>
            </div>
        </div>
    `;
}

function toggleColorFields(selectElement, key) {
    const selectedType = selectElement.value;
    document.getElementById(`solid_color_fields_${key}`).style.display = selectedType === 'solid' ? 'block' : 'none';
    document.getElementById(`gradient_color_fields_${key}`).style.display = selectedType === 'gradient' ? 'block' : 'none';
}

function renderSelectProperty(key, value, options, propType) {
    const optionsHTML = options.map(option => 
        `<option value="${option}" ${value === option ? 'selected' : ''}>${option.charAt(0).toUpperCase() + option.slice(1)}</option>`
    ).join('');

    return `<div class="property-item">
        <label for="prop_${key}">${key}</label>
        <select id="prop_${key}" data-key="${key}" ${propType ? `data-prop-type="${propType}"` : ''}>
            ${optionsHTML}
        </select>
    </div>`;
}

function buildSelectOptions(options, selectedValue, defaultLabel) {
    let html = '';
    const selectedString = selectedValue !== undefined && selectedValue !== null ? String(selectedValue) : '';
    if (defaultLabel !== undefined && defaultLabel !== null) {
        const isSelected = selectedString === '' ? ' selected' : '';
        html += '<option value=""' + isSelected + '>' + (defaultLabel || 'Default') + '</option>';
    }
    options.forEach(option => {
        if (option === undefined || option === null || option === '') return;
        const value = String(option);
        const isSelected = value === selectedString ? ' selected' : '';
        html += '<option value="' + value + '"' + isSelected + '>' + formatOptionLabel(value) + '</option>';
    });
    return html;
}

function formatOptionLabel(option) {
    if (option === null || option === undefined) return '';
    if (option === 'none') return 'None';
    if (option === 'xs') return 'XS';
    if (option === 'sm') return 'SM';
    if (option === 'md') return 'MD';
    if (option === 'lg') return 'LG';
    if (option === 'xl') return 'XL';
    if (option === 'auto') return 'Auto';
    const text = String(option).replace(/_/g, ' ');
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function renderTextComponentProperties(type, props) {
    const typography = props.typography || {};
    const spacing = props.spacing || {};
    const margin = spacing.margin || {};
    const variantMap = TEXT_VARIANTS[type];
    const variantOptions = variantMap ? Object.keys(variantMap) : [];
    const sizeOptions = Object.keys(TYPOGRAPHY_SIZE_MAP);
    const weightOptions = Object.keys(FONT_WEIGHT_MAP);
    const alignOptions = ['inherit', 'left', 'center', 'right', 'justify'];
    const letterSpacingOptions = Object.keys(LETTER_SPACING_MAP);
    const transformOptions = ['none', 'uppercase', 'lowercase', 'capitalize'];
    const spacingOptions = [...SPACING_OPTIONS, 'auto'];

    const segments = [];

    if (type === 'blockquote') {
        segments.push('<div class="property-item"><label>Quote</label><textarea data-key="quote" data-allow-empty="true" rows="4">' + escapeHtml(props.quote || props.text || '') + '</textarea></div>');
        segments.push('<div class="property-item"><label>Citation</label><input type="text" data-key="cite" value="' + escapeHtml(props.cite || '') + '"></div>');
    } else {
        const rows = type === 'paragraph' ? 4 : 3;
        segments.push('<div class="property-item"><label>Text</label><textarea data-key="text" data-allow-empty="true" rows="' + rows + '">' + escapeHtml(props.text || '') + '</textarea></div>');
    }

    if (type === 'heading') {
        const levelValue = props.level !== undefined ? props.level : 2;
        let levelOptions = '';
        for (let i = 1; i <= 6; i++) {
            const selected = Number(levelValue) === i ? ' selected' : '';
            levelOptions += '<option value="' + i + '"' + selected + '>H' + i + '</option>';
        }
        segments.push('<div class="property-item"><label>Heading Level</label><select data-key="level" data-type="number">' + levelOptions + '</select></div>');
    }

    if (variantOptions.length > 1) {
        segments.push('<div class="property-item"><label>Variant</label><select data-key="variant">' + buildSelectOptions(variantOptions, props.variant || 'default', null) + '</select></div>');
    }

    segments.push('<div class="property-group"><h4>Typography</h4>');
    segments.push('<div class="property-item"><label>Font Size</label><select data-key="typography.size">' + buildSelectOptions(sizeOptions, typography.size, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Font Weight</label><select data-key="typography.weight">' + buildSelectOptions(weightOptions, typography.weight, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Alignment</label><select data-key="typography.align">' + buildSelectOptions(alignOptions, typography.align, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Line Height</label><input type="text" data-key="typography.lineHeight" value="' + (typography.lineHeight !== undefined ? typography.lineHeight : '') + '" placeholder="e.g. 1.6 or relaxed"></div>');
    segments.push('<div class="property-item"><label>Letter Spacing</label><select data-key="typography.letterSpacing">' + buildSelectOptions(letterSpacingOptions, typography.letterSpacing, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Transform</label><select data-key="typography.transform">' + buildSelectOptions(transformOptions, typography.transform, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Text Color</label><input type="color" data-key="typography.color" value="' + (typography.color !== undefined ? typography.color : '') + '"></div>');
    segments.push('</div>');

    segments.push('<div class="property-group"><h4>Spacing</h4>');
    segments.push('<div class="property-item"><label>Margin Top</label><select data-key="spacing.margin.top">' + buildSelectOptions(spacingOptions, margin.top, null) + '</select></div>');
    segments.push('<div class="property-item"><label>Margin Bottom</label><select data-key="spacing.margin.bottom">' + buildSelectOptions(spacingOptions, margin.bottom, null) + '</select></div>');
    segments.push('</div>');

    if (type === 'blockquote') {
        const borderColor = props.pullBorderColor !== undefined ? props.pullBorderColor : '#6366f1';
        segments.push('<div class="property-group"><h4>Pull Style</h4>');
        segments.push('<div class="property-item"><label>Border Color</label><input type="color" data-key="pullBorderColor" value="' + borderColor + '"></div>');
        segments.push(renderColorProperty('backgroundColor', props.backgroundColor !== undefined ? props.backgroundColor : ''));
        segments.push('</div>');
    }

    return segments.join('');
}

function setNestedValue(target, path, value) {
    const segments = path.split('.');
    let current = target;
    for (let i = 0; i < segments.length; i++) {
        const key = segments[i];
        if (i === segments.length - 1) {
            current[key] = value;
        } else {
            if (!current[key] || typeof current[key] !== 'object') {
                current[key] = {};
            }
            current = current[key];
        }
    }
}

function deleteNestedValue(target, path) {
    const segments = path.split('.');
    const stack = [];
    let current = target;

    for (let i = 0; i < segments.length; i++) {
        const key = segments[i];
        if (!current || typeof current !== 'object') {
            return;
        }
        stack.push({ parent: current, key });
        current = current[key];
    }

    const last = stack.pop();
    if (last && last.parent && Object.prototype.hasOwnProperty.call(last.parent, last.key)) {
        delete last.parent[last.key];
    }

    for (let i = stack.length - 1; i >= 0; i--) {
        const entry = stack[i];
        if (entry.parent && entry.parent[entry.key] && typeof entry.parent[entry.key] === 'object' && Object.keys(entry.parent[entry.key]).length === 0) {
            delete entry.parent[entry.key];
        }
    }
}

function pruneEmptyObjects(obj) {
    if (!obj || typeof obj !== 'object') return;
    Object.keys(obj).forEach(key => {
        const value = obj[key];
        if (value && typeof value === 'object') {
            pruneEmptyObjects(value);
            if (Object.keys(value).length === 0) {
                delete obj[key];
            }
        } else if (value === '' || value === null) {
            delete obj[key];
        }
    });
}
function applyYamlComponentProperties(componentId, path) {
    if (!yamlStructure || !path) return;

    const newProps = {};
    const newLabelProps = {};
    const pathsToDelete = [];
    const colorProperties = ['backgroundColor', 'color', 'borderColor', 'focusedButtonBackgroundColor', 'border_color'];
    const imageProperties = ['backgroundImage'];

    const inputs = document.querySelectorAll('#propertiesContent input[data-key], #propertiesContent select[data-key], #propertiesContent textarea[data-key]');
    inputs.forEach(input => {
        const keyPath = input.dataset.key;
        if (!keyPath) return;

        if (keyPath.startsWith('links') || keyPath.startsWith('images') || keyPath === 'color_type' || keyPath === 'solid_color' || keyPath === 'gradient_direction' || keyPath === 'gradient_start' || keyPath === 'gradient_end' || imageProperties.includes(keyPath)) {
            return;
        }

        const isLabelProp = input.dataset.propType === 'label_properties';
        const dataType = input.dataset.type;
        const shouldTrim = input.dataset.trim !== 'false';
        const allowEmpty = input.dataset.allowEmpty === 'true';
        let value;

        if (input.type === 'checkbox') {
            value = input.checked;
        } else if (input.tagName === 'SELECT') {
            value = input.value;
        } else {
            value = input.value;
            if (shouldTrim && typeof value === 'string') {
                value = value.trim();
            }
        }

        if (dataType === 'number' && typeof value === 'string' && value !== '') {
            const numeric = Number(value);
            value = Number.isNaN(numeric) ? value : numeric;
        }

        const target = isLabelProp ? newLabelProps : newProps;

        if ((value === '' || value === null) && input.type !== 'checkbox' && !allowEmpty) {
            pathsToDelete.push({ target: isLabelProp ? 'label_properties' : 'properties', path: keyPath });
            return;
        }

        setNestedValue(target, keyPath, value);
    });

    colorProperties.forEach(key => {
        const colorTypeSelect = document.getElementById(`prop_color_type_${key}`);
        if (colorTypeSelect) {
            const isLabelProp = colorTypeSelect.dataset.propType === 'label_properties';
            const target = isLabelProp ? newLabelProps : newProps;
            const selectedType = colorTypeSelect.value;

            if (selectedType === 'solid') {
                setNestedValue(target, key, document.getElementById(`prop_text_${key}`).value);
            } else if (selectedType === 'transparent') {
                setNestedValue(target, key, 'transparent');
            } else if (selectedType === 'gradient' && key === 'backgroundColor') {
                setNestedValue(target, key, {
                    direction: document.getElementById(`prop_gradient_dir_${key}`).value,
                    start: document.getElementById(`prop_gradient_start_${key}`).value,
                    end: document.getElementById(`prop_gradient_end_${key}`).value
                });
            }
        }
    });

    imageProperties.forEach(key => {
        const input = document.getElementById(`prop_${key}`);
        if (input) {
            const isLabelProp = input.dataset.propType === 'label_properties';
            const target = isLabelProp ? newLabelProps : newProps;
            const value = input.value.trim();
            if (value) {
                setNestedValue(target, key, value);
            } else {
                pathsToDelete.push({ target: isLabelProp ? 'label_properties' : 'properties', path: key });
            }
        }
    });

    const component = getComponentByPath(yamlStructure, path);
    if (component) {
        if (component.name === 'titlebar') {
            const links = [];
            document.querySelectorAll('.link-item').forEach((linkItem, index) => {
                const textInput = linkItem.querySelector(`input[data-key="links.${index}.text"]`);
                const valueInput = linkItem.querySelector(`input[data-key="links.${index}.value"]`);
                if (textInput && valueInput) {
                    const textValue = textInput.value.trim();
                    const linkValue = valueInput.value.trim();
                    if (textValue || linkValue) {
                        links.push({ text: textValue, value: linkValue });
                    }
                }
            });
            setNestedValue(newProps, 'links', links);
        }

        component.properties = deepMerge({}, component.properties || {}, newProps);

        if (Object.keys(newLabelProps).length > 0) {
            component.properties.label_properties = deepMerge({}, component.properties.label_properties || {}, newLabelProps);
        }

        pathsToDelete.forEach(entry => {
            if (entry.target === 'label_properties') {
                if (component.properties.label_properties) {
                    deleteNestedValue(component.properties.label_properties, entry.path);
                }
            } else {
                deleteNestedValue(component.properties, entry.path);
            }
        });

        pruneEmptyObjects(component.properties);
    }

    const yamlString = generateYamlFromStructure(yamlStructure);
    document.getElementById('codeEditor').value = yamlString;

    parseYamlComponents(yamlString);

    setTimeout(() => {
        let newComponentId = null;
        for (const [id, compPath] of Object.entries(componentIdToPathMap)) {
            if (JSON.stringify(compPath) === JSON.stringify(path)) {
                newComponentId = id;
                break;
            }
        }

        if (newComponentId) {
            const elementToReselect = document.querySelector('[data-component-id="' + newComponentId + '"]');
            if (elementToReselect) {
                document.querySelectorAll('.rendered-component').forEach(el => el.style.border = '1px solid #404A6B');
                elementToReselect.style.border = '2px solid #ef4444';
                selectedComponentElement = elementToReselect;
                renderPropertiesPanel(component, newComponentId, path);
            }
        }
    }, 50);
}
// =================================================================================================
// --- UI HELPERS ---
// =================================================================================================

function toRem(value) {
    if (typeof value === 'number') {
        return `${value / 10}rem`;
    }
    if (typeof value === 'string') {
        return value.split(' ').map(v => {
            const num = parseFloat(v);
            return isNaN(num) ? v : `${num / 10}rem`;
        }).join(' ');
    }
    return value;
}

function generateCalendarHTML(props) {
    const today = new Date();
    const month = parseInt(props.month) || today.getMonth();
    const year = parseInt(props.year) || today.getFullYear();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    
    let calendarHTML = `<div class="card"><div class="row" style="text-align:center;">
        <div class="col-sm"><strong>${monthNames[month]} ${year}</strong></div>
    </div><div class="row" style="text-align:center;">
        <div class="col-sm">Su</div><div class="col-sm">Mo</div><div class="col-sm">Tu</div><div class="col-sm">We</div><div class="col-sm">Th</div><div class="col-sm">Fr</div><div class="col-sm">Sa</div>
    </div><div class="row" style="text-align:center;">`;
    
    for (let i = 0; i < firstDay; i++) { 
        calendarHTML += '<div class="col-sm"></div>'; 
    } 
    
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        calendarHTML += `<div class="col-sm"><span class="${isToday ? 'tag inverse' : ''}">${day}</span></div>`;
    }
    
    calendarHTML += '</div></div>';
    return calendarHTML;
}

function getAlignmentClass(alignment) {
    switch(alignment) {
        case 'center': return 'titlebar-center';
        case 'right': return 'titlebar-right';
        default: return 'titlebar-left';
    }
}

function generateTitlebarLinks(links, focusColor) {
    if (!Array.isArray(links)) return '';
    
    return links.map(link => 
        `<a href="${link.value || '#'}" class="titlebar-link" style="--focus-bg: ${focusColor || '#f0f0f0'}">${link.text || 'Link'}</a>`
    ).join('');
}

function generateLinksEditor(links) {
    let html = '<div class="links-editor"><h4>Navigation Links</h4>';
    
    links.forEach((link, index) => {
        html += `
            <div class="link-item" data-index="${index}">
                <label>Link ${index + 1}</label>
                <input type="text" placeholder="Link Text" value="${link.text || ''}" data-key="links.${index}.text">
                <input type="text" placeholder="Link URL" value="${link.value || ''}" data-key="links.${index}.value">
                <button type="button" class="btn-remove-link" onclick="removeTitlebarLink(${index})">Remove</button>
            </div>
        `;
    });
    
    html += '<button type="button" class="btn-add-link" onclick="addTitlebarLink()">Add Link</button></div>';
    return html;
}

function addTitlebarLink() {
    const componentId = selectedComponentElement?.dataset.componentId;
    if (!componentId) return;

    const path = componentIdToPathMap[componentId];
    const component = getComponentByPath(yamlStructure, path);
    
    if (component) {
        const links = component.properties.links || [];
        const newLinks = [...links, { text: 'New Link', value: '#' }];
        component.properties.links = newLinks;
        renderPropertiesPanel(component, componentId, path);
    }
}

function removeTitlebarLink(index) {
    const componentId = selectedComponentElement?.dataset.componentId;
    if (!componentId) return;

    const path = componentIdToPathMap[componentId];
    const component = getComponentByPath(yamlStructure, path);
    
    if (component) {
        const links = component.properties.links || [];
        const newLinks = links.filter((_, i) => i !== index);
        component.properties.links = newLinks;
        renderPropertiesPanel(component, componentId, path);
    }
}

function initializeComponentButtons() {
    document.querySelectorAll('.component-item').forEach(button => {
        button.addEventListener('click', () => {
            const componentName = button.dataset.component;
            if (componentName) {
                insertYamlComponent(componentName);
            }
        });
    });
}

function initializeResizer() {
    const resizer = document.getElementById('resizer');
    const editor = document.getElementById('codeEditor');
    let initialEditorHeight = 0;
    let initialMouseY = 0;
    
    resizer.addEventListener('mousedown', function(e) {
        e.preventDefault();
        initialEditorHeight = editor.clientHeight;
        initialMouseY = e.clientY;
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
    });
    
    function handleMouseMove(e) {
        const deltaY = e.clientY - initialMouseY;
        const newEditorHeight = initialEditorHeight + deltaY;
        if (newEditorHeight > 100) {
            editor.style.height = `${newEditorHeight}px`;
        }
    }
    
    function handleMouseUp() {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
    }
}

function toggleHelpPanel() {
    const appContainer = document.getElementById('appContainer');
    const helpPanel = document.getElementById('helpPanel');
    appContainer.classList.toggle('help-visible');
    helpPanel.style.display = appContainer.classList.contains('help-visible') ? 'block' : 'none';
}

function openFullscreen() {
    const yamlText = document.getElementById('codeEditor').value;
    const cleanHTML = generateCleanHTML(yamlText);
    const fullscreenContent = document.getElementById('fullscreenContent');
    const modal = document.getElementById('fullscreenModal');
    fullscreenContent.innerHTML = cleanHTML;
    if (typeof initializeTitlebar === 'function') {
        fullscreenContent.querySelectorAll('.titlebar').forEach(titlebar => initializeTitlebar(titlebar));
    }
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeFullscreen() {
    const modal = document.getElementById('fullscreenModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function clearCanvas() {
    document.getElementById('codeEditor').value = '';
    yamlStructure = null;
    parseYamlComponents('');
    document.getElementById('propertiesContent').innerHTML = `<p style="color: #666; font-style: italic; font-size: 1.2rem; text-align: center; padding: 2rem 0;">Select a component to edit.</p>`;
}

function exportCode() {
    const yamlText = document.getElementById('codeEditor').value;
    const structure = parseYamlContent(yamlText);
    const pageProperties = (structure && structure[0] && structure[0].name === 'page') ? structure[0].properties : {};
    const bodyStyles = generateRemainingStyles(pageProperties);
    const bodyContent = generateCleanHTML(yamlText);
    
    const behaviorScript = generateTitlebarBehaviorScript();
    const fullHTML = `<!DOCTYPE html>
<html lang="en" style="height: 100%;">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Website</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/mini.css@3.0.1/dist/mini-default.min.css">
    <style>
        html { font-size: 10px; }
        body { font-size: 1.6rem; height: 100%; margin: 0; }
    </style>
</head>
<body style="${bodyStyles}">
    ${bodyContent}
    ${behaviorScript}
</body>
</html>`;
    
    const blob = new Blob([fullHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated-website.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function parseYamlComponents(yamlText) {
    componentIdToPathMap = {};
    yamlStructure = parseYamlContent(yamlText);
    
    const preview = document.getElementById('preview');
    const result = renderYamlStructure(yamlStructure, 'preview');

    let pageStyleSheet = document.getElementById('page-styles');
    if (pageStyleSheet) {
        pageStyleSheet.innerText = '';
    }
    
    preview.innerHTML = result.html;
    initializeAllComponents();
}

function generateCleanHTML(yamlText) {
    const structure = parseYamlContent(yamlText);
    const result = renderYamlStructure(structure, 'export');
    return result.html;
}

function generateTitlebarBehaviorScript() {
    return `<script>
(function() {
    const SCROLL_OFFSET = 50;

    function applyScrollState() {
        const scrolled = window.scrollY > SCROLL_OFFSET;
        document.querySelectorAll('.titlebar').forEach(nav => {
            nav.classList.toggle('scrolled', scrolled);
        });
    }

    function bindInteractions(nav) {
        const button = nav.querySelector('.mobile-menu-button');
        const links = nav.querySelector('.titlebar-nav');
        if (button && links) {
            button.addEventListener('click', () => {
                links.classList.toggle('active');
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const navbars = document.querySelectorAll('.titlebar');
        navbars.forEach(bindInteractions);
        applyScrollState();
        window.addEventListener('scroll', applyScrollState, { passive: true });
    });
})();
</script>`;
}
































function logHtml() {
    const yamlText = document.getElementById('codeEditor').value;
    const cleanHTML = generateCleanHTML(yamlText);
    console.log(cleanHTML);
}






