# Site-Level Header/Footer (Approach A) — Implementation Plan

## Context

Currently, the site component is a transparent wrapper that only renders its children (pages). Every page in a multi-page site must duplicate shared components like navigation bars and footers. Approach A adds `header` and `footer` arrays to the site component, rendered once and shared across all pages. This eliminates duplication and ensures consistent navigation/footer across pages.

**Goal:** Add `site.header[]` and `site.footer[]` component arrays that render before and after each page's content, while preserving 100% backward compatibility with existing YAML structures.

---

## YAML Structure (Before vs After)

### Before (current — duplicated titlebar in every page)
```yaml
- name: site
  id: "abc-123"
  components:
    - name: page
      components:
        - name: titlebar          # ← duplicated in every page
          properties: { ... }
        - name: heading
          properties: { text: "Welcome" }
        - name: layout-row
          properties: { ... }
          components: [ ... ]
```

### After (header/footer at site level)
```yaml
- name: site
  id: "abc-123"
  header:                          # ← NEW: shared across all pages
    - name: titlebar
      properties: { ... }
  footer:                          # ← NEW: shared across all pages
    - name: layout-row
      properties: { ... }
      components:
        - name: paragraph
          properties: { text: "Copyright 2026" }
  components:
    - name: page
      components:
        - name: heading
          properties: { text: "Welcome" }
        - name: layout-row
          properties: { ... }
          components: [ ... ]
```

---

## Files to Modify (10 files)

| # | File | Change |
|---|------|--------|
| 1 | `templates/components/layout/_site.html` | Render header → pages → footer |
| 2 | `config/component_defaults.yaml` | Add empty `header: []` and `footer: []` to site |
| 3 | `config/component_schemas.yaml` | Add header/footer schema groups to site |
| 4 | `renderer.py` | Handle `header`/`footer` arrays in merge_component_with_defaults |
| 5 | `static/js/componentTree.js` | Show header/footer sections in tree |
| 6 | `static/js/pathMapBuilder.js` | Traverse `header`/`footer` paths |
| 7 | `static/js/ssr_app.js` | Extract fonts/icons from header/footer too |
| 8 | `static/js/pageManager.js` | Expose header/footer accessors |
| 9 | `guards.py` | Update DEFAULT_PAGE_YAML_TEMPLATE (optional) |
| 10 | `tests/test_renderer.py` | Add regression tests |

---

## Step 1: Template — `_site.html`

**Current code** (transparent pass-through):
```jinja2
{% macro render_site(component, tokens, path, component_id) %}
    {% for child in component.components | default([]) %}
        {{ render_component(child, tokens, path + ['components', loop.index0]) }}
    {% endfor %}
{% endmacro %}
```

**New code** (renders header → pages → footer):
```jinja2
{% macro render_site(component, tokens, path, component_id) %}
    {# Render site-level header components (shared across all pages) #}
    {% for child in component.header | default([]) %}
        {{ render_component(child, tokens, path + ['header', loop.index0]) }}
    {% endfor %}

    {# Render pages (existing behavior) #}
    {% for child in component.components | default([]) %}
        {{ render_component(child, tokens, path + ['components', loop.index0]) }}
    {% endfor %}

    {# Render site-level footer components (shared across all pages) #}
    {% for child in component.footer | default([]) %}
        {{ render_component(child, tokens, path + ['footer', loop.index0]) }}
    {% endfor %}
{% endmacro %}
```

**Why this is safe:** When `header` and `footer` are absent or empty, the `| default([])` produces empty loops — zero output, identical to current behavior.

### Component ID paths

Header components get paths like:
- `[0, 'header', 0]` → `comp_0_header_0` (first header component)
- `[0, 'header', 0, 'components', 1]` → `comp_0_header_0_components_1`

Footer components:
- `[0, 'footer', 0]` → `comp_0_footer_0`

