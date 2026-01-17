import { renderYamlStructure } from '../index.js';
import { resetComponentPathMap } from '../../core/state.js';

describe('ColumnsGrid Rendering', () => {
    beforeEach(() => {
        resetComponentPathMap();
    });

    test('renders 3-column grid with correct widths', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 3,
                                gap: 'md'
                            }
                        },
                        columns: [
                            { components: [{ name: 'heading', properties: { text: 'Col 1', level: 3 } }] },
                            { components: [{ name: 'heading', properties: { text: 'Col 2', level: 3 } }] },
                            { components: [{ name: 'heading', properties: { text: 'Col 3', level: 3 } }] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should have 3 columns with calc() width accounting for gaps
        expect(html).toContain('calc((100% - (');
        expect(html).toContain('* 2)) / 3)'); // 3 columns means 2 gaps

        // Should include all three headings
        expect(html).toContain('Col 1');
        expect(html).toContain('Col 2');
        expect(html).toContain('Col 3');

        // Should apply gap spacing
        expect(html).toContain('gap:');
    });

    test('renders 2-column grid with correct widths', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 2,
                                gap: 'lg'
                            }
                        },
                        columns: [
                            { components: [{ name: 'paragraph', properties: { text: 'Left column' } }] },
                            { components: [{ name: 'paragraph', properties: { text: 'Right column' } }] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should have 2 columns with calc() width accounting for gaps
        expect(html).toContain('calc((100% - (');
        expect(html).toContain('* 1)) / 2)'); // 2 columns means 1 gap
    });

    test('renders 4-column grid with correct widths', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 4
                            }
                        },
                        columns: [
                            { components: [] },
                            { components: [] },
                            { components: [] },
                            { components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should have 4 columns with calc() width accounting for gaps
        expect(html).toContain('calc((100% - (');
        expect(html).toContain('* 3)) / 4)'); // 4 columns means 3 gaps
    });

    test('applies default gap when not specified', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 2
                            }
                        },
                        columns: [
                            { components: [] },
                            { components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should have default gap of 1rem
        expect(html).toContain('gap: 1rem');
    });

    test('renders column labels in preview mode', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 3
                            }
                        },
                        columns: [
                            { components: [] },
                            { components: [] },
                            { components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'preview');
        const html = result.html;

        // Should show column labels in preview
        expect(html).toContain('Col 1');
        expect(html).toContain('Col 2');
        expect(html).toContain('Col 3');
        expect(html).toContain('column-label');
    });

    test('uses col class for responsive styling', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 3
                            }
                        },
                        columns: [
                            { components: [] },
                            { components: [] },
                            { components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should use .col class (not .col-sm) for mobile responsive CSS
        expect(html).toContain('class="col"');
        expect(html).not.toContain('class="col-sm"');
    });

    test('renders image components properly in columns', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'columnsgrid',
                        properties: {
                            layout: {
                                columns: 2
                            }
                        },
                        columns: [
                            {
                                components: [
                                    {
                                        name: 'image',
                                        properties: {
                                            source: {
                                                url: 'test.jpg',
                                                altText: 'Test'
                                            },
                                            layout: {
                                                widthMode: 'stretch'
                                            }
                                        }
                                    }
                                ]
                            },
                            { components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should render image with proper width mode
        expect(html).toContain('test.jpg');
        expect(html).toContain('width: 100%'); // Image stretch + column width
    });
});
