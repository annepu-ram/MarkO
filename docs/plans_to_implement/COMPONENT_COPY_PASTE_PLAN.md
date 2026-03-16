# Component Copy/Paste + Auto-Copy on New Page

## Context

In multi-page sites, users build a homepage with a titlebar and footer, then add new pages that start completely blank — no titlebar, no theme, no fonts. Two features needed:

1. **Tree Copy/Paste** — Copy/Paste buttons on component tree nodes for manual cross-page copying
2. **Auto-copy on new page** — When creating a new page, automatically copy the homepage's theme/fonts and titlebar so new pages match the site's look

---

## Part A: Tree Copy/Paste

### How It Works

1. User selects a component in the tree → **Copy** button appears alongside existing actions
2. Click Copy → component data stored in module-level clipboard variable
3. User can switch to another page or stay on same page
4. On any tree node, a **Paste** button appears (only when clipboard has data)
5. Click Paste on a **container** (page, layout-row, etc.) → inserted as **last child**
6. Click Paste on a **leaf** (heading, paragraph, etc.) → inserted **after** the selected node
7. Clipboard persists until overwritten by another Copy or page unload

---

## Part B: Auto-Copy on New Page

### How It Works

1. Backend `create_page` loads the homepage's YAML
2. Extracts the theme (fonts + colors) from the site wrapper
3. Extracts the first component if it's a `titlebar`
4. Generates new page YAML with homepage's theme + titlebar pre-populated
5. Falls back to default template if homepage has no content

**Trade-off:** `yaml.dump()` produces inline values (no YAML anchors like `&color-primary`). This is acceptable — the page renders identically, and applying a theme via the themes panel re-creates anchors.

---

## Files to Modify (6 files)

| # | File | Change |
|---|------|--------|
| 1 | `static/icon-sprite.svg` | Add `icon-copy` and `icon-clipboard-paste` SVG symbols |
| 2 | `static/js/componentTree.js` | Add clipboard state, `copy`/`paste` to `getNodeActions()`, render buttons |
| 3 | `static/js/main.js` | Handle `copy` and `paste` tree actions in the switch statement |
| 4 | `static/css/style.css` | Hover styles for copy (green) and paste (blue) action buttons |
| 5 | `ssr_python/guards.py` | Add `generate_page_yaml_from_homepage()` helper |
| 6 | `ssr_python/routes/site.py` | Update `create_page` to use homepage as template |

---

## Step 1: Icon Sprite — `icon-sprite.svg`

Add two Lucide icons before `</svg>`:

```svg
<symbol id="icon-copy" viewBox="0 0 24 24">
  <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
</symbol>
<symbol id="icon-clipboard-paste" viewBox="0 0 24 24">
  <path d="M15 2H9a1 1 0 0 0-1 1v2c0 .6.4 1 1 1h6c.6 0 1-.4 1-1V3c0-.6-.4-1-1-1Z"/>
  <path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2M16 4h2a2 2 0 0 1 2 2v2"/>
  <path d="M21 14H11"/><path d="m15 10-4 4 4 4"/>
</symbol>
```

---

## Step 2: Component Tree — `componentTree.js`

### 2a. Module-level clipboard (top of file)

```javascript
let _clipboard = null; // { component: {...}, name: 'heading' }
export function getClipboard() { return _clipboard; }
export function setClipboard(data) { _clipboard = data; }
```

### 2b. Update `getNodeActions()` (~line 263)

Add `copy` and `paste` boolean flags. Pages/virtual nodes can receive paste but not be copied. Regular components can do both. Paste only shows when `_clipboard` is non-null.

### 2c. Render copy/paste buttons (~line 397, after move-down, before add-child)

Same pattern as existing buttons: create `<button>`, set `data-action`, add icon, dispatch `tree-action` custom event. Copy uses `icon-copy`, paste uses `icon-clipboard-paste`.

---

## Step 3: Main.js — Handle actions

### 3a. Import

```javascript
import { ..., getClipboard, setClipboard } from './componentTree.js';
```

### 3b. Add `copy` case (~line 397 in switch)

