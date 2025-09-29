# Sidebar Resizer Implementation Plan

## 1. Problem Statement
The application currently has a fixed-width left sidebar. Users require the ability to dynamically resize this sidebar horizontally to adjust the space allocated to components/properties versus the main editor/preview area. The previous attempt to implement this caused a critical UI rendering issue where the editor and preview were incorrectly displayed within the sidebar.

## 2. Goal
To implement a functional and persistent horizontal resizer for the left sidebar, allowing users to adjust its width. The implementation must maintain the correct application layout (sidebar on the left, main content area on the right) and ensure the resizer's state (sidebar width) persists across sessions.

## 3. Root Cause of Previous Failure
The previous attempt failed because changing the `.app-container` from `display: grid` to `display: flex` without properly configuring the flex items (`sidebar`, `sidebar-resizer`, `main-canvas`) broke the intended two-column layout. The `grid` layout is more suitable for defining distinct areas with flexible sizing.

## 4. Proposed Solution (Revised Approach)
Leverage CSS Grid for the main application layout and use CSS Custom Properties (CSS Variables) to dynamically control the sidebar's width. This CSS variable will be updated via JavaScript based on user interaction with the resizer handle.

## 5. Detailed Plan

### 5.1. HTML Modifications (`index.html`)

*   **Locate:** The `<div class="sidebar">` and `<div class="main-canvas">` elements.
*   **Insert Resizer:** Place a new `div` element for the resizer handle *between* the `sidebar` and `main-canvas` divs.
    ```html
            <div class="sidebar">
                <!-- ... sidebar content ... -->
            </div>

            <!-- Sidebar Resizer Handle -->
            <div class="sidebar-resizer" id="sidebarResizer"></div>

            <div class="main-canvas">
                <!-- ... main canvas content ... -->
            </div>
    ```

### 5.2. CSS Modifications (`css/style.css`)

*   **`.app-container`:**
    *   Ensure `display: grid;` is maintained.
    *   Modify `grid-template-columns` to define three columns: one for the sidebar (using a CSS variable), one for the resizer handle (fixed width), and one for the main content area (`1fr`).
        ```css
        .app-container {
            display: grid;
            grid-template-columns: var(--sidebar-width, 250px) 8px 1fr; /* sidebar, resizer, main-canvas */
            height: 100vh;
            gap: 0; /* Ensure no gap between grid items */
        }
        /* Adjust for help-visible state if necessary */
        .app-container.help-visible {
            grid-template-columns: var(--sidebar-width, 250px) 8px 1fr 350px; /* sidebar, resizer, main-canvas, help-panel */
        }
        ```
*   **`.sidebar`:**
    *   Remove any fixed `width` or `flex-basis` properties. Its width will now be implicitly set by the `grid-template-columns` property on `.app-container`.
    *   Ensure `overflow: hidden;` is present to prevent content overflow during resizing.
*   **`.sidebar-resizer`:**
    *   Define visual styles for the resizer handle to make it visible and interactive.
    *   Set `cursor: ew-resize;` to provide appropriate visual feedback for horizontal resizing.
    *   Ensure it occupies its own grid column (e.g., `8px` as defined in `grid-template-columns`).
    ```css
        .sidebar-resizer {
            background-color: var(--accent-color-light); /* A visible color for the handle */
            cursor: ew-resize;
            position: relative;
            z-index: 10; /* Ensure it's above other content */
        }
        .sidebar-resizer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            height: 100%;
            width: 2px; /* A thin line indicator for better visibility */
            background-color: var(--primary-color); /* Contrast with resizer background */
        }
    ```

### 5.3. JavaScript Modifications (`js/ui/events.js`, `js/core/app.js`)

*   **`js/core/app.js` (`getDomReferences`):**
    *   Add references to the `sidebar` and `sidebarResizer` elements to the `dom` object returned by this function.
        ```javascript
        function getDomReferences() {
            // ... existing references ...
            sidebar: document.querySelector('.sidebar'), // Assuming .sidebar is the class for the sidebar
            sidebarResizer: document.getElementById('sidebarResizer'),
            // ...
        }
        ```
*   **`js/ui/events.js` (`initializeEvents`):**
    *   Retrieve `sidebar` and `sidebarResizer` from the `dom` object.
    *   Call a new `initializeSidebarResizer` function, passing these elements.
        ```javascript
        export function initializeEvents(dom, actions) {
            const {
                // ... existing dom elements ...
                sidebar,
                sidebarResizer,
            } = dom;

            // ... existing event listeners ...

            if (sidebarResizer && sidebar) {
                initializeSidebarResizer(sidebarResizer, sidebar);
            }
        }
        ```
*   **`js/ui/events.js` (`initializeSidebarResizer` - New Function):**
    *   **Function Signature:** `function initializeSidebarResizer(sidebarResizer, sidebar)`
    *   **Internal State:** `let isResizing = false;`, `let initialX;`, `let initialWidth;`.
    *   **Constraints:** Define `minWidth` (e.g., `150`) and `maxWidth` (e.g., `500`) constants for the sidebar.
    *   **Persistence:**
        *   On application load, retrieve the last saved `sidebarWidth` from `localStorage`. If found, apply it by setting the `--sidebar-width` CSS custom property on the `document.documentElement` (or a suitable parent container like `appContainer`).
        *   On `mouseup` (end of drag), save the final `sidebar.offsetWidth` to `localStorage`.
    *   **Event Listeners:**
        *   `sidebarResizer.addEventListener('mousedown', startResizing)`:
            *   Prevent default event behavior (`e.preventDefault()`).
            *   Set `isResizing = true`.
            *   Record `initialX = e.clientX`.
            *   Record `initialWidth = sidebar.offsetWidth`.
            *   Add `mousemove` and `mouseup` listeners to `document` (or `window`) to ensure dragging works even if the mouse leaves the resizer.
            *   Set `document.body.style.cursor = 'ew-resize';` for global visual feedback.
            *   Temporarily disable text selection (`user-select: none;`) on `sidebar` and `main-canvas` (or `document.body`) during resize to prevent accidental text highlighting.
            *   Temporarily disable pointer events on `sidebar` and `main-canvas` to prevent interaction with content during resize.
        *   `document.addEventListener('mousemove', resize)`:
            *   If `isResizing` is true, calculate `dx = e.clientX - initialX`.
            *   Calculate `newWidth = initialWidth + dx`.
            *   Clamp `newWidth` between `minWidth` and `maxWidth`.
            *   Update the `document.documentElement`'s (or `appContainer`'s) `--sidebar-width` CSS custom property: `document.documentElement.style.setProperty('--sidebar-width', `${newWidth}px`);`.
        *   `document.addEventListener('mouseup', stopResizing)`:
            *   Set `isResizing = false`.
            *   Remove `mousemove` and `mouseup` listeners.
            *   Reset `document.body.style.cursor`.
            *   Re-enable text selection and pointer events.
            *   Save `sidebar.offsetWidth` to `localStorage`.

## 6. Testing
*   Verify the initial application layout is correct (sidebar on left, main content on right).
*   Drag the resizer handle horizontally to change the sidebar width.
*   Ensure the main content area (`main-canvas`) adjusts its width correctly in response.
*   Check that the sidebar width respects the defined `minWidth` and `maxWidth` constraints.
*   Reload the page and confirm the sidebar retains its last set width.
*   Ensure the editor resizer (vertical) still functions correctly without interference.
