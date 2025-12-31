import { getPathMapBuilder } from './ssr_app.js';

export class SelectionManager {
    constructor() {
        this.selectedComponentId = null;
        this.selectedPath = null;
        this.onSelectionChange = null; // Callback function
    }

    /**
     * Handle click on preview area
     * @param {MouseEvent} event - Click event
     */
    handlePreviewClick(event) {
        // Find the closest component element
        const componentElement = event.target.closest('[data-component-id]');
        
        if (!componentElement) {
            this.clearSelection();
            return;
        }

        // Prevent selection if clicking on chrome delete button (if it exists)
        if (event.target.classList.contains('chrome-delete')) {
            return;
        }

        // Prevent selection if clicking on form inputs, buttons, links, etc.
        // Allow selection of the component container, but not interactive elements
        const interactiveElements = ['input', 'button', 'a', 'select', 'textarea'];
        if (interactiveElements.includes(event.target.tagName.toLowerCase())) {
            // Find parent component instead
            const parentComponent = event.target.closest('[data-component-id]');
            if (parentComponent && parentComponent !== event.target) {
                const componentId = parentComponent.getAttribute('data-component-id');
                this.selectComponent(componentId);
                return;
            }
        }

        const componentId = componentElement.getAttribute('data-component-id');
        this.selectComponent(componentId);
    }

    /**
     * Select a component by ID
     * @param {string} componentId - Component ID
     */
    selectComponent(componentId) {
        const pathMapBuilder = getPathMapBuilder();
        const path = pathMapBuilder.getPath(componentId);

        if (!path) {
            console.warn(`SelectionManager: No path found for component ID: ${componentId}`);
            return;
        }

        // Clear previous selection
        this.clearHighlight();

        // Set new selection
        this.selectedComponentId = componentId;
        this.selectedPath = path;

        // Highlight selected component
        this.highlightComponent(componentId);

        // Notify listeners
        if (this.onSelectionChange) {
            this.onSelectionChange({
                componentId,
                path: [...path] // Return a copy
            });
        }
    }

    /**
     * Clear selection
     */
    clearSelection() {
        this.clearHighlight();
        this.selectedComponentId = null;
        this.selectedPath = null;

        if (this.onSelectionChange) {
            this.onSelectionChange(null);
        }
    }

    /**
     * Highlight a component
     * @param {string} componentId - Component ID to highlight
     */
    highlightComponent(componentId) {
        const preview = document.getElementById('preview');
        if (!preview) return;

        const element = preview.querySelector(`[data-component-id="${componentId}"]`);
        if (element) {
            element.classList.add('selected');
            // Scroll into view if needed (smooth scroll)
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        }
    }

    /**
     * Clear highlight from all components
     */
    clearHighlight() {
        const preview = document.getElementById('preview');
        if (!preview) return;

        const selectedElements = preview.querySelectorAll('.selected');
        selectedElements.forEach(el => el.classList.remove('selected'));
    }

    /**
     * Get current selection
     * @returns {{componentId: string|null, path: Array|null}} Current selection
     */
    getSelection() {
        return {
            componentId: this.selectedComponentId,
            path: this.selectedPath ? [...this.selectedPath] : null
        };
    }

    /**
     * Restore selection after re-render
     * Call this after the preview is re-rendered to restore the selected component
     */
    restoreSelection() {
        if (this.selectedComponentId) {
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                this.highlightComponent(this.selectedComponentId);
            }, 50);
        }
    }
}

