import { initializeEvents } from './events.js';
import { renderPreview, getPathMapBuilder } from './ssr_app.js';
import { SelectionManager } from './selectionManager.js';
import { loadMetadata, getComponentDefaults } from './metadataLoader.js';
import { renderPropertiesPanel, clearPropertiesPanel, collectPropertyValues, getActiveComponentInfo } from './propertiesPanel.js';
import { getYamlStructureFromEditor, getYamlDocumentFromEditor, getComponentByPath, updateComponentByPath, generateYamlFromStructure, generateYamlFromDocument, updateYamlEditor, updateComponentPropertiesInDocument, navigateToComponent, replacePropertiesWithAliases, deleteComponentInDocument, insertComponentInDocument, moveComponentInDocument, getChildrenKey } from './yamlUtils.js';
import { historyManager } from './historyManager.js';
import { loadSvgSprite } from './sprite.js';
import { deepMerge } from './utils/object.js';
import { initComponentTree, buildTreeFromStructure, renderTree, highlightTreeItem, clearTreeSelection, initTreeActions, showComponentPicker, getClipboard, setClipboard } from './componentTree.js';
import { debounce } from './utils/timing.js';
import { renderThemesPanel, applyTheme } from './themesPanel.js';
import { renderImagesPanel } from './imagesPanel.js';
import { renderSettingsPanel } from './settingsPanel.js';
import { getPageFromStructure, renderPagesPanel, addPage } from './pageManager.js';
import { autosave, saveNow, loadSite, loadPage, listPages, createPage, deletePage, setCurrentSite, setCurrentPage, getSiteSettings } from './siteManager.js';

// Create singleton selection manager instance
export const selectionManager = new SelectionManager();

// 1. Get all DOM references, same as the original app
function getDomReferences() {
    const appContainer = document.getElementById('appContainer');
    return {
        appContainer,
        editor: document.getElementById('codeEditor'),
        lineNumbers: document.getElementById('lineNumbers'),
        editorWrapper: document.getElementById('editorWrapper'),
        preview: document.getElementById('preview'),
        propertiesPanel: document.getElementById('propPanel'),
        propertiesContent: document.getElementById('propertiesContent'),
        resizer: document.getElementById('resizer'),
        sidebar: document.querySelector('.sidebar'),
        sidebarResizer: document.getElementById('sidebarResizer'),
        sidebarNavItems: Array.from(document.querySelectorAll('.sidebar-nav-item')),
        sidebarPanels: Array.from(document.querySelectorAll('.sidebar-panel')),
        undoButton: document.getElementById('undoBtn'),
        redoButton: document.getElementById('redoBtn'),
        exportButton: document.getElementById('exportBtn'),
        clearButton: document.getElementById('clearBtn'),
        fullscreenButton: document.getElementById('fullscreenBtn'),
        closeFullscreenButton: document.getElementById('closeFullscreenBtn'),
        helpButton: document.getElementById('helpBtn'),
        componentButtons: Array.from(document.querySelectorAll('.component-item')),
        componentTree: document.getElementById('componentTree'),
    };
}

/**
 * Updates line numbers in the editor gutter
 */
function updateLineNumbers(editor, lineNumbers) {
    if (!editor || !lineNumbers) return;
    
    const lines = editor.value.split('\n');
    const lineCount = lines.length || 1;
    
    // Build line numbers HTML
    let html = '';
    for (let i = 1; i <= lineCount; i++) {
        html += `<span>${i}</span>`;
    }
    lineNumbers.innerHTML = html;
}

/**
 * Syncs scroll position between editor and line numbers
 */
function syncEditorScroll(editor, lineNumbers) {
    if (!editor || !lineNumbers) return;
    lineNumbers.scrollTop = editor.scrollTop;
}

/**
 * Enable/disable undo and redo toolbar buttons based on history state
 */
function updateHistoryButtons() {
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    if (undoBtn) undoBtn.disabled = !historyManager.canUndo();
    if (redoBtn) redoBtn.disabled = !historyManager.canRedo();
}

