**Enhancement Document: Styling for Titlebar Links (Revised)**

**1. Introduction**

This document proposes an enhancement to allow styling of the links within the `titlebar` component. This revised plan simplifies the initial proposal by applying styles to all links collectively, rather than individually. All numeric values for styling are specified in `rem` units.

**2. Proposed Changes**

The following new properties will be added to the `titlebar` component's `properties` object:

*   `linksBackgroundColor` (string, hex or color name)
*   `linksBorderWidth` (number, in rem)
*   `linksBorderStyle` (string, e.g., 'solid', 'dotted', 'dashed')
*   `linksBorderColor` (string, hex or color name)
*   `linksBorderRadius` (number, in rem)
*   `linksPadding` (string, e.g., '0.5rem 1rem')
*   `linksColor` (string, hex or color name)
*   `linksFontSize` (number, in rem)
*   `linksFontWeight` (string, e.g., 'normal', 'bold')
*   `linksFontStyle` (string, e.g., 'normal', 'italic')

**3. Implementation Plan**

1.  **`component_defaults.yaml`:**
    *   Add the new `links...` properties to the `titlebar` component's default properties, using `rem` for numeric values.

2.  **`js/script.js`:**
    *   **`generateTitlebarLinks` function:**
        *   This function will be modified to accept the `titlebar`'s `properties` object.
        *   It will construct a style string from the new `links...` properties, using the `toRem` utility function for numeric values.
        *   This style string will be applied to each `<a>` tag.
    *   **`renderPropertiesPanel` function:**
        *   When rendering the properties for a `titlebar`, this function will be updated to include input fields for the new `links...` properties.
    *   **`applyYamlComponentProperties` function:**
        *   This function will be updated to read the values of the new `links...` properties from the properties panel and save them to the `titlebar` component's properties.

**4. Example**

**`component_defaults.yaml`:**
```yaml
titlebar:
  ...
  linksBackgroundColor: '#f0f0f0'
  linksBorderWidth: 0.1
  linksBorderStyle: 'solid'
  linksBorderColor: '#cccccc'
  linksBorderRadius: 0.5
  linksPadding: '0.5rem 1rem'
  linksColor: '#000000'
  linksFontSize: 1.6
  linksFontWeight: 'normal'
  linksFontStyle: 'normal'
  links:
    - text: 'Home'
      value: '#home'
    - text: 'About'
      value: '#about'
```

**`generateTitlebarLinks` (pseudo-code):**
```javascript
function generateTitlebarLinks(links, props) {
    let linkStyles = '';
    if (props.linksBorderWidth > 0) {
        linkStyles += `border: ${toRem(props.linksBorderWidth)} ${props.linksBorderStyle || 'solid'} ${props.linksBorderColor || '#000'};`;
    }
    if (props.linksBackgroundColor) {
        linkStyles += `background-color: ${props.linksBackgroundColor};`;
    }
    if (props.linksBorderRadius) {
        linkStyles += `border-radius: ${toRem(props.linksBorderRadius)};`;
    }
    if (props.linksPadding) {
        linkStyles += `padding: ${props.linksPadding};`;
    }
    if (props.linksColor) {
        linkStyles += `color: ${props.linksColor};`;
    }
    if (props.linksFontSize) {
        linkStyles += `font-size: ${toRem(props.linksFontSize)};`;
    }
    if (props.linksFontWeight) {
        linkStyles += `font-weight: ${props.linksFontWeight};`;
    }
    if (props.linksFontStyle) {
        linkStyles += `font-style: ${props.linksFontStyle};`;
    }

    return links.map(link => {
        return `<a href="${link.value || '#'}" class="titlebar-link" style="${linkStyles}">${link.text || 'Link'}</a>`;
    }).join('');
}
```