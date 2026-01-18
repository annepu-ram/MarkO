import { getComponentSchema, getComponentDefaults, getSchemaTokens } from './metadataLoader.js';
import { deepClone, deepMerge, getNestedValue, setNestedValue } from './utils/object.js';
import { customRenderers } from './customRenderers.js';

// Map group IDs to icons for accordion sections (matching wireframe)
const sectionIcons = {
    content: 'icon-type',        // Lucide: type
    typography: 'icon-text',     // Lucide: text (different from type)
    layout: 'icon-layout',       // Lucide: layout
    sizing: 'icon-layout',
    spacing: 'icon-move',        // Lucide: move
    background: 'icon-paintbrush', // Lucide: paintbrush
    appearance: 'icon-paintbrush', // Lucide: paintbrush (same as background)
    branding: 'icon-image',
    navigation: 'icon-link',
    behavior: 'icon-settings',
    items: 'icon-layers',
    default: 'icon-box'
};

// Map component names to icons
const componentIcons = {
    page: 'icon-layout',
    'layout-row': 'icon-layout',
    'layout-column': 'icon-layout',
    columnsgrid: 'icon-grid',
    titlebar: 'icon-menu',
    heading: 'icon-type',
    paragraph: 'icon-type',
    eyebrow: 'icon-type',
    caption: 'icon-type',
    blockquote: 'icon-type',
    image: 'icon-image',
    video: 'icon-video',
    gif: 'icon-image',
    textbox: 'icon-edit',
    textarea: 'icon-edit',
    button: 'icon-box',
    dropdown: 'icon-chevron-down',
    calendar: 'icon-calendar',
    checkbox: 'icon-check-square',
    radio: 'icon-circle-dot',
    accordion: 'icon-layers',
    tabs: 'icon-layout',
    hamburger: 'icon-menu',
    link: 'icon-link',
    form: 'icon-edit',
    carousel: 'icon-image',
    default: 'icon-box'
};

// Map component names to category labels
const componentCategories = {
    page: 'Page Container',
    'layout-row': 'Layout',
    'layout-column': 'Layout',
    columnsgrid: 'Layout',
    titlebar: 'Navigation',
    heading: 'Typography',
    paragraph: 'Typography',
    eyebrow: 'Typography',
    caption: 'Typography',
    blockquote: 'Typography',
    image: 'Media',
    video: 'Media',
    gif: 'Media',
    textbox: 'Form Input',
    textarea: 'Form Input',
    button: 'UI Element',
    dropdown: 'Form Input',
    calendar: 'Form Input',
    checkbox: 'Form Input',
    radio: 'Form Input',
    accordion: 'Interactive',
    tabs: 'Interactive',
    hamburger: 'Navigation',
    link: 'Typography',
    form: 'Form Container',
    carousel: 'Interactive',
    default: 'Component'
};

let activeComponentName = null;
let activeFieldMeta = new Map();
let activeComponentId = null;
let activePath = null;

/**
 * Convert path string or array to segments
 */
const pathToSegments = path => (Array.isArray(path) ? path : String(path || '').split('.').filter(Boolean));

/**
 * Resolve property value from component or defaults
 */
const resolvePropertyValue = (component, pathSegments, defaults, target = 'properties') => {
    if (!pathSegments.length) {
        return undefined;
    }
    if (target === 'component') {
        return getNestedValue(component, pathSegments);
    }
    const props = component.properties || {};
    const value = getNestedValue(props, pathSegments);
    if (value !== undefined) {
        return value;
    }
    return getNestedValue(defaults, pathSegments);
};

/**
 * Determine if field targets component or properties
 */
const determineFieldTarget = (field, component) => {
    // Check for explicit target from schema first
    if (field.target) {
        return field.target;
    }
    if (field.path.includes('.')) {
        return 'properties';
    }
    if (component[field.path] !== undefined) {
        return 'component';
    }
    return 'properties';
};

