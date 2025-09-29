# Refactor `generateTitlebarLinks` Function Plan

## 1. Problem Statement

The `generateTitlebarLinks` function is currently defined as a local helper function within `generateTitlebarHTML` in `js/render/index.js`. While functional, this nesting limits its reusability and can be confusing for developers expecting it to be a standalone utility, especially given its role in generating a significant part of the titlebar's HTML.

## 2. Goal

To extract the `generateTitlebarLinks` function from its nested position within `generateTitlebarHTML` and define it as a module-level helper function in `js/render/index.js`. This will improve code organization, reusability, and clarity.

## 3. Current State

*   `generateTitlebarLinks` is defined inside `generateTitlebarHTML`.
*   It takes `links` (an array of link objects) and `props` (the full resolved properties of the titlebar) as arguments.
*   It utilizes other module-level or imported helper functions such as `getNestedValue`, `ensureRem`, `resolveFontWeight`, and `escapeHtml`.

## 4. Proposed Changes

### 4.1. Extract Function Definition

Move the entire definition of `generateTitlebarLinks` from its current location inside `generateTitlebarHTML` to the module level. A suitable location would be alongside other helper functions like `getAlignmentClass`.

### 4.2. Update Call Site

The call site `const linksHTML = generateTitlebarLinks(links, props);` within `generateTitlebarHTML` will remain unchanged, as `generateTitlebarLinks` will now be accessible in that scope as a module-level function.

### 4.3. Update JSDoc

Ensure the JSDoc comment block for `generateTitlebarLinks` is accurate and complete, reflecting its parameters, return value, and dependencies.

## 5. Dependencies

`generateTitlebarLinks` relies on the following functions:

*   `getNestedValue` (imported from `../utils/object.js`)
*   `ensureRem` (local helper function defined within `js/render/index.js`)
*   `resolveFontWeight` (imported from `../utils/styles.js`)
*   `escapeHtml` (imported from `../utils/strings.js`)

These dependencies must be accessible in the module scope where `generateTitlebarLinks` will be moved.

## 6. Testing

After implementing the refactoring, thoroughly test the `titlebar` component to ensure no regressions:

*   **Rendering:** Verify that the `titlebar` component still renders correctly in the live preview.
*   **Navigation Links:** Ensure that navigation links are displayed and styled as expected.
*   **Properties Panel:** Check that changes to link properties (label, href, typography) via the properties panel are correctly applied and reflected in the preview and YAML output.
*   **Mobile Menu:** Confirm that the mobile menu functionality (hamburger icon) still works as expected.
