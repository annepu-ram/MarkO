/**
 * Dashboard v2 — Full Campaign-First Dashboard
 * Views: Home, Campaigns, Sites, Media
 */

import { showConfirmModal, showMessageModal, showTextPrompt } from './promptModal.js';

let campaigns = [];
let sites = [];
let brands = [];
let products = [];
let mediaImages = [];
let mediaSearch = '';
let mediaUsageFilter = '';
let mediaSourceFilter = '';
let mediaStockResults = [];
let mediaViewMode = 'library';
let mediaStockProvider = '';
let mediaStockColor = '';
let mediaStockOrientation = '';
let mediaStockVisualType = '';
let mediaStockHasSearched = false;
let mediaStockPage = 1;
let mediaStockTotalPages = 0;
let mediaStockIsLoading = false;
let mediaStockResolvedProvider = '';
let activeMediaAssetId = null;
let contentItems = [];
let contentFolders = [];
let brandOptions = { color_palettes: [], fonts: [], theme_categories: [], themes: [], tones: [] };
let activeBrandId = null;
let editingBrandId = null;
let brandEditorMode = 'edit';
let currentView = 'home';
let campaignFilter = 'all';
let contentFilter = 'all';
let contentSearch = '';
let contentBrandFilter = '';
let contentProductFilter = '';
let contentFolderFilter = '';
let selectedContentFolderId = '';
let editingContentId = null;
let contentStatusFilter = '';
let contentSourceFilter = '';
let contentOptions = {
    content_types: [],
    content_type_families: [],
};
let contentOptionsLoaded = false;
let contentFoldersLoaded = false;
let activeSiteId = null;
let productSearch = '';
let productBrandFilter = '';
// Sections (live-binding compositions of content items)
let sectionItems = [];
let sectionsLoaded = false;
let sectionSearch = '';
let sectionBrandFilter = '';
let sectionStatusFilter = '';
let editingSectionId = null;       // null = creating a new section
let sectionDraftRefs = [];         // ordered content_item ids in the editor
let sectionPickerItems = [];       // content items available to add
let sectionPickerSearch = '';
let sectionTypes = [];
let sectionTypesLoaded = false;

// =============================================================================
// API
// =============================================================================

async function apiFetch(url, options = {}) {
    const token = document.querySelector('meta[name="ai-request-token"]')?.content || '';
    const res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'SwiftSitesApp',
            'X-AI-Request-Token': token,
            ...(options.headers || {}),
        },
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Request failed' }));
        const message = err.message || (typeof err.error === 'string' ? err.error : '') || `HTTP ${res.status}`;
        throw new Error(message);
    }
    return res.json();
}

// =============================================================================
// Init
// =============================================================================

async function init() {
    bindNavigation();
    bindModals();
    bindQuickCards();
    bindNewCampaignModal();
    bindBrandKit();
    bindContentFilters();
    bindAddContent();
    bindContentTabs();
    bindSections();
    bindSectionPreviewModal();
    bindBrandSitePreviewModal();
    bindAddProduct();
    await Promise.all([loadCampaigns(), loadSites(), loadBrands(), loadProducts(), loadBrandOptions(), loadContentOptions()]);
    renderHomeView();
}

// =============================================================================
// Navigation
// =============================================================================

function bindNavigation() {
    const toggle = document.getElementById('dashMenuToggle');
    const nav = document.getElementById('dashNav');
    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', String(open));
        });
    }

    document.querySelectorAll('.dash-nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchView(btn.dataset.view);
            nav?.classList.remove('open');
            toggle?.setAttribute('aria-expanded', 'false');
        });
    });

    document.addEventListener('click', (e) => {
        const viewBtn = e.target.closest('[data-switch-view]');
        if (viewBtn) switchView(viewBtn.dataset.switchView);
    });
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.dash-nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    document.querySelectorAll('.dash-view').forEach(el => {
        el.classList.toggle('active', el.dataset.view === view);
    });

    if (view === 'home') renderHomeView();
    if (view === 'campaigns') renderCampaignsView();
    if (view === 'products') renderProductsView();
    if (view === 'sites') renderSitesView();
    if (view === 'brands') return loadBrandView();
    if (view === 'content') loadContentView();
    if (view === 'media') renderMediaView();
}

// =============================================================================
// Data Loading
// =============================================================================

async function loadCampaigns() {
    try {
        campaigns = await apiFetch('/api/campaigns');
    } catch (e) {
        console.error('Failed to load campaigns:', e);
        campaigns = [];
    }
}

async function loadSites() {
    try {
        sites = await apiFetch('/api/sites');
    } catch (e) {
        console.error('Failed to load sites:', e);
        sites = [];
    }
}

async function loadBrands() {
    try {
        brands = await apiFetch('/api/brands');
        if (!activeBrandId && brands.length) {
            const defaultBrand = brands.find(b => b.is_default) || brands[0];
            activeBrandId = defaultBrand.id;
        }
    } catch (e) {
        console.error('Failed to load brands:', e);
        brands = [];
    }
}

async function loadProducts() {
    try {
        products = await apiFetch('/api/products');
    } catch (e) {
        console.error('Failed to load products:', e);
        products = [];
    }
}

async function loadBrandOptions() {
    try {
        brandOptions = await apiFetch('/api/brands/options');
    } catch (e) {
        console.error('Failed to load brand options:', e);
        brandOptions = { color_palettes: [], fonts: [], theme_categories: [], themes: [], tones: [] };
    }
}

async function loadContentOptions() {
    if (contentOptionsLoaded) return;
    try {
        contentOptions = await apiFetch('/api/content/options');
        contentOptionsLoaded = true;
    } catch (e) {
        console.error('Failed to load content options:', e);
        contentOptions = { content_types: [], content_type_families: [] };
        contentOptionsLoaded = true;
    }
}

async function loadContentFolders() {
    if (contentFoldersLoaded) return;
    try {
        contentFolders = await apiFetch('/api/content/folders');
        contentFoldersLoaded = true;
    } catch (e) {
        console.error('Failed to load content folders:', e);
        contentFolders = [];
        contentFoldersLoaded = true;
    }
}

// =============================================================================
// HOME VIEW
// =============================================================================

function renderHomeView() {
    renderHomeHero();
    renderDraftsSection();
    renderLiveSection();
    renderRecentSites();
}

function renderHomeHero() {
    const hasBrands = brands.length > 0;
    const title = document.getElementById('dashHeroTitle');
    const subtitle = document.getElementById('dashHeroSubtitle');
    const ctaText = document.getElementById('dashHeroCtaText');
    const quickStart = document.getElementById('dashQuickStartSection');

    if (!title || !subtitle || !ctaText) return;

    if (hasBrands) {
        title.textContent = 'What do you want to promote?';
        subtitle.textContent = "Start a campaign and we'll help you craft messages and build a landing page that converts.";
        ctaText.textContent = 'Start a campaign';
        if (quickStart) quickStart.style.display = '';
        return;
    }

    title.textContent = 'Create your first brand';
    subtitle.textContent = 'Campaigns need a brand voice, colors, fonts, and reusable rules before AI can create reliable marketing content.';
    ctaText.textContent = 'Create brand';
    if (quickStart) quickStart.style.display = 'none';
}

function renderDraftsSection() {
    const drafts = campaigns.filter(c => c.status === 'draft');
    const section = document.getElementById('dashDraftsSection');

    if (!drafts.length) {
        section.style.display = 'none';
        return;
    }

    section.style.display = '';
    document.getElementById('dashDraftsList').innerHTML = drafts.slice(0, 5).map(c => renderDraftCard(c)).join('');
    bindCampaignCardEvents(document.getElementById('dashDraftsList'));
}

function renderLiveSection() {
    const live = campaigns.filter(c => c.status === 'active' || c.status === 'completed');
    const section = document.getElementById('dashLiveSection');

    if (!live.length) {
        section.style.display = 'none';
        return;
    }

    section.style.display = '';
    document.getElementById('dashLiveList').innerHTML = live.slice(0, 5).map(c => renderLiveCard(c)).join('');
    bindCampaignCardEvents(document.getElementById('dashLiveList'));
}

function renderRecentSites() {
    const section = document.getElementById('dashRecentSitesSection');
    const recentSites = sites.slice(0, 4);

    if (!recentSites.length) {
        section.style.display = 'none';
        return;
    }

    section.style.display = '';
    document.getElementById('dashRecentSites').innerHTML = recentSites.map(s => {
        const badge = s.status === 'published'
            ? '<span class="dash-site-badge dash-site-badge--published">Published</span>'
            : '<span class="dash-site-badge dash-site-badge--draft">Draft</span>';
        return `<a href="/editor/${s.id}" class="dash-site-compact-card">
            <div class="dash-site-compact-info">
                <span class="dash-site-compact-name">${escHtml(s.name)}</span>
                <span class="dash-site-compact-meta">${s.page_count} page${s.page_count !== 1 ? 's' : ''} · ${formatRelativeTime(s.updated_at)}</span>
            </div>
            ${badge}
        </a>`;
    }).join('');
}

// =============================================================================
// Campaign Cards — with next-action intelligence
// =============================================================================

function getNextAction(campaign) {
    if (!campaign.goal) return { label: 'Set goal', step: 2 };
    return { label: 'Continue editing', step: 0 };
}

// Resolve which products/services a campaign targets, into a short label.
function campaignTargetingLabel(c) {
    const ids = c.product_ids || [];
    if (!ids.length) return { generic: true, text: 'Generic' };
    const names = ids
        .map(id => (products.find(p => p.id === id) || {}).name)
        .filter(Boolean);
    if (!names.length) return { generic: false, text: `${ids.length} product${ids.length !== 1 ? 's' : ''}` };
    if (names.length <= 2) return { generic: false, text: names.join(', ') };
    return { generic: false, text: `${names.slice(0, 2).join(', ')} +${names.length - 2}` };
}

const CAMPAIGN_GOAL_ICON = {
    leads: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 7 a4 4 0 1 0 0 0',
};

function campaignStatusMeta(status) {
    if (status === 'active') return { cls: '--active', label: 'Active' };
    if (status === 'completed') return { cls: '--completed', label: 'Completed' };
    if (status === 'paused') return { cls: '--draft', label: 'Paused' };
    return { cls: '--draft', label: 'Draft' };
}

// Unified rich campaign card. variant: 'draft' | 'live'.
function renderCampaignCard(c, variant) {
    const timeAgo = formatRelativeTime(c.updated_at);
    const status = campaignStatusMeta(c.status);
    const goalLabel = c.goal ? capitalize(c.goal) : null;
    const brandName = c.brand && c.brand.name ? c.brand.name : null;
    const target = campaignTargetingLabel(c);

    const chips = [];
    if (brandName) {
        chips.push(`<span class="dash-campaign-chip dash-campaign-chip--brand" title="Brand">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>
            ${escHtml(brandName)}</span>`);
    }
    if (goalLabel) {
        chips.push(`<span class="dash-campaign-chip dash-campaign-chip--goal" title="Goal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
            ${escHtml(goalLabel)}</span>`);
    }
    chips.push(`<span class="dash-campaign-chip dash-campaign-chip--target${target.generic ? ' dash-campaign-chip--generic' : ''}" title="${target.generic ? 'Generic campaign' : 'Targets'}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>
        ${target.generic ? 'Generic' : escHtml(target.text)}</span>`);
    if (c.site_id) {
        chips.push(`<span class="dash-campaign-chip dash-campaign-chip--page" title="Has landing page">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/></svg>
            Page</span>`);
    }

    let footer;
    if (variant === 'live') {
        footer = `
            <button class="dash-btn dash-btn--primary dash-btn--sm" data-action="open" data-id="${c.id}">View</button>
            ${c.site_id ? `<a href="/editor/${c.site_id}" class="dash-btn dash-btn--ghost dash-btn--sm">Edit page</a>` : ''}`;
    } else {
        const action = getNextAction(c);
        footer = `
            <button class="dash-btn dash-btn--primary dash-btn--sm" data-action="open" data-id="${c.id}">${escHtml(action.label)}</button>
            <button class="dash-btn dash-btn--ghost dash-btn--sm dash-btn--icon" data-action="delete" data-id="${c.id}" title="Delete">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>`;
    }

    return `<div class="dash-campaign-card dash-campaign-card--rich" data-id="${c.id}">
        <div class="dash-campaign-card-head">
            <span class="dash-campaign-name">${escHtml(c.name)}</span>
            <span class="dash-campaign-status dash-campaign-status${status.cls}">${status.label}</span>
        </div>
        <div class="dash-campaign-attrs">${chips.join('')}</div>
        <div class="dash-campaign-foot">
            <span class="dash-campaign-time">${timeAgo}</span>
            <div class="dash-campaign-actions">${footer}</div>
        </div>
    </div>`;
}

function renderDraftCard(c) {
    return renderCampaignCard(c, 'draft');
}

function renderLiveCard(c) {
    return renderCampaignCard(c, 'live');
}

function bindCampaignCardEvents(container) {
    container.querySelectorAll('[data-action="open"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            window.location.href = `/campaign-studio/${btn.dataset.id}`;
        });
    });

    container.querySelectorAll('[data-action="delete"]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const confirmed = await showConfirmModal({
                title: 'Delete campaign',
                message: 'Delete this campaign? This cannot be undone.',
                confirmText: 'Delete',
                danger: true,
            });
            if (!confirmed) return;
            try {
                await apiFetch(`/api/campaigns/${btn.dataset.id}`, { method: 'DELETE' });
                campaigns = campaigns.filter(c => c.id !== btn.dataset.id);
                renderHomeView();
                if (currentView === 'campaigns') renderCampaignsView();
            } catch (err) {
                await showMessageModal({ title: 'Delete failed', message: err.message });
            }
        });
    });
}

// =============================================================================
// CAMPAIGNS VIEW (full list with filters)
// =============================================================================

function renderCampaignsView() {
    bindCampaignFilters();
    renderFilteredCampaigns();
}

function bindCampaignFilters() {
    const pills = document.getElementById('campaignFilterPills');
    pills.querySelectorAll('.dash-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            pills.querySelectorAll('.dash-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            campaignFilter = pill.dataset.filter;
            renderFilteredCampaigns();
        });
    });

    document.getElementById('newCampaignBtn').addEventListener('click', () => createCampaign());
}

function renderFilteredCampaigns() {
    const container = document.getElementById('dashCampaignsFull');
    let filtered = campaigns;

    if (campaignFilter !== 'all') {
        filtered = campaigns.filter(c => c.status === campaignFilter);
    }

    if (!filtered.length) {
        container.innerHTML = `<div class="dash-empty-state">
            <p class="dash-empty-text">${campaignFilter === 'all' ? 'No campaigns yet. Start one above!' : `No ${campaignFilter} campaigns.`}</p>
        </div>`;
        return;
    }

    container.innerHTML = filtered.map(c => {
        if (c.status === 'draft') return renderDraftCard(c);
        return renderLiveCard(c);
    }).join('');

    bindCampaignCardEvents(container);
}

// =============================================================================
// Quick Start + Campaign Creation
// =============================================================================

function bindQuickCards() {
    document.getElementById('startCampaignBtn').addEventListener('click', () => {
        if (!brands.length) {
            openCreateBrandModal();
            return;
        }
        createCampaign();
    });

    document.querySelectorAll('.dash-quick-card').forEach(card => {
        card.addEventListener('click', () => createCampaign(card.dataset.goal));
    });
}

// Pending goal for the campaign being named in the modal.
let pendingCampaignGoal = null;

const GOAL_LABELS = {
    leads: 'Leads', sales: 'Sales', signups: 'Signups',
    calls: 'Calls', traffic: 'Traffic', inform: 'Info',
};

function suggestCampaignName(goal) {
    // Structured starter: (Mon-Year)-(Goal). Channels/audience/products are
    // added later in the studio where they're known. Keeps names sortable.
    const now = new Date();
    const mon = now.toLocaleString('en-US', { month: 'short' });
    const year = now.getFullYear();
    const brand = brands.find(b => b.is_default) || brands[0];
    const parts = [`${mon}-${year}`];
    if (brand && brand.name) parts.push(brand.name);
    if (goal && GOAL_LABELS[goal]) parts.push(GOAL_LABELS[goal]);
    parts.push('Campaign');
    return parts.join(' ');
}

async function createCampaign(goal) {
    if (!brands.length) {
        await openCreateBrandModal();
        return;
    }
    pendingCampaignGoal = goal || null;
    openNewCampaignModal();
}

function openNewCampaignModal() {
    const modal = document.getElementById('newCampaignModal');
    const input = document.getElementById('newCampaignName');
    const confirm = document.getElementById('confirmNewCampaign');
    const error = document.getElementById('newCampaignError');
    const suggestionWrap = document.getElementById('newCampaignSuggestion');
    const suggestionChip = document.getElementById('newCampaignSuggestionChip');
    if (!modal) return;

    input.value = '';
    confirm.disabled = true;
    error.style.display = 'none';

    const suggestion = suggestCampaignName(pendingCampaignGoal);
    if (suggestion && suggestionWrap && suggestionChip) {
        suggestionChip.textContent = suggestion;
        suggestionWrap.style.display = '';
    }

    modal.style.display = '';
    input.focus();
}

async function submitNewCampaign() {
    const input = document.getElementById('newCampaignName');
    const error = document.getElementById('newCampaignError');
    const confirm = document.getElementById('confirmNewCampaign');
    const name = (input.value || '').trim();
    if (!name) {
        error.textContent = 'Please enter a campaign name.';
        error.style.display = '';
        return;
    }
    confirm.disabled = true;
    confirm.textContent = 'Creating...';
    try {
        const body = { name };
        if (pendingCampaignGoal) body.goal = pendingCampaignGoal;
        const defaultBrand = brands.find(b => b.is_default) || brands[0];
        if (defaultBrand) body.brand_id = defaultBrand.id;
        const campaign = await apiFetch('/api/campaigns', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        window.location.href = `/campaign-studio/${campaign.id}`;
    } catch (e) {
        error.textContent = e.message || 'Failed to create campaign.';
        error.style.display = '';
        confirm.disabled = false;
        confirm.textContent = 'Continue';
    }
}

function bindNewCampaignModal() {
    const modal = document.getElementById('newCampaignModal');
    const input = document.getElementById('newCampaignName');
    const confirm = document.getElementById('confirmNewCampaign');
    const cancel = document.getElementById('cancelNewCampaign');
    const suggestionChip = document.getElementById('newCampaignSuggestionChip');
    if (!modal) return;

    input.addEventListener('input', () => {
        confirm.disabled = !input.value.trim();
    });
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && input.value.trim()) submitNewCampaign();
    });
    if (suggestionChip) {
        suggestionChip.addEventListener('click', () => {
            input.value = suggestionChip.textContent;
            confirm.disabled = false;
            input.focus();
        });
    }
    confirm.addEventListener('click', submitNewCampaign);
    cancel.addEventListener('click', () => { modal.style.display = 'none'; });
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });
}

