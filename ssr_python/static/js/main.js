import { initializeEvents } from './events.js';
import { renderPreview } from './ssr_app.js';
import { SelectionManager } from './selectionManager.js';
import { loadMetadata } from './metadataLoader.js';
import { renderPropertiesPanel, clearPropertiesPanel, collectPropertyValues, getActiveComponentInfo } from './propertiesPanel.js';
import { getYamlStructureFromEditor, getComponentByPath, updateComponentByPath, generateYamlFromStructure, updateYamlEditor } from './yamlUtils.js';

// Create singleton selection manager instance
export const selectionManager = new SelectionManager();

// 1. Get all DOM references, same as the original app
function getDomReferences() {
    const appContainer = document.getElementById('appContainer');
    return {
        appContainer,
        editor: document.getElementById('codeEditor'),
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
    };
}

// 2. Initialize the app on DOMContentLoaded
document.addEventListener('DOMContentLoaded', async () => {
    const dom = getDomReferences();

    // Load metadata first
    await loadMetadata();

    // Set up selection change handler to update properties panel
    selectionManager.onSelectionChange = (selection) => {
        if (!selection) {
            clearPropertiesPanel();
            return;
        }

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
        handleEditorInput: (yamlContent) => {
            // Store current selection before re-render
            const currentSelection = selectionManager.getSelection();
            renderPreview(yamlContent).then(() => {
                // Restore selection after re-render if it existed
                if (currentSelection.componentId) {
                    selectionManager.restoreSelection();
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
                renderPreview('');
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
            const updatedProperties = collectPropertyValues();
            if (!updatedProperties) {
                console.warn('Failed to collect property values');
                return;
            }

            // Create updated component
            const updatedComponent = {
                ...currentComponent,
                properties: updatedProperties
            };

            // Update YAML structure
            const updatedStructure = updateComponentByPath(yamlStructure, activeInfo.path, updatedComponent);

            // Generate YAML string
            const yamlText = generateYamlFromStructure(updatedStructure);
            if (!yamlText) {
                console.error('Failed to generate YAML');
                return;
            }

            // Update editor
            updateYamlEditor(yamlText);

            // Store selection for restoration
            const selectionToRestore = {
                componentId: activeInfo.componentId,
                path: activeInfo.path
            };

            // Re-render preview
            await renderPreview(yamlText, updatedStructure);

            // Restore selection after re-render
            setTimeout(() => {
                selectionManager.selectComponent(selectionToRestore.componentId);
                // Restore properties panel
                const restoredComponent = getComponentByPath(updatedStructure, selectionToRestore.path);
                if (restoredComponent) {
                    renderPropertiesPanel(restoredComponent, selectionToRestore.componentId, selectionToRestore.path);
                }
            }, 100);
        },
        undo: () => console.log('Undo not implemented.'),
        redo: () => console.log('Redo not implemented.'),
    };

    // 4. Initialize all UI events using the original, robust function
    initializeEvents(dom, actions);

    // 5. Perform an initial render in case there's content in the editor
    if (dom.editor.value) {
        renderPreview(dom.editor.value);
    }
});
