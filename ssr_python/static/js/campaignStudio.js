/**
 * Campaign Studio — Step-based campaign workspace
 * Handles: step navigation, field autosave, tag inputs, messages, goal selection
 */

import { showMessageModal, showTextPrompt } from './promptModal.js';

const CAMPAIGN_ID = window.CAMPAIGN_ID;
const API_BASE = `/api/campaigns/${CAMPAIGN_ID}`;

let campaignData = null;
let brands = [];
let products = [];
let currentStep = 0;
let saveTimeout = null;
let isSaving = false;

const STEPS = [
    { key: 'promotion', label: 'Promotion' },
    { key: 'audience', label: 'Audience' },
    { key: 'goal', label: 'Goal' },
    { key: 'offer', label: 'Offer' },
    { key: 'messages', label: 'Messages' },
    { key: 'landing_page', label: 'Landing Page' },
];

// =============================================================================
// API Helpers
// =============================================================================

async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
}

// Like apiFetch, but carries the AI-request token headers required by the
// AI-spend-protected /api/chat/enhance endpoint (mirrors chatService _appHeaders).
async function aiFetch(url, options = {}) {
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
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
}

// =============================================================================
// Initialization
// =============================================================================

async function init() {
    try {
        const [campaign, brandList, productList] = await Promise.all([
            apiFetch(API_BASE),
            apiFetch('/api/brands').catch(() => []),
            apiFetch('/api/products').catch(() => []),
        ]);
        campaignData = campaign;
        brands = brandList;
        products = productList;
        populateCampaignSelectors();
        populateFields();
        bindEvents();
        bindPageEvents();
        attachCampaignAiButtons();
        bindCampaignAiButtons();
        updateStepStates();
        loadExistingPage();
    } catch (e) {
        console.error('Failed to load campaign:', e);
        document.querySelector('.cs-content').innerHTML = `
            <div class="cs-empty">
                <p class="cs-empty-text">Could not load campaign. It may have been deleted.</p>
                <a href="/" class="cs-btn cs-btn--primary">Back to Dashboard</a>
            </div>`;
    }
}

// =============================================================================
// Field Population
// =============================================================================

function populateFields() {
    const { name, goal, brand_id, brief, offer, messages } = campaignData;

    document.getElementById('csCampaignName').textContent = name || 'Untitled Campaign';
    document.getElementById('csName').value = name || '';
    setVal('csBrand', brand_id);
    renderProductChoices();

    if (brief) {
        setVal('csProduct', brief.product_or_service);
        setVal('csDescription', brief.description);
        setVal('csAudience', brief.target_audience);
        setVal('csProblem', brief.problem_or_desire);
        setVal('csAwareness', brief.awareness_level);
        setVal('csBuyingStage', brief.buying_stage);
        setVal('csLocation', brief.location_or_segment);
    }

    if (goal) {
        selectGoalCard(goal);
    }

    if (offer) {
        setVal('csOffer', offer.offer);
        setVal('csPrimaryCta', offer.primary_cta);
        setVal('csSecondaryCta', offer.secondary_cta);
        renderTags('csBenefitsTags', offer.benefits || []);
        renderTags('csProofTags', offer.proof_points || []);
        renderFaqs(offer.faqs || []);
    }

    if (messages && messages.length) {
        renderMessages(messages);
    }

    updateSaveToLibraryVisibility();
    updateStatusPill();
}

function setVal(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value || '';
}

function populateCampaignSelectors() {
    const brandSelect = document.getElementById('csBrand');
    if (!brandSelect) return;
    brandSelect.innerHTML = '<option value="">No brand selected</option>' + brands.map(brand =>
        `<option value="${escAttr(brand.id)}">${escHtml(brand.name)}</option>`
    ).join('');
}

const STUDIO_GOAL_LABELS = {
    leads: 'Leads', sales: 'Sales', signups: 'Signups',
    calls: 'Calls', traffic: 'Traffic', inform: 'Info',
};

function _shortPhrase(text, words = 2) {
    if (!text) return '';
    return String(text).trim().split(/\s+/).slice(0, words).join(' ');
}

