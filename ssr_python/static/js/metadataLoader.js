/**
 * Loads component schemas and defaults from Flask API endpoints
 */

let componentSchemas = {};
let componentDefaults = {};
let schemaTokens = {};
let metadataLoaded = false;

/**
 * Load all metadata from Flask API endpoints
 * @returns {Promise<boolean>} True if successful, false otherwise
 */
export async function loadMetadata() {
    try {
        // Load component schemas
        const schemasResponse = await fetch('/api/schemas');
        if (schemasResponse.ok) {
            componentSchemas = await schemasResponse.json();
        } else {
            console.warn('Failed to load component schemas');
        }

        // Load component defaults
        const defaultsResponse = await fetch('/api/defaults');
        if (defaultsResponse.ok) {
            componentDefaults = await defaultsResponse.json();
        } else {
            console.warn('Failed to load component defaults');
        }

        // Load schema tokens
        const tokensResponse = await fetch('/api/tokens');
        if (tokensResponse.ok) {
            schemaTokens = await tokensResponse.json();
        } else {
            console.warn('Failed to load schema tokens');
        }

        metadataLoaded = true;
        console.log('Metadata loaded successfully');
        return true;
    } catch (error) {
        console.error('Failed to load metadata:', error);
        metadataLoaded = false;
        return false;
    }
}

/**
 * Get component schema by name
 * @param {string} componentName - Component name
 * @returns {object|null} Component schema or null
 */
export function getComponentSchema(componentName) {
    return componentSchemas[componentName] || null;
}

/**
 * Get component defaults by name
 * @param {string} componentName - Component name
 * @returns {object} Component defaults (empty object if not found)
 */
export function getComponentDefaults(componentName) {
    return deepClone(componentDefaults[componentName] || {});
}

/**
 * Get schema tokens
 * @returns {object} Schema tokens
 */
export function getSchemaTokens() {
    return schemaTokens;
}

/**
 * Check if metadata is loaded
 * @returns {boolean} True if metadata is loaded
 */
export function isMetadataLoaded() {
    return metadataLoaded;
}

// Import deepClone helper
function deepClone(value) {
    if (value === undefined) {
        return undefined;
    }
    return JSON.parse(JSON.stringify(value));
}

