# Plan: Fullscreen Preview, Undo/Redo, and Export Buttons

## Context

The app header (`.header-actions`) already has placeholder buttons for fullscreen (`#fullscreenBtn`) and export (`#exportBtn`), but they show `alert()` stubs. Undo/redo logic exists in `historyManager.js` and is wired to keyboard shortcuts (Ctrl+Z/Y), but has no toolbar buttons. This plan adds working UI buttons for all four features.

---

## Part 1: Add Undo/Redo SVG Icons to Sprite

**File: `ssr_python/static/icon-sprite.svg`**

Add two new `<symbol>` elements (Feather-style rotate-ccw / rotate-cw) to the sprite:

```xml
<symbol id="icon-undo" viewBox="0 0 24 24">
  <polyline points="1 4 1 10 7 10"></polyline>
  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
</symbol>
<symbol id="icon-redo" viewBox="0 0 24 24">
  <polyline points="23 4 23 10 17 10"></polyline>
  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
</symbol>
```

---

## Part 2: Update Header HTML

**File: `ssr_python/templates/index.html`**

### 2A. Replace `.header-actions` (lines 57–68)

New button order: **Undo → Redo → Fullscreen → Clear → Export**

```html
<div class="header-actions">
    <button id="undoBtn" class="btn btn-ghost btn-icon" title="Undo (Ctrl+Z)" disabled>
        <svg class="icon" aria-hidden="true"><use href="#icon-undo"></use></svg>
    </button>
    <button id="redoBtn" class="btn btn-ghost btn-icon" title="Redo (Ctrl+Y)" disabled>
        <svg class="icon" aria-hidden="true"><use href="#icon-redo"></use></svg>
    </button>
    <button id="fullscreenBtn" class="btn btn-ghost btn-icon" title="Fullscreen Preview">
        <svg class="icon" aria-hidden="true"><use href="#icon-maximize"></use></svg>
    </button>
    <button id="clearBtn" class="btn btn-ghost btn-icon" title="Clear Canvas">
        <svg class="icon" aria-hidden="true"><use href="#icon-trash-2"></use></svg>
    </button>
    <button id="exportBtn" class="btn btn-primary" title="Export Site">
        <svg class="icon" aria-hidden="true"><use href="#icon-download"></use></svg>
        <span>Export</span>
    </button>
</div>
```

Changes: added `undoBtn`/`redoBtn` (start disabled), changed fullscreen icon from `eye` → `maximize`, changed export icon from `globe` → `download`, label from "Publish" to "Export".

### 2B. Add fullscreen modal HTML (before closing `</body>`)

```html
<!-- Fullscreen Preview Modal -->
<div id="fullscreenModal" class="fullscreen-modal">
    <div class="fullscreen-content">
        <iframe id="fullscreenFrame" class="fullscreen-preview preview-area" title="Fullscreen Preview"></iframe>
    </div>
    <button id="closeFullscreenBtn" class="fullscreen-close" title="Close (Esc)">
        <svg class="icon" aria-hidden="true" style="width:16px;height:16px;stroke:white;"><use href="#icon-x"></use></svg>
    </button>
</div>
```

---

## Part 3: Update DOM References

**File: `ssr_python/static/js/main.js`** — `getDomReferences()` (line 22–42)

Add undo/redo button references:

```javascript
undoButton: document.getElementById('undoBtn'),
redoButton: document.getElementById('redoBtn'),
```

---

## Part 4: Undo/Redo Button Wiring + State Management

**File: `ssr_python/static/js/main.js`**

### 4A. Add `updateHistoryButtons()` helper (after `getDomReferences`)

```javascript
function updateHistoryButtons() {
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    if (undoBtn) undoBtn.disabled = !historyManager.canUndo();
    if (redoBtn) redoBtn.disabled = !historyManager.canRedo();
}
```

### 4B. Call `updateHistoryButtons()` after every history-changing operation

Add `updateHistoryButtons()` call at the end of:
- `actions.undo()` (line ~302, after `handleEditorInput`)
- `actions.redo()` (line ~312, after `handleEditorInput`)
- `actions.handleEditorInput()` (line ~168, after `historyManager.push`)
- `actions.clearCanvas()` (line ~187, after `historyManager.clear`)
- `actions.applySelectedComponentProperties()` (line ~266, after `historyManager.push`)

### 4C. Implement fullscreen actions (replace stubs at lines 194–195)

```javascript
openFullscreen: async () => {
    const modal = document.getElementById('fullscreenModal');
    const frame = document.getElementById('fullscreenFrame');
    if (!modal || !frame) return;

    const editor = document.getElementById('codeEditor');
    const yamlContent = editor ? editor.value : '';
    if (!yamlContent.trim()) return;

    try {
        // POST to /render to get HTML
        const response = await fetch('/render', {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain' },
            body: yamlContent
        });
        const html = await response.text();

        // Build a standalone HTML document for the iframe
        const standaloneHtml = await buildStandaloneHtml(html);
        frame.srcdoc = standaloneHtml;
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    } catch (err) {
        console.error('[Fullscreen] Render failed:', err);
    }
},
closeFullscreen: () => {
    const modal = document.getElementById('fullscreenModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
},
```

### 4D. Add `buildStandaloneHtml()` helper function

This generates a self-contained HTML page from rendered component HTML. Used by both fullscreen preview and export.