// =============================================================================
// PRODUCTS VIEW
// =============================================================================

function renderProductsView() {
    populateProductBrandFilter();
    renderProductsGrid();
    bindProductFilters();
}

function populateProductBrandFilter() {
    const select = document.getElementById('productBrandFilter');
    if (!select) return;
    const current = select.value;
    select.innerHTML = '<option value="">All brands</option>' + brands.map(b =>
        `<option value="${b.id}">${escHtml(b.name)}</option>`
    ).join('');
    select.value = current;
}

function bindProductFilters() {
    const search = document.getElementById('productSearch');
    const brandFilter = document.getElementById('productBrandFilter');
    if (search && !search.dataset.bound) {
        search.dataset.bound = 'true';
        search.addEventListener('input', () => {
            productSearch = search.value.trim().toLowerCase();
            renderProductsGrid();
        });
    }
    if (brandFilter && !brandFilter.dataset.bound) {
        brandFilter.dataset.bound = 'true';
        brandFilter.addEventListener('change', () => {
            productBrandFilter = brandFilter.value;
            renderProductsGrid();
        });
    }
}

function renderProductsGrid() {
    const grid = document.getElementById('dashProductsGrid');
    if (!grid) return;

    let visible = products.filter(p => p.status !== 'archived');
    if (productSearch) {
        visible = visible.filter(p =>
            (p.name || '').toLowerCase().includes(productSearch) ||
            (p.short_description || '').toLowerCase().includes(productSearch) ||
            (p.sku || '').toLowerCase().includes(productSearch)
        );
    }
    if (productBrandFilter) {
        visible = visible.filter(p => (p.brand_ids || []).includes(productBrandFilter));
    }

    if (!visible.length) {
        grid.innerHTML = '<div class="dash-empty-state"><p class="dash-empty-text">No products yet. Add products so campaigns can reuse accurate product data.</p></div>';
        return;
    }

    grid.innerHTML = visible.map(product => {
        const brandNames = (product.brands || []).map(b => b.name).join(', ') || 'No brand tags';
        const price = product.price !== null && product.price !== undefined
            ? `${product.currency || 'USD'} ${product.price}`
            : 'No price';
        const image = product.default_image_url
            ? `<img src="${escAttr(product.default_image_url)}" alt="${escAttr(product.name)}" loading="lazy">`
            : '<div class="dash-product-image-empty">Product</div>';
        return `<div class="dash-product-card" data-product-id="${product.id}">
            <div class="dash-product-image">${image}</div>
            <div class="dash-product-body">
                <div class="dash-product-top">
                    <h4 class="dash-product-name">${escHtml(product.name)}</h4>
                    <span class="dash-content-category">${escHtml(product.product_type)}</span>
                </div>
                <p class="dash-product-desc">${escHtml(product.short_description || 'No description yet.')}</p>
                <div class="dash-product-meta">
                    <span>${escHtml(brandNames)}</span>
                    <span>${escHtml(price)}</span>
                    <span>${escHtml(product.availability || '')}</span>
                </div>
            </div>
        </div>`;
    }).join('');
}

// =============================================================================
// SITES VIEW (full management)
// =============================================================================

function renderSitesView() {
    const grid = document.getElementById('dashSitesGrid');

    if (!sites.length) {
        grid.innerHTML = '<div class="dash-empty-state"><p class="dash-empty-text">No websites yet. Create one to get started, or start a campaign to generate one automatically.</p></div>';
        return;
    }

    grid.innerHTML = sites.map(site => {
        const badgeClass = site.status === 'published' ? '--published' : '--draft';
        const publishedAt = site.published_at ? formatRelativeTime(site.published_at) : null;

        return `<div class="dash-site-card" data-site-id="${site.id}">
            <div class="dash-site-card-top">
                <h4 class="dash-site-name">${escHtml(site.name)}</h4>
                <span class="dash-site-badge dash-site-badge${badgeClass}">${site.status}</span>
            </div>
            <p class="dash-site-slug">/${site.slug}</p>
            <div class="dash-site-meta">
                <span class="dash-site-pages">${site.page_count} page${site.page_count !== 1 ? 's' : ''}</span>
                ${site.version_count ? `<span class="dash-site-versions">${site.version_count} version${site.version_count !== 1 ? 's' : ''}</span>` : ''}
                ${publishedAt ? `<span class="dash-site-published">Published ${publishedAt}</span>` : ''}
            </div>
            <div class="dash-site-actions">
                <a href="/editor/${site.id}" class="dash-btn dash-btn--primary dash-btn--sm">Edit</a>
                ${site.status === 'draft'
                    ? `<button class="dash-btn dash-btn--primary dash-btn--sm" data-publish-site="${site.id}">Publish</button>`
                    : `<button class="dash-btn dash-btn--primary dash-btn--sm" data-unpublish-site="${site.id}">Unpublish</button>`
                }
                <button class="dash-btn dash-btn--ghost dash-btn--sm" data-settings-site="${site.id}">Settings</button>
                <button class="dash-btn dash-btn--ghost dash-btn--sm dash-btn--danger" data-delete-site="${site.id}">Delete</button>
            </div>
        </div>`;
    }).join('');

    bindSiteActions(grid);
}

function bindSiteActions(container) {
    container.querySelectorAll('[data-delete-site]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const confirmed = await showConfirmModal({
                title: 'Delete site',
                message: 'Delete this site and all its pages? This cannot be undone.',
                confirmText: 'Delete',
                danger: true,
            });
            if (!confirmed) return;
            try {
                await apiFetch(`/api/sites/${btn.dataset.deleteSite}`, { method: 'DELETE' });
                sites = sites.filter(s => s.id !== btn.dataset.deleteSite);
                renderSitesView();
                renderRecentSites();
            } catch (err) {
                await showMessageModal({ title: 'Delete failed', message: err.message });
            }
        });
    });

    container.querySelectorAll('[data-publish-site]').forEach(btn => {
        btn.addEventListener('click', async () => {
            try {
                btn.disabled = true;
                btn.textContent = 'Publishing...';
                await apiFetch(`/api/sites/${btn.dataset.publishSite}/publish`, { method: 'POST' });
                await loadSites();
                renderSitesView();
                renderRecentSites();
            } catch (err) {
                await showMessageModal({ title: 'Publish failed', message: err.message });
                btn.disabled = false;
                btn.textContent = 'Publish';
            }
        });
    });

    container.querySelectorAll('[data-unpublish-site]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const confirmed = await showConfirmModal({
                title: 'Unpublish site',
                message: 'Unpublish this site? It will no longer be publicly accessible.',
                confirmText: 'Unpublish',
            });
            if (!confirmed) return;
            try {
                await apiFetch(`/api/sites/${btn.dataset.unpublishSite}/unpublish`, { method: 'POST' });
                await loadSites();
                renderSitesView();
                renderRecentSites();
            } catch (err) {
                await showMessageModal({ title: 'Unpublish failed', message: err.message });
            }
        });
    });

    container.querySelectorAll('[data-settings-site]').forEach(btn => {
        btn.addEventListener('click', () => openSiteSettings(btn.dataset.settingsSite));
    });
}

// =============================================================================
// Site Settings Modal
// =============================================================================

async function openSiteSettings(siteId) {
    activeSiteId = siteId;
    const modal = document.getElementById('siteSettingsModal');
    const body = document.getElementById('siteSettingsBody');

    try {
        const settings = await apiFetch(`/api/sites/${siteId}/settings`);
        body.innerHTML = `
            <div class="dash-settings-group">
                <h4 class="dash-settings-group-title">SEO</h4>
                <div class="dash-field">
                    <label class="dash-label">Title template</label>
                    <input class="dash-input" id="settTitleTemplate" value="${escAttr(settings.seo?.titleTemplate || '')}">
                    <span class="dash-hint">Use {pageTitle} and {siteName} as placeholders</span>
                </div>
                <div class="dash-field">
                    <label class="dash-label">Meta description</label>
                    <textarea class="dash-input" id="settMetaDesc" rows="2">${escHtml(settings.seo?.metaDescription || '')}</textarea>
                </div>
            </div>
            <div class="dash-settings-group">
                <h4 class="dash-settings-group-title">Branding</h4>
                <div class="dash-field">
                    <label class="dash-label">Site name</label>
                    <input class="dash-input" id="settSiteName" value="${escAttr(settings.branding?.siteName || '')}">
                </div>
                <div class="dash-field">
                    <label class="dash-label">Favicon URL</label>
                    <input class="dash-input" id="settFavicon" value="${escAttr(settings.branding?.faviconUrl || '')}" placeholder="https://...">
                </div>
            </div>
            <div class="dash-settings-group">
                <h4 class="dash-settings-group-title">Social</h4>
                <div class="dash-field">
                    <label class="dash-label">Twitter handle</label>
                    <input class="dash-input" id="settTwitter" value="${escAttr(settings.social?.twitterHandle || '')}" placeholder="@handle">
                </div>
                <div class="dash-field">
                    <label class="dash-label">Facebook page</label>
                    <input class="dash-input" id="settFacebook" value="${escAttr(settings.social?.facebookPage || '')}" placeholder="https://facebook.com/...">
                </div>
            </div>
        `;
        modal.style.display = '';
    } catch (e) {
        await showMessageModal({ title: 'Failed to load settings', message: e.message });
    }
}

function bindSettingsModal() {
    const modal = document.getElementById('siteSettingsModal');

    document.getElementById('cancelSettings').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    document.getElementById('saveSettings').addEventListener('click', async () => {
        if (!activeSiteId) return;
        const settings = {
            seo: {
                titleTemplate: document.getElementById('settTitleTemplate').value,
                metaDescription: document.getElementById('settMetaDesc').value,
            },
            branding: {
                siteName: document.getElementById('settSiteName').value,
                faviconUrl: document.getElementById('settFavicon').value,
            },
            social: {
                twitterHandle: document.getElementById('settTwitter').value,
                facebookPage: document.getElementById('settFacebook').value,
            },
        };

        try {
            await apiFetch(`/api/sites/${activeSiteId}/settings`, {
                method: 'PUT',
                body: JSON.stringify(settings),
            });
            modal.style.display = 'none';
        } catch (e) {
            await showMessageModal({ title: 'Failed to save', message: e.message });
        }
    });
}

// =============================================================================
// MEDIA VIEW
// =============================================================================

function renderMediaView() {
    bindMediaControls();
    syncMediaControls();
    setMediaViewMode(mediaViewMode);
}

function bindMediaControls() {
    const searchInput = document.getElementById('dashMediaSearchInput');
    const searchBtn = document.getElementById('dashMediaSearchBtn');
    const usageFilter = document.getElementById('dashMediaUsageFilter');
    const sourceFilter = document.getElementById('dashMediaSourceFilter');
    const uploadBtn = document.getElementById('dashMediaUploadBtn');
    const uploadInput = document.getElementById('dashMediaUploadInput');
    const stockInput = document.getElementById('dashMediaStockQuery');
    const stockBtn = document.getElementById('dashMediaStockSearchBtn');
    const stockGrid = document.getElementById('dashMediaStockGrid');
    const stockLoadMoreBtn = document.getElementById('dashMediaStockLoadMoreBtn');
    const stockOpenBtn = document.getElementById('dashMediaStockOpenBtn');
    const stockBackBtn = document.getElementById('dashMediaStockBackBtn');
    const grid = document.getElementById('dashMediaGrid');
    const metadataModal = document.getElementById('mediaMetadataModal');
    const metadataCancel = document.getElementById('cancelMediaMetadata');
    const metadataSave = document.getElementById('saveMediaMetadata');

    if (searchInput && !searchInput.dataset.bound) {
        searchInput.dataset.bound = 'true';
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                mediaSearch = searchInput.value.trim();
                loadOrgMedia();
            }
        });
    }
    if (searchBtn && !searchBtn.dataset.bound) {
        searchBtn.dataset.bound = 'true';
        searchBtn.addEventListener('click', () => {
            mediaSearch = searchInput?.value.trim() || '';
            loadOrgMedia();
        });
    }
    if (usageFilter && !usageFilter.dataset.bound) {
        usageFilter.dataset.bound = 'true';
        usageFilter.addEventListener('change', () => {
            mediaUsageFilter = usageFilter.value;
            loadOrgMedia();
        });
    }
    if (sourceFilter && !sourceFilter.dataset.bound) {
        sourceFilter.dataset.bound = 'true';
        sourceFilter.addEventListener('change', () => {
            mediaSourceFilter = sourceFilter.value;
            loadOrgMedia();
        });
    }
    if (uploadBtn && uploadInput && !uploadBtn.dataset.bound) {
        uploadBtn.dataset.bound = 'true';
        uploadBtn.addEventListener('click', () => uploadInput.click());
        uploadInput.addEventListener('change', () => uploadMediaFile(uploadInput));
    }
    if (stockInput && !stockInput.dataset.bound) {
        stockInput.dataset.bound = 'true';
        stockInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') searchMediaStockImages();
        });
    }
    if (stockBtn && !stockBtn.dataset.bound) {
        stockBtn.dataset.bound = 'true';
        stockBtn.addEventListener('click', searchMediaStockImages);
    }
    if (stockLoadMoreBtn && !stockLoadMoreBtn.dataset.bound) {
        stockLoadMoreBtn.dataset.bound = 'true';
        stockLoadMoreBtn.addEventListener('click', () => searchMediaStockImages({ loadMore: true }));
    }
    bindStockOptionGroups();
    if (stockGrid && !stockGrid.dataset.bound) {
        stockGrid.dataset.bound = 'true';
        stockGrid.addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-import-stock-media]');
            if (!btn) return;
            await importStockMediaImage(Number(btn.dataset.importStockMedia), btn);
        });
    }
    if (stockOpenBtn && !stockOpenBtn.dataset.bound) {
        stockOpenBtn.dataset.bound = 'true';
        stockOpenBtn.addEventListener('click', () => {
            setMediaViewMode('stock');
            stockInput?.focus();
        });
    }
    if (stockBackBtn && !stockBackBtn.dataset.bound) {
        stockBackBtn.dataset.bound = 'true';
        stockBackBtn.addEventListener('click', () => {
            setMediaViewMode('library');
        });
    }
    if (grid && !grid.dataset.bound) {
        grid.dataset.bound = 'true';
        grid.addEventListener('click', async (e) => {
            const editBtn = e.target.closest('[data-edit-media]');
            if (editBtn) {
                openMediaMetadataModal(editBtn.dataset.editMedia);
                return;
            }
            const btn = e.target.closest('[data-delete-media]');
            if (!btn) return;
            await deleteMediaAsset(btn.dataset.deleteMedia);
        });
    }
    if (metadataCancel && metadataModal && !metadataCancel.dataset.bound) {
        metadataCancel.dataset.bound = 'true';
        metadataCancel.addEventListener('click', closeMediaMetadataModal);
    }
    if (metadataSave && metadataModal && !metadataSave.dataset.bound) {
        metadataSave.dataset.bound = 'true';
        metadataSave.addEventListener('click', saveMediaMetadata);
    }
}

function syncMediaControls() {
    const searchInput = document.getElementById('dashMediaSearchInput');
    const usageFilter = document.getElementById('dashMediaUsageFilter');
    const sourceFilter = document.getElementById('dashMediaSourceFilter');
    if (searchInput) searchInput.value = mediaSearch;
    if (usageFilter) usageFilter.value = mediaUsageFilter;
    if (sourceFilter) sourceFilter.value = mediaSourceFilter;
    syncStockOptionGroups();
}

function bindStockOptionGroups() {
    document.querySelectorAll('[data-stock-filter]').forEach(group => {
        if (group.dataset.bound) return;
        group.dataset.bound = 'true';
        group.addEventListener('click', (e) => {
            const btn = e.target.closest('.dash-stock-option');
            if (!btn || btn.disabled) return;
            const value = btn.dataset.value || '';
            if (group.dataset.stockFilter === 'provider') mediaStockProvider = value;
            if (group.dataset.stockFilter === 'color') mediaStockColor = value;
            if (group.dataset.stockFilter === 'orientation') mediaStockOrientation = value;
            if (group.dataset.stockFilter === 'visualType') mediaStockVisualType = value;
            syncStockOptionGroups();
        });
    });
}

function syncStockOptionGroups() {
    if (mediaStockProvider === 'pexels' && isPixabayOnlyVisualType(mediaStockVisualType)) {
        mediaStockVisualType = '';
    }
    const values = {
        provider: mediaStockProvider,
        color: mediaStockColor,
        orientation: mediaStockOrientation,
        visualType: mediaStockVisualType,
    };
    document.querySelectorAll('[data-stock-filter]').forEach(group => {
        const current = values[group.dataset.stockFilter] || '';
        group.querySelectorAll('.dash-stock-option').forEach(btn => {
            const isActive = (btn.dataset.value || '') === current;
            const isDisabled = group.dataset.stockFilter === 'visualType'
                && mediaStockProvider === 'pexels'
                && btn.dataset.pixabayOnly === 'true';
            btn.disabled = isDisabled;
            btn.classList.toggle('is-disabled', isDisabled);
            btn.setAttribute('aria-disabled', String(isDisabled));
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-pressed', String(isActive));
        });
    });
}

function isPixabayOnlyVisualType(value) {
    return value === 'vector' || value === 'illustration';
}

function setMediaViewMode(mode) {
    mediaViewMode = mode === 'stock' ? 'stock' : 'library';
    const libraryView = document.getElementById('dashMediaLibraryView');
    const stockView = document.getElementById('dashMediaStockView');
    if (libraryView) libraryView.style.display = mediaViewMode === 'library' ? '' : 'none';
    if (stockView) stockView.style.display = mediaViewMode === 'stock' ? '' : 'none';

    if (mediaViewMode === 'library') {
        const grid = document.getElementById('dashMediaGrid');
        if (grid) grid.innerHTML = '<p class="dash-empty-text">Loading...</p>';
        loadOrgMedia();
    } else {
        renderMediaStockResults();
    }
}

async function loadOrgMedia() {
    const grid = document.getElementById('dashMediaGrid');

    try {
        const params = new URLSearchParams();
        if (mediaSearch) params.set('q', mediaSearch);
        if (mediaUsageFilter) params.set('usage', mediaUsageFilter);
        if (mediaSourceFilter) params.set('source', mediaSourceFilter);

        const data = await apiFetch(`/api/media${params.toString() ? `?${params}` : ''}`);
        mediaImages = Array.isArray(data) ? data : (data.images || []);
        renderMediaSummary(data.stats || {});
        if (!mediaImages.length) {
            grid.innerHTML = '<p class="dash-empty-text">No media matches these filters. Upload assets or import stock images into the library.</p>';
            return;
        }

        grid.innerHTML = mediaImages.map(renderMediaCard).join('');
    } catch (e) {
        grid.innerHTML = '<p class="dash-empty-text">Failed to load media.</p>';
    }
}