Page components (UNCHANGED):
- `[0, 'components', 0]` → `comp_0_components_0` (page)
- `[0, 'components', 0, 'components', 0]` → `comp_0_components_0_components_0` (first child of page)

**Critical:** Existing page component IDs do NOT change. Header/footer get their own unique path segments (`header`, `footer`), so there is zero collision with existing `components` paths.

---

## Step 2: Renderer — `renderer.py`

**Current `merge_component_with_defaults`** handles: `components`, `columns`, `tabs`, `slides`, `items`.

**Add** `header` and `footer` handling (same pattern as `components`):

```python
# After the existing 'components' block (line ~186):
if 'header' in merged_component:
    merged_component['header'] = [
        merge_component_with_defaults(child, defaults, tokens, f"{component_path}.header[{i}]")
        for i, child in enumerate(merged_component.get('header') or [])
    ]

if 'footer' in merged_component:
    merged_component['footer'] = [
        merge_component_with_defaults(child, defaults, tokens, f"{component_path}.footer[{i}]")
        for i, child in enumerate(merged_component.get('footer') or [])
    ]
```

**Why this is safe:** Only fires when `header`/`footer` keys exist. Existing site YAML without these keys is unaffected.

---

## Step 3: Defaults — `component_defaults.yaml`

**Current:**
```yaml
site:
  id: ''
```

**New:**
```yaml
site:
  id: ''
  header: []
  footer: []
```

**Why this is safe:** Empty arrays merge cleanly. `deep_merge({header: []}, {})` returns `{header: []}`. Sites without header/footer in YAML get empty arrays via defaults, producing zero output.

---

## Step 4: Schema — `component_schemas.yaml`

**Current:**
```yaml
site:
  groups: []
```

**New:**
```yaml
site:
  groups:
  - id: header
    label: Header
    fields:
    - path: header
      type: componentList
      label: Header Components
      target: component
      description: Components shared across all pages (rendered above page content)
  - id: footer
    label: Footer
    fields:
    - path: footer
      type: componentList
      label: Footer Components
      target: component
      description: Components shared across all pages (rendered below page content)
```

**Note:** The `componentList` type and `target: component` follow the existing pattern used by carousel slides, accordion items, etc. The properties panel will need a custom renderer for these (similar to `tickerItems` or `accordionItems` in `customRenderers.js`). For Phase 1, header/footer components can be added/edited via the component tree or YAML editor. The schema groups provide awareness that the feature exists.

---

## Step 5: Path Map Builder — `pathMapBuilder.js`

**Add** header/footer traversal in both `traverseStructure` and `traverseYamlStructure` methods.

In `traverseStructure` (line ~70, after the `components` block):

```javascript
// Traverse header (site-level shared components)
if (component.header && Array.isArray(component.header)) {
    const headerPath = [...path, 'header'];
    this.traverseStructure(component.header, headerPath);
}

// Traverse footer (site-level shared components)
if (component.footer && Array.isArray(component.footer)) {
    const footerPath = [...path, 'footer'];
    this.traverseStructure(component.footer, footerPath);
}
```

Same pattern in `traverseYamlStructure` (DOM-based version):

```javascript
// Traverse header
if (component.header && Array.isArray(component.header)) {
    const headerPath = [...path, 'header'];
    const headerParent = element || parentElement;
    this.traverseYamlStructure(component.header, headerPath, headerParent);
}

// Traverse footer
if (component.footer && Array.isArray(component.footer)) {
    const footerPath = [...path, 'footer'];
    const footerParent = element || parentElement;
    this.traverseYamlStructure(component.footer, footerPath, footerParent);
}
```

**Why this is safe:** Only fires when `header`/`footer` arrays exist on a component. No existing component uses these keys.

---

## Step 6: Component Tree — `componentTree.js`

### 6a. Update `hasChildren` to include header/footer

