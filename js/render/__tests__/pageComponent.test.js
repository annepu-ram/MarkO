/**
 * Page component rendering tests - pseudo-element chrome architecture
 */

import { renderComponent } from '../index.js';
import * as State from '../../core/state.js';

jest.mock('../../core/state.js', () => ({
  registerComponentPath: jest.fn(),
  registerComponentForInitialization: jest.fn(),
  queueComponentInitialization: jest.fn(),
  consumeComponentInitializationQueue: jest.fn(() => []),
  resetComponentPathMap: jest.fn(),
}));

describe('Page Component Rendering', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(global.Date, 'now').mockReturnValue(1678886400000);
    jest.spyOn(global.Math, 'random').mockReturnValue(0.123456789);
  });

  describe('Preview Mode', () => {
    test('should render with chrome-target-page class (not chrome-target)', () => {
      const component = {
        name: 'page',
        properties: {
          background: { color: '#ffffff' },
          spacing: { paddingBlock: 'md', paddingInline: 'lg' },
        },
        components: [],
      };
      const path = [0];
      const html = renderComponent(component, path, 'preview');

      // Should have chrome-target-page class
      expect(html).toContain('chrome-target-page');

      // Should NOT have chrome-target class or chrome wrapper elements
      expect(html).not.toContain('class="chrome-target"');
      expect(html).not.toContain('chrome-label');
      expect(html).not.toContain('chrome-delete');
    });

    test('should include data-component-id for selection tracking', () => {
      const component = {
        name: 'page',
        properties: {},
        components: [],
      };
      const path = [0];
      const html = renderComponent(component, path, 'preview');

      expect(html).toContain('data-component-id="');
      expect(State.registerComponentPath).toHaveBeenCalledWith(expect.any(String), path);
    });

    test('should render with placeholder when empty', () => {
      const component = {
        name: 'page',
        properties: {},
        components: [],
      };
      const path = [0];
      const html = renderComponent(component, path, 'preview');

      expect(html).toContain('page-placeholder');
      expect(html).toContain('Click components from the sidebar to get started');
    });

    test('should render child components', () => {
      const component = {
        name: 'page',
        properties: {},
        components: [
          { name: 'heading', properties: { text: 'Test Title', level: 1 } },
        ],
      };
      const path = [0];
      const html = renderComponent(component, path, 'preview');

      expect(html).toContain('Test Title');
      expect(html).toContain('<h1');
    });

    test('should apply page styles correctly', () => {
      const component = {
        name: 'page',
        properties: {
          background: { color: '#f0f4f8' },
          spacing: { paddingBlock: 'lg', paddingInline: 'md' },
        },
        components: [],
      };
      const path = [0];
      const html = renderComponent(component, path, 'preview');

      // Should contain flex display and column direction
      expect(html).toContain('display: flex');
      expect(html).toContain('flex-direction: column');
      expect(html).toContain('width: 100%');
      expect(html).toContain('position: relative');
    });
  });

  describe('Export Mode', () => {
    test('should render clean HTML without chrome classes', () => {
      const component = {
        name: 'page',
        properties: {
          background: { color: '#ffffff' },
        },
        components: [
          { name: 'heading', properties: { text: 'Export Test', level: 2 } },
        ],
      };
      const path = [0];
      const html = renderComponent(component, path, 'export');

      // Should NOT have any chrome-related classes
      expect(html).not.toContain('chrome-target-page');
      expect(html).not.toContain('chrome-target');
      expect(html).not.toContain('chrome-label');
      expect(html).not.toContain('chrome-delete');
      expect(html).not.toContain('data-component-id');

      // Should contain the heading
      expect(html).toContain('Export Test');
    });

    test('should not register component path in export mode', () => {
      const component = {
        name: 'page',
        properties: {},
        components: [],
      };
      const path = [0];
      renderComponent(component, path, 'export');

      expect(State.registerComponentPath).not.toHaveBeenCalled();
    });
  });
});
