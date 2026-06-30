/**
 * Dashboard — Sites & Submissions management.
 *
 * Standalone ES module (does not import editor modules).
 * Handles site listing (In Development / Published sections),
 * version history with rollback, and form submissions view.
 */

import { loadSvgSprite } from './sprite.js';
import { showConfirmModal, showMessageModal } from './promptModal.js';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let currentView = 'sites';
let sitesData = [];
let submissionsData = { items: [], total: 0, page: 1, pages: 0 };
let submissionFilter = 'all';
let submissionPage = 1;
let expandedVersions = new Set();   // site IDs with version panel open
let expandedSubmissions = new Set(); // submission IDs expanded

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatRelativeTime(isoString) {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDate(isoString) {
    if (!isoString) return '';
    return new Date(isoString).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
    });
}

async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || `Request failed: ${res.status}`);
    }
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    return res;
}

// ---------------------------------------------------------------------------
// Sites View
// ---------------------------------------------------------------------------

async function loadSites() {
    try {
        sitesData = await apiFetch('/api/sites');
        renderSitesView();
    } catch (err) {
        document.getElementById('dashboardMain').innerHTML =
            `<div class="empty-state"><p>Failed to load sites: ${escapeHtml(err.message)}</p></div>`;
    }
}

function renderSitesView() {
    const main = document.getElementById('dashboardMain');
    const inDev = sitesData.filter(s => s.sections.includes('development'));
    const published = sitesData.filter(s => s.sections.includes('published'));

    let html = `
        <div class="dashboard-section">
            <div class="dashboard-section-header">
                <h2 class="dashboard-section-title">In Development</h2>
                <button class="create-site-btn" id="createSiteBtn">
                    <svg aria-hidden="true"><use href="#icon-plus"></use></svg>
                    New Site
                </button>
            </div>
            <div class="site-cards-grid">
                ${inDev.length
                    ? inDev.map(s => renderSiteCard(s, 'development')).join('')
                    : '<div class="empty-state"><p>No sites in development</p></div>'
                }
            </div>
        </div>`;

    if (published.length) {
        html += `
        <div class="dashboard-section">
            <div class="dashboard-section-header">
                <h2 class="dashboard-section-title">Published</h2>
            </div>
            <div class="site-cards-grid">
                ${published.map(s => renderSiteCard(s, 'published')).join('')}
            </div>
        </div>`;
    }

    main.innerHTML = html;
    bindSiteEvents();
}

function renderSiteCard(site, section) {
    const isPublished = site.status === 'published';
    const badgeClass = isPublished ? 'published' : 'draft';
    const badgeLabel = isPublished ? 'Published' : 'Draft';

    let actionsHtml = '';
    if (section === 'development') {
        actionsHtml = `
            <button class="btn btn-primary btn-sm site-action" data-action="edit" data-id="${site.id}">Edit</button>
            <button class="btn btn-ghost btn-sm site-action" data-action="settings" data-id="${site.id}">Settings</button>
            ${site.version_count > 0
                ? `<button class="btn btn-ghost btn-sm site-action" data-action="versions" data-id="${site.id}">Versions</button>`
                : ''
            }
            <button class="btn btn-ghost btn-sm btn-danger site-action" data-action="delete" data-id="${site.id}">Delete</button>
        `;
    } else {
        actionsHtml = `
            <a class="btn btn-ghost btn-sm" href="/s/${escapeHtml(site.slug)}" target="_blank">View Live</a>
            <button class="btn btn-ghost btn-sm site-action" data-action="settings" data-id="${site.id}">Settings</button>
            <button class="btn btn-ghost btn-sm site-action" data-action="unpublish" data-id="${site.id}">Unpublish</button>
            ${site.version_count > 0
                ? `<button class="btn btn-ghost btn-sm site-action" data-action="versions" data-id="${site.id}">Versions</button>`
                : ''
            }
        `;
    }

    const versionInfo = site.current_version ? `v${site.current_version}` : '';
    const versionsOpen = expandedVersions.has(site.id + '-' + section);

    return `
    <div class="site-card" data-site-id="${site.id}">
        <div class="site-card-header">
            <div>
                <div class="site-card-name">${escapeHtml(site.name)}</div>
                <div class="site-card-slug">/s/${escapeHtml(site.slug)}</div>
            </div>
            <span class="status-badge ${badgeClass}">${badgeLabel}</span>
        </div>
        <div class="site-card-meta">
            ${versionInfo ? `<span>${versionInfo}</span>` : ''}
            <span class="site-card-updated">Updated ${formatRelativeTime(site.updated_at)}</span>
        </div>
        <div class="site-card-actions">
            ${actionsHtml}
            <button class="pages-toggle-btn site-action" data-action="pages" data-id="${site.id}">
                <svg class="chevron-mini" aria-hidden="true"><use href="#icon-chevron-right"></use></svg>
                ${site.page_count} page${site.page_count !== 1 ? 's' : ''}
            </button>
        </div>
        <div class="pages-list" id="pages-${site.id}-${section}" style="display:none"></div>
        <div class="version-history" id="versions-${site.id}-${section}" style="display:${versionsOpen ? 'block' : 'none'}"></div>
    </div>`;
}

function bindSiteEvents() {
    // Action buttons
    document.querySelectorAll('.site-action').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const action = e.currentTarget.dataset.action;
            const id = e.currentTarget.dataset.id;
            if (action === 'edit') handleEdit(id);
            else if (action === 'settings') showSettingsModal(id);
            else if (action === 'delete') await handleDelete(id);
            else if (action === 'versions') await toggleVersions(e.currentTarget);
            else if (action === 'pages') await togglePages(e.currentTarget);
            else if (action === 'unpublish') await handleUnpublish(id);
        });
    });

    // Create site button
    const createBtn = document.getElementById('createSiteBtn');
    if (createBtn) createBtn.addEventListener('click', showCreateSiteModal);
}

