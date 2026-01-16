import { componentInitializers } from './component_interactions.js';
import { ComponentPathMapBuilder } from './pathMapBuilder.js';

// Create a singleton instance of the path map builder
export const pathMapBuilder = new ComponentPathMapBuilder();

// AbortController for cancelling pending render requests
let currentAbortController = null;

// Security: Trusted origin for postMessage
const TRUSTED_ORIGIN = window.location.origin;

// Track if iframe is ready
let iframeReady = false;
let pendingContent = null;

/**
 * Initialize message listener for iframe communication
 */
function initializeIframeListener() {
    window.addEventListener('message', (event) => {
        // SECURITY: Validate origin
        if (event.origin !== TRUSTED_ORIGIN) {
            console.warn('[SSR App] Blocked message from untrusted origin:', event.origin);
            return;
        }

        // Validate message structure
        if (!event.data || typeof event.data.type !== 'string') {
            return;
        }

        switch (event.data.type) {
            case 'IFRAME_READY':
                console.log('[SSR App] Preview iframe is ready');
                iframeReady = true;

                // Send acknowledgment back to iframe to stop retry loop
                const iframe = document.getElementById('preview-frame');
                if (iframe && iframe.contentWindow) {
                    // SECURITY: Always specify exact origin
                    iframe.contentWindow.postMessage({
                        type: 'IFRAME_READY_ACK'
                    }, TRUSTED_ORIGIN);
                }

                // Send any pending content
                if (pendingContent) {
                    sendContentToIframe(pendingContent);
                    pendingContent = null;
                }
                break;

            case 'COMPONENTS_READY':
                // Components have been rendered in iframe
                console.log('[SSR App] Iframe reported', event.data.componentIds?.length || 0, 'components');
                break;

            case 'COMPONENT_CLICKED':
                // Forward to selection manager (handled in main.js/selectionManager.js)
                // This is dispatched as a custom event that selectionManager listens for
                console.log('[SSR App] COMPONENT_CLICKED received:', event.data.componentId);
                window.dispatchEvent(new CustomEvent('iframe-component-clicked', {
                    detail: { componentId: event.data.componentId }
                }));
                break;
        }
    });
}

// Initialize listener immediately
initializeIframeListener();

/**
 * Send content to iframe via postMessage
 * @param {string} html - HTML content to send
 */
function sendContentToIframe(html) {
    const iframe = document.getElementById('preview-frame');
    if (!iframe || !iframe.contentWindow) {
        console.warn('[SSR App] Iframe not available');
        return;
    }

    // SECURITY: Always specify exact origin
    iframe.contentWindow.postMessage({
        type: 'UPDATE_CONTENT',
        html: html
    }, TRUSTED_ORIGIN);
}

/**
 * Send selection to iframe
 * @param {string} componentId - Component ID to select
 */
export function selectComponentInIframe(componentId) {
    const iframe = document.getElementById('preview-frame');
    if (!iframe || !iframe.contentWindow) return;

    // SECURITY: Always specify exact origin
    iframe.contentWindow.postMessage({
        type: 'SET_SELECTION',
        componentId: componentId
    }, TRUSTED_ORIGIN);
}

/**
 * Clear selection in iframe
 */
export function clearSelectionInIframe() {
    const iframe = document.getElementById('preview-frame');
    if (!iframe || !iframe.contentWindow) return;

    // SECURITY: Always specify exact origin
    iframe.contentWindow.postMessage({
        type: 'CLEAR_SELECTION'
    }, TRUSTED_ORIGIN);
}

