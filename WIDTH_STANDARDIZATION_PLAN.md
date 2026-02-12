# Width Property Standardization Plan

## Goal

Standardize width behavior across ALL components to match text component behavior, which is the desired standard.

### Desired Behavior (Text Component Standard)
- **Width sticks to set value** - components respect their widthMode percentage
- **wrap: nowrap** - items stay on single line (squeezed if necessary)
- **wrap: wrap** - items wrap to next line AND scrollbar appears if needed

---

## Part 1: Property Name, Label, and Value Consistency

### Current State (Inconsistencies Highlighted)

| Component | Property Path | Label | Values Source | Current Values |
|-----------|--------------|-------|---------------|----------------|
| layout-column | `layout.widthMode` | Width | `tokens: widthPercentages` | fit,16,25,33,50,66,75,83,stretch |
| heading | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| paragraph | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| eyebrow | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| caption | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| blockquote | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| **link** | **MISSING** | - | - | - |
| image | `layout.widthMode` | Width | `tokens: widthPercentages` | fit,16,25,33,50,66,75,83,stretch |
| gif | `layout.widthMode` | Width | `tokens: widthPercentages` | fit,16,25,33,50,66,75,83,stretch |
| **tabs** | `layout.widthMode` | **Width Mode** | inline options | fit,25,50,75,stretch |
| accordion | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| video-background | `layout.widthMode` | Width | inline options | fit,25,50,75,stretch |
| **video** | **MISSING** | - | - | - |
| **carousel** | **MISSING** | - | - | - |

### Target State (Standardized)

**All components should use:**
- **Property path:** `layout.widthMode`
- **Label:** `Width` (not "Width Mode")
- **Values source:** `tokens: widthPercentages`
- **Values:** fit, 16, 25, 33, 50, 66, 75, 83, stretch

### widthPercentages Token (schema_tokens.yaml lines 151-171)

```yaml
widthPercentages:
  type: selectOptions
  options:
    - value: stretch
      label: "Full Width (100%)"
    - value: "83"
      label: "83% (10/12 columns)"
    - value: "75"
      label: "75% (9/12 columns)"
    - value: "66"
      label: "66% (8/12 columns)"
    - value: "50"
      label: "50% (6/12 columns)"
    - value: "33"
      label: "33% (4/12 columns)"
    - value: "25"
      label: "25% (3/12 columns)"
    - value: "16"
      label: "16% (2/12 columns)"
    - value: fit
      label: "Fit Content"
```

---

## Part 2: Component-by-Component Analysis

### A. TEXT COMPONENTS (heading, paragraph, eyebrow, caption, blockquote, link)

#### Current Implementation
- **Method:** Inline styles via `build_styles()` macro
- **File:** `_components.html` lines 1289-1326
- **Responsive:** No (same width at all viewports)

#### Current CSS Output

**Column Context (parent is layout-column):**
| widthMode | CSS |
|-----------|-----|
| fit | `width: auto;` |
| 25 | `width: 25%;` |
| 50 | `width: 50%;` |
| 75 | `width: 75%;` |
| stretch | `width: 100%;` |

**Row Context (parent is layout-row):**
| widthMode | CSS |
|-----------|-----|
| fit | `width: auto; flex: 0 0 auto;` |
| 25 | `flex: 1 0 23%; max-width: 25%;` |
| 50 | `flex: 1 0 48%; max-width: 50%;` |
| 75 | `flex: 1 0 73%; max-width: 75%;` |
| stretch | `flex: 1 0 100%;` |

#### Changes Needed

**1. Add missing width values (16, 33, 66, 83):**

| widthMode | Column Context | Row Context |
|-----------|---------------|-------------|
| 16 | `width: 16.67%;` | `flex: 1 0 14%; max-width: 16.67%;` |
| 33 | `width: 33.33%;` | `flex: 1 0 31%; max-width: 33.33%;` |
| 66 | `width: 66.67%;` | `flex: 1 0 64%; max-width: 66.67%;` |
| 83 | `width: 83.33%;` | `flex: 1 0 81%; max-width: 83.33%;` |