function renderMediaSummary(stats = {}) {
    const summary = document.getElementById('dashMediaSummary');
    if (!summary) return;
    const total = mediaImages.length;
    const used = stats.used || 0;
    const unused = stats.unused || 0;
    const sources = stats.sources || {};
    const sourceText = Object.entries(sources)
        .map(([source, count]) => `${sourceLabel(source)} ${count}`)
        .join(' / ') || 'No sources yet';

    summary.innerHTML = `
        <div class="dash-media-stat"><strong>${total}</strong><span>Total assets</span></div>
        <div class="dash-media-stat"><strong>${used}</strong><span>Used</span></div>
        <div class="dash-media-stat"><strong>${unused}</strong><span>Unused</span></div>
        <div class="dash-media-stat dash-media-stat--wide"><strong>${escHtml(sourceText)}</strong><span>Sources</span></div>
    `;
}

function renderMediaCard(img) {
    const url = img.url || `/uploads/${img.storage_path || img.filename || ''}`;
    const label = img.original_name || img.alt_text || img.filename || 'Untitled image';
    const tags = Array.isArray(img.tags) ? img.tags.slice(0, 3) : [];
    const usageTitle = (img.usage_labels || []).join(', ') || 'No current references detected';
    return `
        <div class="dash-media-card" data-id="${escAttr(img.id)}">
            <div class="dash-media-thumb">
                <img src="${escAttr(url)}" alt="${escAttr(img.alt_text || label)}" loading="lazy">
                <div class="dash-media-card-badges">
                    <span class="dash-media-status ${img.is_used ? 'used' : 'unused'}" title="${escAttr(usageTitle)}">${img.is_used ? 'Used' : 'Unused'}</span>
                    ${img.source ? `<span class="dash-media-source">${escHtml(sourceLabel(img.source))}</span>` : ''}
                </div>
            </div>
            <div class="dash-media-card-info">
                <span class="dash-media-card-name" title="${escAttr(label)}">${escHtml(label)}</span>
                <span class="dash-media-card-meta">${escHtml([img.orientation, formatBytes(img.file_size)].filter(Boolean).join(' / '))}</span>
                ${tags.length ? `<div class="dash-media-tags">${tags.map(tag => `<span>${escHtml(tag)}</span>`).join('')}</div>` : ''}
                ${img.usage_labels?.length ? `<span class="dash-media-usage">${escHtml(img.usage_labels[0])}</span>` : '<span class="dash-media-usage">Available for campaigns and pages</span>'}
                <div class="dash-media-card-actions">
                    <button class="dash-btn dash-btn--secondary dash-btn--sm" data-edit-media="${escAttr(img.id)}">Edit metadata</button>
                    <button class="dash-btn dash-btn--ghost dash-btn--sm dash-btn--danger" data-delete-media="${escAttr(img.id)}">Delete</button>
                </div>
            </div>
        </div>
    `;
}

async function uploadMediaFile(input) {
    const file = input.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
        const token = document.querySelector('meta[name="ai-request-token"]')?.content || '';
        const resp = await fetch('/api/images/upload', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'SwiftSitesApp',
                'X-AI-Request-Token': token,
            },
            body: formData,
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ error: 'Upload failed' }));
            throw new Error(err.error || 'Upload failed');
        }
        input.value = '';
        await loadOrgMedia();
    } catch (e) {
        input.value = '';
        await showMessageModal({ title: 'Upload failed', message: e.message });
    }
}

async function searchMediaStockImages(options = {}) {
    const loadMore = Boolean(options.loadMore);
    const input = document.getElementById('dashMediaStockQuery');
    const grid = document.getElementById('dashMediaStockGrid');
    const loadMoreBtn = document.getElementById('dashMediaStockLoadMoreBtn');
    const query = input?.value.trim() || '';
    if (!grid) return;
    if (!query && !mediaStockColor && !mediaStockOrientation && !mediaStockVisualType) return;
    if (mediaStockIsLoading) return;
    if (loadMore && mediaStockTotalPages && mediaStockPage >= mediaStockTotalPages) return;

    mediaStockIsLoading = true;
    mediaStockHasSearched = true;
    const nextPage = loadMore ? mediaStockPage + 1 : 1;
    if (!loadMore) {
        mediaStockPage = 1;
        mediaStockTotalPages = 0;
        mediaStockResolvedProvider = '';
        mediaStockResults = [];
        grid.innerHTML = '<p class="dash-empty-text">Searching stock images...</p>';
        renderMediaStockLoadMore();
    } else if (loadMoreBtn) {
        loadMoreBtn.disabled = true;
        loadMoreBtn.textContent = 'Loading...';
    }
    try {
        const provider = mediaStockProvider || (loadMore ? mediaStockResolvedProvider : '');
        const params = new URLSearchParams({ q: query, per_page: 24, page: nextPage });
        if (provider) params.set('provider', provider);
        if (mediaStockColor) params.set('color', mediaStockColor);
        if (mediaStockOrientation) params.set('orientation', mediaStockOrientation);
        if (mediaStockVisualType) params.set('visual_type', mediaStockVisualType);
        const data = await apiFetch(`/api/images/search?${params}`);
        const newResults = (data.results || []).map(photo => ({
            id: photo.id,
            thumbUrl: photo.thumbUrl || photo.smallUrl || photo.regularUrl,
            fullUrl: photo.fullUrl || photo.regularUrl || photo.smallUrl,
            regularUrl: photo.regularUrl || photo.fullUrl || photo.smallUrl,
            photographer: photo.photographer || 'Unknown',
            altText: photo.altText || query,
            source: photo.source || 'stock',
            width: photo.width,
            height: photo.height,
            tags: Array.isArray(photo.tags) ? photo.tags : [],
        }));
        mediaStockResults = loadMore ? mediaStockResults.concat(newResults) : newResults;
        mediaStockPage = nextPage;
        mediaStockTotalPages = Number(data.total_pages || 0);
        mediaStockResolvedProvider = mediaStockProvider || data.source || mediaStockResolvedProvider;
        renderMediaStockResults();
    } catch (e) {
        if (loadMore) {
            await showMessageModal({ title: 'Stock image search failed', message: e.message || 'Stock image search failed.' });
        } else {
            mediaStockResults = [];
            grid.innerHTML = `<p class="dash-empty-text">${escHtml(e.message || 'Stock image search failed.')}</p>`;
        }
        renderMediaStockLoadMore();
    } finally {
        mediaStockIsLoading = false;
        renderMediaStockLoadMore();
    }
}

function renderMediaStockResults() {
    const grid = document.getElementById('dashMediaStockGrid');
    if (!grid) return;
    if (!mediaStockResults.length) {
        grid.innerHTML = `<p class="dash-empty-text">${mediaStockHasSearched ? 'No stock images found.' : 'Search by keyword, color, orientation, or visual type to find stock images.'}</p>`;
        renderMediaStockLoadMore();
        return;
    }
    grid.innerHTML = mediaStockResults.map((photo, index) => {
        const tags = Array.isArray(photo.tags) ? photo.tags.slice(0, 3) : [];
        return `
        <div class="dash-media-stock-card">
            <img src="${escAttr(photo.thumbUrl || photo.regularUrl || photo.fullUrl)}" alt="${escAttr(photo.altText)}" loading="lazy">
            <div class="dash-media-stock-meta">
                <span>${escHtml(sourceLabel(photo.source))}</span>
                <span>${escHtml(photo.photographer)}</span>
            </div>
            ${tags.length ? `<div class="dash-media-stock-tags">${tags.map(tag => `<span>${escHtml(tag)}</span>`).join('')}</div>` : ''}
            <button class="dash-btn dash-btn--primary dash-btn--sm" data-import-stock-media="${index}">Import</button>
        </div>
        `;
    }).join('');
    renderMediaStockLoadMore();
}

function renderMediaStockLoadMore() {
    const row = document.getElementById('dashMediaStockLoadMoreRow');
    const btn = document.getElementById('dashMediaStockLoadMoreBtn');
    if (!row || !btn) return;
    const hasMore = mediaStockHasSearched
        && mediaStockResults.length > 0
        && mediaStockTotalPages > 0
        && mediaStockPage < mediaStockTotalPages;
    row.style.display = hasMore ? '' : 'none';
    btn.disabled = mediaStockIsLoading;
    btn.textContent = mediaStockIsLoading ? 'Loading...' : 'Load more';
}

async function importStockMediaImage(index, button) {
    const photo = mediaStockResults[index];
    if (!photo || !photo.fullUrl) return;
    const originalText = button.textContent;
    button.disabled = true;
    button.classList.remove('dash-btn--primary', 'dash-btn--success');
    button.classList.add('dash-btn--warning');
    button.textContent = 'Importing';
    try {
        await apiFetch('/api/images/download', {
            method: 'POST',
            body: JSON.stringify({
                url: photo.fullUrl,
                alt_text: photo.altText || '',
                photographer: photo.photographer || '',
                source: photo.source || 'stock',
                tags: photo.tags || [],
            }),
        });
        button.classList.remove('dash-btn--warning');
        button.classList.add('dash-btn--success');
        button.textContent = 'Imported';
        await loadOrgMedia();
    } catch (e) {
        button.disabled = false;
        button.classList.remove('dash-btn--warning', 'dash-btn--success');
        button.classList.add('dash-btn--primary');
        button.textContent = originalText;
        await showMessageModal({ title: 'Import failed', message: e.message });
    }
}

function openMediaMetadataModal(assetId) {
    const asset = mediaImages.find(img => img.id === assetId);
    const modal = document.getElementById('mediaMetadataModal');
    if (!asset || !modal) return;

    activeMediaAssetId = assetId;
    const preview = document.getElementById('mediaMetaPreview');
    const altText = document.getElementById('mediaMetaAltText');
    const tags = document.getElementById('mediaMetaTags');
    const photographer = document.getElementById('mediaMetaPhotographer');
    const license = document.getElementById('mediaMetaLicense');
    const readonly = document.getElementById('mediaMetaReadOnly');

    if (preview) {
        preview.src = asset.url || '';
        preview.alt = asset.alt_text || asset.original_name || '';
    }
    if (altText) altText.value = asset.alt_text || '';
    if (tags) tags.value = Array.isArray(asset.tags) ? asset.tags.join(', ') : '';
    if (photographer) photographer.value = asset.photographer || '';
    if (license) license.value = asset.license_label || '';
    if (readonly) {
        readonly.innerHTML = [
            ['Source', sourceLabel(asset.source || 'upload')],
            ['Dimensions', asset.width && asset.height ? `${asset.width}x${asset.height}` : 'Unknown'],
            ['Orientation', asset.orientation || 'Unknown'],
            ['Usage', asset.usage_labels?.length ? asset.usage_labels.join(', ') : 'No current references detected'],
        ].map(([label, value]) => `<div><span>${escHtml(label)}</span><strong>${escHtml(value)}</strong></div>`).join('');
    }

    modal.style.display = '';
}

function closeMediaMetadataModal() {
    const modal = document.getElementById('mediaMetadataModal');
    if (modal) modal.style.display = 'none';
    activeMediaAssetId = null;
}

async function saveMediaMetadata() {
    if (!activeMediaAssetId) return;
    const altText = document.getElementById('mediaMetaAltText')?.value.trim() || '';
    const tags = document.getElementById('mediaMetaTags')?.value || '';
    const photographer = document.getElementById('mediaMetaPhotographer')?.value.trim() || '';
    const license = document.getElementById('mediaMetaLicense')?.value.trim() || '';

    try {
        await apiFetch(`/api/media/${activeMediaAssetId}`, {
            method: 'PATCH',
            body: JSON.stringify({
                alt_text: altText,
                tags,
                photographer,
                license_label: license,
            }),
        });
        closeMediaMetadataModal();
        await loadOrgMedia();
    } catch (e) {
        await showMessageModal({ title: 'Metadata save failed', message: e.message });
    }
}

async function deleteMediaAsset(assetId) {
    const asset = mediaImages.find(img => img.id === assetId);
    const usage = asset?.usage_labels?.length ? `\n\nDetected usage: ${asset.usage_labels.join(', ')}` : '';
    const confirmed = await showConfirmModal({
        title: 'Delete media asset',
        message: `Delete this media asset?${usage}`,
        confirmText: 'Delete',
        danger: true,
    });
    if (!confirmed) return;
    try {
        await apiFetch(`/api/media/${assetId}`, { method: 'DELETE' });
        mediaImages = mediaImages.filter(img => img.id !== assetId);
        await loadOrgMedia();
    } catch (e) {
        await showMessageModal({ title: 'Delete failed', message: e.message });
    }
}

function sourceLabel(source) {
    const labels = {
        upload: 'Upload',
        pexels: 'Pexels',
        pixabay: 'Pixabay',
        stock: 'Stock',
    };
    return labels[source] || capitalize(String(source || 'unknown'));
}

// =============================================================================
// BRAND & CONTENT VIEW
// =============================================================================

async function loadBrandView() {
    await Promise.all([loadBrands(), loadContent()]);
    populateBrandOptionSelects();
    hideBrandEditor();
    renderBrandList();
}

async function loadContentView() {
    await Promise.all([loadBrands(), loadProducts(), loadContentOptions(), loadContentFolders()]);
    renderContentScopeOptions();
    await loadContent();
}

function brandThemeMeta(themeKey) {
    return (brandOptions.themes || []).find(theme => theme.value === themeKey) || null;
}

function brandThemeCategoryLabel(categoryKey) {
    const category = (brandOptions.theme_categories || []).find(item => item.key === categoryKey);
    return category?.label || capitalize(String(categoryKey || '').replace(/_/g, ' '));
}

function selectedBrandThemeKey() {
    return document.getElementById('brandTheme')?.value || '';
}

function selectedBrandTone() {
    return document.getElementById('brandTone')?.value || '';
}

function paletteMatchesTheme(palette, themeKey) {
    return Boolean(themeKey && (palette.theme_keys || []).includes(themeKey));
}

function paletteMatchesTone(palette, tone) {
    return Boolean(tone && (palette.tone_tags || []).includes(tone));
}

function paletteMatchesThemeCategory(palette, themeKey) {
    const theme = brandThemeMeta(themeKey);
    return Boolean(theme?.category && palette.category === theme.category);
}

function rankBrandPalettes(palettes, themeKey, tone) {
    const ranked = palettes.map((palette, index) => {
        const themeMatch = paletteMatchesTheme(palette, themeKey);
        const toneMatch = paletteMatchesTone(palette, tone);
        const categoryMatch = paletteMatchesThemeCategory(palette, themeKey);
        let score = 0;
        if (themeMatch && toneMatch) score = 400;
        else if (themeMatch) score = 300;
        else if (categoryMatch) score = 200;
        else if (!themeKey && toneMatch) score = 100;
        return { palette, score, index };
    });
    const matches = ranked.filter(item => item.score > 0);
    const visible = matches.length ? matches : ranked;
    return visible
        .sort((a, b) => (b.score - a.score) || (a.index - b.index))
        .map(item => item.palette);
}

function buildThemeOptionsHtml() {
    const themes = brandOptions.themes || [];
    const categories = brandOptions.theme_categories || [];
    const grouped = [];
    const used = new Set();
    categories.forEach(category => {
        const categoryThemes = themes.filter(theme => theme.category === category.key);
        if (!categoryThemes.length) return;
        categoryThemes.forEach(theme => used.add(theme.value));
        grouped.push(`
            <optgroup label="${escAttr(category.label)}">
                ${categoryThemes.map(theme => `<option value="${escAttr(theme.value)}">${escHtml(theme.label)}</option>`).join('')}
            </optgroup>
        `);
    });
    const uncategorized = themes.filter(theme => !used.has(theme.value));
    if (uncategorized.length) {
        grouped.push(`
            <optgroup label="Other">
                ${uncategorized.map(theme => `<option value="${escAttr(theme.value)}">${escHtml(theme.label)}</option>`).join('')}
            </optgroup>
        `);
    }
    return grouped.join('');
}

function bindBrandPaletteFilterControls() {
    ['brandTheme', 'brandTone'].forEach(id => {
        const el = document.getElementById(id);
        if (!el || el.dataset.paletteFilterBound === 'true') return;
        el.dataset.paletteFilterBound = 'true';
        el.addEventListener('change', renderBrandColorPalettes);
    });
}

function populateBrandOptionSelects() {
    const heading = document.getElementById('brandFontHeading');
    const body = document.getElementById('brandFontBody');
    const theme = document.getElementById('brandTheme');
    const tone = document.getElementById('brandTone');
    const fontOptions = (brandOptions.fonts || []).map(f =>
        `<option value="${escAttr(f.value)}">${escHtml(f.label)} - ${escHtml(f.use || '')}</option>`
    ).join('');
    const toneOptions = (brandOptions.tones || []).map(t =>
        `<option value="${escAttr(t)}">${escHtml(capitalize(t.replace(/_/g, ' ')))}</option>`
    ).join('');

    if (heading && body && heading.options.length <= 1) {
        heading.innerHTML = '<option value="">Select heading font</option>' + fontOptions;
        body.innerHTML = '<option value="">Select body font</option>' + fontOptions;
    }
    if (theme) {
        const current = theme.value;
        theme.innerHTML = '<option value="">Select a theme</option>' + buildThemeOptionsHtml();
        theme.value = current;
    }
    if (tone) {
        const current = tone.value;
        tone.innerHTML = '<option value="">Select a tone</option>' + toneOptions;
        tone.value = current;
    }
    bindBrandPaletteFilterControls();
    renderBrandColorPalettes();
}

function renderBrandColorPalettes() {
    const container = document.getElementById('brandColorPalettes');
    if (!container) return;
    const palettes = brandOptions.color_palettes || [];
    const themeKey = selectedBrandThemeKey();
    const tone = selectedBrandTone();
    const rankedPalettes = rankBrandPalettes(palettes, themeKey, tone);
    const hint = document.getElementById('brandPaletteContext');
    if (!palettes.length) {
        container.innerHTML = '';
        if (hint) hint.textContent = '';
        return;
    }
    if (hint) {
        const theme = brandThemeMeta(themeKey);
        const parts = [];
        if (theme) parts.push(theme.label);
        if (tone) parts.push(capitalize(tone.replace(/_/g, ' ')));
        hint.textContent = parts.length
            ? `Showing palettes matched to ${parts.join(' + ')}. Theme and tone changes do not overwrite colors.`
            : 'Select a theme and tone to narrow palette suggestions. Click a palette to apply colors.';
    }
    container.innerHTML = rankedPalettes.map(palette => {
        const colors = palette.colors || {};
        const swatches = ['primary', 'secondary', 'text', 'accent', 'background']
            .map(key => `<span class="dash-palette-swatch" style="background:${escAttr(colors[key] || '#ffffff')}"></span>`)
            .join('');
        const categoryLabel = brandThemeCategoryLabel(palette.category);
        const toneMatch = paletteMatchesTone(palette, tone);
        const themeMatch = paletteMatchesTheme(palette, themeKey);
        return `
            <button class="dash-palette-option" type="button" data-brand-palette="${escAttr(palette.key)}">
                <span class="dash-palette-swatches">${swatches}</span>
                <span class="dash-palette-text">
                    <span class="dash-palette-title">${escHtml(palette.label)}</span>
                    <span class="dash-palette-meta">${escHtml(categoryLabel)}${themeMatch || toneMatch ? ' match' : ''}</span>
                </span>
            </button>
        `;
    }).join('');
    container.querySelectorAll('[data-brand-palette]').forEach(button => {
        button.addEventListener('click', () => applyBrandColorPalette(button.dataset.brandPalette));
    });
}

