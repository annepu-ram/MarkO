
# Property Inconsistency Report

This report details inconsistencies found in the component property definitions across `component_schemas.yaml`, `component_defaults.yaml`, and their usage in the rendering logic (`js/render/index.js`).

## Global Inconsistencies

### 2. `label_properties`
- **Inconsistency**: The `generateComponentInnerHTML` function in `js/render/index.js` attempts to access `componentProps.label_properties` for `textbox`, `textarea`, `dropdown`, `checkbox`, and `radio` components. This property does not exist in either `component_schemas.yaml` or `component_defaults.yaml`. The intended property group seems to be `label`.
- **Affected Components**: `textbox`, `textarea`, `dropdown`, `checkbox`, `radio`
- **Recommendation**: Refactor the rendering logic to use the `label` property group instead of `label_properties`.

## Component-Specific Inconsistencies

### `titlebar`
- **Inconsistency**: The `generateTitlebarHTML` function in `js/render/index.js` accesses `props.layout.shrinkPercent`, but this property is not defined in the `titlebar` schema in `component_schemas.yaml`.
- **Recommendation**: Add `layout.shrinkPercent` to the `titlebar` schema.

### `image`
- **Inconsistency**: The `renderImageComponent` function in `js/render/index.js` accesses `properties.src` and `properties.alt`, but the schema and defaults use `source.url` and `source.altText`.
- **Recommendation**: Update `renderImageComponent` to use `properties.source.url` and `properties.source.altText`.

### `video`
- **Inconsistency**: The `generateComponentInnerHTML` function accesses `componentProps.src` for the video component, but the schema and defaults use `source.url`.
- **Recommendation**: Update `generateComponentInnerHTML` for the `video` component to use `componentProps.source.url`.

### `gif`
- **Inconsistency**: The `generateComponentInnerHTML` function accesses `componentProps.src` for the gif component, but the schema and defaults use `source.url`.
- **Recommendation**: Update `generateComponentInnerHTML` for the `gif` component to use `componentProps.source.url`.

### `link`
- **Inconsistency**: The `generateComponentInnerHTML` function accesses `componentProps.url` for the link component, but the schema and defaults use `href`.
- **Recommendation**: Update `generateComponentInnerHTML` for the `link` component to use `componentProps.href`.

### `columnsgrid`
- **Inconsistency**: The `renderColumnsGrid` function accesses `properties.count` to determine the number of columns, but the schema and defaults use `layout.columns`.
- **Recommendation**: Update `renderColumnsGrid` to use `properties.layout.columns`.

### `hamburger`
- **Inconsistency**: The `generateComponentInnerHTML` function accesses `componentProps.items` for the hamburger menu, but the schema and defaults use `links`.
- **Recommendation**: Update `generateComponentInnerHTML` for the `hamburger` component to use `componentProps.links`.

## Summary of Recommendations

To resolve these inconsistencies, the following actions are recommended:

1.  **Update `js/render/index.js`**:
    -   Correct the property access for `titlebar`, `image`, `video`, `gif`, `link`, `columnsgrid`, and `hamburger` components.
    -   Replace `label_properties` with `label` for form-related components.
2.  **Update `component_schemas.yaml`**:
    -   Add the `variant` property to the schemas of `paragraph` and any other text components that use it.
    -   Add `layout.shrinkPercent` to the `titlebar` schema.

By addressing these inconsistencies, we can improve the predictability and maintainability of the component rendering system.