/**
 * Get token options for select fields
 */
const getTokenOptions = tokenName => {
    const tokens = getSchemaTokens();
    const entry = tokens?.[tokenName];
    if (!entry) {
        return [];
    }
    if (Array.isArray(entry)) {
        return entry;
    }
    if (Array.isArray(entry.options)) {
        return entry.options;
    }
    return [];
};

/**
 * Compare two values for equality (deep comparison for objects/arrays)
 */
const valuesAreEqual = (value1, value2) => {
    // Exact match
    if (value1 === value2) return true;
    
    // Both null/undefined
    if (value1 == null && value2 == null) return true;
    
    // One is null/undefined
    if (value1 == null || value2 == null) return false;
    
    // Both are objects/arrays - deep compare
    if (typeof value1 === 'object' && typeof value2 === 'object') {
        return JSON.stringify(value1) === JSON.stringify(value2);
    }
    
    // Primitive comparison
    return false;
};

/**
 * Get value from form control based on field type
 */
const getValueFromControl = (control, field) => {
    switch (field.type) {
        case 'number':
            const numValue = control.value === '' ? '' : Number(control.value);
            return Number.isNaN(numValue) ? '' : numValue;
        
        case 'checkbox':
            return control.checked;
        
        case 'range':
            return control.controlElement ? Number(control.controlElement.value) : Number(control.value);
        
        default:
            return control.value;
    }
};

/**
 * Render text input
 */
const renderTextInput = ({ field, value, fieldId, type = 'text' }) => {
    const input = document.createElement('input');
    input.type = type;
    input.id = fieldId;
    input.className = 'property-input';
    if (value !== undefined && value !== null) {
        input.value = value;
    }
    if (field.placeholder) {
        input.placeholder = field.placeholder;
    }
    if (type === 'number') {
        if (field.min !== undefined) input.min = field.min;
        if (field.max !== undefined) input.max = field.max;
        if (field.step !== undefined) input.step = field.step;
        input.inputMode = 'decimal';
    }
    return input;
};

/**
 * Render textarea
 */
const renderTextarea = ({ field, value, fieldId }) => {
    const textarea = document.createElement('textarea');
    textarea.id = fieldId;
    textarea.className = 'property-input property-textarea';
    textarea.rows = field.rows || 3;
    textarea.value = value || '';
    if (field.placeholder) {
        textarea.placeholder = field.placeholder;
    }
    return textarea;
};

/**
 * Render select dropdown
 */
const renderSelect = ({ field, value, fieldId }) => {
    const select = document.createElement('select');
    select.id = fieldId;
    select.className = 'property-input';
    let options = [];
    if (Array.isArray(field.options)) {
        options = field.options.map(option => (typeof option === 'object' ? option : { value: option, label: option }));
    } else if (field.tokens) {
        options = getTokenOptions(field.tokens).map(option => (typeof option === 'object' ? option : { value: option, label: option }));
    }
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option.value ?? option;
        opt.textContent = option.label ?? option.value ?? option;
        if ((value ?? '') === opt.value) {
            opt.selected = true;
        }
        select.appendChild(opt);
    });
    if (value !== undefined && value !== null && !options.some(option => (option.value ?? option) === value)) {
        const customOpt = document.createElement('option');
        customOpt.value = value;
        customOpt.textContent = value;
        customOpt.selected = true;
        select.appendChild(customOpt);
    }
    return select;
};

/**
 * Render checkbox
 */
const renderCheckbox = ({ field, value, fieldId }) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'property-item property-checkbox';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = fieldId;
    input.className = 'property-input';
    input.checked = Boolean(value);
    const label = document.createElement('label');
    label.htmlFor = fieldId;
    label.textContent = field.label || field.path;
    wrapper.appendChild(input);
    wrapper.appendChild(label);
    return { wrapper, input };
};

/**
 * Render color input
 */