function applyBrandColorPalette(key) {
    const palette = (brandOptions.color_palettes || []).find(item => item.key === key);
    if (!palette?.colors) return;
    const map = {
        primary: 'brandColorPrimary',
        secondary: 'brandColorSecondary',
        text: 'brandColorText',
        accent: 'brandColorAccent',
        background: 'brandColorBg',
    };
    for (const [colorKey, id] of Object.entries(map)) {
        const el = document.getElementById(id);
        const value = palette.colors[colorKey];
        if (el && value) el.value = value;
    }
}

function brandThemeLabel(themeKey) {
    if (!themeKey) return 'No theme';
    return brandThemeMeta(themeKey)?.label || capitalize(String(themeKey).replace(/_/g, ' '));
}

function brandToneLabel(tone) {
    if (!tone) return 'No tone';
    return capitalize(String(tone).replace(/_/g, ' '));
}

function brandFontLabel(font) {
    if (!font) return '';
    return (brandOptions.fonts || []).find(item => item.value === font)?.label || font;
}

function brandCardColorSwatches(brand) {
    const colors = brand.colors || {};
    const keys = ['primary', 'secondary', 'text', 'accent', 'background'];
    const swatches = keys
        .filter(key => colors[key])
        .map(key => `
            <span class="dash-brand-card-swatch" style="background:${escAttr(colors[key])}" title="${escAttr(`${capitalize(key)}: ${colors[key]}`)}"></span>
        `)
        .join('');
    return swatches || '<span class="dash-brand-card-muted">No colors set</span>';
}

function brandCardFontSummary(brand) {
    const heading = brandFontLabel(brand.fonts?.heading);
    const body = brandFontLabel(brand.fonts?.body);
    if (heading && body) return `${heading} / ${body}`;
    return heading || body || 'No fonts';
}

function renderBrandList() {
    const container = document.getElementById('dashBrandList');
    if (!container) return;
    if (!brands.length) {
        container.innerHTML = '<p class="dash-empty-inline">No brands yet. Create one to give campaigns a voice and visual identity.</p>';
        return;
    }
    container.innerHTML = brands.map(brand => {
        const description = (brand.description || '').trim() || 'No brand description yet.';
        return `
        <div class="dash-brand-card-item${brand.id === activeBrandId ? ' active' : ''}" role="button" tabindex="0" data-brand-id="${escAttr(brand.id)}">
            <span class="dash-brand-card-head">
                <span class="dash-brand-card-title">
                    <span class="dash-brand-card-name">${escHtml(brand.name)}</span>
                    ${brand.is_default ? '<span class="dash-brand-card-badge">Default</span>' : ''}
                </span>
                <button class="dash-brand-card-delete" type="button" data-delete-brand="${escAttr(brand.id)}" title="Delete brand" aria-label="Delete ${escAttr(brand.name)}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M3 6h18"></path>
                        <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
                        <path d="M10 11v6"></path>
                        <path d="M14 11v6"></path>
                    </svg>
                </button>
            </span>
            <span class="dash-brand-card-summary">${escHtml(description)}</span>
            <span class="dash-brand-card-visuals">
                <span class="dash-brand-card-swatches" aria-label="Brand colors">${brandCardColorSwatches(brand)}</span>
                <span class="dash-brand-card-meta">
                    <span><strong>Theme</strong>${escHtml(brandThemeLabel(brand.default_style))}</span>
                    <span><strong>Tone</strong>${escHtml(brandToneLabel(brand.tone))}</span>
                    <span><strong>Fonts</strong>${escHtml(brandCardFontSummary(brand))}</span>
                </span>
            </span>
        </div>
    `}).join('');
    container.querySelectorAll('.dash-brand-card-item').forEach(btn => {
        const openBrand = () => {
            activeBrandId = btn.dataset.brandId;
            renderBrandList();
            showBrandEditor({ mode: 'edit', brandId: activeBrandId });
            renderContentList();
        };
        btn.addEventListener('click', openBrand);
        btn.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openBrand();
            }
        });
    });
    container.querySelectorAll('[data-delete-brand]').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            event.stopPropagation();
            deleteBrandById(button.dataset.deleteBrand, { trigger: button, closeEditor: false });
        });
    });
}

function populateBrandForm() {
    const brand = brands.find(b => b.id === activeBrandId);
    const card = document.getElementById('dashBrandCard');
    if (!brand) {
        if (card) card.style.display = 'none';
        return;
    }
    if (card) card.style.display = '';
    document.getElementById('brandName').value = brand.name || '';
    document.getElementById('brandTagline').value = brand.tagline || '';
    document.getElementById('brandDescription').value = brand.description || '';
    document.getElementById('brandLogoUrl').value = brand.logo_url || '';
    document.getElementById('brandWebsiteUrl').value = brand.website_url || '';
    document.getElementById('brandIndustry').value = brand.industry || '';
    document.getElementById('brandTone').value = brand.tone || '';
    document.getElementById('brandTheme').value = brand.default_style || '';
    document.getElementById('brandVoiceGuidelines').value = brand.voice_guidelines || '';
    document.getElementById('brandFontHeading').value = brand.fonts?.heading || '';
    document.getElementById('brandFontBody').value = brand.fonts?.body || '';
    populateBrandSocialForm(brand.social_links || {});

    if (brand.colors?.primary) document.getElementById('brandColorPrimary').value = brand.colors.primary;
    if (brand.colors?.secondary) document.getElementById('brandColorSecondary').value = brand.colors.secondary;
    if (brand.colors?.text) document.getElementById('brandColorText').value = brand.colors.text;
    if (brand.colors?.accent) document.getElementById('brandColorAccent').value = brand.colors.accent;
    if (brand.colors?.background) document.getElementById('brandColorBg').value = brand.colors.background;

    populateBrandStrategyForm(brand.strategy || {});
    updateBrandSiteActions(brand);
}

function closeBrandOptionalSections() {
    document.getElementById('brandSocialSection')?.removeAttribute('open');
    document.getElementById('brandStrategySection')?.removeAttribute('open');
}

function resetBrandEditor() {
    document.getElementById('brandName').value = '';
    document.getElementById('brandTagline').value = '';
    document.getElementById('brandDescription').value = '';
    document.getElementById('brandLogoUrl').value = '';
    document.getElementById('brandWebsiteUrl').value = '';
    document.getElementById('brandIndustry').value = '';
    document.getElementById('brandTone').value = '';
    document.getElementById('brandTheme').value = '';
    document.getElementById('brandVoiceGuidelines').value = '';
    document.getElementById('brandFontHeading').value = '';
    document.getElementById('brandFontBody').value = '';
    populateBrandSocialForm({});
    populateBrandStrategyForm({});
    document.getElementById('brandColorPrimary').value = '#1a1a1a';
    document.getElementById('brandColorSecondary').value = '#6b7280';
    document.getElementById('brandColorText').value = '#374151';
    document.getElementById('brandColorAccent').value = '#3b82f6';
    document.getElementById('brandColorBg').value = '#ffffff';
    setBrandEditorError('');
    const status = document.getElementById('brandSaveStatus');
    if (status) status.textContent = '';
    updateBrandSiteActions(null);
    closeBrandOptionalSections();
}

function showBrandEditor({ mode = 'edit', brandId = null } = {}) {
    brandEditorMode = mode;
    editingBrandId = mode === 'edit' ? brandId : null;
    const listView = document.getElementById('dashBrandListView');
    const editorView = document.getElementById('dashBrandEditorView');
    const title = document.getElementById('brandEditorTitle');
    const hint = document.getElementById('brandEditorHint');
    const saveBtn = document.getElementById('saveBrandBtn');
    const deleteBtn = document.getElementById('deleteBrandBtn');
    if (listView) listView.style.display = 'none';
    if (editorView) editorView.style.display = '';
    resetBrandEditor();
    if (mode === 'edit') {
        activeBrandId = brandId;
        populateBrandForm();
    }
    if (title) title.textContent = mode === 'create' ? 'Create brand' : 'Edit brand';
    if (hint) {
        hint.textContent = mode === 'create'
            ? 'Create a complete brand profile for site shells, AI wording, and generated sections.'
            : 'Update the brand voice, visuals, and reusable AI prompt context.';
    }
    if (saveBtn) saveBtn.textContent = mode === 'create' ? 'Create brand' : 'Save brand';
    if (deleteBtn) deleteBtn.style.display = mode === 'create' || !(editingBrandId || activeBrandId) ? 'none' : '';
    const siteActions = document.querySelector('.dash-brand-site-actions');
    if (siteActions) siteActions.style.display = mode === 'create' ? 'none' : '';
    document.getElementById('brandName')?.focus();
}

function hideBrandEditor() {
    editingBrandId = null;
    brandEditorMode = 'edit';
    const listView = document.getElementById('dashBrandListView');
    const editorView = document.getElementById('dashBrandEditorView');
    if (editorView) editorView.style.display = 'none';
    if (listView) listView.style.display = '';
    setBrandEditorError('');
}

function updateBrandSiteActions(brand) {
    const actionBtn = document.getElementById('brandSiteActionBtn');
    const regenerateBtn = document.getElementById('brandSiteRegenerateBtn');
    const hint = document.getElementById('brandSiteHint');
    if (!actionBtn || !regenerateBtn || !hint) return;

    const hasSite = Boolean(brand?.site_id);
    actionBtn.textContent = hasSite ? 'Open site' : 'Create site';
    actionBtn.dataset.siteId = brand?.site_id || '';
    regenerateBtn.style.display = hasSite ? '' : 'none';
    hint.textContent = hasSite
        ? 'Open the brand site or refresh its shell from the latest brand attributes.'
        : 'Create a renderer-ready site shell from this brand.';
}

// Maps a strategy field key to its form element id
const STRATEGY_TEXT_FIELDS = {
    target_audience: 'brandTargetAudience',
    brand_promise: 'brandPromise',
    positioning_statement: 'brandPositioning',
    compliance_notes: 'brandComplianceNotes',
    image_style: 'brandImageStyle',
    cta_style: 'brandCtaStyle',
    primary_market: 'brandPrimaryMarket',
    locale: 'brandLocale',
};
const STRATEGY_LIST_FIELDS = {
    differentiators: 'brandDifferentiators',
    competitors: 'brandCompetitors',
    forbidden_words: 'brandForbiddenWords',
    forbidden_claims: 'brandForbiddenClaims',
    required_claims: 'brandRequiredClaims',
    voice_examples: 'brandVoiceExamples',
    voice_anti_examples: 'brandVoiceAntiExamples',
};

const BRAND_AI_FIELDS = [
    { key: 'description', id: 'brandDescription' },
    { key: 'font_heading', id: 'brandFontHeading' },
    { key: 'font_body', id: 'brandFontBody' },
    { key: 'voice_guidelines', id: 'brandVoiceGuidelines' },
    { key: 'target_audience', id: 'brandTargetAudience' },
    { key: 'brand_promise', id: 'brandPromise' },
    { key: 'differentiators', id: 'brandDifferentiators' },
    { key: 'positioning_statement', id: 'brandPositioning' },
    { key: 'voice_examples', id: 'brandVoiceExamples' },
    { key: 'voice_anti_examples', id: 'brandVoiceAntiExamples' },
    { key: 'forbidden_words', id: 'brandForbiddenWords' },
    { key: 'forbidden_claims', id: 'brandForbiddenClaims' },
    { key: 'required_claims', id: 'brandRequiredClaims' },
    { key: 'compliance_notes', id: 'brandComplianceNotes' },
    { key: 'image_style', id: 'brandImageStyle' },
    { key: 'cta_style', id: 'brandCtaStyle' },
    { key: 'primary_market', id: 'brandPrimaryMarket' },
    { key: 'locale', id: 'brandLocale' },
    { key: 'competitors', id: 'brandCompetitors' },
];

function brandStrategyFieldIds() {
    return [
        'brandVoiceGuidelines',
        ...Object.values(STRATEGY_TEXT_FIELDS),
        ...Object.values(STRATEGY_LIST_FIELDS),
    ];
}

function populateBrandStrategyForm(strategy) {
    for (const [key, id] of Object.entries(STRATEGY_TEXT_FIELDS)) {
        const el = document.getElementById(id);
        if (el) el.value = strategy[key] || '';
    }
    for (const [key, id] of Object.entries(STRATEGY_LIST_FIELDS)) {
        const el = document.getElementById(id);
        if (el) el.value = (strategy[key] || []).join('\n');
    }

    const section = document.getElementById('brandStrategySection');
    if (section) section.open = false;
}

function collectBrandStrategy() {
    const strategy = {};
    for (const [key, id] of Object.entries(STRATEGY_TEXT_FIELDS)) {
        const el = document.getElementById(id);
        if (el) strategy[key] = el.value.trim();
    }
    for (const [key, id] of Object.entries(STRATEGY_LIST_FIELDS)) {
        const el = document.getElementById(id);
        if (el) {
            strategy[key] = el.value.split('\n').map(s => s.trim()).filter(Boolean);
        }
    }
    return strategy;
}

const BRAND_SOCIAL_FIELDS = {
    instagram: 'brandSocialInstagram',
    facebook: 'brandSocialFacebook',
    linkedin: 'brandSocialLinkedin',
    x: 'brandSocialX',
    youtube: 'brandSocialYoutube',
    tiktok: 'brandSocialTiktok',
};

function populateBrandSocialForm(socialLinks) {
    for (const [key, id] of Object.entries(BRAND_SOCIAL_FIELDS)) {
        const el = document.getElementById(id);
        if (el) el.value = socialLinks?.[key] || '';
    }
}

function collectSocialLinks(fields = BRAND_SOCIAL_FIELDS) {
    const links = {};
    for (const [key, id] of Object.entries(fields)) {
        const value = document.getElementById(id)?.value.trim();
        if (value) links[key] = value;
    }
    return links;
}

function collectBrandAiContent() {
    const strategy = collectBrandStrategy();
    return {
        name: document.getElementById('brandName')?.value.trim() || '',
        tagline: document.getElementById('brandTagline')?.value.trim() || '',
        description: document.getElementById('brandDescription')?.value.trim() || '',
        logo_url: document.getElementById('brandLogoUrl')?.value.trim() || '',
        website_url: document.getElementById('brandWebsiteUrl')?.value.trim() || '',
        industry: document.getElementById('brandIndustry')?.value.trim() || '',
        tone: document.getElementById('brandTone')?.value || '',
        default_style: document.getElementById('brandTheme')?.value || '',
        colors: {
            primary: document.getElementById('brandColorPrimary')?.value || '',
            secondary: document.getElementById('brandColorSecondary')?.value || '',
            text: document.getElementById('brandColorText')?.value || '',
            accent: document.getElementById('brandColorAccent')?.value || '',
            background: document.getElementById('brandColorBg')?.value || '',
        },
        font_heading: document.getElementById('brandFontHeading')?.value || '',
        font_body: document.getElementById('brandFontBody')?.value || '',
        social_links: collectSocialLinks(),
        voice_guidelines: document.getElementById('brandVoiceGuidelines')?.value.trim() || '',
        ...strategy,
    };
}

function brandSuggestionTargets() {
    return [
        { key: 'voice_guidelines', id: 'brandVoiceGuidelines', source: data => data.voice_guidelines },
        ...Object.entries(STRATEGY_TEXT_FIELDS).map(([key, id]) => ({
            key,
            id,
            source: data => data.strategy?.[key],
        })),
        ...Object.entries(STRATEGY_LIST_FIELDS).map(([key, id]) => ({
            key,
            id,
            source: data => {
                const value = data.strategy?.[key];
                return Array.isArray(value) ? value.join('\n') : value;
            },
        })),
    ];
}

function hasBrandSuggestionValues() {
    return brandSuggestionTargets().some(target => {
        const el = document.getElementById(target.id);
        return Boolean(el?.value?.trim());
    });
}

function applyBrandStrategySuggestions(data, { overwrite = false } = {}) {
    const section = document.getElementById('brandStrategySection');
    if (section) section.open = true;

    let applied = 0;
    brandSuggestionTargets().forEach(target => {
        const el = document.getElementById(target.id);
        const value = target.source(data);
        const text = Array.isArray(value) ? value.join('\n') : String(value || '').trim();
        if (!el || !text) return;
        if (!overwrite && el.value.trim()) return;
        el.value = text;
        el.classList.add('dash-ai-enhanced');
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        setTimeout(() => el.classList.remove('dash-ai-enhanced'), 1400);
        applied += 1;
    });
    return applied;
}

async function suggestBrandStrategyAndGuardrails() {
    const button = document.getElementById('suggestBrandStrategyBtn');
    const status = document.getElementById('brandSaveStatus');
    const lockedFields = brandStrategyFieldIds();
    let overwrite = true;
    if (hasBrandSuggestionValues()) {
        overwrite = await showConfirmModal({
            title: 'Replace existing strategy?',
            message: 'Some AI strategy or voice guardrail fields already contain text. Replace them with new suggestions? Cancel will fill empty fields only.',
            confirmText: 'Replace fields',
            danger: false,
        });
    }

    try {
        setAiGeneratingState({
            active: true,
            button,
            loadingLabel: 'AI is generating...',
            statusEl: status,
            statusText: 'AI is generating strategy and guardrails...',
            fields: lockedFields,
        });
        const suggestion = await apiFetch('/api/brands/suggest-strategy', {
            method: 'POST',
            body: JSON.stringify(collectBrandEditorPayload()),
        });
        const applied = applyBrandStrategySuggestions(suggestion, { overwrite });
        if (status) {
            status.textContent = applied ? 'Strategy suggested' : 'No empty fields to fill';
            status.style.color = '';
            setTimeout(() => { status.textContent = ''; }, 2200);
        }
    } catch (e) {
        if (status) {
            status.textContent = e.message || 'Strategy suggestion failed';
            status.style.color = 'var(--d-danger)';
        }
        await showMessageModal({
            title: 'Suggestion failed',
            message: e.message || 'AI could not suggest strategy and guardrails right now.',
        });
    } finally {
        setAiGeneratingState({ active: false, button, fields: lockedFields });
    }
}

