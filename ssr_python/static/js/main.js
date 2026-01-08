import { initializeEvents } from './events.js';
import { renderPreview } from './ssr_app.js';
import { SelectionManager } from './selectionManager.js';
import { loadMetadata, getComponentDefaults } from './metadataLoader.js';
import { renderPropertiesPanel, clearPropertiesPanel, collectPropertyValues, getActiveComponentInfo } from './propertiesPanel.js';
import { getYamlStructureFromEditor, getComponentByPath, updateComponentByPath, generateYamlFromStructure, updateYamlEditor } from './yamlUtils.js';
import { historyManager } from './historyManager.js';
import { loadSvgSprite } from './sprite.js';
import { deepMerge } from './utils/object.js';
import { initComponentTree, buildTreeFromStructure, renderTree, highlightTreeItem, clearTreeSelection } from './componentTree.js';

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

    // Load SVG sprite first
    const spritePath = window.SPRITE_PATH || '/static/icon-sprite.svg';
    await loadSvgSprite({ spritePath });

    // Load metadata
    await loadMetadata();

    // Function to update component tree
    const updateComponentTree = () => {
        if (!dom.componentTree) return;
        const yamlStructure = getYamlStructureFromEditor();
        if (yamlStructure && yamlStructure.length > 0) {
            const treeData = buildTreeFromStructure(yamlStructure);
            renderTree(treeData, dom.componentTree);
        } else {
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
        if (!selection) {
            clearPropertiesPanel();
            clearTreeSelection();
            return;
        }

        // Highlight tree item
        highlightTreeItem(selection.componentId);

        // Get component from YAML structure
        const yamlStructure = getYamlStructureFromEditor();
        const component = getComponentByPath(yamlStructure, selection.path);

        if (component) {
            renderPropertiesPanel(component, selection.componentId, selection.path);
        } else {
            clearPropertiesPanel();
        }
    };

    // 3. Create a simplified 'actions' object for the SSR app
    const actions = {
        // The most important action: handle editor input by calling the SSR render function
        handleEditorInput: (yamlContent, options = { pushHistory: true }) => {
            // Push to history if not disabled (e.g., during undo/redo)
            if (options.pushHistory) {
                historyManager.push(yamlContent);
            }

            // Store current selection before re-render
            const currentSelection = selectionManager.getSelection();
            renderPreview(yamlContent).then(() => {
                // Update component tree
                updateComponentTree();
                
                // Restore selection after re-render if it existed
                if (currentSelection.componentId) {
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

            // Get current YAML structure
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

            // Create updated component with both component-level and properties updates
            // Use deepMerge for properties to preserve unchanged values
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:196',message:'applySelectedComponentProperties before merge',data:{currentProps:JSON.stringify(currentComponent.properties),collectedProps:JSON.stringify(collectedValues.properties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            // Merge defaults first to ensure we have the full structure, then merge collected values
            // Note: getComponentDefaults returns the properties object directly (not wrapped in a 'properties' key)
            const defaults = getComponentDefaults(currentComponent.name);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:201',message:'before first merge',data:{componentName:currentComponent.name,defaults:JSON.stringify(defaults),currentProps:JSON.stringify(currentComponent.properties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            // Start with defaults, then merge current properties on top (so current overrides defaults)
            const baseProperties = deepMerge({}, defaults || {}, currentComponent.properties || {});
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:205',message:'after first merge',data:{baseProps:JSON.stringify(baseProperties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            // Merge collected values into baseProperties (preserves defaults that aren't being changed)
            const finalProperties = deepMerge({}, baseProperties, collectedValues.properties);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:204',message:'applySelectedComponentProperties after merge',data:{updatedProps:JSON.stringify(finalProperties)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            const updatedComponent = {
                ...currentComponent,
                ...collectedValues.component,  // Apply component-level updates (tabs, items, etc.)
                properties: finalProperties
            };

            // Update YAML structure
            const updatedStructure = updateComponentByPath(yamlStructure, activeInfo.path, updatedComponent);

            // Generate YAML string
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:217',message:'before generateYamlFromStructure',data:{updatedComponentProps:JSON.stringify(updatedComponent.properties),updatedStructure:JSON.stringify(updatedStructure)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
            // #endregion
            const yamlText = generateYamlFromStructure(updatedStructure);
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:232',message:'after generateYamlFromStructure',data:{yamlTextLength:yamlText.length,yamlPreview:yamlText.substring(0,500)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
            // #endregion
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:220',message:'after generateYamlFromStructure',data:{yamlText:yamlText.substring(0,500)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
            // #endregion
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

    // 6. Initialize history with current editor content
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