```javascript
const hasChildren = (component) => {
    if (!component) return false;
    return !!(
        component.components?.length ||
        component.columns?.length ||
        component.tabs?.length ||
        component.slides?.length ||
        component.items?.length ||
        component.header?.length ||    // NEW
        component.footer?.length       // NEW
    );
};
```

### 6b. Update `buildTreeFromStructure`

**Current:**
```javascript
export const buildTreeFromStructure = (structure) => {
    if (!Array.isArray(structure) || structure.length === 0) return [];
    const site = structure[0];
    return buildTreeNodes(site.components || [], [0, 'components']);
};
```

**New:**
```javascript
export const buildTreeFromStructure = (structure) => {
    if (!Array.isArray(structure) || structure.length === 0) return [];
    const site = structure[0];
    const nodes = [];

    // Header section (virtual group node)
    if (site.header?.length) {
        const headerNode = {
            id: 'comp_0_header',
            name: 'Header',
            path: [0, 'header'],
            icon: 'icon-credit-card',
            children: buildTreeNodes(site.header, [0, 'header']),
            isContainer: true,
            isExpanded: true,
            isVirtual: true
        };
        nodes.push(headerNode);
    }

    // Pages (existing behavior)
    nodes.push(...buildTreeNodes(site.components || [], [0, 'components']));

    // Footer section (virtual group node)
    if (site.footer?.length) {
        const footerNode = {
            id: 'comp_0_footer',
            name: 'Footer',
            path: [0, 'footer'],
            icon: 'icon-layout-row',
            children: buildTreeNodes(site.footer, [0, 'footer']),
            isContainer: true,
            isExpanded: true,
            isVirtual: true
        };
        nodes.push(footerNode);
    }

    return nodes;
};
```

**Why this is safe:** When `site.header` and `site.footer` are absent/empty, the conditions evaluate false and tree output is identical to current behavior.

### 6c. Update `buildTreeNodes` to handle header/footer on any component

Inside the `buildTreeNodes` function, add after the `items` handler:

```javascript
// Handle site header (component.header array)
if (component.header?.length) {
    node.children.push(...buildTreeNodes(
        component.header,
        [...currentPath, 'header']
    ));
}

// Handle site footer (component.footer array)
if (component.footer?.length) {
    node.children.push(...buildTreeNodes(
        component.footer,
        [...currentPath, 'footer']
    ));
}
```

---

## Step 7: SSR App — `ssr_app.js`

### 7a. Font extraction (`sendFontsToIframe`)

**Current** (line 126-128):
```javascript
const site = structure[0];
const page = site.components?.[0];
const fonts = page?.properties?.theme?.fonts;
```

**No change needed** — fonts are defined per-page in `page.properties.theme.fonts`. Header/footer components inherit page fonts via CSS variables (`--font-heading`, `--font-content`) that are set on the page wrapper div. Since header components render outside the page div, they won't inherit these CSS vars.

**Solution:** Also check the first page's fonts (same as current) — header/footer components should use the page's font theme. Since the `<div class="page">` wraps only page content and not header/footer, we need the font CSS vars to cascade from a higher level.

**Approach:** In `_site.html`, wrap all output in a div that carries the font CSS vars from the first page:

```jinja2
{% macro render_site(component, tokens, path, component_id) %}
    {# Extract font theme from first page for site-wide cascade #}
    {% set first_page = (component.components | default([]))[0] if component.components else none %}
    {% set theme = first_page.properties.theme | default({}) if first_page and first_page.properties else {} %}
    {% set theme_fonts = theme.fonts | default({}) %}
    {% set font_vars = '' %}
    {% if theme_fonts.heading %}
        {% set font_vars = font_vars ~ '--font-heading: ' ~ theme_fonts.heading ~ '; ' %}
    {% endif %}
    {% if theme_fonts.content %}
        {% set font_vars = font_vars ~ '--font-content: ' ~ theme_fonts.content ~ '; ' %}
    {% endif %}

    {% if font_vars or component.header or component.footer %}
    <div class="site-wrapper" style="{{ font_vars }}">
    {% endif %}

        {# Render site-level header components #}
        {% for child in component.header | default([]) %}
            {{ render_component(child, tokens, path + ['header', loop.index0]) }}
        {% endfor %}

        {# Render pages (existing behavior) #}
        {% for child in component.components | default([]) %}
            {{ render_component(child, tokens, path + ['components', loop.index0]) }}
        {% endfor %}

        {# Render site-level footer components #}
        {% for child in component.footer | default([]) %}
            {{ render_component(child, tokens, path + ['footer', loop.index0]) }}
        {% endfor %}

    {% if font_vars or component.header or component.footer %}
    </div>
    {% endif %}
{% endmacro %}
```

