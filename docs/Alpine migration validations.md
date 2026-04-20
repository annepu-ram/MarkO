# Plan: Introduce Alpine.js to Swift Sites (App Shell Only)

## Context

Swift Sites is a YAML-based website builder with server-side rendering. Alpine.js is being added to the **editor UI (app shell) only** for state management and reactivity. The preview iframe, exported sites, and component templates remain completely untouched.

**Dynamic pages feature** (future): Show/hide sections via URL params will use vanilla JS (`data-visible-when` + ~15 lines in `swift-sites-runtime.js`). Alpine is not needed for that.

---

## Pros and Cons

### Pros
- **Two-way form binding** (`x-model`) — eliminates imperative DOM scraping in properties panel
- **Declarative visibility** (`x-show`) — replaces `data-hidden` toggling and `classList` manipulation
- **Reactive state** (stores) — kills 10 scattered `updateHistoryButtons()` calls
- **Partial updates** (`x-for`) — replaces full innerHTML grid re-renders in images panel
- **Lightweight** (~15KB gzipped), no build step, progressive adoption

### Cons
- Jinja2 `{{ }}` conflict — mitigated by exclusively using `x-text`/`x-bind` directives
- Hybrid architecture during migration — Alpine coexists with vanilla JS temporarily
- Additional vendor dependency — single ~43KB file, no npm needed

---

## Safety Guarantees

### What is NOT touched (across ALL phases)
These files have **zero modifications** in this entire plan:

- `ssr_python/static/js/swift-sites-runtime.js` — preview/export runtime
- `ssr_python/static/js/preview_bridge.js` — iframe communication
- `ssr_python/static/js/ssr_app.js` — parent-iframe bridge
- `ssr_python/templates/preview_frame.html` — iframe template
- `ssr_python/templates/components/**` — ALL Jinja2 component templates
- `ssr_python/renderer.py` — rendering engine
- `ssr_python/config/**` — component schemas, defaults, tokens
- `ssr_python/routes/**` — ALL Flask routes
- `ssr_python/rag/**` — RAG pipeline
- `ssr_python/tests/**` — NO existing tests are modified

### Why existing tests cannot break
- Tests use `client.get('/')` and only check `response.status_code == 200` — not HTML content
- Tests use `client.post('/render', ...)` and check rendered component HTML — this comes from `renderer.py` + component templates, which are untouched
- `test_yaml_validation.py` validates YAML template structure — no HTML involved
- `test_renderer.py` tests `render_yaml_structure()` — generates preview HTML, not app shell HTML
- Alpine.js is only added to `index.html` (app shell) — no test inspects this file's content

---

## Phased Implementation

### Phase 0: Infrastructure — Load Alpine (Zero Behavior Change)

**Goal:** Add Alpine.js to the app shell. Verify it loads without side effects.

**Changes:**

1. **New file:** `ssr_python/static/js/alpine.min.js`
   - Download Alpine.js 3.x production build
   - Place as vendor file alongside `lucide.min.js`

2. **Edit:** `ssr_python/templates/index.html`
   - Add one `<script>` tag in `<head>` after the Lucide script:
     ```html
     <script src="{{ url_for('static', filename='js/alpine.min.js') }}" defer></script>
     ```

3. **Edit:** `ssr_python/static/css/style.css`
   - Add one CSS rule at the top:
     ```css
     [x-cloak] { display: none !important; }
     ```

**What could go wrong & how to verify:**
| Risk | Likelihood | Check |
|------|-----------|-------|
| Alpine auto-initializes and modifies DOM | Near zero — Alpine only affects elements with `x-data` attributes, which don't exist yet | Inspect DOM before/after: identical |
| Alpine conflicts with existing JS modules | Near zero — Alpine uses `x-` prefixed attributes, no naming collisions with existing code | Console: zero errors |
| `defer` script blocks page load | Zero — `defer` is non-blocking by spec | Network tab: parallel load |
| Test failures | Zero — no test inspects `index.html` content | `python -m pytest tests/ -v`: all 1026 pass |

**Verification checklist:**
- [ ] `python -m pytest tests/ -v` — all 1026 tests pass
- [ ] Load `http://localhost:5000` — editor renders identically
- [ ] Browser console: `Alpine` object exists, zero errors/warnings
- [ ] Type YAML → preview renders
- [ ] Click component → properties panel appears
- [ ] Undo/redo works
- [ ] All sidebar panels open/close
- [ ] Export HTML → file downloads, works standalone (no Alpine inside)
- [ ] Chat sends and receives messages

**Rollback:** Delete `alpine.min.js`, remove the one `<script>` tag, remove the one CSS rule. Three-line revert.

---

### Phase 1: History Button Reactivity

**Goal:** Replace `updateHistoryButtons()` (called in 10 places) with one Alpine store.

