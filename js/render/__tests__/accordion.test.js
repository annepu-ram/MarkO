import { renderYamlStructure } from '../index.js';
import { resetComponentPathMap } from '../../core/state.js';

describe('Accordion Rendering', () => {
    beforeEach(() => {
        resetComponentPathMap();
    });

    test('renders multiple accordion items from items array', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' },
                                { title: 'Item 2', content: 'Content 2' },
                                { title: 'Item 3', content: 'Content 3' }
                            ],
                            behavior: {
                                allowMultipleOpen: false
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should render accordion container
        expect(html).toContain('class="accordion-container"');

        // Should render 3 accordion items
        expect(html).toContain('Item 1');
        expect(html).toContain('Item 2');
        expect(html).toContain('Item 3');

        // Should render content
        expect(html).toContain('Content 1');
        expect(html).toContain('Content 2');
        expect(html).toContain('Content 3');

        // Should have details elements
        expect(html).toContain('<details class="accordion"');
        expect(html).toContain('class="accordion-summary"');
    });

    test('renders single accordion item when only one in array', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Single Item', content: 'Only content' }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        expect(html).toContain('Single Item');
        expect(html).toContain('Only content');
        expect(html).toContain('class="accordion-container"');
    });

    test('renders fallback when items array is empty', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: []
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should render default fallback
        expect(html).toContain('Click to expand');
        expect(html).toContain('class="accordion-container"');
    });

    test('applies allowMultipleOpen attribute correctly', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            behavior: {
                                allowMultipleOpen: true
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        expect(html).toContain('data-allow-multiple="true"');
    });

    test('defaults allowMultipleOpen to false when not specified', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        expect(html).toContain('data-allow-multiple="false"');
    });

    test('escapes HTML in titles', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: '<script>alert("xss")</script>', content: 'Safe content' }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should escape HTML tags
        expect(html).toContain('&lt;script&gt;');
        expect(html).not.toContain('<script>alert');
    });

    test('handles multiline content with line breaks', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                {
                                    title: 'FAQ',
                                    content: 'Line 1\nLine 2\nLine 3'
                                }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should convert newlines to <br>
        expect(html).toContain('<br>');
    });

    test('accordion only supports simple string content (not nested components)', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                {
                                    title: 'Simple accordion item',
                                    content: 'This is plain text content only'
                                }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should render simple string content
        expect(html).toContain('Simple accordion item');
        expect(html).toContain('This is plain text content only');

        // Should not have nested component HTML
        expect(html).not.toContain('<p');
        expect(html).not.toContain('<h3');
    });

    test('includes data attributes for accordion items', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' },
                                { title: 'Item 2', content: 'Content 2' }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should include unique IDs for container and items
        expect(html).toContain('data-accordion-id=');
        expect(html).toContain('id="accordion_container_');
    });

    test('renders in preview mode with chrome', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Preview Item', content: 'Preview content' }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'preview');
        const html = result.html;

        // Should have chrome wrapper
        expect(html).toContain('chrome-target');
        expect(html).toContain('data-component-id');
        expect(html).toContain('chrome-label');

        // Should still render content
        expect(html).toContain('Preview Item');
        expect(html).toContain('Preview content');
    });

    test('handles empty content gracefully', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Empty item', content: '' },
                                { title: 'Another empty', content: null }
                            ]
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should render titles without errors
        expect(html).toContain('Empty item');
        expect(html).toContain('Another empty');
        // Content should be empty but not break (now has background-color style)
        expect(html).toContain('class="card-body"');
    });

    test('applies border-bottom to both title and content by default when position not specified', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            appearance: {
                                border: {
                                    width: 2,
                                    style: 'solid',
                                    color: '#000000'
                                }
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should apply border-bottom to both title and content
        const borderBottomCount = (html.match(/border-bottom: 2px solid #000000/g) || []).length;
        expect(borderBottomCount).toBe(2); // Once for title, once for content
    });

    test('applies border-top to both title and content when position is top', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            appearance: {
                                border: {
                                    width: 2,
                                    style: 'solid',
                                    color: '#000000',
                                    position: 'top'
                                }
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should apply border-top to both title and content
        const borderTopCount = (html.match(/border-top: 2px solid #000000/g) || []).length;
        expect(borderTopCount).toBe(2); // Once for title, once for content
        expect(html).not.toContain('border-bottom: 2px solid #000000');
    });

    test('applies border-left to both title and content when position is left', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            appearance: {
                                border: {
                                    width: 3,
                                    style: 'solid',
                                    color: '#ff0000',
                                    position: 'left'
                                }
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should apply border-left to both title and content
        const borderLeftCount = (html.match(/border-left: 3px solid #ff0000/g) || []).length;
        expect(borderLeftCount).toBe(2); // Once for title, once for content
        expect(html).not.toContain('border-bottom');
    });

    test('applies border-right to both title and content when position is right', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            appearance: {
                                border: {
                                    width: 1,
                                    style: 'dashed',
                                    color: '#0000ff',
                                    position: 'right'
                                }
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should apply border-right to both title and content
        const borderRightCount = (html.match(/border-right: 1px dashed #0000ff/g) || []).length;
        expect(borderRightCount).toBe(2); // Once for title, once for content
        expect(html).not.toContain('border-bottom');
    });

    test('applies border on all sides to both title and content when position is all', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'accordion',
                        properties: {
                            items: [
                                { title: 'Item 1', content: 'Content 1' }
                            ],
                            appearance: {
                                border: {
                                    width: 2,
                                    style: 'solid',
                                    color: '#000000',
                                    position: 'all'
                                }
                            }
                        }
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        const html = result.html;

        // Should apply border on all sides to both title and content
        const borderAllCount = (html.match(/border: 2px solid #000000/g) || []).length;
        expect(borderAllCount).toBe(2); // Once for title, once for content
        expect(html).not.toContain('border-bottom');
        expect(html).not.toContain('border-top');
        expect(html).not.toContain('border-left');
        expect(html).not.toContain('border-right');
    });
});