function attachBrandAiButtons() {
    BRAND_AI_FIELDS.forEach(field => {
        const input = document.getElementById(field.id);
        const wrapper = input?.closest('.dash-field');
        const label = wrapper?.querySelector(`label[for="${field.id}"]`);
        if (!input || !wrapper || !label || wrapper.querySelector(`[data-brand-ai-field="${field.key}"]`)) return;

        const row = document.createElement('div');
        row.className = 'dash-label-row';
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'dash-ai-field-btn';
        button.dataset.brandAiField = field.key;
        button.dataset.brandAiTarget = field.id;
        button.title = 'Enhance this field with AI';
        button.innerHTML = `
            <svg class="dash-ai-field-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.64 3.64-1.28-1.28a1.2 1.2 0 0 0-1.72 0L2.36 18.64a1.2 1.2 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72Z"></path>
                <path d="m14 7 3 3"></path>
                <path d="M5 6v4"></path>
                <path d="M19 14v4"></path>
                <path d="M10 2v2"></path>
                <path d="M7 8H3"></path>
                <path d="M21 16h-4"></path>
                <path d="M11 3H9"></path>
            </svg>
        `;

        wrapper.insertBefore(row, label);
        row.appendChild(label);
        row.appendChild(button);
    });
}

function bindBrandAiButtons() {
    document.querySelectorAll('[data-brand-ai-field]').forEach(button => {
        if (button.dataset.bound === 'true') return;
        button.dataset.bound = 'true';
        button.addEventListener('click', () => enhanceBrandField(button));
    });
}

async function enhanceBrandField(button) {
    const field = button.dataset.brandAiField;
    const target = document.getElementById(button.dataset.brandAiTarget);
    if (!field || !target) return;

    const status = document.getElementById('brandSaveStatus');
    try {
        setAiGeneratingState({
            active: true,
            button,
            loadingLabel: 'AI',
            statusEl: status,
            statusText: 'AI is generating...',
            fields: [target],
        });

        const targetValue = (target.value || '').trim();
        const content = collectBrandAiContent();
        const editorPayload = collectBrandEditorPayload();
        const result = await apiFetch('/api/chat/enhance', {
            method: 'POST',
            body: JSON.stringify({
                business_name: content.name,
                industry: content.industry,
                description: targetValue || content.brand_promise || content.tagline || content.target_audience || '',
                section_type: 'brand',
                target_field: field,
                target_value: targetValue,
                current_content: {
                    ...content,
                    full: editorPayload,
                },
            }),
        });
        const enhanced = result.enhanced_fields?.[field];
        if (enhanced) {
            if (target.tagName === 'SELECT') {
                const hasOption = Array.from(target.options).some(option => option.value === enhanced);
                if (hasOption) target.value = enhanced;
            } else {
                target.value = enhanced;
            }
            target.classList.add('dash-ai-enhanced');
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(() => target.classList.remove('dash-ai-enhanced'), 1400);
            if (status) {
                status.textContent = result.source === 'fallback' ? 'Suggested' : 'Enhanced';
                status.style.color = '';
            }
        }
    } catch (e) {
        if (status) {
            status.textContent = e.message || 'AI unavailable';
            status.style.color = 'var(--d-danger)';
        }
    } finally {
        setAiGeneratingState({ active: false, button, fields: [target] });
        if (status) setTimeout(() => { status.textContent = ''; }, 2000);
    }
}

function bindBrandKit() {
    attachBrandAiButtons();
    bindBrandAiButtons();
    document.getElementById('saveBrandBtn').addEventListener('click', saveBrand);
    document.getElementById('deleteBrandBtn')?.addEventListener('click', deleteCurrentBrand);
    document.getElementById('addBrandBtn').addEventListener('click', () => showBrandEditor({ mode: 'create' }));
    document.getElementById('cancelBrandEditor')?.addEventListener('click', hideBrandEditor);
    document.getElementById('suggestBrandStrategyBtn')?.addEventListener('click', suggestBrandStrategyAndGuardrails);
    document.getElementById('brandSiteActionBtn')?.addEventListener('click', handleBrandSiteAction);
    document.getElementById('brandSiteRegenerateBtn')?.addEventListener('click', handleBrandSiteRegenerate);
}

async function openCreateBrandModal() {
    if (currentView !== 'brands') {
        await switchView('brands');
    }
    if (!(brandOptions.fonts || []).length || !(brandOptions.themes || []).length) {
        await loadBrandOptions();
        populateBrandOptionSelects();
    }
    showBrandEditor({ mode: 'create' });
}

function setBrandEditorError(message) {
    const status = document.getElementById('brandSaveStatus');
    if (!status) return;
    status.textContent = message || '';
    status.style.color = message ? 'var(--d-danger)' : '';
}

function collectBrandEditorPayload() {
    return {
        name: document.getElementById('brandName').value.trim(),
        tagline: document.getElementById('brandTagline').value.trim(),
        description: document.getElementById('brandDescription').value.trim(),
        logo_url: document.getElementById('brandLogoUrl').value.trim(),
        website_url: document.getElementById('brandWebsiteUrl').value.trim(),
        industry: document.getElementById('brandIndustry').value.trim(),
        voice_guidelines: document.getElementById('brandVoiceGuidelines').value.trim(),
        tone: document.getElementById('brandTone').value,
        default_style: document.getElementById('brandTheme').value,
        colors: {
            primary: document.getElementById('brandColorPrimary').value,
            secondary: document.getElementById('brandColorSecondary').value,
            text: document.getElementById('brandColorText').value,
            accent: document.getElementById('brandColorAccent').value,
            background: document.getElementById('brandColorBg').value,
        },
        fonts: {
            heading: document.getElementById('brandFontHeading').value,
            body: document.getElementById('brandFontBody').value,
        },
        social_links: collectSocialLinks(),
        strategy: collectBrandStrategy(),
    };
}

async function createBrandFromDashboard() {
    const confirmBtn = document.getElementById('saveBrandBtn');
    const data = collectBrandEditorPayload();
    const name = data.name;
    if (!name) {
        setBrandEditorError('Brand name is required.');
        return;
    }
    data.is_default = brands.length === 0;

    const loadingFields = document.querySelectorAll('#dashBrandEditorView input, #dashBrandEditorView select, #dashBrandEditorView textarea');

    try {
        setAiGeneratingState({
            active: true,
            button: confirmBtn,
            loadingLabel: 'Enhancing brand with AI...',
            statusEl: document.getElementById('brandSaveStatus'),
            statusText: 'Creating your brand shell and AI prompt context. This can take a moment.',
            fields: loadingFields,
        });
        const brand = await apiFetch('/api/brands', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        brands.unshift(brand);
        activeBrandId = brand.id;
        hideBrandEditor();
        renderHomeView();
        renderBrandList();
        renderContentList();
        populateProductBrandFilter();
        renderProductBrandCheckboxes();
    } catch (e) {
        setBrandEditorError(e.message || 'Failed to create brand.');
    } finally {
        setAiGeneratingState({ active: false, button: confirmBtn, fields: loadingFields });
    }
}

async function saveBrand() {
    if (brandEditorMode === 'create') {
        await createBrandFromDashboard();
        return;
    }
    if (!editingBrandId && !activeBrandId) return;
    const brandId = editingBrandId || activeBrandId;
    const status = document.getElementById('brandSaveStatus');
    status.textContent = 'Saving...';
    status.style.color = 'var(--d-text-tertiary)';

    const data = collectBrandEditorPayload();

    try {
        const updated = await apiFetch(`/api/brands/${brandId}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
        brands = brands.map(b => b.id === updated.id ? updated : b);
        activeBrandId = updated.id;
        renderBrandList();
        status.textContent = 'Saved';
        status.style.color = '';
        setTimeout(() => { status.textContent = ''; }, 2000);
    } catch (e) {
        status.textContent = e.message || 'Save failed';
        status.style.color = 'var(--d-danger)';
    }
}

async function deleteCurrentBrand() {
    const brandId = editingBrandId || activeBrandId;
    if (!brandId || brandEditorMode === 'create') return;
    await deleteBrandById(brandId, {
        trigger: document.getElementById('deleteBrandBtn'),
        status: document.getElementById('brandSaveStatus'),
        closeEditor: true,
    });
}

async function deleteBrandById(brandId, { trigger = null, status = null, closeEditor = true } = {}) {
    const brand = brands.find(b => b.id === brandId);
    const brandName = brand?.name || 'this brand';

    const confirmed = await showConfirmModal({
        title: 'Delete brand?',
        message: `This archives "${brandName}" and removes it from active brand lists. Existing sites, content, sections, and campaigns are preserved.`,
        confirmText: 'Delete brand',
        danger: true,
    });
    if (!confirmed) return;

    try {
        if (trigger) trigger.disabled = true;
        if (status) {
            status.textContent = 'Deleting...';
            status.style.color = 'var(--d-text-tertiary)';
        }
        await apiFetch(`/api/brands/${brandId}`, { method: 'DELETE' });
        brands = brands.filter(b => b.id !== brandId);
        if (activeBrandId === brandId) {
            const next = brands.find(b => b.is_default) || brands[0] || null;
            activeBrandId = next?.id || null;
        }
        editingBrandId = null;
        if (contentBrandFilter === brandId) contentBrandFilter = '';
        if (sectionBrandFilter === brandId) sectionBrandFilter = '';
        if (productBrandFilter === brandId) productBrandFilter = '';
        if (closeEditor) {
            hideBrandEditor();
        } else if (editingBrandId === brandId) {
            hideBrandEditor();
        }
        renderHomeView();
        renderBrandList();
        renderContentScopeOptions();
        renderContentList();
        populateProductBrandFilter();
        renderProductBrandCheckboxes();
        renderProductsGrid();
        renderSectionScopeOptions();
        if (sectionsLoaded) renderSectionList();
    } catch (e) {
        if (status) {
            status.textContent = e.message || 'Delete failed';
            status.style.color = 'var(--d-danger)';
        }
        await showMessageModal({
            title: 'Delete failed',
            message: e.message || 'The brand could not be deleted.',
        });
    } finally {
        if (trigger) trigger.disabled = false;
    }
}

async function handleBrandSiteAction() {
    const brand = brands.find(b => b.id === activeBrandId);
    if (!brand) return;
    if (brand.site_id) {
        openBrandSitePreview(brand.id);
        return;
    }
    await createOrRefreshBrandSite({ openAfterCreate: true });
}

async function handleBrandSiteRegenerate() {
    const brand = brands.find(b => b.id === activeBrandId);
    if (!brand?.site_id) return;
    const confirmed = await showConfirmModal({
        title: 'Regenerate site shell?',
        message: 'This updates the site theme, header, and footer from the current brand attributes. Existing page body YAML is preserved.',
        confirmText: 'Regenerate',
        danger: false,
    });
    if (!confirmed) return;
    await createOrRefreshBrandSite({ regenerate: true, openAfterCreate: false });
}

async function createOrRefreshBrandSite({ regenerate = false, openAfterCreate = false } = {}) {
    const brand = brands.find(b => b.id === activeBrandId);
    const status = document.getElementById('brandSaveStatus');
    const actionBtn = document.getElementById('brandSiteActionBtn');
    const regenerateBtn = document.getElementById('brandSiteRegenerateBtn');
    if (!brand) return;

    try {
        if (status) {
            status.textContent = regenerate ? 'Regenerating site...' : 'Creating site...';
            status.style.color = 'var(--d-text-tertiary)';
        }
        if (actionBtn) actionBtn.disabled = true;
        if (regenerateBtn) regenerateBtn.disabled = true;

        const site = await apiFetch(`/api/brands/${brand.id}/site`, {
            method: 'POST',
            body: JSON.stringify({ regenerate }),
        });
        brands = brands.map(b => b.id === brand.id ? { ...b, site_id: site.id } : b);
        await loadSites();
        renderBrandList();
        populateBrandForm();
        renderHomeView();
        if (status) {
            status.textContent = regenerate ? 'Site shell regenerated' : 'Site created';
            status.style.color = '';
        }
        if (openAfterCreate) {
            openBrandSitePreview(brand.id);
        } else {
            setTimeout(() => {
                if (status) status.textContent = '';
            }, 2200);
        }
    } catch (e) {
        if (status) {
            status.textContent = regenerate ? 'Regenerate failed' : 'Site create failed';
            status.style.color = 'var(--d-danger)';
        }
        await showMessageModal({
            title: regenerate ? 'Regenerate failed' : 'Site create failed',
            message: e.message || 'The brand site could not be updated.',
        });
    } finally {
        if (actionBtn) actionBtn.disabled = false;
        if (regenerateBtn) regenerateBtn.disabled = false;
    }
}

// --- Content Library ---

async function loadContent() {
    try {
        const params = new URLSearchParams();
        if (contentFilter && contentFilter !== 'all') params.set('category', contentFilter);
        if (contentSearch) params.set('q', contentSearch);
        if (contentBrandFilter) params.set('brand_id', contentBrandFilter);
        if (contentProductFilter) params.set('product_id', contentProductFilter);
        if (contentFolderFilter) params.set('folder_id', contentFolderFilter);
        if (contentStatusFilter) params.set('status', contentStatusFilter);
        if (contentSourceFilter) params.set('source', contentSourceFilter);
        const query = params.toString();
        contentItems = await apiFetch(`/api/content${query ? `?${query}` : ''}`);
        renderContentList();
    } catch (e) {
        document.getElementById('dashContentList').innerHTML = '<p class="dash-empty-text">Failed to load content.</p>';
    }
}

function renderContentScopeOptions() {
    const brandFilter = document.getElementById('contentBrandFilter');
    const productFilter = document.getElementById('contentProductFilter');
    const folderFilter = document.getElementById('contentFolderFilter');
    const modalBrand = document.getElementById('contentBrandId');
    const modalProduct = document.getElementById('contentProductId');
    const modalFolder = document.getElementById('contentFolderId');

    const brandOptionsHtml = brands.map(brand =>
        `<option value="${escAttr(brand.id)}">${escHtml(brand.name)}</option>`
    ).join('');
    const productOptionsHtml = products.map(product =>
        `<option value="${escAttr(product.id)}">${escHtml(product.name)}</option>`
    ).join('');
    const folderOptionsHtml = contentFolders.map(folder =>
        `<option value="${escAttr(folder.id)}">${escHtml(folder.name)}</option>`
    ).join('');

    if (brandFilter) {
        const current = brandFilter.value;
        brandFilter.innerHTML = '<option value="">All brands</option><option value="shared">Shared only</option>' + brandOptionsHtml;
        brandFilter.value = current;
    }
    if (productFilter) {
        const current = productFilter.value;
        productFilter.innerHTML = '<option value="">All products</option><option value="none">No product</option>' + productOptionsHtml;
        productFilter.value = current;
    }
    if (folderFilter) {
        const current = folderFilter.value;
        folderFilter.innerHTML = '<option value="">All folders</option><option value="unfiled">Unfiled</option>' + folderOptionsHtml;
        folderFilter.value = current;
    }
    if (modalBrand) {
        const current = modalBrand.value;
        modalBrand.innerHTML = '<option value="">Shared across brands</option>' + brandOptionsHtml;
        modalBrand.value = current || activeBrandId || '';
    }
    if (modalProduct) {
        const current = modalProduct.value;
        modalProduct.innerHTML = '<option value="">No product scope</option>' + productOptionsHtml;
        modalProduct.value = current;
    }
    if (modalFolder) {
        const current = modalFolder.value;
        modalFolder.innerHTML = '<option value="">Unfiled</option>' + folderOptionsHtml;
        modalFolder.value = current;
    }
    renderContentTypeControls();
    updateContentTypeGuidance();
}

function contentTypeList() {
    return contentOptions.content_types || [];
}

function contentTypeFamilies() {
    return contentOptions.content_type_families || [];
}

function contentTypeMeta(key) {
    return contentTypeList().find(type => type.key === key) || null;
}

function contentTypeAllowedForChannel(type, channel, selectedValue) {
    if (!type) return false;
    if (type.key === selectedValue) return true;
    if (!channel || channel === 'general') return type.family !== 'channel_assets';
    const affinity = type.channel_affinity || [];
    return affinity.includes(channel) || affinity.includes('general');
}

function renderContentTypeControls() {
    const types = contentTypeList();
    if (!types.length) return;

    const channel = document.getElementById('contentChannel')?.value || 'general';
    const categorySelect = document.getElementById('contentCategory');
    const categoryFilter = document.getElementById('contentSectionFilter');
    const selectedValue = categorySelect?.value || 'headline';
    const filterValue = categoryFilter?.value || contentFilter || 'all';

    const editorOptions = renderContentTypeOptions({
        includeAll: false,
        selectedValue,
        channel,
    });
    if (categorySelect) {
        categorySelect.innerHTML = editorOptions;
        categorySelect.value = types.some(type => type.key === selectedValue) ? selectedValue : 'headline';
    }

    if (categoryFilter) {
        categoryFilter.innerHTML = renderContentTypeOptions({
            includeAll: true,
            selectedValue: filterValue,
            channel: '',
        });
        categoryFilter.value = filterValue;
    }
}

function renderContentTypeOptions({ includeAll, selectedValue, channel }) {
    const families = contentTypeFamilies();
    const types = contentTypeList();
    const familyLabels = new Map(families.map(family => [family.key, family.label]));
    const familyOrder = families.map(family => family.key);
    const grouped = new Map();
    types.forEach(type => {
        if (!contentTypeAllowedForChannel(type, channel, selectedValue)) return;
        if (!grouped.has(type.family)) grouped.set(type.family, []);
        grouped.get(type.family).push(type);
    });

    const groups = familyOrder
        .filter(familyKey => grouped.has(familyKey))
        .map(familyKey => {
            const options = grouped.get(familyKey).map(type =>
                `<option value="${escAttr(type.key)}">${escHtml(type.label)}</option>`
            ).join('');
            return `<optgroup label="${escAttr(familyLabels.get(familyKey) || familyKey)}">${options}</optgroup>`;
        }).join('');

    return `${includeAll ? '<option value="all">All content types</option>' : ''}${groups}`;
}

function updateContentTypeGuidance() {
    const category = document.getElementById('contentCategory')?.value || 'headline';
    const meta = contentTypeMeta(category);
    const hint = document.getElementById('contentTypeHint');
    const proofSourceField = document.getElementById('contentProofSourceField');
    const proofPermissionField = document.getElementById('contentProofPermissionField');
    const showTrustFields = Boolean(meta?.proof_sensitive);

    if (hint) {
        const pageText = meta && meta.page_usable === false ? ' Not inserted directly into page sections.' : '';
        hint.textContent = meta ? `${meta.description}${pageText}` : '';
    }
    if (proofSourceField) proofSourceField.style.display = showTrustFields ? '' : 'none';
    if (proofPermissionField) proofPermissionField.style.display = showTrustFields ? '' : 'none';
    renderContentSlotFields(meta);
}

function renderContentSlotFields(meta) {
    const container = document.getElementById('contentSlotFields');
    if (!container) return;
    const slots = meta?.slot_schema || [];
    if (!slots.length) {
        container.style.display = 'none';
        container.innerHTML = '';
        return;
    }
    container.style.display = '';
    container.innerHTML = slots.map(slot => {
        const max = slot.max_length ? ` maxlength="${escAttr(slot.max_length)}"` : '';
        const placeholder = slot.placeholder || slot.help_text || '';
        const controlType = slot.type || slot.control_type || slot.primitive_type || 'text';
        const isLong = controlType === 'textarea'
            || ['paragraph', 'details', 'answer', 'quote', 'response', 'supporting_points', 'proof_note', 'story', 'body', 'description', 'post_copy', 'meta_description'].includes(slot.key);
        const inputType = ['url', 'date', 'number'].includes(controlType) ? controlType : 'text';
        const input = isLong
            ? `<textarea class="dash-input" data-content-slot="${escAttr(slot.key)}" rows="3" placeholder="${escAttr(placeholder)}"></textarea>`
            : `<input class="dash-input" data-content-slot="${escAttr(slot.key)}" type="${escAttr(inputType)}"${max} placeholder="${escAttr(placeholder)}">`;
        return `<div class="dash-field">
            <label class="dash-label">${escHtml(slot.label || slot.key)}${slot.required ? ' *' : ''}</label>
            ${input}
            ${slot.help_text ? `<span class="dash-hint">${escHtml(slot.help_text)}</span>` : ''}
        </div>`;
    }).join('');
}

function collectContentSlots() {
    const slots = {};
    document.querySelectorAll('[data-content-slot]').forEach(input => {
        const key = input.dataset.contentSlot;
        const value = input.value.trim();
        if (key && value) slots[key] = value;
    });
    return slots;
}

function applyContentSlots(slots) {
    Object.entries(slots || {}).forEach(([key, value]) => {
        const input = document.querySelector(`[data-content-slot="${CSS.escape(key)}"]`);
        if (input) input.value = value;
    });
}

function focusFirstContentSlot() {
    document.querySelector('[data-content-slot]')?.focus();
}

function strongestContentFromSlots(category, payload) {
    const preferred = {
        cta: ['paragraph', 'headline', 'button_label'],
        faq: ['answer', 'question'],
        testimonial: ['quote'],
        offer: ['details', 'headline', 'cta_label'],
        value_proposition: ['paragraph', 'headline'],
        benefit: ['paragraph', 'headline'],
        product_feature: ['paragraph', 'headline'],
        objection: ['response', 'concern'],
        comparison: ['differentiator', 'subject'],
    }[category] || [];
    const schemaOrder = (contentTypeMeta(category)?.slot_schema || [])
        .map(slot => slot.key)
        .filter(Boolean);
    const order = preferred.length ? preferred.concat(schemaOrder.filter(key => !preferred.includes(key))) : schemaOrder;
    for (const key of order) {
        if (payload[key]) return payload[key];
    }
    return '';
}

function renderContentList() {
    const container = document.getElementById('dashContentList');
    const items = contentItems;
    const showFolderCards = !contentFolderFilter;
    const folderCardsHtml = showFolderCards ? renderContentFolderCards() : '';
    const folderContextHtml = renderContentFolderContext();
    updateContentFolderActionVisibility();

    if (!items.length && !folderCardsHtml) {
        const sectionName = categoryLabel(contentFilter);
        container.innerHTML = `${folderContextHtml}<p class="dash-empty-text">${contentFilter === 'all' ? 'No content saved yet. Save messages from campaigns or add items manually.' : `No ${sectionName} items match these filters.`}</p>`;
        bindContentFolderCardActions(container);
        return;
    }

    const contentCardsHtml = items.map(item => {
        const pinnedClass = item.is_pinned ? ' pinned' : '';
        const brandName = item.brand?.name || (item.brand_id ? getBrandName(item.brand_id) : 'Shared');
        const productName = item.product?.name || (item.product_id ? getProductName(item.product_id) : '');
        const folderName = item.folder?.name || (item.folder_id ? getFolderName(item.folder_id) : '');
        const tags = Array.isArray(item.tags) ? item.tags : [];
        const expiry = item.expires_at ? formatShortDate(item.expires_at) : '';
        const score = item.quality_score !== null && item.quality_score !== undefined ? `${item.quality_score}/100` : '';
        return `<div class="dash-content-item${pinnedClass}" data-id="${item.id}">
            <div class="dash-content-body">
                <div class="dash-content-topline">
                    <span class="dash-content-category">${categoryLabel(item.category)}</span>
                    <span class="dash-content-status dash-content-status--${escAttr(item.status)}">${statusLabel(item.status)}</span>
                    <span class="dash-content-title">${escHtml(item.channel || 'general')}</span>
                    <span class="dash-content-title">${escHtml(item.source || 'manual')}</span>
                </div>
                ${item.title ? `<h4 class="dash-content-heading">${escHtml(item.title)}</h4>` : ''}
                <p class="dash-content-text">${escHtml(item.content)}</p>
                <div class="dash-content-meta">
                    <span class="dash-content-title">${escHtml(brandName)}</span>
                    ${productName ? `<span class="dash-content-title">${escHtml(productName)}</span>` : ''}
                    ${folderName ? `<span class="dash-content-title">${escHtml(folderName)}</span>` : ''}
                    ${expiry ? `<span class="dash-content-title">Expires ${escHtml(expiry)}</span>` : ''}
                    ${score ? `<span class="dash-content-title">Score ${escHtml(score)}</span>` : ''}
                    ${item.proof_permission_status ? `<span class="dash-content-title">Permission: ${escHtml(item.proof_permission_status.replace(/_/g, ' '))}</span>` : ''}
                    ${tags.map(tag => `<span class="dash-content-tag">${escHtml(tag)}</span>`).join('')}
                </div>
            </div>
            <div class="dash-content-actions">
                <button class="dash-btn dash-btn--ghost dash-btn--sm" data-edit-content="${item.id}">Edit</button>
                <button class="dash-btn dash-btn--ghost dash-btn--sm dash-btn--ai-section" data-ai-section-content="${item.id}" title="Create a section from this content">Create section</button>
                ${item.status === 'draft' ? `<button class="dash-btn dash-btn--ghost dash-btn--sm" data-status-content="${item.id}" data-status="approved">Approve</button>` : ''}
                ${item.status !== 'archived' ? `<button class="dash-btn dash-btn--ghost dash-btn--sm" data-status-content="${item.id}" data-status="archived">Archive</button>` : ''}
                <button class="dash-btn dash-btn--ghost dash-btn--icon${item.is_pinned ? ' is-pinned' : ''}" data-pin-content="${item.id}" title="${item.is_pinned ? 'Unpin' : 'Pin'}">
                    ${item.is_pinned
                        ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;"><path d="M12 17v5"/><path d="M15 9.34V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H7.89"/><path d="m2 2 20 20"/><path d="M9 9v1.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h11"/></svg>`
                        : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;"><path d="M12 17v5"/><path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/></svg>`
                    }
                </button>
                <button class="dash-btn dash-btn--ghost dash-btn--icon dash-btn--danger" data-delete-content="${item.id}" title="Delete">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M18 6 6 18M6 6l12 12"/></svg>
                </button>
            </div>
        </div>`;
    }).join('');

    const emptyContentHtml = !items.length
        ? '<p class="dash-empty-text">No content saved at this level yet.</p>'
        : '';
    container.innerHTML = `${folderContextHtml}${folderCardsHtml}${contentCardsHtml}${emptyContentHtml}`;
    bindContentFolderCardActions(container);
    bindContentActions(container);
}

function renderContentFolderContext() {
    if (!contentFolderFilter) return '';
    const label = contentFolderFilter === 'unfiled'
        ? 'Unfiled'
        : (selectedContentFolder()?.name || 'Folder');
    return `<div class="dash-content-folder-context">
        <span class="dash-section-hint">Folder: ${escHtml(label)}</span>
        <button class="dash-btn dash-btn--outline dash-btn--sm" type="button" data-open-folder="">Back to library</button>
    </div>`;
}

function renderContentFolderCards() {
    if (!contentFolders.length) return '';
    return `<div class="dash-folder-card-grid">
        ${contentFolders.map(folder => {
            const selected = folder.id === selectedContentFolderId;
            return `<div class="dash-folder-card${selected ? ' is-selected' : ''}" data-open-folder="${escAttr(folder.id)}" role="button" tabindex="0">
            <button type="button" class="dash-folder-checkbox" data-select-folder="${escAttr(folder.id)}" aria-pressed="${selected ? 'true' : 'false'}" title="${selected ? 'Deselect folder' : 'Select folder'}">
                ${selected ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>` : ''}
            </button>
            <span class="dash-folder-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H10l2 2h6.5A2.5 2.5 0 0 1 21 9.5v7A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5z"/>
                </svg>
            </span>
            <span class="dash-folder-card-body">
                <span class="dash-folder-name">${escHtml(folder.name)}</span>
                ${folder.description ? `<span class="dash-folder-meta">${escHtml(folder.description)}</span>` : '<span class="dash-folder-meta">Content folder</span>'}
            </span>
        </div>`;
        }).join('')}
    </div>`;
}

function bindContentFolderCardActions(container) {
    container.querySelectorAll('[data-select-folder]').forEach(btn => {
        btn.addEventListener('click', event => {
            event.stopPropagation();
            const folderId = btn.dataset.selectFolder || '';
            selectedContentFolderId = selectedContentFolderId === folderId ? '' : folderId;
            renderContentList();
        });
    });
    container.querySelectorAll('[data-open-folder]').forEach(btn => {
        btn.addEventListener('click', () => {
            contentFolderFilter = btn.dataset.openFolder || '';
            selectedContentFolderId = '';
            const filter = document.getElementById('contentFolderFilter');
            if (filter) filter.value = contentFolderFilter;
            loadContent();
        });
        btn.addEventListener('keydown', event => {
            if (event.key !== 'Enter' && event.key !== ' ') return;
            event.preventDefault();
            btn.click();
        });
    });
}

function getBrandName(brandId) {
    const brand = brands.find(b => b.id === brandId);
    return brand ? brand.name : 'Brand';
}

function getProductName(productId) {
    const product = products.find(p => p.id === productId);
    return product ? product.name : 'Product';
}

function getFolderName(folderId) {
    const folder = contentFolders.find(f => f.id === folderId);
    return folder ? folder.name : 'Folder';
}

function bindContentActions(container) {
    container.querySelectorAll('[data-edit-content]').forEach(btn => {
        btn.addEventListener('click', () => editContentItem(btn.dataset.editContent));
    });

    container.querySelectorAll('[data-ai-section-content]').forEach(btn => {
        btn.addEventListener('click', () => draftSectionFromContent(btn));
    });

    container.querySelectorAll('[data-delete-content]').forEach(btn => {
        btn.addEventListener('click', async () => {
            try {
                await apiFetch(`/api/content/${btn.dataset.deleteContent}`, { method: 'DELETE' });
                contentItems = contentItems.filter(i => i.id !== btn.dataset.deleteContent);
                renderContentList();
            } catch (e) {
                await showMessageModal({ title: 'Delete failed', message: e.message });
            }
        });
    });

    container.querySelectorAll('[data-pin-content]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const item = contentItems.find(i => i.id === btn.dataset.pinContent);
            if (!item) return;
            try {
                const updated = await apiFetch(`/api/content/${item.id}`, {
                    method: 'PATCH',
                    body: JSON.stringify({ is_pinned: !item.is_pinned }),
                });
                Object.assign(item, updated);
                renderContentList();
            } catch (e) {
                await showMessageModal({ title: 'Update failed', message: e.message });
            }
        });
    });

    container.querySelectorAll('[data-status-content]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const item = contentItems.find(i => i.id === btn.dataset.statusContent);
            if (!item) return;
            try {
                const updated = await apiFetch(`/api/content/${item.id}`, {
                    method: 'PATCH',
                    body: JSON.stringify({ status: btn.dataset.status }),
                });
                Object.assign(item, updated);
                renderContentList();
            } catch (e) {
                await showMessageModal({ title: 'Update failed', message: e.message });
            }
        });
    });
}

