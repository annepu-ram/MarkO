import { parseYamlContent, generateYamlFromStructure, getComponentByPath, deleteComponentByPath } from '../core/yaml.js';
import { getComponentTemplates, setYamlStructure, getYamlStructure, pushHistory, setSelection, getSelection, getPathForComponent, getComponentPathMap, undo, redo, canUndo, canRedo } from '../core/state.js';
import { renderYamlStructure, initializeAllComponents, computeInlineStylesFromProperties } from '../render/index.js';
import { componentInitializers } from '../component_interactions.js';
import { renderPropertiesPanel, clearPropertiesPanel, applyPropertiesForComponent } from '../properties/index.js';
import { deepClone } from '../utils/object.js';

const DEFAULT_PARSE_OPTIONS = { pushHistory: true };

function arraysEqual(a, b) {
    if (!Array.isArray(a) || !Array.isArray(b)) {
        return false;
    }
    if (a.length !== b.length) {
        return false;
    }
    for (let index = 0; index < a.length; index += 1) {
        if (a[index] !== b[index]) {
            return false;
        }
    }
    return true;
}

export function createActions(dom) {
    const {
        appContainer,
        editor,
        preview,
        propertiesPanel,
        propertiesContent,
        fullscreenModal,
        fullscreenContent,
        helpPanel,
        sidebarNavItems,
        sidebarPanels,
        propertiesNavBtn,
    } = dom;

    const childComponentContainers = new Set(['layout-row', 'layout-column', 'section', 'stack', 'form', 'image']);

    const findComponentIdByPath = path => {
        const map = getComponentPathMap();
        for (const [componentId, storedPath] of map.entries()) {
            if (arraysEqual(storedPath, path)) {
                return componentId;
            }
        }
        return null;
    };

    const clearHighlights = () => {
        if (!preview) {
            return;
        }
        preview.querySelectorAll('.chrome-target.selected, .chrome-target-page.selected').forEach(node => {
            node.classList.remove('selected');
            const deleteBtn = node.querySelector('.chrome-delete');
            if(deleteBtn) deleteBtn.setAttribute('tabindex', '-1');
        });
    };

    const highlightElement = element => {
        if (!element) {
            return;
        }
        element.classList.add('selected');
        const deleteBtn = element.querySelector('.chrome-delete');
        if(deleteBtn) deleteBtn.setAttribute('tabindex', '0');
    };

    const refreshSelection = () => {
        const selection = getSelection();
        if (!selection || !selection.path) {
            clearHighlights();
            clearPropertiesPanel();
            return;
        }

        const componentId = findComponentIdByPath(selection.path);
        if (!componentId) {
            setSelection();
            clearHighlights();
            clearPropertiesPanel();
            return;
        }

        const element = preview.querySelector(`.chrome-target[data-component-id="${componentId}"], .chrome-target-page[data-component-id="${componentId}"]`);
        if (!element) {
            setSelection();
            clearHighlights();
            clearPropertiesPanel();
            return;
        }

        clearHighlights();
        highlightElement(element);

        const structure = getYamlStructure();
        const component = getComponentByPath(structure, selection.path);
        if (component) {
            setSelection({ componentId, path: selection.path });
            renderPropertiesPanel(component, componentId, selection.path);
        } else {
            clearPropertiesPanel();
        }
    };

    const parseAndRender = (yamlText, options = DEFAULT_PARSE_OPTIONS) => {
        const shouldPush = options.pushHistory !== undefined ? options.pushHistory : DEFAULT_PARSE_OPTIONS.pushHistory;
        if (shouldPush) {
            pushHistory(yamlText);
        }

        const structure = parseYamlContent(yamlText);
        if (!structure) {
            preview.innerHTML = '<div class="preview-error">Unable to parse YAML. Check the console for details.</div>';
            setYamlStructure(null);
            clearPropertiesPanel();
            return;
        }

        setYamlStructure(structure);
        const { html } = renderYamlStructure(structure, 'preview');
        preview.innerHTML = html;
        initializeAllComponents(componentInitializers);
        refreshSelection();
    };

    const handleEditorInput = value => {
        parseAndRender(value, { pushHistory: true });
    };

    /**
     * Activates a specific sidebar panel by its ID
     * @param {string} panelId - The ID of the panel to activate (e.g., 'propertiesPanel', 'componentsPanel')
     */
    const activateSidebarPanel = panelId => {
        // Validate that we have the necessary DOM elements
        if (!Array.isArray(sidebarNavItems) || !Array.isArray(sidebarPanels) ||
            sidebarNavItems.length === 0 || sidebarPanels.length === 0) {
            return;
        }

        // Check if the target panel is already active
        const isAlreadyActive = sidebarPanels.some(
            panel => panel.id === panelId && panel.classList.contains('active')
        );

        if (isAlreadyActive) {
            return;
        }

        // Update all navigation items: activate the one targeting this panel, deactivate others
        sidebarNavItems.forEach(navItem => {
            const shouldActivate = navItem.dataset.target === panelId;
            navItem.classList.toggle('active', shouldActivate);
            navItem.setAttribute('aria-selected', shouldActivate ? 'true' : 'false');
        });

        // Update all panels: show the target panel, hide others
        sidebarPanels.forEach(panel => {
            const shouldShow = panel.id === panelId;
            panel.classList.toggle('active', shouldShow);
            panel.setAttribute('aria-hidden', shouldShow ? 'false' : 'true');
        });
    };

    /**
     * Switches to the properties panel in the sidebar
     */
    const focusPropertiesPanel = () => {
        activateSidebarPanel('propertiesPanel');
    };

    const handlePreviewClick = event => {
        const deleteButton = event.target.closest('.chrome-delete');
        if (deleteButton) {
            event.stopPropagation();
            deleteComponentById(deleteButton.dataset.componentId);
            return;
        }

        // Find the component (chrome-target or chrome-target-page for page component)
        const target = event.target.closest('.chrome-target, .chrome-target-page');
        clearHighlights();
        if (!target) {
            setSelection();
            clearPropertiesPanel();
            return;
        }

        const componentId = target.dataset.componentId;
        const path = getPathForComponent(componentId);
        if (!path) {
            setSelection();
            clearPropertiesPanel();
            return;
        }

        setSelection({ componentId, path });
        highlightElement(target);
        const structure = getYamlStructure();
        const component = getComponentByPath(structure, path);
        if (component) {
            renderPropertiesPanel(component, componentId, path);
            focusPropertiesPanel();
        }
    };

    const deleteComponentById = componentId => {
        const path = getPathForComponent(componentId);
        if (!path) {
            return;
        }

        // GUARD: Prevent deleting page component (root at path [0])
        if (path.length === 1 && path[0] === 0) {
            console.warn('Cannot delete page component - it is the mandatory root container');
            return;
        }

        const structure = getYamlStructure();
        if (!structure) {
            return;
        }
        const updatedStructure = deleteComponentByPath(structure, path);
        setYamlStructure(updatedStructure);
        const yamlText = generateYamlFromStructure(updatedStructure);
        editor.value = yamlText;
        parseAndRender(yamlText, { pushHistory: true });
        setSelection();
        clearPropertiesPanel();
    };

    const insertComponent = componentName => {
        const templates = getComponentTemplates();
        if (!templates) {
            console.warn('Component templates not loaded yet.');
            return;
        }
        const template = deepClone(templates[componentName]);
        let newComponent;

        if (componentName === 'page') {
            newComponent = {
                name: 'page',
                properties: template || {},
                components: [],
            };
            const yamlText = generateYamlFromStructure([newComponent]);
            editor.value = yamlText;
            parseAndRender(yamlText, { pushHistory: true });
            editor.focus();
            return;
        }

        if (componentName === 'tabs') {
            newComponent = {
                name: 'tabs',
                properties: template || {},
                tabs: [{ title: 'Tab one', components: [] }],
            };
        } else if (componentName === 'carousel') {
            const { slides = [], ...properties } = template || {};
            newComponent = {
                name: 'carousel',
                properties,
                slides,
            };
        } else if (componentName === 'accordion') {
            newComponent = {
                name: 'accordion',
                properties: template || {},
            };
        } else {
            newComponent = {
                name: componentName,
                properties: template || {},
            };
        }

        if (childComponentContainers.has(componentName)) {
            newComponent.components = Array.isArray(newComponent.components) ? newComponent.components : [];
        }

        let structure = parseYamlContent(editor.value);
        if (!structure || !Array.isArray(structure) || structure.length !== 1 || structure[0].name !== 'page') {
            structure = [{ name: 'page', properties: {}, components: [newComponent] }];
        } else {
            if (!Array.isArray(structure[0].components)) {
                structure[0].components = [];
            }
            structure[0].components.push(newComponent);
        }

        const yamlText = generateYamlFromStructure(structure);
        editor.value = yamlText;
        parseAndRender(yamlText, { pushHistory: true });
        editor.focus();
    };

    const applySelectedComponentProperties = () => {
        const selection = getSelection();
        if (!selection || !selection.componentId || !selection.path) {
            return;
        }
        const structure = getYamlStructure();
        if (!structure) {
            return;
        }
        const result = applyPropertiesForComponent({
            componentId: selection.componentId,
            path: selection.path,
            structure: deepClone(structure),
        });
        if (!result || !result.updatedStructure) {
            return;
        }
        setYamlStructure(result.updatedStructure);

        const updatedYaml = generateYamlFromStructure(result.updatedStructure);
        editor.value = updatedYaml;

        parseAndRender(updatedYaml, { pushHistory: true });
        const nextPath = result.nextSelectionPath || selection.path;
        setSelection({ path: nextPath });
        refreshSelection();
    };

    const generateCleanHTML = yamlText => {
        const structure = parseYamlContent(yamlText);
        if (!structure) {
            return '';
        }
        const { html } = renderYamlStructure(structure, 'export');
        return html;
    };

    const generateTitlebarBehaviorScript = () => `
<script>
(function() {
    const SCROLL_OFFSET = 50;
    function applyScrollState() {
        const scrolled = window.scrollY > SCROLL_OFFSET;
        document.querySelectorAll('.titlebar').forEach(nav => {
            nav.classList.toggle('scrolled', scrolled);
        });
    }
    function bindInteractions(nav) {
        const button = nav.querySelector('.mobile-menu-button');
        const links = nav.querySelector('.titlebar-nav');
        if (button && links) {
            button.addEventListener('click', () => {
                links.classList.toggle('active');
            });
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        const navbars = document.querySelectorAll('.titlebar');
        navbars.forEach(bindInteractions);
        applyScrollState();
        window.addEventListener('scroll', applyScrollState, { passive: true });
    });
})();
</script>`;

    const exportCode = () => {
        const yamlText = editor.value;
        const structure = parseYamlContent(yamlText);
        const pageProperties = structure && structure[0] && structure[0].name === 'page' ? structure[0].properties || {} : {};
        const { html } = renderYamlStructure(structure || [], 'export');
        const bodyStyles = computeInlineStylesFromProperties(pageProperties || {});
        const documentHtml = `<!DOCTYPE html>
<html lang="en" style="height: 100%;">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Website</title>
    
    <style>
        html { font-size: 10px; }
        body { font-size: 1.6rem; height: 100%; margin: 0; }
    </style>
</head>
<body style="${bodyStyles}">
    ${html}
    ${generateTitlebarBehaviorScript()}
</body>
</html>`;
        const blob = new Blob([documentHtml], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'generated-website.html';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };


    const openFullscreen = () => {
        if (!fullscreenContent || !fullscreenModal) {
            return;
        }
        const yamlText = editor.value;
        const cleanHTML = generateCleanHTML(yamlText);
        fullscreenContent.innerHTML = `<div class="preview-area fullscreen-preview">${cleanHTML}</div>`;
        fullscreenContent.scrollTop = 0;
        fullscreenModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    };
    const closeFullscreen = () => {
        if (fullscreenModal) {
            fullscreenModal.style.display = 'none';
        }
        if (fullscreenContent) {
            fullscreenContent.innerHTML = '';
            fullscreenContent.scrollTop = 0;
        }
        document.body.style.overflow = 'auto';
    };

    const clearCanvas = () => {
        // Get default page properties from templates
        const templates = getComponentTemplates();
        const pageDefaults = templates?.page || {};

        const defaultPageStructure = [{
            name: 'page',
            properties: pageDefaults,
            components: []
        }];

        const defaultPageYaml = generateYamlFromStructure(defaultPageStructure);

        editor.value = defaultPageYaml;
        setYamlStructure(null);
        parseAndRender(defaultPageYaml, { pushHistory: true });
        clearPropertiesPanel();
    };

    const toggleHelpPanel = () => {
        if (!helpPanel) {
            return;
        }
        const isVisible = appContainer && appContainer.classList.contains('help-visible');
        const nextState = !isVisible;
        if (appContainer) {
            appContainer.classList.toggle('help-visible', nextState);
        }
        helpPanel.style.display = nextState ? 'block' : 'none';
    };

    const undoAction = () => {
        if (!canUndo()) {
            return;
        }
        const previous = undo();
        if (previous !== null) {
            editor.value = previous;
            parseAndRender(previous, { pushHistory: false });
        }
    };

    const redoAction = () => {
        if (!canRedo()) {
            return;
        }
        const next = redo();
        if (next !== null) {
            editor.value = next;
            parseAndRender(next, { pushHistory: false });
        }
    };

    const logHtml = () => {
        console.log(generateCleanHTML(editor.value));
    };

    return {
        parseAndRender,
        handleEditorInput,
        handlePreviewClick,
        focusPropertiesPanel,
        deleteComponent: deleteComponentById,
        insertComponent,
        applySelectedComponentProperties,
        exportCode,
        openFullscreen,
        closeFullscreen,
        clearCanvas,
        toggleHelpPanel,
        undo: undoAction,
        redo: redoAction,
        logHtml,
        refreshSelection,
    };
}

