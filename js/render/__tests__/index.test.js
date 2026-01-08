import { generateComponentInnerHTML, renderSimpleComponent, renderComponent } from '../index.js';
import * as State from '../../core/state.js';
import * as ObjectUtils from '../../utils/object.js';
import * as StyleUtils from '../../utils/styles.js';
import * as StringUtils from '../../utils/strings.js';

// Mock dependencies
jest.mock('../../core/state.js', () => ({
  registerComponentPath: jest.fn(),
  registerComponentForInitialization: jest.fn(),
  queueComponentInitialization: jest.fn(),
  consumeComponentInitializationQueue: jest.fn(() => []),
  resetComponentPathMap: jest.fn(),
}));
jest.mock('../../utils/object.js', () => ({
  deepMerge: jest.fn((target, ...sources) => Object.assign({}, target, ...sources)), // Simple merge for mock
  getNestedValue: jest.fn((obj, path = []) => path.reduce((acc, key) => {
    if (acc === undefined || acc === null) {
      return undefined;
    }
    return acc[key];
  }, obj)),
}));
jest.mock('../../utils/styles.js', () => ({
  toRem: jest.fn(value => {
    if (typeof value === 'number') {
      return `${value / 10}rem`;
    }
    if (typeof value === 'string') {
      const trimmed = value.trim();
      if (trimmed.endsWith('rem')) {
        return trimmed;
      }
      const numeric = parseFloat(trimmed);
      if (!Number.isNaN(numeric)) {
        return `${numeric / 10}rem`;
      }
    }
    return value;
  }),
  resolveSpacingValue: jest.fn(value => {
    const map = {
      none: '0',
      xs: '0.4rem',
      sm: '0.8rem',
      md: '1.6rem',
      lg: '2.4rem',
      xl: '3.2rem',
      auto: 'auto',
    };
    if (map[value] !== undefined) {
      return map[value];
    }
    const numeric = parseFloat(value);
    return !Number.isNaN(numeric) ? `${numeric / 10}rem` : value;
  }),
  resolveLetterSpacing: jest.fn(value => (value === 'wide' ? '0.1em' : value)),
  resolveLineHeight: jest.fn(value => (value === 1.5 ? 1.5 : value)),
  resolveTypographySize: jest.fn(value => {
    if (value === 'xl') {
      return '2.4rem';
    }
    const numeric = parseFloat(value);
    return !Number.isNaN(numeric) ? `${numeric / 10}rem` : value;
  }),
  resolveFontWeight: jest.fn(value => {
    const map = { light: 300, regular: 400, medium: 500, semibold: 600, bold: 700, extrabold: 800 };
    return map[value] ?? value;
  }),
}));
jest.mock('../../utils/strings.js', () => ({
  escapeHtml: jest.fn(value => {
    if (typeof value !== 'string') {
      return value;
    }
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }),
  escapeHtmlWithLineBreaks: jest.fn(value => {
    if (typeof value !== 'string') {
      return value;
    }
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\r\n|\r|\n/g, '<br>');
  }),
}));

describe('generateComponentInnerHTML', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should generate correct HTML for heading with center alignment', () => {
    const props = { level: 1, text: 'Main Title', typography: { align: 'center' } };
    const styleAttr = 'color: red;';
    const html = generateComponentInnerHTML('heading', props, '', styleAttr, 'preview');
    expect(html).toMatchSnapshot();
  });

  test('should generate correct HTML for paragraph', () => {
    const props = { text: 'Some text.' };
    const styleAttr = 'font-size: 1.6rem;';
    const html = generateComponentInnerHTML('paragraph', props, '', styleAttr, 'preview');
    expect(html).toMatchSnapshot();
  });

  test('should convert newline characters into <br> for paragraph text', () => {
    const props = { text: 'Line one\nLine two' };
    const html = generateComponentInnerHTML('paragraph', props, '', '', 'preview');
    expect(html).toContain('Line one<br>Line two');
  });

  test('applies width mode styles for heading', () => {
    const props = { text: 'Width sample', layout: { widthMode: '25' } };
    const html = generateComponentInnerHTML('heading', props, '', '', 'preview');
    const styleMatch = html.match(/style="([^"]*)"/);
    expect(styleMatch).toBeTruthy();
    const styleAttr = styleMatch[1];
    expect(styleAttr).toContain('display: inline-block');
    expect(styleAttr).toContain('box-sizing: border-box');
    expect(styleAttr).toContain('width: 25%');
  });


  test('should generate correct HTML for image', () => {
    const props = { src: 'test.jpg', alt: 'Test Image' };
    const styleAttr = '';
    const html = generateComponentInnerHTML('image', props, '', styleAttr, 'export');
    expect(html).toMatchSnapshot();
  });

  test('should generate correct HTML for textbox', () => {
    const props = { label: 'Name', placeholder: 'Enter name' };
    const styleAttr = '';
    // Mock Date.now and Math.random for predictable IDs
    const mockDate = 1678886400000; // Arbitrary timestamp
    const mockRandom = 0.123456789;
    jest.spyOn(global.Date, 'now').mockReturnValue(mockDate);
    jest.spyOn(global.Math, 'random').mockReturnValue(mockRandom);

    const html = generateComponentInnerHTML('textbox', props, '', styleAttr, 'preview');
    expect(html).toMatchSnapshot();
  });

  test('should handle unknown component type', () => {
    const props = {};
    const styleAttr = '';
    const html = generateComponentInnerHTML('unknown', props, '', styleAttr, 'preview');
    expect(html).toMatchSnapshot();
  });
});