async function draftSectionFromContent(btn) {
    const contentId = btn.dataset.aiSectionContent;
    if (!contentId) return;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Drafting...';
    try {
        const result = await apiFetch('/api/chat/generate-section', {
            method: 'POST',
            body: JSON.stringify({ seed_content_id: contentId, brand_id: contentBrandFilter || activeBrandId || null }),
        });
        if (result.created_draft_ids && result.created_draft_ids.length) {
            await loadContent();
        }
        await loadSectionTypes();
        sectionPickerItems = contentItems.slice();
        (result.section?.items || []).forEach(item => {
            if (item && item.id && !sectionPickerItems.some(existing => existing.id === item.id)) {
                sectionPickerItems.push(item);
            }
        });
        await switchContentTab('sections');
        showSectionEditor(null, result.section);
    } catch (e) {
        await showMessageModal({ title: 'Section draft failed', message: e.message });
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

function bindContentFilters() {
    const search = document.getElementById('contentSearch');
    let searchTimer = null;
    if (search && !search.dataset.bound) {
        search.dataset.bound = 'true';
        search.addEventListener('input', () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                contentSearch = search.value.trim();
                loadContent();
            }, 180);
        });
    }

    [
        ['contentSectionFilter', value => { contentFilter = value || 'all'; }],
        ['contentBrandFilter', value => { contentBrandFilter = value; }],
        ['contentProductFilter', value => { contentProductFilter = value; }],
        ['contentFolderFilter', value => {
            contentFolderFilter = value;
            selectedContentFolderId = '';
        }],
        ['contentStatusFilter', value => { contentStatusFilter = value; }],
        ['contentSourceFilter', value => { contentSourceFilter = value; }],
    ].forEach(([id, setter]) => {
        const el = document.getElementById(id);
        if (!el || el.dataset.bound) return;
        el.dataset.bound = 'true';
        el.addEventListener('change', () => {
            setter(el.value);
            loadContent();
        });
    });

    bindContentFolderControls();
}

function selectedContentFolder() {
    return contentFolders.find(folder => folder.id === selectedContentFolderId) || null;
}

function updateContentFolderActionVisibility() {
    const toolbar = document.querySelector('.dash-content-folder-bar');
    const actions = document.getElementById('contentFolderSelectedActions');
    const renameBtn = document.getElementById('renameContentFolder');
    const deleteBtn = document.getElementById('deleteContentFolder');
    const isTopLevel = !contentFolderFilter;
    const hasSelection = isTopLevel && Boolean(selectedContentFolder());
    if (toolbar) toolbar.style.display = isTopLevel ? 'flex' : 'none';
    if (actions) actions.style.display = hasSelection ? 'inline-flex' : 'none';
    if (renameBtn) renameBtn.disabled = !hasSelection;
    if (deleteBtn) deleteBtn.disabled = !hasSelection;
}

function refreshContentFolders() {
    contentFoldersLoaded = false;
    return loadContentFolders().then(() => {
        if (contentFolderFilter && contentFolderFilter !== 'unfiled' && !contentFolders.some(folder => folder.id === contentFolderFilter)) {
            contentFolderFilter = '';
        }
        if (selectedContentFolderId && !contentFolders.some(folder => folder.id === selectedContentFolderId)) {
            selectedContentFolderId = '';
        }
        renderContentScopeOptions();
        return loadContent();
    });
}

