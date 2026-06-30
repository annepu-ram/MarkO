/**
 * Chat Service - API Communication for LLM Chat
 *
 * Handles stateless communication with the /api/chat endpoint.
 * Each request is independent - no conversation history is sent.
 */

export class ChatService {
    constructor() {
        this.endpoint = '/api/chat';
        this.timeout = 600000; // 10 minute timeout for LLM responses
        this._controller = null;
        this._cancelled = false;
    }

    _appHeaders(extra = {}) {
        const token = document.querySelector('meta[name="ai-request-token"]')?.content || '';
        return {
            'Content-Type': 'application/json',
            'X-Requested-With': 'SwiftSitesApp',
            'X-AI-Request-Token': token,
            ...extra,
        };
    }

    /**
     * Send a message to the LLM and get a response.
     *
     * @param {string} message - User's message
     * @param {string} currentYaml - Current YAML content from editor
     * @param {Object|null} selectedComponent - Currently selected component info
     * @param {string|null} siteId - Site ID for backend to query images from DB
     * @returns {Promise<Object>} Response with response, yaml, action, and optional error
     */
    async sendMessage(message, currentYaml, selectedComponent = null, siteId = null) {
        this._cancelled = false;
        const controller = new AbortController();
        this._controller = controller;
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: this._appHeaders(),
                body: JSON.stringify({
                    message,
                    currentYaml: currentYaml || '',
                    selectedComponent,
                    siteId,
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            this._controller = null;

            const data = await response.json();

            if (!response.ok) {
                // Server returned an error response
                return {
                    response: data.message || data.response || 'An error occurred',
                    yaml: null,
                    action: 'error',
                    error: data.details || data.message,
                    errorType: data.errorType || 'api'
                };
            }

            return data;

        } catch (error) {
            clearTimeout(timeoutId);
            this._controller = null;

            if (error.name === 'AbortError') {
                if (this._cancelled) {
                    return {
                        response: 'Request cancelled.',
                        yaml: null,
                        action: 'error',
                        errorType: 'cancelled'
                    };
                }
                return {
                    response: 'Request timed out. Please try again.',
                    yaml: null,
                    action: 'error',
                    error: 'The request took too long to complete.',
                    errorType: 'timeout'
                };
            }

            return {
                response: 'Failed to connect to AI service.',
                yaml: null,
                action: 'error',
                error: error.message,
                errorType: 'network'
            };
        }
    }

    /**
     * Send a guided-flow generation request.
     *
     * @param {Object} businessContext - Full collected context from the guided wizard.
     * @param {string} currentYaml - Current YAML content (usually empty for create_page).
     * @param {string|null} siteId - Site ID for image lookup.
     * @returns {Promise<Object>} Same shape as sendMessage: {response, yaml, action}.
     */
    async sendGuidedRequest(businessContext, currentYaml = '', siteId = null) {
        this._cancelled = false;
        const controller = new AbortController();
        this._controller = controller;
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch('/api/chat/guided', {
                method: 'POST',
                headers: this._appHeaders(),
                body: JSON.stringify({
                    businessContext,
                    currentYaml: currentYaml || '',
                    siteId,
                }),
                signal: controller.signal,
            });

            clearTimeout(timeoutId);
            this._controller = null;

            const data = await response.json();

            if (!response.ok) {
                return {
                    response: data.message || data.response || 'An error occurred',
                    yaml: null,
                    action: 'error',
                    error: data.details || data.message,
                    errorType: data.errorType || 'api',
                };
            }
            return data;

        } catch (error) {
            clearTimeout(timeoutId);
            this._controller = null;

            if (error.name === 'AbortError') {
                if (this._cancelled) {
                    return { response: 'Request cancelled.', yaml: null, action: 'error', errorType: 'cancelled' };
                }
                return {
                    response: 'Request timed out. Please try again.',
                    yaml: null,
                    action: 'error',
                    error: 'The request took too long to complete.',
                    errorType: 'timeout',
                };
            }

            return {
                response: 'Failed to connect to AI service.',
                yaml: null,
                action: 'error',
                error: error.message,
                errorType: 'network',
            };
        }
    }

    /**
     * Fetch the guided-flow industry config (industries, section_questions,
     * recommendations, page_purposes, styles). Cached on the service instance.
     */
    async getIndustryConfig() {
        if (this._industryConfigPromise) return this._industryConfigPromise;
        this._industryConfigPromise = fetch('/api/chat/industry-config')
            .then(r => {
                if (!r.ok) throw new Error(`industry-config fetch failed: ${r.status}`);
                return r.json();
            })
            .catch(err => {
                this._industryConfigPromise = null;  // allow retry
                throw err;
            });
        return this._industryConfigPromise;
    }

    /**
     * Enhance a guided-flow section's content fields using LLM.
     *
     * @param {string} businessName
     * @param {string} industry
     * @param {string} description
     * @param {string} sectionType
     * @param {Object} currentContent - { field_key: value, ... }
     * @returns {Promise<Object>} { enhanced_fields: { field_key: value, ... } }
     */
    async enhanceSection(businessName, industry, description, sectionType, currentContent) {
        const resp = await fetch('/api/chat/enhance', {
            method: 'POST',
            headers: this._appHeaders(),
            body: JSON.stringify({
                business_name: businessName,
                industry: industry,
                description: description,
                section_type: sectionType,
                current_content: currentContent,
            }),
        });
        if (!resp.ok) {
            const errData = await resp.json().catch(() => ({}));
            throw new Error(errData.message || `Enhance failed: ${resp.status}`);
        }
        return resp.json();
    }

    /**
     * Cancel the active chat request.
     * Aborts the fetch and tells the backend to stop processing.
     */
    cancel() {
        this._cancelled = true;
        if (this._controller) {
            this._controller.abort();
            this._controller = null;
        }
        // Tell backend to stop processing (fire-and-forget)
        fetch('/api/chat/cancel', {
            method: 'POST',
            headers: this._appHeaders(),
        }).catch(() => {});
    }
}

// Export singleton instance
export const chatService = new ChatService();
