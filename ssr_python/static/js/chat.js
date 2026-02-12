/**
 * Chat UI Component for Swift Sites LLM Chat Feature
 *
 * Provides a floating chat interface for AI-powered website creation and modification.
 * - Enter key creates new line (default behavior)
 * - Send button click triggers message send
 * - Loading spinner persists until preview fully renders
 */

import { chatService } from './chatService.js';

class ChatUI {
    constructor(options = {}) {
        this.onYamlApply = options.onYamlApply || (() => {});
        this.getSelectionContext = options.getSelectionContext || (() => null);
        this.getCurrentYaml = options.getCurrentYaml || (() => '');

        this.container = null;
        this.chatWindow = null;
        this.messagesArea = null;
        this.inputArea = null;
        this.sendBtn = null;
        this.bubbleBtn = null;
        this.selectionBadge = null;

        this.isOpen = false;
        this.isLoading = false;
        this.pendingYaml = null;
        this.pendingAction = null;

        this.render();
        this.attachEventListeners();
    }

    render() {
        // Create container
        this.container = document.createElement('div');
        this.container.id = 'chat-container';

        // Chat bubble button
        this.bubbleBtn = document.createElement('button');
        this.bubbleBtn.className = 'chat-bubble-btn';
        this.bubbleBtn.setAttribute('aria-label', 'Open AI Chat');
        this.bubbleBtn.innerHTML = `
            <svg aria-hidden="true"><use href="#icon-sparkles"></use></svg>
        `;
        console.log('[Chat] Bubble button created');

        // Chat window
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'chat-window hidden';
        this.chatWindow.innerHTML = `
            <div class="chat-header">
                <div class="chat-header-left">
                    <span class="chat-title">AI Assistant</span>
                    <div class="chat-selection-badge hidden">
                        Editing: <span class="component-name"></span>
                    </div>
                </div>
                <button class="chat-close-btn" aria-label="Close chat">&times;</button>
            </div>
            <div class="chat-messages">
                <div class="chat-welcome">
                    <h3>Welcome to AI Assistant</h3>
                    <p>Ask me to create a website or modify components.<br>
                    Select a component in the preview for targeted edits.</p>
                </div>
            </div>
            <div class="chat-input-area">
                <textarea class="chat-input" placeholder="Describe your website or changes..." rows="1"></textarea>
                <button class="chat-send-btn">Send</button>
            </div>
        `;

        this.container.appendChild(this.bubbleBtn);
        this.container.appendChild(this.chatWindow);

        // Cache references
        this.messagesArea = this.chatWindow.querySelector('.chat-messages');
        this.inputArea = this.chatWindow.querySelector('.chat-input');
        this.sendBtn = this.chatWindow.querySelector('.chat-send-btn');
        this.selectionBadge = this.chatWindow.querySelector('.chat-selection-badge');
    }