const renderColorInput = ({ field, value, fieldId }) => {
    const input = document.createElement('input');
    input.type = 'color';
    input.id = fieldId;
    input.className = 'property-input';
    let hexValue = value || '#000000';
    if (hexValue.startsWith('rgba')) {
        const matches = hexValue.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (matches) {
            const r = parseInt(matches[1]).toString(16).padStart(2, '0');
            const g = parseInt(matches[2]).toString(16).padStart(2, '0');
            const b = parseInt(matches[3]).toString(16).padStart(2, '0');
            hexValue = `#${r}${g}${b}`;
        }
    }
    input.value = hexValue;
    return input;
};

/**
 * Render range input
 */
const renderRangeInput = ({ field, value, fieldId }) => {
    const container = document.createElement('div');
    container.className = 'range-input-container';
    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = fieldId;
    slider.className = 'property-input range-slider';
    slider.min = field.min !== undefined ? field.min : 0;
    slider.max = field.max !== undefined ? field.max : 100;
    slider.value = value !== undefined ? value : (field.default !== undefined ? field.default : 100);
    const valueDisplay = document.createElement('span');
    valueDisplay.className = 'range-value';
    valueDisplay.textContent = `${slider.value}${field.unit || ''}`;
    slider.addEventListener('input', (e) => {
        valueDisplay.textContent = `${e.target.value}${field.unit || ''}`;
    });
    container.appendChild(slider);
    container.appendChild(valueDisplay);
    container.controlElement = slider;
    return container;
};

/**
 * Render token pills for select fields with few options
 */
const renderTokenPills = ({ field, value, fieldId }) => {
    const container = document.createElement('div');
    container.className = 'token-pills';
    container.id = fieldId;

    let options = [];
    if (Array.isArray(field.options)) {
        options = field.options.map(opt => typeof opt === 'object' ? opt : { value: opt, label: opt });
    } else if (field.tokens) {
        options = getTokenOptions(field.tokens).map(opt =>
            typeof opt === 'object' ? opt : { value: opt, label: opt }
        );
    }

    options.forEach(option => {
        const pill = document.createElement('span');
        pill.className = 'token-pill';
        pill.dataset.value = option.value ?? option;
        pill.textContent = option.label ?? option.value ?? option;

        if ((value ?? '') === pill.dataset.value) {
            pill.classList.add('active');
        }

        pill.onclick = () => {
            container.querySelectorAll('.token-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
        };

        container.appendChild(pill);
    });

    return container;
};

/**
 * Render color input with swatch preview
 */
const renderColorInputWithSwatch = ({ field, value, fieldId }) => {
    const container = document.createElement('div');
    container.className = 'color-input-row';

    // Color swatch
    const swatch = document.createElement('div');
    swatch.className = 'color-input-swatch';
    let hexValue = value || '#000000';
    if (hexValue.startsWith('rgba')) {
        const matches = hexValue.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (matches) {
            const r = parseInt(matches[1]).toString(16).padStart(2, '0');
            const g = parseInt(matches[2]).toString(16).padStart(2, '0');
            const b = parseInt(matches[3]).toString(16).padStart(2, '0');
            hexValue = `#${r}${g}${b}`;
        }
    }
    swatch.style.background = hexValue;

    // Hidden color picker
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.style.display = 'none';
    colorPicker.value = hexValue;

    // Text input
    const textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.id = fieldId;
    textInput.className = 'prop-input';
    textInput.value = hexValue;

    // Sync swatch click -> color picker
    swatch.onclick = () => colorPicker.click();

    // Sync color picker -> text + swatch
    colorPicker.oninput = (e) => {
        textInput.value = e.target.value;
        swatch.style.background = e.target.value;
    };

    // Sync text input -> swatch
    textInput.oninput = (e) => {
        if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
            swatch.style.background = e.target.value;
            colorPicker.value = e.target.value;
        }
    };

    container.appendChild(swatch);
    container.appendChild(colorPicker);
    container.appendChild(textInput);

    return container;
};

