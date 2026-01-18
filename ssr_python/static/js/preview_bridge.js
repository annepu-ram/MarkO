/**
 * Preview Bridge Script
 *
 * This script runs inside the preview iframe and handles:
 * - Receiving content updates from parent via postMessage
 * - Relaying click events to parent for component selection
 * - Managing selection highlighting
 *
 * Component initialization (carousel, accordion, tabs, titlebar) is handled by
 * swift-sites-runtime.js which is included in the preview frame.
 *
 * SECURITY: All postMessage communication validates origin to prevent XSS attacks.
 */

(function() {
    'use strict';

    // Security: Get trusted origin (same as parent since we're same-origin)
    const TRUSTED_ORIGIN = window.location.origin;

    // Allowed message types (whitelist)
    const ALLOWED_MESSAGE_TYPES = {
        UPDATE_CONTENT: 'UPDATE_CONTENT',
        SET_SELECTION: 'SET_SELECTION',
        CLEAR_SELECTION: 'CLEAR_SELECTION'
    };

    // Current selection state
    let currentSelection = null;

    /**
     * Validate component ID format to prevent injection
     * Format: comp_0, comp_0_components_1, comp_0_columns_0_components_2
     */
    function isValidComponentId(id) {
        return typeof id === 'string' && /^comp_[\d_a-z]+$/.test(id);
    }

    /**
     * Handle incoming messages from parent
     */
    function handleMessage(event) {
        // SECURITY: Validate origin first
        if (event.origin !== TRUSTED_ORIGIN) {
            console.warn('[Preview Bridge] Blocked message from untrusted origin:', event.origin);
            return;
        }

        // Validate message structure
        if (!event.data || typeof event.data.type !== 'string') {
            console.warn('[Preview Bridge] Invalid message format');
            return;
        }

        // Process only known message types
        switch (event.data.type) {
            case ALLOWED_MESSAGE_TYPES.UPDATE_CONTENT:
                handleUpdateContent(event.data);
                break;
            case ALLOWED_MESSAGE_TYPES.SET_SELECTION:
                handleSetSelection(event.data);
                break;
            case ALLOWED_MESSAGE_TYPES.CLEAR_SELECTION:
                handleClearSelection();
                break;
            default:
                console.warn('[Preview Bridge] Unknown message type:', event.data.type);
        }
    }

    /**
     * Handle content update from parent
     */
    function handleUpdateContent(data) {
        const container = document.getElementById('preview-content');
        if (!container) {
            console.error('[Preview Bridge] Preview content container not found');
            return;
        }

        // Validate html is a string
        if (typeof data.html !== 'string') {
            console.warn('[Preview Bridge] Invalid HTML content');
            return;
        }

        // Clean up existing titlebar clones before updating
        if (typeof SwiftSites !== 'undefined') {
            SwiftSites.cleanupTitlebarClones();
        }

        // Update content (HTML comes from trusted Flask server)
        container.innerHTML = data.html;

        // Clear any previous selection
        currentSelection = null;

        // Notify parent of available components
        notifyParentOfComponents();

        // Initialize interactive components via runtime
        if (typeof SwiftSites !== 'undefined') {
            SwiftSites.reset();
            SwiftSites.init();
        }
    }

    /**
     * Handle selection request from parent
     */
    function handleSetSelection(data) {
        if (!data.componentId) return;

        // Validate component ID format
        if (!isValidComponentId(data.componentId)) {
            console.warn('[Preview Bridge] Invalid component ID format:', data.componentId);
            return;
        }

        highlightComponent(data.componentId);
    }

    /**
     * Handle clear selection request from parent
     */
    function handleClearSelection() {
        clearHighlight();
    }

    /**
     * Highlight a component by adding 'selected' class
     */
    function highlightComponent(componentId) {
        clearHighlight();

        const element = document.querySelector(`[data-component-id="${componentId}"]`);
        if (element) {
            element.classList.add('selected');
            currentSelection = element;

            // Scroll into view smoothly
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /**
     * Clear current selection highlight
     */
    function clearHighlight() {
        if (currentSelection) {
            currentSelection.classList.remove('selected');
            currentSelection = null;
        }

        // Also clear any other selected elements (in case of stale state)
        document.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }

    /**
     * Notify parent of all available component IDs
     */
    function notifyParentOfComponents() {
        const components = document.querySelectorAll('[data-component-id]');
        const componentIds = Array.from(components).map(el => el.dataset.componentId);

        console.log('[Preview Bridge] Components in DOM:', componentIds);

        // SECURITY: Always specify exact origin
        window.parent.postMessage({
            type: 'COMPONENTS_READY',
            componentIds: componentIds
        }, TRUSTED_ORIGIN);
    }

    /**
     * Handle click events and relay to parent
     */
    function handleClick(event) {
        console.log('[Preview Bridge] Click event on:', event.target);
        const target = event.target.closest('[data-component-id]');
        console.log('[Preview Bridge] Closest component:', target);

        if (target) {
            const componentId = target.dataset.componentId;
            console.log('[Preview Bridge] Component ID:', componentId);

            // Validate component ID before sending
            if (isValidComponentId(componentId)) {
                console.log('[Preview Bridge] Sending COMPONENT_CLICKED to parent');
                // SECURITY: Always specify exact origin
                window.parent.postMessage({
                    type: 'COMPONENT_CLICKED',
                    componentId: componentId
                }, TRUSTED_ORIGIN);
            } else {
                console.warn('[Preview Bridge] Invalid component ID format:', componentId);
            }
        } else {
            console.log('[Preview Bridge] No component found at click target');
        }
    }

    // Handshake state - track if parent acknowledged our IFRAME_READY
    let readyAcknowledged = false;

    /**
     * Handle acknowledgment message from parent
     * This is separate from the main message handler to ensure it's always processed
     */
    function handleAcknowledgment(event) {
        // SECURITY: Validate origin
        if (event.origin !== TRUSTED_ORIGIN) return;

        if (event.data && event.data.type === 'IFRAME_READY_ACK') {
            readyAcknowledged = true;
            console.log('[Preview Bridge] Ready acknowledged by parent');
        }
    }

    /**
     * Send IFRAME_READY with retry until acknowledged
     * This handles the race condition where the iframe loads before the parent's
     * message listener is set up (module scripts are deferred)
     */
    function sendReadySignal() {
        if (readyAcknowledged) return;

        // SECURITY: Always specify exact origin
        window.parent.postMessage({
            type: 'IFRAME_READY'
        }, TRUSTED_ORIGIN);

        console.log('[Preview Bridge] Sent IFRAME_READY, waiting for acknowledgment...');

        // Retry after 100ms if not acknowledged (max ~30 retries = 3 seconds)
        setTimeout(() => {
            if (!readyAcknowledged) {
                sendReadySignal();
            }
        }, 100);
    }

    // Set up event listeners
    window.addEventListener('message', handleMessage);
    window.addEventListener('message', handleAcknowledgment);
    document.addEventListener('click', handleClick);

    // Start handshake with retry pattern
    sendReadySignal();

    console.log('[Preview Bridge] Initialized with trusted origin:', TRUSTED_ORIGIN);
})();
