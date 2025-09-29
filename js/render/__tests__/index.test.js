import { generateComponentInnerHTML, renderSimpleComponent } from '../index.js';
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
    if (value === 'md') {
      return '1.6rem';
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
  escapeHtml: jest.fn(str => str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')),
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

  test('should return raw HTML in export mode', () => {
    const component = { name: 'paragraph', properties: { text: 'Hello' } };
    const path = [0, 0];
    const html = renderSimpleComponent(component, path, 'export');
    expect(html).toMatchSnapshot();
    expect(State.registerComponentPath).not.toHaveBeenCalled();
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

describe('titlebar rendering integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const buildTitlebarProps = overrides => ({
    branding: {
      logoUrl: 'https://example.com/logo.png',
      title: 'Sample Title',
    },
    layout: {
      alignment: 'center',
      height: 80,
    },
    navigation: {
      links: [
        { label: 'Home', href: '#home' },
        { label: 'About', href: '#about' },
      ],
    },
    typography: {
      title: { size: 32, weight: 'semibold', color: '#123456' },
      menu: { size: 18, weight: 'medium', color: '#654321' },
    },
    appearance: {
      focus: { background: '#cccccc', color: '#111111' },
    },
    ...overrides,
  });

  test('respects showLogo flag to hide logo', () => {
    const props = buildTitlebarProps();
    props.branding.showLogo = false;

    const html = generateComponentInnerHTML('titlebar', props, '', '', 'preview');

    expect(html).not.toContain('class="titlebar-logo"');
  });

  test('emits CSS variables for typography colours and weights', () => {
    const html = generateComponentInnerHTML('titlebar', buildTitlebarProps(), '', '', 'preview');

    expect(html).toContain('class="titlebar titlebar-center');

    const styleAttr = html.match(/style="([^"]+)"/)[1];
    expect(styleAttr).toContain('--titlebar-title-color: #123456;');
    expect(styleAttr).toContain('--titlebar-link-color: #654321;');
    expect(styleAttr).toContain('--title-font-weight: 600;');
    expect(styleAttr).toContain('--menu-font-weight: 500;');
    expect(styleAttr).toContain('--titlebar-link-hover-bg: #cccccc;');
    expect(styleAttr).toContain('--titlebar-link-hover-color: #111111;');

    expect(html).not.toMatch(/class="titlebar-link" style=/);
  });

  test('omits optional colour variables when typography values missing', () => {
    const overrides = {
      layout: { alignment: 'right', height: '72' },
      typography: {
        title: { size: 24 },
        menu: { size: 16 },
      },
      navigation: { links: [{ label: 'Docs', href: '#docs' }] },
      appearance: { focus: {} },
    };

    const html = generateComponentInnerHTML('titlebar', buildTitlebarProps(overrides), '', '', 'preview');

    expect(html).toContain('class="titlebar titlebar-right');

    const navIndex = html.indexOf('class="titlebar-nav"');
    const brandIndex = html.indexOf('class="titlebar-brand');
    expect(navIndex).toBeGreaterThan(-1);
    expect(brandIndex).toBeGreaterThan(-1);
    expect(navIndex).toBeLessThan(brandIndex);

    const brandCloseIndex = html.indexOf('</div>', brandIndex);
    const brandSegment = brandCloseIndex !== -1 ? html.slice(brandIndex, brandCloseIndex) : '';
    const titlePos = brandSegment.indexOf('titlebar-title');
    const logoPos = brandSegment.indexOf('titlebar-logo');
    if (logoPos !== -1 && titlePos !== -1) {
      expect(titlePos).toBeLessThan(logoPos);
    }


    const styleAttr = html.match(/style="([^"]+)"/)[1];
    expect(styleAttr).toContain('--title-font-weight: 700;');
    expect(styleAttr).toContain('--menu-font-weight: 500;');
    expect(styleAttr).not.toContain('--titlebar-title-color');
    expect(styleAttr).not.toContain('--titlebar-link-color');
  });
});
