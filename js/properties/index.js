import { getComponentTemplates, getComponentSchemas, getSchemaTokens } from '../core/state.js';
import { getComponentByPath, updateComponentByPath } from '../core/yaml.js';
import { deepClone, deepMerge, getNestedValue, setNestedValue, deleteNestedValue, pruneEmptyValues } from '../utils/object.js';
import { customRenderers } from './customRenderers.js';

let activeComponentName = null;
let activeFieldMeta = new Map();
let activeCustomEditors = [];

/**
 * @function pathToSegments
 * @description Converts a dot-separated path string into an array of segments.
 * @param {string|Array} path - The path string or array.
 * @returns {Array<string>}
 * @calledBy {renderPropertiesPanel|applyPropertiesForComponent|resolvePropertyValue|resolveDefaultValue|determineFieldTarget}
 * @calls {None}
 */
const pathToSegments = path => (Array.isArray(path) ? path : String(path || '').split('.').filter(Boolean));

/**
 * @function getTemplateDefaults
 * @description Retrieves the default properties for a given component name.
 * @param {string} componentName - The name of the component.
 * @returns {object} A deep clone of the component's default properties.
 * @calledBy {renderPropertiesPanel|applyPropertiesForComponent}
 * @calls {getComponentTemplates|deepClone}
 */
const getTemplateDefaults = componentName => {
    const templates = getComponentTemplates();
    return deepClone(templates?.[componentName] || {});
};

/**
 * @function getComponentSchema
 * @description Retrieves the schema definition for a given component name.
 * @param {string} componentName - The name of the component.
 * @returns {object|null} The component's schema, or null if not found.
 * @calledBy {renderPropertiesPanel}
 * @calls {getComponentSchemas}
 */
const getComponentSchema = componentName => {
    const schemas = getComponentSchemas();
    return schemas?.[componentName] || null;
};

/**
 * @function getTokenOptions
 * @description Retrieves the options for a given schema token name.
 * @param {string} tokenName - The name of the token (e.g., 'spacingScale').
 * @returns {Array<object|string>} An array of token options.
 * @calledBy {renderSelect}
 * @calls {getSchemaTokens}
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

const baseInputClass = 'property-input';

/**
 * @function createFieldWrapper
 * @description Creates a DOM wrapper for a property input field, including its label.
 * @param {object} field - The field definition from the component schema.
 * @param {string} fieldId - The unique ID for the input field.
 * @returns {{wrapper: HTMLElement, label: HTMLLabelElement}} An object containing the wrapper div and the label element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement}
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
 * @function resolvePropertyValue
 * @description Resolves the current value of a property, prioritizing component-specific values over defaults.
 * @param {object} component - The component object.
 * @param {Array<string>} pathSegments - The path to the property as an array of segments.
 * @param {object} defaults - The default properties for the component.
 * @param {string} [target='properties'] - Specifies if the property is directly on the 'component' or within its 'properties' sub-object.
 * @returns {*} The resolved property value, or undefined if not found.
 * @calledBy {renderPropertiesPanel}
 * @calls {getNestedValue}
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
 * @function resolveDefaultValue
 * @description Resolves the default value of a property from the component's default properties.
 * @param {object} defaults - The default properties for the component.
 * @param {Array<string>} pathSegments - The path to the property as an array of segments.
 * @param {string} [target='properties'] - Specifies if the property is directly on the 'component' or within its 'properties' sub-object.
 * @returns {*} The default property value, or undefined if not found.
 * @calledBy {renderPropertiesPanel}
 * @calls {getNestedValue}
 */
const resolveDefaultValue = (defaults, pathSegments, target = 'properties') => {
    if (!pathSegments.length) {
        return undefined;
    }
    if (target === 'component') {
        return getNestedValue(defaults, pathSegments);
    }
    return getNestedValue(defaults, pathSegments);
};

/**
 * @function determineFieldTarget
 * @description Determines whether a field's value is stored directly on the component object or within its 'properties' sub-object.
 * @param {object} field - The field definition from the component schema.
 * @param {object} component - The component object.
 * @returns {string} 'component' if the field targets the component directly, otherwise 'properties'.
 * @calledBy {renderPropertiesPanel}
 * @calls {None}
 */
