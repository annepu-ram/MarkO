# Titlebar Component Enhancement Plan

## 1. Problem Statement

The `generateTitlebarHTML` function in `js/render/index.js` currently expects a flat `props` object for the `titlebar` component. However, the `titlebar` schema defined in `component_schemas.yaml` and `component_defaults.yaml` uses a nested structure (e.g., `branding.logoUrl`, `layout.alignment`, `typography.title.size`). This mismatch prevents the `titlebar` from correctly rendering all its properties as defined in the schema.

## 2. Goal

To update the `generateTitlebarHTML` function to correctly access and apply all `titlebar` properties based on its nested schema, ensuring proper rendering, consistency with the new property handling, and full functionality of the properties panel for the `titlebar` component.

## 3. Current State

*   `generateTitlebarHTML` directly accesses properties like `props.alignment`, `props.logo`, `props.title`, `props.links`, `props.height`, `props.logoPosition`, `props.backgroundColor`, `props.titleFontSize`, `props.titleFontWeight`, `props.menuFontSize`, `props.menuFontWeight`.
*   The `titlebar` schema and defaults define these properties with nested paths (e.g., `layout.alignment`, `branding.logoUrl`, `branding.title`, `navigation.links`, `layout.height`, `layout.logoPlacement`, `appearance.background.color`, `typography.title.size`, `typography.title.weight`, `typography.menu.size`, `typography.menu.weight`).

## 4. Proposed Changes to `generateTitlebarHTML`

### 4.1. Access Nested Properties

Modify the `generateTitlebarHTML` function to use `getNestedValue` (from `js/utils/object.js`) to retrieve properties from the `props` object. The `props` object passed to `generateTitlebarHTML` will be the result of `deepMerge`ing the component's properties with its defaults, so it will contain the full, resolved nested structure.

**Specific Property Mappings:**

*   `props.alignment` -> `getNestedValue(props, ['layout', 'alignment'])`
*   `props.logo` -> `getNestedValue(props, ['branding', 'logoUrl'])`
*   `props.title` -> `getNestedValue(props, ['branding', 'title'])`
*   `props.links` -> `getNestedValue(props, ['navigation', 'links'])`
*   `props.height` -> `getNestedValue(props, ['layout', 'height'])`
*   `props.logoPosition` -> `getNestedValue(props, ['layout', 'logoPlacement'])`
*   `props.backgroundColor` -> `getNestedValue(props, ['appearance', 'background', 'color'])`
*   `props.titleFontSize` -> `getNestedValue(props, ['typography', 'title', 'size'])`
*   `props.titleFontWeight` -> `getNestedValue(props, ['typography', 'title', 'weight'])`
*   `props.menuFontSize` -> `getNestedValue(props, ['typography', 'menu', 'size'])`
*   `props.menuFontWeight` -> `getNestedValue(props, ['typography', 'menu', 'weight'])`

### 4.2. Apply Styles

*   The `generateRemainingStyles` function should handle most of the general appearance and typography properties. Ensure that `generateRemainingStyles` is called with the correct `props` object (the fully resolved one).
*   For `titlebar`-specific styles (e.g., `base-height`, `title-font-size`, `menu-font-size`, `shrink-scale`), ensure they are correctly derived from the nested properties and applied as CSS variables or inline styles.

### 4.3. Refactor `generateTitlebarLinks`

*   Ensure the `generateTitlebarLinks` helper function correctly processes the `navigation.links` array, which contains objects with `label` and `href` properties.

### 4.4. Handling Navigation Links (Properties Panel & Rendering)

**Properties Panel Rendering (`linksEditor` custom renderer):**

*   The `navigation.links` property in the `titlebar` schema is defined with `type: custom` and `renderer: linksEditor`.
*   The `linksEditor` custom renderer is located in `js/properties/customRenderers.js`.
*   `renderLinksEditor` is responsible for generating the UI for editing navigation links. It creates a dynamic list of input fields for each link's `label` and `href` properties.
*   Users can add new links or remove existing ones directly within this custom editor.
*   The `renderLinksEditor.serialize()` method extracts the current values from these input fields and returns an array of `{ label: string, href: string }` objects, which is then saved back into the component's `navigation.links` property.

**Titlebar HTML Generation (`generateTitlebarLinks` function):**

*   The `generateTitlebarHTML` function calls a helper function, `generateTitlebarLinks`, to construct the HTML for the navigation menu.
*   `generateTitlebarLinks` iterates through the array of link objects (retrieved from `getNestedValue(props, ['navigation', 'links'])`) and generates appropriate `<a>` tags for each link, incorporating their `label` and `href` values.

## 5. Dependencies

*   `js/utils/object.js`: `getNestedValue`
*   `js/render/index.js`: `generateRemainingStyles` (already used)

## 6. Testing

After implementing the changes, thoroughly test the `titlebar` component:

*   Verify that all properties (branding, navigation, layout, appearance, typography) can be set via the properties panel.
*   Ensure that changes made in the properties panel are correctly reflected in the live preview.
*   Check that the exported HTML for the `titlebar` component includes all applied styles and attributes correctly.
*   Confirm that the mobile menu functionality (hamburger icon) still works as expected.

## 7. Implementation Steps

1.  Import `getNestedValue` into `js/render/index.js`.
2.  Update all property accessors within `generateTitlebarHTML` to use `getNestedValue` with the appropriate paths.
3.  Review and adjust any style calculations (`ensureRem`, `baseHeightPx`, `titleFontSize`, `menuFontSize`, `shrinkScale`) to correctly use the nested property values.
4.  Verify the `generateTitlebarLinks` function's input and output based on the `navigation.links` structure.
