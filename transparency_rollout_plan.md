# Background Transparency Rollout Plan

## Overview
Extend the background transparency feature (color picker + slider) that was implemented for the heading component to all other components that have background color properties.

## Current Implementation Status

### ✅ Completed
- **heading** - Background transparency with color picker + slider (0-100%)

### 🔄 Pending Components
Based on analysis of `component_defaults.yaml` and `component_schemas.yaml`, the following components have background color properties that need transparency sliders:

## Components Requiring Transparency

### 1. Text Components (5 components)
These components have `appearance.background.color`:
- **paragraph** - Line 133-147
- **eyebrow** - Line 156-179
- **caption** - Line 179-201
- **blockquote** - Line 201-225

**Schema Path**: `appearance.background.color` + `appearance.background.transparency`

### 2. Layout Containers (3 components)
These components have `background.color`:
- **page** - Line 1-15
- **layout-row** - Line 16-39
- **layout-column** - Line 40-63

**Schema Path**: `background.color` + `background.transparency`

### 3. Navigation Component (1 component)
- **titlebar** - Line 73-106 (has `appearance.background.color`)

**Schema Path**: `appearance.background.color` + `appearance.background.transparency`

### 4. Form Components (5 components)
These components have `appearance.background.color`:
- **textbox** - Line 280-308
- **textarea** - Line 309-335
- **button** - Line 336-357
- **dropdown** - Line 358-381

**Schema Path**: `appearance.background.color` + `appearance.background.transparency`

### 5. Container Components (2 components)
- **accordion** - Line 410-442 (has `appearance.background.color`)
- **tabs** - Line 443-477 (has content background color)
  - `appearance.content.background.color` + `appearance.content.background.transparency`

**Note**: Tabs component - transparency will ONLY be added to the content area background, NOT to tab button backgrounds (active/inactive).

## Implementation Strategy

### Phase 1: Simple Text Components (Priority: High)
**Components**: paragraph, eyebrow, caption, blockquote

**Changes Required per Component**:
1. ✅ Already have `appearance.background.color` in defaults (currently rgba)
2. ⚠️ Convert rgba color to hex in defaults
3. ⚠️ Add `transparency: 0` to defaults
4. ⚠️ Add transparency slider to schema (if appearance group exists)
5. ✅ Renderer already uses `generateRemainingStyles()` - no changes needed!

**Example for paragraph**:
```yaml
# component_defaults.yaml
paragraph:
  appearance:
    background:
      color: '#000000'      # Changed from rgba(0,0,0,0)
      transparency: 0       # NEW

# component_schemas.yaml
paragraph:
  groups:
  - id: appearance
    fields:
    - path: appearance.background.color
      type: color
    - path: appearance.background.transparency  # NEW
      type: range
      min: 0
      max: 100
      unit: '%'
```

### Phase 2: Layout Containers (Priority: High)
**Components**: page, layout-row, layout-column

**Changes Required per Component**:
1. ✅ Already have `background.color` in defaults
2. ⚠️ Convert rgba/hex to hex in defaults
3. ⚠️ Add `transparency: 100` to defaults (opaque by default for page backgrounds)
4. ⚠️ Add transparency slider to schema
5. ⚠️ Update renderer - these use different path (`background.color` not `appearance.background.color`)

**Special Note**: These components render via `renderPageComponent()` and `renderLayoutContainer()`, which call `generateRemainingStyles()`. The function already checks both `props.background` and `appearance.background`, so it should work!

**Example for page**:
```yaml
# component_defaults.yaml
page:
  background:
    color: '#ffffff'        # Changed from rgba(255,255,255,1)
    transparency: 100       # NEW - opaque by default

# component_schemas.yaml
page:
  groups:
  - id: background
    fields:
    - path: background.color
      type: color
    - path: background.transparency  # NEW
      type: range
      min: 0
      max: 100
      unit: '%'
```

### Phase 3: Navigation & Forms (Priority: Medium)
**Components**: titlebar, textbox, textarea, button, dropdown

**Changes Required per Component**:
1. ✅ Already have `appearance.background.color` in defaults
2. ⚠️ Convert rgba to hex in defaults
3. ⚠️ Add `transparency: 100` to defaults (opaque by default for UI elements)
4. ⚠️ Add transparency slider to schema
5. ⚠️ Check if custom renderers need updates

