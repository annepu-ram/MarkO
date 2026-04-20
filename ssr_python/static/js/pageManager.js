/**
 * Page Manager - Site format helpers, UUID generation, page navigation.
 * Site wrapper is always expected — no backward compatibility with old format.
 *
 * For API-backed site/page CRUD (create, autosave, load, delete),
 * use siteManager.js instead. This module handles YAML structure extraction
 * and the in-editor page panel UI.
 */

import { getYamlStructureFromEditor, getYamlDocumentFromEditor, updateYamlEditor, generateYamlFromDocument } from './yamlUtils.js';
import { parse, stringify, parseDocument, YAML } from './yamlWrapper.js';

// ============================================================================
// UUID Generation (Backend)
// ============================================================================

/**
 * Generate a UUID v4 for a new site via backend API
 * @returns {Promise<string>} UUID string
 */
export async function generateSiteId() {
    try {
        const res = await fetch('/api/site/generate-id');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.id;
    } catch (err) {
        console.error('[PageManager] Failed to generate site ID:', err);
        // Fallback to crypto.randomUUID() if backend is unreachable
        return crypto.randomUUID();
    }
}

// ============================================================================
// Page Extraction
// ============================================================================

/**
 * Get the page object from a site-wrapped structure
 * @param {Array} structure - Parsed YAML structure (site wrapper expected)
 * @returns {object|null} The page component object
 */
export function getPageFromStructure(structure) {
    if (!Array.isArray(structure) || structure.length === 0) return null;
    const site = structure[0];
    return site.components?.[0] || null;
}

/**
 * Get the list of pages from a site structure
 * @param {Array} structure - Parsed YAML structure (site wrapper expected)
 * @returns {Array} Array of {id, slug, title, index} objects
 */
export function getPageList(structure) {
    if (!Array.isArray(structure) || structure.length === 0) return [];
    const site = structure[0];
    return (site.components || []).map((page, index) => ({
        id: page.id || `page-${index + 1}`,
        slug: page.slug || '',
        title: page.title || `Page ${index + 1}`,
        index
    }));
}

// ============================================================================
// Page Operations
// ============================================================================

/**
 * Add a new blank page to the site
 * @param {string} title - Page title
 * @param {string} slug - URL slug
 * @returns {Promise<string|null>} Updated YAML text, or null on failure
 */
export async function addPage(title, slug) {
    const doc = getYamlDocumentFromEditor();
    if (!doc) return null;

    const structure = getYamlStructureFromEditor();
    if (!structure || structure.length === 0) return null;

    const site = structure[0];
    const pageCount = (site.components || []).length;
    const pageId = `page-${pageCount + 1}`;

    // New pages inherit the site-level theme automatically (CSS vars cascade from .site-wrapper)
    const newPage = {
        name: 'page',
        id: pageId,
        slug: slug || `page-${pageCount + 1}`,
        title: title || `Page ${pageCount + 1}`,
        properties: {
            appearance: {
                background: {
                    color: '#ffffff',
                    opacity: 100
                }
            }
        },
        components: []
    };

    // Navigate to site.components in the document and add the new page
    const siteNode = doc.contents?.items?.[0];
    if (!siteNode) return null;

    const componentsNode = siteNode.get('components');
    if (componentsNode && YAML.isSeq(componentsNode)) {
        componentsNode.add(doc.createNode(newPage));
    }

    const yamlText = generateYamlFromDocument(doc);
    return yamlText;
}

// ============================================================================
// Pages Panel Rendering
// ============================================================================

/**
 * Render the Pages panel content
 * @param {HTMLElement} container - The panel content container (#pagesContent)
 * @param {HTMLElement} footer - The panel footer container (#pagesFooter)
 * @param {object} callbacks - { onPageSwitch, onAddPage }
 */
export function renderPagesPanel(container, footer, callbacks = {}, options = {}) {
    if (!container) return;

    // Use provided pages (from API) or extract from editor YAML
    let pages;
    if (options.pages) {
        pages = options.pages.map((p, index) => ({
            id: p.id,
            slug: p.slug || '',
            title: p.title || `Page ${index + 1}`,
            is_homepage: p.is_homepage || false,
            index
        }));
    } else {
        const structure = getYamlStructureFromEditor();
        pages = getPageList(structure);
    }
    const activeIndex = options.activeIndex ?? 0;

    // Render page list
    container.innerHTML = '';
    pages.forEach((page, index) => {
        const item = document.createElement('div');
        item.className = 'page-list-item' + (index === activeIndex ? ' active' : '');
        item.dataset.pageIndex = index;

        const infoEl = document.createElement('div');
        infoEl.className = 'page-list-item-info';

        const titleEl = document.createElement('div');
        titleEl.className = 'page-list-item-title';
        titleEl.textContent = page.title;

        const slugEl = document.createElement('div');
        slugEl.className = 'page-list-item-slug';
        slugEl.textContent = `/${page.slug}`;

        infoEl.appendChild(titleEl);
        infoEl.appendChild(slugEl);
        item.appendChild(infoEl);

        // Delete button (hidden unless multiple pages exist)
        if (pages.length > 1) {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'page-delete-btn';
            deleteBtn.title = 'Delete page';
            deleteBtn.innerHTML = '<svg aria-hidden="true" width="14" height="14"><use href="#icon-trash-2"></use></svg>';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (callbacks.onDeletePage) {
                    callbacks.onDeletePage(index, page);
                }
            });
            item.appendChild(deleteBtn);
        }

        item.addEventListener('click', () => {
            // Update active state
            container.querySelectorAll('.page-list-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            if (callbacks.onPageSwitch) {
                callbacks.onPageSwitch(index, page);
            }
        });

        container.appendChild(item);
    });

    // Render footer with Add Page button
    if (footer) {
        footer.innerHTML = '';
        const addBtn = document.createElement('button');
        addBtn.className = 'page-add-btn';
        addBtn.innerHTML = '<svg aria-hidden="true" width="14" height="14"><use href="#icon-file-plus"></use></svg> Add Page';
        addBtn.addEventListener('click', () => {
            if (callbacks.onAddPage) {
                callbacks.onAddPage();
            }
        });
        footer.appendChild(addBtn);
    }
}
