# Color Picker Not Displaying Values - Bug Report

## Issue Description
After implementing rgba color support with alpha transparency, background color values are not showing up in the properties panel. The color input fields appear empty even though the component has valid rgba color values in the YAML.

## Root Cause Analysis

### 1. **YAML String Quoting Issue**
When colors were converted from hex (`#FFFFFF`) to rgba format (`rgba(255,255,255,1)`), they were wrapped in quotes in `component_defaults.yaml`:

```yaml
# Current (quoted)
background:
  color: 'rgba(255,255,255,1)'

# Expected (unquoted)
background:
  color: rgba(255,255,255,1)
```

**Problem**: YAML treats quoted values as literal strings, including the quotes. When the value is retrieved, it becomes `"'rgba(255,255,255,1)'"` instead of `"rgba(255,255,255,1)"`.

### 2. **Input Value Fallback Logic**
In `js/properties/index.js` line 324:
```javascript
input.value = value || 'rgba(255,255,255,1)';
```

**Problem**: If `value` is a quoted string like `"'rgba(255,255,255,1)'"`, it's truthy but invalid CSS, so the browser input doesn't display it properly.

### 3. **Schema Type Still Set to 'color'**
In `component_schemas.yaml`, all color fields still have:
```yaml
- path: background.color
  type: color  # Still expects hex color picker
  label: Background Color
```

**Problem**: While we changed the input rendering to text type, the schema metadata still says `type: color`, which might cause confusion or issues with validation.

## Files Affected

1. **`component_defaults.yaml`** (547 lines)
   - Lines with quoted rgba values: 3, 31, 37, 55, 61, 91, 95, 102, 106, 119, 122, 142, 151, 166, 174, 188, 196, 212, 220, 287, 297, 299, 316, 326, 328, 343, 345, 352, etc.

2. **`js/properties/index.js`** (lines 319-327)
   - `renderColorInput()` function with text input type

3. **`component_schemas.yaml`** (all color field definitions)
   - All fields with `type: color` (15+ components affected)

## Solution

### Option A: Remove Quotes from YAML (Recommended)

**Pros:**
- Cleaner YAML syntax
- No parsing issues
- rgba() is valid YAML without quotes

**Cons:**
- Need to update entire defaults file

**Implementation:**
```yaml
# Before
background:
  color: 'rgba(255,255,255,1)'

# After
background:
  color: rgba(255,255,255,1)
```

### Option B: Strip Quotes in JavaScript

**Pros:**
- No need to modify YAML file
- Quick fix

**Cons:**
- Adds complexity to rendering logic
- Doesn't fix root cause

**Implementation:**
```javascript
const renderColorInput = ({ field, value, fieldId }) => {
    const input = document.createElement('input');
    input.type = 'text';
    input.id = fieldId;
    input.className = baseInputClass;

    // Strip surrounding quotes if present
    let cleanValue = value || 'rgba(255,255,255,1)';
    if (typeof cleanValue === 'string') {
        cleanValue = cleanValue.replace(/^['"]|['"]$/g, '');
    }

    input.value = cleanValue;
    input.placeholder = field.placeholder || 'rgba(r,g,b,a) or #RRGGBBAA';
    return input;
};
```

### Option C: Use Hex8 Format Instead

**Pros:**
- More compact notation
- Standard web format

**Cons:**
- Less intuitive for alpha values
- Requires hex conversion

**Implementation:**
```yaml
background:
  color: "#FFFFFFFF"  # Last two digits = alpha (FF = 100%)
```

## Recommended Solution

**Use Option A** - Remove quotes from all rgba values in `component_defaults.yaml`

### Steps:
1. Remove quotes from all rgba color values in `component_defaults.yaml`
2. Keep rgba() values unquoted (YAML allows this)
3. Update the placeholder in `renderColorInput()` to be more helpful
4. Optionally update schema `type: color` to `type: rgba` for clarity

### Example Fix:

**component_defaults.yaml:**
```yaml
page:
  background:
    color: rgba(255,255,255,1)
    image: ''

layout-row:
  background:
    color: rgba(255,255,255,1)
  appearance:
    border:
      color: rgba(0,0,0,0)  # transparent
```

**js/properties/index.js:**
```javascript
const renderColorInput = ({ field, value, fieldId }) => {
    const input = document.createElement('input');
    input.type = 'text';
    input.id = fieldId;
    input.className = baseInputClass;
    input.value = value || 'rgba(255,255,255,1)';
    input.placeholder = 'rgba(255,255,255,1) or rgba(0,0,0,0)';
    input.title = 'Format: rgba(red, green, blue, alpha) - alpha from 0 (transparent) to 1 (opaque)';
    return input;
};
```

## Testing Checklist

After implementing the fix:
- [ ] Open app and add a heading component
- [ ] Check properties panel shows `rgba(17,24,39,1)` for text color
- [ ] Change alpha value to `0.5` and verify semi-transparency in preview
- [ ] Add layout-row and verify background shows `rgba(255,255,255,1)`
- [ ] Change background to `rgba(255,0,0,0.3)` and verify red semi-transparent background
- [ ] Export HTML and verify colors render correctly
- [ ] Run `npm test` to ensure all tests pass
- [ ] Check accordion, tabs, and other complex components

## Additional Notes

- YAML 1.2 specification allows unquoted strings that look like function calls (e.g., `rgba(...)`)
- The js-yaml library used in this project supports unquoted rgba values
- CSS `rgba()` format: `rgba(red, green, blue, alpha)` where:
  - red, green, blue: 0-255
  - alpha: 0.0 (fully transparent) to 1.0 (fully opaque)
