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
    } = dom;

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
        preview.querySelectorAll('.rendered-component').forEach(node => {
            node.style.border = '1px solid #404A6B';
        });
    };

    const highlightElement = element => {
        if (element) {
            element.style.border = '2px solid #ef4444';
        }
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

        const element = preview.querySelector(`[data-component-id="${componentId}"]`);
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

    const handlePreviewClick = event => {
        const deleteButton = event.target.closest('.delete-component-btn');
        if (deleteButton) {
            event.stopPropagation();
            deleteComponentById(deleteButton.dataset.componentId);
            return;
        }

        const wrapper = event.target.closest('.rendered-component');
        clearHighlights();
        if (!wrapper) {
            setSelection();
            clearPropertiesPanel();
            return;
        }

        const componentId = wrapper.dataset.componentId;
        const path = getPathForComponent(componentId);
        if (!path) {
            setSelection();
            clearPropertiesPanel();
            return;
        }

        setSelection({ componentId, path });
        highlightElement(wrapper);
        const structure = getYamlStructure();
        const component = getComponentByPath(structure, path);
        if (component) {
            renderPropertiesPanel(component, componentId, path);
        }
    };

    const deleteComponentById = componentId => {
        const path = getPathForComponent(componentId);
        if (!path) {
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
                tabs: [{ title: 'Tab Name', components: [] }],
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
                content: { components: [] },
            };
        } else if (componentName === 'form' || componentName === 'image') {
            newComponent = {
                name: componentName,
                properties: template || {},
                components: [],
            };
        } else {
            newComponent = {
                name: componentName,
                properties: template || {},
            };
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

        // Generate YAML for the editor using the cleaned component
        // We need to reconstruct the full YAML structure with the cleaned component
        const tempStructureForEditor = deepClone(structure);
        let cursor = tempStructureForEditor;
        for (let i = 0; i < selection.path.length - 1; i++) {
            cursor = cursor[selection.path[i]];
        }
        cursor[selection.path[selection.path.length - 1]] = result.cleanedComponent;

        const yamlTextForEditor = generateYamlFromStructure(tempStructureForEditor);
        editor.value = yamlTextForEditor;

        // Re-render the preview using the full, uncleaned updatedStructure
        parseAndRender(generateYamlFromStructure(result.updatedStructure), { pushHistory: true });
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
        const yamlText = editor.value;
        const cleanHTML = generateCleanHTML(yamlText);
        fullscreenContent.innerHTML = cleanHTML;
        fullscreenModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    };

    const closeFullscreen = () => {
        fullscreenModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    const clearCanvas = () => {
        editor.value = '';
        setYamlStructure(null);
        parseAndRender('', { pushHistory: true });
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