function buildSuggestedName() {
    // Structured name: Mon-Year · Brand · Goal · Audience · Product · Region.
    // Only includes parts that are actually set, so it stays clean early on.
    const now = new Date();
    const datePart = `${now.toLocaleString('en-US', { month: 'short' })}-${now.getFullYear()}`;
    const parts = [datePart];

    const brand = brands.find(b => b.id === campaignData.brand_id);
    if (brand && brand.name) parts.push(brand.name);

    if (campaignData.goal && STUDIO_GOAL_LABELS[campaignData.goal]) {
        parts.push(STUDIO_GOAL_LABELS[campaignData.goal]);
    }

    const audience = _shortPhrase(document.getElementById('csAudience')?.value, 2);
    if (audience) parts.push(audience);

    const selectedIds = new Set(campaignData.product_ids || []);
    const productNames = products.filter(p => selectedIds.has(p.id)).map(p => p.name);
    if (productNames.length === 1) parts.push(productNames[0]);
    else if (productNames.length > 1) parts.push(`${productNames.length} products`);

    const region = _shortPhrase(document.getElementById('csLocation')?.value, 2);
    if (region) parts.push(region);

    return parts.join(' · ');
}

function applySuggestedName() {
    const suggested = buildSuggestedName();
    const input = document.getElementById('csName');
    if (input) input.value = suggested;
    const header = document.getElementById('csCampaignName');
    if (header) header.textContent = suggested;
    scheduleFieldSave('name', suggested);
}

function renderProductChoices() {
    const container = document.getElementById('csProductChoices');
    if (!container) return;

    if (!products.length) {
        container.innerHTML = '<p class="cs-empty-inline">No products yet.</p>';
        return;
    }

    const selectedIds = new Set(campaignData.product_ids || []);
    const selectedBrandId = campaignData.brand_id || '';
    const orderedProducts = [...products].sort((a, b) => {
        const aMatches = selectedBrandId && (a.brand_ids || []).includes(selectedBrandId);
        const bMatches = selectedBrandId && (b.brand_ids || []).includes(selectedBrandId);
        return Number(bMatches) - Number(aMatches) || (a.name || '').localeCompare(b.name || '');
    });

    container.innerHTML = orderedProducts.map(product => {
        const brandNames = (product.brands || []).map(brand => brand.name).join(', ');
        const price = product.price !== null && product.price !== undefined && product.price !== ''
            ? `${product.currency || 'USD'} ${product.price}`
            : '';
        const meta = [brandNames, price].filter(Boolean).join(' - ');
        return `<label class="cs-checkbox-row">
            <input type="checkbox" value="${escAttr(product.id)}" ${selectedIds.has(product.id) ? 'checked' : ''}>
            <span>
                <strong>${escHtml(product.name)}</strong>
                ${meta ? `<small>${escHtml(meta)}</small>` : ''}
            </span>
        </label>`;
    }).join('');
}

async function saveProductSelection() {
    const productIds = Array.from(document.querySelectorAll('#csProductChoices input:checked'))
        .map(input => input.value);
    showSaving();
    try {
        await apiFetch(API_BASE, {
            method: 'PATCH',
            body: JSON.stringify({ product_ids: productIds }),
        });
        campaignData.product_ids = productIds;
        showSaved();
    } catch (e) {
        console.error('Product save failed:', e);
        showSaveError();
    }
}

// =============================================================================
// Step Navigation
// =============================================================================

function goToStep(step) {
    if (step < 0 || step >= STEPS.length) return;
    currentStep = step;

    document.querySelectorAll('.cs-step-panel').forEach((panel, i) => {
        panel.classList.toggle('active', i === step);
    });

    document.querySelectorAll('.cs-step-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === step);
    });

    document.getElementById('csPrevBtn').style.display = step === 0 ? 'none' : '';
    const nextBtn = document.getElementById('csNextBtn');
    if (step === STEPS.length - 1) {
        nextBtn.textContent = campaignData && campaignData.site_id ? 'Open in Editor' : 'Done';
    } else {
        nextBtn.textContent = 'Continue';
    }

    updateStepStates();
}

function updateStepStates() {
    const btns = document.querySelectorAll('.cs-step-btn');
    btns.forEach((btn, i) => {
        if (i < currentStep) {
            btn.classList.add('completed');
        } else {
            btn.classList.remove('completed');
        }
    });
}

// =============================================================================
// Goal Selection
// =============================================================================

function selectGoalCard(goal) {
    document.querySelectorAll('#csGoalGrid .cs-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.goal === goal);
    });
}

// =============================================================================
// Tag Inputs (Benefits, Proof Points)
// =============================================================================

function renderTags(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = items.map((item, i) => `
        <span class="cs-tag">
            ${escHtml(item)}
            <button class="cs-tag-remove" data-index="${i}" data-container="${containerId}">&times;</button>
        </span>
    `).join('');
}

