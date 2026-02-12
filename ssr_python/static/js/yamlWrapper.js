/**
 * YAML wrapper - compatibility layer for eemeli/yaml
 * Provides js-yaml compatible API + Document API for native anchor/alias support
 *
 * Migration from js-yaml to eemeli/yaml enables:
 * - Native anchor creation: node.anchor = 'color-primary'
 * - Native alias creation: doc.createAlias(anchorNode)
 * - Preserves comments, anchors, aliases when using Document API
 */

// Import from local bundle (CSP-compliant)
import * as YAML from './yaml.bundle.js';

// Re-export the full library for advanced usage
export { YAML };

/**
 * Simple parse - equivalent to jsyaml.load()
 * Returns plain JavaScript objects (anchors resolved, not preserved)
 * @param {string} content - YAML string to parse
 * @returns {Array|object|null} Parsed content or empty array
 */
export function parse(content) {
    if (!content || content.trim() === '') {
        return [];
    }
    try {
        return YAML.parse(content) || [];
    } catch (error) {
        console.error('[YAML] Parse error:', error);
        throw error;
    }
}

/**
 * Simple stringify - equivalent to jsyaml.dump()
 * Auto-generates anchors for duplicate object references
 * @param {any} value - Value to stringify
 * @param {object} options - Stringify options
 * @returns {string} YAML string
 */
export function stringify(value, options = {}) {
    const defaultOptions = {
        indent: 2,
        lineWidth: 0,  // 0 means unlimited (equivalent to js-yaml's -1)
    };

    // Map js-yaml options to eemeli/yaml options
    const mappedOptions = { ...defaultOptions };

    if (options.indent !== undefined) {
        mappedOptions.indent = options.indent;
    }
    if (options.lineWidth !== undefined) {
        // js-yaml uses -1 for unlimited, eemeli/yaml uses 0
        mappedOptions.lineWidth = options.lineWidth === -1 ? 0 : options.lineWidth;
    }

    try {
        return YAML.stringify(value, mappedOptions);
    } catch (error) {
        console.error('[YAML] Stringify error:', error);
        throw error;
    }
}

/**
 * Parse to Document - preserves anchors, aliases, and comments
 * Use this when you need to work with anchors
 * @param {string} content - YAML string to parse
 * @returns {Document} YAML Document object
 */
export function parseDocument(content) {
    if (!content || content.trim() === '') {
        return new YAML.Document([]);
    }
    try {
        const doc = YAML.parseDocument(content);
        if (doc.errors && doc.errors.length > 0) {
            console.warn('[YAML] Parse warnings:', doc.errors);
        }
        return doc;
    } catch (error) {
        console.error('[YAML] parseDocument error:', error);
        throw error;
    }
}

/**
 * Create a new empty Document
 * @param {any} value - Initial value for the document
 * @returns {Document} New YAML Document
 */
export function createDocument(value) {
    return new YAML.Document(value);
}

/**
 * Stringify a Document - preserves anchors and aliases
 * @param {Document} doc - YAML Document to stringify
 * @returns {string} YAML string with anchors/aliases preserved
 */
export function stringifyDocument(doc) {
    return String(doc);
}

/**
 * Check if a node is a Map
 * @param {any} node - Node to check
 * @returns {boolean}
 */
export function isMap(node) {
    return YAML.isMap(node);
}

/**
 * Check if a node is a Sequence (array)
 * @param {any} node - Node to check
 * @returns {boolean}
 */
export function isSeq(node) {
    return YAML.isSeq(node);
}

/**
 * Check if a node is a Scalar (primitive value)
 * @param {any} node - Node to check
 * @returns {boolean}
 */
export function isScalar(node) {
    return YAML.isScalar(node);
}

/**
 * Check if a node is a Pair (key-value)
 * @param {any} node - Node to check
 * @returns {boolean}
 */
export function isPair(node) {
    return YAML.isPair(node);
}

/**
 * Check if a node is an Alias
 * @param {any} node - Node to check
 * @returns {boolean}
 */
export function isAlias(node) {
    return YAML.isAlias(node);
}

// Backward compatibility shim - mimics window.jsyaml interface
export const jsyamlCompat = {
    load: parse,
    dump: stringify,
    // Extended API for anchor-aware operations
    parseDocument,
    createDocument,
    stringifyDocument,
    // Type checks
    isMap,
    isSeq,
    isScalar,
    isPair,
    isAlias,
    // Full library access
    YAML
};

// Expose globally for backward compatibility during transition
// This allows code using window.jsyaml.load() to continue working
if (typeof window !== 'undefined') {
    window.yamlLib = jsyamlCompat;
    window.jsyaml = jsyamlCompat;
    console.log('[YAML] eemeli/yaml wrapper loaded, window.jsyaml available');
}