function handleEdit(siteId) {
    const card = document.querySelector(`.site-card[data-site-id="${siteId}"]`);
    if (!card) { window.location.href = `/editor/${siteId}`; return; }

    const rect = card.getBoundingClientRect();

    // Create fixed-position clone overlay at the card's exact position
    const clone = card.cloneNode(true);
    clone.classList.add('site-card-zoom');
    clone.style.position = 'fixed';
    clone.style.top = rect.top + 'px';
    clone.style.left = rect.left + 'px';
    clone.style.width = rect.width + 'px';
    clone.style.height = rect.height + 'px';
    clone.style.zIndex = '9999';
    clone.style.margin = '0';
    document.body.appendChild(clone);

    // Force reflow then animate to fullscreen
    clone.offsetHeight;
    clone.classList.add('site-card-zoom-active');

    // Navigate once animation finishes
    let navigated = false;
    const navigate = () => {
        if (navigated) return;
        navigated = true;
        window.location.href = `/editor/${siteId}`;
    };
    clone.addEventListener('transitionend', navigate, { once: true });
    setTimeout(navigate, 600); // fallback
}

async function handleDelete(siteId) {
    const site = sitesData.find(s => s.id === siteId);
    if (!site) return;
    const confirmed = await showConfirmModal({
        title: 'Delete site',
        message: `Delete "${site.name}"? This cannot be undone.`,
        confirmText: 'Delete',
        danger: true,
    });
    if (!confirmed) return;
    try {
        await apiFetch(`/api/sites/${siteId}`, { method: 'DELETE' });
        await loadSites();
    } catch (err) {
        await showMessageModal({ title: 'Delete failed', message: err.message });
    }
}

async function handleUnpublish(siteId) {
    const confirmed = await showConfirmModal({
        title: 'Unpublish site',
        message: 'Unpublish this site? It will no longer be accessible to visitors.',
        confirmText: 'Unpublish',
    });
    if (!confirmed) return;
    try {
        await apiFetch(`/api/sites/${siteId}/unpublish`, { method: 'POST' });
        await loadSites();
    } catch (err) {
        await showMessageModal({ title: 'Unpublish failed', message: err.message });
    }
}

// ---------------------------------------------------------------------------
// Pages Accordion
// ---------------------------------------------------------------------------

async function togglePages(btn) {
    const siteId = btn.dataset.id;
    const card = btn.closest('.site-card');
    const container = card.querySelector('.pages-list');
    if (!container) return;

    const chevron = btn.querySelector('.chevron-mini');

    if (container.style.display !== 'none') {
        container.style.display = 'none';
        if (chevron) chevron.classList.remove('open');
        return;
    }

    container.innerHTML = '<div class="pages-loading">Loading pages...</div>';
    container.style.display = 'block';
    if (chevron) chevron.classList.add('open');

    try {
        const pages = await apiFetch(`/api/sites/${siteId}/pages`);
        if (!pages.length) {
            container.innerHTML = '<div class="pages-empty">No pages</div>';
            return;
        }
        container.innerHTML = pages.map(p => `
            <div class="page-item">
                <div class="page-info">
                    <span class="page-title">${escapeHtml(p.title)}</span>
                    <span class="page-slug">/${escapeHtml(p.slug)}</span>
                </div>
                <button class="btn btn-ghost btn-xs page-edit-btn"
                        data-site-id="${siteId}" data-page-id="${p.id}">
                    Edit
                </button>
            </div>
        `).join('');

        container.querySelectorAll('.page-edit-btn').forEach(eb => {
            eb.addEventListener('click', () => {
                handleEdit(eb.dataset.siteId);
            });
        });
    } catch (err) {
        container.innerHTML = `<div class="pages-empty">Error: ${escapeHtml(err.message)}</div>`;
    }
}

// ---------------------------------------------------------------------------
// Version History
// ---------------------------------------------------------------------------

async function toggleVersions(btn) {
    const siteId = btn.dataset.id;
    const card = btn.closest('.site-card');
    const container = card.querySelector('.version-history');
    if (!container) return;

    if (container.style.display !== 'none') {
        container.style.display = 'none';
        return;
    }

    container.innerHTML = '<div class="version-loading">Loading versions...</div>';
    container.style.display = 'block';

    try {
        const versions = await apiFetch(`/api/sites/${siteId}/versions`);
        if (!versions.length) {
            container.innerHTML = '<div class="version-item version-empty">No versions yet</div>';
            return;
        }
        container.innerHTML = versions.map(v => `
            <div class="version-item">
                <div class="version-info">
                    <span class="version-num">v${v.version_number}</span>
                    ${v.label ? `<span class="version-label">${escapeHtml(v.label)}</span>` : ''}
                    <span class="version-date">${formatDate(v.published_at)}</span>
                    ${v.is_current ? '<span class="version-current">live</span>' : ''}
                    <span class="version-pages">${v.page_count} page${v.page_count !== 1 ? 's' : ''}</span>
                </div>
                ${!v.is_current ? `
                    <button class="btn btn-ghost btn-xs version-rollback"
                            data-site-id="${siteId}" data-version-id="${v.id}" data-version-num="${v.version_number}">
                        Rollback
                    </button>
                ` : ''}
            </div>
        `).join('');

        container.querySelectorAll('.version-rollback').forEach(rb => {
            rb.addEventListener('click', async () => {
                const vNum = rb.dataset.versionNum;
                const confirmed = await showConfirmModal({
                    title: 'Rollback draft',
                    message: `Rollback draft to v${vNum}? Current draft pages will be overwritten.`,
                    confirmText: 'Rollback',
                });
                if (!confirmed) return;
                try {
                    await apiFetch(`/api/sites/${rb.dataset.siteId}/versions/${rb.dataset.versionId}/rollback`, { method: 'POST' });
                    await loadSites();
                } catch (err) {
                    await showMessageModal({ title: 'Rollback failed', message: err.message });
                }
            });
        });
    } catch (err) {
        container.innerHTML = `<div class="version-item version-empty">Error: ${escapeHtml(err.message)}</div>`;
    }
}