function getTagsFromContainer(containerId) {
    const container = document.getElementById(containerId);
    return Array.from(container.querySelectorAll('.cs-tag')).map(tag => {
        const clone = tag.cloneNode(true);
        clone.querySelector('.cs-tag-remove')?.remove();
        return clone.textContent.trim();
    });
}

function addTag(containerId, inputId) {
    const input = document.getElementById(inputId);
    const value = input.value.trim();
    if (!value) return;

    const items = getTagsFromContainer(containerId);
    items.push(value);
    renderTags(containerId, items);
    input.value = '';
    scheduleOfferSave();
}

function removeTag(containerId, index) {
    const items = getTagsFromContainer(containerId);
    items.splice(index, 1);
    renderTags(containerId, items);
    scheduleOfferSave();
}

// =============================================================================
// FAQ Management
// =============================================================================

function renderFaqs(faqs) {
    const container = document.getElementById('csFaqList');
    container.innerHTML = faqs.map((faq, i) => `
        <div class="cs-faq-item" data-index="${i}">
            <div class="cs-field">
                <label class="cs-label">Question</label>
                <input class="cs-input cs-faq-q" type="text" value="${escAttr(faq.question || '')}" placeholder="e.g., How long does shipping take?">
            </div>
            <div class="cs-field">
                <label class="cs-label">Answer</label>
                <textarea class="cs-textarea cs-faq-a" rows="2" placeholder="Keep it concise and helpful">${escHtml(faq.answer || '')}</textarea>
            </div>
            <button class="cs-btn cs-btn--ghost cs-btn--sm cs-faq-remove" data-index="${i}">Remove</button>
        </div>
    `).join('');
}

function getFaqsFromDom() {
    return Array.from(document.querySelectorAll('.cs-faq-item')).map(item => ({
        question: item.querySelector('.cs-faq-q').value.trim(),
        answer: item.querySelector('.cs-faq-a').value.trim(),
    })).filter(f => f.question || f.answer);
}

function addFaq() {
    const faqs = getFaqsFromDom();
    faqs.push({ question: '', answer: '' });
    renderFaqs(faqs);
}

function removeFaq(index) {
    const faqs = getFaqsFromDom();
    faqs.splice(index, 1);
    renderFaqs(faqs);
    scheduleOfferSave();
}

// =============================================================================
// Messages (Step 5)
// =============================================================================

function renderMessages(messages) {
    const container = document.getElementById('csMessagesContainer');
    const groups = {};
    messages.forEach(msg => {
        if (!groups[msg.category]) groups[msg.category] = [];
        groups[msg.category].push(msg);
    });

    const categoryLabels = {
        headline: 'Headlines',
        subheadline: 'Subheadlines',
        benefit: 'Benefits',
        proof: 'Proof',
        objection: 'Objection Answers',
        faq: 'FAQs',
        cta: 'Calls to Action',
        testimonial: 'Testimonials',
    };

    const order = ['headline', 'subheadline', 'benefit', 'proof', 'cta', 'testimonial', 'objection', 'faq'];
    let html = '';

    for (const cat of order) {
        const msgs = groups[cat];
        if (!msgs || !msgs.length) continue;
        html += `<div class="cs-messages-group">
            <h3 class="cs-messages-group-title">${categoryLabels[cat] || cat}</h3>
            ${msgs.map(m => renderMessageItem(m)).join('')}
        </div>`;
    }

    container.innerHTML = html || `
        <div class="cs-empty">
            <p class="cs-empty-text">No messages yet. Click "Generate messages" to create copy from your campaign brief.</p>
        </div>`;
}

function renderMessageItem(msg) {
    const keptClass = msg.is_kept ? ' kept' : '';
    const keptIcon = msg.is_kept
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';

    return `<div class="cs-message-item${keptClass}" data-msg-id="${msg.id}">
        <div class="cs-message-content">${escHtml(msg.content)}</div>
        <div class="cs-message-actions">
            <button class="cs-msg-action-btn${msg.is_kept ? ' kept-active' : ''}" data-action="keep" data-id="${msg.id}" title="Keep this message">
                ${keptIcon}
            </button>
            <button class="cs-msg-action-btn" data-action="delete" data-id="${msg.id}" title="Remove">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
        </div>
    </div>`;
}

