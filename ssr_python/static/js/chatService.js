/**
 * Chat Service - API Communication for LLM Chat
 *
 * Handles stateless communication with the /api/chat endpoint.
 * Each request is independent - no conversation history is sent.
 */

export class ChatService {
    constructor() {
        this.endpoint = '/api/chat';
        this.timeout = 60000; // 60 second timeout for LLM responses
    }

    /**
     * Send a message to the LLM and get a response.
     *
     * @param {string} message - User's message
     * @param {string} currentYaml - Current YAML content from editor
     * @param {Object|null} selectedComponent - Currently selected component info
     *   - id: Component DOM ID
     *   - path: YAML path array
     *   - name: Component type name
     * @returns {Promise<Object>} Response with response, yaml, action, and optional error
     */
    async sendMessage(message, currentYaml, selectedComponent = null) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    currentYaml: currentYaml || '',
                    selectedComponent
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                // Server returned an error response
                return {
                    response: data.message || 'An error occurred',
                    yaml: null,
                    action: 'error',
                    error: data.details || data.message,
                    errorType: data.errorType || 'api'
                };
            }

            return data;

        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
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
}

// Export singleton instance
export const chatService = new ChatService();
