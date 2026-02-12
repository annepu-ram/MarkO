import { initializeEvents } from './events.js';
import { renderPreview } from './ssr_app.js';
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
        propertiesPanel: document.getElementById('propertiesPanel'),
        propertiesContent: document.getElementById('propertiesContent'),
        resizer: document.getElementById('resizer'),
        sidebar: document.querySelector('.sidebar'),
        sidebarResizer: document.getElementById('sidebarResizer'),
        sidebarNavItems: Array.from(document.querySelectorAll('.sidebar-nav-item')),
        sidebarPanels: Array.from(document.querySelectorAll('.sidebar-panel')),
        exportButton: document.getElementById('exportBtn'),
        clearButton: document.getElementById('clearBtn'),
        fullscreenButton: document.getElementById('fullscreenBtn'),
        closeFullscreenButton: document.getElementById('closeFullscreenBtn'), // May be null
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
        },
        // Handle preview clicks for component selection
        handlePreviewClick: (event) => {
            selectionManager.handlePreviewClick(event);
        },
        exportCode: () => alert('Export functionality not implemented in this version.'),
        clearCanvas: () => {
            if(dom.editor) {
                dom.editor.value = '';
                selectionManager.clearSelection();
                clearPropertiesPanel();
                clearTreeSelection();
                historyManager.clear();
                yamlStorage.clear(); // Clear sessionStorage
                renderPreview('').then(() => {
                    updateComponentTree();
                });
            }
        },
        openFullscreen: () => alert('Fullscreen functionality not implemented in this version.'),
        closeFullscreen: () => alert('Fullscreen functionality not implemented in this version.'),
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
