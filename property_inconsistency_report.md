**Property Name Inconsistency Report and Fix Plan**

**1. Introduction**

This document outlines inconsistencies in property names used across the project, specifically in `component_defaults.yaml` and `js/script.js`. These inconsistencies make the code harder to understand and maintain. The goal is to standardize all property names to a consistent format.

**2. Inconsistent Property Names**

The following table summarizes the observed inconsistencies. The proposed standard is to use **camelCase** for all property names.

| Inconsistent Pair | Standard (camelCase) | Files Affected |
| :--- | :--- | :--- |
| `borderColor` / `border_color` | `borderColor` | `js/script.js` |
| `borderWidth` / `border_size` | `borderWidth` | `js/script.js` |
| `borderRadius` / `border_radius`| `borderRadius` | `js/script.js` |
| `fontColor` / `color` | `color` | `component_defaults.yaml`, `js/script.js` |

**3. Analysis of Inconsistencies**

*   **Border Properties:** The function `generateRemainingStyles` in `js/script.js` handles both camelCase (`borderColor`, `borderWidth`, `borderRadius`) and snake_case (`border_color`, `border_size`, `border_radius`) versions of border properties. This is redundant and confusing. The `applyYamlComponentProperties` function also lists both `borderColor` and `border_color` as color properties.

*   **Font Color:** In `component_defaults.yaml`, some components like `textbox`, `dropdown`, and `radio` use `fontColor`, while others like `h1`, `paragraph` use `color` for the same purpose. The standard should be `color`.

**4. Fix Plan**

I will perform the following changes to standardize the property names:

1.  **`js/script.js`:**
    *   In `generateRemainingStyles`:
        *   Remove the `if` conditions for `border_size`, `border_color`, and `border_radius`.
        *   Ensure that only `borderWidth`, `borderColor`, and `borderRadius` are used.
    *   In `applyYamlComponentProperties`:
        *   Remove `border_color` from the `colorProperties` array.

2.  **`component_defaults.yaml`:**
    *   Rename all instances of `fontColor` to `color`.
