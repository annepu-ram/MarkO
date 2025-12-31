# SSR Component Selection & Properties Editing Plan

## Overview

This plan outlines the implementation of component selection and properties editing functionality in the SSR (Server-Side Rendering) application, matching the behavior of the original CSR (Client-Side Rendering) app.

**Goal:** Enable users to:
1. Click components in the preview to select them
2. View and edit component properties in the properties panel
3. Apply changes and see updates reflected in the preview
4. Map component IDs to YAML line numbers for precise editing

---

## Architecture Overview

### Current State (SSR)
- ✅ Server renders HTML from YAML using Jinja2 templates
- ✅ Client sends YAML to `/render` endpoint, receives HTML
- ❌ No component IDs in rendered HTML
- ❌ No component selection mechanism
- ❌ No properties panel integration
- ❌ No YAML update mechanism

### Target State
- ✅ Server renders HTML with component IDs (`data-component-id`)
- ✅ Client builds component path map from rendered HTML
- ✅ Client handles component selection and highlighting
- ✅ Client renders properties panel using component schemas
- ✅ Client updates YAML and re-renders preview

---

## Implementation Plan

### Phase 1: Server-Side Component ID Generation

**Goal:** Add unique component IDs to all rendered components in Jinja2 templates.

#### Step 1.1: Create Component ID Generation Function

**File:** `ssr_python/renderer.py`

Add a function to generate unique component IDs based on component path:

```python
import hashlib

def generate_component_id(path):
    """
    Generate a unique component ID from a YAML path.
    Path format: [0, 'components', 1, 'components', 2]
    Returns: 'comp_0_components_1_components_2'
    """
    if not path:
        return 'comp_root'
    
    # Convert path to string representation
    path_str = '_'.join(str(segment) for segment in path)
    
    # Create hash for uniqueness (optional, for very long paths)
    if len(path_str) > 50:
        hash_obj = hashlib.md5(path_str.encode())
        return f'comp_{hash_obj.hexdigest()[:12]}'
    
    return f'comp_{path_str}'
```

#### Step 1.2: Modify `render_yaml_structure()` to Track Paths

**File:** `ssr_python/renderer.py`

Update the template to pass path information:

```python
def render_yaml_structure(structure, tokens=None):
    # ... existing validation code ...
    
    template = """
        {% import 'macros/_components.html' as components %}
        {% for component in structure %}
            {{ components.render_component(component, tokens, [loop.index0]) }}
        {% endfor %}
    """
    
    return render_template_string(template, structure=structure, tokens=tokens)
```

#### Step 1.3: Update Component Macros to Accept and Use Path

**File:** `ssr_python/templates/macros/_components.html`

Modify `render_component()` macro signature:

```jinja2
{% macro render_component(component, tokens, path=[]) %}
    {% set component_id = 'comp_' ~ path | join('_') %}
    {% set name = component.name %}
    
    {# Add data-component-id to all component outputs #}
    {% if name == 'page' %}
        {{ render_page(component, tokens, path, component_id) }}
    {% elif name == 'layout-row' %}
        {{ render_layout_row(component, tokens, path, component_id) }}
    {# ... etc ... #}
{% endmacro %}
```

#### Step 1.4: Update Individual Component Macros

**Example for `render_page`:**

```jinja2
{% macro render_page(component, tokens, path, component_id) %}
    {% set page_styles = build_styles(component, tokens) %}
    <div class="chrome-target-page" data-component-id="{{ component_id }}"{% if page_styles %} style="{{ page_styles }}"{% endif %}>
        {% for child in component.components | default([]) %}
            {% set child_path = path + ['components', loop.index0] %}
            {{ render_component(child, tokens, child_path) }}
        {% endfor %}
    </div>
{% endmacro %}
```

**Example for `render_text_component`:**

```jinja2
{% macro render_text_component(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set name = component.name %}
    {% set tag = 'h' ~ (properties.level | default(1)) if name == 'heading' else name %}
    {% set styles = build_styles(component, tokens) %}
    
    <{{ tag }} class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }}"{% endif %}>
        {{ properties.text | default('') | escape }}
    </{{ tag }}>
{% endmacro %}
```

**Key Changes:**
- Add `path` parameter to all macros
- Add `component_id` parameter (generated from path)
- Add `data-component-id="{{ component_id }}"` to all component HTML elements
- Add `class="chrome-target"` or `class="chrome-target-page"` for selection styling
- Pass updated path to nested component renders