// ---------------------------------------------------------------------------
// Create Site Modal
// ---------------------------------------------------------------------------

function showCreateSiteModal() {
    const overlay = document.createElement('div');
    overlay.className = 'dashboard-modal-overlay';
    overlay.innerHTML = `
        <div class="dashboard-modal">
            <h3>Create New Site</h3>
            <label class="modal-label">Site Name</label>
            <input type="text" id="newSiteName" placeholder="My Awesome Site" autofocus>
            <label class="modal-label">Slug (URL path)</label>
            <input type="text" id="newSiteSlug" placeholder="my-awesome-site">
            <div id="createSiteError" class="modal-error" style="display:none"></div>
            <div class="dashboard-modal-actions">
                <button class="btn btn-ghost" id="cancelCreate">Cancel</button>
                <button class="btn btn-primary" id="confirmCreate">Create</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    const nameInput = overlay.querySelector('#newSiteName');
    const slugInput = overlay.querySelector('#newSiteSlug');
    const errorDiv = overlay.querySelector('#createSiteError');

    // Auto-generate slug from name
    nameInput.addEventListener('input', () => {
        slugInput.value = nameInput.value
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
    });

    overlay.querySelector('#cancelCreate').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    overlay.querySelector('#confirmCreate').addEventListener('click', async () => {
        const name = nameInput.value.trim();
        const slug = slugInput.value.trim();
        if (!name || !slug) {
            errorDiv.textContent = 'Both name and slug are required.';
            errorDiv.style.display = 'block';
            return;
        }
        try {
            const result = await apiFetch('/api/sites', {
                method: 'POST',
                body: JSON.stringify({ name, slug }),
            });
            overlay.remove();
            window.location.href = `/editor/${result.id}`;
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.style.display = 'block';
        }
    });

    nameInput.focus();
}

// ---------------------------------------------------------------------------
// Settings Modal
// ---------------------------------------------------------------------------

function showSettingsModal(siteId) {
    const overlay = document.createElement('div');
    overlay.className = 'dashboard-modal-overlay';
    overlay.innerHTML = `
        <div class="dashboard-modal dashboard-modal-wide">
            <h3>Site Settings</h3>
            <div class="settings-modal-loading">Loading settings...</div>
        </div>
    `;
    document.body.appendChild(overlay);

    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    // Load settings and render form
    _loadSettingsForm(overlay, siteId);
}

async function _loadSettingsForm(overlay, siteId) {
    const modal = overlay.querySelector('.dashboard-modal');
    try {
        const settings = await apiFetch(`/api/sites/${siteId}/settings`);
        const seo = settings.seo || {};
        const branding = settings.branding || {};
        const social = settings.social || {};

        modal.innerHTML = `
            <h3>Site Settings</h3>
            <div class="settings-modal-sections">
                <div class="settings-modal-section">
                    <div class="settings-modal-section-title">SEO</div>
                    <label class="modal-label">Title Template</label>
                    <input type="text" id="settTitleTemplate" value="${_escAttr(seo.titleTemplate)}" placeholder="{pageTitle} | {siteName}">
                    <div class="settings-modal-hint">Use {pageTitle} and {siteName} as placeholders</div>
                    <label class="modal-label">Meta Description</label>
                    <textarea id="settMetaDescription" rows="2" placeholder="Brief description for search engines">${_escHtml(seo.metaDescription)}</textarea>
                    <label class="modal-label">OG Title</label>
                    <input type="text" id="settOgTitle" value="${_escAttr(seo.ogTitle)}" placeholder="Title for social sharing">
                    <label class="modal-label">OG Image URL</label>
                    <input type="text" id="settOgImage" value="${_escAttr(seo.ogImage)}" placeholder="https://example.com/image.jpg">
                </div>
                <div class="settings-modal-section">
                    <div class="settings-modal-section-title">Branding</div>
                    <label class="modal-label">Site Display Name</label>
                    <input type="text" id="settSiteName" value="${_escAttr(branding.siteName)}" placeholder="My Site">
                    <label class="modal-label">Favicon URL</label>
                    <div class="settings-modal-favicon-row">
                        <input type="text" id="settFaviconUrl" value="${_escAttr(branding.faviconUrl)}" placeholder="https://example.com/favicon.ico">
                        ${branding.faviconUrl ? `<img class="settings-modal-favicon-preview" src="${_escAttr(branding.faviconUrl)}" alt="favicon">` : ''}
                    </div>
                </div>
                <div class="settings-modal-section">
                    <div class="settings-modal-section-title">Social</div>
                    <label class="modal-label">Twitter Handle</label>
                    <input type="text" id="settTwitter" value="${_escAttr(social.twitterHandle)}" placeholder="@yourhandle">
                    <label class="modal-label">Facebook Page</label>
                    <input type="text" id="settFacebook" value="${_escAttr(social.facebookPage)}" placeholder="https://facebook.com/yourpage">
                    <label class="modal-label">Default Share Image</label>
                    <input type="text" id="settShareImage" value="${_escAttr(social.defaultShareImage)}" placeholder="https://example.com/share.jpg">
                </div>
            </div>
            <div id="settingsModalError" class="modal-error" style="display:none"></div>
            <div class="dashboard-modal-actions">
                <button class="btn btn-ghost" id="settingsCancel">Cancel</button>
                <button class="btn btn-primary" id="settingsSave">Save</button>
            </div>
        `;

        // Favicon preview on URL change
        const faviconInput = modal.querySelector('#settFaviconUrl');
        faviconInput.addEventListener('change', () => {
            const row = faviconInput.closest('.settings-modal-favicon-row');
            const existing = row.querySelector('.settings-modal-favicon-preview');
            if (existing) existing.remove();
            if (faviconInput.value.trim()) {
                const img = document.createElement('img');
                img.className = 'settings-modal-favicon-preview';
                img.src = faviconInput.value.trim();
                img.alt = 'favicon';
                row.appendChild(img);
            }
        });

        modal.querySelector('#settingsCancel').addEventListener('click', () => overlay.remove());

        modal.querySelector('#settingsSave').addEventListener('click', async () => {
            const errorDiv = modal.querySelector('#settingsModalError');
            const payload = {
                seo: {
                    titleTemplate: modal.querySelector('#settTitleTemplate').value,
                    metaDescription: modal.querySelector('#settMetaDescription').value,
                    ogTitle: modal.querySelector('#settOgTitle').value,
                    ogImage: modal.querySelector('#settOgImage').value,
                },
                branding: {
                    siteName: modal.querySelector('#settSiteName').value,
                    faviconUrl: modal.querySelector('#settFaviconUrl').value,
                },
                social: {
                    twitterHandle: modal.querySelector('#settTwitter').value,
                    facebookPage: modal.querySelector('#settFacebook').value,
                    defaultShareImage: modal.querySelector('#settShareImage').value,
                },
            };

            try {
                await apiFetch(`/api/sites/${siteId}/settings`, {
                    method: 'PUT',
                    body: JSON.stringify(payload),
                });
                overlay.remove();
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.style.display = 'block';
            }
        });

    } catch (err) {
        modal.innerHTML = `
            <h3>Site Settings</h3>
            <div class="settings-modal-error-state">Failed to load settings: ${escapeHtml(err.message)}</div>
            <div class="dashboard-modal-actions">
                <button class="btn btn-ghost" id="settingsCancel">Close</button>
            </div>
        `;
        modal.querySelector('#settingsCancel').addEventListener('click', () => overlay.remove());
    }
}

function _escAttr(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ---------------------------------------------------------------------------
// Submissions View
// ---------------------------------------------------------------------------

async function loadSubmissions(page = 1) {
    submissionPage = page;
    try {
        submissionsData = await apiFetch(
            `/api/submissions?filter=${submissionFilter}&page=${page}&per_page=25`
        );
        renderSubmissionsView();
    } catch (err) {
        document.getElementById('dashboardMain').innerHTML =
            `<div class="empty-state"><p>Failed to load submissions: ${escapeHtml(err.message)}</p></div>`;
    }
}

function renderSubmissionsView() {
    const main = document.getElementById('dashboardMain');
    const { items, total, page, pages } = submissionsData;

    const filterTabs = ['all', 'unread', 'spam'].map(f =>
        `<button class="filter-tab ${f === submissionFilter ? 'active' : ''}" data-filter="${f}">
            ${f.charAt(0).toUpperCase() + f.slice(1)}
        </button>`
    ).join('');

    let tableHtml = '';
    if (items.length) {
        const rows = items.map(sub => {
            const isExpanded = expandedSubmissions.has(sub.id);
            const dataEntries = Object.entries(sub.data);
            return `
            <tr class="submission-row ${sub.is_read ? '' : 'unread'} ${sub.is_spam ? 'spam' : ''}"
                data-id="${sub.id}">
                <td class="sub-toggle" data-id="${sub.id}">
                    <svg class="chevron ${isExpanded ? 'open' : ''}" aria-hidden="true"><use href="#icon-chevron-down"></use></svg>
                </td>
                <td>${escapeHtml(sub.site_name)}</td>
                <td>${escapeHtml(sub.form_name)}</td>
                <td>${escapeHtml(sub.page_slug)}</td>
                <td>${formatRelativeTime(sub.submitted_at)}</td>
                <td>
                    <button class="btn btn-ghost btn-xs sub-action" data-action="${sub.is_read ? 'unread' : 'read'}" data-id="${sub.id}">
                        ${sub.is_read ? 'Mark Unread' : 'Mark Read'}
                    </button>
                    <button class="btn btn-ghost btn-xs sub-action" data-action="${sub.is_spam ? 'unspam' : 'spam'}" data-id="${sub.id}">
                        ${sub.is_spam ? 'Not Spam' : 'Spam'}
                    </button>
                    <button class="btn btn-ghost btn-xs btn-danger sub-action" data-action="delete" data-id="${sub.id}">Delete</button>
                </td>
            </tr>
            ${isExpanded ? `
            <tr class="submission-detail-row"><td colspan="6">
                <div class="submission-detail">
                    ${dataEntries.length
                        ? dataEntries.map(([k, v]) =>
                            `<div class="detail-field"><strong>${escapeHtml(k)}:</strong> ${escapeHtml(String(v))}</div>`
                        ).join('')
                        : '<em>No form data</em>'
                    }
                </div>
            </td></tr>` : ''}
            `;
        }).join('');

        tableHtml = `
        <table class="submissions-table">
            <thead><tr>
                <th></th><th>Site</th><th>Form</th><th>Page</th><th>Date</th><th>Actions</th>
            </tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
    } else {
        tableHtml = '<div class="empty-state"><p>No submissions found</p></div>';
    }

    // Pagination
    let paginationHtml = '';
    if (pages > 1) {
        paginationHtml = '<div class="pagination">';
        if (page > 1) paginationHtml += `<button class="btn btn-ghost btn-sm page-btn" data-page="${page - 1}">Previous</button>`;
        paginationHtml += `<span class="page-info">Page ${page} of ${pages} (${total} total)</span>`;
        if (page < pages) paginationHtml += `<button class="btn btn-ghost btn-sm page-btn" data-page="${page + 1}">Next</button>`;
        paginationHtml += '</div>';
    }

    main.innerHTML = `
        <div class="dashboard-section">
            <div class="dashboard-section-header">
                <h2 class="dashboard-section-title">Form Submissions</h2>
                <button class="btn btn-ghost btn-sm" id="exportCsvBtn">
                    <svg aria-hidden="true"><use href="#icon-download"></use></svg>
                    Export CSV
                </button>
            </div>
            <div class="filter-tabs">${filterTabs}</div>
            ${tableHtml}
            ${paginationHtml}
        </div>
    `;

    bindSubmissionEvents();
}