**2. Update schemas to use `tokens: widthPercentages`**

---

### B. LINK COMPONENT

#### Current State
- **NO widthMode in schema** (component_schemas.yaml lines 2092-2166)
- Always renders at default `stretch` (100% width)
- Macro does check for widthMode in `build_styles()`, but schema doesn't expose it

#### Changes Needed
1. Add layout group to schema with widthMode using `tokens: widthPercentages`
2. No template changes needed (already handled by build_styles)

---

### C. LAYOUT-COLUMN COMPONENT

#### Current Implementation
- **Method:** CSS via `data-width-mode` attribute
- **File:** `components.css` lines 59-106
- **Template:** `_components.html` lines 207-238
- **Uses:** `--margin-inline` CSS variable for margin-aware calculations

#### Current CSS (components.css)
```css
.layout-column[data-width-mode="50"] {
    flex: 0 0 calc(50% - var(--margin-inline, 0px) * 2);
    max-width: calc(50% - var(--margin-inline, 0px) * 2);
}
```

#### Problem
- Uses `flex: 0 0` (no grow, no shrink) which behaves differently than text
- Text uses `flex: 1 0` (can grow, no shrink)

#### Changes Needed
1. Move width handling to inline styles in `build_styles()` macro
2. Match text component behavior exactly
3. Remove CSS-based width handling from `components.css`
4. Keep `--margin-inline` calculation if margins are needed

---

### D. IMAGE COMPONENT

#### Current Implementation
- **Method:** CSS via `data-width-mode` attribute with RESPONSIVE breakpoints
- **File:** `components.css` lines 1380-1486
- **Template:** `_components.html` lines 457-478 (outputs `data-width-mode`)

#### Current Responsive CSS Behavior

| widthMode | Mobile (≤480px) | Tablet (481-768px) | Desktop (769px+) |
|-----------|-----------------|-------------------|------------------|
| fit | auto | auto | auto |
| 25 | 100% | 50% | 25% |
| 50 | 100% | 50% | 50% |
| 75 | 100% | 100% | 75% |
| stretch | 100% | 100% | 100% |

#### Problem
This responsive behavior is DIFFERENT from text components, which maintain their width at all viewports.

#### Changes Needed

**1. Remove responsive CSS behavior**
- Delete responsive media queries in `components.css` (lines 1397-1456)

**2. Move to inline styles matching text component:**

**Column Context:**
| widthMode | CSS |
|-----------|-----|
| fit | `width: auto;` |
| 16 | `width: 16.67%;` |
| 25 | `width: 25%;` |
| 33 | `width: 33.33%;` |
| 50 | `width: 50%;` |
| 66 | `width: 66.67%;` |
| 75 | `width: 75%;` |
| 83 | `width: 83.33%;` |
| stretch | `width: 100%;` |

**Row Context:**
| widthMode | CSS |
|-----------|-----|
| fit | `width: auto; flex: 0 0 auto;` |
| 16 | `flex: 1 0 14%; max-width: 16.67%;` |
| 25 | `flex: 1 0 23%; max-width: 25%;` |
| 33 | `flex: 1 0 31%; max-width: 33.33%;` |
| 50 | `flex: 1 0 48%; max-width: 50%;` |
| 66 | `flex: 1 0 64%; max-width: 66.67%;` |
| 75 | `flex: 1 0 73%; max-width: 75%;` |
| 83 | `flex: 1 0 81%; max-width: 83.33%;` |
| stretch | `flex: 1 0 100%;` |

**3. Update template to generate inline styles instead of relying on CSS**

---

### E. GIF COMPONENT

#### Current Implementation
Identical to image component - uses CSS via `data-width-mode` with responsive breakpoints.

#### Changes Needed
Same as image component - move to inline styles matching text component behavior.

---

### F. VIDEO COMPONENT