#### Step 1.5: Add Chrome UI Elements (Optional for SSR)

For visual selection feedback, add chrome elements similar to CSR:

```jinja2
{% macro render_text_component(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set name = component.name %}
    {% set tag = 'h' ~ (properties.level | default(1)) if name == 'heading' else name %}
    {% set styles = build_styles(component, tokens) %}
    
    <{{ tag }} class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>
        <span class="chrome-label">{{ name }}</span>
        {{ properties.text | default('') | escape }}
    </{{ tag }}>
{% endmacro %}
```

**Note:** Chrome delete buttons can be added later if needed. For now, focus on selection.

---

### Phase 2: Client-Side Component Path Map Building

**Goal:** Build a map of component IDs to YAML paths from the rendered HTML.

#### Step 2.1: Create Path Map Builder Module

**File:** `ssr_python/static/js/pathMapBuilder.js`

```javascript
/**
 * Builds a map of component IDs to YAML paths from rendered HTML.
 * Parses data-component-id attributes and reconstructs paths from DOM structure.
 */

export class ComponentPathMapBuilder {
    constructor() {
        this.pathMap = new Map();
        this.yamlStructure = null;
    }

    /**
     * Build path map from rendered HTML and YAML structure
     * @param {HTMLElement} previewElement - The preview container
     * @param {Array} yamlStructure - The parsed YAML structure
     */
    buildPathMap(previewElement, yamlStructure) {
        this.yamlStructure = yamlStructure;
        this.pathMap.clear();
        
        // Traverse YAML structure and match with DOM elements
        this.traverseYamlStructure(yamlStructure, [], previewElement);
        
        return this.pathMap;
    }

    /**
     * Recursively traverse YAML structure and match with DOM elements
     */
    traverseYamlStructure(structure, currentPath, parentElement) {
        if (!Array.isArray(structure)) {
            return;
        }

        structure.forEach((component, index) => {
            const path = [...currentPath, index];
            
            // Find corresponding DOM element
            const componentId = this.generateComponentId(path);
            const element = parentElement.querySelector(`[data-component-id="${componentId}"]`);
            
            if (element) {
                this.pathMap.set(componentId, path);
            }

            // Traverse nested components
            if (component.components && Array.isArray(component.components)) {
                const childPath = [...path, 'components'];
                this.traverseYamlStructure(component.components, childPath, element || parentElement);
            }

            // Traverse columns (for columnsgrid)
            if (component.columns && Array.isArray(component.columns)) {
                component.columns.forEach((column, colIndex) => {
                    const colPath = [...path, 'columns', colIndex];
                    if (column.components) {
                        const colComponentsPath = [...colPath, 'components'];
                        this.traverseYamlStructure(column.components, colComponentsPath, element || parentElement);
                    }
                });
            }

            // Traverse tabs
            if (component.tabs && Array.isArray(component.tabs)) {
                component.tabs.forEach((tab, tabIndex) => {
                    const tabPath = [...path, 'tabs', tabIndex];
                    if (tab.components) {
                        const tabComponentsPath = [...tabPath, 'components'];
                        this.traverseYamlStructure(tab.components, tabComponentsPath, element || parentElement);
                    }
                });
            }

            // Traverse carousel slides
            if (component.slides && Array.isArray(component.slides)) {
                component.slides.forEach((slide, slideIndex) => {
                    const slidePath = [...path, 'slides', slideIndex];
                    if (slide.components) {
                        const slideComponentsPath = [...slidePath, 'components'];
                        this.traverseYamlStructure(slide.components, slideComponentsPath, element || parentElement);
                    }
                });
            }
        });
    }

    /**
     * Generate component ID from path (must match server-side generation)
     */
    generateComponentId(path) {
        if (!path || path.length === 0) {
            return 'comp_root';
        }
        return 'comp_' + path.join('_');
    }

    /**
     * Get path for a component ID
     */
    getPath(componentId) {
        return this.pathMap.get(componentId) || null;
    }

    /**
     * Get all paths
     */
    getAllPaths() {
        return new Map(this.pathMap);
    }
}
```

#### Step 2.2: Integrate Path Map Builder into SSR App

**File:** `ssr_python/static/js/ssr_app.js`

