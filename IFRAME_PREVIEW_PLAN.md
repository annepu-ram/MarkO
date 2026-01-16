# Iframe Preview Migration Plan

## Problem

The preview window shares the same document as the application UI. This causes:
1. App CSS (tokens.css, style.css) can affect preview components
2. Preview component CSS (components.css) can affect app UI
3. Font families, colors, and box-sizing may clash
4. No true viewport isolation - preview doesn't represent actual page rendering

---

## Pros and Cons

### ✅ PROS of Iframe Approach

| Benefit | Description |
|---------|-------------|
| **Complete style isolation** | Preview CSS cannot affect app UI and vice versa |
| **True viewport representation** | Preview behaves like an actual browser page |
| **Accurate responsive testing** | Can resize iframe to test breakpoints |
| **Clean export** | Rendered HTML is exactly what will be exported |
| **No CSS specificity battles** | Don't need to worry about selector conflicts |
| **Third-party CSS safe** | Can load external CSS libraries without app impact |
| **Security sandbox available** | Can sandbox preview content if needed |

### ❌ CONS of Iframe Approach

| Challenge | Description | Mitigation |
|-----------|-------------|------------|
| **Cross-frame communication** | Need postMessage for parent-child communication | Use structured message protocol |
| **Click event complexity** | Must relay clicks from iframe to parent | Inject click handler script into iframe |
| **Selection highlighting** | CSS for `.selected` must be in iframe | Inject selection CSS or use postMessage |
| **Path map building** | Must query iframe DOM, not parent DOM | Use `iframe.contentDocument.querySelectorAll()` |
| **Performance overhead** | Iframe creates separate browsing context | Minimal impact for single iframe |
| **Height synchronization** | Iframe won't auto-resize to content | Use ResizeObserver or fixed height |
| **Debugging complexity** | Two separate DOM trees to inspect | Minor inconvenience |
| **Focus management** | Keyboard events may get trapped | Handle focus appropriately |

---

## Security Implementation

### Overview

The iframe preview must be secured against XSS attacks and ensure safe cross-origin communication. Even though the iframe loads same-origin content, proper security measures prevent potential vulnerabilities.

### 1. Origin Validation (Critical)

**NEVER use wildcard `*` for postMessage targetOrigin.**

**Parent to Iframe (ssr_app.js):**
```javascript
// ❌ INSECURE - Never do this
iframe.contentWindow.postMessage({ type: 'UPDATE_CONTENT', html }, '*');

// ✅ SECURE - Always specify exact origin
const TRUSTED_ORIGIN = window.location.origin; // e.g., 'http://localhost:5000'
iframe.contentWindow.postMessage({ type: 'UPDATE_CONTENT', html }, TRUSTED_ORIGIN);
```

**Iframe to Parent (preview_bridge.js):**
```javascript
// ❌ INSECURE - Never do this
window.parent.postMessage({ type: 'COMPONENT_CLICKED', componentId }, '*');

// ✅ SECURE - Always specify exact origin
const TRUSTED_ORIGIN = window.location.origin;
window.parent.postMessage({ type: 'COMPONENT_CLICKED', componentId }, TRUSTED_ORIGIN);
```

### 2. Message Origin Validation (Critical)

**Always validate `event.origin` before processing messages.**

**In preview_bridge.js (iframe):**
```javascript
const TRUSTED_ORIGIN = window.location.origin;

window.addEventListener('message', (event) => {
    // ✅ CRITICAL: Validate origin first
    if (event.origin !== TRUSTED_ORIGIN) {
        console.warn('Blocked message from untrusted origin:', event.origin);
        return;
    }

    // ✅ Validate message structure
    if (!event.data || typeof event.data.type !== 'string') {
        console.warn('Invalid message format');
        return;
    }

    // Process only known message types
    switch (event.data.type) {
        case 'UPDATE_CONTENT':
            handleUpdateContent(event.data);
            break;
        case 'SET_SELECTION':
            handleSetSelection(event.data);
            break;
        case 'CLEAR_SELECTION':
            handleClearSelection();
            break;
        default:
            console.warn('Unknown message type:', event.data.type);
    }
});
```