describe('renderSimpleComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(global.Date, 'now').mockReturnValue(1678886400000);
    jest.spyOn(global.Math, 'random').mockReturnValue(0.123456789);
  });

  test('should wrap component in rendered-component div in preview mode', () => {
    const component = { name: 'paragraph', properties: { text: 'Hello' } };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'preview');
    expect(html).toMatchSnapshot();
    expect(State.registerComponentPath).toHaveBeenCalledWith(expect.any(String), path);
  });

  test('applies width mode styles to component directly in preview', () => {
    const component = {
      name: 'paragraph',
      properties: {
        text: 'Sized heading',
        layout: { widthMode: '25' },
      },
    };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'preview');
    // Component should have chrome-target class and all width styles
    expect(html).toContain('chrome-target');
    expect(html).toContain('width: 25%');
    expect(html).toContain('flex: 0 1 25%');
  });

  test('should return raw HTML in export mode', () => {
    const component = { name: 'paragraph', properties: { text: 'Hello' } };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'export');
    expect(html).toMatchSnapshot();
    expect(State.registerComponentPath).not.toHaveBeenCalled();
  });

  test('applies stretch width to component', () => {
    const component = {
      name: 'paragraph',
      properties: {
        text: 'Stretch me',
        layout: { widthMode: 'stretch' },
      },
    };
    const path = [0, 1];
    const html = renderSimpleComponent(component, path, 'preview');
    // Component should have chrome-target class and all width styles
    expect(html).toContain('chrome-target');
    expect(html).toContain('width: 100%');
    expect(html).toContain('flex: 1 1 100%');
  });

  test('applies spacing tokens when rendering simple component', () => {
    const component = {
      name: 'paragraph',
      properties: {
        text: 'Spacing tokens',
        spacing: {
          margin: { top: 'md', bottom: 'sm' },
          padding: { left: 'lg' },
        },
      },
    };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'export');
    expect(html).toContain('margin-top: 1.6rem;');
    expect(html).toContain('margin-bottom: 0.8rem;');
    expect(html).toContain('padding-left: 2.4rem;');
  });

  test('should register titlebar for initialization in preview mode', () => {
    const component = { name: 'titlebar', properties: { title: 'My Site' } };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'preview');
    expect(html).toMatchSnapshot();
    expect(State.queueComponentInitialization).toHaveBeenCalledWith({
      name: 'titlebar',
      id: expect.any(String),
      props: component.properties,
    });
  });
});

describe('renderLayoutContainer integration', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
    jest.clearAllMocks();
    jest.spyOn(global.Date, 'now').mockReturnValue(1678886400000);
    jest.spyOn(global.Math, 'random').mockReturnValue(0.987654321);
  });

  test('renders layout-row preview chrome with spacing', () => {
    const component = {
      name: 'layout-row',
      properties: {
        layout: { align: 'center', justify: 'space-between', gap: 'md' },
        spacing: { paddingBlock: 'md', paddingInline: 'lg' },
        background: { color: '#f0f4f8' },
        size: { minHeight: '160px' },
      },
      components: [],
    };
    const path = [0, 1];
    const html = renderComponent(component, path, 'preview');
    expect(html).toMatchSnapshot();
    expect(State.registerComponentPath).toHaveBeenCalledWith(expect.any(String), path);
  });

  test('renders layout-column export markup', () => {
    const component = {
      name: 'layout-column',
      properties: {
        layout: { align: 'stretch', justify: 'start', gap: 'md', tag: 'article' },
        spacing: { paddingBlock: 'sm', paddingInline: 'sm', marginBlock: 'none', marginInline: 'auto' },
        size: { maxWidth: '800px' },
        appearance: { radius: 'md' },
      },
      components: [],
    };
    const path = [0, 2];
    const html = renderComponent(component, path, 'export');
    expect(html).toContain('<article class="layout-column"');
    expect(html).toContain('max-width: 800px;');
    expect(State.registerComponentPath).not.toHaveBeenCalled();
  });
});
describe('Overlay Chrome', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        jest.spyOn(global.Date, 'now').mockReturnValue(1678886400000);
        jest.spyOn(global.Math, 'random').mockReturnValue(0.123456789);
    });

    test('should include chrome elements in preview mode', () => {
        const component = { name: 'paragraph', properties: { text: 'Hello' } };
        const path = [0, 0];
        const html = renderSimpleComponent(component, path, 'preview');
        expect(html).toContain('chrome-target');
        expect(html).toContain('chrome-label');
        expect(html).toContain('chrome-delete');
    });

    test('should not include chrome elements in export mode', () => {
        const component = { name: 'paragraph', properties: { text: 'Hello' } };
        const path = [0, 0];
        const html = renderSimpleComponent(component, path, 'export');
        expect(html).not.toContain('chrome-target');
        expect(html).not.toContain('chrome-label');
        expect(html).not.toContain('chrome-delete');
    });
});