async function renameSelectedContentFolder() {
    const folder = selectedContentFolder();
    if (!folder) {
        await showMessageModal({ title: 'Select a folder', message: 'Select a folder first.' });
        return;
    }
    const name = await showTextPrompt({
        title: 'Rename folder',
        message: 'Update the selected content folder name.',
        value: folder.name,
        confirmText: 'Rename folder',
    });
    if (!name) return;
    try {
        await apiFetch(`/api/content/folders/${folder.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ name }),
        });
        await refreshContentFolders();
    } catch (e) {
        await showMessageModal({ title: 'Folder rename failed', message: e.message });
    }
}

async function deleteSelectedContentFolder() {
    const folder = selectedContentFolder();
    if (!folder) {
        await showMessageModal({ title: 'Select a folder', message: 'Select a folder first.' });
        return;
    }
    const confirmed = await showConfirmModal({
        title: 'Delete folder',
        message: `Delete folder "${folder.name}"? Content will become unfiled.`,
        confirmText: 'Delete',
        danger: true,
    });
    if (!confirmed) return;
    try {
        await apiFetch(`/api/content/folders/${folder.id}`, { method: 'DELETE' });
        selectedContentFolderId = '';
        contentFolderFilter = '';
        await refreshContentFolders();
    } catch (e) {
        await showMessageModal({ title: 'Folder delete failed', message: e.message });
    }
}

function bindContentFolderControls() {
    const addBtn = document.getElementById('addContentFolder');
    const renameBtn = document.getElementById('renameContentFolder');
    const deleteBtn = document.getElementById('deleteContentFolder');

    if (addBtn && !addBtn.dataset.bound) {
        addBtn.dataset.bound = 'true';
        addBtn.addEventListener('click', async () => {
            const name = await showTextPrompt({
                title: 'New folder',
                message: 'Create a folder for organizing content items.',
                placeholder: 'Homepage sections',
                confirmText: 'Create folder',
            });
            if (!name) {
                return;
            }
            const originalText = addBtn.textContent;
            addBtn.disabled = true;
            addBtn.textContent = 'Creating...';
            try {
                const folder = await apiFetch('/api/content/folders', {
                    method: 'POST',
                    body: JSON.stringify({ name }),
                });
                selectedContentFolderId = folder.id;
                contentFolderFilter = '';
                await refreshContentFolders();
            } catch (e) {
                await showMessageModal({ title: 'Folder create failed', message: e.message });
            } finally {
                addBtn.disabled = false;
                addBtn.textContent = originalText;
            }
        });
    }

    if (renameBtn && !renameBtn.dataset.bound) {
        renameBtn.dataset.bound = 'true';
        renameBtn.addEventListener('click', renameSelectedContentFolder);
    }

    if (deleteBtn && !deleteBtn.dataset.bound) {
        deleteBtn.dataset.bound = 'true';
        deleteBtn.addEventListener('click', deleteSelectedContentFolder);
    }
}

function bindAddContent() {
    const addBtn = document.getElementById('addContentBtn');
    const confirmBtn = document.getElementById('confirmAddContent');
    const categorySelect = document.getElementById('contentCategory');
    const channelSelect = document.getElementById('contentChannel');
    const enhanceBtn = document.getElementById('enhanceContentFormat');
    const cancelBtns = [
        document.getElementById('cancelAddContent'),
        document.getElementById('cancelAddContentSecondary'),
    ].filter(Boolean);
    if (!addBtn || !confirmBtn) return;

    if (!addBtn.dataset.bound) {
        addBtn.dataset.bound = 'true';
        addBtn.addEventListener('click', showContentEditor);
    }

    cancelBtns.forEach(btn => {
        if (btn.dataset.bound) return;
        btn.dataset.bound = 'true';
        btn.addEventListener('click', hideContentEditor);
    });

    if (categorySelect && !categorySelect.dataset.bound) {
        categorySelect.dataset.bound = 'true';
        categorySelect.addEventListener('change', updateContentTypeGuidance);
    }

    if (channelSelect && !channelSelect.dataset.bound) {
        channelSelect.dataset.bound = 'true';
        channelSelect.addEventListener('change', () => {
            renderContentTypeControls();
            updateContentTypeGuidance();
        });
    }

    if (enhanceBtn && !enhanceBtn.dataset.bound) {
        enhanceBtn.dataset.bound = 'true';
        enhanceBtn.addEventListener('click', enhanceContentFormat);
    }

    if (confirmBtn.dataset.bound) return;
    confirmBtn.dataset.bound = 'true';
    confirmBtn.addEventListener('click', async () => {
        const category = document.getElementById('contentCategory').value;
        const status = document.getElementById('contentStatus').value;
        const source = document.getElementById('contentSource').value;
        const channel = document.getElementById('contentChannel').value;
        const brandId = document.getElementById('contentBrandId').value || null;
        const productId = document.getElementById('contentProductId').value || null;
        const folderId = document.getElementById('contentFolderId').value || null;
        const title = document.getElementById('contentTitle').value.trim();
        const tags = document.getElementById('contentTags').value.trim();
        const slots = collectContentSlots();
        const content = strongestContentFromSlots(category, slots);
        const proofSource = document.getElementById('contentProofSource').value.trim();
        const proofPermission = document.getElementById('contentProofPermission').value;
        const expiresAt = document.getElementById('contentExpiresAt').value;
        const qualityScore = document.getElementById('contentQualityScore').value;

        if (!content) {
            setContentEditorError('Content is required.');
            return;
        }

        confirmBtn.disabled = true;
        const editing = Boolean(editingContentId);
        confirmBtn.textContent = editing ? 'Saving...' : 'Adding...';
        setContentEditorError('');

        try {
            const brand = brands.find(b => b.id === brandId);
            await apiFetch(editing ? `/api/content/${editingContentId}` : '/api/content', {
                method: editing ? 'PATCH' : 'POST',
                body: JSON.stringify({
                    category,
                    status,
                    source,
                    channel,
                    title,
                    slots,
                    brand_id: brandId,
                    product_id: productId,
                    folder_id: folderId,
                    tone: brand?.tone || null,
                    tags,
                    proof_source: proofSource,
                    proof_permission_status: proofPermission || null,
                    expires_at: expiresAt || null,
                    quality_score: qualityScore || null,
                }),
            });
            await loadContent();
            hideContentEditor();
        } catch (e) {
            setContentEditorError(`Failed to ${editing ? 'update' : 'add'}: ${e.message}`);
        } finally {
            confirmBtn.disabled = false;
            setContentEditorMode(editingContentId);
        }
    });
}

async function enhanceContentFormat() {
    const button = document.getElementById('enhanceContentFormat');
    const category = document.getElementById('contentCategory')?.value || 'headline';
    const slots = collectContentSlots();
    const content = strongestContentFromSlots(category, slots);
    if (!content) {
        setContentEditorError('Add slot content first, then enhance the slots.');
        return;
    }
    const originalText = button?.textContent || 'Enhance format';
    if (button) {
        button.disabled = true;
        button.textContent = 'Enhancing...';
    }
    setContentEditorError('');
    try {
        const result = await apiFetch('/api/chat/enhance-content', {
            method: 'POST',
            body: JSON.stringify({
                mode: 'format',
                channel: document.getElementById('contentChannel')?.value || 'general',
                content_type: category,
                brand_id: document.getElementById('contentBrandId')?.value || null,
                product_id: document.getElementById('contentProductId')?.value || null,
                title: document.getElementById('contentTitle')?.value.trim() || '',
                content,
                slots,
                tags: document.getElementById('contentTags')?.value.trim() || '',
            }),
        });
        if (result.slots) applyContentSlots(result.slots);
    } catch (e) {
        setContentEditorError(e.message || 'Enhance failed.');
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
}

function showContentEditor() {
    editingContentId = null;
    renderContentScopeOptions();
    resetContentEditor();
    applyCurrentFolderToNewContent();
    setContentEditorMode(null);
    document.getElementById('dashContentListView').style.display = 'none';
    document.getElementById('dashContentEditorView').style.display = '';
    focusFirstContentSlot();
}

function hideContentEditor() {
    editingContentId = null;
    document.getElementById('dashContentEditorView').style.display = 'none';
    document.getElementById('dashContentListView').style.display = '';
    setContentEditorError('');
    setContentEditorMode(null);
}

function resetContentEditor() {
    setContentCategory('headline');
    document.getElementById('contentStatus').value = 'approved';
    document.getElementById('contentSource').value = 'manual';
    document.getElementById('contentChannel').value = 'general';
    document.getElementById('contentBrandId').value = activeBrandId || '';
    document.getElementById('contentProductId').value = '';
    document.getElementById('contentFolderId').value = '';
    document.getElementById('contentTitle').value = '';
    document.getElementById('contentTags').value = '';
    document.getElementById('contentProofSource').value = '';
    document.getElementById('contentProofPermission').value = '';
    document.getElementById('contentExpiresAt').value = '';
    document.getElementById('contentQualityScore').value = '';
    setContentEditorError('');
    updateContentTypeGuidance();
}

function applyCurrentFolderToNewContent() {
    const folderInput = document.getElementById('contentFolderId');
    if (!folderInput || !contentFolderFilter || contentFolderFilter === 'unfiled') return;
    folderInput.value = contentFolderFilter;
}

function editContentItem(itemId) {
    const item = contentItems.find(entry => entry.id === itemId);
    if (!item) return;

    editingContentId = item.id;
    renderContentScopeOptions();
    resetContentEditor();
    setContentEditorMode(item.id);

    document.getElementById('contentChannel').value = item.channel || 'general';
    document.getElementById('contentCategory').value = item.category || 'headline';
    renderContentTypeControls();
    setContentCategory(item.category || 'headline');
    document.getElementById('contentStatus').value = item.status || 'approved';
    document.getElementById('contentSource').value = item.source || 'manual';
    document.getElementById('contentBrandId').value = item.brand_id || '';
    document.getElementById('contentProductId').value = item.product_id || '';
    document.getElementById('contentFolderId').value = item.folder_id || '';
    document.getElementById('contentTitle').value = item.title || '';
    document.getElementById('contentTags').value = Array.isArray(item.tags) ? item.tags.join(', ') : '';
    document.getElementById('contentProofSource').value = item.proof_source || '';
    document.getElementById('contentProofPermission').value = item.proof_permission_status || '';
    document.getElementById('contentExpiresAt').value = item.expires_at ? String(item.expires_at).slice(0, 10) : '';
    document.getElementById('contentQualityScore').value = item.quality_score ?? '';
    applyContentSlots(item.slots || {});
    setContentEditorError('');

    document.getElementById('dashContentListView').style.display = 'none';
    document.getElementById('dashContentEditorView').style.display = '';
    focusFirstContentSlot();
}

function setContentEditorMode(itemId) {
    const title = document.getElementById('contentEditorTitle');
    const hint = document.getElementById('contentEditorHint');
    const confirmBtn = document.getElementById('confirmAddContent');
    const editing = Boolean(itemId);
    if (title) title.textContent = editing ? 'Edit content' : 'Add content';
    if (hint) {
        hint.textContent = editing
            ? 'Update reusable copy used by campaigns, pages, and generated sections.'
            : 'Create reusable copy that campaigns, pages, and AI generation can pull from later.';
    }
    if (confirmBtn) confirmBtn.textContent = editing ? 'Save changes' : 'Add to library';
}

function setContentCategory(category) {
    const selected = category || 'headline';
    const input = document.getElementById('contentCategory');
    if (input) input.value = selected;
    updateContentTypeGuidance();
}

function setContentEditorError(message) {
    const error = document.getElementById('contentEditorError');
    if (!error) return;
    error.textContent = message || '';
    error.style.display = message ? '' : 'none';
}

// =============================================================================
// Sections (Content view → Sections tab)
// =============================================================================

function bindContentTabs() {
    const tabs = document.querySelectorAll('[data-content-tab]');
    if (!tabs.length) return;
    tabs.forEach(tab => {
        if (tab.dataset.bound) return;
        tab.dataset.bound = 'true';
        tab.addEventListener('click', () => switchContentTab(tab.dataset.contentTab));
    });
}

function switchContentTab(tab) {
    document.querySelectorAll('[data-content-tab]').forEach(btn => {
        btn.classList.toggle('dash-content-tab--active', btn.dataset.contentTab === tab);
    });
    document.querySelectorAll('[data-content-tab-panel]').forEach(panel => {
        panel.style.display = panel.dataset.contentTabPanel === tab ? '' : 'none';
    });
    if (tab === 'sections') return loadSectionsView();
    return Promise.resolve();
}

async function loadSectionsView() {
    // Sections need brands (for the brand select) + content (for the picker).
    await Promise.all([loadBrands(), loadContent(), loadSectionTypes()]);
    sectionPickerItems = contentItems.slice();
    renderSectionScopeOptions();
    await loadSections();
}

async function loadSectionTypes() {
    if (sectionTypesLoaded) return;
    try {
        sectionTypes = await apiFetch('/api/sections/types');
        sectionTypesLoaded = true;
    } catch (e) {
        sectionTypes = [{ key: 'custom', label: 'Custom', suggested_categories: [] }];
        sectionTypesLoaded = true;
    }
}

function renderSectionScopeOptions() {
    const brandFilter = document.getElementById('sectionBrandFilter');
    const editorBrand = document.getElementById('sectionBrandId');
    const editorType = document.getElementById('sectionType');
    const brandOptionsHtml = brands.map(brand =>
        `<option value="${escAttr(brand.id)}">${escHtml(brand.name)}</option>`
    ).join('');
    if (brandFilter) {
        const current = brandFilter.value;
        brandFilter.innerHTML = '<option value="">All brands</option><option value="shared">Shared only</option>' + brandOptionsHtml;
        brandFilter.value = current;
    }
    if (editorBrand) {
        const current = editorBrand.value;
        editorBrand.innerHTML = '<option value="">Shared / org default</option>' + brandOptionsHtml;
        editorBrand.value = current || activeBrandId || '';
    }
    if (editorType) {
        const current = editorType.value || 'custom';
        const typeOptionsHtml = (sectionTypes.length ? sectionTypes : [{ key: 'custom', label: 'Custom' }]).map(type =>
            `<option value="${escAttr(type.key)}">${escHtml(type.label)}</option>`
        ).join('');
        editorType.innerHTML = typeOptionsHtml;
        editorType.value = sectionTypes.some(type => type.key === current) ? current : 'custom';
    }
}

async function loadSections() {
    try {
        const params = new URLSearchParams();
        if (sectionSearch) params.set('q', sectionSearch);
        if (sectionBrandFilter) params.set('brand_id', sectionBrandFilter);
        if (sectionStatusFilter) params.set('status', sectionStatusFilter);
        const query = params.toString();
        sectionItems = await apiFetch(`/api/sections${query ? `?${query}` : ''}`);
        sectionsLoaded = true;
        renderSectionList();
    } catch (e) {
        const list = document.getElementById('dashSectionList');
        if (list) list.innerHTML = '<p class="dash-empty-text">Failed to load sections.</p>';
    }
}

function renderSectionList() {
    const container = document.getElementById('dashSectionList');
    if (!container) return;

    if (!sectionItems.length) {
        container.innerHTML = '<p class="dash-empty-text">No sections yet. Create one to compose reusable page blocks from your content.</p>';
        return;
    }

    container.innerHTML = sectionItems.map(section => {
        const pinnedClass = section.is_pinned ? ' pinned' : '';
        const brandName = section.brand?.name || (section.brand_id ? getBrandName(section.brand_id) : 'Shared');
        const tags = Array.isArray(section.tags) ? section.tags : [];
        const chips = (section.items || []).map(it =>
            `<span class="dash-content-tag">${escHtml(categoryLabel(it.category))}</span>`
        ).join('');
        const missing = section.missing_count
            ? `<span class="dash-content-title">${section.missing_count} missing</span>` : '';
        return `<div class="dash-content-item${pinnedClass}" data-id="${escAttr(section.id)}">
            <div class="dash-content-body">
                <div class="dash-content-topline">
                    <span class="dash-content-category">${escHtml(section.section_type_label || 'Section')}</span>
                    <span class="dash-content-status dash-content-status--${escAttr(section.status)}">${statusLabel(section.status)}</span>
                    <span class="dash-content-title">${escHtml(String(section.item_count))} item${section.item_count === 1 ? '' : 's'}</span>
                </div>
                <h4 class="dash-content-heading">${escHtml(section.name)}</h4>
                ${section.description ? `<p class="dash-content-text">${escHtml(section.description)}</p>` : ''}
                <div class="dash-content-meta">
                    <span class="dash-content-title">${escHtml(brandName)}</span>
                    ${missing}
                    ${chips}
                    ${tags.map(tag => `<span class="dash-content-tag">${escHtml(tag)}</span>`).join('')}
                </div>
            </div>
            <div class="dash-content-actions">
                <button class="dash-btn dash-btn--ghost dash-btn--sm" data-view-section="${escAttr(section.id)}" title="Preview">View</button>
                <button class="dash-btn dash-btn--ghost dash-btn--sm" data-edit-section="${escAttr(section.id)}">Edit</button>
                <button class="dash-btn dash-btn--ghost dash-btn--icon${section.is_pinned ? ' is-pinned' : ''}" data-pin-section="${escAttr(section.id)}" title="${section.is_pinned ? 'Unpin' : 'Pin'}">
                    ${section.is_pinned
                        ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;"><path d="M12 17v5"/><path d="M15 9.34V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H7.89"/><path d="m2 2 20 20"/><path d="M9 9v1.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h11"/></svg>`
                        : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:15px;height:15px;"><path d="M12 17v5"/><path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/></svg>`
                    }
                </button>
                <button class="dash-btn dash-btn--ghost dash-btn--icon dash-btn--danger" data-delete-section="${escAttr(section.id)}" title="Delete">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M18 6 6 18M6 6l12 12"/></svg>
                </button>
            </div>
        </div>`;
    }).join('');

    bindSectionActions(container);
}

function bindSectionActions(container) {
    container.querySelectorAll('[data-view-section]').forEach(btn => {
        btn.addEventListener('click', () => openSectionPreview(btn.dataset.viewSection));
    });
    container.querySelectorAll('[data-edit-section]').forEach(btn => {
        btn.addEventListener('click', () => showSectionEditor(btn.dataset.editSection));
    });
    container.querySelectorAll('[data-delete-section]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const confirmed = await showConfirmModal({
                title: 'Delete section',
                message: 'Delete this section? Content items are not affected.',
                confirmText: 'Delete',
                danger: true,
            });
            if (!confirmed) return;
            try {
                await apiFetch(`/api/sections/${btn.dataset.deleteSection}`, { method: 'DELETE' });
                sectionItems = sectionItems.filter(s => s.id !== btn.dataset.deleteSection);
                renderSectionList();
            } catch (e) {
                await showMessageModal({ title: 'Delete failed', message: e.message });
            }
        });
    });
    container.querySelectorAll('[data-pin-section]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const section = sectionItems.find(s => s.id === btn.dataset.pinSection);
            if (!section) return;
            try {
                const updated = await apiFetch(`/api/sections/${section.id}`, {
                    method: 'PATCH',
                    body: JSON.stringify({ is_pinned: !section.is_pinned }),
                });
                Object.assign(section, updated);
                renderSectionList();
            } catch (e) {
                await showMessageModal({ title: 'Update failed', message: e.message });
            }
        });
    });
}

function bindSections() {
    const addBtn = document.getElementById('addSectionBtn');
    if (addBtn && !addBtn.dataset.bound) {
        addBtn.dataset.bound = 'true';
        addBtn.addEventListener('click', () => showSectionEditor(null));
    }

    [document.getElementById('cancelSection'), document.getElementById('cancelSectionSecondary')]
        .filter(Boolean).forEach(btn => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = 'true';
            btn.addEventListener('click', hideSectionEditor);
        });

    const confirmBtn = document.getElementById('confirmSaveSection');
    if (confirmBtn && !confirmBtn.dataset.bound) {
        confirmBtn.dataset.bound = 'true';
        confirmBtn.addEventListener('click', saveSection);
    }

    // Section list filters
    const search = document.getElementById('sectionSearch');
    let searchTimer = null;
    if (search && !search.dataset.bound) {
        search.dataset.bound = 'true';
        search.addEventListener('input', () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                sectionSearch = search.value.trim();
                loadSections();
            }, 180);
        });
    }
    [
        ['sectionBrandFilter', value => { sectionBrandFilter = value; }],
        ['sectionStatusFilter', value => { sectionStatusFilter = value; }],
    ].forEach(([id, setter]) => {
        const el = document.getElementById(id);
        if (!el || el.dataset.bound) return;
        el.dataset.bound = 'true';
        el.addEventListener('change', () => { setter(el.value); loadSections(); });
    });

    // Editor picker search
    const pickerSearch = document.getElementById('sectionPickerSearch');
    if (pickerSearch && !pickerSearch.dataset.bound) {
        pickerSearch.dataset.bound = 'true';
        pickerSearch.addEventListener('input', () => {
            sectionPickerSearch = pickerSearch.value.trim().toLowerCase();
            renderSectionPicker();
        });
    }

    const typeSelect = document.getElementById('sectionType');
    if (typeSelect && !typeSelect.dataset.bound) {
        typeSelect.dataset.bound = 'true';
        typeSelect.addEventListener('change', () => {
            renderSectionChosen();
            renderSectionPicker();
        });
    }
}

function showSectionEditor(sectionId, draft = null) {
    editingSectionId = sectionId || null;
    renderSectionScopeOptions();

    const titleEl = document.getElementById('sectionEditorTitle');
    if (draft) {
        if (titleEl) titleEl.textContent = 'Review AI section';
        (draft.items || []).forEach(item => {
            if (item && item.id && !sectionPickerItems.some(existing => existing.id === item.id)) {
                sectionPickerItems.push(item);
            }
        });
        document.getElementById('sectionName').value = draft.name || '';
        document.getElementById('sectionDescription').value = draft.description || '';
        document.getElementById('sectionStatus').value = draft.status || 'draft';
        document.getElementById('sectionType').value = draft.section_type || 'custom';
        document.getElementById('sectionBrandId').value = draft.brand_id || activeBrandId || '';
        document.getElementById('sectionTags').value = '';
        sectionDraftRefs = (draft.content_refs || []).slice();
    } else if (editingSectionId) {
        const section = sectionItems.find(s => s.id === editingSectionId);
        if (titleEl) titleEl.textContent = 'Edit section';
        document.getElementById('sectionName').value = section?.name || '';
        document.getElementById('sectionDescription').value = section?.description || '';
        document.getElementById('sectionStatus').value = section?.status || 'draft';
        document.getElementById('sectionType').value = section?.section_type || 'custom';
        document.getElementById('sectionBrandId').value = section?.brand_id || '';
        document.getElementById('sectionTags').value = (section?.tags || []).join(', ');
        sectionDraftRefs = (section?.content_refs || []).slice();
    } else {
        if (titleEl) titleEl.textContent = 'Add section';
        document.getElementById('sectionName').value = '';
        document.getElementById('sectionDescription').value = '';
        document.getElementById('sectionStatus').value = 'draft';
        document.getElementById('sectionType').value = 'custom';
        document.getElementById('sectionBrandId').value = activeBrandId || '';
        document.getElementById('sectionTags').value = '';
        sectionDraftRefs = [];
    }
    setSectionEditorError('');
    sectionPickerSearch = '';
    const pickerSearch = document.getElementById('sectionPickerSearch');
    if (pickerSearch) pickerSearch.value = '';

    document.getElementById('dashSectionListView').style.display = 'none';
    document.getElementById('dashSectionEditorView').style.display = '';

    renderSectionChosen();
    renderSectionPicker();
    document.getElementById('sectionName')?.focus();
}

function hideSectionEditor() {
    document.getElementById('dashSectionEditorView').style.display = 'none';
    document.getElementById('dashSectionListView').style.display = '';
    setSectionEditorError('');
}

// Resolve a content item (from the loaded picker list) by id.
function sectionContentById(id) {
    return sectionPickerItems.find(c => c.id === id);
}

function getSelectedSectionType() {
    return document.getElementById('sectionType')?.value || 'custom';
}

function getSectionTypeDef(key) {
    return sectionTypes.find(type => type.key === key) || sectionTypes.find(type => type.key === 'custom') || { key: 'custom', label: 'Custom', suggested_categories: [] };
}

function getSuggestedSectionCategories() {
    return new Set(getSectionTypeDef(getSelectedSectionType()).suggested_categories || []);
}

function renderSectionTypeHint() {
    const type = getSectionTypeDef(getSelectedSectionType());
    const cats = type.suggested_categories || [];
    if (!cats.length) return '';
    return `<div class="dash-section-fit-hint">Best fit: ${cats.map(cat => `<span class="dash-content-tag">${escHtml(categoryLabel(cat))}</span>`).join('')}</div>`;
}

function renderSectionChosen() {
    const container = document.getElementById('sectionChosenList');
    if (!container) return;
    const suggested = getSuggestedSectionCategories();
    const hint = renderSectionTypeHint();
    if (!sectionDraftRefs.length) {
        container.innerHTML = `${hint}<p class="dash-empty-text">No content added yet. Pick items from the right.</p>`;
        return;
    }
    container.innerHTML = hint + sectionDraftRefs.map((id, idx) => {
        const item = sectionContentById(id);
        const mismatch = item && suggested.size && !suggested.has(item.category)
            ? '<span class="dash-section-mismatch">Check fit</span>'
            : '';
        const label = item
            ? `${categoryLabel(item.category)} · ${escHtml(item.title || (item.content || '').slice(0, 50))}`
            : `<em>Missing content (${escHtml(id)})</em>`;
        return `<div class="dash-section-chosen-row" data-ref-id="${escAttr(id)}">
            <span class="dash-section-chosen-order">${idx + 1}</span>
            <span class="dash-section-chosen-label">${item ? `<span class="dash-content-tag">${escHtml(categoryLabel(item.category))}</span> ${escHtml(item.title || (item.content || '').slice(0, 60))} ${mismatch}` : label}</span>
            <span class="dash-section-chosen-actions">
                <button class="dash-btn dash-btn--ghost dash-btn--icon" data-move-up="${idx}" title="Move up" ${idx === 0 ? 'disabled' : ''}>↑</button>
                <button class="dash-btn dash-btn--ghost dash-btn--icon" data-move-down="${idx}" title="Move down" ${idx === sectionDraftRefs.length - 1 ? 'disabled' : ''}>↓</button>
                <button class="dash-btn dash-btn--ghost dash-btn--icon dash-btn--danger" data-remove-ref="${idx}" title="Remove">✕</button>
            </span>
        </div>`;
    }).join('');

    container.querySelectorAll('[data-move-up]').forEach(btn => {
        btn.addEventListener('click', () => moveSectionRef(parseInt(btn.dataset.moveUp, 10), -1));
    });
    container.querySelectorAll('[data-move-down]').forEach(btn => {
        btn.addEventListener('click', () => moveSectionRef(parseInt(btn.dataset.moveDown, 10), 1));
    });
    container.querySelectorAll('[data-remove-ref]').forEach(btn => {
        btn.addEventListener('click', () => {
            sectionDraftRefs.splice(parseInt(btn.dataset.removeRef, 10), 1);
            renderSectionChosen();
            renderSectionPicker();
        });
    });
}

function moveSectionRef(idx, delta) {
    const next = idx + delta;
    if (next < 0 || next >= sectionDraftRefs.length) return;
    const [moved] = sectionDraftRefs.splice(idx, 1);
    sectionDraftRefs.splice(next, 0, moved);
    renderSectionChosen();
}

function renderSectionPicker() {
    const container = document.getElementById('sectionPickerList');
    if (!container) return;
    const chosen = new Set(sectionDraftRefs);
    const term = sectionPickerSearch;
    const suggested = getSuggestedSectionCategories();
    const available = sectionPickerItems.filter(item => {
        if (chosen.has(item.id)) return false;
        if (!term) return true;
        const hay = `${item.title || ''} ${item.content || ''} ${item.category || ''}`.toLowerCase();
        return hay.includes(term);
    }).sort((a, b) => {
        const aSuggested = suggested.has(a.category) ? 0 : 1;
        const bSuggested = suggested.has(b.category) ? 0 : 1;
        if (aSuggested !== bSuggested) return aSuggested - bSuggested;
        return String(a.title || a.content || '').localeCompare(String(b.title || b.content || ''));
    });

    if (!available.length) {
        container.innerHTML = '<p class="dash-empty-text">No matching content. Create content in the Content tab first.</p>';
        return;
    }

    container.innerHTML = available.map(item =>
        `<button type="button" class="dash-section-picker-row${suggested.has(item.category) ? ' dash-section-picker-row--suggested' : ''}" data-add-ref="${escAttr(item.id)}">
            <span class="dash-content-tag">${escHtml(categoryLabel(item.category))}</span>
            <span class="dash-section-picker-text">${escHtml(item.title || (item.content || '').slice(0, 70))}</span>
            ${suggested.has(item.category) ? '<span class="dash-section-suggested-chip">Suggested</span>' : ''}
            <span class="dash-section-picker-add">+ Add</span>
        </button>`
    ).join('');

    container.querySelectorAll('[data-add-ref]').forEach(btn => {
        btn.addEventListener('click', () => {
            sectionDraftRefs.push(btn.dataset.addRef);
            renderSectionChosen();
            renderSectionPicker();
        });
    });
}

async function saveSection() {
    const name = document.getElementById('sectionName').value.trim();
    if (!name) {
        setSectionEditorError('Section name is required.');
        return;
    }
    const payload = {
        name,
        description: document.getElementById('sectionDescription').value.trim(),
        status: document.getElementById('sectionStatus').value,
        section_type: document.getElementById('sectionType').value || 'custom',
        brand_id: document.getElementById('sectionBrandId').value || null,
        tags: document.getElementById('sectionTags').value.trim(),
        content_refs: sectionDraftRefs.slice(),
    };

    const confirmBtn = document.getElementById('confirmSaveSection');
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Saving...';
    setSectionEditorError('');

    try {
        if (editingSectionId) {
            await apiFetch(`/api/sections/${editingSectionId}`, {
                method: 'PATCH', body: JSON.stringify(payload),
            });
        } else {
            await apiFetch('/api/sections/from-content', {
                method: 'POST', body: JSON.stringify(payload),
            });
        }
        await loadSections();
        hideSectionEditor();
    } catch (e) {
        setSectionEditorError('Failed to save: ' + e.message);
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Save section';
    }
}

function setSectionEditorError(message) {
    const error = document.getElementById('sectionEditorError');
    if (!error) return;
    error.textContent = message || '';
    error.style.display = message ? '' : 'none';
}

function openSectionPreview(sectionId) {
    const modal = document.getElementById('sectionViewModal');
    const iframe = document.getElementById('sectionViewIframe');
    if (!modal || !iframe) return;
    iframe.src = `/api/sections/${sectionId}/preview?t=${Date.now()}`;
    modal.style.display = '';
}

function bindSectionPreviewModal() {
    const modal = document.getElementById('sectionViewModal');
    const closeBtn = document.getElementById('closeSectionView');
    if (!modal) return;
    const hide = () => {
        modal.style.display = 'none';
        const iframe = document.getElementById('sectionViewIframe');
        if (iframe) iframe.src = 'about:blank';
    };
    if (closeBtn) closeBtn.addEventListener('click', hide);
    modal.addEventListener('click', (e) => { if (e.target === modal) hide(); });
}

async function openBrandSitePreview(brandId) {
    const modal = document.getElementById('brandSiteViewModal');
    const iframe = document.getElementById('brandSiteViewIframe');
    const title = document.getElementById('brandSiteViewTitle');
    const brand = brands.find(b => b.id === brandId);
    if (!modal || !iframe || !brandId) return;

    let doc;
    try {
        const token = document.querySelector('meta[name="ai-request-token"]')?.content || '';
        const res = await fetch(`/api/brands/${brandId}/site/preview?t=${Date.now()}`, {
            headers: { 'X-Requested-With': 'SwiftSitesApp', 'X-AI-Request-Token': token },
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            const message = err.message || (typeof err.error === 'string' ? err.error : '') || `HTTP ${res.status}`;
            throw new Error(message);
        }
        doc = await res.text();
    } catch (e) {
        await showMessageModal({
            title: 'Preview unavailable',
            message: e.message || 'Could not load the brand site preview. Create or regenerate the site shell, then try again.',
        });
        return;
    }

    if (title) title.textContent = brand?.name ? `${brand.name} site preview` : 'Brand site preview';
    iframe.srcdoc = doc;
    modal.style.display = '';
}

function bindBrandSitePreviewModal() {
    const modal = document.getElementById('brandSiteViewModal');
    const closeBtn = document.getElementById('closeBrandSiteView');
    if (!modal) return;
    const hide = () => {
        modal.style.display = 'none';
        const iframe = document.getElementById('brandSiteViewIframe');
        if (iframe) iframe.src = 'about:blank';
    };
    if (closeBtn) closeBtn.addEventListener('click', hide);
    modal.addEventListener('click', (e) => { if (e.target === modal) hide(); });
}

function categoryLabel(value) {
    const meta = contentTypeMeta(value);
    if (meta) return meta.label;
    const labels = {
        ad_copy: 'Ad copy',
        boilerplate: 'Boilerplate',
        case_study: 'Case study',
        cta: 'CTA',
        email_subject: 'Email subject',
        product_feature: 'Product feature',
        product_spec: 'Product spec',
        seo_meta: 'SEO meta',
        social_post: 'Social post',
        value_proposition: 'Value prop',
    };
    return labels[value] || capitalize(String(value || '').replace(/_/g, ' '));
}

function statusLabel(value) {
    return capitalize(String(value || '').replace(/_/g, ' '));
}

function formatShortDate(value) {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function bindAddProduct() {
    const modal = document.getElementById('addProductModal');
    const openBtn = document.getElementById('addProductBtn');
    const cancelBtn = document.getElementById('cancelAddProduct');
    const confirmBtn = document.getElementById('confirmAddProduct');
    if (!modal || !openBtn || !cancelBtn || !confirmBtn) return;

    openBtn.addEventListener('click', () => {
        renderProductBrandCheckboxes();
        document.getElementById('productName').value = '';
        document.getElementById('productType').value = 'service';
        document.getElementById('productShortDescription').value = '';
        document.getElementById('productPrice').value = '';
        modal.style.display = '';
        document.getElementById('productName').focus();
    });

    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    confirmBtn.addEventListener('click', async () => {
        const name = document.getElementById('productName').value.trim();
        if (!name) {
            await showMessageModal({ title: 'Product name required', message: 'Product name is required.' });
            return;
        }

        const brandIds = Array.from(document.querySelectorAll('#productBrandList input:checked'))
            .map(input => input.value);
        const body = {
            name,
            product_type: document.getElementById('productType').value,
            short_description: document.getElementById('productShortDescription').value.trim(),
            price: document.getElementById('productPrice').value || null,
            brand_ids: brandIds,
            status: 'active',
        };

        try {
            const product = await apiFetch('/api/products', {
                method: 'POST',
                body: JSON.stringify(body),
            });
            products.unshift(product);
            modal.style.display = 'none';
            renderProductsGrid();
        } catch (e) {
            await showMessageModal({ title: 'Failed to add product', message: e.message });
        }
    });
}

function renderProductBrandCheckboxes() {
    const container = document.getElementById('productBrandList');
    if (!container) return;
    if (!brands.length) {
        container.innerHTML = '<p class="dash-empty-inline">Create a brand first, then tag products to it.</p>';
        return;
    }
    container.innerHTML = brands.map((brand, index) => `
        <label class="dash-checkbox-row">
            <input type="checkbox" value="${brand.id}" ${index === 0 ? 'checked' : ''}>
            <span>${escHtml(brand.name)}</span>
        </label>
    `).join('');
}

// =============================================================================
// Create Site Modal
// =============================================================================

function bindModals() {
    const modal = document.getElementById('createSiteModal');
    const createBtn = document.getElementById('createSiteBtn');
    const cancelBtn = document.getElementById('cancelCreateSite');
    const confirmBtn = document.getElementById('confirmCreateSite');
    const nameInput = document.getElementById('newSiteName');
    const slugInput = document.getElementById('newSiteSlug');
    const errorEl = document.getElementById('createSiteError');

    createBtn.addEventListener('click', () => {
        modal.style.display = '';
        nameInput.value = '';
        slugInput.value = '';
        errorEl.style.display = 'none';
        nameInput.focus();
    });

    cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    nameInput.addEventListener('input', () => {
        if (!slugInput.dataset.manual) {
            slugInput.value = nameInput.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        }
    });

    slugInput.addEventListener('input', () => {
        slugInput.dataset.manual = 'true';
    });

    confirmBtn.addEventListener('click', async () => {
        const name = nameInput.value.trim();
        const slug = slugInput.value.trim();
        if (!name || !slug) {
            showError(errorEl, 'Name and slug are required.');
            return;
        }
        try {
            errorEl.style.display = 'none';
            const site = await apiFetch('/api/sites', {
                method: 'POST',
                body: JSON.stringify({ name, slug }),
            });
            modal.style.display = 'none';
            window.location.href = `/editor/${site.id}`;
        } catch (e) {
            showError(errorEl, e.message);
        }
    });

    bindSettingsModal();
}

function showError(el, msg) {
    el.textContent = msg;
    el.style.display = '';
}

// =============================================================================
// Utilities
// =============================================================================

function escHtml(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function escAttr(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

function resolveElements(items) {
    if (!items) return [];
    if (items instanceof Element) return [items];
    if (typeof items === 'string') return [document.getElementById(items)].filter(Boolean);
    if (items instanceof NodeList || items instanceof HTMLCollection) {
        return resolveElements(Array.from(items));
    }
    if (Array.isArray(items)) {
        const seen = new Set();
        return items.flatMap(item => resolveElements(item)).filter(el => {
            if (!el || seen.has(el)) return false;
            seen.add(el);
            return true;
        });
    }
    return [];
}

function setFieldsDisabled(fields, disabled) {
    resolveElements(fields).forEach(el => {
        if (disabled) {
            if (!Object.prototype.hasOwnProperty.call(el.dataset, 'aiWasDisabled')) {
                el.dataset.aiWasDisabled = String(Boolean(el.disabled));
            }
            el.disabled = true;
            el.classList.add('dash-ai-field-locked');
            el.setAttribute('aria-disabled', 'true');
            return;
        }
        const wasDisabled = el.dataset.aiWasDisabled === 'true';
        if (!wasDisabled) {
            el.disabled = false;
        }
        delete el.dataset.aiWasDisabled;
        el.classList.remove('dash-ai-field-locked');
        el.removeAttribute('aria-disabled');
    });
}

function setAiGeneratingState({ active, button = null, loadingLabel = 'AI', statusEl = null, statusText = '', fields = [] } = {}) {
    const buttonEl = resolveElements(button)[0] || null;
    const status = resolveElements(statusEl)[0] || null;
    if (active) {
        if (buttonEl) {
            if (!Object.prototype.hasOwnProperty.call(buttonEl.dataset, 'aiOriginalHtml')) {
                buttonEl.dataset.aiOriginalHtml = buttonEl.innerHTML;
                buttonEl.dataset.aiWasDisabled = String(Boolean(buttonEl.disabled));
            }
            buttonEl.disabled = true;
            buttonEl.classList.add('dash-ai-generating');
            buttonEl.setAttribute('aria-busy', 'true');
            buttonEl.innerHTML = `<span class="dash-ai-spinner" aria-hidden="true"></span><span>${escHtml(loadingLabel)}</span>`;
        }
        if (status && statusText) {
            status.textContent = statusText;
            status.style.color = 'var(--d-text-tertiary)';
        }
        setFieldsDisabled(fields, true);
        return;
    }

    if (buttonEl) {
        if (Object.prototype.hasOwnProperty.call(buttonEl.dataset, 'aiOriginalHtml')) {
            buttonEl.innerHTML = buttonEl.dataset.aiOriginalHtml;
        }
        const wasDisabled = buttonEl.dataset.aiWasDisabled === 'true';
        if (!wasDisabled) {
            buttonEl.disabled = false;
        }
        delete buttonEl.dataset.aiOriginalHtml;
        delete buttonEl.dataset.aiWasDisabled;
        buttonEl.classList.remove('dash-ai-generating');
        buttonEl.removeAttribute('aria-busy');
    }
    setFieldsDisabled(fields, false);
}

function formatBytes(bytes) {
    if (!bytes && bytes !== 0) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatRelativeTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// =============================================================================
// Boot
// =============================================================================

init();
