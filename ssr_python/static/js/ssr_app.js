import { componentInitializers } from './component_interactions.js';
import { ComponentPathMapBuilder } from './pathMapBuilder.js';

// Create a singleton instance of the path map builder
export const pathMapBuilder = new ComponentPathMapBuilder();

// Function to initialize all interactive components in the preview
export const initializeAllComponents = () => {
    const preview = document.getElementById('preview');
    if (!preview) return;

    for (const componentName in componentInitializers) {
        const initializer = componentInitializers[componentName];
        const elements = preview.querySelectorAll(`[data-component-type="${componentName}"]`);
        elements.forEach(element => {
            // Here we could pass props if we stored them in data attributes
            initializer(element, {}); 
        });
    }
};

/**
 * Parse YAML string to structure
 * @param {string} yamlContent - YAML string
 * @returns {Array|null} Parsed YAML structure or null on error
 */
function parseYaml(yamlContent) {
    if (!yamlContent || yamlContent.trim() === '') {
        return [];
    }

    try {
        // Use js-yaml if available (loaded via CDN or npm)
        if (typeof jsyaml !== 'undefined') {
            return jsyaml.load(yamlContent) || [];
        }
        
        // Fallback: try to parse as JSON if it's valid JSON
        try {
            return JSON.parse(yamlContent);
        } catch (e) {
            console.warn('YAML parser not available. Install js-yaml or load it via CDN.');
            return null;
        }
    } catch (error) {
        console.error('Failed to parse YAML:', error);
        return null;
    }
}

// Function to send YAML to the server and get HTML back
export const renderPreview = async (yamlContent, yamlStructure = null) => {
    const preview = document.getElementById('preview');
    if (!preview) return;

    // Parse YAML if structure not provided
    let structure = yamlStructure;
    if (!structure) {
        structure = parseYaml(yamlContent);
        if (structure === null) {
            // Invalid YAML, but still try to render (server will handle error)
            structure = [];
        }
    }

    try {
        const response = await fetch('/render', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml'
            },
            body: yamlContent
        });

        if (!response.ok) {
            const errorData = await response.json();
            preview.innerHTML = `<div class="error-message">
                <h3>Error Rendering Preview</h3>
                <p><strong>Error:</strong> ${errorData.error}</p>
                <pre>${errorData.details || ''}</pre>
            </div>`;
            // Clear path map on error
            pathMapBuilder.clear();
            return;
        }

        const htmlContent = await response.text();
        preview.innerHTML = htmlContent;

        // Build component path map after rendering
        if (structure && Array.isArray(structure)) {
            pathMapBuilder.buildPathMap(preview, structure);
            console.log(`ComponentPathMapBuilder: Built path map with ${pathMapBuilder.size()} components`);
        } else {
            console.warn('ComponentPathMapBuilder: Invalid YAML structure, skipping path map build');
            pathMapBuilder.clear();
        }

        // Initialize components after rendering the new HTML
        initializeAllComponents();

        // Return a promise that resolves after rendering is complete
        return Promise.resolve();

    } catch (error) {
        preview.innerHTML = `<div class="error-message">
            <h3>Connection Error</h3>
            <p>Could not connect to the rendering server.</p>
            <pre>${error.toString()}</pre>
        </div>`;
        // Clear path map on error
        pathMapBuilder.clear();
    }
};

// Export path map builder getter for use in other modules
export const getPathMapBuilder = () => pathMapBuilder;
