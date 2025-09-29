import { setComponentTemplates, setComponentSchemas, setSchemaTokens } from './state.js';

const yaml = window.jsyaml;

/**
 * @function loadYamlFile
 * @description Fetches and parses a YAML file from the given path.
 * @param {string} path - The path to the YAML file.
 * @returns {Promise<object>} A promise that resolves with the parsed YAML content.
 * @throws {Error} If the file fails to load.
 * @calledBy {loadComponentTemplates|loadComponentSchemas|loadSchemaTokens}
 * @calls {fetch|Response.text|window.jsyaml.load}
 */
async function loadYamlFile(path) {
    const response = await fetch(path);
    if (!response.ok) {
        throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    const text = await response.text();
    return yaml.load(text);
}

/**
 * @function loadComponentTemplates
 * @description Loads component templates from 'component_defaults.yaml' and sets them in the state.
 * @returns {Promise<object>} A promise that resolves with the loaded templates.
 * @calledBy {loadMetadata}
 * @calls {loadYamlFile|setComponentTemplates}
 */
export async function loadComponentTemplates() {
    const templates = await loadYamlFile('component_defaults.yaml');
    setComponentTemplates(templates || {});
    return templates;
}

/**
 * @function loadComponentSchemas
 * @description Loads component schemas from 'component_schemas.yaml' and sets them in the state.
 * @returns {Promise<object>} A promise that resolves with the loaded schemas.
 * @calledBy {loadMetadata}
 * @calls {loadYamlFile|setComponentSchemas}
 */
export async function loadComponentSchemas() {
    const schemas = await loadYamlFile('component_schemas.yaml');
    setComponentSchemas(schemas || {});
    return schemas;
}

/**
 * @function loadSchemaTokens
 * @description Loads schema tokens from 'schema_tokens.yaml' and sets them in the state.
 * @returns {Promise<object>} A promise that resolves with the loaded tokens.
 * @calledBy {loadMetadata}
 * @calls {loadYamlFile|setSchemaTokens}
 */
export async function loadSchemaTokens() {
    const tokens = await loadYamlFile('schema_tokens.yaml');
    setSchemaTokens(tokens || {});
    return tokens;
}

/**
 * @function loadMetadata
 * @description Loads all component metadata (templates, schemas, tokens) concurrently.
 * @returns {Promise<void>}
 * @calledBy {js/core/app.js}
 * @calls {loadComponentTemplates|loadComponentSchemas|loadSchemaTokens}
 */
export async function loadMetadata() {
    await Promise.all([
        loadComponentTemplates(),
        loadComponentSchemas(),
        loadSchemaTokens(),
    ]);
}