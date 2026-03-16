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

    // Find theme colors node: prefer site.properties.theme, fallback to page
    const siteNode = doc.contents.items[0];
    if (!siteNode) return;

    let themeColors = siteNode.get('properties', true)?.get('theme', true)?.get('colors', true);
    if (!themeColors || !YAML.isMap(themeColors)) {
        // Fallback: page-level theme
        const siteComponents = siteNode.get('components', true);
        if (YAML.isSeq(siteComponents) && siteComponents.items.length > 0) {
            const pageNode = siteComponents.items[0];
            if (YAML.isMap(pageNode)) {
                themeColors = pageNode.get('properties', true)?.get('theme', true)?.get('colors', true);
            }
        }
    }
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

/**
 * Delete a component from the YAML Document AST by its path.
 * Navigates to the parent sequence and removes the item at the given index.
 * @param {Document} doc - YAML Document
 * @param {Array} componentPath - Path to component (e.g., [0, 'components', 2])
 * @returns {boolean} True if component was deleted, false otherwise
 */
export function deleteComponentInDocument(doc, componentPath) {
    if (!doc || !componentPath || componentPath.length < 2) {
        // Can't delete root-level components (path too short)
        return false;
    }

    // Last segment is the index within the parent sequence
    const index = componentPath[componentPath.length - 1];
    // Parent path leads to the sequence (e.g., [0, 'components'])
    const parentPath = componentPath.slice(0, -1);

    // Navigate to parent sequence
    let node = doc.contents;
    for (const segment of parentPath) {
        if (!node) return false;
        if (typeof segment === 'number') {
            node = YAML.isSeq(node) ? node.items[segment] : node[segment];
        } else {
            node = YAML.isMap(node) ? node.get(segment, true) : node[segment];
        }
    }

    // Parent should be a sequence — delete the item by index
    if (YAML.isSeq(node) && typeof index === 'number' && index >= 0 && index < node.items.length) {
        node.items.splice(index, 1);
        return true;
    }
    return false;
}

/**
 * Get the children array key for a given component name.
 * @param {string} componentName - Component type name
 * @returns {string|null} Children key ('components', 'columns', 'tabs', 'slides', 'items') or null for leaf components
 */
export function getChildrenKey(componentName) {
    switch (componentName) {
        case 'page':
        case 'layout-row':
        case 'layout-column':
        case 'form':
        case 'video-background':
        case 'hamburger':
            return 'components';
        case 'columnsgrid':
        case 'ticker':
            return 'columns';
        case 'tabs':
            return 'tabs';
        case 'carousel':
            return 'slides';
        case 'accordion':
            return 'items';
        default:
            return null;
    }
}

/**
 * Insert a new component into a parent sequence in the YAML Document AST.
 * @param {Document} doc - YAML Document
 * @param {Array} parentSeqPath - Path to the parent sequence (e.g., [0, 'components'])
 * @param {object} component - Plain JS object for the new component
 * @param {number} [index] - Index to insert at (appends if undefined)
 * @returns {boolean} True if insertion succeeded
 */
export function insertComponentInDocument(doc, parentSeqPath, component, index) {
    if (!doc || !parentSeqPath || parentSeqPath.length === 0) return false;

    // Navigate to the parent sequence
    let node = doc.contents;
    for (let i = 0; i < parentSeqPath.length; i++) {
        const segment = parentSeqPath[i];
        if (!node) return false;

        if (typeof segment === 'number') {
            node = YAML.isSeq(node) ? node.items[segment] : node[segment];
        } else {
            // String key — might need to create the sequence if it doesn't exist
            let child;
            if (YAML.isMap(node)) {
                child = node.get(segment, true);
            } else if (typeof node === 'object') {
                child = node[segment];
            }

            if (!child && i === parentSeqPath.length - 1 && YAML.isMap(node)) {
                // Last segment doesn't exist — create an empty sequence
                node.set(segment, doc.createNode([]));
                child = node.get(segment, true);
            }
            node = child;
        }
    }

    if (!node || !YAML.isSeq(node)) return false;

    // Create and insert the new node
    const newNode = doc.createNode(component);
    if (typeof index === 'number' && index >= 0 && index <= node.items.length) {
        node.items.splice(index, 0, newNode);
    } else {
        node.items.push(newNode);
    }
    return true;
}

/**
 * Move a component up or down within its parent sequence.
 * @param {Document} doc - YAML Document
 * @param {Array} componentPath - Path to component (e.g., [0, 'components', 2])
 * @param {number} direction - -1 for up, +1 for down
 * @returns {{ success: boolean, newPath?: Array }} Result with new path if moved
 */
export function moveComponentInDocument(doc, componentPath, direction) {
    if (!doc || !componentPath || componentPath.length < 2) {
        return { success: false };
    }

    const index = componentPath[componentPath.length - 1];
    if (typeof index !== 'number') return { success: false };

    const parentPath = componentPath.slice(0, -1);
    const targetIndex = index + direction;

    // Navigate to parent sequence
    let node = doc.contents;
    for (const segment of parentPath) {
        if (!node) return { success: false };
        if (typeof segment === 'number') {
            node = YAML.isSeq(node) ? node.items[segment] : node[segment];
        } else {
            node = YAML.isMap(node) ? node.get(segment, true) : node[segment];
        }
    }

    if (!YAML.isSeq(node)) return { success: false };
    if (targetIndex < 0 || targetIndex >= node.items.length) return { success: false };

    // Swap
    const temp = node.items[index];
    node.items[index] = node.items[targetIndex];
    node.items[targetIndex] = temp;

    return { success: true, newPath: [...parentPath, targetIndex] };
}

// Re-export for advanced usage (Document API, type checks)
export { YAML, parseDocument, stringifyDocument };
