import { renderYamlStructure } from '../index.js';
import { resetComponentPathMap, getComponentPathMap } from '../../core/state.js';

describe('renderYamlStructure component path map behaviour', () => {
    beforeEach(() => {
        resetComponentPathMap();
    });

    afterEach(() => {
        resetComponentPathMap();
    });

    test('export mode does not clear preview component path map', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'heading',
                        properties: {
                            text: 'Sample Heading',
                        },
                    },
                ],
            },
        ];

        renderYamlStructure(structure, 'preview');
        const previewMap = getComponentPathMap();

        expect(previewMap.size).toBeGreaterThan(0);

        renderYamlStructure(structure, 'export');
        const afterExportMap = getComponentPathMap();

        expect(afterExportMap.size).toBe(previewMap.size);
    });
});
