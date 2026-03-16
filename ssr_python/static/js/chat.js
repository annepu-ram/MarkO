/**
 * Chat UI Component for Swift Sites LLM Chat Feature
 *
 * References static HTML elements in #chatPanel (right-side panel).
 * Panel visibility is controlled by the right-panel toggle system.
 * - Send button click triggers message send
 * - Loading spinner persists until preview fully renders
 */

import { chatService } from './chatService.js';
import { updateSiteSettings, getCurrentSiteId } from './siteManager.js';

class ChatUI {
    constructor(options = {}) {
        this.onYamlApply = options.onYamlApply || (() => {});
        this.getSelectionContext = options.getSelectionContext || (() => null);
        this.getCurrentYaml = options.getCurrentYaml || (() => '');

        this.messagesArea = null;
        this.inputArea = null;
        this.sendBtn = null;
        this.selectionBadge = null;
        this.componentName = null;

        this.isLoading = false;
        this.pendingYaml = null;
        this.pendingAction = null;

        this.bindDom();
        this.attachEventListeners();
    }

    /** Bind to existing DOM elements in #chatPanel */
    bindDom() {
        this.messagesArea = document.getElementById('chatMessages');
        this.inputArea = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('chatSendBtn');
        this.selectionBadge = document.getElementById('chatSelectionBadge');
        this.componentName = document.getElementById('chatComponentName');

        if (!this.messagesArea || !this.inputArea || !this.sendBtn) {
            console.error('[Chat] Required DOM elements not found');
        }
    }

    attachEventListeners() {
        // Send button
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Auto-resize textarea
        if (this.inputArea) {
            this.inputArea.addEventListener('input', () => {
                this.inputArea.style.height = 'auto';
                this.inputArea.style.height = Math.min(this.inputArea.scrollHeight, 100) + 'px';
            });
        }

        // Listen for selection changes to update the selection indicator
        window.addEventListener('swift-selection-changed', () => {
            this.updateSelectionIndicator();
        });
    }

