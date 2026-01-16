/**
 * @jest-environment jsdom
 */

import { createActions } from '../actions.js';
import * as State from '../../core/state.js';
import { parseYamlContent, generateYamlFromStructure } from '../../core/yaml.js';

// Mock dependencies
jest.mock('../../core/state.js', () => ({
  getComponentTemplates: jest.fn(),
  setYamlStructure: jest.fn(),
  getYamlStructure: jest.fn(),
  pushHistory: jest.fn(),
  setSelection: jest.fn(),
  getSelection: jest.fn(),
  getPathForComponent: jest.fn(),
  getComponentPathMap: jest.fn(() => new Map()),
  undo: jest.fn(),
  redo: jest.fn(),
  canUndo: jest.fn(),
  canRedo: jest.fn(),
}));

jest.mock('../../core/yaml.js', () => ({
  parseYamlContent: jest.fn(),
  generateYamlFromStructure: jest.fn(),
  getComponentByPath: jest.fn(),
  deleteComponentByPath: jest.fn(),
}));

jest.mock('../../../js/render/index.js', () => ({
  renderYamlStructure: jest.fn(() => ({ html: '<div>Mock HTML</div>' })),
  initializeAllComponents: jest.fn(),
  computeInlineStylesFromProperties: jest.fn(() => ''),
}));

jest.mock('../../component_interactions.js', () => ({
  componentInitializers: {},
}));

jest.mock('../../../js/properties/index.js', () => ({
  renderPropertiesPanel: jest.fn(),
  clearPropertiesPanel: jest.fn(),
  applyPropertiesForComponent: jest.fn(),
}));

describe('Page Component Mandatory Root', () => {
  let dom;
  let actions;
  let consoleWarnSpy;

  beforeEach(() => {
    // Setup DOM elements
    document.body.innerHTML = `
      <div id="appContainer">
        <textarea id="codeEditor"></textarea>
        <div id="preview"></div>
        <div id="propertiesContent"></div>
        <div id="propertiesPanel"></div>
      </div>
    `;

    dom = {
      appContainer: document.getElementById('appContainer'),
      editor: document.getElementById('codeEditor'),
      preview: document.getElementById('preview'),
      propertiesContent: document.getElementById('propertiesContent'),
      propertiesPanel: document.getElementById('propertiesPanel'),
      fullscreenModal: null,
      fullscreenContent: null,
      helpPanel: null,
      sidebarTabs: [],
      sidebarPanels: [],
      propertiesTab: null,
    };

    actions = createActions(dom);
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.clearAllMocks();
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
  });

  describe('Delete Guard', () => {
    test('should prevent deletion of page component (root at path [0])', () => {
      // Mock the structure with page component
      const pageStructure = [
        {
          name: 'page',
          properties: {},
          components: [
            { name: 'heading', properties: { text: 'Title' } },
          ],
        },
      ];

      State.getPathForComponent.mockReturnValue([0]); // Root path
      State.getYamlStructure.mockReturnValue(pageStructure);

      // Attempt to delete page component
      actions.deleteComponent('page-component-id');

      // Verify warning was logged
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        'Cannot delete page component - it is the mandatory root container'
      );

      // Verify no structure changes were made
      expect(State.setYamlStructure).not.toHaveBeenCalled();
    });

    test('should allow deletion of non-root components', () => {
      const pageStructure = [
        {
          name: 'page',
          properties: {},
          components: [
            { name: 'heading', properties: { text: 'Title' } },
          ],
        },
      ];

      const updatedStructure = [
        {
          name: 'page',
          properties: {},
          components: [],
        },
      ];

      State.getPathForComponent.mockReturnValue([0, 'components', 0]); // Child path
      State.getYamlStructure.mockReturnValue(pageStructure);

      const { deleteComponentByPath } = require('../../core/yaml.js');
      deleteComponentByPath.mockReturnValue(updatedStructure);
      generateYamlFromStructure.mockReturnValue('- name: page\n  properties: {}\n  components: []');

      // Attempt to delete child component
      actions.deleteComponent('heading-component-id');

      // Verify structure was updated
      expect(State.setYamlStructure).toHaveBeenCalledWith(updatedStructure);
      expect(deleteComponentByPath).toHaveBeenCalledWith(pageStructure, [0, 'components', 0]);
    });
  });

  describe('Clear Canvas', () => {
    test('should reset to default page component instead of clearing completely', () => {
      dom.editor.value = '- name: page\n  properties: {}\n  components:\n    - name: heading\n      properties:\n        text: "Title"';

      // Mock page defaults from component_defaults.yaml
      const pageDefaults = {
        background: { color: '#ffffff', image: '' },
        layout: {
          padding: { top: 'md', right: 'md', bottom: 'md', left: 'md' },
          margin: { top: 'none', right: 'none', bottom: 'none', left: 'none' }
        }
      };

      State.getComponentTemplates.mockReturnValue({ page: pageDefaults });

      const expectedDefaultYaml = `- name: page
  properties:
    background:
      color: '#ffffff'
      image: ''
    layout:
      padding:
        top: md
        right: md
        bottom: md
        left: md
      margin:
        top: none
        right: none
        bottom: none
        left: none
  components: []
`;

      generateYamlFromStructure.mockReturnValue(expectedDefaultYaml);
      parseYamlContent.mockReturnValue([
        { name: 'page', properties: pageDefaults, components: [] },
      ]);

      // Call clearCanvas
      actions.clearCanvas();

      // Verify editor was set to default page YAML with defaults
      expect(dom.editor.value).toBe(expectedDefaultYaml);

      // Verify parseAndRender was called with default page YAML
      expect(parseYamlContent).toHaveBeenCalledWith(expectedDefaultYaml);
      expect(State.pushHistory).toHaveBeenCalledWith(expectedDefaultYaml);
    });
  });
});
