/** @jest-environment jsdom */
import { jest } from '@jest/globals';

jest.mock('../../core/state.js', () => ({
    getComponentTemplates: jest.fn(),
    getComponentSchemas: jest.fn(),
    getSchemaTokens: jest.fn(() => ({})),
}));

let renderPropertiesPanel;
let applyPropertiesForComponent;
let clearPropertiesPanel;
let getComponentTemplates;
let getComponentSchemas;

beforeAll(async () => {
    if (typeof window === 'undefined') {
        global.window = {};
    }
    if (!window.jsyaml) {
        window.jsyaml = require('js-yaml');
    }

    ({ renderPropertiesPanel, applyPropertiesForComponent, clearPropertiesPanel } = await import('../index.js'));
    ({ getComponentTemplates, getComponentSchemas } = await import('../../core/state.js'));
});

const createStructure = component => [{ name: 'page', properties: {}, components: [component] }];

describe('applyPropertiesForComponent', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="propertiesPanel"></div><div id="propertiesContent"></div>';
        getComponentTemplates.mockReset();
        getComponentSchemas.mockReset();
    });

    afterEach(() => {
        clearPropertiesPanel();
    });

    test('retains defaults in YAML and normalizes blank text to a space', () => {
        getComponentTemplates.mockReturnValue({
            heading: {
                text: 'Default heading',
                typography: { align: 'left', color: '#111827' },
            },
        });
        getComponentSchemas.mockReturnValue({
            heading: {
                groups: [
                    {
                        id: 'content',
                        label: 'Content',
                        fields: [
                            { path: 'text', type: 'text', label: 'Text' },
                        ],
                    },
                ],
            },
        });

        const structure = createStructure({ name: 'heading', properties: { text: 'Hello' } });
        const component = structure[0].components[0];

        renderPropertiesPanel(component, 'comp-1', [0, 'components', 0]);
        const input = document.querySelector('[data-field-path="text"]');
        expect(input).not.toBeNull();
        input.value = '';

        const result = applyPropertiesForComponent({
            componentId: 'comp-1',
            path: [0, 'components', 0],
            structure: JSON.parse(JSON.stringify(structure)),
        });

        expect(result).not.toBeNull();
        const updatedProps = result.updatedStructure[0].components[0].properties;
        expect(updatedProps.text).toBe(' ');
        expect(updatedProps.typography).toBeDefined();
        expect(updatedProps.typography.align).toBe('left');
        expect(updatedProps.typography.color).toBe('#111827');

        const cleanedProps = result.cleanedComponent.properties;
        expect(cleanedProps.text).toBe(' ');
        expect(cleanedProps.typography.align).toBe('left');
    });
});