**In parent (selectionManager.js or main.js):**
```javascript
const TRUSTED_ORIGIN = window.location.origin;

window.addEventListener('message', (event) => {
    // ✅ CRITICAL: Validate origin
    if (event.origin !== TRUSTED_ORIGIN) {
        console.warn('Blocked message from untrusted origin:', event.origin);
        return;
    }

    // ✅ Validate message structure
    if (!event.data || typeof event.data.type !== 'string') {
        return;
    }

    // Process only known message types
    if (event.data.type === 'COMPONENT_CLICKED') {
        // ✅ Validate componentId format before using
        const componentId = event.data.componentId;
        if (typeof componentId === 'string' && /^comp_[\d_]+$/.test(componentId)) {
            selectionManager.selectComponentById(componentId);
        }
    }
});
```

### 3. XSS Prevention - Safe DOM Manipulation

**NEVER use innerHTML with untrusted data directly.**

**In preview_bridge.js:**
```javascript
function handleUpdateContent(data) {
    const container = document.getElementById('preview-content');

    // The HTML comes from our trusted Flask server via /render endpoint
    // It's server-rendered, not user-generated, so innerHTML is acceptable here
    // However, we still validate the source via origin check above

    if (container && typeof data.html === 'string') {
        container.innerHTML = data.html;
        notifyParentOfComponents();
        initializeInteractiveComponents();
    }
}

// ✅ For any user-generated text, use textContent
function showErrorMessage(message) {
    const container = document.getElementById('preview-content');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message; // ✅ Safe - no HTML interpretation
    container.appendChild(errorDiv);
}
```

### 4. Iframe Sandbox Attribute

**Use restrictive sandbox with only necessary permissions:**

```html
<iframe id="preview-frame"
        src="/preview-frame"
        class="preview-area"
        title="Preview"
        sandbox="allow-scripts allow-same-origin">
</iframe>
```

| Permission | Purpose | Included |
|------------|---------|----------|
| `allow-scripts` | Run JavaScript for interactivity | ✅ Yes |
| `allow-same-origin` | Access same-origin resources | ✅ Yes |
| `allow-forms` | Submit forms | ❌ No |
| `allow-popups` | Open new windows | ❌ No |
| `allow-top-navigation` | Navigate parent frame | ❌ No |
| `allow-modals` | Show alert/confirm/prompt | ❌ No |

**Note:** `allow-same-origin` is required for postMessage origin validation to work correctly.

### 5. Content Security Policy (CSP)

**Add CSP headers in Flask (app.py):**
```python
@app.after_request
def add_security_headers(response):
    # Restrict iframe embedding to same origin only
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "  # Allow inline styles for components
        "img-src 'self' data: https:; "       # Allow images from various sources
        "frame-src 'self'; "                   # Only allow same-origin frames
        "frame-ancestors 'self'; "             # Prevent embedding in other sites
    )

    return response
```

### 6. Message Type Whitelist

**Define allowed message types explicitly:**

```javascript
// constants.js or at top of files
const ALLOWED_MESSAGE_TYPES = {
    // Parent → Iframe
    UPDATE_CONTENT: 'UPDATE_CONTENT',
    SET_SELECTION: 'SET_SELECTION',
    CLEAR_SELECTION: 'CLEAR_SELECTION',

    // Iframe → Parent
    COMPONENT_CLICKED: 'COMPONENT_CLICKED',
    COMPONENTS_READY: 'COMPONENTS_READY',
    CONTENT_HEIGHT: 'CONTENT_HEIGHT'
};

// Validate message type
function isValidMessageType(type) {
    return Object.values(ALLOWED_MESSAGE_TYPES).includes(type);
}
```

### 7. Input Validation for Component IDs

**Validate componentId format to prevent injection:**

```javascript
// ✅ Validate component ID matches expected format
function isValidComponentId(id) {
    // Format: comp_0, comp_0_components_1, comp_0_columns_0_components_2
    return typeof id === 'string' && /^comp_(\d+_?)+[a-z]*_?\d*$/.test(id);
}

// Usage
if (event.data.type === 'SET_SELECTION') {
    if (isValidComponentId(event.data.componentId)) {
        highlightComponent(event.data.componentId);
    }
}
```

### 8. Security Checklist

- [ ] All postMessage calls specify exact origin (not `*`)
- [ ] All message listeners validate `event.origin`
- [ ] Message types are whitelisted and validated
- [ ] Component IDs are validated with regex
- [ ] Sandbox attribute restricts iframe permissions
- [ ] CSP headers are set on server responses
- [ ] X-Frame-Options header prevents clickjacking
- [ ] No user input directly used in innerHTML
- [ ] Error messages use textContent, not innerHTML

