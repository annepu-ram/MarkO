/**
 * @description Manages the application's central state.
 * @property {Array|null} yamlStructure - The parsed YAML structure of the website.
 * @property {object} componentTemplates - Stores default properties for all components.
 * @property {object} componentSchemas - Stores schemas for component properties.
 * @property {object} schemaTokens - Stores design tokens used in schemas.
 * @property {Map<string, Array>} componentPathMap - Maps component IDs to their paths in the YAML structure.
 * @property {Array<object>} componentsToInitialize - Queue of components requiring post-render JavaScript initialization.
 * @property {string|null} selectedComponentId - The ID of the currently selected component in the preview.
 * @property {Array|null} selectedComponentPath - The path of the currently selected component in the YAML structure.
 * @property {boolean} metadataLoaded - Indicates if component metadata (templates, schemas, tokens) has been loaded.
 * @property {object} history - Manages undo/redo history.
 * @property {Array<string>} history.undoStack - Stack of previous YAML states for undo functionality.
 * @property {Array<string>} history.redoStack - Stack of undone YAML states for redo functionality.
 * @property {number} history.maxSize - Maximum size of the undo/redo stacks.
 */
const state = {
    yamlStructure: null,
    componentTemplates: {},
    componentSchemas: {},
    schemaTokens: {},
    componentPathMap: new Map(),
    componentsToInitialize: [],
    selectedComponentId: null,
    selectedComponentPath: null,
    metadataLoaded: false,
    history: {
        undoStack: [],
        redoStack: [],
        maxSize: 50,
    },
};

/**
 * @function getState
 * @description Returns the current immutable state object.
 * @returns {object} The current application state.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function getState() {
    return state;
}

/**
 * @function setYamlStructure
 * @description Sets the main YAML structure in the state.
 * @param {Array} structure - The new YAML structure to set.
 * @returns {void}
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function setYamlStructure(structure) {
    state.yamlStructure = structure;
}

/**
 * @function getYamlStructure
 * @description Retrieves the current YAML structure from the state.
 * @returns {Array|null} The current YAML structure.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function getYamlStructure() {
    return state.yamlStructure;
}

/**
 * @function setComponentTemplates
 * @description Sets the component templates in the state.
 * @param {object} templates - The component templates object.
 * @returns {void}
 * @calledBy {js/core/templates.js}
 * @calls {None}
 */
export function setComponentTemplates(templates) {
    state.componentTemplates = templates || {};
}

/**
 * @function getComponentTemplates
 * @description Retrieves the component templates from the state.
 * @returns {object} The component templates object.
 * @calledBy {js/properties/index.js|js/ui/actions.js}
 * @calls {None}
 */
export function getComponentTemplates() {
    return state.componentTemplates;
}

/**
 * @function setComponentSchemas
 * @description Sets the component schemas in the state.
 * @param {object} schemas - The component schemas object.
 * @returns {void}
 * @calledBy {js/core/templates.js}
 * @calls {None}
 */
export function setComponentSchemas(schemas) {
    state.componentSchemas = schemas || {};
}

/**
 * @function getComponentSchemas
 * @description Retrieves the component schemas from the state.
 * @returns {object} The component schemas object.
 * @calledBy {js/properties/index.js}
 * @calls {None}
 */
export function getComponentSchemas() {
    return state.componentSchemas;
}

/**
 * @function setSchemaTokens
 * @description Sets the schema tokens in the state.
 * @param {object} tokens - The schema tokens object.
 * @returns {void}
 * @calledBy {js/core/templates.js}
 * @calls {None}
 */
export function setSchemaTokens(tokens) {
    state.schemaTokens = tokens || {};
}

/**
 * @function getSchemaTokens
 * @description Retrieves the schema tokens from the state.
 * @returns {object} The schema tokens object.
 * @calledBy {js/properties/index.js}
 * @calls {None}
 */
export function getSchemaTokens() {
    return state.schemaTokens;
}

/**
 * @function markMetadataLoaded
 * @description Marks the component metadata as loaded in the state.
 * @returns {void}
 * @calledBy {js/core/app.js}
 * @calls {None}
 */
export function markMetadataLoaded() {
    state.metadataLoaded = true;
}

/**
 * @function isMetadataLoaded
 * @description Checks if the component metadata has been loaded.
 * @returns {boolean} True if metadata is loaded, false otherwise.
 * @calledBy {None}
 * @calls {None}
 */
export function isMetadataLoaded() {
    return state.metadataLoaded;
}