    updateSelectionIndicator() {
        const selection = this.getSelectionContext();
        if (selection && selection.name && this.selectionBadge && this.componentName) {
            this.selectionBadge.classList.remove('hidden');
            this.componentName.textContent = selection.name;
        } else if (this.selectionBadge) {
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

        let displayContent = this.formatMessageContent(content);
        messageEl.innerHTML = displayContent;

        this.messagesArea.appendChild(messageEl);
        this.scrollToBottom();

        return messageEl;
    }

    formatMessageContent(content) {
        let formatted = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    displayYamlResponse(response, yaml, action, warning = null) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';

        let cleanResponse = response.replace(/<!--\s*ACTION:\s*\w+\s*-->/gi, '').trim();
        cleanResponse = cleanResponse.replace(/```yaml[\s\S]*?```/gi, '').trim();

        let html = '';

        if (cleanResponse) {
            html += `<div class="response-text">${this.formatMessageContent(cleanResponse)}</div>`;
        }

        if (warning) {
            html += `<div class="yaml-warning">${this.escapeHtml(warning)}</div>`;
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

        if (yaml) {
            this.pendingYaml = yaml;
            this.pendingAction = action;

            const applyBtn = messageEl.querySelector('.apply-btn');
            applyBtn.addEventListener('click', () => this.applyYamlChanges());
        }

        this.messagesArea.appendChild(messageEl);
        this.scrollToBottom();
    }

    displayActionResponse(response, action) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';

        let cleanResponse = response.replace(/<!--\s*ACTION:\s*[\w-]+\s*-->/gi, '').trim();
        let html = '';
        if (cleanResponse) {
            html += `<div class="response-text">${this.formatMessageContent(cleanResponse)}</div>`;
        }
        html += `<button class="apply-btn" data-action="${action}">Apply Changes</button>`;
        messageEl.innerHTML = html;

        this.pendingYaml = null;
        this.pendingAction = action;

        const applyBtn = messageEl.querySelector('.apply-btn');
        applyBtn.addEventListener('click', () => this.applyYamlChanges());

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
        if (this.inputArea) this.inputArea.disabled = !enabled;
        if (this.sendBtn) this.sendBtn.disabled = !enabled;
    }

    scrollToBottom() {
        if (this.messagesArea) {
            this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
        }
    }

    async sendMessage() {
        const message = this.inputArea.value.trim();
        if (!message || this.isLoading) return;

        this.inputArea.value = '';
        this.inputArea.style.height = 'auto';

        this.addMessage('user', message);
        this.showLoading();

        // Poll backend for progress status updates
        const statusInterval = setInterval(async () => {
            try {
                const res = await fetch('/api/chat/status');
                const data = await res.json();
                if (data.active && data.message) {
                    this.updateLoadingText(data.message);
                }
            } catch (_) { /* ignore polling errors */ }
        }, 2000);

        const currentYaml = this.getCurrentYaml();
        const selectedComponent = this.getSelectionContext();
        const siteId = getCurrentSiteId();

        try {
            const result = await chatService.sendMessage(message, currentYaml, selectedComponent, siteId);
            clearInterval(statusInterval);
            this.hideLoading();

            if (result.action === 'error') {
                this.addMessage('ai', result.response, { isError: true });
                if (result.error) {
                    console.error('[Chat] Error:', result.error);
                }
            } else if (result.action === 'settings' && result.yaml) {
                this.handleSettingsAction(result);
            } else if (result.action === 'delete') {
                this.displayActionResponse(result.response, 'delete');
            } else if (result.yaml) {
                this.displayYamlResponse(result.response, result.yaml, result.action, result.warning);
            } else {
                this.addMessage('ai', result.response);
            }

        } catch (error) {
            clearInterval(statusInterval);
            this.hideLoading();
            this.addMessage('ai', `Error: ${error.message}`, { isError: true });
            console.error('[Chat] Exception:', error);
        }
    }

    async handleSettingsAction(result) {
        const siteId = getCurrentSiteId();
        if (!siteId) {
            this.addMessage('ai', 'Save your site first before applying SEO settings.');
            return;
        }

        // Parse YAML content as key-value (metaDescription, ogTitle)
        let seoData = {};
        try {
            // Try JSON parse first
            seoData = JSON.parse(result.yaml);
        } catch (_) {
            // Try simple key:value YAML parsing
            const lines = result.yaml.split('\n');
            for (const line of lines) {
                const match = line.match(/^(\w+):\s*["']?(.*?)["']?\s*$/);
                if (match) seoData[match[1]] = match[2];
            }
        }

        if (!seoData.metaDescription && !seoData.ogTitle) {
            this.addMessage('ai', result.response || 'Could not parse settings from AI response.');
            return;
        }

        // Build settings payload
        const settingsPayload = { seo: {} };
        if (seoData.metaDescription) settingsPayload.seo.metaDescription = seoData.metaDescription;
        if (seoData.ogTitle) settingsPayload.seo.ogTitle = seoData.ogTitle;

        // Show the suggestion with an apply button
        const messageEl = document.createElement('div');
        messageEl.className = 'message message-ai';
        let html = '';
        if (result.response) {
            const cleanResponse = result.response.replace(/<!--\s*ACTION:\s*\w+\s*-->/gi, '').trim();
            if (cleanResponse) html += `<div class="response-text">${this.formatMessageContent(cleanResponse)}</div>`;
        }
        html += `<div class="yaml-block"><div class="yaml-block-header"><span>SEO Settings</span></div><pre><code>`;
        if (seoData.metaDescription) html += `Meta Description: ${this.escapeHtml(seoData.metaDescription)}\n`;
        if (seoData.ogTitle) html += `OG Title: ${this.escapeHtml(seoData.ogTitle)}`;
        html += `</code></pre></div>`;
        html += `<button class="apply-btn" data-action="settings">Apply to Site Settings</button>`;
        messageEl.innerHTML = html;

        const applyBtn = messageEl.querySelector('.apply-btn');
        applyBtn.addEventListener('click', async () => {
            applyBtn.disabled = true;
            applyBtn.textContent = 'Applying...';
            try {
                await updateSiteSettings(settingsPayload);
                applyBtn.textContent = 'Applied!';
                this.addMessage('ai', 'SEO settings updated successfully!');
                // Refresh settings panel if open
                if (window.renderSettingsPanel) window.renderSettingsPanel();
            } catch (err) {
                applyBtn.disabled = false;
                applyBtn.textContent = 'Apply to Site Settings';
                this.addMessage('ai', `Failed to apply settings: ${err.message}`, { isError: true });
            }
        });

        this.messagesArea.appendChild(messageEl);
        this.scrollToBottom();
    }

    async applyYamlChanges() {
        if (this.isLoading) return;
        if (!this.pendingYaml && this.pendingAction !== 'delete') return;

        const yaml = this.pendingYaml;
        const action = this.pendingAction;

        this.showLoading();
        this.updateLoadingText('Applying changes...');

        const applyBtns = this.messagesArea.querySelectorAll('.apply-btn');
        applyBtns.forEach(btn => btn.disabled = true);

        try {
            await this.onYamlApply(yaml, action);

            this.updateLoadingText('Rendering preview...');
            await new Promise(resolve => setTimeout(resolve, 500));

            this.hideLoading();
            this.addMessage('ai', `Changes applied successfully! (${action})`);

            this.pendingYaml = null;
            this.pendingAction = null;

        } catch (error) {
            this.hideLoading();
            this.addMessage('ai', `Failed to apply: ${error.message}\n\nYou can try clicking "Apply Changes" again, or ask me to fix the issue.`, { isError: true });
            console.error('[Chat] Apply error:', error);

            applyBtns.forEach(btn => btn.disabled = false);
        }
    }
}

// Factory function for initialization (no container param needed - binds to existing DOM)
export function initChat(options = {}) {
    console.log('[Chat] initChat called');
    try {
        const chatUI = new ChatUI(options);
        console.log('[Chat] Chat UI initialized (bound to existing DOM)');
        return chatUI;
    } catch (error) {
        console.error('[Chat] Failed to initialize chat:', error);
        throw error;
    }
}

export { ChatUI };
