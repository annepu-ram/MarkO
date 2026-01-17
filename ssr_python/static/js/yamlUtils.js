/**
 * YAML utility functions for SSR
 */
import { deepClone } from './utils/object.js';

/**
 * Get YAML structure from editor
 * @returns {Array|null} Parsed YAML structure or null on error
 */
export function getYamlStructureFromEditor() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return null;

    // Check for empty content
    if (!editor.value || editor.value.trim() === '') {
        return [];
    }

    try {
        // Check both global and window.jsyaml (module scripts may not see bare globals)
        const yaml = typeof jsyaml !== 'undefined' ? jsyaml : window.jsyaml;
        if (yaml) {
            return yaml.load(editor.value) || [];
        }
        console.warn('YAML parser not available');
        return null;
    } catch (error) {
        console.error('Failed to parse YAML:', error);
        return null;
    }
}

/**
 * Get component by path from YAML structure
 * @param {Array} structure - YAML structure
 * @param {Array} path - Path to component
 * @returns {object|null} Component or null if not found
 */
export function getComponentByPath(structure, path) {
    if (!structure || !path || path.length === 0) {
        return null;
    }

    let cursor = structure;
    for (const segment of path) {
        if (cursor === null || cursor === undefined) {
            return null;
        }
        cursor = cursor[segment];
    }
    return cursor || null;
}

/**
 * Update component by path in YAML structure
 * @param {Array} structure - YAML structure
 * @param {Array} path - Path to component
 * @param {object} newComponent - Updated component
 * @returns {Array} New YAML structure with updated component
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
    cursor[path[path.length - 1]] = deepClone(newComponent);
    return newStructure;
}

/**
 * Generate YAML string from structure
 * @param {Array} structure - YAML structure
 * @returns {string} YAML string
 */
export function generateYamlFromStructure(structure) {
    try {
        // Check both global and window.jsyaml (module scripts may not see bare globals)
        const yaml = typeof jsyaml !== 'undefined' ? jsyaml : window.jsyaml;
        if (yaml) {
            return yaml.dump(structure, {
                indent: 2,
                lineWidth: -1,
                noRefs: true,
                sortKeys: false,
                skipInvalid: true
            });
        }
        console.warn('YAML parser not available');
        return '';
    } catch (error) {
        console.error('Failed to generate YAML:', error);
        return '';
    }
}

/**
 * Update YAML editor with new content
 * @param {string} yamlText - YAML string to set
 */
export function updateYamlEditor(yamlText) {
    const editor = document.getElementById('codeEditor');
    if (editor) {
        editor.value = yamlText;
        // Dispatch input event to update line numbers (won't trigger auto-render due to debounce)
        editor.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