async function generateMessages() {
    const btn = document.getElementById('csGenerateBtn');
    btn.disabled = true;
    btn.innerHTML = `<span class="cs-generating-spinner"></span> Generating...`;

    try {
        const res = await apiFetch(`${API_BASE}/compile`, { method: 'POST' });
        const sections = res.sections || [];
        const messagesToCreate = [];

        for (const section of sections) {
            const bc = section.business_content || {};
            if (bc.headline) messagesToCreate.push({ category: 'headline', content: bc.headline });
            if (bc.subheadline) messagesToCreate.push({ category: 'subheadline', content: bc.subheadline });
            if (bc.cta_text) messagesToCreate.push({ category: 'cta', content: bc.cta_text });
            if (bc.offer_text) messagesToCreate.push({ category: 'headline', content: bc.offer_text });
            if (bc.primary_cta && bc.primary_cta !== bc.cta_text) {
                messagesToCreate.push({ category: 'cta', content: bc.primary_cta });
            }
            if (bc.benefits) {
                for (const b of bc.benefits.slice(0, 3)) {
                    messagesToCreate.push({ category: 'benefit', content: b });
                }
            }
            if (bc.proof_points) {
                for (const p of bc.proof_points.slice(0, 3)) {
                    messagesToCreate.push({ category: 'proof', content: p });
                }
            }
            if (bc.testimonials) {
                for (const t of bc.testimonials.slice(0, 2)) {
                    messagesToCreate.push({ category: 'testimonial', content: t });
                }
            }
        }

        const unique = dedupeMessages(messagesToCreate);
        if (unique.length) {
            const created = await apiFetch(`${API_BASE}/messages`, {
                method: 'POST',
                body: JSON.stringify({ messages: unique }),
            });
            campaignData.messages = [...(campaignData.messages || []), ...created];
        }

        renderMessages(campaignData.messages);
    } catch (e) {
        console.error('Generate failed:', e);
        await showMessageModal({ title: 'Failed to generate messages', message: e.message });
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg> Generate messages from campaign`;
    }
}

function updateSaveToLibraryVisibility() {
    const btn = document.getElementById('csSaveToLibraryBtn');
    const hasKept = campaignData.messages && campaignData.messages.some(m => m.is_kept);
    btn.style.display = hasKept ? '' : 'none';
}

async function saveKeptToLibrary() {
    const btn = document.getElementById('csSaveToLibraryBtn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
        const res = await apiFetch('/api/content/save-from-campaign', {
            method: 'POST',
            body: JSON.stringify({ campaign_id: CAMPAIGN_ID }),
        });
        btn.textContent = `Saved ${res.saved_count} item${res.saved_count !== 1 ? 's' : ''}`;
        setTimeout(() => {
            btn.textContent = 'Save kept to content library';
            btn.disabled = false;
        }, 2000);
    } catch (e) {
        await showMessageModal({ title: 'Failed to save', message: e.message });
        btn.textContent = 'Save kept to content library';
        btn.disabled = false;
    }
}

function dedupeMessages(messages) {
    const seen = new Set();
    return messages.filter(m => {
        if (!m.content) return false;
        const key = `${m.category}:${m.content.toLowerCase().trim()}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

async function toggleKeep(messageId) {
    const msg = campaignData.messages.find(m => m.id === messageId);
    if (!msg) return;

    const newKept = !msg.is_kept;
    await apiFetch(`${API_BASE}/messages/${messageId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_kept: newKept }),
    });
    msg.is_kept = newKept;
    renderMessages(campaignData.messages);
    updateSaveToLibraryVisibility();
}

async function deleteMessage(messageId) {
    await apiFetch(`${API_BASE}/messages/${messageId}`, { method: 'DELETE' });
    campaignData.messages = campaignData.messages.filter(m => m.id !== messageId);
    renderMessages(campaignData.messages);
}

// =============================================================================
// Autosave
// =============================================================================

function scheduleFieldSave(field, value) {
    clearTimeout(saveTimeout);
    showSaving();
    saveTimeout = setTimeout(() => saveField(field, value), 600);
}

async function saveField(field, value) {
    try {
        if (field === 'name') {
            await apiFetch(API_BASE, { method: 'PATCH', body: JSON.stringify({ name: value }) });
            campaignData.name = value;
            document.getElementById('csCampaignName').textContent = value || 'Untitled Campaign';
        } else if (field === 'goal') {
            await apiFetch(API_BASE, { method: 'PATCH', body: JSON.stringify({ goal: value }) });
            campaignData.goal = value;
        } else if (field === 'brand_id') {
            const brandId = value || null;
            await apiFetch(API_BASE, { method: 'PATCH', body: JSON.stringify({ brand_id: brandId }) });
            campaignData.brand_id = brandId;
            renderProductChoices();
        } else if (field.startsWith('brief.')) {
            const key = field.replace('brief.', '');
            await apiFetch(`${API_BASE}/brief`, { method: 'PATCH', body: JSON.stringify({ [key]: value }) });
            if (!campaignData.brief) campaignData.brief = {};
            campaignData.brief[key] = value;
        } else if (field.startsWith('offer.')) {
            const key = field.replace('offer.', '');
            await apiFetch(`${API_BASE}/offer`, { method: 'PATCH', body: JSON.stringify({ [key]: value }) });
            if (!campaignData.offer) campaignData.offer = {};
            campaignData.offer[key] = value;
        }
        showSaved();
    } catch (e) {
        console.error('Save failed:', e);
        showSaveError();
    }
}

function scheduleOfferSave() {
    clearTimeout(saveTimeout);
    showSaving();
    saveTimeout = setTimeout(async () => {
        const benefits = getTagsFromContainer('csBenefitsTags');
        const proof_points = getTagsFromContainer('csProofTags');
        const faqs = getFaqsFromDom();
        try {
            await apiFetch(`${API_BASE}/offer`, {
                method: 'PATCH',
                body: JSON.stringify({ benefits, proof_points, faqs }),
            });
            if (!campaignData.offer) campaignData.offer = {};
            campaignData.offer.benefits = benefits;
            campaignData.offer.proof_points = proof_points;
            campaignData.offer.faqs = faqs;
            showSaved();
        } catch (e) {
            console.error('Save failed:', e);
            showSaveError();
        }
    }, 800);
}

function showSaving() {
    const el = document.getElementById('csAutosave');
    el.innerHTML = '<span class="cs-autosave-dot" style="background: var(--cs-warning);"></span> Saving...';
}

function showSaved() {
    const el = document.getElementById('csAutosave');
    el.innerHTML = '<span class="cs-autosave-dot"></span> Saved';
}

function showSaveError() {
    const el = document.getElementById('csAutosave');
    el.innerHTML = '<span class="cs-autosave-dot" style="background: var(--cs-danger);"></span> Save failed';
}

function updateStatusPill() {
    const pill = document.getElementById('csStatusPill');
    const text = document.getElementById('csStatusText');
    const status = campaignData.status || 'draft';
    text.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    pill.className = `cs-status-pill cs-status-pill--${status}`;
}

// =============================================================================
// AI Field Enhancement
// =============================================================================

// Free-text fields that get a per-field AI "Enhance" button. `field` is the
// data-field path (server key), `id` is the input/textarea element id.
const CAMPAIGN_AI_FIELDS = [
    { field: 'brief.product_or_service', id: 'csProduct' },
    { field: 'brief.description', id: 'csDescription' },
    { field: 'brief.target_audience', id: 'csAudience' },
    { field: 'brief.problem_or_desire', id: 'csProblem' },
    { field: 'brief.location_or_segment', id: 'csLocation' },
    { field: 'offer.offer', id: 'csOffer' },
    { field: 'offer.primary_cta', id: 'csPrimaryCta' },
    { field: 'offer.secondary_cta', id: 'csSecondaryCta' },
];

const CAMPAIGN_AI_ICON = `
    <svg class="cs-ai-field-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
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

// Inject a sparkle "Enhance" button next to each AI-eligible field's label.
function attachCampaignAiButtons() {
    CAMPAIGN_AI_FIELDS.forEach(({ field, id }) => {
        const input = document.getElementById(id);
        const wrapper = input?.closest('.cs-field');
        const label = wrapper?.querySelector(`label[for="${id}"]`);
        if (!input || !wrapper || !label || wrapper.querySelector(`[data-ai-field="${field}"]`)) return;

        const row = document.createElement('div');
        row.className = 'cs-label-row';
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'cs-ai-field-btn';
        button.dataset.aiField = field;
        button.dataset.aiTarget = id;
        button.title = 'Enhance this field with AI';
        button.innerHTML = CAMPAIGN_AI_ICON;

        wrapper.insertBefore(row, label);
        row.appendChild(label);
        row.appendChild(button);
    });
}

function bindCampaignAiButtons() {
    document.querySelectorAll('[data-ai-field]').forEach(button => {
        if (button.dataset.bound === 'true') return;
        button.dataset.bound = 'true';
        button.addEventListener('click', () => enhanceCampaignField(button));
    });
}

// Build the full campaign context sent to the AI as `current_content`. Reads
// live field values (so unsaved edits count) and folds in the selected brand's
// strategy so enhancements stay on-brand.
function collectCampaignContext() {
    const val = (id) => document.getElementById(id)?.value.trim() || '';
    const context = {
        name: val('csName'),
        goal: campaignData?.goal || '',
        'brief.product_or_service': val('csProduct'),
        'brief.description': val('csDescription'),
        'brief.target_audience': val('csAudience'),
        'brief.problem_or_desire': val('csProblem'),
        'brief.awareness_level': val('csAwareness'),
        'brief.buying_stage': val('csBuyingStage'),
        'brief.location_or_segment': val('csLocation'),
        'offer.offer': val('csOffer'),
        'offer.primary_cta': val('csPrimaryCta'),
        'offer.secondary_cta': val('csSecondaryCta'),
        'offer.benefits': getTagsFromContainer('csBenefitsTags'),
        'offer.proof_points': getTagsFromContainer('csProofTags'),
    };

    const brand = brands.find(b => b.id === campaignData?.brand_id);
    if (brand) {
        const strategy = brand.strategy || {};
        context.brand = {
            name: brand.name || '',
            tagline: brand.tagline || '',
            description: brand.description || '',
            industry: brand.industry || '',
            tone: brand.tone || '',
            target_audience: strategy.target_audience || '',
            brand_promise: strategy.brand_promise || '',
            positioning_statement: strategy.positioning_statement || '',
            differentiators: strategy.differentiators || [],
            cta_style: strategy.cta_style || '',
            primary_market: strategy.primary_market || '',
            forbidden_words: strategy.forbidden_words || [],
            forbidden_claims: strategy.forbidden_claims || [],
        };
    }
    return context;
}

async function enhanceCampaignField(button) {
    const field = button.dataset.aiField;
    const target = document.getElementById(button.dataset.aiTarget);
    if (!field || !target) return;

    const originalHtml = button.innerHTML;
    const context = collectCampaignContext();
    const brand = brands.find(b => b.id === campaignData?.brand_id);
    try {
        button.disabled = true;
        button.innerHTML = '<span class="cs-ai-field-loading">AI…</span>';
        showSaving();

        const result = await aiFetch('/api/chat/enhance', {
            method: 'POST',
            body: JSON.stringify({
                section_type: 'campaign',
                target_field: field,
                business_name: brand?.name || '',
                industry: brand?.industry || '',
                description: context['brief.product_or_service'] || '',
                current_content: context,
            }),
        });

        const enhanced = result.enhanced_fields?.[field];
        if (enhanced) {
            target.value = enhanced;
            target.classList.add('cs-ai-enhanced');
            // Reuse the existing autosave path ([data-field] input listener).
            target.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(() => target.classList.remove('cs-ai-enhanced'), 1400);
        } else {
            showSaved();
        }
    } catch (e) {
        console.error('Enhance failed:', e);
        showSaveError();
    } finally {
        button.disabled = false;
        button.innerHTML = originalHtml;
    }
}

// =============================================================================
// Event Binding
// =============================================================================

function bindEvents() {
    // Back button
    document.getElementById('csBackBtn').addEventListener('click', () => {
        window.location.href = '/';
    });

    // Step nav clicks
    document.querySelectorAll('.cs-step-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            goToStep(parseInt(btn.dataset.step));
        });
    });

    // Next / Prev
    document.getElementById('csNextBtn').addEventListener('click', () => {
        if (currentStep === STEPS.length - 1) {
            if (campaignData.site_id) {
                window.location.href = `/editor/${campaignData.site_id}`;
            } else {
                window.location.href = '/';
            }
        } else {
            goToStep(currentStep + 1);
        }
    });
    document.getElementById('csPrevBtn').addEventListener('click', () => {
        goToStep(currentStep - 1);
    });

    // Text field autosave
    document.querySelectorAll('[data-field]').forEach(el => {
        const event = el.tagName === 'SELECT' ? 'change' : 'input';
        el.addEventListener(event, () => {
            scheduleFieldSave(el.dataset.field, el.value.trim());
        });
    });

    document.getElementById('csProductChoices').addEventListener('change', (e) => {
        if (e.target.matches('input[type="checkbox"]')) {
            saveProductSelection();
        }
    });

    // Suggest name lives in the header (available on every step). Fall back to
    // a Step 1 button if present, so markup changes don't break the binding.
    const suggestBtn = document.getElementById('csSuggestNameHeader')
        || document.getElementById('csSuggestName');
    if (suggestBtn) suggestBtn.addEventListener('click', applySuggestedName);

    // Goal card selection
    document.getElementById('csGoalGrid').addEventListener('click', (e) => {
        const card = e.target.closest('.cs-card');
        if (!card) return;
        selectGoalCard(card.dataset.goal);
        scheduleFieldSave('goal', card.dataset.goal);
    });

    // Benefits tag input
    document.getElementById('csBenefitsAdd').addEventListener('click', () => addTag('csBenefitsTags', 'csBenefitsInput'));
    document.getElementById('csBenefitsInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); addTag('csBenefitsTags', 'csBenefitsInput'); }
    });

    // Proof tag input
    document.getElementById('csProofAdd').addEventListener('click', () => addTag('csProofTags', 'csProofInput'));
    document.getElementById('csProofInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); addTag('csProofTags', 'csProofInput'); }
    });

    // Tag remove (delegated)
    document.addEventListener('click', (e) => {
        if (e.target.closest('.cs-tag-remove')) {
            const btn = e.target.closest('.cs-tag-remove');
            removeTag(btn.dataset.container, parseInt(btn.dataset.index));
        }
    });

    // FAQ add/remove
    document.getElementById('csFaqAdd').addEventListener('click', addFaq);
    document.addEventListener('click', (e) => {
        if (e.target.closest('.cs-faq-remove')) {
            removeFaq(parseInt(e.target.closest('.cs-faq-remove').dataset.index));
        }
    });

    // FAQ field changes
    document.getElementById('csFaqList').addEventListener('input', () => {
        scheduleOfferSave();
    });

    // Generate messages
    document.getElementById('csGenerateBtn').addEventListener('click', generateMessages);

    // Message actions (delegated)
    document.getElementById('csMessagesContainer').addEventListener('click', (e) => {
        const actionBtn = e.target.closest('.cs-msg-action-btn');
        if (!actionBtn) return;
        const { action, id } = actionBtn.dataset;
        if (action === 'keep') toggleKeep(id);
        if (action === 'delete') deleteMessage(id);
    });

    // Save kept messages to content library
    document.getElementById('csSaveToLibraryBtn').addEventListener('click', saveKeptToLibrary);
}

