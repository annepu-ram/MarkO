# Component Tree Action Buttons — Implementation Plan

**Status:** COMPLETED (Feb 24, 2026)

## Context

The component tree (left sidebar "Page Components" panel) was previously **read-only** — it displayed the YAML component hierarchy but offered no way to manipulate components. Users had to edit YAML manually to move, insert, or delete components. This plan added action buttons to each tree node so users can:

1. **Move Up / Move Down** — Reorder a component within its parent
2. **Add Child** — Insert a new component inside a container (page, layout-column, layout-row, etc.)
3. **Add After** — Insert a sibling component below the selected component
4. **Delete** — Remove a component

All buttons appear on hover to keep the tree clean.

---

## Files Modified (5 files)

| # | File | Action |
|---|------|--------|
| 1 | `static/js/yamlUtils.js` | Added `insertComponentInDocument()`, `moveComponentInDocument()`, `getChildrenKey()` |
| 2 | `static/js/componentTree.js` | Added action buttons to tree nodes, component type picker popover, `initTreeActions()`, fixed accordion item children |
| 3 | `static/js/main.js` | Wired up tree action handlers (move, delete, add child, add after) |
| 4 | `static/css/style.css` | CSS for action buttons (hover reveal) and component picker popover |
| 5 | `static/icon-sprite.svg` | Added `icon-chevron-up` and `icon-plus` symbols |

---

## Step 1: SVG Sprite — Added Missing Icons

**File:** `ssr_python/static/icon-sprite.svg`

Added two new symbols (Lucide icons):
```xml
<symbol id="icon-chevron-up" viewBox="0 0 24 24"><path d="m18 15-6-6-6 6" /></symbol>
<symbol id="icon-plus" viewBox="0 0 24 24"><path d="M5 12h14"/><path d="M12 5v14"/></symbol>
```

---

## Step 2: YAML Utility Functions

**File:** `ssr_python/static/js/yamlUtils.js` — Added after `deleteComponentInDocument()`

### 2a. `getChildrenKey(componentName)` → `string | null`

Maps component names to their children array key:
```
page, layout-row, layout-column, form, video-background, hamburger → 'components'
columnsgrid, ticker → 'columns'
tabs → 'tabs'
carousel → 'slides'
accordion → 'items'
Everything else → null (leaf component)
```

### 2b. `insertComponentInDocument(doc, parentSeqPath, component, index?)` → `boolean`

Insert a new component into a parent sequence at a given index.

**Algorithm:**
1. Navigate to parent sequence using `parentSeqPath` (reuse same navigation pattern as `deleteComponentInDocument`)
2. If the sequence doesn't exist (empty container with no children key in YAML), navigate to the parent map and create it: `containerNode.set(key, doc.createNode([]))`
3. Create new YAML node: `doc.createNode(component)`
4. Splice into sequence at `index` (or append if index undefined)

**Key path examples:**
- "Add After" heading at path `[0, 'components', 0, 'components', 2]` → parentSeqPath = `[0, 'components', 0, 'components']`, index = 3
- "Add Child" into layout-column at path `[0, 'components', 0, 'components', 1]` → parentSeqPath = `[0, 'components', 0, 'components', 1, 'components']`
- "Add Child" into virtual columnsgrid column at path `[0, 'components', 2, 'columns', 0]` → parentSeqPath = `[0, 'components', 2, 'columns', 0, 'components']`

### 2c. `moveComponentInDocument(doc, componentPath, direction)` → `{ success, newPath }`

Swap a component with its adjacent sibling.

**Algorithm:**
1. Extract `index` (last segment) and `parentPath` (path without last segment)
2. Navigate to parent sequence
3. Calculate `targetIndex = index + direction` (-1 for up, +1 for down)
4. Boundary check: return `{ success: false }` if out of bounds
5. Swap: `[items[index], items[targetIndex]] = [items[targetIndex], items[index]]`
6. Return `{ success: true, newPath: [...parentPath, targetIndex] }`

---

## Step 3: Component Tree UI Changes

**File:** `ssr_python/static/js/componentTree.js`

### 3a. Button Visibility Rules — `getNodeActions(node, siblingCount, siblingIndex)`

| Node Type | Move Up | Move Down | Add Child | Add After | Delete |
|-----------|---------|-----------|-----------|-----------|--------|
| Page | No | No | Yes | No | No |
| Regular leaf (heading, image, etc.) | Yes* | Yes* | No | Yes | Yes |
| Simple container (layout-row, layout-column, form) | Yes* | Yes* | Yes | Yes | Yes |
| Complex container (columnsgrid, tabs, carousel, accordion, ticker) | Yes* | Yes* | Yes | Yes | Yes |
| Virtual node (column, tab panel, slide, accordion item) | No | No | Yes | No | No |

*Disabled if first (move up) or last (move down) in parent.

### 3b. Modified `renderTreeNode(node, depth, siblingCount, siblingIndex)`

Added a `.tree-actions` container after `.tree-label` inside `.tree-item-content`:

```
.tree-item-content
  ├── .tree-toggle
  ├── .tree-icon (svg)
  ├── .tree-label
  └── .tree-actions (hidden by default, flex on hover)
       ├── button.tree-action-btn[data-action="move-up"]     — icon-chevron-up
       ├── button.tree-action-btn[data-action="move-down"]   — icon-chevron-down
       ├── button.tree-action-btn[data-action="add-child"]   — icon-plus
       ├── button.tree-action-btn[data-action="add-after"]   — icon-plus
       └── button.tree-action-btn[data-action="delete"]      — icon-trash-2
```