**Special Considerations**:
- **titlebar**: Has complex renderer (`renderTitlebar()`), may need custom handling
- **button**: Background color is critical for visibility - default to opaque
- **form inputs**: Background should typically be opaque for usability

### Phase 4: Container Components (Priority: Low)
**Components**: accordion, tabs

**Accordion**:
- Simple - same pattern as text components
- Already uses `generateRemainingStyles()`

**Tabs**:
- Add transparency ONLY to content area background
- Tab button backgrounds (active/inactive) remain opaque - no transparency sliders
- Custom renderer needs manual update for content background

**Example for tabs**:
```yaml
# component_defaults.yaml
tabs:
  appearance:
    tab:
      background:
        active: '#ffffff'      # Remains hex, no transparency
        inactive: '#f3f4f6'    # Remains hex, no transparency
    content:
      background:
        color: '#ffffff'       # Changed from rgba
        transparency: 100      # NEW - only for content area

# component_schemas.yaml
tabs:
  groups:
  - id: appearance
    fields:
    # Tab backgrounds - NO transparency sliders
    - path: appearance.tab.background.active
      type: color
    - path: appearance.tab.background.inactive
      type: color
    # Content background - WITH transparency slider
    - path: appearance.content.background.color
      type: color
    - path: appearance.content.background.transparency  # NEW
      type: range
      label: Content Background Transparency
      min: 0
      max: 100
      unit: '%'
```

**Tabs Renderer Update Required**:
```javascript
// In renderTabs function
const contentBg = getNestedValue(properties, ['appearance', 'content', 'background', 'color']) || '#ffffff';
const contentTransparency = getNestedValue(properties, ['appearance', 'content', 'background', 'transparency']);

let contentBgColor = contentBg;
if (contentTransparency !== undefined && contentBg.startsWith('#')) {
    contentBgColor = hexToRgba(contentBg, contentTransparency);
}

const contentStyles = buildStyleString([
    `background-color: ${contentBgColor};`,
    // ... other styles
]);
```

## Implementation Checklist

### For Each Component:

#### Step 1: Update component_defaults.yaml
- [ ] Locate component's background color property
- [ ] Convert rgba/hex to clean hex format (e.g., `'#3b82f6'`)
- [ ] Add `transparency: <value>` property
  - Use `0` for transparent by default (text components)
  - Use `100` for opaque by default (UI elements, layouts)
- [ ] Keep text colors as hex WITHOUT transparency

#### Step 2: Update component_schemas.yaml
- [ ] Find or create appearance/background group
- [ ] Locate existing `background.color` or `appearance.background.color` field
- [ ] Add transparency slider field immediately after color field:
  ```yaml
  - path: <color-path>.transparency
    type: range
    label: Background Transparency
    min: 0
    max: 100
    unit: '%'
  ```

#### Step 3: Verify Renderer Support
- [ ] Check if component uses `generateRemainingStyles()` - if yes, ✅ done!
- [ ] Check if component has custom renderer - may need manual updates
- [ ] Test that `hexToRgba()` is called correctly

#### Step 4: Testing
- [ ] Add component to page
- [ ] Open properties panel
- [ ] Verify color picker shows current color
- [ ] Verify transparency slider appears
- [ ] Adjust transparency to 50%
- [ ] Verify preview shows semi-transparent background
- [ ] Set transparency to 0% - verify fully transparent
- [ ] Set transparency to 100% - verify fully opaque
- [ ] Export HTML and verify rgba values are correct

## Batch Implementation Order

### Batch 1: Text Components (Similar Structure)
Do all together in one session:
1. paragraph
2. eyebrow
3. caption
4. blockquote

**Time Estimate**: 20 minutes

### Batch 2: Layout Containers
Do all together:
1. page
2. layout-row
3. layout-column

**Time Estimate**: 15 minutes

### Batch 3: Form Components
Do all together:
1. textbox
2. textarea
3. button
4. dropdown

**Time Estimate**: 20 minutes

### Batch 4: Navigation
1. titlebar (test separately due to complex renderer)

**Time Estimate**: 10 minutes

### Batch 5: Containers
1. accordion (simple)
2. tabs (simple - only content background, needs custom renderer update)