function bindSubmissionEvents() {
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            submissionFilter = tab.dataset.filter;
            expandedSubmissions.clear();
            loadSubmissions(1);
        });
    });

    // Expand/collapse rows
    document.querySelectorAll('.sub-toggle').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const id = toggle.dataset.id;
            if (expandedSubmissions.has(id)) expandedSubmissions.delete(id);
            else expandedSubmissions.add(id);
            renderSubmissionsView();
        });
    });

    // Actions
    document.querySelectorAll('.sub-action').forEach(btn => {
        btn.addEventListener('click', async () => {
            const { action, id } = btn.dataset;
            try {
                if (action === 'read') {
                    await apiFetch(`/api/submissions/${id}`, { method: 'PATCH', body: JSON.stringify({ is_read: true }) });
                } else if (action === 'unread') {
                    await apiFetch(`/api/submissions/${id}`, { method: 'PATCH', body: JSON.stringify({ is_read: false }) });
                } else if (action === 'spam') {
                    await apiFetch(`/api/submissions/${id}`, { method: 'PATCH', body: JSON.stringify({ is_spam: true }) });
                } else if (action === 'unspam') {
                    await apiFetch(`/api/submissions/${id}`, { method: 'PATCH', body: JSON.stringify({ is_spam: false }) });
                } else if (action === 'delete') {
                    const confirmed = await showConfirmModal({
                        title: 'Delete submission',
                        message: 'Delete this submission?',
                        confirmText: 'Delete',
                        danger: true,
                    });
                    if (!confirmed) return;
                    await apiFetch(`/api/submissions/${id}`, { method: 'DELETE' });
                }
                await loadSubmissions(submissionPage);
            } catch (err) {
                await showMessageModal({ title: 'Action failed', message: err.message });
            }
        });
    });

    // Pagination
    document.querySelectorAll('.page-btn').forEach(btn => {
        btn.addEventListener('click', () => loadSubmissions(parseInt(btn.dataset.page)));
    });

    // CSV export
    const exportBtn = document.getElementById('exportCsvBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            window.location.href = `/api/submissions/export?filter=${submissionFilter}`;
        });
    }
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', async () => {
    // Load SVG sprite
    const spritePath = window.SPRITE_PATH || '/static/icon-sprite.svg';
    await loadSvgSprite({ spritePath });

    // Collapsible sidebar
    const sidebar = document.getElementById('dashboardSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebar && sidebarToggle) {
        if (localStorage.getItem('sidebar-collapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
        });
    }

    // Sidebar navigation
    document.querySelectorAll('.dashboard-nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.dashboard-nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            if (currentView === 'sites') loadSites();
            else if (currentView === 'media') loadMediaView();
            else loadSubmissions(1);
        });
    });

    // Initial load
    await loadSites();
});

