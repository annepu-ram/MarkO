#0>6++965+ CSS Conflicts and Variable Mapping Audit

**Date:** January 5, 2026  
**Issue:** CSS specificity conflicts preventing properties panel updates from working

---

## Summary

During debugging of the titlebar component properties not updating, we discovered **CSS specificity conflicts** where global `.preview-area` rules were overriding component-specific styles. This document audits all components for similar issues.

---

## Root Causes Identified

### 1. Global Preview Area Styles (style.css)

The `.preview-area` container has several global element selectors that can override component-specific styles:

```css
/* ssr_python/static/css/style.css */

.preview-area a {
    color: #3b82f6;           /* Specificity: 0,1,1 */
    text-decoration: none;
}

.preview-area h1,
.preview-area h2,
.preview-area h3,
.preview-area h4,
.preview-area h5,
.preview-area h6 {
    margin: 0;                /* Specificity: 0,1,1 */
    font-weight: 600;
    line-height: 1.2;
}

.preview-area p {
    margin: 0;                /* Specificity: 0,1,1 */
}
```

### 2. Duplicate Component-Specific Rules (components.css)

Some components have duplicate CSS rules with conflicting specificity:

```css
/* ssr_python/static/css/components.css */

/* Lower specificity - uses CSS variables */
.titlebar-title {
    font-size: var(--title-font-size, 1.5rem);    /* Specificity: 0,1,0 */
    font-weight: var(--title-font-weight, 700);
    color: var(--titlebar-title-color, inherit);
}

/* Higher specificity - hardcoded values (CONFLICT!) */
.titlebar-branding .titlebar-title {
    font-size: 1.25rem;                           /* Specificity: 0,2,0 - WINS! */
    font-weight: 600;
    margin: 0;
}
```

---

## Components Analysis

### ✅ Text Components (NO CONFLICTS)

**Components:** `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`

**Styling Method:** Inline styles via `build_styles()` macro

**Potential Conflicts:** 
- `.preview-area h1, h2, h3, h4, h5, h6` sets `margin`, `font-weight`, `line-height`
- `.preview-area p` sets `margin`

**Risk Level:** **LOW** ⚠️
- Inline styles have highest specificity (1,0,0,0) and override all CSS rules
- The global rules only affect properties NOT set inline (margin, line-height)
- Typography properties (size, weight, color) are set inline and work correctly

**Status:** ✅ Working as expected

---

### ✅ Layout Components (NO CONFLICTS)

**Components:** `page`, `layout-row`, `layout-column`, `columnsgrid`, `form`

**Styling Method:** Inline styles via `build_styles()` macro

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

### ⚠️ Titlebar Component (FIXED)

**Component:** `titlebar`

**Styling Method:** CSS variables

**Conflicts Found:**
1. **.titlebar-branding .titlebar-title** overriding CSS variables (title size, title weight)
2. **.preview-area a** overriding `.titlebar-link` color (menu color)

**Fixes Applied:**
1. Removed hardcoded `font-size` and `font-weight` from `.titlebar-branding .titlebar-title`
2. Increased specificity of `.titlebar-link` to `.titlebar-nav .titlebar-link`

**Status:** ✅ FIXED

---

### ⚠️ Link Component (POTENTIAL MINOR ISSUE)

**Component:** `link`

**Styling Method:** Inline styles via `build_styles()` + class-based underline styling

**Potential Conflicts:**
- `.preview-area a` (specificity: 0,1,1) sets `color: #3b82f6`
- `a.link` (specificity: 0,1,1) sets `color: #3b82f6`

**Risk Level:** **VERY LOW** ⚠️
- Link component uses inline styles for typography (color, size, weight)
- Inline styles have highest specificity and override both rules
- The CSS rules only apply if no inline color is set

**Recommendation:** No action needed - inline styles take precedence

**Status:** ✅ Working as expected

---

### ✅ Button Component (NO CONFLICTS)

**Component:** `button`

**Styling Method:** Inline styles via `build_styles()` + `.btn` class

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

### ⚠️ Tabs Component (NEEDS VERIFICATION)

**Component:** `tabs`

**Styling Method:** CSS variables

**CSS Variables Generated:**
- `--tabs-gap`, `--tabs-margin-block`, `--tabs-margin-inline`
- `--tabs-label-font-size`, `--tabs-label-font-weight`
- `--tabs-label-color-inactive`, `--tabs-label-color-active`
- `--tabs-label-bg-active`, `--tabs-label-bg-inactive`
- `--tabs-border-width`, `--tabs-border-style`
- `--tabs-content-bg`, `--tabs-content-border-*`, `--tabs-content-padding-*`