#### Current State
- **NO widthMode** - always renders at 100% width
- Uses `aspect-ratio` CSS for height proportions
- Embeds iframe that fills container

#### Decision Required
**Option 1:** Keep at 100% (videos typically fill container)
**Option 2:** Add widthMode support

**Recommendation:** Keep at 100% width. Videos are typically meant to fill their container, and adding width control could cause usability issues with video player controls.

---

### G. CAROUSEL COMPONENT

#### Current State
- **NO widthMode** - always renders at 100% width
- Contains slides that are each 100% width

#### Decision Required
Same as video - keep at 100% width is recommended since carousels are typically full-width containers.

---

### H. VIDEO-BACKGROUND COMPONENT

#### Current State
- **Has widthMode in schema** (line 2414)
- **NOT implemented in template** - always renders at 100%
- Schema is misleading (suggests width control but does nothing)

#### Changes Needed
**Option 1:** Implement widthMode to match text behavior
**Option 2:** Remove widthMode from schema (if 100% is intended)

**Recommendation:** Option 2 - Remove from schema. Video backgrounds are typically meant to span full width.

---

### I. TABS COMPONENT

#### Current State
- Has widthMode with label "**Width Mode**" (inconsistent)
- Uses inline options instead of `tokens: widthPercentages`

#### Changes Needed
1. Change label from "Width Mode" to "Width"
2. Change from inline options to `tokens: widthPercentages`

---

### J. ACCORDION COMPONENT

#### Current State
- Has widthMode with correct label "Width"
- Uses inline options instead of `tokens: widthPercentages`
- Missing 16, 33, 66, 83 values

#### Changes Needed
1. Change from inline options to `tokens: widthPercentages`

---

## Part 3: Detailed Implementation Plan

### Task 1: Update Schema Tokens (if needed)

**File:** `schema_tokens.yaml`

The `widthPercentages` token already has all values (fit, 16, 25, 33, 50, 66, 75, 83, stretch). No changes needed.

---

### Task 2: Update Text Component Schemas

**File:** `component_schemas.yaml`

**Components:** heading, paragraph, eyebrow, caption, blockquote

**Change for each component:**

FROM (inline options):
```yaml
- path: layout.widthMode
  type: select
  label: Width
  options:
  - value: fit
    label: Fit to content
  - value: '25'
    label: 25%
  - value: '50'
    label: 50%
  - value: '75'
    label: 75%
  - value: stretch
    label: Stretch
```

TO (token reference):
```yaml
- path: layout.widthMode
  type: select
  label: Width
  tokens: widthPercentages
```

**Schema locations:**
- heading: line 555
- paragraph: line 681
- eyebrow: line 807
- caption: line 936
- blockquote: line 1065

---

### Task 3: Add Layout Group to Link Schema

**File:** `component_schemas.yaml`
**Location:** After line 2155 (before spacing group)

**Add:**
```yaml
  - id: layout
    label: Layout
    fields:
    - path: layout.widthMode
      type: select
      label: Width
      tokens: widthPercentages
```

---

### Task 4: Fix Tabs Schema Label

**File:** `component_schemas.yaml`
**Location:** Line 1935

**Change:**
```yaml
# FROM:
label: Width Mode

# TO:
label: Width
```

Also change from inline options to token reference:
```yaml
# FROM:
options:
- value: fit
  label: Fit to content
...

# TO:
tokens: widthPercentages
```

---

### Task 5: Update Accordion Schema

**File:** `component_schemas.yaml`
**Location:** Line 1965-1977

**Change from inline options to token reference:**
```yaml
# FROM:
options:
- value: fit
  label: Fit to content
...

# TO:
tokens: widthPercentages
```

---

### Task 6: Fix Video-Background Schema

**File:** `component_schemas.yaml`
**Location:** Lines 2411-2426

**Option A (Remove widthMode):**
Delete the entire layout group since it's not implemented.

**Option B (Implement widthMode):**
Keep schema, implement in template. (Not recommended for video backgrounds)

