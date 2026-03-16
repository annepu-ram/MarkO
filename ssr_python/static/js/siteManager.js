/**
 * Site Manager — Client-side API wrapper for site/page CRUD and autosave.
 *
 * Manages the current site and page state, autosaves YAML to the server,
 * and provides methods for site/page lifecycle operations.
 */
import { debounce } from './utils/timing.js';

// =============================================================================
// State
// =============================================================================

let _currentSiteId = null;
let _currentPageId = null;
let _currentPageSlug = null;
let _saving = false;
let _lastSavedAt = null;

// =============================================================================
// API Helpers
// =============================================================================

async function _apiFetch(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data;
}

// =============================================================================
// Site Operations
// =============================================================================

export async function listSites() {
    return _apiFetch('/api/sites');
}

export async function createSite(name, slug) {
    const data = await _apiFetch('/api/sites', {
        method: 'POST',
        body: JSON.stringify({ name, slug }),
    });
    // Auto-load the new site
    _currentSiteId = data.id;
    if (data.pages && data.pages.length > 0) {
        _currentPageId = data.pages[0].id;
        _currentPageSlug = data.pages[0].slug;
    }
    return data;
}

export async function loadSite(siteId) {
    const data = await _apiFetch(`/api/sites/${siteId}`);
    _currentSiteId = data.id;
    return data;
}

export async function updateSite(siteId, updates) {
    return _apiFetch(`/api/sites/${siteId}`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
    });
}

export async function deleteSite(siteId) {
    const data = await _apiFetch(`/api/sites/${siteId}`, { method: 'DELETE' });
    if (siteId === _currentSiteId) {
        _currentSiteId = null;
        _currentPageId = null;
        _currentPageSlug = null;
    }
    return data;
}

// =============================================================================
// Page Operations
// =============================================================================

export async function listPages(siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/pages`);
}

export async function createPage(title, slug, siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/pages`, {
        method: 'POST',
        body: JSON.stringify({ title, slug }),
    });
}

export async function loadPage(pageId, siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    const data = await _apiFetch(`/api/sites/${siteId}/pages/${pageId}`);
    _currentPageId = data.id;
    _currentPageSlug = data.slug;
    return data;
}

export async function updatePage(pageId, updates, siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/pages/${pageId}`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
    });
}

export async function deletePage(pageId, siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/pages/${pageId}`, { method: 'DELETE' });
}

// =============================================================================
// Autosave — debounced YAML save to server
// =============================================================================

async function _saveYamlToServer(yamlContent) {
    if (!_currentSiteId || !_currentPageId) return;
    if (_saving) return; // Prevent concurrent saves

    _saving = true;
    try {
        const data = await _apiFetch(`/api/sites/${_currentSiteId}/pages/${_currentPageId}`, {
            method: 'PUT',
            body: JSON.stringify({ yaml_content: yamlContent }),
        });
        _lastSavedAt = data.updated_at;
        _dispatchSaveEvent('saved', _lastSavedAt);
    } catch (err) {
        console.error('[SiteManager] Autosave failed:', err);
        _dispatchSaveEvent('error', err.message);
    } finally {
        _saving = false;
    }
}

// Debounced autosave (2 seconds)
const _debouncedSave = debounce(_saveYamlToServer, 2000);

/**
 * Queue a YAML autosave. Call this on every editor change.
 * The actual save is debounced to 2 seconds.
 */
export function autosave(yamlContent) {
    if (!_currentSiteId || !_currentPageId) return;
    _dispatchSaveEvent('saving');
    _debouncedSave(yamlContent);
}

/**
 * Force an immediate save (e.g., before page switch).
 */
export async function saveNow(yamlContent) {
    await _saveYamlToServer(yamlContent);
}

// =============================================================================
// Publish / Unpublish
// =============================================================================

export async function publishSite(siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/publish`, { method: 'POST' });
}

export async function unpublishSite(siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/unpublish`, { method: 'POST' });
}

// =============================================================================
// Site Settings (SEO, Branding, Social)
// =============================================================================

export async function getSiteSettings(siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/settings`);
}

export async function updateSiteSettings(settings, siteId) {
    siteId = siteId || _currentSiteId;
    if (!siteId) throw new Error('No site loaded');
    return _apiFetch(`/api/sites/${siteId}/settings`, {
        method: 'PUT',
        body: JSON.stringify(settings),
    });
}

// =============================================================================
// State Accessors
// =============================================================================

export function getCurrentSiteId() { return _currentSiteId; }
export function getCurrentPageId() { return _currentPageId; }
export function getCurrentPageSlug() { return _currentPageSlug; }
export function getLastSavedAt() { return _lastSavedAt; }
export function isSaving() { return _saving; }

export function setCurrentSite(siteId) { _currentSiteId = siteId; }
export function setCurrentPage(pageId, pageSlug) {
    _currentPageId = pageId;
    _currentPageSlug = pageSlug || null;
}

// =============================================================================
// Save Status Events
// =============================================================================

function _dispatchSaveEvent(status, detail = null) {
    window.dispatchEvent(new CustomEvent('swift-save-status', {
        detail: { status, detail },
    }));
}
