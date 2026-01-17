/** @jest-environment jsdom */

import { jest } from '@jest/globals';

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
    getSelection: jest.fn(() => null),
    getPathForComponent: jest.fn(),
    getComponentPathMap: jest.fn(() => new Map()),
    undo: jest.fn(),
    redo: jest.fn(),
    canUndo: jest.fn(() => false),
    canRedo: jest.fn(() => false),
}));

jest.mock('../../render/index.js', () => ({
    renderYamlStructure: jest.fn(() => ({ html: '' })),
    initializeAllComponents: jest.fn(),
    computeInlineStylesFromProperties: jest.fn(() => ''),
}));

jest.mock('../../properties/index.js', () => ({
    renderPropertiesPanel: jest.fn(),
    clearPropertiesPanel: jest.fn(),
    applyPropertiesForComponent: jest.fn(),
}));

jest.mock('../../component_interactions.js', () => ({
    componentInitializers: {},
}));

let createActions;
let state;
let yaml;
let properties;

const buildBaseDom = () => {
    const appContainer = document.createElement('div');
    const editor = document.createElement('textarea');
    const preview = document.createElement('div');
    const propertiesPanel = document.createElement('div');
    const propertiesContent = document.createElement('div');
    const fullscreenModal = document.createElement('div');
    const fullscreenContent = document.createElement('div');
    const helpPanel = document.createElement('div');

    const componentsNavBtn = document.createElement('button');
    componentsNavBtn.id = 'componentsNavBtn';
    componentsNavBtn.className = 'sidebar-nav-item active';
    componentsNavBtn.dataset.target = 'componentsPanel';
    componentsNavBtn.setAttribute('aria-selected', 'true');

    const propertiesNavBtn = document.createElement('button');
    propertiesNavBtn.id = 'propertiesNavBtn';
    propertiesNavBtn.className = 'sidebar-nav-item';
    propertiesNavBtn.dataset.target = 'propertiesPanel';
    propertiesNavBtn.setAttribute('aria-selected', 'false');

    const componentsPanel = document.createElement('div');
    componentsPanel.id = 'componentsPanel';
    componentsPanel.className = 'sidebar-panel active';
    componentsPanel.setAttribute('aria-hidden', 'false');

    const propsPanel = document.createElement('div');
    propsPanel.id = 'propertiesPanel';
    propsPanel.className = 'sidebar-panel';
    propsPanel.setAttribute('aria-hidden', 'true');

    return {
        appContainer,
        editor,
        preview,
        propertiesPanel: propsPanel,
        propertiesContent,
        fullscreenModal,
        fullscreenContent,
        helpPanel,
        sidebarNavItems: [componentsNavBtn, propertiesNavBtn],
        sidebarPanels: [componentsPanel, propsPanel],
        propertiesNavBtn,
        componentsNavBtn,
        componentsPanel,
        propsPanel,
    };
};

beforeAll(async () => {
    ({ createActions } = await import('../actions.js'));
    state = await import('../../core/state.js');
    yaml = await import('../../core/yaml.js');
    properties = await import('../../properties/index.js');
});

beforeEach(() => {
    jest.clearAllMocks();
    state.getSelection.mockReturnValue(null);
});

describe('preview click focuses properties tab', () => {
    test('focusPropertiesPanel switches to properties nav item when inactive', () => {
        const dom = buildBaseDom();
        const actions = createActions(dom);

        actions.focusPropertiesPanel();

        const [componentsNavBtn, propertiesNavBtn] = dom.sidebarNavItems;
        const [componentsPanel, propsPanel] = dom.sidebarPanels;

        expect(componentsNavBtn.classList.contains('active')).toBe(false);
        expect(componentsNavBtn.getAttribute('aria-selected')).toBe('false');
        expect(componentsPanel.classList.contains('active')).toBe(false);
        expect(componentsPanel.getAttribute('aria-hidden')).toBe('true');

        expect(propertiesNavBtn.classList.contains('active')).toBe(true);
        expect(propertiesNavBtn.getAttribute('aria-selected')).toBe('true');
        expect(propsPanel.classList.contains('active')).toBe(true);
        expect(propsPanel.getAttribute('aria-hidden')).toBe('false');
    });

    test('handlePreviewClick activates properties nav item after selecting component', () => {
        const dom = buildBaseDom();
        const actions = createActions(dom);

        const componentId = 'component-1';
        const componentPath = ['components', 0];
        const component = { name: 'heading', properties: {} };
        const structure = [{ name: 'page', properties: {}, components: [component] }];

        state.getPathForComponent.mockReturnValue(componentPath);
        state.getYamlStructure.mockReturnValue(structure);
        yaml.getComponentByPath.mockReturnValue(component);

        // Create the new chrome structure (zero wrappers)
        const heading = document.createElement('h2');
        heading.className = 'chrome-target';
        heading.dataset.componentId = componentId;
        heading.textContent = 'Test Heading';

        dom.preview.appendChild(heading);

        const event = { target: heading };

        actions.handlePreviewClick(event);

        const [, propertiesNavBtn] = dom.sidebarNavItems;
        const [, propsPanel] = dom.sidebarPanels;

        expect(properties.renderPropertiesPanel).toHaveBeenCalledWith(component, componentId, componentPath);
        expect(propertiesNavBtn.classList.contains('active')).toBe(true);
        expect(propertiesNavBtn.getAttribute('aria-selected')).toBe('true');
        expect(propsPanel.classList.contains('active')).toBe(true);
        expect(propsPanel.getAttribute('aria-hidden')).toBe('false');
    });
});
