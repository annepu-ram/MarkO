import { getPathMapBuilder, selectComponentInIframe, clearSelectionInIframe } from './ssr_app.js';

export class SelectionManager {
    constructor() {
        this.selectedComponentId = null;
        this.selectedPath = null;
        this.onSelectionChange = null; // Callback function

        // Listen for iframe component clicks (dispatched by ssr_app.js)
        this.setupIframeClickListener();
    }

    /**
     * Set up listener for iframe component click events
     */
    setupIframeClickListener() {
        console.log('[SelectionManager] Setting up iframe click listener');
        window.addEventListener('iframe-component-clicked', (event) => {
            console.log('[SelectionManager] Received iframe-component-clicked event:', event.detail);
            const { componentId } = event.detail;
            if (componentId) {
                this.selectComponent(componentId);
            }
        });
    }

    /**
     * Check if we're in iframe mode
     * @returns {boolean} True if using iframe preview
     */
    isIframeMode() {
        return !!document.getElementById('preview-frame');
    }

    /**
     * Handle click on preview area (legacy mode - direct DOM clicks)
     * @param {MouseEvent} event - Click event
     */
    handlePreviewClick(event) {
        // In iframe mode, clicks are handled via postMessage
        if (this.isIframeMode()) {
            return;
        }

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
        console.log(`[SelectionManager] selectComponent called with: ${componentId}`);

        const pathMapBuilder = getPathMapBuilder();
        console.log(`[SelectionManager] Path map size: ${pathMapBuilder.size()}`);

        const path = pathMapBuilder.getPath(componentId);
        console.log(`[SelectionManager] Path lookup result:`, path);

        if (!path) {
            console.warn(`[SelectionManager] No path found for component ID: ${componentId}`);
            console.log(`[SelectionManager] Available IDs:`, Array.from(pathMapBuilder.pathMap.keys()));
            return;
        }

        // Clear previous selection
        this.clearHighlight();

        // Set new selection
        this.selectedComponentId = componentId;
        this.selectedPath = path;

        // Highlight selected component
        this.highlightComponent(componentId);

        // Dispatch custom event for multiple listeners (chat, etc.)
        window.dispatchEvent(new CustomEvent('swift-selection-changed', {
            detail: { componentId, path: [...path] }
        }));

        // Notify callback listener (for backwards compatibility)
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

        // Dispatch custom event for multiple listeners (chat, etc.)
        window.dispatchEvent(new CustomEvent('swift-selection-changed', {
            detail: { componentId: null, path: null }
        }));

        if (this.onSelectionChange) {
            this.onSelectionChange(null);
        }
    }

    /**
     * Highlight a component
     * @param {string} componentId - Component ID to highlight
     */
    highlightComponent(componentId) {
        if (this.isIframeMode()) {
            // Send selection to iframe via postMessage
            selectComponentInIframe(componentId);
        } else {
            // Legacy: Direct DOM manipulation
            const preview = document.getElementById('preview');
            if (!preview) return;

            const element = preview.querySelector(`[data-component-id="${componentId}"]`);
            if (element) {
                element.classList.add('selected');
                // Scroll into view if needed (smooth scroll)
                element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
            }
        }
    }

    /**
     * Clear highlight from all components
     */
    clearHighlight() {
        if (this.isIframeMode()) {
            // Send clear selection to iframe
            clearSelectionInIframe();
        } else {
            // Legacy: Direct DOM manipulation
            const preview = document.getElementById('preview');
            if (!preview) return;

            const selectedElements = preview.querySelectorAll('.selected');
            selectedElements.forEach(el => el.classList.remove('selected'));
        }
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
            // Small delay to ensure DOM/iframe is ready
            setTimeout(() => {
                this.highlightComponent(this.selectedComponentId);
            }, 100);
        }
    }
}
