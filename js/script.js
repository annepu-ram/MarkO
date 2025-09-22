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
    document.getElementById('logHtmlBtn').addEventListener('click', logHtml);
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
    const template = componentTemplates[componentName] || {};

    let newComponent;
    if (componentName === 'page') {
        newComponent = {
            name: 'page',
            properties: { ...template },
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
        newComponent = {
            name: 'tabs',
            properties: { ...template },
            tabs: [ {title : 'Tab Name', components: [] }]
        };
    } else if (componentName === 'carousel') {
        const { slides, ...properties } = template;
        newComponent = {
            name: 'carousel',
            properties: properties,
            slides: slides || []
        };
    } else if (componentName === 'accordion') {
        newComponent = {
            name: 'accordion',
            properties: { ...template },
            content: {
                components: []
            }
        };
    } else if (componentName === 'form') {
        newComponent = {
            name: 'form',
            properties: { ...template },
            components: []
        };
    } else if (componentName === 'image') {
        newComponent = {
            name: 'image',
            properties: { ...template },
            components: []
        };
    } else {
        newComponent = {
            name: componentName,
            properties: { ...template }
        };
    }

    let structure = parseYamlContent(editor.value);

    // If the editor is empty or doesn't have a page component, create one.
    if (!structure || !Array.isArray(structure) || structure.length !== 1 || structure[0].name !== 'page') {
        structure = [{
            name: 'page',
            properties: {},
            components: [newComponent]
        }];
    } else {
        if (!structure[0].components) {
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
&nbsp;&nbsp;&nbsp;&nbsp;- name: h1<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;properties:<br>
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
    const classes = generateMiniCssClasses(name, properties);
    const styles = generateRemainingStyles(properties);
    const componentHTML = generateComponentInnerHTML(name, properties, classes, styles, mode);

    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        componentIdToPathMap[componentId] = path;

        if (name === 'titlebar') {
            const idMatch = componentHTML.match(/id="([^"]+)"/);
            if (idMatch && idMatch[1]) {
                registerComponentForInitialization('titlebar', idMatch[1]);
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

    const accordionHTML = `<details>
        <summary>${title}</summary>
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
    const finalAttrs = `${classes ? `class="${classes}"` : ''} style="${styleAttr}"`;
    const id = `input_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const labelStyles = generateRemainingStyles(props.label_properties || {});

    const componentGenerators = {
        h1: () => `<h1 ${finalAttrs}>${props.text || 'Main Heading'}</h1>`,
        h2: () => `<h2 ${finalAttrs}>${props.text || 'Section Heading'}</h2>`,
        h3: () => `<h3 ${finalAttrs}>${props.text || 'Subsection Heading'}</h3>`,
        paragraph: () => `<p ${finalAttrs}>${props.text || 'This is a paragraph of text content.'}</p>`,
        image: () => `<img src="${props.src || 'https://via.placeholder.com/150'}" alt="${props.alt || ''}" style="width: 100%; height: ${toRem(props.height) || 'auto'}; object-fit: cover;">`,
        video: () => {
            const videoId = (props.src || '').split('v=')[1];
            const embedUrl = videoId ? `https://www.youtube.com/embed/${videoId.split('&')[0]}` : '';
            return `<iframe ${finalAttrs} src="${embedUrl}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width: 100%; aspect-ratio: 16/9;"></iframe>`;
        },
        gif: () => `<img src="${props.src || 'https://media.giphy.com/media/VseXoJs6vVmwU/giphy.gif'}" alt="gif" ${finalAttrs} />`,
        textbox: () => `<div style="width: 100%; margin-bottom: 1rem;"><label for="${id}" style="${labelStyles}">${props.label}</label><input type="text" id="${id}" placeholder="${props.placeholder || 'Enter text...'}" value="${props.value || ''}" ${finalAttrs} /></div>`,
        textarea: () => `<div style="width: 100%; margin-bottom: 1rem;"><label for="${id}" style="${labelStyles}">${props.label}</label><textarea id="${id}" placeholder="${props.placeholder || 'Enter text...'}" rows="${props.rows || 3}" ${finalAttrs}>${props.value || ''}</textarea></div>`,
        button: () => `<button onclick="${props.onclick || ''}" ${finalAttrs}>${props.text || 'Click Me'}</button>`,
        dropdown: () => {
            const options = (props.options || 'Option 1,Option 2,Option3').split(',');
            const optionHTML = options.map(opt => `<option value="${opt.trim()}" ${props.selected === opt.trim() ? 'selected' : ''}>${opt.trim()}</option>`).join('');
            return `<div style="width: 100%; margin-bottom: 1rem;"><label for="${id}" style="${labelStyles}">${props.label}</label><select id="${id}" ${finalAttrs}>${optionHTML}</select></div>`;
        },
        calendar: () => generateCalendarHTML(props),
        checkbox: () => `<div style="width: 100%; margin-bottom: 1rem;"><label for="${id}" ${finalAttrs} style="${labelStyles}"><input type="checkbox" id="${id}" ${props.checked ? 'checked' : ''} /><span>${props.text || 'Check me'}</span></label></div>`,
        radio: () => `<div style="width: 100%; margin-bottom: 1rem;"><label for="${id}" ${finalAttrs} style="${labelStyles}"><input type="radio" id="${id}" name="${props.name || 'radio1'}" value="${props.value || 'option1'}" /><span>${props.text || 'Select me'}</span></label></div>`,
        hamburger: () => {
            const items = (props.items || 'Home,About,Services,Contact').split(',');
            let menuHTML = `<div class="dropdown" ${finalAttrs}><button class="button primary">☰</button><div class="menu">`;
            items.forEach(item => { menuHTML += `<a href="#" class="menu-item">${item.trim()}</a>`; });
            menuHTML += '</div></div>';
            return menuHTML;
        },
        br: () => mode === 'preview' ? `<div class="comp-br" style="height: 2rem; border-bottom: 1px dashed #ccc; margin: 1rem 0;"></div>` : '<br>',
        titlebar: () => generateTitlebarHTML(props, classes, styleAttr, mode),
        link: () => {
            let linkStyle = '';
            if (props.underline) {
                linkStyle += 'text-decoration: underline;';
            } else {
                linkStyle += 'text-decoration: none;';
            }
            let arrowHTML = '';
            if (props.showArrow) {
                arrowHTML = '&nbsp;&#x2192;';
            }
            const finalStyle = styleAttr.replace(/text-align:[^;]+;/g, '');
            return `<div style="text-align: ${props.textAlign || 'left'};}"><a href="${props.url || '#'}" style="${linkStyle} ${finalStyle}">${props.text || 'Click Me'}${arrowHTML}</a></div>`;
        }
    };

    return componentGenerators[type] ? componentGenerators[type]() : `<div style="color: #ef4444; font-style: italic;">Unknown component: ${type}</div>`;
}

function generateTitlebarHTML(props, classes, styleAttr, mode) {
    const alignmentClass = getAlignmentClass(props.alignment);
    const logoHTML = props.logo ? `<img src="${props.logo}" alt="Logo" class="titlebar-logo" />` : '';
    const titleHTML = props.title ? `<h1 class="titlebar-title">${props.title}</h1>` : '';
    const linksHTML = generateTitlebarLinks(props.links, props.focusedButtonBackgroundColor);
    const titlebarId = `titlebar_${Date.now()}`;
    
    return `
        <nav class="titlebar ${alignmentClass} ${classes}" style="${styleAttr} height: ${toRem(props.height || 60)};" id="${titlebarId}">
            <div class="titlebar-brand">
                ${logoHTML}
                ${titleHTML}
            </div>
            <button id="mobile-menu-button" class="mobile-menu-button">
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
    let classes = [];
    if (type === 'button') {
        classes.push('button');
        if (props.variant) classes.push(props.variant);
    }
    return classes.join(' ');
}

function generateRemainingStyles(props) {
    let styles = '';
    if (props.backgroundImage) {
        styles += `background-image: url('${props.backgroundImage}');`;
        styles += `background-size: cover;`;
        styles += `background-position: center;`;
    }
    else if (props.backgroundColor) {
        if (typeof props.backgroundColor === 'object' && props.backgroundColor !== null) {
            styles += `background-image: linear-gradient(${props.backgroundColor.direction}, ${props.backgroundColor.start}, ${props.backgroundColor.end});`;
        } else if (props.backgroundColor === 'transparent') {
            styles += 'background-color: transparent;';
        } else {
            styles += `background-color: ${props.backgroundColor};`;
        }
    }
    if (props.color) styles += `color: ${props.color};`;
    if (props.fontStyle) styles += `font-style: ${props.fontStyle};`;
    if (props.fontWeight) styles += `font-weight: ${props.fontWeight};`;
    if (props.fontSize) styles += `font-size: ${toRem(props.fontSize)};`;
    if (props.textAlign) styles += `text-align: ${props.textAlign};`;
    if (props.padding) styles += `padding: ${toRem(props.padding)};`;
    if (props.margin) styles += `margin: ${toRem(props.margin)};`;
    if (props.borderWidth > 0 && props.borderStyle !== 'none') {
        styles += `border: ${toRem(props.borderWidth)} ${props.borderStyle || 'solid'} ${props.borderColor || '#000000'};`;
    }
    if (props.borderRadius) styles += `border-radius: ${toRem(props.borderRadius)};`;
    if (props.border_size) styles += `border-width: ${props.border_size};`;
    if (props.border_color) styles += `border-color: ${props.border_color};`;
    if (props.border_radius) styles += `border-radius: ${props.border_radius};`;
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
        propertiesContent.innerHTML = `<p style="color: #666; font-style: italic; font-size: 1.2rem; text-align: center; padding: 2rem 0;">Select a component to edit.</p>`;
        return;
    }

    let propertiesHTML = '';
    const templateProps = componentTemplates[component.name] || {};
    const finalProps = { ...templateProps, ...component.properties };

    for (const key in finalProps) {
        if (key === 'content' || key === 'columns' || key === 'tabs' || key === 'components' || key === 'slides' || key === 'backgroundImage' || key === 'label_properties') continue;
        if (typeof finalProps[key] === 'object' && finalProps[key] !== null && key !== 'links' && key !== 'backgroundColor') continue;
        
        const value = finalProps[key] === undefined ? '' : finalProps[key];
        
        propertiesHTML += renderProperty(key, value);
    }

    if (component.name === 'titlebar') {
        let links = finalProps.links || [];
        propertiesHTML += generateLinksEditor(links);
    }

    if (finalProps.label_properties) {
        propertiesHTML += '<h4>Label Properties</h4>';
        for (const key in finalProps.label_properties) {
            const value = finalProps.label_properties[key] === undefined ? '' : finalProps.label_properties[key];
            propertiesHTML += renderProperty(key, value, 'label_properties');
        }
    }

    if (component.name === 'page') {
        propertiesHTML += renderProperty('backgroundImage', finalProps.backgroundImage || '');
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
        textAlign: ['left', 'center', 'right']
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

function applyYamlComponentProperties(componentId, path) {
    if (!yamlStructure || !path) return;

    const newProps = {};
    const newLabelProps = {};
    const colorProperties = ['backgroundColor', 'color', 'borderColor', 'focusedButtonBackgroundColor', 'border_color'];
    const imageProperties = ['backgroundImage'];

    document.querySelectorAll('#propertiesContent input[data-key], #propertiesContent select[data-key], #propertiesContent textarea[data-key]').forEach(input => {
        const key = input.dataset.key;
        const isLabelProp = input.dataset.propType === 'label_properties';

        if (colorProperties.includes(key)) {
            const colorTypeSelect = document.getElementById(`prop_color_type_${key}`);
            if (colorTypeSelect) {
                const selectedType = colorTypeSelect.value;
                if (selectedType === 'solid') {
                    const value = document.getElementById(`prop_text_${key}`).value;
                    if (isLabelProp) newLabelProps[key] = value; else newProps[key] = value;
                } else if (selectedType === 'transparent') {
                    if (isLabelProp) newLabelProps[key] = 'transparent'; else newProps[key] = 'transparent';
                } else if (selectedType === 'gradient' && key === 'backgroundColor') {
                    const value = {
                        direction: document.getElementById(`prop_gradient_dir_${key}`).value,
                        start: document.getElementById(`prop_gradient_start_${key}`).value,
                        end: document.getElementById(`prop_gradient_end_${key}`).value
                    };
                    if (isLabelProp) newLabelProps[key] = value; else newProps[key] = value;
                }
            }
        } else if (imageProperties.includes(key)) {
            const value = input.value;
            if (isLabelProp) newLabelProps[key] = value; else newProps[key] = value;
        } else if (!key.startsWith('images.') && key !== 'color_type' && key !== 'solid_color' && key !== 'gradient_direction' && key !== 'gradient_start' && key !== 'gradient_end') {
            const value = input.type === 'checkbox' ? input.checked : input.value;
            if (isLabelProp) {
                newLabelProps[key] = value;
            } else {
                newProps[key] = value;
            }
        }
    });

    const component = getComponentByPath(yamlStructure, path);
    if (component) {
        // special handling for links
        if (component.name === 'titlebar') {
            const links = [];
            document.querySelectorAll('.link-item').forEach((linkItem, index) => {
                const textInput = linkItem.querySelector(`input[data-key="links.${index}.text"]`);
                const valueInput = linkItem.querySelector(`input[data-key="links.${index}.value"]`);
                if (textInput && valueInput) {
                    links.push({ text: textInput.value, value: valueInput.value });
                }
            });
            newProps.links = links;
        }
        
        component.properties = { ...component.properties, ...newProps };
        if (Object.keys(newLabelProps).length > 0) {
            component.properties.label_properties = { ...component.properties.label_properties, ...newLabelProps };
        }
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
            const elementToReselect = document.querySelector(`[data-component-id="${newComponentId}"]`);
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

function logHtml() {
    const yamlText = document.getElementById('codeEditor').value;
    const cleanHTML = generateCleanHTML(yamlText);
    console.log(cleanHTML);
}
