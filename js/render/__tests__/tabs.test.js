import { renderYamlStructure } from '../index.js';
import { resetComponentPathMap } from '../../core/state.js';

describe('Tabs Rendering', () => {
    beforeEach(() => {
        resetComponentPathMap();
    });

    test('renders tabs with nested components', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [
                            {
                                title: 'Tab 1',
                                components: [
                                    {
                                        name: 'heading',
                                        properties: { text: 'Heading 1', level: 2 }
                                    }
                                ]
                            },
                            {
                                title: 'Tab 2',
                                components: [
                                    {
                                        name: 'paragraph',
                                        properties: { text: 'Paragraph 2' }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('Tab 1');
        expect(result.html).toContain('Heading 1');
        expect(result.html).toContain('Tab 2');
        expect(result.html).toContain('Paragraph 2');
        expect(result.html).toContain('class="tabs"');
    });

    test('renders empty tabs with components array', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [
                            { title: 'Empty Tab', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('Empty Tab');
        expect(result.html).toContain('class="tabs"');
        expect(result.html).toContain('type="radio"');
    });

    test('applies typography styling to tab labels', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            typography: {
                                label: {
                                    size: 'lg',
                                    weight: 'bold',
                                    active: { color: '#FF0000' },
                                    inactive: { color: '#0000FF' }
                                }
                            }
                        },
                        tabs: [
                            { title: 'Styled Tab', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('font-weight: 700');
        expect(result.html).toContain('--active-color: #FF0000');
        expect(result.html).toContain('color: #0000FF');
    });

    test('applies appearance styling to tabs and content', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                tab: {
                                    background: {
                                        active: '#00FF00',
                                        inactive: '#FFFF00'
                                    }
                                },
                                content: {
                                    background: {
                                        color: '#0000FF'
                                    }
                                }
                            }
                        },
                        tabs: [
                            { title: 'Tab', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('--active-bg: #00FF00');
        expect(result.html).toContain('background-color: #FFFF00');
        expect(result.html).toContain('background-color: #0000FF');
    });

    test('applies width mode', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            layout: {
                                widthMode: '75'
                            }
                        },
                        tabs: [
                            { title: 'Tab', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('width: 75%');
    });

    test('applies orientation attribute', () => {
        const structureHorizontal = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            layout: { orientation: 'horizontal' }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const resultHorizontal = renderYamlStructure(structureHorizontal, 'export');
        expect(resultHorizontal.html).toContain('data-orientation="horizontal"');

        const structureVertical = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            layout: { orientation: 'vertical' }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const resultVertical = renderYamlStructure(structureVertical, 'export');
        expect(resultVertical.html).toContain('data-orientation="vertical"');
    });

    test('applies spacing (margins)', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            spacing: {
                                marginBlock: 'lg',
                                marginInline: 'md'
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('margin-block:');
        expect(result.html).toContain('margin-inline:');
    });

    test('renders multiple tabs with correct radio grouping', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [
                            { title: 'Tab A', components: [] },
                            { title: 'Tab B', components: [] },
                            { title: 'Tab C', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('Tab A');
        expect(result.html).toContain('Tab B');
        expect(result.html).toContain('Tab C');

        // All radio buttons should have the same name for grouping
        const radioMatches = result.html.match(/name="tabs_[a-z0-9]+"/g);
        expect(radioMatches).not.toBeNull();
        const uniqueNames = [...new Set(radioMatches)];
        expect(uniqueNames.length).toBe(1); // All should have same name
    });

    test('first tab is checked by default', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [
                            { title: 'First', components: [] },
                            { title: 'Second', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');

        // Find the first radio button
        const firstRadioMatch = result.html.match(/<input type="radio"[^>]*checked/);
        expect(firstRadioMatch).not.toBeNull();

        // Ensure only one is checked
        const checkedCount = (result.html.match(/checked/g) || []).length;
        expect(checkedCount).toBe(1);
    });

    test('escapes HTML in tab titles', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [
                            { title: '<script>alert("xss")</script>', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).not.toContain('<script>');
        expect(result.html).toContain('&lt;script&gt;');
    });

    test('applies border styling to content', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                content: {
                                    border: {
                                        width: 3,
                                        color: '#00FF00'
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('border: 3px solid #00FF00');
    });

    test('applies content padding', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                content: {
                                    padding: {
                                        block: 'xl',
                                        inline: 'lg'
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('padding-block:');
        expect(result.html).toContain('padding-inline:');
    });

    test('renders in preview mode with chrome', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {},
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'preview');
        expect(result.html).toContain('chrome-target');
        expect(result.html).toContain('chrome-label');
        expect(result.html).toContain('>tabs</span>');
    });

    test('applies upper border position', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                tab: {
                                    border: {
                                        width: 2,
                                        position: 'upper'
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('border-top: 2px solid');
        expect(result.html).toContain('--border-position: upper');
    });

    test('applies lower border position (default)', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                tab: {
                                    border: {
                                        position: 'lower'
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('border-bottom:');
        expect(result.html).toContain('--border-position: lower');
    });

    test('applies full border position', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                tab: {
                                    border: {
                                        position: 'full'
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('border: 2px solid');
        expect(result.html).not.toContain('border-top:');
        expect(result.html).not.toContain('border-bottom:');
        expect(result.html).toContain('--border-position: full');
    });

    test('border color uses typography inactive color', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            typography: {
                                label: {
                                    inactive: {
                                        color: '#FF0000'
                                    }
                                }
                            },
                            appearance: {
                                tab: {
                                    border: {
                                        position: 'lower',
                                        width: 2
                                    }
                                }
                            }
                        },
                        tabs: [{ title: 'Tab', components: [] }]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('border-bottom: 2px solid #FF0000');
    });

    test('applies gap between tabs', () => {
        const structure = [
            {
                name: 'page',
                properties: {},
                components: [
                    {
                        name: 'tabs',
                        properties: {
                            appearance: {
                                tab: {
                                    gap: 'md'
                                }
                            }
                        },
                        tabs: [
                            { title: 'Tab 1', components: [] },
                            { title: 'Tab 2', components: [] }
                        ]
                    }
                ]
            }
        ];

        const result = renderYamlStructure(structure, 'export');
        expect(result.html).toContain('gap:');
    });
});