// ---------------------------------------------------------------------------
// Media Library View
// ---------------------------------------------------------------------------

let mediaSiteId = null;
let mediaImages = [];
let mediaPages = [];
let mediaFilter = { orientation: null, q: '', page_id: null };
let mediaSelectedIds = new Set();

// Add-images modal state
let addImgQuery = '';
let addImgColor = null;
let addImgOrientation = null;
let addImgResults = [];
let addImgSelected = [];
let addImgPage = 1;
let addImgTotalPages = 1;
let addImgLoading = false;

const ADD_IMG_COLORS = [
    { value: 'red', hex: '#EF4444' },
    { value: 'orange', hex: '#F97316' },
    { value: 'yellow', hex: '#EAB308' },
    { value: 'green', hex: '#22C55E' },
    { value: 'blue', hex: '#3B82F6' },
    { value: 'purple', hex: '#A855F7' },
    { value: 'black', hex: '#1A1A1A' },
    { value: 'white', hex: '#FFFFFF' },
];

const ADD_IMG_ORIENTATIONS = [
    { value: 'horizontal', label: 'Horizontal' },
    { value: 'vertical', label: 'Vertical' },
    { value: 'square', label: 'Square' },
];

async function loadMediaView() {
    const main = document.getElementById('dashboardMain');

    // Need sites list first
    if (!sitesData.length) {
        try { sitesData = await apiFetch('/api/sites'); } catch (_) {}
    }

    if (!sitesData.length) {
        main.innerHTML = '<div class="empty-state"><p>Create a site first to manage media.</p></div>';
        return;
    }

    if (!mediaSiteId) mediaSiteId = sitesData[0].id;

    await Promise.all([fetchMediaPages(), fetchMediaImages()]);
    renderMediaView();
}

async function fetchMediaPages() {
    try {
        mediaPages = await apiFetch(`/api/sites/${mediaSiteId}/pages`);
    } catch (err) {
        console.error('[Media] Failed to load pages:', err);
        mediaPages = [];
    }
}

async function fetchMediaImages() {
    try {
        const params = new URLSearchParams();
        if (mediaFilter.orientation) params.set('orientation', mediaFilter.orientation);
        if (mediaFilter.q) params.set('q', mediaFilter.q);
        if (mediaFilter.page_id) params.set('page_id', mediaFilter.page_id);
        const data = await apiFetch(`/api/media?${params}`);
        mediaImages = data.images || [];
    } catch (err) {
        console.error('[Media] Failed to load:', err);
        mediaImages = [];
    }
}

