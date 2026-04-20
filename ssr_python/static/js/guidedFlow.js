/**
 * Guided Flow UI — wizard collecting rich businessContext before LLM generation.
 *
 * Activated by chat.js when the user types a create-page request. Renders a
 * sequence of interactive step cards inside #chatMessages, then POSTs the
 * collected context to /api/chat/guided.
 *
 * State machine:
 *   IDLE → BUSINESS_INFO → INDUSTRY_SELECT → PURPOSE_SELECT → SECTION_SELECT
 *        → SECTION_CONTENT → STYLE_SELECT → REVIEW → GENERATING → DONE
 *
 * Principles:
 *   - Zero LLM calls during collection (only at final GENERATING).
 *   - Each step replaces its in-progress card with a compact summary chip
 *     once advanced, so the chat log stays clean.
 *   - User can cancel at any time via the "Skip, just generate" link, which
 *     falls back to the standard /api/chat pipeline.
 */

import { chatService } from './chatService.js';
import { getCurrentSiteId } from './siteManager.js';

// Client-side industry detection (mirrors query_analyzer.INDUSTRY_KEYWORDS).
// Ordered by specificity — first match wins.
const INDUSTRY_PATTERNS = [
    ['saas',                  /\bsaas\b|software|\bapp\b|platform|startup|\btech\b/i],
    ['restaurant',            /restaurant|menu|bakery|cafe|coffee|pizza|diner/i],
    ['homeservices',          /plumbing|plumber|electric(?:ian|al)|hvac|roofing|handyman|landscap|cleaning.?service/i],
    ['construction',          /construction|contractor|renovation|remodel/i],
    ['beauty',                /salon|barber|spa\b|nail|\bhair\b|stylist|beauty|cosmetic/i],
    ['automotive_services',   /mechanic|auto.?repair|tire|oil.?change|body.?shop|car.?wash|detailing/i],
    ['food_services',         /catering|food.?truck|meal.?prep|juice|smoothie|donut|ice.?cream|brewery/i],
    ['retail_local',          /hardware|furniture|florist|flower|gift.?shop|pet.?store|book.?store|jewel/i],
    ['professional_services', /account(?:ant|ing)|tax\b|insurance|financ|mortgage|dental|chiropract|veterinar/i],
    ['trades',                /weld(?:ing|er)|carpent|masonry|concrete|fencing|siding|drywall|flooring/i],
    ['community',             /church|mosque|temple|nonprofit|charity|volunteer|daycare|preschool/i],
    ['fitness_recreation',    /yoga|pilates|martial.?art|boxing|crossfit|swim|dance.?studio|\bsport\b/i],
    ['portfolio',             /portfolio|agency|freelanc|creative/i],
    ['health',                /health|medical|clinic|wellness|fitness|gym/i],
    ['education',             /education|school|course|tutor|learning|training|coaching/i],
    ['realestate',            /real.?estate|property|housing/i],
    ['logistics',             /logistics|shipping|delivery|transport/i],
    ['hospitality',           /hospitality|hotel|travel|tourism|resort/i],
    ['automotive',            /\bauto\b|\bcar\b|vehicle|dealer|motor/i],
    ['entertainment',         /entertainment|gaming|music|event|conference/i],
    ['legal',                 /legal|\blaw\b|attorney|consulting/i],
    ['ecommerce',             /shop|store|\bproduct\b|ecommerce|retail|boutique/i],
];

function detectIndustry(text) {
    if (!text) return null;
    for (const [key, re] of INDUSTRY_PATTERNS) {
        if (re.test(text)) return key;
    }
    return null;
}

const SECTION_LABELS = {
    navigation: 'Navigation', hero: 'Hero', stats: 'Stats', about: 'About',
    features: 'Features', services: 'Services', pricing: 'Pricing',
    testimonials: 'Testimonials', gallery: 'Gallery', faq: 'FAQ',
    menu: 'Menu', products: 'Products', contact: 'Contact',
    countdown: 'Countdown', cta: 'Call to Action', team: 'Team',
    footer: 'Footer', order_form: 'Order Form', booking_form: 'Booking Form',
    enquiry_form: 'Enquiry Form', catering_form: 'Catering Form',
    reservation: 'Reservation', delivery_areas: 'Delivery Areas',
    how_it_works: 'How It Works', subjects: 'Subjects', levels: 'Levels',
    methodology: 'Methodology', courses: 'Courses', toppers: 'Toppers',
    achievements: 'Achievements', trusted_by: 'Trusted By',
    categories: 'Categories', download_cta: 'Download CTA',
    combos: 'Combos', custom_orders: 'Custom Orders', schedule: 'Schedule',
    events: 'Events', form_cta: 'Form + CTA',
};