const determineFieldTarget = (field, component) => {
    if (field.type === 'custom') {
        if (!field.path.includes('.')) {
            return 'component';
        }
        return 'properties';
    }
    if (field.path.includes('.')) {
        return 'properties';
    }
    // If component has property directly on top-level and schema path has no dot, treat as component-level
    if (component[field.path] !== undefined) {
        return 'component';
    }
    return 'properties';
};

/**
 * @function renderTextInput
 * @description Renders a standard HTML text input element.
 * @param {object} options - Options for rendering the input.
 * @param {object} options.field - The field definition.
 * @param {*} options.value - The current value of the input.
 * @param {string} options.fieldId - The ID for the input element.
 * @param {string} [options.type='text'] - The type of the input (e.g., 'text', 'number').
 * @returns {HTMLInputElement} The created input element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement}
 */
const renderTextInput = ({ field, value, fieldId, type = 'text' }) => {
    const input = document.createElement('input');
    input.type = type;
    input.id = fieldId;
    input.className = baseInputClass;
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
 * @function renderTextarea
 * @description Renders an HTML textarea element.
 * @param {object} options - Options for rendering the textarea.
 * @param {object} options.field - The field definition.
 * @param {string} options.value - The current value of the textarea.
 * @param {string} options.fieldId - The ID for the textarea element.
 * @returns {HTMLTextAreaElement} The created textarea element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement}
 */
const renderTextarea = ({ field, value, fieldId }) => {
    const textarea = document.createElement('textarea');
    textarea.id = fieldId;
    textarea.className = `${baseInputClass} property-textarea`;
    textarea.rows = field.rows || 3;
    textarea.value = value || '';
    if (field.placeholder) {
        textarea.placeholder = field.placeholder;
    }
    return textarea;
};

/**
 * @function renderSelect
 * @description Renders an HTML select element with options.
 * @param {object} options - Options for rendering the select.
 * @param {object} options.field - The field definition.
 * @param {*} options.value - The current value of the select.
 * @param {string} options.fieldId - The ID for the select element.
 * @returns {HTMLSelectElement} The created select element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement|getTokenOptions}
 */
const renderSelect = ({ field, value, fieldId }) => {
    const select = document.createElement('select');
    select.id = fieldId;
    select.className = baseInputClass;
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
 * @function renderCheckbox
 * @description Renders an HTML checkbox element.
 * @param {object} options - Options for rendering the checkbox.
 * @param {object} options.field - The field definition.
 * @param {boolean} options.value - The current checked state of the checkbox.
 * @param {string} options.fieldId - The ID for the checkbox element.
 * @returns {{wrapper: HTMLElement, input: HTMLInputElement}} An object containing the wrapper div and the input element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement}
 */
const renderCheckbox = ({ field, value, fieldId }) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'property-item property-checkbox';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = fieldId;
    input.className = baseInputClass;
    input.checked = Boolean(value);
    const label = document.createElement('label');
    label.htmlFor = fieldId;
    label.textContent = field.label || field.path;
    wrapper.appendChild(input);
    wrapper.appendChild(label);
    return { wrapper, input };
};

/**
 * @function renderColorInput
 * @description Renders an HTML text input element specifically for color values.
 * @param {object} options - Options for rendering the color input.
 * @param {object} options.field - The field definition.
 * @param {string} options.value - The current color value.
 * @param {string} options.fieldId - The ID for the input element.
 * @returns {HTMLInputElement} The created input element.
 * @calledBy {renderPropertiesPanel}
 * @calls {document.createElement}
 */
const renderColorInput = ({ field, value, fieldId }) => {
    const input = document.createElement('input');
    input.type = 'color';
    input.id = fieldId;
    input.className = baseInputClass;
    input.value = value || '';
    input.placeholder = field.placeholder || '#RRGGBB or CSS value';
    return input;
};