**Time Estimate**: 20 minutes

**Total Time Estimate**: ~1.5 hours for all components

## Automated Approach (Optional)

### Script to Update Defaults
Create Python script to convert all rgba colors to hex + transparency:

```python
import re
import yaml

def rgba_to_hex_and_transparency(rgba_str):
    """Convert 'rgba(255,255,255,1)' to ('#ffffff', 100)"""
    match = re.match(r'rgba\((\d+),(\d+),(\d+),([\d.]+)\)', rgba_str)
    if not match:
        return None, None

    r, g, b, a = match.groups()
    hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
    transparency = int(float(a) * 100)

    return hex_color, transparency

# Process component_defaults.yaml
with open('component_defaults.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Iterate through components and update
# ... automation logic ...
```

### Script to Update Schemas
Automatically add transparency fields after color fields in schemas.

## Special Cases & Edge Cases

### 1. Components Without Appearance Group
Some components may not have an appearance group in the schema yet:
- Create the group
- Add both color and transparency fields

### 2. Nested Background Colors
**Tabs component** has nested color structures:
- `appearance.tab.background.active` - NO transparency (remains opaque)
- `appearance.tab.background.inactive` - NO transparency (remains opaque)
- `appearance.content.background.color` - YES transparency slider

Only the content area gets transparency control.

### 3. Accordion Background Color
Accordion applies background to BOTH summary and content:
```javascript
// In accordion renderer
const summaryStyles = `background-color: ${backgroundColor};`;
const contentStyles = `background-color: ${backgroundColor};`;
```

Transparency will apply to both - which is correct behavior.

### 4. Components Not Using generateRemainingStyles()
These need custom handling:
- **titlebar**: Custom renderer, manually builds styles
- **accordion**: Custom renderer, but applies background directly
- **tabs**: Custom renderer, needs update for content background only

### 5. Color Validation
Ensure color picker handles:
- Existing rgba values → convert to hex
- Existing hex values → use as-is
- Missing values → default to `#000000`

## Verification Strategy

### Manual Testing
For each component:
1. Insert component
2. Check properties panel
3. Test all transparency values (0%, 25%, 50%, 75%, 100%)
4. Verify preview renders correctly
5. Export and check HTML

### Automated Testing
Add test cases for each component:
```javascript
test('applies background transparency to paragraph', () => {
    const component = {
        name: 'paragraph',
        properties: {
            appearance: {
                background: {
                    color: '#3b82f6',
                    transparency: 50
                }
            }
        }
    };

    const html = renderSimpleComponent(component, [0], 'export');
    expect(html).toContain('background-color: rgba(59,130,246,0.5)');
});
```

### Visual Regression Testing
Create test page with all components at various transparency levels:
- Save screenshot
- After changes, compare screenshots

## Rollback Plan

If issues arise:
1. Keep git commit before batch changes
2. Can revert individual components
3. Transparency defaults to 100 (opaque) for safety
4. Old rgba values still work (fallback in renderer)

## Success Criteria

✅ All components with background colors have transparency sliders
✅ Color picker + slider work together seamlessly
✅ Preview shows correct rgba colors
✅ Export HTML contains correct rgba values
✅ All existing tests pass
✅ No breaking changes to existing YAML files
✅ Text colors remain unaffected (no transparency)

## Post-Implementation

### Documentation Updates
- Update README.md with transparency feature
- Add transparency examples to example templates
- Update CLAUDE.md with new pattern
- Create video/gif demo of transparency feature

### Example Templates
Update all example templates to use new format:
- `example_templates/restaurant_template.yaml`
- `example_templates/conference_template.yaml`
- etc.

### Migration Guide
For users with existing YAML:
```yaml
# Old format (still works)
appearance:
  background:
    color: rgba(59,130,246,0.5)

# New format (recommended)
appearance:
  background:
    color: '#3b82f6'
    transparency: 50
```

## Notes

- **IMPORTANT**: Only add transparency to BACKGROUND colors, never to text/foreground colors
- Default transparency values:
  - Text components: `0` (transparent)
  - UI elements: `100` (opaque)
  - Layout containers: `100` (opaque)
- Renderer `generateRemainingStyles()` already handles the logic
- Native HTML5 color picker for best UX
- Range slider provides intuitive transparency control
