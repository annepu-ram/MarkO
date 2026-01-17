/**
 * @jest-environment jsdom
 */
import { createActions } from '../actions.js';
import { getComponentPathMap, setYamlStructure, getYamlStructure, setSelection, getSelection, getPathForComponent } from '../../core/state.js';
import { deleteComponentByPath, getComponentByPath } from '../../core/yaml.js';
import { initializeEvents } from '../events.js';

jest.mock('../../core/yaml.js', () => ({
    parseYamlContent: jest.fn(),
    generateYamlFromStructure: jest.fn(),
    getComponentByPath: jest.fn(),
    deleteComponentByPath: jest.fn(),
}));

jest.mock('../../core/state.js', () => ({
    getComponentTemplates: jest.fn(),
    setYamlStructure: jest.fn(),
    getYamlStructure: jest.fn(),
    pushHistory: jest.fn(),
    setSelection: jest.fn(),
    getSelection: jest.fn(),
    getPathForComponent: jest.fn(),
    getComponentPathMap: jest.fn(),
    undo: jest.fn(),
    redo: jest.fn(),
    canUndo: jest.fn(),
    canRedo: jest.fn(),
}));

jest.mock('../../render/index.js', () => ({
    renderYamlStructure: jest.fn(),
    initializeAllComponents: jest.fn(),
    computeInlineStylesFromProperties: jest.fn(),
}));

jest.mock('../../properties/index.js', () => ({
    renderPropertiesPanel: jest.fn(),
    clearPropertiesPanel: jest.fn(),
    applyPropertiesForComponent: jest.fn(),
}));

describe('Overlay interaction', () => {
    let dom;
    let actions;

    beforeEach(() => {
        document.body.innerHTML = `
            <div id="app-container">
                <textarea id="editor"></textarea>
                <div id="preview"></div>
                <div id="properties-panel"></div>
                <div class="sidebar-tab" data-target="propertiesPanel"></div>
            </div>
        `;
        dom = {
            appContainer: document.getElementById('app-container'),
            editor: document.getElementById('editor'),
            preview: document.getElementById('preview'),
            propertiesPanel: document.getElementById('properties-panel'),
            sidebarTabs: [document.querySelector('.sidebar-tab')],
            sidebarPanels: [document.getElementById('properties-panel')],
            propertiesTab: document.querySelector('.sidebar-tab'),
        };
        actions = createActions(dom);
        initializeEvents(dom, actions);
    });

    test('clicking on a component should select it', () => {
        const componentId = 'comp_123';
        const path = [0, 0];
        dom.preview.innerHTML = `
            <p class="chrome-target" data-component-id="${componentId}" style="position: relative;">
                <span class="chrome-label">paragraph</span>
                <button class="chrome-delete" data-component-id="${componentId}">×</button>
                Hello
            </p>
        `;
        const p = dom.preview.querySelector('p');

        getPathForComponent.mockReturnValue(path);
        getComponentByPath.mockReturnValue({ name: 'paragraph', properties: { text: 'Hello' } });
        getYamlStructure.mockReturnValue({ components: [{ name: 'paragraph', properties: { text: 'Hello' } }] });

        const event = new MouseEvent('click', { bubbles: true });
        p.dispatchEvent(event);

        expect(setSelection).toHaveBeenCalledWith({ componentId, path });
    });

    test('clicking on the delete button should delete the component', () => {
        const componentId = 'comp_123';
        const path = [0, 0];
        dom.preview.innerHTML = `
            <p class="chrome-target" data-component-id="${componentId}" style="position: relative;">
                <span class="chrome-label">paragraph</span>
                <button class="chrome-delete" data-component-id="${componentId}">×</button>
                Hello
            </p>
        `;
        const deleteButton = dom.preview.querySelector('.chrome-delete');

        getPathForComponent.mockReturnValue(path);
        getYamlStructure.mockReturnValue({ components: [{ name: 'paragraph', properties: { text: 'Hello' } }] });
        deleteComponentByPath.mockReturnValue({ components: [] });

        const event = new MouseEvent('click', { bubbles: true });
        deleteButton.dispatchEvent(event);

        expect(getPathForComponent).toHaveBeenCalledWith(componentId);
        expect(deleteComponentByPath).toHaveBeenCalled();
    });

    test('clicking on page component (chrome-target-page) should select it', () => {
        const componentId = 'page_123';
        const path = [0];
        dom.preview.innerHTML = `
            <div class="chrome-target-page" data-component-id="${componentId}" style="position: relative;">
                <p class="chrome-target" data-component-id="comp_456">Child component</p>
            </div>
        `;
        const pageElement = dom.preview.querySelector('.chrome-target-page');

        getPathForComponent.mockReturnValue(path);
        getComponentByPath.mockReturnValue({ name: 'page', properties: {}, components: [] });
        getYamlStructure.mockReturnValue([{ name: 'page', properties: {}, components: [] }]);

        const event = new MouseEvent('click', { bubbles: true });
        pageElement.dispatchEvent(event);

        expect(setSelection).toHaveBeenCalledWith({ componentId, path });
    });
});