/**
 * @function ensureApplyButton
 * @description Ensures that the 'Apply Changes' button is present in the properties panel and its disabled state is correct.
 * @param {boolean} componentSelected - True if a component is currently selected, false otherwise.
 * @returns {void}
 * @calledBy {renderPropertiesPanel|clearPropertiesPanel}
 * @calls {document.getElementById|document.querySelector|document.createElement}
 */
const ensureApplyButton = (componentSelected) => {
    const panel = document.getElementById('propertiesPanel');
    if (!panel) {
        return;
    }
    let applyButton = panel.querySelector('.properties-apply-button');
    if (!applyButton) {
        applyButton = document.createElement('button');
        applyButton.type = 'button';
        applyButton.className = 'btn btn-primary properties-apply-button';
        applyButton.textContent = 'Apply Changes';
        panel.appendChild(applyButton);
    }
    applyButton.disabled = !componentSelected;
};

/**
 * Renders the properties panel for a selected component.
 * @param {object} component The component to render the properties for.
 * @param {string} componentId The ID of the component.
 * @param {Array} path The path to the component in the YAML structure.
 */
export function renderPropertiesPanel(component, componentId, path) {
    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) {
        return;
    }

    activeComponentName = component?.name || null;
    activeFieldMeta = new Map();
    activeCustomEditors = [];

    if (!component || !componentId) {
        propertiesContent.innerHTML = '<p style="color: #666; font-style: italic; font-size: 1.2rem; text-align: center; padding: 2rem 0;">Select a component to edit.</p>';
        ensureApplyButton(false);
        return;
    }

    const schema = getComponentSchema(component.name);
    if (!schema) {
        propertiesContent.innerHTML = '<p style="color: #b91c1c; font-size: 1.2rem; text-align: center; padding: 2rem 0;">No schema available for this component yet.</p>';
        ensureApplyButton(false);
        return;
    }

    const defaults = getTemplateDefaults(component.name);
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
            const defaultValue = resolveDefaultValue(defaults, pathSegments, target);
            const currentValue = resolvePropertyValue(component, pathSegments, defaults, target);
            const fieldId = `prop_${componentId}_${field.path.replace(/[^a-z0-9]/gi, '_')}`;

            if (field.type === 'custom') {
                const renderer = customRenderers[field.renderer];
                const { wrapper: customWrapper } = createFieldWrapper(field, fieldId);
                customWrapper.classList.add('property-item-custom');

                let renderedEditor = null;
                if (renderer && typeof renderer.render === 'function') {
                    renderedEditor = renderer.render({ value: currentValue, field, component });
                }

                if (renderedEditor && renderedEditor.element) {
                    const renderedElement = renderedEditor.element;
                    renderedElement.id = fieldId;
                    renderedElement.dataset.customRenderer = field.renderer;
                    renderedElement.dataset.fieldPath = field.path;
                    customWrapper.appendChild(renderedElement);
                    groupEl.appendChild(customWrapper);
                    activeCustomEditors.push({
                        path: field.path,
                        target,
                        renderer: field.renderer,
                        instance: renderedEditor,
                        defaultValue,
                    });
                } else {
                    const placeholder = document.createElement('p');
                    placeholder.className = 'helper-text';
                    placeholder.textContent = 'Custom editor not available.';
                    customWrapper.appendChild(placeholder);
                    groupEl.appendChild(customWrapper);
                }
                return;
            }

            if (field.type === 'checkbox') {
                const { wrapper, input } = renderCheckbox({ field, value: currentValue, fieldId });
                input.dataset.fieldPath = field.path;
                input.dataset.fieldType = field.type;
                groupEl.appendChild(wrapper);
                activeFieldMeta.set(field.path, {
                    field,
                    defaultValue,
                    target,
                });
                return;
            }

            const { wrapper, label } = createFieldWrapper(field, fieldId);
            let control;
            switch (field.type) {
                case 'textarea':
                    control = renderTextarea({ field, value: currentValue, fieldId });
                    break;
                case 'select':
                    control = renderSelect({ field, value: currentValue, fieldId });
                    break;
                case 'number':
                    control = renderTextInput({ field, value: currentValue, fieldId, type: 'number' });
                    break;
                case 'color':
                    control = renderColorInput({ field, value: currentValue, fieldId });
                    break;
                default:
                    control = renderTextInput({ field, value: currentValue, fieldId, type: 'text' });
                    break;
            }
            control.dataset.fieldPath = field.path;
            control.dataset.fieldType = field.type;
            wrapper.appendChild(control);
            groupEl.appendChild(wrapper);
            activeFieldMeta.set(field.path, {
                field,
                defaultValue,
                target,
            });
        });

        formContainer.appendChild(groupEl);
    });

    propertiesContent.appendChild(formContainer);
    ensureApplyButton(true);
}