**Potential Conflicts:** None found in global styles

**Risk Level:** **LOW** ⚠️
- No global `.preview-area` rules affect tabs
- All styling is component-scoped

**Recommendation:** Test tabs typography properties to ensure they update correctly

**Status:** ⚠️ Needs verification

---

### ⚠️ Accordion Component (NEEDS VERIFICATION)

**Component:** `accordion`

**Styling Method:** CSS variables

**CSS Variables Generated:**
- `--accordion-gap`, `--accordion-margin-block`, `--accordion-margin-inline`
- `--accordion-border-radius`
- `--accordion-title-font-size`, `--accordion-title-font-weight`, `--accordion-title-color`
- `--accordion-title-bg`, `--accordion-title-padding-*`
- `--accordion-border-width`, `--accordion-border-style`, `--accordion-border-color`
- `--accordion-content-font-size`, `--accordion-content-font-weight`, `--accordion-content-color`
- `--accordion-content-bg`, `--accordion-content-padding-*`

**Potential Conflicts:** None found in global styles

**Risk Level:** **LOW** ⚠️
- No global `.preview-area` rules affect accordion
- All styling is component-scoped

**Recommendation:** Test accordion typography properties to ensure they update correctly

**Status:** ⚠️ Needs verification

---

### ✅ Form Input Components (NO CONFLICTS)

**Components:** `textbox`, `textarea`, `dropdown`, `checkbox`, `radio`, `calendar`

**Styling Method:** Inline styles via `build_styles()`

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

### ✅ Media Components (NO CONFLICTS)

**Components:** `image`, `video`, `gif`

**Styling Method:** Inline styles via `build_styles()`

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

### ✅ Carousel Component (NO CONFLICTS)

**Component:** `carousel`

**Styling Method:** Inline styles via `build_styles()`

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

### ✅ Hamburger Component (NO CONFLICTS)

**Component:** `hamburger`

**Styling Method:** Inline styles via `build_styles()`

**Potential Conflicts:** None found

**Risk Level:** **NONE** ✅

**Status:** ✅ Working as expected

---

## Recommendations

### Immediate Actions (Completed)

1. ✅ **Titlebar Title Styles:** Removed duplicate hardcoded styles from `.titlebar-branding .titlebar-title`
2. ✅ **Titlebar Link Color:** Increased specificity of `.titlebar-link` to `.titlebar-nav .titlebar-link`

### Future Testing

1. ⚠️ **Test Tabs Component:** Verify title/label typography properties update correctly
2. ⚠️ **Test Accordion Component:** Verify title and content typography properties update correctly

### Best Practices Going Forward

1. **Avoid Global Element Selectors:** Don't add new rules like `.preview-area h1` or `.preview-area a`
2. **Consistent Specificity:** When using CSS variables, ensure the selector specificity is higher than any potential conflicts
3. **Prefer Inline Styles:** For properties that should be customizable via properties panel, use inline styles (highest specificity)
4. **Document CSS Variables:** When adding new CSS variable-based components, document the variables and their usage
5. **Audit on Component Addition:** When adding new components, check for global selector conflicts

---

## CSS Specificity Reference

Understanding CSS specificity (in order from lowest to highest):

1. **Element selectors:** `p { }` → (0,0,1)
2. **Class selectors:** `.class { }` → (0,1,0)
3. **Multiple classes/descendant:** `.preview-area a { }` → (0,1,1)
4. **Increased specificity:** `.titlebar-nav .titlebar-link { }` → (0,2,0)
5. **ID selectors:** `#id { }` → (1,0,0)
6. **Inline styles:** `style="color: red"` → (1,0,0,0) **HIGHEST**
7. **!important:** Overrides everything (avoid using)

**Rule of Thumb:** Inline styles always win (except against `!important`), which is why most components use inline styles via `build_styles()`.

---

## Files Modified

1. `ssr_python/static/css/components.css`
   - Lines 876-880: Removed hardcoded `font-size` and `font-weight` from `.titlebar-branding .titlebar-title`
   - Line 372: Changed `.titlebar-link` to `.titlebar-nav .titlebar-link`
   - Line 382: Changed `.titlebar-link:hover` to `.titlebar-nav .titlebar-link:hover`
   - Line 460: Changed `.titlebar.scrolled .titlebar-link` to `.titlebar.scrolled .titlebar-nav .titlebar-link`

---

## Conclusion

The titlebar component CSS conflicts have been resolved. Most other components use inline styles and are not affected by global CSS rules. Tabs and Accordion components should be tested to ensure their CSS variable-based styling works correctly, though no conflicts were found in the audit.

**Overall Status:** ✅ Critical issues fixed, minor verification recommended

