# JavaScript Testing Plan

## 1. Purpose
This document outlines a plan for implementing comprehensive test cases for the application's JavaScript functions. The goal is to improve code reliability, prevent regressions, and ensure that components render and behave as expected across various configurations.

## 2. Scope
This plan will focus on unit and integration tests for the core rendering logic and related utility functions. Key areas to be covered include:
- `js/render/index.js`: `renderYamlStructure`, `renderComponentsList`, `renderComponent`, `generateComponentInnerHTML`, `generateRemainingStyles`, and specific component renderers (e.g., `renderCarousel`, `renderFormComponent`, `renderPageComponent`, `renderImageComponent`, `renderColumnsGrid`, `renderAccordion`, `renderTabs`).
- `js/utils/object.js`: `deepClone`, `deepMerge`, `getNestedValue`, `setNestedValue`, `deleteNestedValue`, `pruneEmptyValues`.
- `js/utils/styles.js`: `toRem`, `resolveSpacingValue`, `resolveLetterSpacing`, `resolveLineHeight`, `resolveTypographySize`, `resolveFontWeight`.
- `js/utils/strings.js`: `escapeHtml`.

## 3. Testing Framework/Tools
**Recommendation:** Jest

**Reasons:**
- Widely adopted, well-documented, and actively maintained.
- Provides a complete testing solution (test runner, assertion library, mocking capabilities).
- Excellent for unit testing JavaScript modules.
- Supports snapshot testing, which can be valuable for UI rendering components.

## 4. Test Strategy

### 4.1 Unit Tests
- **Focus:** Isolate individual functions and test their inputs and outputs.
- **Mocks:** Mock external dependencies (e.g., DOM manipulation, `Date.now()`, `Math.random()`, `jsyaml`, state management functions) to ensure tests are deterministic and fast.
- **Coverage:** Aim for high code coverage for utility functions and core rendering logic.

### 4.2 Integration Tests
- **Focus:** Verify the interaction between multiple modules or components.
- **Example:** Test that `renderYamlStructure` correctly orchestrates calls to `renderComponent` and `generateComponentInnerHTML`.
- **Snapshot Testing:** Use Jest's snapshot testing for `generateComponentInnerHTML` and `renderComponent` to ensure that the generated HTML output remains consistent across changes.

## 5. Detailed Test Cases (Examples)

### 5.1 `generateComponentInnerHTML(type, props, classes, styleAttr, mode)`
- **Purpose:** Verify that the function correctly generates the inner HTML string for various component types based on their properties.
- **Test Cases:**
    - **Heading Component:**
        - Input: `type: 'heading'`, `props: { level: 1, text: 'Main Title', typography: { align: 'center' } }`, `styleAttr: 'color: red;'`, `mode: 'preview'`
        - Expected Output: `<div style="text-align: center;"><h1 style="color: red;">Main Title</h1></div>`
        - Input: `type: 'heading'`, `props: { level: 3, text: 'Subtitle' }`, `styleAttr: ''`, `mode: 'export'`
        - Expected Output: `<h3>Subtitle</h3>`
    - **Paragraph Component:**
        - Input: `type: 'paragraph'`, `props: { text: 'Some text.' }`, `styleAttr: 'font-size: 1.6rem;'`, `mode: 'preview'`
        - Expected Output: `<p style="font-size: 1.6rem;">Some text.</p>`
    - **Image Component:**
        - Input: `type: 'image'`, `props: { src: 'test.jpg', alt: 'Test Image' }`, `styleAttr: ''`, `mode: 'export'`
        - Expected Output: `<img src="test.jpg" alt="Test Image" style="width: 100%; height: auto; object-fit: cover;">`
    - **Textbox Component:**
        - Input: `type: 'textbox'`, `props: { label: 'Name', placeholder: 'Enter name' }`, `styleAttr: ''`, `mode: 'preview'`
        - Expected Output: `<div style="width: 100%; margin-bottom: 1rem;"><label for="input_..." style="">Name</label><input type="text" id="input_..." placeholder="Enter name" value=""  /></div>` (unique ID will be mocked)
    - **Unknown Component:**
        - Input: `type: 'unknown'`, `props: {}`, `styleAttr: ''`, `mode: 'preview'`
        - Expected Output: `<div style="color: #ef4444; font-style: italic;">Unknown component: unknown</div>`

