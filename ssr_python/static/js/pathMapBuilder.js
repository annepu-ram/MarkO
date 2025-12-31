/**
 * Builds a map of component IDs to YAML paths from rendered HTML.
 * Parses data-component-id attributes and reconstructs paths from DOM structure.
 */

export class ComponentPathMapBuilder {
    constructor() {
        this.pathMap = new Map();
        this.yamlStructure = null;
    }

    /**
     * Build path map from rendered HTML and YAML structure
     * @param {HTMLElement} previewElement - The preview container
     * @param {Array} yamlStructure - The parsed YAML structure
     */
    buildPathMap(previewElement, yamlStructure) {
        this.yamlStructure = yamlStructure;
        this.pathMap.clear();
        
        if (!previewElement || !yamlStructure) {
            console.warn('ComponentPathMapBuilder: Missing previewElement or yamlStructure');
            return this.pathMap;
        }
        
        // Traverse YAML structure and match with DOM elements
        this.traverseYamlStructure(yamlStructure, [], previewElement);
        
        return this.pathMap;
    }

    /**
     * Recursively traverse YAML structure and match with DOM elements
     * @param {Array} structure - YAML structure array
     * @param {Array} currentPath - Current path in YAML structure
     * @param {HTMLElement} parentElement - Parent DOM element to search within
     */
    traverseYamlStructure(structure, currentPath, parentElement) {
        if (!Array.isArray(structure)) {
            return;
        }

        structure.forEach((component, index) => {
            const path = [...currentPath, index];
            
            // Find corresponding DOM element
            const componentId = this.generateComponentId(path);
            const element = parentElement.querySelector(`[data-component-id="${componentId}"]`);
            
            if (element) {
                this.pathMap.set(componentId, path);
            } else {
                console.warn(`ComponentPathMapBuilder: No DOM element found for component ID: ${componentId} at path:`, path);
            }

            // Traverse nested components
            if (component.components && Array.isArray(component.components)) {
                const childPath = [...path, 'components'];
                // Use the found element as parent, or fallback to parentElement
                const childParentElement = element || parentElement;
                this.traverseYamlStructure(component.components, childPath, childParentElement);
            }

            // Traverse columns (for columnsgrid)
            if (component.columns && Array.isArray(component.columns)) {
                component.columns.forEach((column, colIndex) => {
                    const colPath = [...path, 'columns', colIndex];
                    if (column.components && Array.isArray(column.components)) {
                        const colComponentsPath = [...colPath, 'components'];
                        const colParentElement = element || parentElement;
                        this.traverseYamlStructure(column.components, colComponentsPath, colParentElement);
                    }
                });
            }

            // Traverse tabs
            if (component.tabs && Array.isArray(component.tabs)) {
                component.tabs.forEach((tab, tabIndex) => {
                    const tabPath = [...path, 'tabs', tabIndex];
                    if (tab.components && Array.isArray(tab.components)) {
                        const tabComponentsPath = [...tabPath, 'components'];
                        const tabParentElement = element || parentElement;
                        this.traverseYamlStructure(tab.components, tabComponentsPath, tabParentElement);
                    }
                });
            }

            // Traverse carousel slides
            if (component.slides && Array.isArray(component.slides)) {
                component.slides.forEach((slide, slideIndex) => {
                    const slidePath = [...path, 'slides', slideIndex];
                    if (slide.components && Array.isArray(slide.components)) {
                        const slideComponentsPath = [...slidePath, 'components'];
                        const slideParentElement = element || parentElement;
                        this.traverseYamlStructure(slide.components, slideComponentsPath, slideParentElement);
                    }
                });
            }
        });
    }

    /**
     * Generate component ID from path (must match server-side generation)
     * Path format: [0, 'components', 1, 'components', 2]
     * Returns: 'comp_0_components_1_components_2'
     * @param {Array} path - YAML path array
     * @returns {string} Component ID
     */
    generateComponentId(path) {
        if (!path || path.length === 0) {
            return 'comp_root';
        }
        
        // Convert path to string representation matching server-side format
        return 'comp_' + path.join('_');
    }

    /**
     * Get path for a component ID
     * @param {string} componentId - Component ID
     * @returns {Array|null} YAML path or null if not found
     */
    getPath(componentId) {
        return this.pathMap.get(componentId) || null;
    }

    /**
     * Get all paths
     * @returns {Map} Copy of the path map
     */
    getAllPaths() {
        return new Map(this.pathMap);
    }

    /**
     * Clear the path map
     */
    clear() {
        this.pathMap.clear();
    }

    /**
     * Get the size of the path map
     * @returns {number} Number of mapped components
     */
    size() {
        return this.pathMap.size;
    }
}

