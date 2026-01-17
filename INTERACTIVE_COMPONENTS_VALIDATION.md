# Interactive Components Validation

## Date: 2026-01-03
## Status: IN PROGRESS

---

## 1. Titlebar Component

### Requirements:
1.  **Left Alignment (Default):**
    *   Layout: `[Brand (Logo + Title)]` -------- `[Links]`
    *   Brand order: Logo then Title.
2.  **Right Alignment:**
    *   Layout: `[Links]` -------- `[Brand (Title + Logo)]`
    *   Brand order: Title then Logo.
3.  **Center Alignment:**
    *   Layout:
        ```
           [Title] [Logo]
              [Links]
        ```
    *   Brand order: Title then Logo.

### Current Implementation Status:
*   ❌ **Left:** Default works, but explicit alignment support needed.
*   ❌ **Right:** Not implemented (Branding is on left, Links on right).
*   ❌ **Center:** Not implemented (No stacked layout).

### Planned Fixes:
*   Update `render_titlebar` macro to apply alignment classes.
*   Update CSS to handle `flex-direction` and ordering based on alignment classes.

---

## 2. Carousel Component

### Requirements:
1.  **Auto-scrolling:** Slides should move automatically after delay.
2.  **Manual Navigation:** Next/Prev buttons and Dots should work.
3.  **Animation:** Smooth sliding transition.
4.  **Content:** Support nested components (images, text, etc.).

### Current Implementation Status:
*   ✅ **Structure:** Renders slides and controls.
*   ❌ **Animation:** CSS `display: none` on inactive slides breaks sliding transform animation.
*   ⚠️ **Auto-scroll:** JS exists but needs verification with fixed CSS.

### Planned Fixes:
*   Fix CSS: Remove `display: none` from slides, ensure flex layout for sliding.
*   Verify JS initialization.

---

## 3. Tabs Component

### Requirements:
1.  **Switching:** Clicking tabs switches content.
2.  **Orientation:** Horizontal vs Vertical.
3.  **Content:** Support nested components.

### Current Implementation Status:
*   ✅ **Structure:** Uses radio button hack for CSS-only switching (or JS?).
*   *Note:* CSR uses JS. SSR template uses radio inputs which suggests CSS-only fallback or hybrid.
*   *Check:* `initializeTabs`? `render_tabs` uses radio inputs.

### Planned Fixes:
*   Ensure CSS/JS works for switching.

---

## 4. Accordion Component

### Requirements:
1.  **Expansion:** Clicking header expands/collapses content.
2.  **Multiple Items:** Support lists of items.
3.  **Content:** Support nested components.

### Current Implementation Status:
*   ✅ **Structure:** Renders summary and details/content.
*   *Check:* `initializeAccordion` in JS.

### Planned Fixes:
*   Verify interaction works.

---