// =============================================================================
// Landing Page (Step 6)
// =============================================================================

let pageYaml = null;
let pageSections = [];

async function generateLandingPage() {
    const btn = document.getElementById('csGeneratePageBtn');
    const progress = document.getElementById('csPageGenerating');
    const progressText = document.getElementById('csPageProgress');

    btn.style.display = 'none';
    progress.style.display = '';
    progressText.textContent = 'Generating your landing page...';

    try {
        const res = await apiFetch(`${API_BASE}/generate-page`, { method: 'POST' });

        if (res.yaml) {
            pageYaml = res.yaml;
            campaignData.site_id = res.site_id;
            parseSections(res.yaml);
            renderSectionControls();
            showPreview(res.html);

            document.getElementById('csGeneratePageLabel').textContent = 'Regenerate entire page';
        }
    } catch (e) {
        console.error('Page generation failed:', e);
        await showMessageModal({ title: 'Page generation failed', message: e.message });
    } finally {
        btn.style.display = '';
        progress.style.display = 'none';
    }
}

function parseSections(yamlString) {
    pageSections = [];
    const sectionPattern = /- name: (layout-row|columnsgrid|layout-column)/g;
    let match;
    let index = 0;

    const lines = yamlString.split('\n');
    let currentIndent = -1;
    let inPageComponents = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.match(/^\s*- name: page\b/)) {
            inPageComponents = true;
            continue;
        }
        if (inPageComponents && line.match(/^\s{4,6}- name: /)) {
            const nameMatch = line.match(/- name:\s*(.+)/);
            if (nameMatch) {
                pageSections.push({
                    index: index++,
                    name: nameMatch[1].trim(),
                    lineStart: i,
                });
            }
        }
    }

    if (!pageSections.length) {
        pageSections = [{ index: 0, name: 'Full Page', lineStart: 0 }];
    }
}