---

## Current Architecture

### Preview Container
**File:** `ssr_python/templates/index.html` (lines 87-92)
```html
<div id="preview" class="preview-area">
    <div class="preview-placeholder">...</div>
</div>
```

### Rendering Flow
**File:** `ssr_python/static/js/ssr_app.js` (lines 107-108)
```javascript
const htmlContent = await response.text();
preview.innerHTML = htmlContent;
```

### Selection & Click Handling
**File:** `ssr_python/static/js/events.js` (line 33)
```javascript
preview.addEventListener('click', actions.handlePreviewClick);
```

**File:** `ssr_python/static/js/selectionManager.js` (line 16)
```javascript
const targetElement = event.target.closest('[data-component-id]');
```

### CSS Loading Order
1. `tokens.css` - Design tokens (colors, shadows)
2. `style.css` - App UI + chrome-target selection styles
3. `components.css` - Component rendering styles

---

## Implementation Plan

### Phase 1: Create Iframe Infrastructure

#### 1.1 Update index.html
**File:** `ssr_python/templates/index.html`

Replace preview div with iframe:
```html
<iframe id="preview-frame"
        src="/preview-frame"
        class="preview-area"
        title="Preview"
        sandbox="allow-scripts allow-same-origin">
</iframe>
```

#### 1.2 Create Preview Template
**New File:** `ssr_python/templates/preview_frame.html`

Standalone HTML for iframe content:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/css/tokens.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <link rel="stylesheet" href="/static/css/preview-chrome.css">
    <style id="dynamic-styles"></style>
</head>
<body>
    <div id="preview-content"></div>
    <script src="/static/js/preview_bridge.js"></script>
</body>
</html>
```

#### 1.3 Create Preview Chrome CSS
**New File:** `ssr_python/static/css/preview-chrome.css`

Extract selection-related styles from style.css:
```css
/* Chrome target selection styles - for iframe only */
.chrome-target {
    position: relative;
    box-sizing: border-box;
    cursor: pointer;
}

.chrome-target::before {
    content: '';
    position: absolute;
    inset: -2px;
    border: 2px dashed var(--color-secondary);
    pointer-events: none;
    opacity: 0;
    z-index: 999;
    box-sizing: border-box;
}

.chrome-target:hover::before {
    border-color: var(--color-secondary);
    opacity: 1;
}

.chrome-target.selected::before {
    border-color: var(--color-danger);
    opacity: 1;
}
```

---

### Phase 2: Create Communication Bridge

#### 2.1 Preview Bridge Script
**New File:** `ssr_python/static/js/preview_bridge.js`

Runs inside iframe, communicates with parent:
```javascript
// Handle messages from parent
window.addEventListener('message', (event) => {
    if (event.data.type === 'UPDATE_CONTENT') {
        document.getElementById('preview-content').innerHTML = event.data.html;
        notifyParentOfComponents();
        initializeInteractiveComponents();
    }
    if (event.data.type === 'SET_SELECTION') {
        highlightComponent(event.data.componentId);
    }
    if (event.data.type === 'CLEAR_SELECTION') {
        clearHighlight();
    }
});

// Relay clicks to parent
document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-component-id]');
    if (target) {
        window.parent.postMessage({
            type: 'COMPONENT_CLICKED',
            componentId: target.dataset.componentId
        }, '*');
    }
});

// Notify parent of available components (for path map)
function notifyParentOfComponents() {
    const components = document.querySelectorAll('[data-component-id]');
    const ids = Array.from(components).map(el => el.dataset.componentId);
    window.parent.postMessage({ type: 'COMPONENTS_READY', componentIds: ids }, '*');
}

// Selection highlighting
let currentSelection = null;

function highlightComponent(componentId) {
    clearHighlight();
    const element = document.querySelector(`[data-component-id="${componentId}"]`);
    if (element) {
        element.classList.add('selected');
        currentSelection = element;
    }
}

function clearHighlight() {
    if (currentSelection) {
        currentSelection.classList.remove('selected');
        currentSelection = null;
    }
}