const labelFor = (key) =>
    SECTION_LABELS[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

// Step → Lucide icon id mapping (from #icon-sprite.svg)
const STEP_ICONS = {
    BUSINESS_INFO:   'icon-user',
    INDUSTRY_SELECT: 'icon-building-2',
    PURPOSE_SELECT:  'icon-target',
    SECTION_SELECT:  'icon-list-checks',
    SECTION_CONTENT: 'icon-message-square',
    STYLE_SELECT:    'icon-palette',
    REVIEW:          'icon-check-circle',
};

const STEP_ORDER = [
    'BUSINESS_INFO', 'INDUSTRY_SELECT', 'PURPOSE_SELECT',
    'SECTION_SELECT', 'SECTION_CONTENT', 'STYLE_SELECT', 'REVIEW',
];


export class GuidedFlow {
    /**
     * @param {Object} host — ChatUI reference providing:
     *   messagesArea, addMessage, scrollToBottom, showLoading, hideLoading,
     *   updateLoadingText, displayYamlResponse, displayActionResponse,
     *   applyYamlFallback, setInputEnabled, onYamlApply
     */
    constructor(host) {
        this.host = host;
        this._active = false;
        this._state = 'IDLE';
        this._config = null;              // full industry-config response
        this._stepEl = null;              // current step container
        this._initialMessage = '';

        this.businessContext = {
            business_name: '',
            industry: '',
            variant_id: '',
            variant_label: '',
            description: '',
            sections: [],          // [{type, content:{}}]
            style_preference: '',
            color_preference: '',
        };

        this._sectionCursor = 0;   // current index in SECTION_CONTENT loop
    }

    isActive() { return this._active; }

    async start(initialMessage) {
        if (this._active) return;
        this._active = true;
        this._initialMessage = initialMessage || '';

        // Show user's initial message as their chat bubble
        if (this._initialMessage) {
            this.host.addMessage('user', this._initialMessage);
        }

        // Greeting from assistant
        const intro = this.host.addMessage(
            'ai',
            "Great — I'll build you a site with real content. A few quick questions (no AI guesses)."
        );

        // Load config (cached)
        try {
            this._config = await chatService.getIndustryConfig();
        } catch (err) {
            console.error('[GuidedFlow] config fetch failed:', err);
            this.host.addMessage('ai', 'Could not load guided config. Falling back to standard chat.', { isError: true });
            this._active = false;
            // Fallback — send the raw message via the standard pipeline
            if (this.host.fallbackToStandardChat) {
                this.host.fallbackToStandardChat(this._initialMessage);
            }
            return;
        }

        // Seed industry from initial message (user can change)
        this.businessContext.industry = detectIndustry(this._initialMessage) || '';

        this._goto('BUSINESS_INFO');
    }

    destroy() {
        this._active = false;
        this._state = 'DONE';
        if (this._stepEl && this._stepEl.parentNode) {
            this._stepEl.classList.add('guided-step-dismissed');
        }
        this._stepEl = null;
    }

    // ───────────────── State machine dispatcher ─────────────────
    _goto(state) {
        this._state = state;
        try {
            switch (state) {
                case 'BUSINESS_INFO':    return this._renderBusinessInfo();
                case 'INDUSTRY_SELECT':  return this._renderIndustrySelect();
                case 'PURPOSE_SELECT':   return this._renderPurposeSelect();
                case 'SECTION_SELECT':   return this._renderSectionSelect();
                case 'SECTION_CONTENT':  return this._renderSectionContent();
                case 'STYLE_SELECT':     return this._renderStyleSelect();
                case 'REVIEW':           return this._renderReview();
                case 'GENERATING':       return this._runGeneration();
                case 'DONE':             this._active = false; return;
                default: console.warn('[GuidedFlow] unknown state', state);
            }
        } catch (err) {
            console.error(`[GuidedFlow] _goto('${state}') threw:`, err);
            this.host.addMessage('ai',
                `Step "${state}" failed to render: ${err.message}. Check browser console for details.`,
                { isError: true });
        }
    }

    // ───────────────── Step helpers ─────────────────
    /** Create a fresh step container and append to messages. */
    _newStep(stepLabel, totalSteps = 7) {
        // Convert previous in-progress step into a compact summary (if any)
        if (this._stepEl) {
            this._stepEl.classList.add('guided-step-locked');
        }
        const el = document.createElement('div');
        el.className = 'message message-ai guided-step';
        const stepNum = STEP_ORDER.indexOf(this._state) + 1;
        const iconId = STEP_ICONS[this._state] || 'icon-sparkles';
        const progressPct = Math.max(0, Math.min(100, Math.round((stepNum / totalSteps) * 100)));
        el.style.setProperty('--guided-progress', progressPct + '%');
        el.innerHTML = `
            <div class="guided-step-progress" aria-hidden="true"></div>
            <div class="guided-step-head">
                <svg class="guided-step-icon" aria-hidden="true"><use href="#${iconId}"></use></svg>
                <div class="guided-step-label">
                    <span class="guided-step-label-text">${this._escape(stepLabel)}</span>
                    <span class="guided-step-label-sub">Step ${stepNum} of ${totalSteps}</span>
                </div>
                <button type="button" class="guided-skip-link" title="Skip the wizard and generate now">Skip wizard</button>
            </div>
            <div class="guided-step-body"></div>
        `;
        el.querySelector('.guided-skip-link').addEventListener('click', () => this._skipWizard());
        this.host.messagesArea.appendChild(el);
        this._stepEl = el;
        this.host.scrollToBottom();
        return el.querySelector('.guided-step-body');
    }

    _replaceStepWithSummary(title, valueText) {
        if (!this._stepEl) return;
        const v = (valueText || '(skipped)').trim() || '(skipped)';
        this._stepEl.innerHTML = `
            <div class="guided-summary-chip">
                <svg class="guided-summary-check" aria-hidden="true"><use href="#icon-check"></use></svg>
                <span class="guided-summary-title">${this._escape(title)}:</span>
                <span class="guided-summary-value">${this._escape(v)}</span>
            </div>
        `;
        this._stepEl.classList.add('guided-step-locked');
        this._stepEl = null;
    }

    _skipWizard() {
        this._active = false;
        if (this._stepEl) {
            this._stepEl.remove();
            this._stepEl = null;
        }
        this.host.addMessage('ai', 'Skipping wizard — generating from your original message.');
        if (this.host.fallbackToStandardChat) {
            this.host.fallbackToStandardChat(this._initialMessage);
        }
    }

    // ───────────────── Step 1: Business Info ─────────────────
    _renderBusinessInfo() {
        const body = this._newStep('Business basics');
        body.innerHTML = `
            <div class="guided-form-group">
                <label>Business name</label>
                <input type="text" class="guided-input" id="gf-business-name"
                    placeholder="e.g., Sweet Dreams Bakery"
                    value="${this._escape(this.businessContext.business_name)}">
            </div>
            <div class="guided-form-group">
                <label>What does your business do?</label>
                <textarea class="guided-textarea" id="gf-business-desc" rows="3"
                    placeholder="1-2 sentences — what you offer, who it's for">${this._escape(this.businessContext.description)}</textarea>
            </div>
            <div class="guided-actions">
                <button type="button" class="guided-btn-primary" id="gf-next">
                    <span>Continue</span>
                    <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                </button>
            </div>
        `;
        const nameEl = body.querySelector('#gf-business-name');
        const descEl = body.querySelector('#gf-business-desc');
        setTimeout(() => nameEl && nameEl.focus(), 60);

        body.querySelector('#gf-next').addEventListener('click', () => {
            const name = (nameEl.value || '').trim();
            const desc = (descEl.value || '').trim();
            if (!name) { nameEl.focus(); nameEl.classList.add('guided-input-error'); return; }
            this.businessContext.business_name = name;
            this.businessContext.description = desc;

            // Re-run industry detection using description if not already set
            if (!this.businessContext.industry) {
                this.businessContext.industry = detectIndustry(`${this._initialMessage} ${desc}`) || '';
            }

            this._replaceStepWithSummary('Business', name + (desc ? ` — ${desc}` : ''));
            this._goto('INDUSTRY_SELECT');
        });
    }

    // ───────────────── Step 2: Industry select ─────────────────
    _renderIndustrySelect() {
        const body = this._newStep('Industry');
        const industries = (this._config && this._config.industries) || {};
        const entries = Object.entries(industries);

        // Group by category
        const byCat = { services: [], products: [], events: [] };
        for (const [key, entry] of entries) {
            const cat = entry.category || 'services';
            if (!byCat[cat]) byCat[cat] = [];
            byCat[cat].push([key, entry]);
        }

        const detected = this.businessContext.industry;
        const renderCat = (list) => list.map(([key, entry]) => `
            <button type="button" class="guided-card ${key === detected ? 'selected' : ''}"
                data-key="${this._escape(key)}">
                <div class="guided-card-title">${this._escape(entry.label || key)}</div>
            </button>
        `).join('');

        body.innerHTML = `
            <p class="guided-prompt">${detected
                ? `I detected <strong>${this._escape(industries[detected]?.label || detected)}</strong> — confirm or change:`
                : `Which best describes your business?`}</p>
            <div class="guided-tabs">
                <button type="button" class="guided-tab active" data-tab="services">Services</button>
                <button type="button" class="guided-tab" data-tab="products">Products</button>
                <button type="button" class="guided-tab" data-tab="events">Events</button>
            </div>
            <div class="guided-tabpanel" data-panel="services">
                <div class="guided-card-grid">${renderCat(byCat.services || [])}</div>
            </div>
            <div class="guided-tabpanel hidden" data-panel="products">
                <div class="guided-card-grid">${renderCat(byCat.products || [])}</div>
            </div>
            <div class="guided-tabpanel hidden" data-panel="events">
                <div class="guided-card-grid">${renderCat(byCat.events || [])}</div>
            </div>
            <div class="guided-actions">
                <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                <button type="button" class="guided-btn-primary" id="gf-next" ${detected ? '' : 'disabled'}>
                    <span>Continue</span>
                    <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                </button>
            </div>
        `;

        // Open the tab containing the detected industry
        if (detected && industries[detected]) {
            const cat = industries[detected].category || 'services';
            body.querySelectorAll('.guided-tab').forEach(t =>
                t.classList.toggle('active', t.dataset.tab === cat));
            body.querySelectorAll('.guided-tabpanel').forEach(p =>
                p.classList.toggle('hidden', p.dataset.panel !== cat));
        }

        // Tab switching
        body.querySelectorAll('.guided-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                body.querySelectorAll('.guided-tab').forEach(t => t.classList.toggle('active', t === tab));
                body.querySelectorAll('.guided-tabpanel').forEach(p =>
                    p.classList.toggle('hidden', p.dataset.panel !== tab.dataset.tab));
            });
        });

        // Card selection
        const nextBtn = body.querySelector('#gf-next');
        body.querySelectorAll('.guided-card').forEach(card => {
            card.addEventListener('click', () => {
                body.querySelectorAll('.guided-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.businessContext.industry = card.dataset.key;
                nextBtn.disabled = false;
            });
        });

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            this._stepEl.remove();
            this._stepEl = null;
            this._goto('BUSINESS_INFO');
        });

        nextBtn.addEventListener('click', () => {
            if (!this.businessContext.industry) return;
            const label = industries[this.businessContext.industry]?.label || this.businessContext.industry;
            this._replaceStepWithSummary('Industry', label);
            this._goto('PURPOSE_SELECT');
        });
    }

    // ───────────────── Step 3: Purpose / variant ─────────────────
    _renderPurposeSelect() {
        const body = this._newStep('Page purpose');
        const industries = (this._config && this._config.industries) || {};
        const industryEntry = industries[this.businessContext.industry] || {};
        const variants = industryEntry.variants || [];

        if (!variants.length) {
            // No variants configured — use the generic PAGE_PURPOSES as fallback
            const purposes = (this._config.page_purposes && this._config.page_purposes.purposes) || [];
            body.innerHTML = `
                <p class="guided-prompt">What's the main purpose of this site?</p>
                <div class="guided-card-grid">
                    ${purposes.map(p => `
                        <button type="button" class="guided-variant-card" data-key="${this._escape(p.id)}" data-label="${this._escape(p.label)}">
                            <div class="guided-card-title">${this._escape(p.label)}</div>
                            <div class="guided-card-desc">${this._escape(p.description || '')}</div>
                        </button>
                    `).join('')}
                </div>
                <div class="guided-actions">
                    <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                    <button type="button" class="guided-btn-primary" id="gf-next" disabled>
                        <span>Continue</span>
                        <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                    </button>
                </div>
            `;
        } else {
            body.innerHTML = `
                <p class="guided-prompt">What kind of ${this._escape(industryEntry.label || 'business')} is it?</p>
                <div class="guided-variant-grid">
                    ${variants.map(v => `
                        <button type="button" class="guided-variant-card" data-key="${this._escape(v.id)}" data-label="${this._escape(v.label)}">
                            <div class="guided-card-title">${this._escape(v.label)}</div>
                            ${v.purpose ? `<div class="guided-card-desc">${this._escape(v.purpose)}</div>` : ''}
                            ${v.description ? `<div class="guided-card-hint">${this._escape(v.description)}</div>` : ''}
                        </button>
                    `).join('')}
                </div>
                <div class="guided-actions">
                    <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                    <button type="button" class="guided-btn-primary" id="gf-next" disabled>
                        <span>Continue</span>
                        <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                    </button>
                </div>
            `;
        }

        const nextBtn = body.querySelector('#gf-next');
        let chosen = null;
        body.querySelectorAll('.guided-variant-card').forEach(card => {
            card.addEventListener('click', () => {
                body.querySelectorAll('.guided-variant-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                chosen = { id: card.dataset.key, label: card.dataset.label };
                nextBtn.disabled = false;
            });
        });

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            this._stepEl.remove();
            this._stepEl = null;
            this._goto('INDUSTRY_SELECT');
        });

        nextBtn.addEventListener('click', () => {
            if (!chosen) return;
            this.businessContext.variant_id = chosen.id;
            this.businessContext.variant_label = chosen.label;
            this._replaceStepWithSummary('Purpose', chosen.label);
            this._goto('SECTION_SELECT');
        });
    }

    // ───────────────── Step 4: Section select ─────────────────
    _renderSectionSelect() {
        const body = this._newStep('Sections to include');
        const industries = (this._config && this._config.industries) || {};
        const industryEntry = industries[this.businessContext.industry] || {};
        const variant = (industryEntry.variants || []).find(v => v.id === this.businessContext.variant_id);

        // Pre-selected sections from variant, fallback to category flow
        const flows = (this._config.recommendations && this._config.recommendations.category_flows) || {};
        const categoryFallback = flows[industryEntry.category] || [];
        const preselected = new Set((variant && variant.sections) ? variant.sections : categoryFallback);

        // Union of: preselected + all known section types (so user can add extras)
        const known = Object.keys((this._config.section_questions || {}));
        const all = new Set([...preselected, ...known]);
        // Always offer these even if not in questions
        ['navigation', 'footer'].forEach(s => all.add(s));

        const ordered = Array.from(all);
        // Keep variant's order first, then append the rest
        const variantOrder = variant && variant.sections ? variant.sections : [];
        const rest = ordered.filter(s => !variantOrder.includes(s));
        const sortedSections = [...variantOrder, ...rest];

        const cardsHtml = sortedSections.map(s => `
            <label class="guided-check-card ${preselected.has(s) ? 'selected' : ''}">
                <input type="checkbox" ${preselected.has(s) ? 'checked' : ''} value="${this._escape(s)}">
                <span class="guided-check-box" aria-hidden="true"></span>
                <span class="guided-check-label">${this._escape(labelFor(s))}</span>
            </label>
        `).join('');

        body.innerHTML = `
            <p class="guided-prompt">We pre-selected the usual sections for this type of site. Add or remove as you like.</p>
            <div class="guided-check-grid">${cardsHtml}</div>
            <div class="guided-hint" id="gf-rec-hint" hidden></div>
            <div class="guided-actions">
                <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                <button type="button" class="guided-btn-primary" id="gf-next">
                    <span>Continue</span>
                    <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                </button>
            </div>
        `;

        const recs = (this._config.recommendations && this._config.recommendations.section_pairs) || {};
        const checkboxes = body.querySelectorAll('input[type="checkbox"]');
        const hintEl = body.querySelector('#gf-rec-hint');
        const dismissed = new Set();

        const currentSelection = () => Array.from(checkboxes)
            .filter(c => c.checked)
            .map(c => c.value);

        const refreshHint = () => {
            const selected = new Set(currentSelection());
            // For each newly-added section, surface its recommendation once
            let shown = null;
            for (const key of selected) {
                const rec = recs[key];
                if (!rec || !rec.suggest) continue;
                const missing = rec.suggest.filter(s => !selected.has(s) && !dismissed.has(s));
                if (missing.length) { shown = { trigger: key, missing, reason: rec.reason }; break; }
            }
            if (!shown) { hintEl.hidden = true; hintEl.innerHTML = ''; return; }
            hintEl.hidden = false;
            hintEl.innerHTML = `
                <svg class="guided-hint-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                <span class="guided-hint-text">Sites with <strong>${this._escape(labelFor(shown.trigger))}</strong> also add:</span>
                ${shown.missing.map(m => `<button type="button" class="guided-hint-add" data-add="${this._escape(m)}">+ ${this._escape(labelFor(m))}</button>`).join('')}
                <button type="button" class="guided-hint-dismiss" data-dismiss-trigger="${this._escape(shown.trigger)}" title="Dismiss">
                    <svg aria-hidden="true"><use href="#icon-x"></use></svg>
                </button>
            `;
            hintEl.querySelectorAll('.guided-hint-add').forEach(btn => {
                btn.addEventListener('click', () => {
                    const key = btn.dataset.add;
                    const box = Array.from(checkboxes).find(c => c.value === key);
                    if (box) {
                        box.checked = true;
                        box.closest('.guided-check-card').classList.add('selected');
                    }
                    refreshHint();
                });
            });
            hintEl.querySelectorAll('.guided-hint-dismiss').forEach(btn => {
                btn.addEventListener('click', () => {
                    (recs[btn.dataset.dismissTrigger]?.suggest || []).forEach(s => dismissed.add(s));
                    refreshHint();
                });
            });
        };

        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                cb.closest('.guided-check-card').classList.toggle('selected', cb.checked);
                refreshHint();
            });
        });
        refreshHint();

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            this._stepEl.remove();
            this._stepEl = null;
            this._goto('PURPOSE_SELECT');
        });

        body.querySelector('#gf-next').addEventListener('click', () => {
            const chosen = currentSelection();
            if (!chosen.length) {
                hintEl.hidden = false;
                hintEl.innerHTML = `
                    <svg class="guided-hint-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                    <span class="guided-hint-text">Pick at least one section.</span>
                `;
                return;
            }
            // Preserve chosen ordering (variant order first, then rest)
            this.businessContext.sections = chosen.map(type => ({ type, content: {} }));
            this._sectionCursor = 0;
            this._replaceStepWithSummary('Sections', chosen.map(labelFor).join(', '));
            this._goto('SECTION_CONTENT');
        });
    }

    // ───────────────── Step 5: Section content (loop) ─────────────────
    _renderSectionContent() {
        const sections = this.businessContext.sections;
        // Skip sections that have no question fields (nothing to ask)
        const sectionQuestions = this._config.section_questions || {};
        while (this._sectionCursor < sections.length) {
            const s = sections[this._sectionCursor];
            const qs = sectionQuestions[s.type];
            if (qs && Array.isArray(qs.base_fields) && qs.base_fields.length) break;
            this._sectionCursor++;
        }
        if (this._sectionCursor >= sections.length) {
            // Nothing more to ask — go to style
            this._goto('STYLE_SELECT');
            return;
        }

        const idx = this._sectionCursor;
        const section = sections[idx];
        const qs = sectionQuestions[section.type];

        // Merge industry overrides
        const overrides = (qs.industry_overrides || {})[this.businessContext.industry] || {};
        const fields = qs.base_fields.map(f => {
            const ov = overrides[f.key] || {};
            return { ...f, ...ov };
        });

        // count how many content steps there are total for progress display
        const totalContent = sections.filter(s => {
            const q = sectionQuestions[s.type];
            return q && Array.isArray(q.base_fields) && q.base_fields.length;
        }).length;
        const contentOrdinal = sections
            .slice(0, idx + 1)
            .filter(s => {
                const q = sectionQuestions[s.type];
                return q && Array.isArray(q.base_fields) && q.base_fields.length;
            }).length;

        const body = this._newStep(`${labelFor(section.type)} content (${contentOrdinal}/${totalContent})`);

        const fieldHtml = fields.map(f => {
            const val = section.content[f.key] || '';
            const label = this._escape(f.label || f.key);
            const placeholder = this._escape(f.placeholder || '');
            if (f.type === 'textarea') {
                return `
                    <div class="guided-form-group">
                        <label>${label}</label>
                        <textarea class="guided-textarea" data-key="${this._escape(f.key)}" rows="3"
                            placeholder="${placeholder}">${this._escape(val)}</textarea>
                    </div>
                `;
            }
            return `
                <div class="guided-form-group">
                    <label>${label}</label>
                    <input type="text" class="guided-input" data-key="${this._escape(f.key)}"
                        placeholder="${placeholder}" value="${this._escape(val)}">
                </div>
            `;
        }).join('');

        body.innerHTML = `
            <p class="guided-prompt">Tell me what to put in the <strong>${this._escape(labelFor(section.type))}</strong> section. Leave blank to skip a field.</p>
            ${fieldHtml}
            <div class="guided-actions">
                <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                <button type="button" class="guided-btn-skip" data-act="skip">Skip</button>
                <button type="button" class="guided-btn-primary" data-act="next">${idx + 1 === sections.length ? 'Finish content' : 'Next section'}</button>
            </div>
        `;

        const collect = () => {
            const inputs = body.querySelectorAll('[data-key]');
            const content = {};
            inputs.forEach(inp => {
                const v = (inp.value || '').trim();
                if (v) content[inp.dataset.key] = v;
            });
            return content;
        };

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            // Save current progress before going back
            section.content = collect();
            this._stepEl.remove();
            this._stepEl = null;
            if (this._sectionCursor === 0) {
                this._goto('SECTION_SELECT');
            } else {
                // Step back to previous content section (that had fields)
                const sq = sectionQuestions;
                let j = this._sectionCursor - 1;
                while (j >= 0) {
                    const q = sq[sections[j].type];
                    if (q && Array.isArray(q.base_fields) && q.base_fields.length) break;
                    j--;
                }
                this._sectionCursor = Math.max(0, j);
                this._goto('SECTION_CONTENT');
            }
        });

        body.querySelector('[data-act="skip"]').addEventListener('click', () => {
            section.content = {};
            this._replaceStepWithSummary(labelFor(section.type), '(skipped)');
            this._sectionCursor++;
            this._goto('SECTION_CONTENT');
        });

        body.querySelector('[data-act="next"]').addEventListener('click', () => {
            section.content = collect();
            const summary = Object.entries(section.content)
                .map(([k, v]) => `${k}: ${v.split('\n')[0].slice(0, 40)}`)
                .slice(0, 2)
                .join(' · ') || '(no content)';
            this._replaceStepWithSummary(labelFor(section.type), summary);
            this._sectionCursor++;
            this._goto('SECTION_CONTENT');
        });
    }

    // ───────────────── Step 6: Style ─────────────────
    _renderStyleSelect() {
        const body = this._newStep('Style & colors');
        const styles = (this._config.styles && this._config.styles.canonical) || [];
        const defaultStyles = (this._config.styles && this._config.styles.industry_default_style) || {};
        const suggested = defaultStyles[this.businessContext.industry] || '';

        const cardsHtml = styles.map(s => `
            <button type="button" class="guided-card guided-style-card ${s.id === suggested ? 'selected' : ''}"
                data-key="${this._escape(s.id)}" title="${this._escape(s.label)}">
                <div class="guided-card-title">${this._escape(s.label)}</div>
                ${s.id === suggested ? '<div class="guided-card-hint">Recommended</div>' : ''}
            </button>
        `).join('');

        body.innerHTML = `
            <p class="guided-prompt">Pick a visual style${suggested ? ' — we pre-selected one that matches your industry.' : '.'}</p>
            <div class="guided-style-grid">${cardsHtml}</div>
            <div class="guided-form-group">
                <label>Color preference (optional)</label>
                <input type="text" class="guided-input" id="gf-colors"
                    placeholder="e.g., warm earth tones, navy + gold, pastel pink"
                    value="${this._escape(this.businessContext.color_preference || '')}">
            </div>
            <div class="guided-actions">
                <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                <button type="button" class="guided-btn-primary" id="gf-next" ${suggested ? '' : 'disabled'}>
                    <span>Continue</span>
                    <svg aria-hidden="true"><use href="#icon-arrow-right"></use></svg>
                </button>
            </div>
        `;

        this.businessContext.style_preference = suggested;
        const nextBtn = body.querySelector('#gf-next');
        body.querySelectorAll('.guided-style-card').forEach(card => {
            card.addEventListener('click', () => {
                body.querySelectorAll('.guided-style-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.businessContext.style_preference = card.dataset.key;
                nextBtn.disabled = false;
            });
        });

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            this._stepEl.remove();
            this._stepEl = null;
            // go back to section content loop last step
            this._sectionCursor = Math.max(0, this.businessContext.sections.length - 1);
            this._goto('SECTION_CONTENT');
        });

        nextBtn.addEventListener('click', () => {
            try {
                const colorInput = body.querySelector('#gf-colors');
                this.businessContext.color_preference = colorInput ? colorInput.value.trim() : '';
                if (!this.businessContext.style_preference) {
                    console.warn('[GuidedFlow] style Continue clicked with empty style_preference');
                    return;
                }
                const styleLabel = styles.find(s => s.id === this.businessContext.style_preference)?.label
                    || this.businessContext.style_preference;
                this._replaceStepWithSummary('Style', styleLabel
                    + (this.businessContext.color_preference ? ` · ${this.businessContext.color_preference}` : ''));
                this._goto('REVIEW');
            } catch (err) {
                console.error('[GuidedFlow] STYLE_SELECT → REVIEW failed:', err);
                this.host.addMessage('ai', `Could not advance from Style step: ${err.message}`, { isError: true });
            }
        });
    }

    // ───────────────── Step 7: Review ─────────────────
    _renderReview() {
        const body = this._newStep('Review & generate');
        const bc = this.businessContext;
        const industries = this._config.industries || {};
        const industryLabel = industries[bc.industry]?.label || bc.industry;
        const sectionsList = bc.sections.map(s => labelFor(s.type)).join(', ');
        const contentCount = bc.sections.filter(s => Object.keys(s.content || {}).length).length;

        const row = (label, value) => `
            <div class="guided-review-row">
                <span class="guided-review-label">${this._escape(label)}</span>
                <span class="guided-review-value">${this._escape(value)}</span>
            </div>
        `;

        body.innerHTML = `
            <p class="guided-prompt">Looks good? Review and hit generate.</p>
            <div class="guided-review">
                ${row('Business', bc.business_name)}
                ${bc.description ? row('About', bc.description) : ''}
                ${row('Industry', industryLabel)}
                ${bc.variant_label ? row('Purpose', bc.variant_label) : ''}
                ${row('Sections', sectionsList)}
                ${row('Content filled', `${contentCount} of ${bc.sections.length} sections`)}
                ${row('Style', bc.style_preference + (bc.color_preference ? ` · ${bc.color_preference}` : ''))}
            </div>
            <div class="guided-actions">
                <button type="button" class="guided-btn-secondary" data-act="back">Back</button>
                <button type="button" class="guided-btn-primary" id="gf-generate">
                    <svg aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                    <span>Generate Website</span>
                </button>
            </div>
        `;

        body.querySelector('[data-act="back"]').addEventListener('click', () => {
            this._stepEl.remove();
            this._stepEl = null;
            this._goto('STYLE_SELECT');
        });

        body.querySelector('#gf-generate').addEventListener('click', () => {
            this._goto('GENERATING');
        });
    }

    // ───────────────── Step 8: Generate ─────────────────
    async _runGeneration() {
        this._replaceStepWithSummary('Review', 'submitted → generating');
        this.host.showLoading();
        this.host.updateLoadingText('Planning your site...');

        // Poll backend for progress status updates
        const statusInterval = setInterval(async () => {
            try {
                const res = await fetch('/api/chat/status');
                const data = await res.json();
                if (data.active && data.message) {
                    this.host.updateLoadingText(data.message);
                }
            } catch (_) { /* ignore */ }
        }, 2000);

        const siteId = getCurrentSiteId();
        const currentYaml = this.host.getCurrentYaml ? this.host.getCurrentYaml() : '';

        try {
            const result = await chatService.sendGuidedRequest(this.businessContext, currentYaml, siteId);
            clearInterval(statusInterval);
            this.host.hideLoading();
            this._active = false;
            this._state = 'DONE';

            // Delegate result display to the host (same handling as regular chat)
            if (this.host.handleGuidedResult) {
                this.host.handleGuidedResult(result);
            }
        } catch (err) {
            clearInterval(statusInterval);
            this.host.hideLoading();
            this._active = false;
            this._state = 'DONE';
            this.host.addMessage('ai', `Generation failed: ${err.message}`, { isError: true });
            console.error('[GuidedFlow] generation error:', err);
        }
    }

    // ───────────────── Utils ─────────────────
    _escape(text) {
        return String(text == null ? '' : text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

// Regex used by chat.js to decide when to activate the guided flow.
export const CREATE_PAGE_RE = /\b(create|build|make|generate|design)\b.*\b(page|website|site|landing)\b/i;