// Function to initialize all interactive components in the preview
// Note: With iframe, components are initialized inside the iframe by preview_bridge.js
export const initializeAllComponents = () => {
    // Legacy: For non-iframe mode (kept for backwards compatibility)
    const preview = document.getElementById('preview');
    if (!preview) return;

    for (const componentName in componentInitializers) {
        const initializer = componentInitializers[componentName];
        const elements = preview.querySelectorAll(`[data-component-type="${componentName}"]`);
        elements.forEach(element => {
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
        // Check both global and window.jsyaml (module scripts may not see bare globals)
        const yaml = typeof jsyaml !== 'undefined' ? jsyaml : window.jsyaml;
        if (yaml) {
            return yaml.load(yamlContent) || [];
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

/**
 * Show error in iframe
 * @param {string} title - Error title
 * @param {string} message - Error message
 * @param {string} details - Error details
 */
function showErrorInIframe(title, message, details = '') {
    const errorHtml = `
        <div class="error-message">
            <h3>${escapeHtml(title)}</h3>
            <p>${escapeHtml(message)}</p>
            ${details ? `<pre>${escapeHtml(details)}</pre>` : ''}
        </div>
    `;

    if (iframeReady) {
        sendContentToIframe(errorHtml);
    } else {
        pendingContent = errorHtml;
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Function to send YAML to the server and get HTML back
export const renderPreview = async (yamlContent, yamlStructure = null) => {
    const iframe = document.getElementById('preview-frame');

    // Check if we're using iframe mode or legacy div mode
    const isIframeMode = !!iframe;
    const preview = isIframeMode ? null : document.getElementById('preview');

    if (!isIframeMode && !preview) return;

    // Cancel any pending request
    if (currentAbortController) {
        currentAbortController.abort();
    }
    currentAbortController = new AbortController();

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
        // Create timeout promise (10 second timeout)
        const timeoutMs = 10000;
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Request timeout')), timeoutMs);
        });

        // Fetch with abort signal
        const fetchPromise = fetch('/render', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml'
            },
            body: yamlContent,
            signal: currentAbortController.signal
        });

        // Race between fetch and timeout
        const response = await Promise.race([fetchPromise, timeoutPromise]);

        if (!response.ok) {
            const errorData = await response.json();

            if (isIframeMode) {
                showErrorInIframe(
                    'Error Rendering Preview',
                    `Error: ${errorData.error}`,
                    errorData.details || ''
                );
            } else {
                preview.innerHTML = `<div class="error-message">
                    <h3>Error Rendering Preview</h3>
                    <p><strong>Error:</strong> ${errorData.error}</p>
                    <pre>${errorData.details || ''}</pre>
                </div>`;
            }

            pathMapBuilder.clear();
            return;
        }

        const htmlContent = await response.text();

        if (isIframeMode) {
            // Send to iframe via postMessage
            if (iframeReady) {
                sendContentToIframe(htmlContent);
            } else {
                // Queue content until iframe is ready
                pendingContent = htmlContent;
            }
        } else {
            // Legacy: Direct DOM update
            preview.innerHTML = htmlContent;
            initializeAllComponents();
        }

        // Build component path map from YAML structure
        if (structure && Array.isArray(structure)) {
            pathMapBuilder.buildPathMapFromStructure(structure);
            console.log(`[SSR App] Built path map with ${pathMapBuilder.size()} components`);
            console.log('[SSR App] Path map keys:', Array.from(pathMapBuilder.pathMap.keys()));
        } else {
            console.warn('[SSR App] Invalid YAML structure, skipping path map build');
            pathMapBuilder.clear();
        }

        // Return a promise that resolves after rendering is complete
        return Promise.resolve();

    } catch (error) {
        // Ignore abort errors (expected when cancelling previous request)
        if (error.name === 'AbortError') {
            console.log('[SSR App] Render request cancelled (superseded by newer request)');
            return;
        }

        // Show user-friendly error message
        const errorMessage = error.message === 'Request timeout'
            ? 'The server took too long to respond. Please try again.'
            : 'Could not connect to the rendering server.';

        if (isIframeMode) {
            showErrorInIframe('Connection Error', errorMessage, error.toString());
        } else {
            preview.innerHTML = `<div class="error-message">
                <h3>Connection Error</h3>
                <p>${errorMessage}</p>
                <pre>${error.toString()}</pre>
            </div>`;
        }

        pathMapBuilder.clear();
    }
};

// Export path map builder getter for use in other modules
export const getPathMapBuilder = () => pathMapBuilder;

// Export trusted origin for use in other modules
export const getTrustedOrigin = () => TRUSTED_ORIGIN;