function renderMediaView() {
    const main = document.getElementById('dashboardMain');

    // Site tab strip
    const siteTabs = sitesData.map(s => {
        const active = s.id === mediaSiteId ? 'active' : '';
        return `<button class="media-site-tab ${active}" data-site-id="${s.id}">${escapeHtml(s.name)}</button>`;
    }).join('');

    // Page dropdown
    const pageOptions = [
        `<option value="">All Pages</option>`,
        ...mediaPages.map(p =>
            `<option value="${p.id}" ${mediaFilter.page_id === p.id ? 'selected' : ''}>${escapeHtml(p.title)}</option>`
        )
    ].join('');

    // Orientation pills
    const orientations = ['landscape', 'portrait', 'square'];
    const orientationPills = orientations.map(o => {
        const active = mediaFilter.orientation === o ? 'active' : '';
        return `<button class="media-filter-pill ${active}" data-orientation="${o}">${o}</button>`;
    }).join('');

    // Image grid
    let gridHtml = '';
    if (mediaImages.length === 0) {
        gridHtml = '<div class="empty-state"><p>No images yet. Upload or search stock photos in the designer.</p></div>';
    } else {
        gridHtml = mediaImages.map(img => {
            const isSelected = mediaSelectedIds.has(img.id);
            return `
            <div class="media-card ${isSelected ? 'selected' : ''}" data-image-id="${img.id}">
                <div class="media-card-thumb">
                    <img src="${img.url}" alt="${escapeHtml(img.alt_text || '')}" loading="lazy">
                    <input type="checkbox" class="media-checkbox" ${isSelected ? 'checked' : ''}>
                    ${img.orientation ? `<span class="media-orientation-badge">${img.orientation}</span>` : ''}
                </div>
                <div class="media-card-info">
                    <span class="media-card-name" title="${escapeHtml(img.alt_text || img.original_name || '')}">${escapeHtml(img.alt_text || img.original_name || 'Untitled')}</span>
                    <span class="media-card-meta">${img.photographer ? escapeHtml(img.photographer) : ''} ${img.file_size ? Math.round(img.file_size / 1024) + 'KB' : ''}</span>
                </div>
            </div>`;
        }).join('');
    }

    // Bulk bar
    let bulkBar = '';
    if (mediaSelectedIds.size > 0) {
        bulkBar = `<div class="media-bulk-bar">
            <span>${mediaSelectedIds.size} selected</span>
            <button class="btn btn-danger btn-xs" id="mediaBulkDelete">Delete Selected</button>
        </div>`;
    }

    main.innerHTML = `
        <div class="media-view">
            <div class="media-section-label">Sites</div>
            <div class="media-site-tabs">${siteTabs}</div>
            <div class="media-toolbar-row">
                <select class="media-page-select" id="mediaPageSelect">${pageOptions}</select>
                <input type="text" class="media-search-input" id="mediaSearchInput"
                       placeholder="Search images..." value="${escapeHtml(mediaFilter.q)}">
            </div>
            <div class="media-toolbar-secondary">
                <div class="media-filter-pills">
                    <button class="media-filter-pill ${!mediaFilter.orientation ? 'active' : ''}" data-orientation="">All</button>
                    ${orientationPills}
                </div>
                <span class="media-image-count">${mediaImages.length} image${mediaImages.length !== 1 ? 's' : ''}</span>
            </div>
            <hr class="media-separator">
            <button class="media-add-images-btn" id="mediaAddImagesBtn">
                <svg aria-hidden="true"><use href="#icon-image"></use></svg>
                Add Images
            </button>
            ${bulkBar}
            <div class="media-grid">${gridHtml}</div>
        </div>
    `;

    bindMediaEvents();
}

function bindMediaEvents() {
    // Site tabs
    document.querySelectorAll('.media-site-tab').forEach(tab => {
        tab.addEventListener('click', async () => {
            mediaSiteId = tab.dataset.siteId;
            mediaSelectedIds.clear();
            mediaFilter.page_id = null;
            await Promise.all([fetchMediaPages(), fetchMediaImages()]);
            renderMediaView();
        });
    });

    // Page selector
    const pageSelect = document.getElementById('mediaPageSelect');
    if (pageSelect) {
        pageSelect.addEventListener('change', async () => {
            mediaFilter.page_id = pageSelect.value || null;
            mediaSelectedIds.clear();
            await fetchMediaImages();
            renderMediaView();
        });
    }

    // Search
    const searchInput = document.getElementById('mediaSearchInput');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                mediaFilter.q = searchInput.value.trim();
                await fetchMediaImages();
                renderMediaView();
            }, 300);
        });
    }

    // Orientation filter pills
    document.querySelectorAll('.media-filter-pill').forEach(pill => {
        pill.addEventListener('click', async () => {
            mediaFilter.orientation = pill.dataset.orientation || null;
            await fetchMediaImages();
            renderMediaView();
        });
    });

    // Card selection
    document.querySelectorAll('.media-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') return;
            const id = card.dataset.imageId;
            if (mediaSelectedIds.has(id)) {
                mediaSelectedIds.delete(id);
            } else {
                mediaSelectedIds.add(id);
            }
            renderMediaView();
        });
    });

    // Add Images button
    const addImagesBtn = document.getElementById('mediaAddImagesBtn');
    if (addImagesBtn) {
        addImagesBtn.addEventListener('click', () => openAddImagesModal());
    }

    // Bulk delete
    const bulkDeleteBtn = document.getElementById('mediaBulkDelete');
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', async () => {
            const confirmed = await showConfirmModal({
                title: 'Delete images',
                message: `Delete ${mediaSelectedIds.size} image(s)?`,
                confirmText: 'Delete',
                danger: true,
            });
            if (!confirmed) return;
            try {
                await apiFetch('/api/media/bulk', {
                    method: 'POST',
                    body: JSON.stringify({ action: 'delete', asset_ids: [...mediaSelectedIds] }),
                });
                mediaSelectedIds.clear();
                await fetchMediaImages();
                renderMediaView();
            } catch (err) {
                await showMessageModal({ title: 'Failed to delete', message: err.message });
            }
        });
    }
}

// ---------------------------------------------------------------------------
// Add Images Modal
// ---------------------------------------------------------------------------

function renderAddImagesColorPills() {
    return ADD_IMG_COLORS.map(c => {
        const active = addImgColor === c.value ? 'active' : '';
        const border = c.value === 'white' ? 'border: 1px solid var(--border);' : '';
        return `<button class="add-img-color-pill ${active}" data-color="${c.value}"
                    style="background:${c.hex};${border}" title="${c.value}"></button>`;
    }).join('');
}