- `getComponentByPath(structure, path)` to extract component
- Deep clone via `JSON.parse(JSON.stringify(component))`
- `setClipboard({ component: cloned, name: component.name })`
- `updateComponentTree()` to refresh tree (shows paste buttons)
- Re-select the copied component

### 3c. Add `paste` case

- `getClipboard()` → get stored component data
- Deep clone the clipboard data (so pasting twice works)
- If target is **container** (isContainer || name === 'page' || isVirtual): `insertComponentInDocument(doc, [...path, childrenKey], pastedComponent)`
- If target is **leaf**: `insertComponentInDocument(doc, path.slice(0,-1), pastedComponent, path.at(-1) + 1)`
- `commitDocChange(yamlDoc)` — saves, re-renders, rebuilds tree

**Existing functions reused:**
- `getComponentByPath()` from yamlUtils.js — extracts component at path
- `insertComponentInDocument()` from yamlUtils.js — inserts into YAML Document AST
- `getChildrenKey()` from yamlUtils.js — resolves children array name per component type
- `commitDocChange()` from main.js — saves + renders + rebuilds tree

---

## Step 4: CSS — `style.css`

```css
.tree-action-btn[data-action="copy"]:hover {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
}
.tree-action-btn[data-action="paste"]:hover {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
}
```

---

## Step 5: Guards — `ssr_python/guards.py`

Add `generate_page_yaml_from_homepage()` function:

```python
def generate_page_yaml_from_homepage(homepage_yaml, slug, title):
    """Generate new page YAML based on homepage — copies theme + titlebar."""
    try:
        structure = yaml.safe_load(homepage_yaml)
        if not structure or not isinstance(structure, list):
            return generate_default_page_yaml(slug, title)

        site = structure[0]
        theme = (site.get('properties') or {}).get('theme', {})
        page = (site.get('components') or [{}])[0]
        page_components = page.get('components') or []

        # Extract titlebar if first component
        titlebar = None
        if page_components and page_components[0].get('name') == 'titlebar':
            titlebar = page_components[0]

        # Build new structure
        new_site = {
            'name': 'site',
            'properties': {'theme': theme} if theme else {},
            'components': [{
                'name': 'page',
                'slug': slug,
                'title': title,
                'properties': {
                    'appearance': {
                        'background': {
                            'color': (theme.get('colors', {}).get('background', '#ffffff')),
                            'transparency': 100
                        }
                    }
                },
                'components': [titlebar] if titlebar else []
            }]
        }

        return yaml.dump([new_site], default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception:
        return generate_default_page_yaml(slug, title)
```

Fallback to `generate_default_page_yaml()` if homepage parsing fails — always safe.

---

## Step 6: Route — `ssr_python/routes/site.py`

Update `create_page()` (~line 282) to use homepage as template:

```python
# Before: always used default template
yaml_content = generate_default_page_yaml(slug=slug, title=title)

# After: copy theme + titlebar from homepage
homepage = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
if homepage and homepage.yaml_content:
    yaml_content = generate_page_yaml_from_homepage(
        homepage.yaml_content, slug=slug, title=title
    )
else:
    yaml_content = generate_default_page_yaml(slug=slug, title=title)
```

Import `generate_page_yaml_from_homepage` from guards at the top.

---

## Verification

### Tree Copy/Paste
1. Load bookstore template → select titlebar in tree → Copy button visible → click it
2. Tree refreshes → Paste buttons appear on all nodes
3. Paste on page node → titlebar inserted as last child of page
4. Paste on a heading → titlebar inserted after the heading
5. Switch to Page 2 → Paste buttons still visible (clipboard persists in memory)
6. Paste on Page 2 → titlebar copied successfully
7. Copy a layout-row with nested children → paste preserves all nested components
8. Undo after paste → works correctly (commitDocChange pushes history)
9. Paste multiple times → each paste creates independent copy

### Auto-Copy on New Page
10. Create a site, build homepage with titlebar + theme colors
11. Add a new page → new page YAML includes homepage's theme (fonts, colors)
12. New page YAML includes the titlebar component from homepage
13. Preview renders new page with correct fonts and titlebar
14. If homepage has no titlebar → new page gets theme but empty components
15. If homepage is blank → falls back to default template (Inter font)
16. Run `python -m pytest ssr_python/tests/ -v` → all tests pass
