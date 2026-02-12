/**
 * YAML utility functions for SSR
 * Uses eemeli/yaml via yamlWrapper for native anchor/alias support
 */
import { deepClone } from './utils/object.js';
import { parse, stringify, parseDocument, stringifyDocument, YAML } from './yamlWrapper.js';

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
        return parse(editor.value);
    } catch (error) {
        console.error('Failed to parse YAML:', error);
        return null;
    }
}

/**
 * Get YAML Document from editor (preserves anchors/aliases)
 * Use this when you need to work with anchors
 * @returns {Document|null} YAML Document or null on error
 */
export function getYamlDocumentFromEditor() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return null;

    if (!editor.value || editor.value.trim() === '') {
        return null;
    }

    try {
        const doc = parseDocument(editor.value);
        if (doc.errors && doc.errors.length > 0) {
            console.error('YAML parse errors:', doc.errors);
            return null;
        }
        return doc;
    } catch (error) {
        console.error('Failed to parse YAML document:', error);
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
        return stringify(structure, {
            indent: 2,
            lineWidth: -1  // Unlimited line width
        });
    } catch (error) {
        console.error('Failed to generate YAML:', error);
        return '';
    }
}

/**
 * Generate YAML string from Document (preserves anchors/aliases)
 * @param {Document} doc - YAML Document
 * @returns {string} YAML string with anchors preserved
 */
