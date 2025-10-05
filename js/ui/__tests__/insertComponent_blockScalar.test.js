/** @jest-environment jsdom */

import { jest } from '@jest/globals';

jest.mock('../../core/state.js', () => {
    return {
        getComponentTemplates: jest.fn(),
        setYamlStructure: jest.fn(),
        getYamlStructure: jest.fn(() => null),
        pushHistory: jest.fn(),
        setSelection: jest.fn(),
        getSelection: jest.fn(() => null),
        getPathForComponent: jest.fn(),
        getComponentPathMap: jest.fn(() => new Map()),
        undo: jest.fn(),
        redo: jest.fn(),
        canUndo: jest.fn(() => false),
        canRedo: jest.fn(() => false),
    };
});

jest.mock('../../render/index.js', () => ({
    renderYamlStructure: jest.fn(() => ({ html: '<div></div>' })),
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
let state;

describe('insertComponent multiline defaults', () => {
    beforeAll(async () => {
        if (typeof window === 'undefined') {
            global.window = {};
        }
        window.jsyaml = require('js-yaml');
        state = await import('../../core/state.js');
        ({ createActions } = await import('../actions.js'));
    });

    beforeEach(() => {
        jest.clearAllMocks();
    });

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
        };
    };

    test('inserting a paragraph component emits block-scalar YAML', () => {
        const templates = {
            paragraph: {
                text: 'Line one\nLine two',
            },
        };
        state.getComponentTemplates.mockReturnValue(templates);

        const dom = buildDom();
        const actions = createActions(dom);

        actions.insertComponent('paragraph');

        const { editor } = dom;
        const yamlText = editor.value;

        expect(state.pushHistory).toHaveBeenCalled();
        expect(state.setYamlStructure).toHaveBeenCalledWith(expect.any(Array));
        expect(yamlText).toContain('text: |');
        expect(yamlText).toMatch(/text: \|[-+]?\s*\n\s+Line one\n\s+Line two/);
        expect(yamlText).toMatch(/- name: paragraph/);
    });
});