```javascript
import { ComponentPathMapBuilder } from './pathMapBuilder.js';

const pathMapBuilder = new ComponentPathMapBuilder();

export const renderPreview = async (yamlContent, yamlStructure) => {
    const preview = document.getElementById('preview');
    if (!preview) return;

    try {
        const response = await fetch('/render', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-yaml' },
            body: yamlContent
        });

        if (!response.ok) {
            // ... error handling ...
            return;
        }

        const htmlContent = await response.text();
        preview.innerHTML = htmlContent;

        // Build component path map after rendering
        pathMapBuilder.buildPathMap(preview, yamlStructure);

        // Initialize components
        initializeAllComponents();
    } catch (error) {
        // ... error handling ...
    }
};

export const getPathMapBuilder = () => pathMapBuilder;
```

---

### Phase 3: Component Selection & Highlighting

**Goal:** Enable clicking components to select them and highlight selected components.

#### Step 3.1: Create Selection Manager Module

**File:** `ssr_python/static/js/selectionManager.js`

```javascript
import { getPathMapBuilder } from './ssr_app.js';

export class SelectionManager {
    constructor() {
        this.selectedComponentId = null;
        this.selectedPath = null;
        this.onSelectionChange = null; // Callback function
    }

    /**
     * Handle click on preview area
     */
    handlePreviewClick(event) {
        // Find the closest component element
        const componentElement = event.target.closest('[data-component-id]');
        
        if (!componentElement) {
            this.clearSelection();
            return;
        }

        // Prevent selection if clicking on chrome delete button
        if (event.target.classList.contains('chrome-delete')) {
            return;
        }

        const componentId = componentElement.getAttribute('data-component-id');
        this.selectComponent(componentId);
    }

    /**
     * Select a component by ID
     */
    selectComponent(componentId) {
        const pathMapBuilder = getPathMapBuilder();
        const path = pathMapBuilder.getPath(componentId);

        if (!path) {
            console.warn(`No path found for component ID: ${componentId}`);
            return;
        }

        // Clear previous selection
        this.clearHighlight();

        // Set new selection
        this.selectedComponentId = componentId;
        this.selectedPath = path;

        // Highlight selected component
        this.highlightComponent(componentId);

        // Notify listeners
        if (this.onSelectionChange) {
            this.onSelectionChange({
                componentId,
                path
            });
        }
    }

    /**
     * Clear selection
     */
    clearSelection() {
        this.clearHighlight();
        this.selectedComponentId = null;
        this.selectedPath = null;

        if (this.onSelectionChange) {
            this.onSelectionChange(null);
        }
    }

    /**
     * Highlight a component
     */
    highlightComponent(componentId) {
        const preview = document.getElementById('preview');
        if (!preview) return;

        const element = preview.querySelector(`[data-component-id="${componentId}"]`);
        if (element) {
            element.classList.add('selected');
            // Scroll into view if needed
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /**
     * Clear highlight
     */
    clearHighlight() {
        const preview = document.getElementById('preview');
        if (!preview) return;

        const selectedElements = preview.querySelectorAll('.selected');
        selectedElements.forEach(el => el.classList.remove('selected'));
    }

    /**
     * Get current selection
     */
    getSelection() {
        return {
            componentId: this.selectedComponentId,
            path: this.selectedPath
        };
    }
}
```

#### Step 3.2: Add Selection CSS

**File:** `ssr_python/static/css/components.css`

```css
/* Component selection highlighting */
.chrome-target.selected,
.chrome-target-page.selected {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* Chrome label styling */
.chrome-label {
    position: absolute;
    top: -20px;
    left: 0;
    background: #3b82f6;
    color: white;
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 3px;
    pointer-events: none;
    z-index: 1000;
    white-space: nowrap;
}

.chrome-target-page .chrome-label {
    top: -24px;
}
```

#### Step 3.3: Integrate Selection Manager

**File:** `ssr_python/static/js/main.js` or `ssr_python/static/js/events.js`

```javascript
import { SelectionManager } from './selectionManager.js';

const selectionManager = new SelectionManager();

// Set up preview click handler
const preview = document.getElementById('preview');
if (preview) {
    preview.addEventListener('click', (event) => {
        selectionManager.handlePreviewClick(event);
    });
}

// Export for use in other modules
export { selectionManager };
```

---

### Phase 4: Properties Panel Integration