**Recommended: Option A**

---

### Task 7: Add Missing Width Values to Template

**File:** `ssr_python/templates/macros/_components.html`
**Location:** Lines 1295-1326 (build_styles macro)

**Add to Column Context (after line 1307):**
```jinja2
{% elif width_mode == '16' %}
    {% set _ = styles.append('width: 16.67%;') %}
{% elif width_mode == '33' %}
    {% set _ = styles.append('width: 33.33%;') %}
{% elif width_mode == '66' %}
    {% set _ = styles.append('width: 66.67%;') %}
{% elif width_mode == '83' %}
    {% set _ = styles.append('width: 83.33%;') %}
```

**Add to Row Context (after line 1321):**
```jinja2
{% elif width_mode == '16' %}
    {% set _ = styles.append('flex: 1 0 14%;') %}
    {% set _ = styles.append('max-width: 16.67%;') %}
{% elif width_mode == '33' %}
    {% set _ = styles.append('flex: 1 0 31%;') %}
    {% set _ = styles.append('max-width: 33.33%;') %}
{% elif width_mode == '66' %}
    {% set _ = styles.append('flex: 1 0 64%;') %}
    {% set _ = styles.append('max-width: 66.67%;') %}
{% elif width_mode == '83' %}
    {% set _ = styles.append('flex: 1 0 81%;') %}
    {% set _ = styles.append('max-width: 83.33%;') %}
```

---

### Task 8: Update Image/GIF Width Handling in Template

**File:** `ssr_python/templates/macros/_components.html`
**Location:** Lines 1328-1334

**Replace current code with:**
```jinja2
{# Width Mode Support for Image/GIF - Match Text Component Behavior #}
{% if component.name in ['image', 'gif'] %}
    {% set width_mode = props.layout.widthMode | default('stretch') if props.layout else 'stretch' %}
    {% set _ = styles.append('display: block;') %}
    {% set _ = styles.append('box-sizing: border-box;') %}

    {% if layout_direction == 'column' %}
        {# Column context: use explicit width percentages #}
        {% if width_mode == 'fit' %}
            {% set _ = styles.append('width: auto;') %}
        {% elif width_mode == '16' %}
            {% set _ = styles.append('width: 16.67%;') %}
        {% elif width_mode == '25' %}
            {% set _ = styles.append('width: 25%;') %}
        {% elif width_mode == '33' %}
            {% set _ = styles.append('width: 33.33%;') %}
        {% elif width_mode == '50' %}
            {% set _ = styles.append('width: 50%;') %}
        {% elif width_mode == '66' %}
            {% set _ = styles.append('width: 66.67%;') %}
        {% elif width_mode == '75' %}
            {% set _ = styles.append('width: 75%;') %}
        {% elif width_mode == '83' %}
            {% set _ = styles.append('width: 83.33%;') %}
        {% elif width_mode == 'stretch' %}
            {% set _ = styles.append('width: 100%;') %}
        {% endif %}
    {% else %}
        {# Row context: use flex-basis percentages for wrapping support #}
        {% if width_mode == 'fit' %}
            {% set _ = styles.append('width: auto;') %}
            {% set _ = styles.append('flex: 0 0 auto;') %}
        {% elif width_mode == '16' %}
            {% set _ = styles.append('flex: 1 0 14%;') %}
            {% set _ = styles.append('max-width: 16.67%;') %}
        {% elif width_mode == '25' %}
            {% set _ = styles.append('flex: 1 0 23%;') %}
            {% set _ = styles.append('max-width: 25%;') %}
        {% elif width_mode == '33' %}
            {% set _ = styles.append('flex: 1 0 31%;') %}
            {% set _ = styles.append('max-width: 33.33%;') %}
        {% elif width_mode == '50' %}
            {% set _ = styles.append('flex: 1 0 48%;') %}
            {% set _ = styles.append('max-width: 50%;') %}
        {% elif width_mode == '66' %}
            {% set _ = styles.append('flex: 1 0 64%;') %}
            {% set _ = styles.append('max-width: 66.67%;') %}
        {% elif width_mode == '75' %}
            {% set _ = styles.append('flex: 1 0 73%;') %}
            {% set _ = styles.append('max-width: 75%;') %}
        {% elif width_mode == '83' %}
            {% set _ = styles.append('flex: 1 0 81%;') %}
            {% set _ = styles.append('max-width: 83.33%;') %}
        {% elif width_mode == 'stretch' %}
            {% set _ = styles.append('flex: 1 0 100%;') %}
        {% endif %}
    {% endif %}
{% endif %}
```