/**
 * Create field wrapper
 */
const createFieldWrapper = (field, fieldId) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'property-item';
    const label = document.createElement('label');
    label.className = 'property-label';
    label.htmlFor = fieldId;
    label.textContent = field.label || field.path;
    wrapper.appendChild(label);
    return { wrapper, label };
};

/**
 * Update the properties header with component info
 */
const updatePropertiesHeader = (component) => {
    const header = document.getElementById('propertiesHeader');
    const titleEl = document.getElementById('propertiesTitle');
    const subtitleEl = document.getElementById('propertiesSubtitle');
    const iconContainer = document.getElementById('propertiesIcon');

    if (!header) return;

    if (component && component.name) {
        header.style.display = 'flex';

        // Format component name for display (e.g., "layout-row" -> "Layout Row")
        const displayName = component.name
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');

        if (titleEl) titleEl.textContent = displayName;
        if (subtitleEl) subtitleEl.textContent = componentCategories[component.name] || componentCategories.default;

        // Update icon
        if (iconContainer) {
            const iconName = componentIcons[component.name] || componentIcons.default;
            iconContainer.innerHTML = `<svg aria-hidden="true"><use href="#${iconName}"></use></svg>`;
        }
    } else {
        header.style.display = 'none';
    }
};

/**
 * Render properties panel for selected component
 */
