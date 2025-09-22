# Refactor Components Plan

This document outlines the plan to refactor the form components to include styling properties for their labels.

## 1. Update `component_defaults.yaml`

Add a `label_properties` object to the `textbox`, `textarea`, `dropdown`, `radio`, and `checkbox` components. This object will contain the following properties:

- `fontSize`: 14
- `fontWeight`: '500'
- `fontStyle`: 'normal'
- `color`: '#374151'
- `backgroundColor`: 'transparent'

**Example for `textbox`:**

```yaml
textbox:
  label: 'Textbox Label'
  placeholder: 'Enter text...'
  value: ''
  padding: 10
  margin: 10
  borderWidth: 1
  borderColor: '#cccccc'
  borderRadius: 4
  fontColor: '#333333'
  fontWeight: 'normal'
  label_properties:
    fontSize: 14
    fontWeight: '500'
    fontStyle: 'normal'
    color: '#374151'
    backgroundColor: 'transparent'
```

## 2. Update `js/script.js`

### a. `generateComponentInnerHTML` function

Modify this function to handle the new `label_properties`. For each form component, it will:

1.  Generate a unique ID for the input element.
2.  Create a `<label>` element with the `for` attribute pointing to the input's ID.
3.  Generate the styles for the label using the `generateRemainingStyles` function and the `label_properties`.
4.  Apply the styles to the `<label>` element.
5.  Wrap the `<label>` and the input element in a `div` container.

**Example for `textbox`:**

```javascript
textbox: () => {
    const id = `input_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const labelStyles = generateRemainingStyles(props.label_properties || {});
    return `<div style="width: 100%; margin-bottom: 1rem;">
              <label for="${id}" style="${labelStyles}">${props.label}</label>
              <input type="text" id="${id}" placeholder="${props.placeholder || 'Enter text...'}" value="${props.value || ''}" ${finalAttrs} />
            </div>`;
},
```

### b. `renderPropertiesPanel` function

Modify this function to render the properties for the `label_properties` object. When a form component is selected, it will:

1.  Check if the component has `label_properties`.
2.  If it does, render a new section in the properties panel for the label properties.
3.  This section will contain input fields for `fontSize`, `fontWeight`, `fontStyle`, `color`, and `backgroundColor` for the label.

### c. `applyYamlComponentProperties` function

Modify this function to apply the changes from the new label properties section in the properties panel to the `label_properties` object in the component's YAML structure.