function renderSectionControls() {
    const container = document.getElementById('csSectionsList');
    const controls = document.getElementById('csSectionControls');
    controls.style.display = '';

    const sectionLabels = {
        'layout-row': 'Section',
        'columnsgrid': 'Grid Section',
        'accordion': 'FAQ Section',
    };

    container.innerHTML = pageSections.map((sec, i) => {
        const label = sectionLabels[sec.name] || sec.name.replace(/-/g, ' ');
        const displayName = `${label} ${i + 1}`;
        return `<div class="cs-section-row" data-index="${sec.index}">
            <div class="cs-section-info">
                <span class="cs-section-index">${i + 1}</span>
                <span class="cs-section-name">${escHtml(displayName)}</span>
            </div>
            <div class="cs-section-actions">
                <button class="cs-section-action-btn" data-action="regenerate" data-index="${sec.index}" title="Regenerate this section">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6"/><path d="M23 20v-6h-6"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4-4.64 4.36A9 9 0 0 1 3.51 15"/></svg>
                    Regenerate
                </button>
                <button class="cs-section-action-btn" data-action="rewrite" data-index="${sec.index}" title="Rewrite shorter or stronger">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    Rewrite
                </button>
            </div>
        </div>`;
    }).join('');
}

function showPreview(html) {
    const frame = document.getElementById('csPreviewFrame');
    const iframe = document.getElementById('csPreviewIframe');
    frame.style.display = '';

    if (html) {
        iframe.srcdoc = html;
    } else {
        loadPreviewFromServer();
    }
}