export function renderPropertiesPanel(component, componentId, path) {
    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) {
        return;
    }

    activeComponentName = component?.name || null;
    activeComponentId = componentId;
    activePath = path;
    activeFieldMeta.clear();

    // Update header with component info
    updatePropertiesHeader(component);

    if (!component || !componentId) {
        propertiesContent.innerHTML = '<p class="properties-empty-state">Select a component to edit.</p>';
        updatePropertiesHeader(null);  // Hide header when no component
        return;
    }

    const schema = getComponentSchema(component.name);
    if (!schema) {
        propertiesContent.innerHTML = '<p style="color: #b91c1c; font-size: 1.2rem; text-align: center; padding: 2rem 0;">No schema available for this component yet.</p>';
        return;
    }

    const defaults = getComponentDefaults(component.name);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:285',message:'renderPropertiesPanel defaults loaded',data:{componentName:component.name,defaults:JSON.stringify(defaults),componentProps:JSON.stringify(component.properties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    // Note: getComponentDefaults returns the properties object directly (not wrapped in a 'properties' key)
    // Merge defaults first, then component.properties on top
    // This ensures we have the full structure with defaults, then override with component values
    const resolvedProps = deepMerge({}, defaults || {}, component.properties || {});
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:293',message:'renderPropertiesPanel resolved properties',data:{resolvedProps:JSON.stringify(resolvedProps)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion

    propertiesContent.innerHTML = '';
    
    // Create scrollable wrapper for form
    const formScrollWrapper = document.createElement('div');
    formScrollWrapper.className = 'properties-form';
    
    const formContainer = document.createElement('div');
    formContainer.className = 'properties-form-content';

    schema.groups?.forEach(group => {
        // Create accordion section
        const sectionEl = document.createElement('div');
        sectionEl.className = 'prop-section';
        sectionEl.dataset.groupId = group.id;

        // Create accordion header
        const header = document.createElement('div');
        header.className = 'prop-section-header';
        header.onclick = () => sectionEl.classList.toggle('collapsed');

        // Section title with icon
        const titleSpan = document.createElement('span');
        titleSpan.className = 'prop-section-title';

        const iconSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        iconSvg.setAttribute('aria-hidden', 'true');
        const iconUse = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        iconUse.setAttributeNS('http://www.w3.org/1999/xlink', 'href',
            `#${sectionIcons[group.id] || sectionIcons.default}`);
        iconSvg.appendChild(iconUse);
        titleSpan.appendChild(iconSvg);
        titleSpan.appendChild(document.createTextNode(group.label || group.id));

        // Toggle chevron
        const toggleSpan = document.createElement('span');
        toggleSpan.className = 'prop-section-toggle';
        const chevronSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        chevronSvg.setAttribute('aria-hidden', 'true');
        const chevronUse = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        chevronUse.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#icon-chevron-down');
        chevronSvg.appendChild(chevronUse);
        toggleSpan.appendChild(chevronSvg);

        header.appendChild(titleSpan);
        header.appendChild(toggleSpan);
        sectionEl.appendChild(header);

        // Section content
        const contentEl = document.createElement('div');
        contentEl.className = 'prop-section-content';

        group.fields?.forEach(field => {
            const pathSegments = pathToSegments(field.path);
            const target = determineFieldTarget(field, component);
            const defaultValue = getNestedValue(defaults || {}, pathSegments);
            const currentValue = resolvePropertyValue(component, pathSegments, defaults || {}, target);
            const fieldId = `prop_${componentId}_${field.path.replace(/[^a-z0-9]/gi, '_')}`;

            const { wrapper } = createFieldWrapper(field, fieldId);
            let control;
            let customEditorInstance;

            switch (field.type) {
                case 'custom':
                    // Handle custom renderers (accordion items, tabs, etc.)
                    if (field.renderer && customRenderers[field.renderer]) {
                        customEditorInstance = customRenderers[field.renderer].render({ value: currentValue });
                        wrapper.appendChild(customEditorInstance.element);
                        activeFieldMeta.set(field.path, {
                            field,
                            target,
                            defaultValue,
                            customSerializer: customEditorInstance.serialize
                        });
                    } else {
                        console.warn(`Custom renderer "${field.renderer}" not found`);
                    }
                    break;

                case 'text':
                case 'textarea':
                    if (field.type === 'textarea') {
                        control = renderTextarea({ field, value: currentValue, fieldId });
                    } else {
                        control = renderTextInput({ field, value: currentValue, fieldId });
                    }
                    wrapper.appendChild(control);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'number':
                    control = renderTextInput({ field, value: currentValue, fieldId, type: 'number' });
                    wrapper.appendChild(control);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'select':
                    // Get options to determine if we should use pills or dropdown
                    let selectOptions = [];
                    if (Array.isArray(field.options)) {
                        selectOptions = field.options;
                    } else if (field.tokens) {
                        selectOptions = getTokenOptions(field.tokens);
                    }

                    // Use token pills for small option sets (≤ 6 options), dropdown otherwise
                    if (selectOptions.length > 0 && selectOptions.length <= 6) {
                        control = renderTokenPills({ field, value: currentValue, fieldId });
                        activeFieldMeta.set(field.path, { field, target, defaultValue, isTokenPills: true });
                    } else {
                        control = renderSelect({ field, value: currentValue, fieldId });
                        activeFieldMeta.set(field.path, { field, target, defaultValue });
                    }
                    wrapper.appendChild(control);
                    break;

                case 'checkbox':
                    const checkboxResult = renderCheckbox({ field, value: currentValue, fieldId });
                    wrapper.innerHTML = '';
                    wrapper.appendChild(checkboxResult.wrapper);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'color':
                    control = renderColorInputWithSwatch({ field, value: currentValue, fieldId });
                    wrapper.appendChild(control);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'range':
                    control = renderRangeInput({ field, value: currentValue, fieldId });
                    wrapper.appendChild(control);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                default:
                    console.warn(`Unknown field type: ${field.type}`);
                    return;
            }

            contentEl.appendChild(wrapper);
        });

        sectionEl.appendChild(contentEl);
        formContainer.appendChild(sectionEl);
    });

    // Append form content to scrollable wrapper
    formScrollWrapper.appendChild(formContainer);
    propertiesContent.appendChild(formScrollWrapper);

    // Add Apply button (click handler is set up in events.js)
    // Button is added as sibling to scroll wrapper, so it stays at bottom
    const applyButton = document.createElement('button');
    applyButton.type = 'button';
    applyButton.className = 'btn btn-primary properties-apply-button';
    applyButton.textContent = 'Apply Changes';
    propertiesContent.appendChild(applyButton);
}