/**
 * @function resetComponentPathMap
 * @description Resets the map that links component IDs to their YAML paths.
 * @returns {void}
 * @calledBy {js/render/index.js}
 * @calls {None}
 */
export function resetComponentPathMap() {
    state.componentPathMap = new Map();
}

/**
 * @function registerComponentPath
 * @description Registers a component's unique ID with its path in the YAML structure.
 * @param {string} componentId - The unique ID of the component.
 * @param {Array<number|string>} path - The path to the component in the YAML structure.
 * @returns {void}
 * @calledBy {js/render/index.js}
 * @calls {None}
 */
export function registerComponentPath(componentId, path) {
    state.componentPathMap.set(componentId, Array.isArray(path) ? [...path] : path);
}

/**
 * @function getPathForComponent
 * @description Retrieves the YAML path for a given component ID.
 * @param {string} componentId - The unique ID of the component.
 * @returns {Array<number|string>|null} The YAML path, or null if not found.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function getPathForComponent(componentId) {
    return state.componentPathMap.get(componentId) || null;
}

/**
 * @function getComponentPathMap
 * @description Returns a copy of the component path map.
 * @returns {Map<string, Array>} A new Map object containing component IDs and their paths.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function getComponentPathMap() {
    return new Map(state.componentPathMap);
}

/**
 * @function queueComponentInitialization
 * @description Adds a component to the queue for post-render JavaScript initialization.
 * @param {object} entry - An object containing component initialization details (name, id, props).
 * @returns {void}
 * @calledBy {js/render/index.js}
 * @calls {None}
 */
export function queueComponentInitialization(entry) {
    state.componentsToInitialize.push(entry);
}

/**
 * @function consumeComponentInitializationQueue
 * @description Retrieves and clears the queue of components awaiting initialization.
 * @returns {Array<object>} An array of component initialization entries.
 * @calledBy {js/render/index.js}
 * @calls {None}
 */
export function consumeComponentInitializationQueue() {
    const queue = [...state.componentsToInitialize];
    state.componentsToInitialize.length = 0;
    return queue;
}

/**
 * @function setSelection
 * @description Sets the currently selected component's ID and path in the state.
 * @param {object} options - The selection options.
 * @param {string|null} [options.componentId=null] - The ID of the selected component.
 * @param {Array|null} [options.path=null] - The YAML path of the selected component.
 * @returns {void}
 * @calledBy {js/core/app.js|js/ui/actions.js}
 * @calls {None}
 */
export function setSelection({ componentId = null, path = null } = {}) {
    state.selectedComponentId = componentId;
    state.selectedComponentPath = path ? [...path] : null;
}

/**
 * @function getSelection
 * @description Retrieves the currently selected component's ID and path from the state.
 * @returns {{componentId: string|null, path: Array|null}} An object containing the selected component's ID and path.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function getSelection() {
    return {
        componentId: state.selectedComponentId,
        path: state.selectedComponentPath ? [...state.selectedComponentPath] : null,
    };
}

/**
 * @function pushHistory
 * @description Pushes the current YAML content onto the undo stack and clears the redo stack.
 * @param {string} value - The YAML content to add to the history.
 * @returns {void}
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function pushHistory(value) {
    const { history } = state;
    if (history.undoStack.length >= history.maxSize) {
        history.undoStack.shift();
    }
    history.undoStack.push(value);
    history.redoStack = [];
}

/**
 * @function canUndo
 * @description Checks if an undo operation is possible.
 * @returns {boolean} True if undo is possible, false otherwise.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function canUndo() {
    const { history } = state;
    return history.undoStack.length > 1;
}

/**
 * @function undo
 * @description Performs an undo operation, reverting to the previous YAML state.
 * @returns {string|null} The previous YAML content, or null if undo is not possible.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function undo() {
    const { history } = state;
    if (history.undoStack.length > 1) {
        const currentState = history.undoStack.pop();
        history.redoStack.push(currentState);
        return history.undoStack[history.undoStack.length - 1];
    }
    return null;
}

/**
 * @function canRedo
 * @description Checks if a redo operation is possible.
 * @returns {boolean} True if redo is possible, false otherwise.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function canRedo() {
    const { history } = state;
    return history.redoStack.length > 0;
}

/**
 * @function redo
 * @description Performs a redo operation, advancing to the next YAML state.
 * @returns {string|null} The next YAML content, or null if redo is not possible.
 * @calledBy {js/ui/actions.js}
 * @calls {None}
 */
export function redo() {
    const { history } = state;
    if (history.redoStack.length > 0) {
        const nextState = history.redoStack.pop();
        history.undoStack.push(nextState);
        return nextState;
    }
    return null;
}