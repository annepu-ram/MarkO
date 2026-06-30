/**
 * Settings Panel — Site-wide settings (SEO, branding, social).
 *
 * Renders a form in the sidebar panel with grouped sections.
 * Loads settings from API on open, saves on button click.
 */
import { getSiteSettings, updateSiteSettings, getCurrentSiteId } from './siteManager.js';
import { chatService } from './chatService.js';
import { showMessageModal } from './promptModal.js';

function _escapeAttr(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _escapeHtml(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export async function renderSettingsPanel() {
    const container = document.getElementById('settingsContent');
    const footer = document.getElementById('settingsFooter');
    if (!container) return;

    const siteId = getCurrentSiteId();
    if (!siteId) {
        container.innerHTML = '<div class="settings-empty">Save your site first to configure settings.</div>';
        if (footer) footer.innerHTML = '';
        return;
    }

    container.innerHTML = '<div class="settings-loading">Loading settings...</div>';

    let settings;
    try {
        settings = await getSiteSettings(siteId);
    } catch (err) {
        container.innerHTML = `<div class="settings-error">Failed to load settings.</div>`;
        return;
    }

    const seo = settings.seo || {};
    const branding = settings.branding || {};
    const social = settings.social || {};

    container.innerHTML = `
        <div class="settings-form">
            <div class="settings-section">
                <div class="settings-section-header">
                    <h4 class="settings-section-title">SEO</h4>
                    <button class="btn btn-ghost btn-sm settings-ai-btn" id="settingsAiBtn">Generate with AI</button>
                </div>
                <label class="settings-label" for="seoTitleTemplate">Title Template</label>
                <input type="text" class="settings-input" id="seoTitleTemplate"
                       value="${_escapeAttr(seo.titleTemplate)}"
                       placeholder="{pageTitle} | {siteName}">
                <span class="settings-hint">Use {pageTitle} and {siteName} as placeholders</span>

                <label class="settings-label" for="seoMetaDescription">Meta Description</label>
                <textarea class="settings-textarea" id="seoMetaDescription" rows="3"
                          placeholder="Brief description for search engines">${_escapeHtml(seo.metaDescription)}</textarea>

                <label class="settings-label" for="seoOgTitle">OG Title</label>
                <input type="text" class="settings-input" id="seoOgTitle"
                       value="${_escapeAttr(seo.ogTitle)}"
                       placeholder="Social sharing title (defaults to page title)">

                <label class="settings-label" for="seoOgImage">OG Image URL</label>
                <input type="text" class="settings-input" id="seoOgImage"
                       value="${_escapeAttr(seo.ogImage)}"
                       placeholder="https://example.com/image.jpg">
            </div>

            <div class="settings-section">
                <h4 class="settings-section-title">Branding</h4>
                <label class="settings-label" for="brandingSiteName">Site Display Name</label>
                <input type="text" class="settings-input" id="brandingSiteName"
                       value="${_escapeAttr(branding.siteName)}"
                       placeholder="Defaults to site name">

                <label class="settings-label" for="brandingFaviconUrl">Favicon URL</label>
                <div class="settings-favicon-row">
                    <input type="text" class="settings-input" id="brandingFaviconUrl"
                           value="${_escapeAttr(branding.faviconUrl)}"
                           placeholder="/uploads/favicon.webp or URL">
                    ${branding.faviconUrl
                        ? `<img class="settings-favicon-preview" src="${_escapeAttr(branding.faviconUrl)}" alt="Favicon">`
                        : ''}
                </div>
            </div>

            <div class="settings-section">
                <h4 class="settings-section-title">Social Media</h4>
                <label class="settings-label" for="socialTwitterHandle">Twitter / X Handle</label>
                <input type="text" class="settings-input" id="socialTwitterHandle"
                       value="${_escapeAttr(social.twitterHandle)}"
                       placeholder="@yourhandle">

                <label class="settings-label" for="socialFacebookPage">Facebook Page URL</label>
                <input type="text" class="settings-input" id="socialFacebookPage"
                       value="${_escapeAttr(social.facebookPage)}"
                       placeholder="https://facebook.com/yourpage">

                <label class="settings-label" for="socialDefaultShareImage">Default Share Image</label>
                <input type="text" class="settings-input" id="socialDefaultShareImage"
                       value="${_escapeAttr(social.defaultShareImage)}"
                       placeholder="https://example.com/share.jpg">
            </div>
        </div>
    `;

    if (footer) {
        footer.innerHTML = `
            <button class="btn btn-primary settings-save-btn" id="settingsSaveBtn">Save Settings</button>
            <div class="settings-save-status" id="settingsSaveStatus"></div>
        `;
        document.getElementById('settingsSaveBtn').addEventListener('click', _saveSettings);
    }

    // Wire up AI generate button
    const aiBtn = document.getElementById('settingsAiBtn');
    if (aiBtn) {
        aiBtn.addEventListener('click', () => _generateSeoWithAi(aiBtn));
    }
}

async function _generateSeoWithAi(btn) {
    const editor = document.getElementById('codeEditor');
    const yamlContent = editor ? editor.value.trim() : '';
    if (!yamlContent) {
        await showMessageModal({
            title: 'Content required',
            message: 'Add some content to the editor first so AI can analyze your page.',
        });
        return;
    }

    const origText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        const prompt = `Based on this website YAML content, generate SEO metadata as JSON with exactly these fields:
{"metaDescription": "a compelling 150-160 character description for search engines", "ogTitle": "an engaging social sharing title"}
Only output the JSON object, no other text. Analyze the page content to write relevant, specific SEO copy.`;

        const result = await chatService.sendMessage(prompt, yamlContent, null);

        // Try to extract JSON from the response
        let seoData = null;
        const responseText = result.response || '';

        // Try parsing the raw response as JSON
        const jsonMatch = responseText.match(/\{[\s\S]*?"metaDescription"[\s\S]*?\}/);
        if (jsonMatch) {
            try { seoData = JSON.parse(jsonMatch[0]); } catch (_) { /* ignore */ }
        }

        // Also check if result.yaml contains JSON (some models wrap in code blocks)
        if (!seoData && result.yaml) {
            try { seoData = JSON.parse(result.yaml); } catch (_) { /* ignore */ }
        }

        if (seoData) {
            // Pre-fill the form fields (user can review before saving)
            if (seoData.metaDescription) {
                const el = document.getElementById('seoMetaDescription');
                if (el) el.value = seoData.metaDescription;
            }
            if (seoData.ogTitle) {
                const el = document.getElementById('seoOgTitle');
                if (el) el.value = seoData.ogTitle;
            }
            btn.textContent = 'Fields updated!';
            setTimeout(() => { btn.textContent = origText; }, 2000);
        } else {
            btn.textContent = 'AI returned no data';
            setTimeout(() => { btn.textContent = origText; }, 3000);
        }
    } catch (err) {
        console.error('[Settings] AI generation failed:', err);
        btn.textContent = 'AI unavailable';
        setTimeout(() => { btn.textContent = origText; }, 3000);
    } finally {
        btn.disabled = false;
    }
}

async function _saveSettings() {
    const statusEl = document.getElementById('settingsSaveStatus');
    const saveBtn = document.getElementById('settingsSaveBtn');

    const settingsData = {
        seo: {
            titleTemplate: document.getElementById('seoTitleTemplate')?.value || '',
            metaDescription: document.getElementById('seoMetaDescription')?.value || '',
            ogTitle: document.getElementById('seoOgTitle')?.value || '',
            ogImage: document.getElementById('seoOgImage')?.value || '',
        },
        branding: {
            siteName: document.getElementById('brandingSiteName')?.value || '',
            faviconUrl: document.getElementById('brandingFaviconUrl')?.value || '',
        },
        social: {
            twitterHandle: document.getElementById('socialTwitterHandle')?.value || '',
            facebookPage: document.getElementById('socialFacebookPage')?.value || '',
            defaultShareImage: document.getElementById('socialDefaultShareImage')?.value || '',
        },
    };

    if (saveBtn) saveBtn.disabled = true;
    if (statusEl) { statusEl.textContent = 'Saving...'; statusEl.className = 'settings-save-status'; }

    try {
        await updateSiteSettings(settingsData);
        if (statusEl) { statusEl.textContent = 'Saved!'; statusEl.className = 'settings-save-status success'; }
        setTimeout(() => { if (statusEl) statusEl.textContent = ''; }, 2000);
    } catch (err) {
        if (statusEl) { statusEl.textContent = 'Error saving settings.'; statusEl.className = 'settings-save-status error'; }
    } finally {
        if (saveBtn) saveBtn.disabled = false;
    }
}