Each button dispatches a `tree-action` CustomEvent with detail: `{ action, nodeId, path, name, isVirtual, isContainer, sourceElement }`.

Buttons call `e.stopPropagation()` to prevent triggering tree item selection.

### 3c. Component Type Picker — `showComponentPicker(anchorEl, callback)`

A floating popover positioned near the clicked button. Categories:

| Category | Components |
|----------|-----------|
| Layout | layout-row, layout-column, columnsgrid, form |
| Text | heading, paragraph, eyebrow, caption, blockquote, link |
| Media | image, video, gif, video-background, panorama-display |
| Interactive | tabs, accordion, carousel, hamburger, ticker |
| UI | button, titlebar, br |
| Marketing | icon, badge, rating, progress-bar, counter-up, countdown |
| Forms | textbox, textarea, dropdown, checkbox, radio, calendar |

Each item shows the component icon + name. Clicking calls `callback(componentName)` and dismisses the picker. Click-outside or Escape dismisses. Uses `position: fixed` with viewport boundary checks.

**When to show picker vs. direct insert:**
- "Add After" → always show picker
- "Add Child" on simple container (uses `components` key) → show picker
- "Add Child" on virtual node → show picker (adds into virtual node's `components`)
- "Add Child" on complex container (columnsgrid, tabs, carousel, accordion, ticker) → **no picker** — directly inserts a new structural group (empty column/tab/slide/item)

### 3d. New Export: `initTreeActions(container, onAction)`

Listens for `tree-action` events on the container, delegates to callback.

### 3e. Fixed Accordion Items — Recurse into Children

Previously accordion items were `isContainer: false` and didn't recurse into `item.components`. Fixed to match the pattern used by tabs/carousel/columnsgrid: set `isContainer: true`, `isExpanded: true`, and recurse into `item.components`.

---

## Step 4: Main Module — Action Handlers

**File:** `ssr_python/static/js/main.js`

### 4a. New Imports

Added to yamlUtils import: `insertComponentInDocument`, `moveComponentInDocument`, `getChildrenKey`
Added to componentTree import: `initTreeActions`, `showComponentPicker`

### 4b. Wire Up Tree Actions

After `initComponentTree()`, added:
```javascript
initTreeActions(dom.componentTree, (action, nodeData) => { ... });
```

### 4c. Handler Functions

All handlers follow the established pattern from the existing delete handler:
`get doc → manipulate → serialize → update editor → save → push history → re-render → update tree`

**`commitDocChange(yamlDoc)`** — Standard save/render flow extracted as helper.

**`buildNewComponent(componentName)`** — Creates component from defaults, separating component-level arrays from properties.

**Move Up/Down handler:**
1. `moveComponentInDocument(doc, path, direction)` → get `newPath`
2. Standard save/render flow
3. Select component at new path after re-render

**Delete handler:**
1. `deleteComponentInDocument(doc, path)`
2. Standard save/render flow
3. Clear selection

**Add Child handler:**
- If virtual node → `showComponentPicker()`, then insert into `[...path, 'components']`
- If complex container → directly insert structural group (empty column/tab/slide/item)
- If simple container → `showComponentPicker()`, then insert into `[...path, childrenKey]`

**Add After handler:**
- `showComponentPicker()`, then insert at `parentPath[siblingIndex + 1]`

---

## Step 5: CSS

**File:** `ssr_python/static/css/style.css` — Added after tree CSS section

### Tree Action Buttons
- `.tree-actions` — Hidden by default, flex on hover of `.tree-item-content`
- `.tree-action-btn` — 20x20px transparent buttons with 13x13px SVG icons
- Delete button gets red hover state
- Disabled buttons get 0.25 opacity

### Component Picker Popover
- `.tree-component-picker` — Fixed position, 190-230px wide, max 360px tall, scrollable
- `.tree-picker-category-label` — Uppercase 10px category headers
- `.tree-picker-item` — Flex row with icon + name, hover highlight

---

## Edge Cases Handled

1. **Empty containers** — Container may not have a `components` key in YAML yet. `insertComponentInDocument` creates the sequence.
2. **First/last items** — Move Up button only shown if not first child, Move Down only if not last.
3. **Virtual nodes** — Cannot be moved/deleted. Only "Add Child" available.
4. **Component-level arrays** — When inserting accordion/tabs/carousel/columnsgrid/ticker, defaults have `items`/`tabs`/`slides`/`columns` at top level. `buildNewComponent()` separates these from `properties`.
5. **Picker dismissal** — Click outside or Escape key closes the picker. Only one picker open at a time.
6. **Event propagation** — Action buttons call `stopPropagation()` so clicks don't also select the tree item.

---

## Verification Checklist

1. Hover over tree items — action buttons appear on right side
2. **Move Up/Down:** Move a heading up/down within a layout-column, verify YAML reorders
3. **Add After:** Click "Add After" on a paragraph → picker shows → select "button" → button appears below paragraph in tree and preview
4. **Add Child (simple container):** Click "Add Child" on layout-column → picker shows → select "heading" → heading appears as last child
5. **Add Child (complex container):** Click "Add Child" on columnsgrid → new empty column appears (no picker)
6. **Add Child (virtual node):** Click "Add Child" on a columnsgrid Column 1 → picker shows → select "image" → image appears inside that column
7. **Delete:** Click delete on a component → component removed, selection cleared
8. **Boundaries:** First child has no "Move Up" button, last child has no "Move Down" button
9. **Undo/Redo:** Each tree action pushes to history — Ctrl+Z undoes the operation
10. **YAML anchors:** After tree operations, theme color anchors/aliases remain intact