function renderAddImagesOrientationPills() {
    return ADD_IMG_ORIENTATIONS.map(o => {
        const active = addImgOrientation === o.value ? 'active' : '';
        return `<button class="add-img-orient-pill ${active}" data-orient="${o.value}">${o.label}</button>`;
    }).join('');
}

function renderAddImagesResults() {
    if (addImgLoading && addImgResults.length === 0) {
        let skeletons = '';
        for (let i = 0; i < 9; i++) skeletons += '<div class="add-img-skeleton"></div>';
        return skeletons;
    }
    if (addImgResults.length === 0) {
        return `<div class="add-img-empty">
            <svg aria-hidden="true" width="32" height="32"><use href="#icon-search"></use></svg>
            <div>Search for stock photos above</div>
        </div>`;
    }
    return addImgResults.map(photo => {
        const sel = addImgSelected.find(s => s.id === photo.id);
        const isSelected = !!sel;
        const downloaded = sel && sel.downloaded;
        let badge = '';
        if (isSelected) {
            badge = downloaded
                ? '<span class="add-img-badge downloaded">&#10003;</span>'
                : '<span class="add-img-badge pending"></span>';
        }
        return `<div class="add-img-card ${isSelected ? 'selected' : ''}" data-photo-id="${photo.id}">
            <img src="${photo.thumbUrl}" alt="${escapeHtml(photo.altText)}" loading="lazy">
            ${badge}
            <div class="add-img-overlay">
                <span class="add-img-credit">${escapeHtml(photo.photographer)}</span>
                <button class="add-img-select-btn">${isSelected ? '&#10003;' : '+'}</button>
            </div>
        </div>`;
    }).join('');
}

