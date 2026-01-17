**Title:** Link properties are duplicated in YAML structure when applying changes to a Titlebar component.

**Description:**
When editing a `titlebar` component, the `applyYamlComponentProperties` function incorrectly processes the properties for navigation links. This results in duplicated and malformed link data in the component's YAML structure.

**Steps to Reproduce:**
1. Add a `titlebar` component to the canvas.
2. Select the `titlebar` component to open the properties panel.
3. Add or modify a navigation link.
4. Click "Apply Changes".
5. Inspect the YAML in the code editor.

**Expected Behavior:**
The `links` property in the YAML structure should be a clean array of link objects, like this:
```yaml
properties:
  links:
    - text: 'Home'
      value: '#home'
```

**Actual Behavior:**
The YAML structure contains both the correct `links` array and also individual properties for each link field, leading to duplicated data:
```yaml
properties:
  'links.0.text': 'Home'
  'links.0.value': '#home'
  links:
    - text: 'Home'
      value: '#home'
```
This happens because the main property processing loop in `applyYamlComponentProperties` does not exclude the individual link input fields (e.g., `links.0.text`). These are processed, and then a separate block of code for `titlebar` components processes them again to create the `links` array.

**Root Cause:**
The `forEach` loop in `applyYamlComponentProperties` iterates through all input fields in the properties panel. The condition to process a field is `!key.startsWith('images.') && key !== 'color_type' && ...`. This condition does not filter out keys starting with `links.`, causing them to be added as individual properties to the `newProps` object.

**Proposed Fix:**
Update the condition in the `forEach` loop to also exclude keys starting with `links.`.
Change:
`else if (!key.startsWith('images.') && key !== 'color_type' && ...)`
to:
`else if (!key.startsWith('images.') && !key.startsWith('links.') && key !== 'color_type' && ...)`

Additionally, the logic for handling color properties seems to be flawed and should be reviewed. The current implementation does not seem to correctly identify and process color inputs.