---

### Task 9: Update Layout-Column Width Handling in Template

**File:** `ssr_python/templates/macros/_components.html`

**Add to `build_styles` macro (after image/gif handling):**
```jinja2
{# Width Mode Support for Layout-Column - Match Text Component Behavior #}
{% if component.name == 'layout-column' %}
    {% set width_mode = props.layout.widthMode | default('stretch') if props.layout else 'stretch' %}
    {% set _ = styles.append('box-sizing: border-box;') %}

    {% if layout_direction == 'column' %}
        {# Column context: use explicit width percentages #}
        {% if width_mode == 'fit' %}
            {% set _ = styles.append('width: auto;') %}
        {% elif width_mode == '16' %}
            {% set _ = styles.append('width: 16.67%;') %}
        {% elif width_mode == '25' %}
            {% set _ = styles.append('width: 25%;') %}
        {% elif width_mode == '33' %}
            {% set _ = styles.append('width: 33.33%;') %}
        {% elif width_mode == '50' %}
            {% set _ = styles.append('width: 50%;') %}
        {% elif width_mode == '66' %}
            {% set _ = styles.append('width: 66.67%;') %}
        {% elif width_mode == '75' %}
            {% set _ = styles.append('width: 75%;') %}
        {% elif width_mode == '83' %}
            {% set _ = styles.append('width: 83.33%;') %}
        {% elif width_mode == 'stretch' %}
            {% set _ = styles.append('width: 100%;') %}
        {% endif %}
    {% else %}
        {# Row context: use flex-basis percentages for wrapping support #}
        {% if width_mode == 'fit' %}
            {% set _ = styles.append('flex: 0 0 auto;') %}
        {% elif width_mode == '16' %}
            {% set _ = styles.append('flex: 1 0 14%;') %}
            {% set _ = styles.append('max-width: 16.67%;') %}
        {% elif width_mode == '25' %}
            {% set _ = styles.append('flex: 1 0 23%;') %}
            {% set _ = styles.append('max-width: 25%;') %}
        {% elif width_mode == '33' %}
            {% set _ = styles.append('flex: 1 0 31%;') %}
            {% set _ = styles.append('max-width: 33.33%;') %}
        {% elif width_mode == '50' %}
            {% set _ = styles.append('flex: 1 0 48%;') %}
            {% set _ = styles.append('max-width: 50%;') %}
        {% elif width_mode == '66' %}
            {% set _ = styles.append('flex: 1 0 64%;') %}
            {% set _ = styles.append('max-width: 66.67%;') %}
        {% elif width_mode == '75' %}
            {% set _ = styles.append('flex: 1 0 73%;') %}
            {% set _ = styles.append('max-width: 75%;') %}
        {% elif width_mode == '83' %}
            {% set _ = styles.append('flex: 1 0 81%;') %}
            {% set _ = styles.append('max-width: 83.33%;') %}
        {% elif width_mode == 'stretch' %}
            {% set _ = styles.append('flex: 1 0 100%;') %}
        {% endif %}
    {% endif %}
{% endif %}
```

---

### Task 10: Remove/Simplify CSS Width Rules

**File:** `ssr_python/static/css/components.css`

**1. Remove Layout-Column CSS Width Rules (lines 59-106):**
- Delete or comment out `.layout-column[data-width-mode]` rules
- Inline styles will now take precedence