**WAIT — backward compatibility concern:** Adding a `<div class="site-wrapper">` changes the DOM structure. For sites WITHOUT header/footer, we should NOT add this wrapper. The condition `if font_vars or component.header or component.footer` ensures the wrapper only appears when needed. But `font_vars` will be truthy for any site with fonts (which is all of them).

**Better approach:** Only add the wrapper when header OR footer exist:

```jinja2
{% macro render_site(component, tokens, path, component_id) %}
    {% set has_header = component.header | default([]) | length > 0 %}
    {% set has_footer = component.footer | default([]) | length > 0 %}

    {% if has_header or has_footer %}
        {# Extract font theme from first page for site-wide cascade #}
        {% set first_page = (component.components | default([]))[0] if component.components else none %}
        {% set theme = first_page.properties.theme | default({}) if first_page and first_page.properties else {} %}
        {% set theme_fonts = theme.fonts | default({}) %}
        {% set font_vars = '' %}
        {% if theme_fonts.heading %}
            {% set font_vars = font_vars ~ '--font-heading: ' ~ theme_fonts.heading ~ '; ' %}
        {% endif %}
        {% if theme_fonts.content %}
            {% set font_vars = font_vars ~ '--font-content: ' ~ theme_fonts.content ~ '; ' %}
        {% endif %}
        <div class="site-wrapper" {% if font_vars %}style="{{ font_vars }}"{% endif %}>
    {% endif %}

    {# Render site-level header components #}
    {% for child in component.header | default([]) %}
        {{ render_component(child, tokens, path + ['header', loop.index0]) }}
    {% endfor %}

    {# Render pages (existing behavior) #}
    {% for child in component.components | default([]) %}
        {{ render_component(child, tokens, path + ['components', loop.index0]) }}
    {% endfor %}

    {# Render site-level footer components #}
    {% for child in component.footer | default([]) %}
        {{ render_component(child, tokens, path + ['footer', loop.index0]) }}
    {% endfor %}

    {% if has_header or has_footer %}
        </div>
    {% endif %}
{% endmacro %}
```

**This preserves backward compatibility:** Sites without header/footer produce identical output (no wrapper div). Sites WITH header/footer get a `<div class="site-wrapper">` that carries font CSS vars.

### 7b. Icon extraction (`extractIconNames`)

**Current** `walk()` handles: `components`, `columns`, `tabs`, `slides`.

**Add** header/footer:

```javascript
if (node.header) walk(node.header);
if (node.footer) walk(node.footer);
```

---

## Step 8: Page Manager — `pageManager.js`

No changes required for Phase 1. The `getPageFromStructure` and `getPageList` functions only deal with pages inside `site.components[]`, which remain unchanged.

**Future enhancement:** Add `getHeaderFromStructure(structure)` and `getFooterFromStructure(structure)` accessors when a header/footer editor UI is needed.

---

## Step 9: Guards — `guards.py` (Optional)

The `DEFAULT_PAGE_YAML_TEMPLATE` does NOT need to include `header`/`footer` initially. The defaults (`header: []`, `footer: []`) handle this via `deep_merge`. Users add header/footer components explicitly.

