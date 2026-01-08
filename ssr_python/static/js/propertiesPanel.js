import { getComponentSchema, getComponentDefaults, getSchemaTokens } from './metadataLoader.js';
import { deepClone, deepMerge, getNestedValue, setNestedValue } from './utils/object.js';
import { customRenderers } from './customRenderers.js';

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
        const groupEl = document.createElement('div');
        groupEl.className = 'property-group';
        const heading = document.createElement('h4');
        heading.textContent = group.label || group.id;
        groupEl.appendChild(heading);

        group.fields?.forEach(field => {
            const pathSegments = pathToSegments(field.path);
            const target = determineFieldTarget(field, component);
            // Note: defaults is the properties object directly (not wrapped in a 'properties' key)
            const defaultValue = getNestedValue(defaults || {}, pathSegments);
            const currentValue = resolvePropertyValue(component, pathSegments, defaults || {}, target);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:312',message:'renderPropertiesPanel field values',data:{fieldPath:field.path,fieldType:field.type,defaultValue,currentValue,target},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
            // #endregion
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
        const { field, target, defaultValue, customSerializer } = meta;
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

            // Get value from control using helper
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:458',message:'collectPropertyValues before getValueFromControl',data:{fieldPath,fieldType:field.type,controlValue:control.value,controlChecked:control.checked},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        value = getValueFromControl(control, field);
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
            // Apply component-level standard fields
            if (!valuesAreEqual(value, defaultValue)) {
                const pathSegments = pathToSegments(fieldPath);
                setNestedValue(componentUpdates, pathSegments, value === undefined ? null : value);
            }
            return;
        }

        // Only set value if it differs from default (properties-level)
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:480',message:'collectPropertyValues before setNestedValue',data:{fieldPath,value,defaultValue,areEqual:valuesAreEqual(value,defaultValue),updatedPropsBefore:JSON.stringify(updatedProperties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        if (!valuesAreEqual(value, defaultValue)) {
            const pathSegments = pathToSegments(fieldPath);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:483',message:'collectPropertyValues calling setNestedValue',data:{pathSegments,value,updatedPropsBefore:JSON.stringify(updatedProperties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
            // #endregion
            setNestedValue(updatedProperties, pathSegments, value === undefined ? null : value);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'propertiesPanel.js:485',message:'collectPropertyValues after setNestedValue',data:{updatedPropsAfter:JSON.stringify(updatedProperties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
            // #endregion
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

