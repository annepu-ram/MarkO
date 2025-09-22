
# Form Enhancement Plan

This document outlines the plan to enhance the form elements in the website builder, based on standard HTML form practices.

## 1. Deprecate Standalone Label Component

The `label` component will be removed as a standalone component from the component library. It will be integrated directly into the form field components.

**Action:**
- Remove `label` from the component insertion UI.
- Update the `insertYamlComponent` function in `js/script.js` to remove the `label` case.
- Remove the `label` entry from `component_defaults.yaml`.

## 2. Introduce a `form` Component

A new `form` component will be created to act as a container for form elements. This will replace the existing `group` component, which will be repurposed or removed. The `form` component will have a `width` property that defaults to `100%`.

**Action:**
- Rename the `group` component to `form` in `js/script.js` and `component_defaults.yaml`.
- The `renderGroupComponent` function will be renamed to `renderFormComponent`.
- The new `form` component will have a default `width` of `100%`.

## 3. Integrate Labels into Form Fields

The following components will be enhanced to include a `label` property:
- `textbox`
- `textarea`
- `dropdown`
- `radio`
- `checkbox`

The `label` property will be a string that represents the label text for the form field.

**Action:**
- Update `component_defaults.yaml` to add a `label` property to the `textbox`, `textarea`, `dropdown`, `radio`, and `checkbox` components.
- Update the `generateComponentInnerHTML` function in `js/script.js` to render the label and the form field wrapped in a `div` container. The `div` will have a `width` of `100%`. The `label` and the input will be associated using the `for` and `id` attributes.

### New HTML Structure Example (Textbox):

```html
<div style="width: 100%; margin-bottom: 1rem;">
  <label for="some_unique_id">Your Label Text</label>
  <input type="text" id="some_unique_id" ...>
</div>
```

## 4. Update Properties Panel

The properties panel will be updated to allow editing the new `label` property for the form field components.

**Action:**
- Update the `renderPropertiesPanel` function in `js/script.js` to render a text input for the `label` property when a `textbox`, `textarea`, `dropdown`, `radio`, or `checkbox` component is selected.

## 5. Example YAML Usage

Here is an example of how the new `form` and form field components will be used in the YAML structure:

```yaml
- name: form
  properties:
    width: '100%'
  components:
    - name: textbox
      properties:
        label: 'Your Name'
        placeholder: 'Enter your full name'
    - name: textarea
      properties:
        label: 'Your Message'
        placeholder: 'Enter your message'
        rows: 5
    - name: dropdown
      properties:
        label: 'Your Country'
        options: 'USA,Canada,UK'
    - name: checkbox
      properties:
        label: 'I agree to the terms'
        checked: true
    - name: button
      properties:
        text: 'Submit'
        variant: 'primary'
```