**No changes required for backward compatibility.**

---

## Step 10: CSS — `components.css`

Add minimal styling for the site wrapper:

```css
/* Site wrapper — only present when header or footer exist */
.site-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
```

---

## Step 11: Export/Fullscreen — `main.js`

The `buildStandaloneHtml` function receives the rendered HTML string from `/render`. Since header/footer are rendered server-side inside the HTML, no changes are needed — the exported HTML already includes them.

**No changes required.**

---

## Step 12: Publishing — `routes/site.py`

**Current behavior** (line 436): Each page's `yaml_content` is rendered independently:
```python
structure = yaml.safe_load(sp.yaml_content)
html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
```

Each page's `yaml_content` is the full site document (with site wrapper). When header/footer exist in the site YAML, they will automatically render with each page. **No changes needed** — the rendering is already per-document, not per-page-component.

**However**, if we want header/footer shared across pages in a multi-page site where each page has its own `yaml_content` (current data model), we need to inject header/footer from the site-level YAML into each page's YAML before rendering.

**Phase 1 approach:** Since the current editor works with a single YAML document containing the full site, and publishing renders that full document, header/footer will render correctly. Multi-page publishing (where pages are stored separately) is a future concern.

**No changes required for Phase 1.**

---

## Example Template Modifications

### Converting existing template (bookstore example)

**Before** (duplicated titlebar in page):
```yaml
- name: site
  id: "bookstore-site"
  components:
    - name: page
      id: "page-1"
      slug: "home"
      title: "The Book Nook"
      properties:
        theme:
          fonts:
            heading: &font-heading "'Playfair Display', serif"
            content: &font-content "'Inter', sans-serif"
          colors:
            primary: &color-primary "#1e293b"
            accent: &color-accent "#3b82f6"
            background: &color-background "#fefce8"
        appearance:
          background:
            color: *color-background
            transparency: 100
      components:
        - name: titlebar            # ← DUPLICATED per page
          properties:
            logo:
              text: "The Book Nook"
            links:
              items:
                - text: Home
                  url: "#"
                - text: Categories
                  url: "#categories"
        - name: heading
          properties:
            text: "Welcome to The Book Nook"
        # ... rest of page content
```

**After** (titlebar moved to site header):
```yaml
- name: site
  id: "bookstore-site"
  header:                            # ← MOVED here
    - name: titlebar
      properties:
        logo:
          text: "The Book Nook"
        links:
          items:
            - text: Home
              url: "#"
            - text: Categories
              url: "#categories"
  footer:                            # ← NEW
    - name: layout-row
      properties:
        spacing:
          paddingBlock: lg
        appearance:
          background:
            color: "#1e293b"
      components:
        - name: paragraph
          properties:
            text: "Copyright 2026 The Book Nook. All rights reserved."
            typography:
              color: "#ffffff"
              size: sm
  components:
    - name: page
      id: "page-1"
      slug: "home"
      title: "The Book Nook"
      properties:
        theme:
          fonts:
            heading: &font-heading "'Playfair Display', serif"
            content: &font-content "'Inter', sans-serif"
          colors:
            primary: &color-primary "#1e293b"
            accent: &color-accent "#3b82f6"
            background: &color-background "#fefce8"
        appearance:
          background:
            color: *color-background
            transparency: 100
      components:
        - name: heading
          properties:
            text: "Welcome to The Book Nook"
        # ... rest of page content (titlebar removed)
```

### Creating a new template with header/footer