function openAddImagesModal() {
    // Reset state
    addImgQuery = '';
    addImgColor = null;
    addImgOrientation = null;
    addImgResults = [];
    addImgSelected = [];
    addImgPage = 1;
    addImgTotalPages = 1;
    addImgLoading = false;

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'addImagesOverlay';
    overlay.innerHTML = `
        <div class="add-images-modal">
            <div class="add-images-header">
                <h3>Add Images</h3>
                <button class="add-images-close" id="addImagesClose" title="Close">
                    <svg aria-hidden="true" width="18" height="18"><use href="#icon-x"></use></svg>
                </button>
            </div>
            <div class="add-images-body">
                <div class="add-img-search">
                    <input type="text" class="add-img-search-input" id="addImgSearchInput"
                           placeholder="Search stock photos...">
                    <svg class="add-img-search-icon" aria-hidden="true" width="16" height="16"><use href="#icon-search"></use></svg>
                </div>
                <div class="add-img-filters">
                    <div class="add-img-filter-group">
                        <span class="add-img-label">Colors</span>
                        <div class="add-img-color-pills">${renderAddImagesColorPills()}</div>
                    </div>
                    <div class="add-img-filter-group">
                        <span class="add-img-label">Orientation</span>
                        <div class="add-img-orient-pills">${renderAddImagesOrientationPills()}</div>
                    </div>
                </div>
                <div class="add-img-results" id="addImgResults">
                    ${renderAddImagesResults()}
                </div>
                <div class="add-img-load-more" id="addImgLoadMore" style="display:none;">
                    <button class="add-img-load-more-btn">Load More</button>
                </div>
            </div>
            <div class="add-images-footer">
                <span class="add-img-selected-count" id="addImgSelectedCount">0 selected</span>
                <div class="add-images-footer-actions">
                    <button class="add-img-upload-btn" id="addImgUploadBtn">
                        <svg aria-hidden="true" width="14" height="14"><use href="#icon-upload"></use></svg>
                        Upload File
                    </button>
                    <input type="file" id="addImgFileInput" accept="image/*" multiple hidden>
                    <button class="add-img-done-btn" id="addImgDoneBtn">Done</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    bindAddImagesModalEvents(overlay);

    // Focus search
    const searchInput = overlay.querySelector('#addImgSearchInput');
    if (searchInput) searchInput.focus();
}

async function closeAddImagesModal() {
    const overlay = document.getElementById('addImagesOverlay');
    if (overlay) overlay.remove();

    // Refresh media grid to show newly downloaded images
    await fetchMediaImages();
    renderMediaView();
}

function bindAddImagesModalEvents(overlay) {
    const modal = overlay.querySelector('.add-images-modal');

    // Close handlers
    overlay.querySelector('#addImagesClose').addEventListener('click', () => closeAddImagesModal());
    overlay.querySelector('#addImgDoneBtn').addEventListener('click', () => closeAddImagesModal());
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeAddImagesModal();
    });
    overlay.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAddImagesModal();
    });

    // Search with debounce
    const searchInput = overlay.querySelector('#addImgSearchInput');
    let debounceTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            addImgQuery = searchInput.value.trim();
            if (addImgQuery || addImgColor) searchAddImages();
        }, 300);
    });
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            addImgQuery = searchInput.value.trim();
            if (addImgQuery || addImgColor) searchAddImages();
        }
    });

    // Color pills
    overlay.querySelectorAll('.add-img-color-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const color = pill.dataset.color;
            addImgColor = addImgColor === color ? null : color;
            overlay.querySelectorAll('.add-img-color-pill').forEach(p =>
                p.classList.toggle('active', p.dataset.color === addImgColor));
            if (addImgQuery || addImgColor) searchAddImages();
        });
    });

    // Orientation pills
    overlay.querySelectorAll('.add-img-orient-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const orient = pill.dataset.orient;
            addImgOrientation = addImgOrientation === orient ? null : orient;
            overlay.querySelectorAll('.add-img-orient-pill').forEach(p =>
                p.classList.toggle('active', p.dataset.orient === addImgOrientation));
            if (addImgQuery || addImgColor) searchAddImages();
        });
    });

    // Load More
    overlay.querySelector('.add-img-load-more-btn').addEventListener('click', () => {
        addImgPage++;
        searchAddImages(true);
    });

    // Upload
    const uploadBtn = overlay.querySelector('#addImgUploadBtn');
    const fileInput = overlay.querySelector('#addImgFileInput');
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        fileInput.value = '';
        for (const file of files) {
            await handleAddImageUpload(file);
        }
    });

    // Delegate result card clicks
    const resultsContainer = overlay.querySelector('#addImgResults');
    resultsContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.add-img-card');
        if (!card) return;
        toggleAddImageSelection(card.dataset.photoId);
    });
}

async function searchAddImages(append = false) {
    if (addImgLoading) return;
    if (!addImgQuery && !addImgColor) return;

    addImgLoading = true;
    if (!append) {
        addImgPage = 1;
        addImgResults = [];
    }
    updateAddImgResultsUI();

    try {
        const params = new URLSearchParams({
            q: addImgQuery || 'wallpaper',
            page: addImgPage,
            per_page: 30,
        });
        if (addImgColor) params.set('color', addImgColor);
        if (addImgOrientation) {
            const map = { horizontal: 'landscape', vertical: 'portrait', square: 'square' };
            params.set('orientation', map[addImgOrientation]);
        }

        const resp = await fetch(`/api/images/search?${params}`);
        if (!resp.ok) throw new Error(`Search failed (${resp.status})`);
        const data = await resp.json();

        const newResults = (data.results || []).map(photo => ({
            id: String(photo.id),
            url: photo.regularUrl || photo.fullUrl,
            thumbUrl: photo.thumbUrl || photo.smallUrl,
            smallUrl: photo.smallUrl,
            photographer: photo.photographer || 'Unknown',
            altText: photo.altText || addImgQuery,
            source: photo.source || 'stock',
            width: photo.width,
            height: photo.height,
            tags: Array.isArray(photo.tags) ? photo.tags : [],
        }));

        addImgResults = append ? [...addImgResults, ...newResults] : newResults;
        addImgTotalPages = data.total_pages || 1;
    } catch (err) {
        console.error('[AddImages] Search failed:', err);
        if (!append) addImgResults = [];
    } finally {
        addImgLoading = false;
        updateAddImgResultsUI();
        updateAddImgLoadMore();
    }
}

function updateAddImgResultsUI() {
    const grid = document.getElementById('addImgResults');
    if (!grid) return;
    grid.innerHTML = renderAddImagesResults();
}

function updateAddImgLoadMore() {
    const container = document.getElementById('addImgLoadMore');
    if (!container) return;
    container.style.display = (addImgResults.length > 0 && addImgPage < addImgTotalPages) ? 'block' : 'none';
    const btn = container.querySelector('.add-img-load-more-btn');
    if (btn) btn.disabled = addImgLoading;
}

function updateAddImgFooter() {
    const count = document.getElementById('addImgSelectedCount');
    if (count) count.textContent = `${addImgSelected.length} selected`;
}

function updateAddImgCardStates() {
    const overlay = document.getElementById('addImagesOverlay');
    if (!overlay) return;
    overlay.querySelectorAll('.add-img-card').forEach(card => {
        const id = card.dataset.photoId;
        const sel = addImgSelected.find(s => s.id === id);
        const isSelected = !!sel;
        card.classList.toggle('selected', isSelected);

        // Update badge
        let existingBadge = card.querySelector('.add-img-badge');
        if (isSelected) {
            if (!existingBadge) {
                existingBadge = document.createElement('span');
                existingBadge.className = 'add-img-badge';
                card.appendChild(existingBadge);
            }
            if (sel.downloaded) {
                existingBadge.className = 'add-img-badge downloaded';
                existingBadge.innerHTML = '&#10003;';
            } else {
                existingBadge.className = 'add-img-badge pending';
                existingBadge.innerHTML = '';
            }
        } else if (existingBadge) {
            existingBadge.remove();
        }

        // Update select button
        const btn = card.querySelector('.add-img-select-btn');
        if (btn) btn.innerHTML = isSelected ? '&#10003;' : '+';
    });
}

function toggleAddImageSelection(photoId) {
    const existingIdx = addImgSelected.findIndex(s => s.id === photoId);
    if (existingIdx >= 0) {
        addImgSelected.splice(existingIdx, 1);
    } else {
        const photo = addImgResults.find(r => r.id === photoId);
        if (!photo) return;
        const entry = {
            id: photo.id,
            url: photo.url,
            thumbUrl: photo.thumbUrl,
            photographer: photo.photographer,
            altText: photo.altText,
            source: photo.source,
            tags: photo.tags || [],
            downloaded: false,
        };
        addImgSelected.push(entry);
        // Auto-download
        _downloadAddImage(entry);
    }
    updateAddImgCardStates();
    updateAddImgFooter();
}

async function _downloadAddImage(entry) {
    try {
        const data = await apiFetch('/api/images/download', {
            method: 'POST',
            body: JSON.stringify({
                url: entry.url,
                alt_text: entry.altText || '',
                photographer: entry.photographer || '',
                source: entry.source || 'stock',
                tags: entry.tags || [],
            }),
        });
        const sel = addImgSelected.find(s => s.id === entry.id);
        if (sel) {
            sel.downloaded = true;
            sel.localUrl = data.url;
        }
        updateAddImgCardStates();
    } catch (err) {
        console.warn('[AddImages] Download failed:', err);
    }
}

async function handleAddImageUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const resp = await fetch('/api/images/upload', {
            method: 'POST',
            body: formData,
        });
        if (!resp.ok) throw new Error(`Upload failed (${resp.status})`);
        addImgSelected.push({
            id: 'upload_' + Date.now(),
            url: '',
            thumbUrl: '',
            photographer: 'Uploaded',
            altText: file.name.replace(/\.[^/.]+$/, ''),
            source: 'upload',
            downloaded: true,
        });
        updateAddImgFooter();
    } catch (err) {
        console.error('[AddImages] Upload failed:', err);
        await showMessageModal({ title: 'Upload failed', message: err.message });
    }
}