/**
 * Clears the properties panel.
 */
export function clearPropertiesPanel() {
    const propertiesContent = document.getElementById('propertiesContent');
    if (propertiesContent) {
        propertiesContent.innerHTML = '<p style="color: #666; font-style: italic; font-size: 1.2rem; text-align: center; padding: 2rem 0;">Select a component to edit.</p>';
    }
    ensureApplyButton(false);
    activeComponentName = null;
    activeFieldMeta = new Map();
    activeCustomEditors = [];
}

/**
 * @function removeDefaults
 * @description Recursively removes properties from a target object if their values match the corresponding default values.
 *   This is used to keep the YAML output clean by not serializing redundant default properties.
 * @param {object} target - The object from which to remove default-matching properties.
 * @param {object} defaults - The object containing default values for comparison.
 * @returns {void}
 * @calledBy {applyPropertiesForComponent}
 * @calls {JSON.stringify}
 */


/**
 * Applies the properties from the properties panel to the selected component.
 * @param {object} options The options for applying the properties.
 * @param {string} options.componentId The ID of the component.
 * @param {Array} options.path The path to the component in the YAML structure.
 * @param {object} options.structure The current YAML structure.
 * @returns {{updatedStructure: object, nextSelectionPath: Array} | null} The updated structure and the next selection path, or null if the operation fails.
 */
export function applyPropertiesForComponent({ componentId, path, structure }) {
    if (!activeComponentName || !structure || !path) {
        return null;
    }
    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) {
        return null;
    }

    const component = getComponentByPath(structure, path);
    if (!component) {
        return null;
    }
    const defaults = getTemplateDefaults(activeComponentName);
    const updatedComponent = deepClone(component);
    updatedComponent.properties = deepClone(component.properties || {});

    activeFieldMeta.forEach((meta, fieldPath) => {
        const control = propertiesContent.querySelector(`[data-field-path="${fieldPath}"]`);
        if (!control) {
            return;
        }
        const pathSegments = pathToSegments(fieldPath);
        const { field, defaultValue, target } = meta;
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
            default:
                value = control.value.trim();
                break;
        }

        const destination = target === 'component' ? updatedComponent : updatedComponent.properties;
        if (field.type !== 'checkbox' && (value === '' || value === null)) {
            deleteNestedValue(destination, pathSegments);
        } else {
            setNestedValue(destination, pathSegments, value);
        }
    });

    activeCustomEditors.forEach(entry => {
        const { path: fieldPath, target, instance, defaultValue } = entry;
        if (!instance || typeof instance.serialize !== 'function') {
            return;
        }
        const value = instance.serialize();
        const destination = target === 'component' ? updatedComponent : updatedComponent.properties;
        const pathSegments = pathToSegments(fieldPath);
        if (value === undefined || value === null) {
            deleteNestedValue(destination, pathSegments);
        } else {
            setNestedValue(destination, pathSegments, value);
        }
    });

    
    const updatedStructure = updateComponentByPath(structure, path, updatedComponent);

    // Create a *separate* cleaned version of the component for YAML generation (editor display)
    const cleanedComponentForYaml = deepClone(updatedComponent); // Clone the fully updated component

    return {
        updatedStructure,
        nextSelectionPath: path,
        cleanedComponent: cleanedComponentForYaml, // The cleaned component for editor YAML display
    };
}