**Goal:** Display component properties in the properties panel when a component is selected.

#### Step 4.1: Load Component Schemas and Defaults

**File:** `ssr_python/static/js/metadataLoader.js`

```javascript
/**
 * Loads component schemas and defaults from YAML files
 * These are the same files used in CSR: component_schemas.yaml and component_defaults.yaml
 */

let componentSchemas = {};
let componentDefaults = {};
let schemaTokens = {};

export async function loadMetadata() {
    try {
        // Load component schemas
        const schemasResponse = await fetch('/static/component_schemas.yaml');
        const schemasText = await schemasResponse.text();
        // Parse YAML (you'll need a YAML parser like js-yaml)
        componentSchemas = parseYaml(schemasText);

        // Load component defaults
        const defaultsResponse = await fetch('/static/component_defaults.yaml');
        const defaultsText = await defaultsResponse.text();
        componentDefaults = parseYaml(defaultsText);

        // Load schema tokens
        const tokensResponse = await fetch('/static/schema_tokens.yaml');
        const tokensText = await tokensResponse.text();
        schemaTokens = parseYaml(tokensText);

        return true;
    } catch (error) {
        console.error('Failed to load metadata:', error);
        return false;
    }
}

export function getComponentSchema(componentName) {
    return componentSchemas[componentName] || null;
}

export function getComponentDefaults(componentName) {
    return componentDefaults[componentName] || {};
}

export function getSchemaTokens() {
    return schemaTokens;
}

// Simple YAML parser (or use js-yaml library)
function parseYaml(yamlText) {
    // For now, use a simple approach or integrate js-yaml
    // You can add js-yaml via CDN or npm
    if (typeof jsyaml !== 'undefined') {
        return jsyaml.load(yamlText);
    }
    // Fallback: return empty object
    console.warn('YAML parser not available');
    return {};
}
```

**Alternative:** Serve schemas as JSON from Flask:

**File:** `ssr_python/app.py`

```python
import yaml
import json

@app.route('/api/schemas')
def get_schemas():
    with open('component_schemas.yaml', 'r') as f:
        schemas = yaml.safe_load(f)
    return jsonify(schemas)

@app.route('/api/defaults')
def get_defaults():
    with open('component_defaults.yaml', 'r') as f:
        defaults = yaml.safe_load(f)
    return jsonify(defaults)

@app.route('/api/tokens')
def get_tokens():
    with open('schema_tokens.yaml', 'r') as f:
        tokens = yaml.safe_load(f)
    return jsonify(tokens)
```

#### Step 4.2: Reuse CSR Properties Panel Code

**Option A: Copy and Adapt CSR Properties Code**

Copy `js/properties/index.js` to `ssr_python/static/js/properties/index.js` and adapt:

- Remove CSR-specific imports (like `getYamlStructure` from state)
- Add SSR-specific functions to get YAML structure from editor
- Keep all rendering logic the same

**Option B: Create SSR-Specific Properties Panel**

Create a simplified version that works with SSR architecture.

**File:** `ssr_python/static/js/propertiesPanel.js`