/**
 * Clear properties panel
 */
export function clearPropertiesPanel() {
    const propertiesContent = document.getElementById('propertiesContent');
    if (propertiesContent) {
        propertiesContent.innerHTML = '<p class="properties-empty-state">Select a component to edit.</p>';
    }
    // Hide the properties header
    updatePropertiesHeader(null);

    activeComponentName = null;
    activeComponentId = null;
    activePath = null;
    activeFieldMeta.clear();
}

/**
 * Apply properties to component (called from main.js after YAML update)
 * This function reads form values and returns updated component properties.
 * Only returns properties that differ from defaults (keeps YAML clean).
 */
export function collectPropertyValues() {
    if (!activeComponentName || !activePath) {
        return null;
    }

    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) {
        return null;
    }

    // Separate objects for component-level and properties-level updates
    const updatedProperties = {};
    const componentUpdates = {};
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:432',message:'collectPropertyValues entry',data:{activeComponentName,numFields:activeFieldMeta.size},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion

    activeFieldMeta.forEach((meta, fieldPath) => {
        const { field, target, defaultValue, customSerializer, isTokenPills } = meta;
        let value;

        // Handle custom fields with serializers
        if (field.type === 'custom' && customSerializer) {
            value = customSerializer();

            // Apply to correct destination based on target
            if (target === 'component') {
                const pathSegments = pathToSegments(fieldPath);
                setNestedValue(componentUpdates, pathSegments, value);
            } else {
                const pathSegments = pathToSegments(fieldPath);
                setNestedValue(updatedProperties, pathSegments, value);
            }
            return;
        }

        // Handle standard fields
        const fieldId = `prop_${activeComponentId}_${fieldPath.replace(/[^a-z0-9]/gi, '_')}`;
        const control = propertiesContent.querySelector(`#${fieldId}`);

        if (!control) {
            return;
        }

        // Handle token pills - get value from active pill
        if (isTokenPills && control.classList?.contains('token-pills')) {
            const activePill = control.querySelector('.token-pill.active');
            value = activePill ? activePill.dataset.value : '';
        } else {
            // Get value from control using helper
            value = getValueFromControl(control, field);
        }
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:460',message:'collectPropertyValues after getValueFromControl',data:{fieldPath,value,valueType:typeof value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion

        // Handle empty strings for text fields - preserve if explicitly set
        if ((field.type === 'text' || field.type === 'textarea') && value === '') {
            // Empty string is only meaningful if default is not also empty
            if (defaultValue !== '' && defaultValue !== undefined) {
                value = '';  // Keep empty string as explicit value
            } else {
                return;  // Skip if default is also empty
            }
        }

        if (target === 'component') {
            // Apply component-level standard fields - always include the value
            const pathSegments = pathToSegments(fieldPath);
            if (value !== undefined) {
                setNestedValue(componentUpdates, pathSegments, value);
            }
            return;
        }

        // Always include properties-level values - let merge in main.js handle defaults
        const pathSegments = pathToSegments(fieldPath);
        if (value !== undefined && value !== null) {
            setNestedValue(updatedProperties, pathSegments, value);
        }
    });
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:505',message:'collectPropertyValues final result',data:{finalProperties:JSON.stringify(updatedProperties),finalComponent:JSON.stringify(componentUpdates)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion

    return {
        properties: updatedProperties,
        component: componentUpdates
    };
}

/**
 * Get active component info for applying properties
 */
export function getActiveComponentInfo() {
    return {
        componentName: activeComponentName,
        componentId: activeComponentId,
        path: activePath ? [...activePath] : null
    };
}

