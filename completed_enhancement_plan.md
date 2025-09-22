# Enhancement Plan

This document outlines the plan for the following enhancements:


1.  Add `transparent` and `gradient` options to the background color picker.
2.  Make component background transparent in preview mode when `backgroundColor` is `transparent`.

## 2. `transparent` and `gradient` Background Color

### `js/script.js` Changes:

1.  **Update `renderColorProperty` function in `renderPropertiesPanel`:**
    *   Add a dropdown (`<select>`) to choose the color type: `solid`, `transparent`, or `gradient`.
    *   Based on the selection, show the appropriate input fields:
        *   **`solid`:** The existing color picker.
        *   **`transparent`:** No input field needed.
        *   **`gradient`:** Input fields for gradient direction, start color, and end color.

2.  **Update `applyYamlComponentProperties` function:**
    *   Update the logic to read the new color type and its corresponding values.

3.  **Update `generateRemainingStyles` function:**
    *   Add logic to generate the correct CSS for `transparent` and `gradient` backgrounds.
        *   For `transparent`, it will set `background-color: transparent;`.
        *   For `gradient`, it will generate a `background-image: linear-gradient(...);`.

## 3. Transparent Background in Preview

This feature will be implemented as part of the changes for the `transparent` and `gradient` background color feature. The `generateRemainingStyles` function will handle the logic to set the background to `transparent` when the `backgroundColor` property is set to `transparent`.

## 4. Full Viewport Page Component

### `js/script.js` Changes:

1.  **Modify `renderComponents` function:**
    *   When a `page` component is found, apply its `backgroundColor`, `padding`, and other relevant properties directly to the `document.body` style.
    *   Ensure the `html` and `body` elements have `height: 100%` and `width: 100%` to fill the viewport. This can be done in `style.css` or directly via JavaScript.

## 5. Enhanced Form Component Styling

### `component_defaults.yaml` Changes:

1.  **Add new properties for form-related components:**
    *   For `label`, `textbox`, `dropdown`, and `radio` components, add the following properties with default values:
        *   `borderWidth`: e.g., `1px`
        *   `borderColor`: e.g., `#cccccc`
        *   `borderRadius`: e.g., `4px`
        *   `fontColor`: e.g., `#333333`
        *   `fontWeight`: e.g., `normal`

### `js/script.js` Changes:

1.  **Update rendering functions for form components:**
    *   In the rendering logic for `label`, `textbox`, `dropdown`, and `radio`, read the new style properties (`borderWidth`, `borderColor`, etc.) from the component's properties.
    *   Apply these properties as inline styles to the generated HTML elements.

### `css/style.css` or `css/components.css` Changes:

1.  **Add base styles for form elements:**
    *   Define default styles for `label`, `input[type="text"]`, `select`, etc., to ensure a consistent minimal look.
    *   These styles will be overridden by the inline styles from the component properties if provided.

## 6. Group (Form) Component

### `component_defaults.yaml` Changes:

1.  **Add a new `group` component:**
    *   Define a default structure for the `group` component, which will act as a form.
    *   It should have a `components` property to hold nested form elements.

### `js/script.js` Changes:

1.  **Add `group` component rendering logic:**
    *   Create a new rendering function for the `group` component.
    *   This function will generate a `<form>` element.
    *   It will then recursively call `renderComponents` to render the components defined within the `group`'s `components` property.