```yaml
- name: site
  id: "demo-site"
  header:
    - name: titlebar
      properties:
        logo:
          text: "My Site"
        appearance:
          background:
            color: "#1e293b"
        links:
          items:
            - text: Home
              url: "/"
            - text: About
              url: "/about"
  footer:
    - name: br
      properties:
        style: solid
        appearance:
          color: "#e5e7eb"
    - name: layout-row
      properties:
        layout:
          horizontalAlign: center
        spacing:
          paddingBlock: md
      components:
        - name: paragraph
          properties:
            text: "Built with Swift Sites"
            typography:
              size: sm
              color: "#6b7280"
  components:
    - name: page
      id: "page-1"
      slug: "home"
      title: "Home"
      properties:
        theme:
          fonts:
            heading: "'Inter', sans-serif"
            content: "'Inter', sans-serif"
          colors:
            primary: "#1e293b"
            background: "#ffffff"
        appearance:
          background:
            color: "#ffffff"
            transparency: 100
      components:
        - name: heading
          properties:
            text: "Welcome Home"
            typography:
              size: xxxl
              weight: bold
```

---

## Backward Compatibility Guarantees

### 1. Existing YAML without header/footer renders identically

**Proof:**
- `_site.html`: `has_header` and `has_footer` are both false when keys are absent → no wrapper div, no extra output
- `renderer.py`: `if 'header' in merged_component` is false → no extra merge
- `componentTree.js`: `if (site.header?.length)` is falsy → no header node in tree
- `pathMapBuilder.js`: `if (component.header && ...)` is false → no extra traversal

### 2. Existing component IDs are unchanged

Header gets paths `[0, 'header', N]` → IDs `comp_0_header_N`.
Footer gets paths `[0, 'footer', N]` → IDs `comp_0_footer_N`.
Page paths remain `[0, 'components', N]` → IDs `comp_0_components_N`.
No collision, no shift.

### 3. Test fixture uses `[{name: 'page'}]` (no site wrapper)

The test fixture `sample_page.yaml` starts with `name: page` (not `name: site`). These tests render the page directly without a site wrapper. Since we're not changing page rendering, all existing tests pass unchanged.

### 4. Existing templates continue to work

Templates without `header`/`footer` keys in the YAML are completely unaffected. The defaults add `header: []` and `footer: []` to the site, but empty arrays produce zero output.

---

## Regression Tests

Add to `tests/test_renderer.py`:

### Test 1: Existing page-only structure still renders correctly
```python
def test_render_page_without_site_wrapper(self, app):
    """Page-only YAML (no site wrapper) still renders correctly."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: page
  properties:
    appearance:
      background:
        color: '#ffffff'
        transparency: 100
  components:
    - name: heading
      properties:
        text: Regression Test
        typography:
          size: lg
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'class="page"' in html
        assert 'Regression Test' in html
        assert 'comp_0' in html
        assert 'comp_0_components_0' in html
        # No site-wrapper div should appear
        assert 'site-wrapper' not in html
```

### Test 2: Site wrapper without header/footer renders identically to current
```python
def test_site_without_header_footer_no_wrapper(self, app):
    """Site with no header/footer produces no wrapper div (backward compatible)."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: site
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: heading
          properties:
            text: No Header Footer
            typography:
              size: lg
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'No Header Footer' in html
        assert 'class="page"' in html
        # Must NOT have site-wrapper when no header/footer
        assert 'site-wrapper' not in html
```

### Test 3: Site with header renders header before page
```python
def test_site_with_header_renders_before_page(self, app):
    """Site header components render before page content."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: site
  header:
    - name: heading
      properties:
        text: Site Header
        typography:
          size: lg
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: heading
          properties:
            text: Page Content
            typography:
              size: lg
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'Site Header' in html
        assert 'Page Content' in html
        assert 'site-wrapper' in html
        # Header should appear before page content
        header_pos = html.index('Site Header')
        page_pos = html.index('Page Content')
        assert header_pos < page_pos
```

### Test 4: Site with footer renders after page
```python
def test_site_with_footer_renders_after_page(self, app):
    """Site footer components render after page content."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: site
  footer:
    - name: heading
      properties:
        text: Site Footer
        typography:
          size: lg
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: heading
          properties:
            text: Page Content
            typography:
              size: lg
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'Site Footer' in html
        assert 'Page Content' in html
        # Footer should appear after page content
        footer_pos = html.index('Site Footer')
        page_pos = html.index('Page Content')
        assert footer_pos > page_pos
```