**2. Remove Responsive Image/GIF Width Rules (lines 1380-1486):**
- Delete responsive media queries for image/gif widths
- Keep base `.image-container` and `.gif-container` styles
- Inline styles will now take precedence

---

## Part 4: Files Summary

| File | Changes |
|------|---------|
| `component_schemas.yaml` | Update 10+ components to use `tokens: widthPercentages`, add layout to link, fix tabs label |
| `ssr_python/templates/macros/_components.html` | Add 16/33/66/83 values, add image/gif/layout-column inline styles |
| `ssr_python/static/css/components.css` | Remove layout-column and image/gif CSS width rules |

---

## Part 5: Width Value Reference

### Complete Width Mode CSS Output

| widthMode | % Value | Column CSS | Row CSS (flex-basis / max-width) |
|-----------|---------|-----------|-----------------------------------|
| fit | auto | `width: auto` | `flex: 0 0 auto` |
| 16 | 16.67% | `width: 16.67%` | `flex: 1 0 14%; max-width: 16.67%` |
| 25 | 25% | `width: 25%` | `flex: 1 0 23%; max-width: 25%` |
| 33 | 33.33% | `width: 33.33%` | `flex: 1 0 31%; max-width: 33.33%` |
| 50 | 50% | `width: 50%` | `flex: 1 0 48%; max-width: 50%` |
| 66 | 66.67% | `width: 66.67%` | `flex: 1 0 64%; max-width: 66.67%` |
| 75 | 75% | `width: 75%` | `flex: 1 0 73%; max-width: 75%` |
| 83 | 83.33% | `width: 83.33%` | `flex: 1 0 81%; max-width: 83.33%` |
| stretch | 100% | `width: 100%` | `flex: 1 0 100%` |

### Flex-Basis Offset Explanation

Row context uses offset percentages (14%, 23%, 31%, etc.) instead of exact values to ensure proper wrapping behavior:
- Two 50% items: `48% + 48% = 96%` fills the row, allowing wrap to trigger if needed
- The `max-width` property ensures items don't exceed their target size

---

## Part 6: Verification Steps

1. **Start server:** `cd ssr_python && python app.py`

2. **Test all width values for each component type:**
   - fit, 16%, 25%, 33%, 50%, 66%, 75%, 83%, stretch
   - Verify visual width matches expected percentage

3. **Test wrap behavior:**
   - `wrap: nowrap` + two 50% items → squeeze into single line
   - `wrap: wrap` + two 50% items → wrap to separate lines

4. **Test link component:**
   - Verify widthMode appears in properties panel
   - Test width values

5. **Test images/gifs:**
   - Verify width matches text behavior (no responsive changes)
   - Test in both layout-row and layout-column contexts

6. **Test layout-column:**
   - Verify width matches text behavior
   - Test nested layouts

7. **Verify removed responsive behavior:**
   - Check images at different viewport sizes
   - Should maintain set width at all viewports (unlike before)

---

## Part 7: Components NOT Getting widthMode

The following components will intentionally NOT have widthMode and will remain at 100% width:

| Component | Reason |
|-----------|--------|
| video | Video players typically fill container; width control could break player UI |
| carousel | Carousels are full-width containers with slides that need 100% width |
| video-background | Video backgrounds span full width by design |

---

## Part 8: Schema Changes Summary

| Component | Current State | Target State |
|-----------|--------------|--------------|
| heading | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| paragraph | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| eyebrow | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| caption | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| blockquote | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| link | MISSING | Add layout group with `tokens: widthPercentages` |
| tabs | inline options, label "Width Mode" | `tokens: widthPercentages`, label "Width" |
| accordion | inline options (5 values) | `tokens: widthPercentages` (9 values) |
| image | already uses token | No change needed |
| gif | already uses token | No change needed |
| layout-column | already uses token | No change needed |
| video-background | inline options (5 values) | REMOVE widthMode (not implemented) |
