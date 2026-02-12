# Gradient Backgrounds Implementation Plan

## Overview
Add gradient background support to all components that support background color. Users can toggle between solid color and gradient mode in the properties panel.

---

## UI Behavior
- **Background group** shows toggle pills: `Color` | `Gradient`
- **Color mode** (default): Single color picker + text input (current behavior)
- **Gradient mode**: Two color pickers + direction pills (4 options)

---

## Data Structure
```yaml
appearance:
  background:
    type: 'color'           # NEW: 'color' or 'gradient'
    color: '#ffffff'        # Existing - also used as gradient fallback
    transparency: 100       # Existing
    gradient:               # NEW
      colorStart: '#ff0000'
      colorEnd: '#0000ff'
      direction: 'to right' # 'to right', 'to bottom', 'to bottom right', 'to top right'
```

---

## Architecture Notes

**Properties Panel Field Rendering:**
- Uses `type: select` for options (NOT a separate "pills" type)
- Automatically renders as pills when options ≤ 6, dropdown otherwise (line 615)
- Value collection for pills: reads `.token-pill.active` data-value (lines 736-738)
- No existing `showWhen` support - needs to be added

**Key Functions:**
- `renderPropertiesPanel()` - Main render function (line 471)
- `renderTokenPills()` - Renders pill-style select (line 327)
- `collectPropertyValues()` - Collects form values (line 691)
- `activeFieldMeta` - Tracks field metadata for value collection

---

## Files to Modify

### 1. `component_schemas.yaml`
Add gradient fields to background group for all components with background support.

**Components to update:**
- page, layout-row, layout-column
- heading, paragraph, eyebrow, caption, blockquote
- button, textbox, textarea, dropdown
- titlebar, accordion, tabs

**Fields to add to each background group (after existing background fields):**
```yaml
- path: appearance.background.type
  type: select
  label: Background Type
  options:
    - color
    - gradient

- path: appearance.background.gradient.colorStart
  type: color
  label: Gradient Start
  showWhen:
    field: appearance.background.type
    value: gradient

- path: appearance.background.gradient.colorEnd
  type: color
  label: Gradient End
  showWhen:
    field: appearance.background.type
    value: gradient

- path: appearance.background.gradient.direction
  type: select
  label: Gradient Direction
  options:
    - to right
    - to bottom
    - to bottom right
    - to top right
  showWhen:
    field: appearance.background.type
    value: gradient
```

Note: `type: select` with ≤6 options automatically renders as pills.

---

### 2. `ssr_python/static/js/propertiesPanel.js`
Add conditional field rendering based on `showWhen` conditions.

**Changes Required:**

#### A. Add helper function to evaluate showWhen (after line 360):
```javascript
/**
 * Evaluate showWhen condition for conditional field visibility
 */
const evaluateShowWhen = (field, resolvedProps) => {
    if (!field.showWhen) return true;

    const { field: conditionPath, value: expectedValue } = field.showWhen;
    const pathSegments = pathToSegments(conditionPath);
    const actualValue = getNestedValue(resolvedProps, pathSegments);

    return actualValue === expectedValue;
};
```

#### B. Modify field rendering in renderPropertiesPanel (line 560):
Add conditional check before rendering each field:
```javascript
group.fields?.forEach(field => {
    // Check showWhen condition
    if (!evaluateShowWhen(field, resolvedProps)) {
        return; // Skip rendering this field
    }

    // ... existing field rendering code
});
```

#### C. Render all fields with data attributes for conditional visibility:
Instead of conditionally skipping fields, render ALL fields but mark hidden ones:

```javascript
group.fields?.forEach(field => {
    // ... existing setup code ...

    const { wrapper } = createFieldWrapper(field, fieldId);

    // Check showWhen condition and set visibility
    if (field.showWhen) {
        wrapper.dataset.showWhenField = field.showWhen.field;
        wrapper.dataset.showWhenValue = field.showWhen.value;

        const isVisible = evaluateShowWhen(field, resolvedProps);
        wrapper.dataset.hidden = !isVisible;
    }

    // ... rest of field rendering ...
});
```

#### D. Update pill click handler to toggle dependent fields:
In `renderTokenPills` (around line 351), modify the onclick:

```javascript
pill.onclick = () => {
    container.querySelectorAll('.token-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');

    // Toggle visibility of dependent fields
    const propertiesContent = document.getElementById('propertiesContent');
    if (propertiesContent) {
        const dependentFields = propertiesContent.querySelectorAll(
            `[data-show-when-field="${field.path}"]`
        );
        dependentFields.forEach(wrapper => {
            const expectedValue = wrapper.dataset.showWhenValue;
            wrapper.dataset.hidden = (pill.dataset.value !== expectedValue);
        });
    }
};
```

#### E. Exclude hidden fields from value collection:
In `collectPropertyValues()` (around line 708), skip hidden fields:

```javascript
activeFieldMeta.forEach((meta, fieldPath) => {
    // Skip hidden conditional fields
    const fieldId = `prop_${activeComponentId}_${fieldPath.replace(/[^a-z0-9]/gi, '_')}`;
    const wrapper = propertiesContent.querySelector(`#${fieldId}`)?.closest('.property-item');
    if (wrapper?.dataset.hidden === 'true') {
        return; // Don't collect value for hidden field
    }

    // ... existing collection code ...
});
```

---

### 3. `ssr_python/templates/macros/_components.html`
Update `build_styles` macro to render gradient CSS.

**Location:** Lines 913-921 (background rendering section)

**Replace current background logic with:**
```jinja2
{% if appearance.background %}
    {% set bg = appearance.background %}
    {% set bg_type = bg.type | default('color') %}

    {# Always set background-color for fallback/compatibility #}
    {% if bg_type == 'gradient' and bg.gradient %}
        {% set fallback_color = bg.gradient.colorStart | default(bg.color) | default('#ffffff') %}
    {% else %}
        {% set fallback_color = bg.color | default('#ffffff') %}
    {% endif %}

    {% if bg.transparency is defined %}
        {% set alpha_hex = bg.transparency | transparency_to_hex %}
        {% set fallback_color = fallback_color ~ alpha_hex %}
    {% endif %}
    {% set _ = styles.append('background-color: ' ~ fallback_color ~ ';') %}

    {# Add gradient if type is gradient #}
    {% if bg_type == 'gradient' and bg.gradient %}
        {% set direction = bg.gradient.direction | default('to right') %}
        {% set color_start = bg.gradient.colorStart | default('#ffffff') %}
        {% set color_end = bg.gradient.colorEnd | default('#000000') %}
        {% set _ = styles.append('background-image: linear-gradient(' ~ direction ~ ', ' ~ color_start ~ ', ' ~ color_end ~ ');') %}
    {% endif %}
{% endif %}
```

**Output CSS:**
- Solid color: `background-color: #ffffff;`
- Gradient: `background-color: #ff0000; background-image: linear-gradient(to right, #ff0000, #0000ff);`

---

### 4. `ssr_python/static/css/style.css`
Add styles for conditional field visibility.

```css
/* Conditional field visibility */
.property-item[data-hidden="true"] {
    display: none;
}

/* Gradient direction pills - compact */
.token-pills.direction-pills .token-pill {
    font-size: 0.7rem;
    padding: 2px 6px;
}
```

---

### 5. `LLM_COMPONENT_GUIDE.md`
Add gradient documentation section after the "Transparency System" section.

```markdown
## Gradient Backgrounds

Components with `appearance.background` support gradient backgrounds.

### Gradient Structure
\```yaml
appearance:
  background:
    type: 'gradient'
    color: '#ff6b6b'        # Fallback for older browsers
    gradient:
      colorStart: '#ff6b6b'
      colorEnd: '#4ecdc4'
      direction: 'to right'
\```

### Direction Options
| Value | Description |
|-------|-------------|
| `to right` | Left to right (horizontal) |
| `to bottom` | Top to bottom (vertical) |
| `to bottom right` | Diagonal ↘ |
| `to top right` | Diagonal ↗ |

### Examples

#### Hero gradient overlay
\```yaml
- name: layout-column
  properties:
    appearance:
      background:
        type: 'gradient'
        gradient:
          colorStart: 'rgba(0,0,0,0.8)'
          colorEnd: 'transparent'
          direction: 'to bottom'
\```

#### Vibrant CTA button
\```yaml
- name: button
  properties:
    appearance:
      background:
        type: 'gradient'
        gradient:
          colorStart: '#667eea'
          colorEnd: '#764ba2'
          direction: 'to right'
\```

#### Sunset hero section
\```yaml
- name: layout-row
  properties:
    appearance:
      background:
        type: 'gradient'
        gradient:
          colorStart: '#ff7e5f'
          colorEnd: '#feb47b'
          direction: 'to bottom right'
\```
```

---

## Implementation Order

1. **Schema** - Update `component_schemas.yaml` with gradient fields
2. **Properties Panel** - Add `showWhen` conditional rendering to `propertiesPanel.js`
3. **Jinja Macro** - Update `build_styles` in `_components.html` for gradient CSS
4. **CSS** - Add supporting styles to `style.css`
5. **Documentation** - Update `LLM_COMPONENT_GUIDE.md`

---

## What NOT to Change

- **component_defaults.yaml** - Keep defaults as-is (solid colors, no gradient defaults)
- Existing color picker behavior when in "Color" mode

---

## Verification Steps

1. Start Flask server: `cd ssr_python && python app.py`
2. Load bakery template or create a new page
3. Select a layout-row or button component
4. In properties panel Background group:
   - Verify "Color | Gradient" pills appear
   - Click "Color" - verify single color picker shows
   - Click "Gradient" - verify two color pickers + direction pills appear
5. Set gradient colors (e.g., #ff0000 to #0000ff) and direction (to right)
6. Verify preview shows gradient
7. Inspect rendered HTML - verify both `background-color` and `background-image` present
8. Switch back to "Color" - verify gradient fields hide, solid color applies
9. Test on multiple components (page, layout-column, button)

---

## CSS Output Reference

**Solid Color:**
```css
background-color: #ffffff;
```

**Gradient:**
```css
background-color: #ff0000;
background-image: linear-gradient(to right, #ff0000, #0000ff);
```

The `background-color` serves as a fallback for browsers that don't support gradients, and uses the first gradient color for visual consistency.