// Initialize interactive components (tabs, accordion, carousel)
function initializeInteractiveComponents() {
    // Import and call component initializers
    // This will need to import from component_interactions.js
}
```

---

### Phase 3: Update Parent-Side Code

#### 3.1 Update ssr_app.js
**File:** `ssr_python/static/js/ssr_app.js`

Change `renderPreview()` to post message to iframe:
```javascript
export const renderPreview = async (yamlContent, yamlStructure = null) => {
    const iframe = document.getElementById('preview-frame');
    if (!iframe || !iframe.contentWindow) return;

    // Cancel any pending request
    if (currentAbortController) {
        currentAbortController.abort();
    }
    currentAbortController = new AbortController();

    // Parse YAML if structure not provided
    let structure = yamlStructure;
    if (!structure) {
        structure = parseYaml(yamlContent);
        if (structure === null) {
            structure = [];
        }
    }

    try {
        const response = await fetch('/render', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-yaml' },
            body: yamlContent,
            signal: currentAbortController.signal
        });

        if (!response.ok) {
            const errorData = await response.json();
            iframe.contentWindow.postMessage({
                type: 'UPDATE_CONTENT',
                html: `<div class="error-message">...</div>`
            }, '*');
            return;
        }

        const htmlContent = await response.text();

        // Post to iframe instead of innerHTML
        iframe.contentWindow.postMessage({
            type: 'UPDATE_CONTENT',
            html: htmlContent
        }, '*');

        // Build path map from YAML structure
        if (structure && Array.isArray(structure)) {
            pathMapBuilder.buildPathMapFromStructure(structure);
        }

    } catch (error) {
        if (error.name === 'AbortError') return;
        // Handle error...
    }
};
```

#### 3.2 Update selectionManager.js
**File:** `ssr_python/static/js/selectionManager.js`

Handle selection via postMessage:
```javascript
export class SelectionManager {
    constructor() {
        this.selectedComponentId = null;
        this.selectedPath = null;
        this.onSelectionChange = null;

        // Listen for clicks from iframe
        window.addEventListener('message', (event) => {
            if (event.data.type === 'COMPONENT_CLICKED') {
                this.selectComponentById(event.data.componentId);
            }
        });
    }

    selectComponentById(componentId) {
        // Get path from path map
        const path = pathMapBuilder.getPath(componentId);
        if (!path) return;

        this.selectedComponentId = componentId;
        this.selectedPath = path;

        // Tell iframe to highlight
        this.highlightComponent(componentId);

        // Notify parent of selection change
        if (this.onSelectionChange) {
            this.onSelectionChange({
                componentId: this.selectedComponentId,
                path: this.selectedPath
            });
        }
    }

    highlightComponent(componentId) {
        const iframe = document.getElementById('preview-frame');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: 'SET_SELECTION',
                componentId: componentId
            }, '*');
        }
    }

    clearHighlight() {
        const iframe = document.getElementById('preview-frame');
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: 'CLEAR_SELECTION'
            }, '*');
        }
    }
}
```

#### 3.3 Update pathMapBuilder.js
**File:** `ssr_python/static/js/pathMapBuilder.js`

Build path map from YAML structure (no DOM query needed):
```javascript
export class ComponentPathMapBuilder {
    constructor() {
        this.pathMap = new Map();
    }

    // Build path map purely from YAML structure
    buildPathMapFromStructure(structure) {
        this.clear();
        this.traverseStructure(structure, []);
    }

    traverseStructure(components, basePath) {
        if (!Array.isArray(components)) return;

        components.forEach((component, index) => {
            const path = [...basePath, index];
            const componentId = 'comp_' + path.join('_');
            this.pathMap.set(componentId, path);

            // Handle nested components
            if (component.components) {
                this.traverseStructure(component.components, [...path, 'components']);
            }
            if (component.columns) {
                component.columns.forEach((col, colIndex) => {
                    if (col.components) {
                        this.traverseStructure(col.components, [...path, 'columns', colIndex, 'components']);
                    }
                });
            }
            // Handle tabs, slides, items...
        });
    }

    getPath(componentId) {
        return this.pathMap.get(componentId);
    }

    clear() {
        this.pathMap.clear();
    }
}
```

#### 3.4 Update events.js
**File:** `ssr_python/static/js/events.js`

Remove direct click listener on preview:
```javascript
// Remove this line:
// preview.addEventListener('click', actions.handlePreviewClick);

// The message listener is now in SelectionManager
// No changes needed here if SelectionManager handles it
```

---

### Phase 4: Flask Route for Preview Frame

#### 4.1 Add Route
**File:** `ssr_python/app.py`

```python
@app.route('/preview-frame')
def preview_frame():
    return render_template('preview_frame.html')
