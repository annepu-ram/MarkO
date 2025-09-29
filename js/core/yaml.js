import { deepClone, setNestedValue, deleteNestedValue } from '../utils/object.js';

const yaml = window.jsyaml;

/**
 * @function parseYamlContent
 * @description Parses a YAML string into a JavaScript object structure.
 * @param {string} text - The YAML content as a string.
 * @returns {Array|null} The parsed JavaScript object (expected to be an array of components), or null if parsing fails.
 * @calledBy {js/ui/actions.js}
 * @calls {window.jsyaml.load}
 */
export function parseYamlContent(text) {
    if (!text || !text.trim()) {
        return [];
    }
    try {
        const parsed = yaml.load(text);
        if (!Array.isArray(parsed)) {
            throw new Error('Root of YAML document must be an array of components');
        }
        return parsed;
    } catch (error) {
        console.error('Failed to parse YAML content:', error);
        return null;
    }
}

/**
 * @function generateYamlFromStructure
 * @description Converts a JavaScript object structure back into a YAML string.
 * @param {Array} structure - The JavaScript object structure to convert.
 * @returns {string} The generated YAML string, or an empty string if conversion fails.
 * @calledBy {js/ui/actions.js}
 * @calls {window.jsyaml.dump}
 */
export function generateYamlFromStructure(structure) {
    try {
        return yaml.dump(structure, { skipInvalid: true, noRefs: true });
    } catch (error) {
        console.error('Failed to generate YAML:', error);
        return '';
    }
}

/**
 * @function getComponentByPath
 * @description Retrieves a component from the YAML structure using its path.
 * @param {Array} structure - The full YAML structure.
 * @param {Array<number|string>} path - The path to the component (e.g., `[0, 'components', 1]`).
 * @returns {object|null} The component object, or null if not found.
 * @calledBy {js/properties/index.js|js/ui/actions.js}
 * @calls {None}
 */
export function getComponentByPath(structure, path) {
    if (!structure) {
        return null;
    }
    const segments = Array.isArray(path) ? path : [];
    let cursor = structure;
    for (const segment of segments) {
        if (cursor === undefined || cursor === null) {
            return null;
        }
        cursor = cursor[segment];
    }
    return cursor || null;
}

/**
 * @function updateComponentByPath
 * @description Updates a component in the YAML structure using its path.
 * @param {Array} structure - The full YAML structure.
 * @param {Array<number|string>} path - The path to the component to update.
 * @param {object} newComponent - The new component object to insert.
 * @returns {Array} A new YAML structure with the updated component.
 * @calledBy {js/properties/index.js|js/ui/actions.js}
 * @calls {deepClone}
 */
export function updateComponentByPath(structure, path, newComponent) {
    if (!structure) {
        return structure;
    }
    if (path.length === 0) {
        return deepClone(newComponent);
    }
    const newStructure = deepClone(structure);
    let cursor = newStructure;
    for (let index = 0; index < path.length - 1; index += 1) {
        cursor = cursor[path[index]];
    }
    cursor[path[path.length - 1]] = newComponent;
    return newStructure;
}

/**
 * @function deleteComponentByPath
 * @description Deletes a component from the YAML structure using its path.
 * @param {Array} structure - The full YAML structure.
 * @param {Array<number|string>} path - The path to the component to delete.
 * @returns {Array} A new YAML structure with the component removed.
 * @calledBy {js/ui/actions.js}
 * @calls {deepClone|getComponentByPath}
 */
export function deleteComponentByPath(structure, path) {
    if (!structure || path.length === 0) {
        return structure;
    }
    const newStructure = deepClone(structure);
    const parentPath = path.slice(0, -1);
    const index = path[path.length - 1];
    const parent = getComponentByPath(newStructure, parentPath);
    if (Array.isArray(parent)) {
        parent.splice(index, 1);
    } else if (parent && typeof parent === 'object') {
        if (Array.isArray(parent.components)) {
            parent.components.splice(index, 1);
        } else {
            delete parent[index];
        }
    }
    return newStructure;
}

/**
 * @function setValueByPath
 * @description Sets a nested value within an object using a path array.
 * @param {object} target - The object to modify.
 * @param {Array<string>} path - The path to the value (e.g., `['properties', 'typography', 'align']`).
 * @param {*} value - The value to set.
 * @returns {void}
 * @calledBy {None}
 * @calls {setNestedValue}
 */
export function setValueByPath(target, path, value) {
    setNestedValue(target, path, value);
}

/**
 * @function deleteValueByPath
 * @description Deletes a nested value from an object using a path array.
 * @param {object} target - The object to modify.
 * @param {Array<string>} path - The path to the value to delete.
 * @returns {void}
 * @calledBy {None}
 * @calls {deleteNestedValue}
 */
export function deleteValueByPath(target, path) {
    deleteNestedValue(target, path);
}