import { initializeEvents } from './events.js';
import { renderPreview, extractIconNames } from './ssr_app.js';
import { SelectionManager } from './selectionManager.js';
import { loadMetadata, getComponentDefaults } from './metadataLoader.js';
import { renderPropertiesPanel, clearPropertiesPanel, collectPropertyValues, getActiveComponentInfo } from './propertiesPanel.js';
import { getYamlStructureFromEditor, getYamlDocumentFromEditor, getComponentByPath, updateComponentByPath, generateYamlFromStructure, generateYamlFromDocument, updateYamlEditor, updateComponentPropertiesInDocument, navigateToComponent, replacePropertiesWithAliases } from './yamlUtils.js';
import { historyManager } from './historyManager.js';
import { loadSvgSprite } from './sprite.js';
import { deepMerge } from './utils/object.js';
import { initComponentTree, buildTreeFromStructure, renderTree, highlightTreeItem, clearTreeSelection } from './componentTree.js';
import { debounce } from './utils/timing.js';
import { yamlStorage } from './yamlStorage.js';
import { renderThemesPanel, applyTheme } from './themesPanel.js';
import { renderImagesPanel } from './imagesPanel.js';

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
async function buildStandaloneHtml(renderedHtml, iconNames = []) {
    const [tokensCss, componentsCss, runtimeJs, spriteSvg] = await Promise.all([
        fetch('/static/css/tokens.css').then(r => r.text()),
        fetch('/static/css/components.css').then(r => r.text()),
        fetch('/static/js/swift-sites-runtime.js').then(r => r.text()),
        fetch('/static/icon-sprite.svg').then(r => r.text()),
    ]);

    const baseStyles = `* { box-sizing: border-box; }
html { font-size: clamp(12px, 1vw + 8px, 18px); }
body { margin:0; padding:0; min-height:100%; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; font-size:1rem; line-height:1.5; color:#1f2937; background:#fff; }
#preview-content { min-height:100vh; }
.page { min-height:100vh; position:relative; }
.page > .titlebar { position:sticky; top:0; z-index:100; }`;

    // Build optimized Material Symbols font link (only icons used in YAML)
    const iconFontLink = iconNames.length > 0
        ? `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0,0&icon_names=${iconNames.join(',')}" />`
        : '';

    // Escape </script> inside JS content so it doesn't break the HTML parser
    const safeJs = runtimeJs.replace(/<\/script>/gi, '<\\/script>');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swift Sites Export</title>
    ${iconFontLink}
    <style>${baseStyles}</style>
    <style>${tokensCss}</style>
    <style>${componentsCss}</style>
</head>
<body>
    <div id="svgSpriteRoot" hidden>${spriteSvg}</div>
    <div id="preview-content">${renderedHtml}</div>
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

    // Initialize component tree with selection handler
    initComponentTree(dom.componentTree, (componentId, path) => {
        // Sync tree selection with preview selection
        selectionManager.selectComponent(componentId);
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

            // Save to sessionStorage for persistence across tab refresh
            yamlStorage.save(yamlContent);

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

                // Extract icon names from YAML for optimized font loading
                const structure = getYamlStructureFromEditor();
                const iconNames = structure ? extractIconNames(structure) : [];
                const standaloneHtml = await buildStandaloneHtml(html, iconNames);

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
                yamlStorage.clear(); // Clear sessionStorage
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
                const iconNames = structure ? extractIconNames(structure) : [];
                const standaloneHtml = await buildStandaloneHtml(html, iconNames);
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

    // 6. Load persisted YAML from sessionStorage (survives tab refresh)
    const storedYaml = yamlStorage.load();
    if (storedYaml) {
        console.log('[Main] Restored YAML from sessionStorage');
        dom.editor.value = storedYaml;
        updateLineNumbers(dom.editor, dom.lineNumbers);
    }

    // 7. Initialize history with current editor content
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