    attachEventListeners() {
        // Bubble button - toggle chat
        this.bubbleBtn.addEventListener('click', () => this.toggle());

        // Close button
        this.chatWindow.querySelector('.chat-close-btn').addEventListener('click', () => this.close());

        // Send button - ONLY way to send messages (no Enter key)
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Auto-resize textarea
        this.inputArea.addEventListener('input', () => {
            this.inputArea.style.height = 'auto';
            this.inputArea.style.height = Math.min(this.inputArea.scrollHeight, 120) + 'px';
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Listen for selection changes to update the selection indicator
        window.addEventListener('swift-selection-changed', () => {
            this.updateSelectionIndicator();
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.chatWindow.classList.remove('hidden');
        this.bubbleBtn.classList.add('hidden');
        this.updateSelectionIndicator();
        this.inputArea.focus();
    }

    close() {
        this.isOpen = false;
        this.chatWindow.classList.add('hidden');
        this.bubbleBtn.classList.remove('hidden');
    }

    updateSelectionIndicator() {
        const selection = this.getSelectionContext();
        if (selection && selection.name) {
            this.selectionBadge.classList.remove('hidden');
            this.selectionBadge.querySelector('.component-name').textContent = selection.name;
        } else {
            this.selectionBadge.classList.add('hidden');
        }
    }

    addMessage(role, content, options = {}) {
        // Remove welcome message if present
        const welcome = this.messagesArea.querySelector('.chat-welcome');
        if (welcome) {
            welcome.remove();
        }

        const messageEl = document.createElement('div');
        messageEl.className = `message message-${role}`;

        if (options.isError) {
            messageEl.classList.add('message-error');
        }

        // Parse content for display
        let displayContent = this.formatMessageContent(content);
        messageEl.innerHTML = displayContent;

        this.messagesArea.appendChild(messageEl);
        this.scrollToBottom();

        return messageEl;
    }

    formatMessageContent(content) {
        // Escape HTML
        let formatted = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Convert markdown-style bold
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Convert newlines to breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    displayYamlResponse(response, yaml, action, warning = null) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';

        // Clean response text (remove ACTION comment for display)
        let cleanResponse = response.replace(/<!--\s*ACTION:\s*\w+\s*-->/gi, '').trim();

        // Remove YAML code blocks from displayed text (we show them separately)
        cleanResponse = cleanResponse.replace(/```yaml[\s\S]*?```/gi, '').trim();

        let html = '';

        if (cleanResponse) {
            html += `<div class="response-text">${this.formatMessageContent(cleanResponse)}</div>`;
        }

        if (warning) {
            html += `<div class="yaml-warning">⚠️ ${this.escapeHtml(warning)}</div>`;
        }

        if (yaml) {
            html += `
                <div class="yaml-block">
                    <div class="yaml-block-header">
                        <span>YAML (${action})</span>
                    </div>
                    <pre><code>${this.escapeHtml(yaml)}</code></pre>
                </div>
                <button class="apply-btn" data-action="${action}">Apply Changes</button>
            `;
        }

        messageEl.innerHTML = html;

        // Store pending YAML for apply
        if (yaml) {
            this.pendingYaml = yaml;
            this.pendingAction = action;

            const applyBtn = messageEl.querySelector('.apply-btn');
            applyBtn.addEventListener('click', () => this.applyYamlChanges());
        }

        this.messagesArea.appendChild(messageEl);
        this.scrollToBottom();
    }

    escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    showLoading() {
        this.isLoading = true;
        this.setInputEnabled(false);

        const loadingEl = document.createElement('div');
        loadingEl.className = 'chat-loading';
        loadingEl.id = 'chat-loading-indicator';
        loadingEl.innerHTML = `
            <div class="spinner"></div>
            <span class="loading-text">Generating...</span>
        `;

        this.messagesArea.appendChild(loadingEl);
        this.scrollToBottom();
    }

    hideLoading() {
        this.isLoading = false;
        this.setInputEnabled(true);

        const loadingEl = document.getElementById('chat-loading-indicator');
        if (loadingEl) {
            loadingEl.remove();
        }
    }

    updateLoadingText(text) {
        const loadingEl = document.getElementById('chat-loading-indicator');
        if (loadingEl) {
            const textEl = loadingEl.querySelector('.loading-text');
            if (textEl) {
                textEl.textContent = text;
            }
        }
    }

    setInputEnabled(enabled) {
        this.inputArea.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
    }

    scrollToBottom() {
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }

    async sendMessage() {
        const message = this.inputArea.value.trim();
        if (!message || this.isLoading) return;

        // Clear input
        this.inputArea.value = '';
        this.inputArea.style.height = 'auto';

        // Add user message
        this.addMessage('user', message);

        // Show loading
        this.showLoading();

        // Get context
        const currentYaml = this.getCurrentYaml();
        const selectedComponent = this.getSelectionContext();

        try {
            // Send to API
            const result = await chatService.sendMessage(message, currentYaml, selectedComponent);

            // Hide loading
            this.hideLoading();

            if (result.action === 'error') {
                this.addMessage('ai', result.response, { isError: true });
                if (result.error) {
                    console.error('[Chat] Error:', result.error);
                }
            } else if (result.yaml) {
                this.displayYamlResponse(result.response, result.yaml, result.action, result.warning);
            } else {
                this.addMessage('ai', result.response);
            }

        } catch (error) {
            this.hideLoading();
            this.addMessage('ai', `Error: ${error.message}`, { isError: true });
            console.error('[Chat] Exception:', error);
        }
    }

    async applyYamlChanges() {
        if (!this.pendingYaml || this.isLoading) return;

        const yaml = this.pendingYaml;
        const action = this.pendingAction;

        // Show loading for apply
        this.showLoading();
        this.updateLoadingText('Applying changes...');

        // Disable apply button
        const applyBtns = this.messagesArea.querySelectorAll('.apply-btn');
        applyBtns.forEach(btn => btn.disabled = true);

        try {
            // Call the apply callback
            await this.onYamlApply(yaml, action);

            // Wait a bit for preview to render
            this.updateLoadingText('Rendering preview...');

            // Give time for the preview to update
            await new Promise(resolve => setTimeout(resolve, 500));

            this.hideLoading();

            // Add success message
            this.addMessage('ai', `Changes applied successfully! (${action})`);

            // Clear pending
            this.pendingYaml = null;
            this.pendingAction = null;

        } catch (error) {
            this.hideLoading();
            this.addMessage('ai', `Failed to apply: ${error.message}\n\nYou can try clicking "Apply Changes" again, or ask me to fix the issue.`, { isError: true });
            console.error('[Chat] Apply error:', error);

            // Re-enable apply buttons - pendingYaml is preserved so user can retry
            applyBtns.forEach(btn => btn.disabled = false);
        }
    }

    // Public method to append to DOM
    appendTo(parent) {
        console.log('[Chat] Appending chat container to:', parent);
        parent.appendChild(this.container);
        console.log('[Chat] Chat container appended successfully');
    }
}

// Factory function for initialization
export function initChat(options = {}) {
    console.log('[Chat] initChat called');
    try {
        const chatUI = new ChatUI(options);
        chatUI.appendTo(document.body);
        console.log('[Chat] Chat UI fully initialized');
        return chatUI;
    } catch (error) {
        console.error('[Chat] Failed to initialize chat:', error);
        throw error;
    }
}

export { ChatUI };