```

---

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `templates/index.html` | Modify | Replace div with iframe |
| `templates/preview_frame.html` | **Create** | Iframe HTML template |
| `static/css/preview-chrome.css` | **Create** | Selection styles for iframe |
| `static/css/style.css` | Modify | Remove chrome styles (moved to preview-chrome.css) |
| `static/js/preview_bridge.js` | **Create** | Iframe-side communication |
| `static/js/ssr_app.js` | Modify | PostMessage instead of innerHTML |
| `static/js/selectionManager.js` | Modify | PostMessage for selection |
| `static/js/pathMapBuilder.js` | Modify | Build from structure, not DOM |
| `static/js/events.js` | Modify | Remove preview click listener |
| `app.py` | Modify | Add /preview-frame route |

---

## Migration Strategy

### Step 1: Create iframe infrastructure (non-breaking)
- Add preview_frame.html template
- Add preview-chrome.css
- Add preview_bridge.js
- Add /preview-frame route

### Step 2: Update parent-side code
- Modify ssr_app.js to support both modes
- Add feature flag: `const USE_IFRAME = true;`
- Update selectionManager.js with dual support

### Step 3: Switch to iframe
- Replace div with iframe in index.html
- Remove old preview div handling

### Step 4: Cleanup
- Remove unused code paths
- Remove feature flag
- Update documentation

---

## Resize Bar Compatibility

### Current Resize Implementation

**Files:** `ssr_python/static/js/events.js` (lines 188-265), `ssr_python/static/css/style.css`

| Resizer | Target | Method | Iframe Impact |
|---------|--------|--------|---------------|
| Editor Resizer (`#resizer`) | `#editorWrapper` height | `editorWrapper.style.height` | ✅ No change needed |
| Sidebar Resizer (`#sidebarResizer`) | CSS variable `--sidebar-width` | `appContainer.style.setProperty()` | ✅ No change needed |

### Why Resize Bars Will Work

The resize bars operate at the **container level**, not on the preview content directly:
- Editor resizer changes `#editorWrapper` height
- Preview area uses `flex-grow: 1` to fill remaining space
- Whether preview is `<div>` or `<iframe>`, the flex layout applies to the outer element

### CSS Adjustments Required

**Current CSS for `.preview-area` (style.css lines 610-625):**
```css
.preview-area {
    padding: var(--spacing-lg);    /* ❌ Won't work on iframe */
    overflow-y: auto;              /* ⚠️ Iframe has own scroll */
    flex-grow: 1;                  /* ✅ Works on iframe */
    min-height: 10rem;             /* ✅ Works on iframe */
}
```

**Updated CSS for iframe:**
```css
#preview-frame {
    border: none;
    flex-grow: 1;
    min-height: 10rem;
    width: 100%;
}
```

Move padding to `preview_frame.html` body:
```css
body {
    margin: 0;
    padding: var(--spacing-lg);
}
```

### Pointer Events During Resize

**Issue:** During sidebar resize, `pointerEvents = 'none'` is set on sidebar. If mouse moves over iframe during drag, events could get "trapped".

**Solution:** Add iframe to pointer-events blocking during resize.

**Update in `events.js` (line 214-227):**
```javascript
const resize = (e) => {
    if (!isResizing) return;
    // ... existing code ...
};

const startResizing = (e) => {
    // ... existing code ...
    const iframe = document.getElementById('preview-frame');
    if (iframe) iframe.style.pointerEvents = 'none';
};

const stopResizing = () => {
    // ... existing code ...
    const iframe = document.getElementById('preview-frame');
    if (iframe) iframe.style.pointerEvents = '';
};
```

---

## Testing Checklist

- [ ] Preview renders correctly in iframe
- [ ] Component selection works via click
- [ ] Selection highlighting shows in iframe
- [ ] Properties panel updates on selection
- [ ] Path map builds correctly from YAML structure
- [ ] Component tree syncs with iframe content
- [ ] Undo/redo works across iframe boundary
- [ ] Interactive components (tabs, accordion, carousel) work
- [ ] **Editor resizer works (drag to resize editor height)**
- [ ] **Sidebar resizer works (drag to resize sidebar width)**
- [ ] **Resize drag over iframe doesn't get stuck**
- [ ] Responsive preview (if implementing resize)
- [ ] No style leakage between app and preview
- [ ] Export produces correct HTML

---

**Last Updated:** January 2025