**Current pattern** ([main.js:77](ssr_python/static/js/main.js#L77)):
```js
function updateHistoryButtons() {
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    if (undoBtn) undoBtn.disabled = !historyManager.canUndo();
    if (redoBtn) redoBtn.disabled = !historyManager.canRedo();
}
```
Called at lines: 202, 256, 337, 623, 687, 819, 856, 868, 936 in `main.js`.

**Changes:**

1. **Edit:** `ssr_python/static/js/main.js`
   - Add near the top (after imports):
     ```js
     // Register Alpine store for history state (reactive button binding)
     document.addEventListener('alpine:init', () => {
         Alpine.store('history', { canUndo: false, canRedo: false });
     });
     ```
   - Create helper to replace `updateHistoryButtons()`:
     ```js
     function syncHistoryState() {
         if (typeof Alpine !== 'undefined' && Alpine.store) {
             Alpine.store('history').canUndo = historyManager.canUndo();
             Alpine.store('history').canRedo = historyManager.canRedo();
         }
     }
     ```
   - Replace all 10 `updateHistoryButtons()` calls with `syncHistoryState()`
   - Delete the `updateHistoryButtons()` function

2. **Edit:** `ssr_python/templates/index.html`
   - Change undo button (line 60):
     ```html
     <button id="undoBtn" class="btn btn-ghost btn-icon" title="Undo (Ctrl+Z)" :disabled="!$store.history.canUndo" x-data>
     ```
   - Change redo button (line 63):
     ```html
     <button id="redoBtn" class="btn btn-ghost btn-icon" title="Redo (Ctrl+Y)" :disabled="!$store.history.canRedo" x-data>
     ```
   - Note: `x-data` is needed on each button so Alpine processes the `:disabled` binding. The `disabled` HTML attribute is removed (Alpine controls it now).

**What could go wrong & how to verify:**
| Risk | Likelihood | Check |
|------|-----------|-------|
| Buttons don't disable on page load | Low — store initializes with `canUndo: false, canRedo: false`, matching the initial `disabled` state | Load page: both buttons disabled |
| Store not ready when first history push happens | Low — `alpine:init` fires before DOMContentLoaded completes | Timeline: Alpine init → store registered → DOMContentLoaded → app bootstrap → first syncHistoryState() |
| Buttons stay disabled after edit | Zero if `syncHistoryState()` is called at all 10 sites | Test each: edit YAML, undo, redo, clear, tree actions, chat apply |
| Test failures | Zero — no test checks button disabled state | `python -m pytest tests/ -v`: all pass |

**Verification checklist:**
- [ ] All 1026 tests pass
- [ ] Load editor: both undo/redo buttons disabled (correct initial state)
- [ ] Type in YAML editor → undo button enables
- [ ] Click undo → undo button disables, redo enables
- [ ] Click redo → redo button disables, undo enables
- [ ] Clear canvas → both buttons disabled
- [ ] Apply chat YAML → undo button enables
- [ ] Tree action (delete, move) → undo button enables
- [ ] Apply properties → undo button enables
- [ ] Multiple edits → undo several times → redo several times → states correct

**Rollback:** Revert `main.js` (restore `updateHistoryButtons()` and 10 call sites), revert `index.html` (restore static `disabled` attribute). Two-file revert.

---

### Phase 2: Sidebar Panel Toggles

**Goal:** Replace imperative `togglePanel()` / `toggleRightPanel()` with Alpine store.

**Current pattern** ([events.js:3-51](ssr_python/static/js/events.js#L3-L51)):
- Closure variable `currentPanel` tracks open left panel
- `togglePanel()` manually adds/removes `.open` class on panel elements and `.active` on buttons
- Same pattern for `currentRightPanel` / `toggleRightPanel()`
- Panel-open callbacks call `renderThemesPanel()`, `renderImagesPanel()`, etc.

**Changes:**

1. **Edit:** `ssr_python/static/js/events.js`
   - Register Alpine store:
     ```js
     document.addEventListener('alpine:init', () => {
         Alpine.store('panels', { left: null, right: null });
     });
     ```
   - Rewrite `togglePanel()` to update store instead of DOM classes:
     ```js
     export function togglePanel(panelName) {
         const store = Alpine.store('panels');
         if (store.left === panelName) {
             store.left = null;
         } else {
             store.left = panelName;
             // Fire panel render callbacks
             if (panelName === 'themes' && window.renderThemesPanel) window.renderThemesPanel();
             if (panelName === 'images' && window.renderImagesPanel) window.renderImagesPanel();
             if (panelName === 'pages' && window.renderPagesPanel) window.renderPagesPanel();
             if (panelName === 'settings' && window.renderSettingsPanel) window.renderSettingsPanel();
         }
     }
     ```
   - Same approach for `toggleRightPanel()`, `closePanel()`, `closeRightPanel()`

2. **Edit:** `ssr_python/templates/index.html`
   - On each sidebar panel element, add Alpine bindings:
     ```html
     <div id="layersPanel" class="sidebar-slide-panel"
          x-data x-show="$store.panels.left === 'layers'"
          x-transition:enter="panel-enter" x-transition:leave="panel-leave">
     ```
   - On each sidebar button, add active class binding:
     ```html
     <button class="sidebar-btn" data-panel="layers"
          x-data :class="{ 'active': $store.panels.left === 'layers' }">
     ```
   - Same pattern for right panels with `$store.panels.right`

**What could go wrong & how to verify:**
| Risk | Likelihood | Check |
|------|-----------|-------|
| Panel render callbacks not firing | Medium — must ensure callbacks fire inside `togglePanel()` | Open themes panel: themes load. Open images: images load |
| Panel close animation missing | Low — `x-transition` provides enter/leave, may need CSS adjustment | Visual: panels slide in/out smoothly |
| Bottom sheet (mobile) not syncing | Medium — `toggleRightPanel` also manages `.bottom-sheet-tab` active states | Test on mobile viewport: bottom sheet tabs sync |
| `window.togglePanel` global not updated | Low — line 189 `window.togglePanel = togglePanel` still exports | Inline onclick handlers still work |
| Test failures | Zero — no test covers panel UI | All pass |

**Verification checklist:**
- [ ] All 1026 tests pass
- [ ] Click layers button → layers panel opens, button active
- [ ] Click layers again → panel closes, button inactive
- [ ] Click themes → themes panel opens, layers closes (only one at a time)
- [ ] Click images → images panel opens with search UI loaded
- [ ] Click pages → pages panel opens with page list
- [ ] Click settings → settings panel opens
- [ ] Right panels: chat opens/closes, properties opens/closes
- [ ] Mobile viewport: bottom sheet tabs sync with right panels
- [ ] Keyboard: Escape doesn't break panels
- [ ] Panel close buttons (X) work
- [ ] Sidebar resize still works (no interference)

**Rollback:** Revert `events.js` and `index.html` to previous versions. Two-file revert.

---

### Phase 3: Images Panel Reactive State

**Goal:** Replace innerHTML grid re-renders with Alpine reactivity.

**Current pain:** [imagesPanel.js](ssr_python/static/js/imagesPanel.js) re-renders the entire image grid via innerHTML on every search/filter/select action, then re-attaches all event listeners.

**Changes:**

1. **Edit:** `ssr_python/static/js/imagesPanel.js`
   - Convert to Alpine component definition:
     ```js
     export function imagesPanel() {
         return {
             searchQuery: '',
             activeColor: null,
             activeOrientation: null,
             searchResults: [],
             selectedImages: [],
             isLoading: false,
             currentPage: 1,
             hasSearched: false,
             
             async init() {
                 await this.loadSelectedImages();
             },
             async searchImages() { /* API call, updates this.searchResults */ },
             async toggleImageSelection(photo) { /* select/deselect logic */ },
             // ... remaining methods converted from closure functions
         };
     }
     ```
   - Remove all `innerHTML` rendering functions
   - Remove manual event listener attachment

2. **Edit:** `ssr_python/templates/index.html`
   - Replace static images panel content with Alpine-driven template:
     ```html
     <div id="imagesPanel" class="sidebar-slide-panel" x-data="imagesPanel()" ...>
         <input type="text" x-model.debounce.300ms="searchQuery" 
                @input="searchImages()" placeholder="Search photos...">
         <!-- Color pills -->
         <template x-for="color in colors">
             <button :class="{ 'active': activeColor === color }" 
                     @click="activeColor = activeColor === color ? null : color; searchImages()">
             </button>
         </template>
         <!-- Results grid -->
         <div class="images-grid">
             <template x-for="photo in searchResults" :key="photo.id">
                 <div class="image-card" @click="toggleImageSelection(photo)">
                     <img :src="photo.thumbnail" :alt="photo.alt">
                 </div>
             </template>
         </div>
         <div x-show="isLoading" class="loading-skeleton">...</div>
     </div>
     ```

**What could go wrong & how to verify:**
| Risk | Likelihood | Check |
|------|-----------|-------|
| API calls fail (search, select, upload) | Zero — API endpoints unchanged, only UI layer changes | Search returns results, selection persists to DB |
| Image selection not syncing with DB | Medium — must ensure `toggleImageSelection()` still calls proper endpoints | Select image → refresh page → image still selected |
| Upload flow broken | Medium — file input + progress UI must be preserved | Upload image → appears in selected grid |
| `renderImagesPanel()` global callback no longer works | Medium — panel toggle calls this on open | Open images panel → selected images load |
| Pagination broken | Low — must preserve page increment logic | Search → scroll → more results load |

**Verification checklist:**
- [ ] All 1026 tests pass
- [ ] Open images panel → selected images load from DB
- [ ] Type search query → results appear (debounced, no flicker)
- [ ] Click color pill → results filter. Click again → filter clears
- [ ] Click orientation pill → results filter
- [ ] Click image → downloads and appears in selected section
- [ ] Click selected image → removes from selection
- [ ] Upload image via file picker → appears in selected
- [ ] Pagination: search, scroll/click next → more results
- [ ] Close and reopen panel → state preserved
- [ ] No console errors

**Rollback:** Revert `imagesPanel.js` and images panel section of `index.html`. Two-file revert.

---

### Phase 4: Properties Panel Conditional Visibility

**Goal:** Replace `data-hidden` attribute toggling with `x-show`.

**Current pattern:** Fields have `data-show-when-field` and `data-show-when-value` attributes. When a token pill is clicked, JS manually sets `wrapper.dataset.hidden` on dependent fields.

**Changes:**

1. **Edit:** `ssr_python/static/js/propertiesPanel.js`
   - Add reactive state for field visibility conditions:
     ```js
     // Track current field values for conditional visibility
     let fieldValues = {};  // Will be exposed to Alpine
     
     export function propertiesState() {
         return {
             fieldValues: {},
             shouldShow(field, value) {
                 return !field || this.fieldValues[field] === value;
             }
         };
     }
     ```
   - When rendering token pills, update `fieldValues` instead of setting `dataset.hidden`
   - When pill clicked: `Alpine.store('props').fieldValues[fieldName] = selectedValue`

2. **Edit:** `ssr_python/templates/index.html`
   - Add `x-data="propertiesState()"` on properties panel container
   - Field wrappers get: `x-show="shouldShow('appearance.background.type', 'color')"`

**What could go wrong & how to verify:**
| Risk | Likelihood | Check |
|------|-----------|-------|
| Conditional fields stuck hidden | Medium — must initialize `fieldValues` from current component on selection change | Select button with gradient bg → gradient fields visible |
| Fields visible when they shouldn't be | Medium — `shouldShow()` logic must match previous `data-show-when` behavior exactly | Select "color" bg type → gradient/image fields hidden |
| Properties Apply still works | Low — `collectPropertyValues()` reads from DOM, not from Alpine state | Edit properties → Apply → preview updates |
| Field rendering broken | Low — only visibility logic changes, not field creation | All field types (text, number, color, select, pills) render correctly |

**Verification checklist:**
- [ ] All 1026 tests pass
- [ ] Select a button → properties panel shows fields
- [ ] Background type "color" → only color fields visible
- [ ] Switch to "gradient" → gradient fields appear, color fields hide
- [ ] Switch to "image" → image fields appear
- [ ] Select accordion → allowMultiple toggle shows correctly
- [ ] Select carousel → autoplay fields show/hide based on toggle
- [ ] Apply properties → preview updates correctly
- [ ] Select different component → fields update properly
- [ ] Deselect → properties panel clears

**Rollback:** Revert `propertiesPanel.js` and properties section of `index.html`. Two-file revert.

---

## Implementation Order

```
Phase 0 (Infrastructure) → verify → merge
  ↓
Phase 1 (History buttons) → verify → merge
  ↓
Phase 2 (Panel toggles) → verify → merge
  ↓
Phase 3 (Images panel) → verify → merge
  ↓
Phase 4 (Properties panel) → verify → merge
```

Each phase is a separate git branch/PR. Phase N+1 starts ONLY after Phase N passes all verification checks and is merged.

---

## Summary of Files Changed

| File | Phases | Change Type | Rollback Complexity |
|------|--------|-------------|---------------------|
| `ssr_python/static/js/alpine.min.js` | 0 | New vendor file | Delete file |
| `ssr_python/templates/index.html` | 0-4 | Add script tag + Alpine directives | Git revert |
| `ssr_python/static/css/style.css` | 0 | Add 1 CSS rule | Remove 1 line |
| `ssr_python/static/js/main.js` | 1 | Replace `updateHistoryButtons()` | Git revert |
| `ssr_python/static/js/events.js` | 2 | Simplify panel toggles | Git revert |
| `ssr_python/static/js/imagesPanel.js` | 3 | Rewrite as Alpine component | Git revert |
| `ssr_python/static/js/propertiesPanel.js` | 4 | Alpine conditional visibility | Git revert |

**Files with zero changes:** `swift-sites-runtime.js`, `preview_bridge.js`, `ssr_app.js`, `preview_frame.html`, all `templates/components/**`, `renderer.py`, all `config/**`, all `routes/**`, all `rag/**`, all `tests/**`.
