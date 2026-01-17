# Color Transparency Slider Implementation Plan

## Overview
Implement a transparency/opacity slider for the heading component's background color that works alongside the native HTML5 color picker. The color picker provides RGB values, and the slider provides the alpha (transparency) value.

## Problem Statement
- Native HTML5 `<input type="color">` only supports RGB hex colors (no alpha)
- Users need ability to set transparency for **background colors only**
- **Text/foreground colors (typography.color) should remain fully opaque - NO transparency option**
- Current rgba text input approach is not user-friendly
- Need visual, intuitive way to control background transparency

## Solution Architecture

### UI Components
1. **Color Picker** (`<input type="color">`) - Provides RGB values in hex format
2. **Transparency Slider** (`<input type="range">`) - Provides alpha value (0-100%)
3. **Display Label** - Shows current rgba value with transparency percentage

### Data Flow
```
User Interaction → Update Properties → Re-render Preview
     ↓                     ↓                    ↓
Color Picker         YAML Storage         Compute RGBA
  (#RRGGBB)      (rgb + transparency)    (rgb,r,g,b,a)
     +                    ↓
Transparency         Inline Styles
  Slider          background-color: rgba(...)
  (0-100%)
```

## Implementation Details

### 1. Schema Changes (`component_schemas.yaml`)

**Current (heading component):**
```yaml
heading:
  groups:
  - id: appearance
    label: Appearance
    fields:
    - path: appearance.background.color
      type: color
      label: Background Color
```

**New:**
```yaml
heading:
  groups:
  - id: typography
    label: Typography
    fields:
    - path: typography.color
      type: color
      label: Text Color
      # NOTE: NO transparency slider for text color - text is always opaque
  - id: appearance
    label: Appearance
    fields:
    - path: appearance.background.color
      type: color
      label: Background Color
    - path: appearance.background.transparency
      type: range
      label: Background Transparency
      min: 0
      max: 100
      default: 100
      unit: '%'
      # NOTE: Transparency only for background, not text
```

### 2. Default Values (`component_defaults.yaml`)

**Current:**
```yaml
heading:
  appearance:
    background:
      color: rgba(0,0,0,0)
```

**New:**
```yaml
heading:
  appearance:
    background:
      color: '#000000'
      transparency: 0
```

**Note:** Store color as hex (`#RRGGBB`) and transparency as percentage (0-100)

### 3. Properties Panel Renderer (`js/properties/index.js`)

#### Add Range Input Renderer
```javascript
/**
 * @function renderRangeInput
 * @description Renders an HTML range slider with value display
 * @param {object} options - Options for rendering the range input
 * @param {object} options.field - The field definition
 * @param {number} options.value - The current value
 * @param {string} options.fieldId - The ID for the input element
 * @returns {HTMLElement} Container with slider and value display
 */
const renderRangeInput = ({ field, value, fieldId }) => {
    const container = document.createElement('div');
    container.className = 'range-input-container';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.id = fieldId;
    slider.className = baseInputClass + ' range-slider';
    slider.min = field.min || 0;
    slider.max = field.max || 100;
    slider.value = value !== undefined ? value : (field.default || 100);

    const valueDisplay = document.createElement('span');
    valueDisplay.className = 'range-value';
    valueDisplay.textContent = `${slider.value}${field.unit || ''}`;

    slider.addEventListener('input', (e) => {
        valueDisplay.textContent = `${e.target.value}${field.unit || ''}`;
    });

    container.appendChild(slider);
    container.appendChild(valueDisplay);

    return container;
};
```

#### Update Field Type Switch
```javascript
// In renderPropertiesPanel function
switch (field.type) {
    case 'textarea':
        control = renderTextarea({ field, value: currentValue, fieldId });
        break;
    case 'select':
        control = renderSelect({ field, value: currentValue, fieldId });
        break;
    case 'number':
        control = renderTextInput({ field, value: currentValue, fieldId, type: 'number' });
        break;
    case 'color':
        control = renderColorInput({ field, value: currentValue, fieldId });
        break;
    case 'range':  // NEW
        control = renderRangeInput({ field, value: currentValue, fieldId });
        break;
    default:
        control = renderTextInput({ field, value: currentValue, fieldId, type: 'text' });
        break;
}
```

#### Revert Color Input to Native Picker
```javascript
const renderColorInput = ({ field, value, fieldId }) => {
    const input = document.createElement('input');
    input.type = 'color';  // Back to native color picker
    input.id = fieldId;
    input.className = baseInputClass;

    // Convert rgba to hex if needed
    let hexValue = value;
    if (value && value.startsWith('rgba')) {
        hexValue = rgbaToHex(value);
    } else if (!value || value === 'rgba(0,0,0,0)') {
        hexValue = '#000000';
    }

    input.value = hexValue;
    return input;
};

// Helper function to extract RGB from rgba
const rgbaToHex = (rgba) => {
    const matches = rgba.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!matches) return '#000000';

    const r = parseInt(matches[1]).toString(16).padStart(2, '0');
    const g = parseInt(matches[2]).toString(16).padStart(2, '0');
    const b = parseInt(matches[3]).toString(16).padStart(2, '0');

    return `#${r}${g}${b}`;
};
```

### 4. Renderer Logic (`js/render/index.js`)

Update `generateComponentInnerHTML` or heading-specific renderer to combine color + transparency:

```javascript
// In heading renderer or generateComponentInnerHTML
const backgroundColor = getNestedValue(properties, ['appearance', 'background', 'color']) || '#000000';
const transparency = getNestedValue(properties, ['appearance', 'background', 'transparency']);

