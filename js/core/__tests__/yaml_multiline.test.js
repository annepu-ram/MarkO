/** @jest-environment jsdom */
let parseYamlContent;
let generateYamlFromStructure;

describe('YAML multiline serialization', () => {
    beforeAll(async () => {
        if (typeof window === 'undefined') {
            global.window = {};
        }
        window.jsyaml = require('js-yaml');
        ({ parseYamlContent, generateYamlFromStructure } = await import('../yaml.js'));
    });

    test('roundtrips multiline text values without loss', () => {
        const originalStructure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'paragraph',
                        properties: {
                            text: 'Line one\nLine two\nLine three',
                        },
                    },
                ],
            },
        ];

        const yamlText = generateYamlFromStructure(originalStructure);
        expect(typeof yamlText).toBe('string');
        expect(yamlText).toMatch(/text: \|?-\n\s{8,10}Line one/);
        const parsed = parseYamlContent(yamlText);
        expect(parsed).not.toBeNull();
        const parsedText = parsed?.[0]?.components?.[0]?.properties?.text;
        expect(parsedText).toBe('Line one\nLine two\nLine three');
    });
});