```javascript
import { getComponentSchema, getComponentDefaults, getSchemaTokens } from './metadataLoader.js';
import { getYamlStructureFromEditor } from './yamlUtils.js';

let activeComponentName = null;
let activeFieldMeta = new Map();

/**
 * Render properties panel for selected component
 */
export function renderPropertiesPanel(component, componentId, path) {
    const propertiesContent = document.getElementById('propertiesContent');
    if (!propertiesContent) return;

    if (!component || !componentId) {
        propertiesContent.innerHTML = '<p class="properties-empty-state">Select a component to edit.</p>';
        return;
    }

    activeComponentName = component.name;
    activeFieldMeta.clear();

    const schema = getComponentSchema(component.name);
    if (!schema) {
        propertiesContent.innerHTML = '<p>No schema available for this component.</p>';
        return;
    }

    const defaults = getComponentDefaults(component.name);
    const resolvedProps = deepMerge({}, defaults, component.properties || {});

    propertiesContent.innerHTML = '';
    const formContainer = document.createElement('div');
    formContainer.className = 'properties-form';

    // Render schema groups and fields
    schema.groups?.forEach(group => {
        const groupEl = document.createElement('div');
        groupEl.className = 'property-group';
        
        const groupTitle = document.createElement('h3');
        groupTitle.className = 'property-group-title';
        groupTitle.textContent = group.label || group.id;
        groupEl.appendChild(groupTitle);

        group.fields?.forEach(field => {
            const fieldEl = renderField(field, resolvedProps, component);
            if (fieldEl) {
                groupEl.appendChild(fieldEl);
            }
        });

        formContainer.appendChild(groupEl);
    });

    propertiesContent.appendChild(formContainer);

    // Add Apply button
    const applyButton = document.createElement('button');
    applyButton.className = 'properties-apply-button';
    applyButton.textContent = 'Apply Changes';
    applyButton.addEventListener('click', () => {
        applyProperties(componentId, path);
    });
    propertiesContent.appendChild(applyButton);
}

/**
 * Render a single property field
 */
function renderField(field, resolvedProps, component) {
    // Similar to CSR implementation
    // Create input based on field.type (text, number, select, color, etc.)
    // Store field metadata in activeFieldMeta
    // Return field wrapper element
}

/**
 * Apply properties to component
 */
function applyProperties(componentId, path) {
    const yamlStructure = getYamlStructureFromEditor();
    const component = getComponentByPath(yamlStructure, path);
    
    if (!component) return;

    // Read form values and update component
    // Similar to CSR applyPropertiesForComponent
    
    // Update YAML editor
    const updatedYaml = generateYamlFromStructure(yamlStructure);
    updateYamlEditor(updatedYaml);
    
    // Re-render preview
    renderPreview(updatedYaml, yamlStructure);
}
```

#### Step 4.3: Connect Selection to Properties Panel

**File:** `ssr_python/static/js/main.js`

```javascript
import { selectionManager } from './selectionManager.js';
import { renderPropertiesPanel } from './propertiesPanel.js';
import { getYamlStructureFromEditor, getComponentByPath } from './yamlUtils.js';

selectionManager.onSelectionChange = (selection) => {
    if (!selection) {
        // Clear properties panel
        const propertiesContent = document.getElementById('propertiesContent');
        if (propertiesContent) {
            propertiesContent.innerHTML = '<p class="properties-empty-state">Select a component to edit.</p>';
        }
        return;
    }

    // Get component from YAML structure
    const yamlStructure = getYamlStructureFromEditor();
    const component = getComponentByPath(yamlStructure, selection.path);

    if (component) {
        renderPropertiesPanel(component, selection.componentId, selection.path);
    }
};
```

---

### Phase 5: YAML Update & Re-rendering

**Goal:** Update YAML when properties change and re-render preview.

#### Step 5.1: Create YAML Utilities Module

**File:** `ssr_python/static/js/yamlUtils.js`

```javascript
import yaml from 'js-yaml'; // Or use CDN version

/**
 * Get YAML structure from editor
 */
export function getYamlStructureFromEditor() {
    const editor = document.getElementById('codeEditor');
    if (!editor) return null;

    try {
        return yaml.load(editor.value) || [];
    } catch (error) {
        console.error('Failed to parse YAML:', error);
        return null;
    }
}

/**
 * Get component by path
 */
export function getComponentByPath(structure, path) {
    if (!structure || !path || path.length === 0) {
        return null;
    }

    let cursor = structure;
    for (const segment of path) {
        if (cursor === null || cursor === undefined) {
            return null;
        }
        cursor = cursor[segment];
    }
    return cursor || null;
}

/**
 * Update component by path
 */
export function updateComponentByPath(structure, path, newComponent) {
    if (!structure || !path) {
        return structure;
    }

    const newStructure = deepClone(structure);
    
    if (path.length === 0) {
        return newComponent;
    }

    let cursor = newStructure;
    for (let i = 0; i < path.length - 1; i++) {
        cursor = cursor[path[i]];
    }
    cursor[path[path.length - 1]] = newComponent;

    return newStructure;
}

/**
 * Generate YAML string from structure
 */
export function generateYamlFromStructure(structure) {
    try {
        return yaml.dump(structure, {
            indent: 2,
            lineWidth: -1,
            noRefs: true,
            sortKeys: false
        });
    } catch (error) {
        console.error('Failed to generate YAML:', error);
        return '';
    }
}

/**
 * Update YAML editor
 */
export function updateYamlEditor(yamlText) {
    const editor = document.getElementById('codeEditor');
    if (editor) {
        editor.value = yamlText;
        // Trigger input event to notify listeners
        editor.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

/**
 * Deep clone utility
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}
```