/**
 * Build a self-contained HTML page from rendered component HTML.
 * Fetches and inlines CSS, JS, and SVG sprite so the result works standalone.
 */
async function buildStandaloneHtml(renderedHtml, pageTitle = 'Swift Sites Export', seoMeta = {}) {
    const [tokensCss, componentsCss, runtimeJs, spriteSvg, lucideJs] = await Promise.all([
        fetch('/static/css/tokens.css').then(r => r.text()),
        fetch('/static/css/components.css').then(r => r.text()),
        fetch('/static/js/swift-sites-runtime.js').then(r => r.text()),
        fetch('/static/icon-sprite.svg').then(r => r.text()),
        fetch('/static/js/lucide.min.js').then(r => r.text()),
    ]);

    const baseStyles = `* { box-sizing: border-box; }
html { font-size: clamp(12px, 1vw + 8px, 18px); }
body { margin:0; padding:0; min-height:100%; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; font-size:1rem; line-height:1.5; color:#1f2937; background:#fff; }
#preview-content { min-height:100vh; }
.page { min-height:100vh; position:relative; }
.page > .titlebar { position:sticky; top:0; z-index:100; }`;

    // Escape </script> in Lucide JS content
    const safeLucideJs = lucideJs.replace(/<\/script>/gi, '<\\/script>');

    // Build SEO meta tags from settings
    const esc = s => s ? s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';
    let seoTags = '';
    if (seoMeta.metaDescription) {
        seoTags += `\n    <meta name="description" content="${esc(seoMeta.metaDescription)}">`;
    }
    if (seoMeta.ogTitle || pageTitle) {
        seoTags += `\n    <meta property="og:title" content="${esc(seoMeta.ogTitle || pageTitle)}">`;
        seoTags += `\n    <meta property="og:type" content="website">`;
    }
    if (seoMeta.metaDescription) {
        seoTags += `\n    <meta property="og:description" content="${esc(seoMeta.metaDescription)}">`;
    }
    if (seoMeta.ogImage) {
        seoTags += `\n    <meta property="og:image" content="${esc(seoMeta.ogImage)}">`;
    }
    if (seoMeta.twitterHandle) {
        seoTags += `\n    <meta name="twitter:card" content="summary_large_image">`;
        seoTags += `\n    <meta name="twitter:site" content="${esc(seoMeta.twitterHandle)}">`;
    }
    const faviconLink = seoMeta.faviconUrl
        ? `\n    <link rel="icon" href="${esc(seoMeta.faviconUrl)}">`
        : '';

    // Escape </script> inside JS content so it doesn't break the HTML parser
    const safeJs = runtimeJs.replace(/<\/script>/gi, '<\\/script>');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${pageTitle}</title>${faviconLink}${seoTags}
    <style>${baseStyles}</style>
    <style>${tokensCss}</style>
    <style>${componentsCss}</style>

</head>
<body>
    <div id="svgSpriteRoot" hidden>${spriteSvg}</div>
    <div id="preview-content">${renderedHtml}</div>
    <script>${safeLucideJs}<\/script>
    <script>${safeJs}<\/script>
</body>
</html>`;
}

// 2. Initialize the app on DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {
    const dom = getDomReferences();

    // Expose panel functions globally for events.js
    window.renderThemesPanel = renderThemesPanel;
    window.applyTheme = applyTheme;
    window.renderImagesPanel = renderImagesPanel;
    window.renderSettingsPanel = renderSettingsPanel;

    // Page management state (API-backed when SITE_ID is present)
    let _sitePages = [];
    let _activePageIndex = 0;

    window.renderPagesPanel = async () => {
        const container = document.getElementById('pagesContent');
        const footer = document.getElementById('pagesFooter');

        if (window.SITE_ID) {
            // API-backed: fetch page list from server
            try {
                _sitePages = await listPages(window.SITE_ID);
            } catch (err) {
                console.error('[Main] Failed to load pages list:', err);
                _sitePages = [];
            }

            renderPagesPanel(container, footer, {
                onPageSwitch: async (index, page) => {
                    if (index === _activePageIndex) return;
                    console.log('[Main] Switching to page:', page.title, page.id);

                    // Save current page first
                    if (dom.editor.value.trim()) {
                        await saveNow(dom.editor.value);
                    }

                    // Load new page YAML from API
                    try {
                        const pageData = await loadPage(page.id, window.SITE_ID);
                        if (pageData.yaml_content) {
                            _activePageIndex = index;
                            dom.editor.value = pageData.yaml_content;
                            updateLineNumbers(dom.editor, dom.lineNumbers);

                            // Reset history for new page context
                            historyManager.clear();
                            historyManager.push(pageData.yaml_content);
                            updateHistoryButtons();

                            // Re-render preview and tree
                            await renderPreview(pageData.yaml_content);
                            updateComponentTree();

                            // Clear selection
                            selectionManager.clearSelection();
                            clearPropertiesPanel();
                            clearTreeSelection();
                        }
                    } catch (err) {
                        console.error('[Main] Failed to load page:', err);
                    }
                },
                onAddPage: async () => {
                    const title = prompt('Page title:');
                    if (!title) return;
                    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
                    if (!slug) return;

                    try {
                        await createPage(title, slug, window.SITE_ID);
                        // Refresh pages panel with new list
                        await window.renderPagesPanel();
                    } catch (err) {
                        alert('Failed to create page: ' + err.message);
                    }
                },
                onDeletePage: async (index, page) => {
                    if (!confirm(`Delete "${page.title}"? This cannot be undone.`)) return;
                    try {
                        await deletePage(page.id, window.SITE_ID);

                        // If we deleted the active page, switch to the first remaining page
                        if (index === _activePageIndex) {
                            _activePageIndex = 0;
                        } else if (index < _activePageIndex) {
                            _activePageIndex--;
                        }

                        // Refresh pages panel
                        await window.renderPagesPanel();

                        // If the deleted page was active, load the new active page
                        if (index === _activePageIndex || _sitePages.length > 0) {
                            const newActivePage = _sitePages[_activePageIndex];
                            if (newActivePage) {
                                const pageData = await loadPage(newActivePage.id, window.SITE_ID);
                                if (pageData.yaml_content) {
                                    dom.editor.value = pageData.yaml_content;
                                    updateLineNumbers(dom.editor, dom.lineNumbers);
                                    historyManager.clear();
                                    historyManager.push(pageData.yaml_content);
                                    updateHistoryButtons();
                                    await renderPreview(pageData.yaml_content);
                                    updateComponentTree();
                                    selectionManager.clearSelection();
                                    clearPropertiesPanel();
                                    clearTreeSelection();
                                }
                            }
                        }
                    } catch (err) {
                        alert('Failed to delete page: ' + err.message);
                    }
                }
            }, {
                pages: _sitePages,
                activeIndex: _activePageIndex,
            });
        } else {
            // Fallback: read pages from editor YAML (no site context)
            renderPagesPanel(container, footer, {
                onPageSwitch: (index) => {
                    console.log('[Main] Page switch to index:', index);
                },
                onAddPage: async () => {
                    const yamlText = await addPage();
                    if (yamlText) {
                        updateYamlEditor(yamlText);
                        historyManager.push(yamlText);
                        actions.handleEditorInput(yamlText, { pushHistory: false });
                        window.renderPagesPanel();
                    }
                }
            });
        }
    };

    // Load SVG sprite first
    const spritePath = window.SPRITE_PATH || '/static/icon-sprite.svg';
    await loadSvgSprite({ spritePath });

    // Load metadata
    await loadMetadata();

    // Function to update component tree
    const updateComponentTree = () => {
        console.log('[Main] updateComponentTree called');
        if (!dom.componentTree) {
            console.warn('[Main] componentTree DOM element not found');
            return;
        }
        const yamlStructure = getYamlStructureFromEditor();
        console.log('[Main] YAML structure:', yamlStructure);
        if (yamlStructure && yamlStructure.length > 0) {
            const treeData = buildTreeFromStructure(yamlStructure);
            console.log('[Main] Tree data built with', treeData.length, 'root nodes');
            renderTree(treeData, dom.componentTree);
        } else {
            console.log('[Main] No components in structure, showing empty message');
            dom.componentTree.innerHTML = '<p class="tree-empty">No components</p>';
        }
    };
    window.updateComponentTree = updateComponentTree;

    // Initialize component tree with selection handler
    initComponentTree(dom.componentTree, (componentId, path) => {
        // Sync tree selection with preview selection
        selectionManager.selectComponent(componentId);
    });

    // --- Tree Action Handlers ---

    /**
     * Standard save/render flow after a YAML document mutation
     */
    async function commitDocChange(yamlDoc) {
        const yamlText = generateYamlFromDocument(yamlDoc);
        if (!yamlText) return null;

        updateYamlEditor(yamlText);
        autosave(yamlText);
        historyManager.push(yamlText);
        updateHistoryButtons();

        const updatedStructure = getYamlStructureFromEditor();
        await renderPreview(yamlText, updatedStructure);
        updateComponentTree();
        return updatedStructure;
    }

    /**
     * Build a new component object from defaults
     */
    function buildNewComponent(componentName) {
        const defaults = getComponentDefaults(componentName);
        const component = { name: componentName };

        // Separate component-level arrays from properties
        const componentLevelKeys = ['items', 'tabs', 'slides', 'columns', 'components'];
        const properties = {};

        for (const [key, value] of Object.entries(defaults)) {
            if (componentLevelKeys.includes(key)) {
                component[key] = value;
            } else {
                properties[key] = value;
            }
        }

        if (Object.keys(properties).length > 0) {
            component.properties = properties;
        }

        return component;
    }

    /**
     * Handle tree action events
     */
    initTreeActions(dom.componentTree, async (action, nodeData) => {
        const { path, name, isVirtual, isContainer, sourceElement } = nodeData;

        switch (action) {
            case 'move-up':
            case 'move-down': {
                const direction = action === 'move-up' ? -1 : 1;
                const yamlDoc = getYamlDocumentFromEditor();
                if (!yamlDoc) return;

                const result = moveComponentInDocument(yamlDoc, path, direction);
                if (!result.success) return;

                const updatedStructure = await commitDocChange(yamlDoc);
                if (updatedStructure) {
                    // Select the component at its new position
                    const newId = 'comp_' + result.newPath.join('_');
                    setTimeout(() => {
                        selectionManager.selectComponent(newId);
                        highlightTreeItem(newId);
                    }, 100);
                }
                break;
            }

            case 'delete': {
                const yamlDoc = getYamlDocumentFromEditor();
                if (!yamlDoc) return;

                const deleted = deleteComponentInDocument(yamlDoc, path);
                if (!deleted) return;

                await commitDocChange(yamlDoc);
                selectionManager.clearSelection();
                clearPropertiesPanel();
                clearTreeSelection();
                break;
            }

            case 'add-child': {
                // Determine the children key for this container
                const childrenKey = isVirtual ? 'components' : getChildrenKey(name);
                if (!childrenKey) return;

                // Complex containers (columnsgrid, tabs, carousel, accordion, ticker) —
                // directly insert a structural group instead of showing picker
                const complexContainers = ['columnsgrid', 'ticker', 'tabs', 'carousel', 'accordion'];
                if (!isVirtual && complexContainers.includes(name)) {
                    const yamlDoc = getYamlDocumentFromEditor();
                    if (!yamlDoc) return;

                    let newGroup;
                    if (name === 'columnsgrid' || name === 'ticker') {
                        newGroup = { components: [] };
                    } else if (name === 'tabs') {
                        newGroup = { title: 'New Tab', components: [] };
                    } else if (name === 'carousel') {
                        newGroup = { components: [] };
                    } else if (name === 'accordion') {
                        newGroup = { title: 'New Item', components: [] };
                    }

                    const parentSeqPath = [...path, childrenKey];
                    const inserted = insertComponentInDocument(yamlDoc, parentSeqPath, newGroup);
                    if (!inserted) return;

                    await commitDocChange(yamlDoc);
                    break;
                }

                // Simple containers and virtual nodes — show picker
                showComponentPicker(sourceElement, async (componentName) => {
                    const yamlDoc = getYamlDocumentFromEditor();
                    if (!yamlDoc) return;

                    const newComponent = buildNewComponent(componentName);
                    const parentSeqPath = [...path, childrenKey];
                    const inserted = insertComponentInDocument(yamlDoc, parentSeqPath, newComponent);
                    if (!inserted) return;

                    const updatedStructure = await commitDocChange(yamlDoc);
                    // Select the newly inserted component (last child)
                    if (updatedStructure) {
                        const newComp = getComponentByPath(updatedStructure, path);
                        if (newComp) {
                            const children = newComp[childrenKey] || newComp.components;
                            if (children) {
                                const newPath = [...parentSeqPath, children.length - 1];
                                const newId = 'comp_' + newPath.join('_');
                                setTimeout(() => {
                                    selectionManager.selectComponent(newId);
                                    highlightTreeItem(newId);
                                }, 100);
                            }
                        }
                    }
                });
                break;
            }

            case 'copy': {
                const structure = getYamlStructureFromEditor();
                if (!structure) return;

                const component = getComponentByPath(structure, path);
                if (!component) return;

                // Deep clone to detach from original
                const cloned = JSON.parse(JSON.stringify(component));
                setClipboard({ component: cloned, name: component.name || name });

                // Refresh tree so paste buttons appear
                updateComponentTree();

                // Re-select the copied component
                const copiedId = 'comp_' + path.join('_');
                setTimeout(() => {
                    selectionManager.selectComponent(copiedId);
                    highlightTreeItem(copiedId);
                }, 50);
                break;
            }

            case 'paste': {
                const clipData = getClipboard();
                if (!clipData) return;

                const yamlDoc = getYamlDocumentFromEditor();
                if (!yamlDoc) return;

                // Deep clone so pasting twice creates independent copies
                const pastedComponent = JSON.parse(JSON.stringify(clipData.component));

                let inserted;
                if (isContainer || name === 'page' || isVirtual) {
                    // Paste as last child of container
                    const childrenKey = isVirtual ? 'components' : getChildrenKey(name);
                    if (!childrenKey) return;
                    const parentSeqPath = [...path, childrenKey];
                    inserted = insertComponentInDocument(yamlDoc, parentSeqPath, pastedComponent);
                } else {
                    // Paste after the selected leaf
                    const parentSeqPath = path.slice(0, -1);
                    const insertIndex = path[path.length - 1] + 1;
                    inserted = insertComponentInDocument(yamlDoc, parentSeqPath, pastedComponent, insertIndex);
                }

                if (!inserted) return;
                await commitDocChange(yamlDoc);
                break;
            }

            case 'add-after': {
                showComponentPicker(sourceElement, async (componentName) => {
                    const yamlDoc = getYamlDocumentFromEditor();
                    if (!yamlDoc) return;

                    const newComponent = buildNewComponent(componentName);
                    // Parent sequence path is everything except last index
                    const parentSeqPath = path.slice(0, -1);
                    const insertIndex = path[path.length - 1] + 1;
                    const inserted = insertComponentInDocument(yamlDoc, parentSeqPath, newComponent, insertIndex);
                    if (!inserted) return;

                    const updatedStructure = await commitDocChange(yamlDoc);
                    if (updatedStructure) {
                        const newPath = [...parentSeqPath, insertIndex];
                        const newId = 'comp_' + newPath.join('_');
                        setTimeout(() => {
                            selectionManager.selectComponent(newId);
                            highlightTreeItem(newId);
                        }, 100);
                    }
                });
                break;
            }
        }
    });

    // Set up selection change handler to update properties panel and tree
    selectionManager.onSelectionChange = (selection) => {
        console.log('[Main] onSelectionChange called with:', selection);
        if (!selection) {
            console.log('[Main] Selection cleared');
            clearPropertiesPanel();
            clearTreeSelection();
            return;
        }

        // Highlight tree item
        highlightTreeItem(selection.componentId);

        // Get component from YAML structure
        const yamlStructure = getYamlStructureFromEditor();
        const component = getComponentByPath(yamlStructure, selection.path);
        console.log('[Main] Component at path:', component);

        if (component) {
            console.log('[Main] Rendering properties panel for:', component.name);
            renderPropertiesPanel(component, selection.componentId, selection.path);

            // Auto-open the properties right panel if not already open
            if (window.toggleRightPanel && window.getCurrentRightPanel && window.getCurrentRightPanel() !== 'prop') {
                window.toggleRightPanel('prop');
            }
        } else {
            console.warn('[Main] Component not found at path, clearing properties panel');
            clearPropertiesPanel();
        }
    };

    // Create debounced render function to prevent rapid-fire requests
    const debouncedRender = debounce((yamlContent, currentSelection) => {
        renderPreview(yamlContent).then(() => {
            // Update component tree
            updateComponentTree();

            // Restore selection after re-render if it existed
            if (currentSelection && currentSelection.componentId) {
                selectionManager.restoreSelection();
                highlightTreeItem(currentSelection.componentId);
                // Restore properties panel
                const yamlStructure = getYamlStructureFromEditor();
                const component = getComponentByPath(yamlStructure, currentSelection.path);
                if (component) {
                    renderPropertiesPanel(component, currentSelection.componentId, currentSelection.path);
                }
            }
        });
    }, 300);

    // 3. Create a simplified 'actions' object for the SSR app
    const actions = {
        // The most important action: handle editor input by calling the SSR render function
        handleEditorInput: (yamlContent, options = { pushHistory: true }) => {
            // Push to history immediately (not debounced for accurate undo/redo)
            if (options.pushHistory) {
                historyManager.push(yamlContent);
            }

            // Save to DB (debounced 2s)
            autosave(yamlContent);

            // Store current selection before re-render
            const currentSelection = selectionManager.getSelection();

            // Debounce the render to prevent rapid-fire requests
            debouncedRender(yamlContent, currentSelection);

            updateHistoryButtons();
        },
        // Handle preview clicks for component selection
        handlePreviewClick: (event) => {
            selectionManager.handlePreviewClick(event);
        },
        exportCode: async () => {
            const editor = document.getElementById('codeEditor');
            const yamlContent = editor ? editor.value : '';
            if (!yamlContent.trim()) return;

            try {
                const response = await fetch('/render', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: yamlContent
                });
                const html = await response.text();

                // Extract page title from YAML
                const structure = getYamlStructureFromEditor();
                const page = structure ? getPageFromStructure(structure) : null;
                const pageTitle = page?.title || 'Swift Sites Export';

                // Fetch site settings for SEO metadata (if editing a site)
                let seoMeta = {};
                if (window.SITE_ID) {
                    try {
                        const settings = await getSiteSettings();
                        const seo = settings.seo || {};
                        const branding = settings.branding || {};
                        const social = settings.social || {};
                        seoMeta = {
                            metaDescription: seo.metaDescription,
                            ogTitle: seo.ogTitle,
                            ogImage: seo.ogImage || social.defaultShareImage,
                            faviconUrl: branding.faviconUrl,
                            twitterHandle: social.twitterHandle,
                        };
                    } catch (err) {
                        console.warn('[Export] Could not load site settings:', err);
                    }
                }

                const standaloneHtml = await buildStandaloneHtml(html, pageTitle, seoMeta);

                const blob = new Blob([standaloneHtml], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'index.html';
                a.click();
                URL.revokeObjectURL(url);
            } catch (err) {
                console.error('[Export] Failed:', err);
            }
        },
        clearCanvas: () => {
            if(dom.editor) {
                dom.editor.value = '';
                selectionManager.clearSelection();
                clearPropertiesPanel();
                clearTreeSelection();
                historyManager.clear();
                updateHistoryButtons();
                renderPreview('').then(() => {
                    updateComponentTree();
                });
            }
        },
        openFullscreen: async () => {
            const modal = document.getElementById('fullscreenModal');
            const frame = document.getElementById('fullscreenFrame');
            if (!modal || !frame) return;

            const editor = document.getElementById('codeEditor');
            const yamlContent = editor ? editor.value : '';
            if (!yamlContent.trim()) return;

            try {
                const response = await fetch('/render', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: yamlContent
                });
                const html = await response.text();
                const structure = getYamlStructureFromEditor();
                const page = structure ? getPageFromStructure(structure) : null;
                const pageTitle = page?.title || 'Swift Sites Export';

                // Fetch site settings for SEO metadata (if editing a site)
                let seoMeta = {};
                if (window.SITE_ID) {
                    try {
                        const settings = await getSiteSettings();
                        const seo = settings.seo || {};
                        const branding = settings.branding || {};
                        const social = settings.social || {};
                        seoMeta = {
                            metaDescription: seo.metaDescription,
                            ogTitle: seo.ogTitle,
                            ogImage: seo.ogImage || social.defaultShareImage,
                            faviconUrl: branding.faviconUrl,
                            twitterHandle: social.twitterHandle,
                        };
                    } catch (err) {
                        console.warn('[Fullscreen] Could not load site settings:', err);
                    }
                }

                const standaloneHtml = await buildStandaloneHtml(html, pageTitle, seoMeta);
                frame.srcdoc = standaloneHtml;
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            } catch (err) {
                console.error('[Fullscreen] Render failed:', err);
            }
        },
        closeFullscreen: () => {
            const modal = document.getElementById('fullscreenModal');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
        },
        toggleHelpPanel: () => alert('Help functionality not implemented in this version.'),
        insertComponent: () => alert('Component insertion not implemented in this version.'),
        applySelectedComponentProperties: async () => {
            // Get active component info
            const activeInfo = getActiveComponentInfo();
            if (!activeInfo.componentId || !activeInfo.path) {
                console.warn('No component selected');
                return;
            }

            // Get current YAML Document (preserves anchors/aliases)
            const yamlDoc = getYamlDocumentFromEditor();
            if (!yamlDoc) {
                console.error('Failed to parse YAML document');
                return;
            }

            // Also get plain structure for component lookup and merge logic
            const yamlStructure = getYamlStructureFromEditor();
            if (!yamlStructure) {
                console.error('Failed to parse YAML structure');
                return;
            }

            // Get current component
            const currentComponent = getComponentByPath(yamlStructure, activeInfo.path);
            if (!currentComponent) {
                console.error('Component not found at path:', activeInfo.path);
                return;
            }

            // Collect property values from form
            const collectedValues = collectPropertyValues();
            if (!collectedValues) {
                console.warn('Failed to collect property values');
                return;
            }

            // Use Document API to update properties while preserving anchors
            // This modifies the document in place
            updateComponentPropertiesInDocument(yamlDoc, activeInfo.path, collectedValues.properties);

            // Replace tagged color values with YAML aliases (theme swatch selections)
            if (collectedValues.aliases && Object.keys(collectedValues.aliases).length > 0) {
                replacePropertiesWithAliases(yamlDoc, activeInfo.path, collectedValues.aliases);
            }

            // Handle component-level updates (tabs, items, etc.) separately
            // These are typically arrays that need full replacement
            if (collectedValues.component && Object.keys(collectedValues.component).length > 0) {
                // For component-level updates, we need to set them directly on the component node
                const componentNode = navigateToComponent(yamlDoc, activeInfo.path);
                if (componentNode) {
                    for (const [key, value] of Object.entries(collectedValues.component)) {
                        componentNode.set(key, value);
                    }
                }
            }

            // Generate YAML string from Document (preserves anchors!)
            const yamlText = generateYamlFromDocument(yamlDoc);
            if (!yamlText) {
                console.error('Failed to generate YAML');
                return;
            }

            // Update editor
            updateYamlEditor(yamlText);

            // Push to history
            historyManager.push(yamlText);
            updateHistoryButtons();

            // Store selection for restoration
            const selectionToRestore = {
                componentId: activeInfo.componentId,
                path: activeInfo.path
            };

            // Re-render preview (history already pushed above)
            // Get fresh structure from the new YAML text
            const updatedStructure = getYamlStructureFromEditor();
            await renderPreview(yamlText, updatedStructure);

            // Update component tree
            updateComponentTree();

            // Restore selection after re-render
            setTimeout(() => {
                selectionManager.selectComponent(selectionToRestore.componentId);
                highlightTreeItem(selectionToRestore.componentId);
                // Restore properties panel
                const restoredComponent = getComponentByPath(updatedStructure, selectionToRestore.path);
                if (restoredComponent) {
                    renderPropertiesPanel(restoredComponent, selectionToRestore.componentId, selectionToRestore.path);
                }
            }, 100);
        },
        undo: () => {
            if (!historyManager.canUndo()) {
                return;
            }
            const previousYaml = historyManager.undo();
            if (previousYaml !== null) {
                dom.editor.value = previousYaml;
                // Re-render without pushing to history
                actions.handleEditorInput(previousYaml, { pushHistory: false });
            }
            updateHistoryButtons();
        },
        redo: () => {
            if (!historyManager.canRedo()) {
                return;
            }
            const nextYaml = historyManager.redo();
            if (nextYaml !== null) {
                dom.editor.value = nextYaml;
                // Re-render without pushing to history
                actions.handleEditorInput(nextYaml, { pushHistory: false });
            }
            updateHistoryButtons();
        },
    };

    // 4. Initialize all UI events using the original, robust function
    initializeEvents(dom, actions);

    // 5. Initialize line numbers
    updateLineNumbers(dom.editor, dom.lineNumbers);
    
    // Add scroll sync for line numbers
    dom.editor.addEventListener('scroll', () => {
        syncEditorScroll(dom.editor, dom.lineNumbers);
    });
    
    // Update line numbers on input
    dom.editor.addEventListener('input', () => {
        updateLineNumbers(dom.editor, dom.lineNumbers);
    });

    // 6. Load site and page YAML from database
    const siteId = window.SITE_ID;
    if (siteId) {
        try {
            console.log('[Main] Loading site from API:', siteId);
            const siteData = await loadSite(siteId);
            if (siteData.pages && siteData.pages.length > 0) {
                _sitePages = siteData.pages;
                const homepage = siteData.pages.find(p => p.is_homepage) || siteData.pages[0];
                _activePageIndex = siteData.pages.findIndex(p => p.id === homepage.id);
                if (_activePageIndex < 0) _activePageIndex = 0;
                const pageData = await loadPage(homepage.id, siteId);
                if (pageData.yaml_content) {
                    dom.editor.value = pageData.yaml_content;
                    updateLineNumbers(dom.editor, dom.lineNumbers);
                    console.log('[Main] Loaded page YAML from API:', homepage.slug);
                }
            }
        } catch (err) {
            console.error('[Main] Failed to load site:', err);
        }
    }

    // 7. Listen for component deletion from iframe
    window.addEventListener('iframe-component-deleted', async (event) => {
        const { componentId } = event.detail;
        const pathMap = getPathMapBuilder();
        const path = pathMap.getPath(componentId);
        if (!path) {
            console.warn('[Main] No path found for deleted component:', componentId);
            return;
        }

        const yamlDoc = getYamlDocumentFromEditor();
        if (!yamlDoc) return;

        const deleted = deleteComponentInDocument(yamlDoc, path);
        if (!deleted) {
            console.error('[Main] Failed to delete component at path:', path);
            return;
        }

        const yamlText = generateYamlFromDocument(yamlDoc);
        if (!yamlText) return;

        updateYamlEditor(yamlText);
        autosave(yamlText);
        historyManager.push(yamlText);
        updateHistoryButtons();

        // Clear selection (component no longer exists)
        selectionManager.clearSelection();
        clearPropertiesPanel();
        clearTreeSelection();

        // Re-render preview
        const updatedStructure = getYamlStructureFromEditor();
        await renderPreview(yamlText, updatedStructure);
        updateComponentTree();
    });

    // 8. Initialize history with current editor content
    if (dom.editor.value) {
        historyManager.push(dom.editor.value);
        renderPreview(dom.editor.value).then(() => {
            updateComponentTree();
        });
    } else {
        // Push empty state to history
        historyManager.push('');
        updateComponentTree();
    }
});
