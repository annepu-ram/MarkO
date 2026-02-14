# Form Components Bug Report

**Date:** 2025-10-24
**Components Affected:** `button`, `textbox`, `textarea`, `dropdown`, and other form elements

---

## Issues Identified

### 1. Button Component Spanning Full Width

**Location:** [js/render/index.js:1136-1137](js/render/index.js#L1136-L1137)

**Current Behavior:**
- Button components are rendering with full width (100%) in flex containers
- Buttons stretch horizontally to fill their parent container

**Root Cause:**
The button renderer generates a simple `<button>` element without any width constraints:
```javascript
return '<button onclick="' + (componentProps.onclick || '') + '" ' + finalAttrs + '>' + (componentProps.text || 'Click Me') + '</button>';
```

However, the button is subject to width mode rules from lines 999-1015, which apply `flex: 1 1 100%` for stretch mode, causing it to grow to 100% width.

**Expected Behavior:**
- Buttons should have `width: auto` by default and only take up as much space as needed for their content
- Buttons should respect explicit width settings from properties

---

### 2. Textbox Label Not Displaying Properly

**Location:** [js/render/index.js:1128-1131](js/render/index.js#L1128-L1131)

**Current Behavior:**
- Textbox labels are not rendering or displaying correctly

**Root Cause:**
The textbox renderer has a mismatch between the data structure and the rendering code:

**Component Defaults Structure** ([component_defaults.yaml:289-318](component_defaults.yaml#L289-L318)):
```yaml
textbox:
  label:
    text: Textbox Label
    show: true
    typography:
      size: sm
      weight: medium
      color: '#374151'
  field:
    placeholder: Enter text...
    initialValue: ''
```

**Renderer Code** ([js/render/index.js:1131](js/render/index.js#L1131)):
```javascript
return '<div style="width: 100%; margin-bottom: 1rem;"><label for="' + id + '" style="' + labelStyles + '">' + (componentProps.label || '') + '</label>...
```

**Problems:**
1. **Property path mismatch**: Renderer looks for `componentProps.label` (string), but schema has `componentProps.label.text` (nested object)
2. **Label styles generation**: Uses `componentProps.label_properties` but should use `componentProps.label`
3. **Show/hide logic**: No implementation of `label.show` property to control label visibility
4. **Typography properties**: Label typography properties are not being applied

**Expected Behavior:**
- Label should display the text from `label.text` property
- Label should respect `label.show` to control visibility
- Label should apply typography properties (size, weight, color) from `label.typography`

---

### 3. Similar Issues in Other Form Components

**Affected Components:**
- `textarea` - Same label issues as textbox
- `dropdown` - Same label issues as textbox
- `checkbox` - Label structure issues
- `radio` - Label structure issues

All form field components have the same property path mismatch between:
- Component defaults (nested `label.text`, `label.show`, `label.typography`)
- Renderer code (expects flat `label` string)

---

## Detailed Analysis

### Button Width Issue

**CSS Contributing Factors** ([css/components.css:323-331](css/components.css#L323-L331)):
```css
button, .button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}
```

No explicit `width` or `display` property in CSS. The button inherits flex behavior from its parent container.

**Width Mode Logic** ([js/render/index.js:999-1015](js/render/index.js#L999-L1015)):
```javascript
if (TEXT_COMPONENTS_WITH_WIDTH_MODE.has(componentType)) {
    const widthMode = getNestedValue(componentProps, ['layout', 'widthMode']) || 'stretch';
    const widthRule = getWidthModeRule(widthMode);

    styleString = appendInlineStyle(styleString, 'display: inline-block; box-sizing: border-box;');
    styleString = appendInlineStyle(styleString, widthRule.component);

    if (Array.isArray(widthRule.flex)) {
        widthRule.flex.forEach(declaration => {
            if (declaration) {
                styleString = appendInlineStyle(styleString, declaration);
            }
        });
    }
}
```

**Issue:** Button is not in `TEXT_COMPONENTS_WITH_WIDTH_MODE` set (line 50), so it doesn't get width mode handling. However, when placed in a flex container (like `form`, `layout-row`, or `page`), it may stretch due to default flex behavior.

### Textbox Label Property Mapping

**Expected Data Flow:**
```
component_defaults.yaml → YAML editor → parseYamlContent() → State.yamlStructure → renderComponent() → generateComponentInnerHTML()
```

**Current Mismatch:**
- **Defaults define:** `textbox.label.text`, `textbox.label.show`, `textbox.label.typography.*`
- **Renderer expects:** `componentProps.label` (string), `componentProps.placeholder`, `componentProps.value`
- **Renderer uses:** `componentProps.label_properties` for styles (doesn't exist in defaults)

**Field Properties:**
- **Defaults define:** `textbox.field.placeholder`, `textbox.field.initialValue`, `textbox.field.required`
- **Renderer expects:** Direct properties `placeholder`, `value`

---

## Recommended Fixes

### Fix 1: Button Width Handling

**Option A - Add to Width Mode Components:**
Add button to `TEXT_COMPONENTS_WITH_WIDTH_MODE` set and default to `fit` mode:
```javascript
// Line 50
const TEXT_COMPONENTS_WITH_WIDTH_MODE = new Set(['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote', 'image', 'gif', 'button']);
```

Update button defaults to include layout.widthMode:
```yaml
button:
  text: Click Me
  layout:
    widthMode: fit  # Add this
  # ... rest of properties
```

**Option B - Add Explicit Width Styles:**
Modify button renderer to always include width constraint:
```javascript
} else if (componentType === 'button') {
    styleString = appendInlineStyle(styleString, 'width: auto; flex: 0 0 auto;');
    return '<button onclick="' + (componentProps.onclick || '') + '" ' + finalAttrs + '>' + (componentProps.text || 'Click Me') + '</button>';
}
```

### Fix 2: Textbox Label Property Access

Update textbox renderer to correctly access nested properties:

```javascript
} else if (componentType === 'textbox') {
    const id = 'input_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    // Access nested label properties
    const labelObj = componentProps.label || {};
    const labelText = labelObj.text || 'Label';
    const showLabel = labelObj.show !== false; // Default to true

    // Access nested field properties
    const fieldObj = componentProps.field || {};
    const placeholder = fieldObj.placeholder || 'Enter text...';
    const initialValue = fieldObj.initialValue || '';

    // Generate label styles from label.typography
    const labelTypography = labelObj.typography || {};
    const labelStyles = generateTypographyStyles(labelTypography);

    // Build label HTML only if show is true
    const labelHTML = showLabel ? '<label for="' + id + '" style="' + labelStyles + '">' + escapeHtml(labelText) + '</label>' : '';

    return '<div style="width: 100%; margin-bottom: 1rem;">' + labelHTML + '<input type="text" id="' + id + '" placeholder="' + escapeHtml(placeholder) + '" value="' + escapeHtml(initialValue) + '" ' + finalAttrs + ' /></div>';
}
```

**Note:** Need to create `generateTypographyStyles()` helper function or integrate with existing `generateRemainingStyles()`.

### Fix 3: Apply Similar Fixes to All Form Components

Update renderers for:
- `textarea` (line 1132-1135)
- `dropdown` (line 1138-1147)
- `checkbox` (line 1150-1153)
- `radio` (line 1154+)

All should:
1. Access `label.text`, `label.show`, `label.typography` correctly
2. Access `field.*` properties correctly
3. Generate proper label styles from typography settings
4. Respect show/hide logic

---

## Testing Plan

1. **Button Width Test:**
   - Create a form with a button component
   - Button should be auto-width (fit content)
   - Test button in different containers (form, layout-row, layout-column)
   - Test explicit width settings via properties panel

2. **Textbox Label Test:**
   - Create a textbox with default label
   - Label "Textbox Label" should be visible above input
   - Toggle `label.show` property - label should hide/show
   - Change `label.text` - text should update
   - Change `label.typography.color` - color should update
   - Change `label.typography.size` - size should update

3. **Form Component Integration Test:**
   - Create a complete form with: textbox, textarea, dropdown, checkbox, radio, button
   - All labels should display correctly
   - All components should have proper spacing
   - Button should not span full width

---

## Files Requiring Changes

1. **[js/render/index.js](js/render/index.js)** - Lines 1128-1160
   - Fix textbox renderer (line 1128-1131)
   - Fix textarea renderer (line 1132-1135)
   - Fix button renderer (line 1136-1137)
   - Fix dropdown renderer (line 1138-1147)
   - Fix checkbox renderer (line 1150-1153)
   - Fix radio renderer (line 1154+)

2. **[component_defaults.yaml](component_defaults.yaml)** - Lines 347-369 (optional)
   - Add `layout.widthMode: fit` to button if using Option A for button fix

3. **[css/components.css](css/components.css)** - Lines 323-331 (optional)
   - Add explicit width/flex properties to button if using Option B

---

## Priority

**High Priority:**
- Textbox label display (critical usability issue)
- Button width (affects layout significantly)

**Medium Priority:**
- Other form component label issues (same root cause as textbox)

---

## Related Code References

- Width mode logic: [js/render/index.js:50-72](js/render/index.js#L50-L72)
- Width mode application: [js/render/index.js:999-1015](js/render/index.js#L999-L1015)
- Form component renderer: [js/render/index.js:371-388](js/render/index.js#L371-L388)
- Component inner HTML generator: [js/render/index.js:974+](js/render/index.js#L974)