#### Step 5.2: Integrate YAML Updates with Preview Rendering

**File:** `ssr_python/static/js/ssr_app.js`

```javascript
import { renderPreview } from './ssr_app.js';
import { getYamlStructureFromEditor, generateYamlFromStructure } from './yamlUtils.js';
import { getPathMapBuilder } from './pathMapBuilder.js';

/**
 * Apply properties and re-render
 */
export async function applyPropertiesAndRender(componentId, path, updatedComponent) {
    // Get current YAML structure
    const yamlStructure = getYamlStructureFromEditor();
    
    // Update component in structure
    const updatedStructure = updateComponentByPath(yamlStructure, path, updatedComponent);
    
    // Generate YAML string
    const yamlText = generateYamlFromStructure(updatedStructure);
    
    // Update editor
    updateYamlEditor(yamlText);
    
    // Re-render preview
    await renderPreview(yamlText, updatedStructure);
    
    // Restore selection after re-render
    setTimeout(() => {
        selectionManager.selectComponent(componentId);
    }, 100);
}
```

---

## File Structure Summary

### New Files to Create

```
ssr_python/
├── static/
│   ├── js/
│   │   ├── pathMapBuilder.js          # NEW: Builds component ID → path map
│   │   ├── selectionManager.js        # NEW: Handles component selection
│   │   ├── propertiesPanel.js        # NEW: Renders properties panel
│   │   ├── metadataLoader.js          # NEW: Loads schemas/defaults
│   │   └── yamlUtils.js               # NEW: YAML manipulation utilities
│   └── css/
│       └── components.css             # UPDATE: Add selection styles
├── templates/
│   └── macros/
│       └── _components.html           # UPDATE: Add component IDs
└── renderer.py                        # UPDATE: Pass paths to templates
```

### Files to Modify

1. **`ssr_python/renderer.py`**
   - Add path tracking
   - Pass paths to component macros

2. **`ssr_python/templates/macros/_components.html`**
   - Add `path` and `component_id` parameters to all macros
   - Add `data-component-id` attributes to all components
   - Add `chrome-target` classes for selection

3. **`ssr_python/static/js/ssr_app.js`**
   - Integrate path map builder
   - Update renderPreview to build path map

4. **`ssr_python/static/js/main.js` or `events.js`**
   - Add selection manager
   - Connect selection to properties panel

5. **`ssr_python/app.py`** (Optional)
   - Add endpoints for serving schemas/defaults as JSON

---

## Implementation Order

1. **Phase 1:** Server-side component ID generation (Foundation)
2. **Phase 2:** Client-side path map building (Mapping)
3. **Phase 3:** Component selection & highlighting (UI)
4. **Phase 4:** Properties panel integration (Editing)
5. **Phase 5:** YAML update & re-rendering (Completeness)

---

## Testing Checklist

- [ ] Components render with `data-component-id` attributes
- [ ] Component IDs match between server and client
- [ ] Path map correctly maps IDs to YAML paths
- [ ] Clicking components selects them
- [ ] Selected components are highlighted
- [ ] Properties panel displays for selected components
- [ ] Property changes update YAML structure
- [ ] Preview re-renders after property changes
- [ ] Selection persists after re-render
- [ ] Nested components (columns, tabs, etc.) work correctly

---

## Notes

1. **Component ID Generation:** Must be consistent between server and client. Use the same algorithm.

2. **Path Map Building:** Can be done client-side by traversing YAML structure and matching with DOM, or server-side by including path data in HTML attributes.

3. **Properties Panel:** Can reuse CSR code with minimal changes, or create SSR-specific version.

4. **YAML Parsing:** Use `js-yaml` library (same as CSR) or serve parsed JSON from Flask.

5. **Performance:** Path map building happens after each render. Consider caching or optimizing if performance becomes an issue.

6. **Chrome UI:** Can add chrome labels and delete buttons later. Start with basic selection highlighting.

---

## Future Enhancements

- Add chrome delete buttons for component deletion
- Add component insertion UI
- Add undo/redo functionality
- Add component drag-and-drop reordering
- Add YAML editor sync (highlight selected component's YAML)
- Add component tree view sidebar

---

**Plan Complete** ✅