async function loadPreviewFromServer() {
    try {
        const res = await fetch(`${API_BASE}/preview`);
        if (res.ok) {
            const html = await res.text();
            document.getElementById('csPreviewIframe').srcdoc = html;
        }
    } catch (e) {
        console.error('Preview load failed:', e);
    }
}

async function regenerateSection(index, instruction) {
    const btn = document.querySelector(`[data-action="regenerate"][data-index="${index}"], [data-action="rewrite"][data-index="${index}"]`);
    if (btn) btn.classList.add('regenerating');

    try {
        const body = { section_index: index };
        if (instruction) body.instruction = instruction;

        const res = await apiFetch(`${API_BASE}/regenerate-section`, {
            method: 'POST',
            body: JSON.stringify(body),
        });

        if (res.yaml) {
            pageYaml = res.yaml;
            parseSections(res.yaml);
            renderSectionControls();
        }
        if (res.html) {
            showPreview(res.html);
        }
        showSaved();
    } catch (e) {
        console.error('Regenerate failed:', e);
        await showMessageModal({ title: 'Regeneration failed', message: e.message });
    } finally {
        if (btn) btn.classList.remove('regenerating');
    }
}

function bindPageEvents() {
    document.getElementById('csGeneratePageBtn').addEventListener('click', generateLandingPage);

    document.getElementById('csSectionsList').addEventListener('click', async (e) => {
        const btn = e.target.closest('.cs-section-action-btn');
        if (!btn) return;
        const index = parseInt(btn.dataset.index);
        const action = btn.dataset.action;

        if (action === 'regenerate') {
            regenerateSection(index, null);
        } else if (action === 'rewrite') {
            const instruction = await showTextPrompt({
                title: 'Rewrite section',
                message: 'Describe how this section should change.',
                placeholder: 'Make it shorter, more urgent, or add social proof',
                confirmText: 'Rewrite',
                multiline: true,
            });
            if (instruction) regenerateSection(index, instruction);
        }
    });

    document.getElementById('csEditInEditor').addEventListener('click', () => {
        if (campaignData.site_id) {
            window.location.href = `/editor/${campaignData.site_id}`;
        }
    });
}

// Load existing preview if campaign already has a site
function loadExistingPage() {
    if (campaignData.site_id) {
        document.getElementById('csGeneratePageLabel').textContent = 'Regenerate entire page';
        document.getElementById('csSectionControls').style.display = '';
        document.getElementById('csPreviewFrame').style.display = '';
        loadPreviewFromServer();

        // Try to get YAML to build section list
        fetch(`/api/sites/${campaignData.site_id}/pages`)
            .then(r => r.json())
            .then(pages => {
                if (pages.length) {
                    return fetch(`/api/sites/${campaignData.site_id}/pages/${pages[0].id}`).then(r => r.json());
                }
            })
            .then(page => {
                if (page && page.yaml_content) {
                    pageYaml = page.yaml_content;
                    parseSections(page.yaml_content);
                    renderSectionControls();
                }
            })
            .catch(() => {});
    }
}

// =============================================================================
// Utilities
// =============================================================================

function escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escAttr(str) {
    return escHtml(str);
}

// =============================================================================
// Boot
// =============================================================================

init();