export function generateYamlFromDocument(doc) {
    try {
        return stringifyDocument(doc);
    } catch (error) {
        console.error('Failed to stringify YAML document:', error);
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

/**
 * Navigate to a component node in the YAML Document AST
 * @param {Document} doc - YAML Document
 * @param {Array} componentPath - Path to component (e.g., [0, 'components', 1])
 * @returns {YAMLMap|null} Component node or null if not found
 */
export function navigateToComponent(doc, componentPath) {
    if (!doc || !componentPath) {
        return null;
    }

    let currentNode = doc.contents;
    for (const segment of componentPath) {
        if (!currentNode) {
            console.error('[YAML] Could not navigate to path segment:', segment);
            return null;
        }

        if (typeof segment === 'number') {
            // Array index - currentNode should be a sequence
            if (YAML.isSeq(currentNode)) {
                currentNode = currentNode.items[segment];
            } else if (Array.isArray(currentNode)) {
                currentNode = currentNode[segment];
            } else {
                console.error('[YAML] Expected sequence at path segment:', segment);
                return null;
            }
        } else {
            // Object key - currentNode should be a map
            if (YAML.isMap(currentNode)) {
                currentNode = currentNode.get(segment, true);
            } else if (typeof currentNode === 'object') {
                currentNode = currentNode[segment];
            } else {
                console.error('[YAML] Expected map at path segment:', segment);
                return null;
            }
        }
    }

    return currentNode && YAML.isMap(currentNode) ? currentNode : null;
}

/**
 * Update a component's properties in the YAML Document AST
 * This preserves anchors and aliases by modifying the document directly
 * @param {Document} doc - YAML Document
 * @param {Array} componentPath - Path to component (e.g., [0, 'components', 1])
 * @param {object} propertyUpdates - Object with property updates to apply
 * @returns {Document} Modified document (same reference)
 */
export function updateComponentPropertiesInDocument(doc, componentPath, propertyUpdates) {
    if (!doc || !componentPath) {
        console.error('[YAML] updateComponentPropertiesInDocument: missing doc or path');
        return doc;
    }

    // Navigate to the component in the document
    const componentNode = navigateToComponent(doc, componentPath);
    if (!componentNode) {
        console.error('[YAML] Component not found at path');
        return doc;
    }

    // Get or create 'properties' map
    let propsNode = componentNode.get('properties', true);
    if (!propsNode) {
        // Create properties map if it doesn't exist
        componentNode.set('properties', {});
        propsNode = componentNode.get('properties', true);
    }

    // Apply property updates recursively
    applyUpdatesToNode(propsNode, propertyUpdates, doc);

    return doc;
}

/**
 * Recursively apply updates to a YAML node while preserving aliases
 * @param {any} node - YAML node (Map, Seq, Scalar, or Alias)
 * @param {any} updates - Updates to apply
 * @param {Document} doc - Parent document for creating nodes
 */
function applyUpdatesToNode(node, updates, doc) {
    if (!YAML.isMap(node) || typeof updates !== 'object' || updates === null) {
        return;
    }

    for (const [key, value] of Object.entries(updates)) {
        const existingNode = node.get(key, true);

        if (value === null || value === undefined) {
            // Remove the key
            node.delete(key);
        } else if (typeof value === 'object' && !Array.isArray(value)) {
            // Nested object - recurse if existing is a map, otherwise replace
            if (existingNode && YAML.isMap(existingNode)) {
                applyUpdatesToNode(existingNode, value, doc);
            } else if (existingNode && YAML.isAlias(existingNode)) {
                // Don't overwrite aliases with objects - preserve the alias
                // This handles the case where a theme color alias exists
                console.log('[YAML] Preserving alias for key:', key);
            } else {
                // Create new nested structure
                node.set(key, value);
            }
        } else if (Array.isArray(value)) {
            // Arrays - replace entirely
            node.set(key, value);
        } else {
            // Primitive value
            if (existingNode && YAML.isAlias(existingNode)) {
                // Check if this is a theme color alias we should preserve
                // If the new value is the same as the resolved alias value, keep the alias
                const resolvedValue = existingNode.resolve(doc);
                if (resolvedValue === value) {
                    console.log('[YAML] Keeping alias, value unchanged:', key, value);
                    continue; // Don't overwrite - keep the alias
                }
                // Value changed - need to replace the alias with the new value
                console.log('[YAML] Replacing alias with new value:', key, value);
            }
            node.set(key, value);
        }
    }
}

/**
 * Replace specific property values with YAML aliases (for theme color swatches).
 * After updateComponentPropertiesInDocument sets plain values, this replaces
 * tagged fields with alias nodes pointing to the theme color anchors.
 * @param {Document} doc - YAML Document
 * @param {Array} componentPath - Path to component
 * @param {object} aliases - Map of fieldPath -> anchorName (e.g., { 'typography.color': 'color-primary' })
 */
export function replacePropertiesWithAliases(doc, componentPath, aliases) {
    if (!doc || !componentPath || !aliases || Object.keys(aliases).length === 0) return;

    // Find theme colors node (where anchors are defined)
    const pageNode = doc.contents.items[0];
    if (!pageNode) return;
    const themeColors = pageNode.get('properties', true)?.get('theme', true)?.get('colors', true);
    if (!themeColors || !YAML.isMap(themeColors)) return;

    // Build anchor-name -> node map
    const anchorMap = new Map();
    for (const pair of themeColors.items) {
        if (YAML.isPair(pair) && YAML.isScalar(pair.value) && pair.value.anchor) {
            anchorMap.set(pair.value.anchor, pair.value);
        }
    }

    // Navigate to the component's properties
    const componentNode = navigateToComponent(doc, componentPath);
    if (!componentNode) return;
    const propsNode = componentNode.get('properties', true);
    if (!propsNode || !YAML.isMap(propsNode)) return;

    // For each alias, navigate the dot-path and replace with alias node
    for (const [fieldPath, anchorName] of Object.entries(aliases)) {
        const anchorNode = anchorMap.get(anchorName);
        if (!anchorNode) continue;

        const segments = fieldPath.split('.');
        let node = propsNode;
        for (let i = 0; i < segments.length - 1; i++) {
            node = node.get(segments[i], true);
            if (!node || !YAML.isMap(node)) break;
        }
        if (node && YAML.isMap(node)) {
            node.set(segments[segments.length - 1], doc.createAlias(anchorNode));
        }
    }
}

// Re-export for advanced usage (Document API, type checks)
export { YAML, parseDocument, stringifyDocument };