### Test 5: Header/footer component IDs use correct paths
```python
def test_header_footer_component_ids(self, app):
    """Header and footer components get correct component IDs."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: site
  header:
    - name: heading
      properties:
        text: Header Heading
        typography:
          size: lg
  footer:
    - name: paragraph
      properties:
        text: Footer Text
        typography:
          size: sm
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: heading
          properties:
            text: Page Heading
            typography:
              size: lg
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        # Header component: path [0, 'header', 0] → comp_0_header_0
        assert 'comp_0_header_0' in html
        # Footer component: path [0, 'footer', 0] → comp_0_footer_0
        assert 'comp_0_footer_0' in html
        # Page: path [0, 'components', 0] → comp_0_components_0
        assert 'comp_0_components_0' in html
        # Page child: path [0, 'components', 0, 'components', 0]
        assert 'comp_0_components_0_components_0' in html
```

### Test 6: Existing test fixture still passes with site defaults
```python
def test_existing_fixture_unchanged(self, app, sample_page_structure):
    """Existing sample_page.yaml fixture renders exactly as before."""
    with app.app_context():
        html = render_yaml_structure(sample_page_structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        # All existing assertions from test_render_nested_components
        assert 'Hello World' in html
        assert 'comp_0' in html
        assert 'comp_0_components_2' in html
        assert 'comp_0_components_2_components_0' in html
        assert 'comp_0_components_2_components_1' in html
        # Must not have site wrapper
        assert 'site-wrapper' not in html
```

### Test 7: Header with nested layout components
```python
def test_header_with_nested_components(self, app):
    """Header can contain layout components with nested children."""
    with app.app_context():
        import yaml
        structure = yaml.safe_load("""
- name: site
  header:
    - name: layout-row
      properties:
        layout:
          wrap: nowrap
      components:
        - name: heading
          properties:
            text: Logo
            typography:
              size: lg
        - name: button
          properties:
            text: Sign Up
  components:
    - name: page
      properties:
        appearance:
          background:
            color: '#ffffff'
            transparency: 100
      components:
        - name: paragraph
          properties:
            text: Body
""")
        html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
        assert 'Logo' in html
        assert 'Sign Up' in html
        assert 'Body' in html
        # Nested: [0, 'header', 0, 'components', 0] → comp_0_header_0_components_0
        assert 'comp_0_header_0_components_0' in html
        assert 'comp_0_header_0_components_1' in html
```

---

## Implementation Order

1. **`renderer.py`** — Add header/footer to `merge_component_with_defaults` (safe, no-op when absent)
2. **`component_defaults.yaml`** — Add `header: []` and `footer: []` to site defaults
3. **`_site.html`** — Render header → pages → footer with conditional wrapper
4. **`components.css`** — Add `.site-wrapper` styles
5. **`component_schemas.yaml`** — Add header/footer schema groups
6. **`pathMapBuilder.js`** — Add header/footer traversal
7. **`componentTree.js`** — Show header/footer in tree
8. **`ssr_app.js`** — Add header/footer to icon extraction
9. **`tests/test_renderer.py`** — Add all 7 regression tests
10. **Run all tests** — Verify all 30 existing + 7 new tests pass

---

## Verification Checklist

1. Run `python -m pytest tests/ -v` — all existing 30 tests pass
2. Run the 7 new regression tests — all pass
3. Load existing YAML (e.g., bookstore_template.yaml) — renders identically
4. Load YAML with header/footer — header appears above page, footer below
5. Component tree shows Header/Footer sections when present
6. Click header/footer components in preview — selection works
7. Properties panel opens for header/footer components
8. Export HTML includes header/footer
9. Fullscreen preview includes header/footer