### 5.2 `renderSimpleComponent(component, path, mode)`
- **Purpose:** Verify that the function correctly wraps simple components in the `rendered-component` div for preview mode and handles initialization registration.
- **Test Cases:**
    - **Preview Mode:**
        - Input: `component: { name: 'paragraph', properties: { text: 'Hello' } }`, `path: [0, 0]`, `mode: 'preview'`
        - Expected Output: HTML string containing `<div class="rendered-component" data-component-id="comp_..." ...><div class="component-label">paragraph</div>...<p>Hello</p></div>`
    - **Export Mode:**
        - Input: `component: { name: 'paragraph', properties: { text: 'Hello' } }`, `path: [0, 0]`, `mode: 'export'`
        - Expected Output: `<p>Hello</p>` (no wrapper divs)
    - **Titlebar Initialization:**
        - Input: `component: { name: 'titlebar', properties: { title: 'My Site' } }`, `path: [0, 0]`, `mode: 'preview'`
        - Expected: `registerComponentForInitialization` is called with `('titlebar', 'titlebar_...', { title: 'My Site' })`.

### 5.3 Other Rendering Functions (General Guidelines)
- **`renderYamlStructure`:**
    - Test with a minimal valid `page` structure.
    - Test with an invalid root (e.g., not a `page` component, empty array).
    - Test with nested components to ensure recursive rendering.
- **`renderComponentsList`:**
    - Test with an empty list of components.
    - Test with multiple components, verifying correct concatenation.
- **`renderComponent`:**
    - Test that it dispatches to the correct specific renderer (e.g., `renderPageComponent`, `renderColumnsGrid`).
- **Specific Component Renderers (e.g., `renderColumnsGrid`, `renderAccordion`, `renderTabs`):**
    - Test correct HTML structure for the component.
    - Verify nested `renderComponentsList` calls for child components.
    - Test property application (e.g., `columnCount` for `columnsgrid`, `title` for `accordion`).

## 6. Mocking Strategy
- **DOM Manipulation:** For functions that create or query DOM elements (e.g., `document.createElement`, `document.getElementById`, `querySelector`), use Jest's `jsdom` environment or mock these methods directly.
- **Unique IDs:** Mock `Date.now()` and `Math.random()` to return predictable values for `componentId` generation.
- **State Management:** Mock functions from `js/core/state.js` (e.g., `registerComponentPath`, `getComponentPathMap`) to control and inspect their calls.
- **YAML Parsing:** Mock `window.jsyaml` if direct YAML parsing is tested, though most rendering tests will assume parsed JavaScript objects as input.

## 7. Integration with CI/CD
- Configure a `test` script in `package.json` (e.g., `"test": "jest"`).
- Ensure tests run automatically on every pull request or commit to the main branch.

## 8. Timeline/Phases
- **Phase 1 (Setup):** Configure Jest, set up basic test files for `js/utils` functions. **(Completed)**
- **Phase 2 (Core Rendering):** Implement unit and snapshot tests for `generateComponentInnerHTML` and `renderSimpleComponent`. **(Completed)**
- **Phase 3 (Complex Renderers):** Implement tests for `renderYamlStructure`, `renderComponentsList`, and specific component renderers (`renderColumnsGrid`, `renderAccordion`, etc.).
- **Phase 4 (Properties Panel):** Implement tests for `js/properties/index.js` and `js/properties/customRenderers.js`.
- **Phase 5 (Refinement):** Review test coverage, add edge case tests, and integrate into CI/CD.
