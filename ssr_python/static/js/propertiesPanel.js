import { getComponentSchema, getComponentDefaults, getSchemaTokens } from './metadataLoader.js';
import { deepClone, deepMerge, getNestedValue, setNestedValue } from './utils/object.js';

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

    if (!component || !componentId) {
        propertiesContent.innerHTML = '<p class="properties-empty-state">Select a component to edit.</p>';
        return;
    }

    const schema = getComponentSchema(component.name);
    if (!schema) {
        propertiesContent.innerHTML = '<p style="color: #b91c1c; font-size: 1.2rem; text-align: center; padding: 2rem 0;">No schema available for this component yet.</p>';
        return;
    }

    const defaults = getComponentDefaults(component.name);
    const resolvedProps = deepMerge({}, defaults, component.properties || {});

    propertiesContent.innerHTML = '';
    const formContainer = document.createElement('div');
    formContainer.className = 'properties-form';

    schema.groups?.forEach(group => {
        const groupEl = document.createElement('div');
        groupEl.className = 'property-group';
        const heading = document.createElement('h4');
        heading.textContent = group.label || group.id;
        groupEl.appendChild(heading);

        group.fields?.forEach(field => {
            const pathSegments = pathToSegments(field.path);
            const target = determineFieldTarget(field, component);
            const defaultValue = getNestedValue(defaults, pathSegments);
            const currentValue = resolvePropertyValue(component, pathSegments, defaults, target);
            const fieldId = `prop_${componentId}_${field.path.replace(/[^a-z0-9]/gi, '_')}`;

            // Skip custom fields for now (can be added later)
            if (field.type === 'custom') {
                return;
            }

            const { wrapper } = createFieldWrapper(field, fieldId);
            let control;

            switch (field.type) {
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
                    control = renderSelect({ field, value: currentValue, fieldId });
                    wrapper.appendChild(control);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'checkbox':
                    const checkboxResult = renderCheckbox({ field, value: currentValue, fieldId });
                    wrapper.innerHTML = '';
                    wrapper.appendChild(checkboxResult.wrapper);
                    activeFieldMeta.set(field.path, { field, target, defaultValue });
                    break;

                case 'color':
                    control = renderColorInput({ field, value: currentValue, fieldId });
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

            groupEl.appendChild(wrapper);
        });

        formContainer.appendChild(groupEl);
    });

    propertiesContent.appendChild(formContainer);

    // Add Apply button (click handler is set up in events.js)
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
    activeComponentName = null;
    activeComponentId = null;
    activePath = null;
    activeFieldMeta.clear();
}

/**
 * Apply properties to component (called from main.js after YAML update)
 * This function reads form values and returns updated component
 */
export function collectPropertyValues() {
    if (!activeComponentName || !activePath) {
        return null;
    }

    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) {
        return null;
    }

    const defaults = getComponentDefaults(activeComponentName);
    const updatedProperties = deepMerge({}, defaults);

    activeFieldMeta.forEach((meta, fieldPath) => {
        const { field, target } = meta;
        const fieldId = `prop_${activeComponentId}_${fieldPath.replace(/[^a-z0-9]/gi, '_')}`;
        const control = propertiesContent.querySelector(`#${fieldId}`);

        if (!control) {
            return;
        }

        let value;
        switch (field.type) {
            case 'number':
                value = control.value === '' ? '' : Number(control.value);
                if (Number.isNaN(value)) {
                    value = '';
                }
                break;
            case 'checkbox':
                value = control.checked;
                break;
            case 'range':
                value = control.controlElement ? Number(control.controlElement.value) : Number(control.value);
                break;
            default:
                value = control.value;
                if ((field.type === 'text' || field.type === 'textarea') && value === '') {
                    value = ' ';
                }
                break;
        }

        if (target === 'component') {
            // Component-level properties are handled separately
            return;
        }

        const pathSegments = pathToSegments(fieldPath);
        setNestedValue(updatedProperties, pathSegments, value === undefined ? null : value);
    });

    return updatedProperties;
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