let bgColorStyle = '';
if (backgroundColor && backgroundColor !== 'rgba(0,0,0,0)') {
    if (transparency !== undefined) {
        // Convert hex to rgba with transparency
        const rgbaColor = hexToRgba(backgroundColor, transparency);
        bgColorStyle = `background-color: ${rgbaColor};`;
    } else {
        bgColorStyle = `background-color: ${backgroundColor};`;
    }
}

// Helper function
const hexToRgba = (hex, transparencyPercent) => {
    // Remove # if present
    hex = hex.replace('#', '');

    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    // Convert transparency percent (0-100) to alpha (0-1)
    const alpha = transparencyPercent / 100;

    return `rgba(${r},${g},${b},${alpha})`;
};
```

### 5. CSS Styling (`css/style.css`)

```css
/* Range slider container */
.range-input-container {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    width: 100%;
}

.range-slider {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(to right, #e5e7eb, #3b82f6);
    outline: none;
    -webkit-appearance: none;
}

.range-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.range-slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #3b82f6;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.range-value {
    min-width: 45px;
    text-align: right;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
}
```

## Implementation Steps

### Phase 1: Schema & Defaults
1. Update `component_schemas.yaml` for heading component
   - Add transparency field with type `range` **ONLY for `appearance.background.transparency`**
   - Keep `typography.color` as simple color picker (no transparency)
2. Update `component_defaults.yaml` for heading component
   - Change background color from `rgba(0,0,0,0)` to `#000000`
   - Add `transparency: 0` (fully transparent by default)
   - Keep text color as hex (e.g., `#111827`) - no alpha value

### Phase 2: Properties Panel
1. Add `renderRangeInput()` function to `js/properties/index.js`
2. Add `range` case to field type switch
3. Revert `renderColorInput()` to use `type="color"`
4. Add `rgbaToHex()` helper function
5. Add CSS for range slider styling

### Phase 3: Renderer
1. Add `hexToRgba()` helper function to `js/render/index.js`
2. Update heading renderer to:
   - Read both `appearance.background.color` and `appearance.background.transparency`
   - Combine them into rgba format for inline styles
3. Handle edge cases (undefined transparency, transparent keyword)

### Phase 4: Testing
1. Create test file `js/render/__tests__/heading_transparency.test.js`
2. Test cases:
   - Color picker with 100% transparency (opaque)
   - Color picker with 0% transparency (fully transparent)
   - Color picker with 50% transparency (semi-transparent)
   - Default values on component insertion
   - Changing only color (transparency persists)
   - Changing only transparency (color persists)

### Phase 5: Extend to Other Components
Once heading component works, apply transparency slider to **background colors only** for:
1. Text components: paragraph, eyebrow, caption, blockquote
2. Layout components: layout-row, layout-column, page
3. Form components: textbox, textarea, button, dropdown
4. Container components: accordion, tabs (content background)

**IMPORTANT:**
- ✅ Add transparency to: `appearance.background.transparency`, `background.transparency`
- ❌ NO transparency for: `typography.color`, `appearance.border.color`, or any text/foreground colors

## Data Structure Examples

### YAML Storage
```yaml
- name: heading
  properties:
    text: Welcome
    appearance:
      background:
        color: '#3b82f6'        # Blue color
        transparency: 50        # 50% transparent
```

### Rendered Output
```html
<h2 style="background-color: rgba(59,130,246,0.5); ...">
  Welcome
</h2>
```

### Properties Panel State
```javascript
{
  'appearance.background.color': '#3b82f6',
  'appearance.background.transparency': 50
}
```

## Edge Cases to Handle

1. **Migrating Old Data**
   - Old YAML with `color: rgba(255,0,0,0.5)`
   - Convert to: `color: '#ff0000'` + `transparency: 50`

2. **Fully Transparent Background**
   - When transparency = 0, don't render background-color style at all
   - Or use `rgba(r,g,b,0)` which is valid CSS

3. **Undefined Transparency**
   - Default to 100 (fully opaque) if transparency not specified
   - Maintains backward compatibility

4. **Color Picker Changes**
   - When user changes color, preserve transparency value
   - When user changes transparency, preserve color value

## Benefits

✅ **User-Friendly**: Visual slider is more intuitive than typing rgba values
✅ **Standard UI**: Native color picker provides familiar color selection
✅ **Separation of Concerns**: RGB (color) and alpha (transparency) are independent
✅ **Backward Compatible**: Can convert existing rgba values during migration
✅ **Flexible**: Easy to extend to other components
✅ **Performance**: No complex parsing or validation needed

## Future Enhancements

1. **Color Preview Box**: Show live preview of color + transparency
2. **Preset Transparency Buttons**: Quick select 0%, 25%, 50%, 75%, 100%
3. **Gradient Support**: Multiple colors with different transparencies
4. **Copy/Paste**: Copy rgba value to clipboard
5. **Color Picker with Alpha**: Upgrade to custom color picker that includes alpha channel

## Testing Checklist

- [ ] Transparency slider appears for heading background color
- [ ] Slider shows current transparency percentage
- [ ] Color picker shows current RGB color (hex format)
- [ ] Changing color updates preview with same transparency
- [ ] Changing transparency updates preview with same color
- [ ] Setting transparency to 0% makes background fully transparent
- [ ] Setting transparency to 100% makes background fully opaque
- [ ] Default heading has transparent background (0%)
- [ ] Export HTML includes correct rgba inline styles
- [ ] All existing tests still pass
