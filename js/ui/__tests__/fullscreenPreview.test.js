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
    resetComponentPathMap: jest.fn(),
    queueComponentInitialization: jest.fn(),
    consumeComponentInitializationQueue: jest.fn(() => []),
    undo: jest.fn(),
    redo: jest.fn(),
    canUndo: jest.fn(() => false),
    canRedo: jest.fn(() => false),
}));

jest.mock('../../render/index.js', () => ({
    renderYamlStructure: jest.fn(() => ({ html: '<div class="mock-export">Ready</div>' })),
    initializeAllComponents: jest.fn(),
    computeInlineStylesFromProperties: jest.fn(() => ''),
}));

jest.mock('../../properties/index.js', () => ({
    renderPropertiesPanel: jest.fn(),
    clearPropertiesPanel: jest.fn(),
    applyPropertiesForComponent: jest.fn(() => null),
}));

jest.mock('../../component_interactions.js', () => ({
    componentInitializers: {},
}));

let createActions;
let yaml;

const buildDom = () => {
    const appContainer = document.createElement('div');
    const editor = document.createElement('textarea');
    const preview = document.createElement('div');
    const propertiesPanel = document.createElement('div');
    const propertiesContent = document.createElement('div');
    const fullscreenModal = document.createElement('div');
    const fullscreenContent = document.createElement('div');
    const helpPanel = document.createElement('div');

    return {
        appContainer,
        editor,
        preview,
        propertiesPanel,
        propertiesContent,
        fullscreenModal,
        fullscreenContent,
        helpPanel,
        sidebarTabs: [],
        sidebarPanels: [],
        propertiesTab: null,
    };
};

beforeAll(async () => {
    ({ createActions } = await import('../actions.js'));
    yaml = await import('../../core/yaml.js');
});

beforeEach(() => {
    jest.clearAllMocks();
    yaml.parseYamlContent.mockReturnValue([{ name: 'page', properties: {}, components: [] }]);
});

describe('fullscreen preview rendering', () => {
    test('openFullscreen wraps export markup in preview container', () => {
        const dom = buildDom();
        dom.editor.value = 'page: {}';
        dom.fullscreenContent.scrollTop = 42;

        const actions = createActions(dom);

        actions.openFullscreen();

        expect(dom.fullscreenContent.innerHTML).toBe('<div class="preview-area fullscreen-preview"><div class="mock-export">Ready</div></div>');
        expect(dom.fullscreenContent.scrollTop).toBe(0);
        expect(dom.fullscreenModal.style.display).toBe('block');
        expect(document.body.style.overflow).toBe('hidden');
    });

    test('closeFullscreen clears modal content and restores body overflow', () => {
        const dom = buildDom();
        const actions = createActions(dom);
        dom.fullscreenModal.style.display = 'block';
        dom.fullscreenContent.innerHTML = '<div>stale</div>';
        dom.fullscreenContent.scrollTop = 80;
        document.body.style.overflow = 'hidden';

        actions.closeFullscreen();

        expect(dom.fullscreenModal.style.display).toBe('none');
        expect(dom.fullscreenContent.innerHTML).toBe('');
        expect(dom.fullscreenContent.scrollTop).toBe(0);
        expect(document.body.style.overflow).toBe('auto');
    });
});
