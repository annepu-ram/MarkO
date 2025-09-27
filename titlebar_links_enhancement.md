**Enhancement Document: Styling for Titlebar Links**

**1. Introduction**

This document proposes an enhancement to allow more granular styling of the links within the `titlebar` component. Currently, the links are simple text links. This enhancement will add support for border and background styles for each individual link.

**2. Proposed Changes**

The following new properties will be added to the link objects within the `links` array of the `titlebar` component:

*   `borderWidth` (number, in pixels)
*   `borderStyle` (string, e.g., 'solid', 'dotted', 'dashed')
*   `borderColor` (string, hex or color name)
*   `backgroundColor` (string, hex or color name)
*   `borderRadius` (number, in pixels)
*   `padding` (string, e.g., '5px 10px')

**3. Implementation Plan**

1.  **`component_defaults.yaml`:**
    *   Update the `titlebar.navigation.links` property to include the new styling properties for each link.

2.  **`js/render/index.js`:**
    *   **`generateTitlebarLinks` function:**
        *   Modify this function to read the new properties from each link object.
        *   Generate inline styles for `border`, `background-color`, `border-radius`, and `padding` and apply them to the `<a>` tag for each link.

3.  **`js/properties/customRenderers.js`:**
    *   **`linksEditor` function:**
        *   Update this function to add input fields for `borderWidth`, `borderStyle`, `borderColor`, `backgroundColor`, `borderRadius`, and `padding` for each link in the properties panel.
        *   This will allow users to edit the new properties.

**4. Example**

**`component_defaults.yaml`:**
```yaml
titlebar:
  navigation:
    links:
      - label: Home
        href: '#home'
        borderWidth: 1
        borderStyle: 'solid'
        borderColor: '#cccccc'
        backgroundColor: '#f0f0f0'
        borderRadius: 5
        padding: '5px 10px'
```

**`generateTitlebarLinks` in `js/render/index.js` (pseudo-code):**
```javascript
function generateTitlebarLinks(links, focusColor) {
    return links.map(link => {
        let linkStyles = '';
        if (link.borderWidth > 0) {
            linkStyles += `border: ${link.borderWidth}px ${link.borderStyle || 'solid'} ${link.borderColor || '#000'};`;
        }
        if (link.backgroundColor) {
            linkStyles += `background-color: ${link.backgroundColor};`;
        }
        if (link.borderRadius) {
            linkStyles += `border-radius: ${link.borderRadius}px;`;
        }
        if (link.padding) {
            linkStyles += `padding: ${link.padding};`;
        }
        return `<a href="${link.href || '#'}" class="titlebar-link" style="${linkStyles} --focus-bg: ${focusColor || '#f0f0f0'}">${link.label || 'Link'}</a>`;
    }).join('');
}
```