```javascript
async function buildStandaloneHtml(renderedHtml) {
    // Fetch CSS and JS assets (cached after first call)
    const [tokensCss, componentsCss, runtimeJs, spriteSvg] = await Promise.all([
        fetch('/static/css/tokens.css').then(r => r.text()),
        fetch('/static/css/components.css').then(r => r.text()),
        fetch('/static/js/swift-sites-runtime.js').then(r => r.text()),
        fetch('/static/icon-sprite.svg').then(r => r.text()),
    ]);

    // Base styles from preview_frame.html (inline <style> block)
    const baseStyles = `* { box-sizing: border-box; }
html { font-size: clamp(12px, 1vw + 8px, 18px); }
body { margin:0; padding:0; min-height:100%; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; font-size:1rem; line-height:1.5; color:#1f2937; background:#fff; }
#preview-content { min-height:100vh; }
.page { min-height:100vh; position:relative; }
.page > .titlebar { position:sticky; top:0; z-index:100; }`;

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swift Sites Export</title>
    <style>${baseStyles}</style>
    <style>${tokensCss}</style>
    <style>${componentsCss}</style>
</head>
<body>
    <div id="svgSpriteRoot" hidden>${spriteSvg}</div>
    <div id="preview-content">${renderedHtml}</div>
    <script>${runtimeJs}<\/script>
</body>
</html>`;
}
```

### 4E. Implement export (replace stub at line 180)

```javascript
exportCode: async () => {
    const editor = document.getElementById('codeEditor');
    const yamlContent = editor ? editor.value : '';
    if (!yamlContent.trim()) return;

    try {
        // Render current YAML
        const response = await fetch('/render', {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain' },
            body: yamlContent
        });
        const html = await response.text();

        // Build standalone page
        const standaloneHtml = await buildStandaloneHtml(html);

        // Download as HTML file
        const blob = new Blob([standaloneHtml], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'index.html';
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error('[Export] Failed:', err);
    }
},
```

**Note:** The export produces a single self-contained `index.html` with CSS and JS inlined in `<style>` and `<script>` tags. This avoids needing a zip library and produces a file that works by just double-clicking it. If separate files are later desired, a zip download option can be added.

---

## Part 5: Wire Undo/Redo + Escape Key in Events

**File: `ssr_python/static/js/events.js`**

### 5A. Add undo/redo buttons to `initializeEvents()` destructuring (line 131)

Add to the destructured `dom` object:
```javascript
undoButton,
redoButton,
```

### 5B. Add button click handlers (after line 175)

```javascript
if (undoButton) {
    undoButton.addEventListener('click', actions.undo);
}
if (redoButton) {
    redoButton.addEventListener('click', actions.redo);
}
```

### 5C. Add Escape key handler for fullscreen (in global keydown listener)

Add a document-level keydown listener for Escape:

```javascript
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        actions.closeFullscreen();
    }
});
```

---

## Part 6: CSS Updates

**File: `ssr_python/static/css/style.css`**

### 6A. Disabled button state (add after `.btn-icon` rules, ~line 937)

```css
.btn-icon:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    pointer-events: none;
}
```

### 6B. Fix fullscreen modal CSS variables (lines 950–999)

The existing CSS uses undefined variables (`--color-primary`, `--color-danger`, `--color-base`). Replace the entire fullscreen modal section with:

```css
/* Fullscreen Modal */
.fullscreen-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.92);
    z-index: 10000;
    padding: 0;
}

.fullscreen-content {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: stretch;
}

.fullscreen-preview {
    width: 100%;
    height: 100%;
    border: none;
    background: #ffffff;
}

.fullscreen-close {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: var(--bg-medium);
    color: var(--text);
    border: 1px solid var(--border);
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    cursor: pointer;
    z-index: 10001;
    transition: all 0.15s ease;
}

.fullscreen-close:hover {
    background: var(--accent);
    border-color: var(--accent);
}
```

---

## Files Summary

| File | Change |
|------|--------|
| `static/icon-sprite.svg` | Add `#icon-undo` and `#icon-redo` symbols |
| `templates/index.html` | Add undo/redo buttons to header, add fullscreen modal HTML |
| `static/js/main.js` | Add `undoBtn`/`redoBtn` to DOM refs. Add `updateHistoryButtons()`. Add `buildStandaloneHtml()`. Implement `openFullscreen`/`closeFullscreen`/`exportCode`. |
| `static/js/events.js` | Wire undo/redo button clicks, add Escape key for fullscreen close |
| `static/css/style.css` | Add `.btn-icon:disabled` style, fix fullscreen modal CSS |

## What Does NOT Change

- `historyManager.js` — Already complete, no modifications needed
- `renderer.py` / `routes/render.py` — Already handles POST /render
- `preview_bridge.js` — Not involved
- `preview_frame.html` — Not modified (fullscreen uses `buildStandaloneHtml()`)
- No new Flask routes needed — export is client-side using Blob download

## Verification

1. Start Flask, load app, add some YAML content
2. **Undo/Redo:** Make edits, click undo button → reverts. Click redo → re-applies. Buttons grey out when stack is empty. Ctrl+Z/Y still work.
3. **Fullscreen:** Click maximize button → dark overlay modal shows rendered preview in a full-screen iframe. Click X or press Escape → modal closes.
4. **Export:** Click Export button → downloads `index.html` file. Open it in a browser → renders the site standalone with all CSS, JS, and icons inlined.
5. `python -m pytest tests/ -v` — all 30 tests pass
