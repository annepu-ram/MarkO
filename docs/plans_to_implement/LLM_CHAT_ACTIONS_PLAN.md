# AI Chat Component Actions (Delete, Insert)

> **Step 0:** Copy this plan to `docs/plans_to_implement/LLM_CHAT_ACTIONS_PLAN.md` before starting implementation.

## Context

The AI chat can currently `create` full pages and `modify` selected components. But users can't ask the AI to **delete** a component, or **insert** a new component at a specific location. These operations are only available via tree action buttons. This plan adds three new ACTION types (`delete`, `insert_child`, `insert_after`) to the chat system so users can say things like "delete this heading" or "add a button below this image" in natural language.

Copy/paste is out of scope — it's a client-side clipboard operation already served by tree buttons. The LLM can achieve the same result via `insert_child` / `insert_after` by generating the component YAML directly.

---

## Files to Modify (3 files)

| # | File | Change |
|---|------|--------|
| 1 | `ssr_python/llm_service.py` | Update regex + action whitelist in `_parse_response()`, add action docs to `_build_system_prompt()`, add container flag to `_build_prompt()` |
| 2 | `ssr_python/static/js/chat.js` | Add `displayActionResponse()` for no-YAML actions, route `delete` in `sendMessage()`, relax null guard in `applyYamlChanges()` |
| 3 | `ssr_python/templates/index.html` | Add yamlUtils imports, add `delete`/`insert_child`/`insert_after` branches to `onYamlApply`, guard YAML validation for delete |

No changes to: `chatService.js` (transparent transport), `yamlUtils.js` (functions already exist), `main.js` (tree actions unchanged), `routes/chat.py` (pass-through).

---

## Step 1: `llm_service.py` — Backend Changes

### 1a. Update `_parse_response()` (~line 311)

Update regex to match hyphenated/underscored action names, expand whitelist, add delete special case:

```python
# Change regex from \w+ to [\w-]+ to support insert_child etc.
action_match = re.search(r'<!--\s*ACTION:\s*([\w-]+)\s*-->', response_text[:150], re.IGNORECASE)
# ... fallback search same change ...

# Expand whitelist
if action in ('create', 'modify', 'explain', 'error', 'settings', 'delete', 'insert_child', 'insert_after'):
    result["action"] = action
```

Add delete special case before YAML extraction (~after line 319):
```python
if result["action"] == 'delete':
    result["yaml"] = None  # Delete needs no YAML
    return result
```

### 1b. Update `_build_system_prompt()` (~line 162)

Add new action documentation after the existing "For Component MODIFICATION" section:

```
### For Component DELETION:
- When user asks to remove/delete a selected component
- Do NOT output any YAML
- Add `<!-- ACTION: delete -->` at the START
- REQUIRES a component to be selected — if none is selected, use ACTION: error

### For INSERTING a Component as Child:
- When user asks to add a new component INSIDE a selected container
- Output the new component YAML (just the component to insert)
- Add `<!-- ACTION: insert_child -->` at the START
- REQUIRES a container to be selected (page, layout-row, layout-column, form, etc.)
- If selected component is NOT a container, use insert_after instead

### For INSERTING a Component After Selection:
- When user asks to add a new component AFTER/BELOW the selected component
- Output the new component YAML (just the component to insert)
- Add `<!-- ACTION: insert_after -->` at the START
- REQUIRES a component to be selected — if none is selected, use ACTION: create
```

Add choosing guide:
```
### Choosing the Right Action:
- "delete/remove this" → delete
- "add X inside this section" → insert_child (if container selected)
- "add X after/below this" → insert_after
- "change/update this" → modify
- "create/build a page" → create
```

Add output examples for the three new actions.

### 1c. Update `_build_prompt()` (~line 274)

Add container flag to selected component context so the LLM knows whether to use `insert_child` or `insert_after`:

```python
container_names = ['page', 'layout-row', 'layout-column', 'columnsgrid',
                   'form', 'video-background', 'hamburger', 'tabs',
                   'accordion', 'carousel', 'ticker']
is_container = component_name in container_names

prompt_parts.append(f"""
[SELECTED COMPONENT]
Currently selected: {component_name} at path {component_path}
Component ID: {selected_component.get('id', 'unknown')}
Is container (can hold children): {is_container}""")
```

---

## Step 2: `chat.js` — UI Changes

### 2a. Route `delete` in `sendMessage()` (~line 232)

Delete has no YAML, so it won't match `result.yaml` check. Add before the `result.yaml` branch:

```javascript
} else if (result.action === 'delete') {
    this.displayActionResponse(result.response, 'delete');
} else if (result.yaml) {
```

### 2b. Add `displayActionResponse()` method

New method for actions with no YAML preview (like delete). Shows LLM explanation + "Apply Changes" button:

```javascript
displayActionResponse(response, action) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message message-ai';

    let cleanResponse = response.replace(/<!--\s*ACTION:\s*[\w-]+\s*-->/gi, '').trim();
    let html = '';
    if (cleanResponse) {
        html += `<div class="response-text">${this.formatMessageContent(cleanResponse)}</div>`;
    }
    html += `<button class="apply-btn" data-action="${action}">Apply Changes</button>`;
    messageEl.innerHTML = html;

    this.pendingYaml = null;
    this.pendingAction = action;

    const applyBtn = messageEl.querySelector('.apply-btn');
    applyBtn.addEventListener('click', () => this.applyYamlChanges());

    this.messagesArea.appendChild(messageEl);
    this.scrollToBottom();
}
```

### 2c. Relax null guard in `applyYamlChanges()` (~line 315)

Currently: `if (!this.pendingYaml || this.isLoading) return;`
Change to: `if (this.isLoading) return;`
Then: `if (!this.pendingYaml && this.pendingAction !== 'delete') return;`

---

## Step 3: `index.html` — Apply Logic

### 3a. Add imports (~line 341)

Add Document API functions to existing import:

```javascript
import { getYamlStructureFromEditor, getComponentByPath, updateComponentByPath,
         generateYamlFromStructure, updateYamlEditor,
         getYamlDocumentFromEditor, generateYamlFromDocument,
         deleteComponentInDocument, insertComponentInDocument, getChildrenKey
       } from '/static/js/yamlUtils.js';
```

### 3b. Guard YAML validation for delete (~line 383)

Wrap existing YAML parse + validate in `if (action !== 'delete')` since delete has no YAML.

### 3c. Add action branches in `onYamlApply` (~after the `modify` branch at line 434)

**delete:**
```javascript
} else if (action === 'delete') {
    const selection = selectionManager.selectedPath;
    if (!selection || selection.length === 0) throw new Error('Cannot delete: no component selected');

    const yamlDoc = getYamlDocumentFromEditor();
    if (!yamlDoc) throw new Error('Cannot delete: no valid YAML');

    const deleted = deleteComponentInDocument(yamlDoc, selection);
    if (!deleted) throw new Error('Cannot delete: component not found');

    editor.value = generateYamlFromDocument(yamlDoc);
    selectionManager.clearSelection();
```

**insert_child:**
```javascript
} else if (action === 'insert_child') {
    const selection = selectionManager.selectedPath;
    if (!selection || selection.length === 0) throw new Error('Cannot insert: no component selected');

    const currentStructure = getYamlStructureFromEditor();
    const selectedComp = getComponentByPath(currentStructure, selection);
    const childrenKey = getChildrenKey(selectedComp.name);
    if (!childrenKey) throw new Error(`"${selectedComp.name}" is not a container`);

    let newComponent = parsedYaml;
    if (Array.isArray(parsedYaml) && parsedYaml.length === 1) newComponent = parsedYaml[0];

    const yamlDoc = getYamlDocumentFromEditor();
    const inserted = insertComponentInDocument(yamlDoc, [...selection, childrenKey], newComponent);
    if (!inserted) throw new Error('Failed to insert component');

    editor.value = generateYamlFromDocument(yamlDoc);
```

**insert_after:**
```javascript
} else if (action === 'insert_after') {
    const selection = selectionManager.selectedPath;
    if (!selection || selection.length < 2) throw new Error('Cannot insert: no component selected');

    let newComponent = parsedYaml;
    if (Array.isArray(parsedYaml) && parsedYaml.length === 1) newComponent = parsedYaml[0];

    const yamlDoc = getYamlDocumentFromEditor();
    const parentSeqPath = selection.slice(0, -1);
    const insertIndex = selection[selection.length - 1] + 1;
    const inserted = insertComponentInDocument(yamlDoc, parentSeqPath, newComponent, insertIndex);
    if (!inserted) throw new Error('Failed to insert component');

    editor.value = generateYamlFromDocument(yamlDoc);
```

The existing history/autosave/render/rollback code after all branches stays unchanged.

---

## Existing Functions Reused (no changes needed)

| Function | From | Used By |
|----------|------|---------|
| `deleteComponentInDocument(doc, path)` | `yamlUtils.js` | `delete` action |
| `insertComponentInDocument(doc, parentSeqPath, component, index?)` | `yamlUtils.js` | `insert_child`, `insert_after` |
| `getChildrenKey(componentName)` | `yamlUtils.js` | `insert_child` (determine children array name) |
| `getYamlDocumentFromEditor()` | `yamlUtils.js` | All 3 new actions (preserves anchors) |
| `generateYamlFromDocument(doc)` | `yamlUtils.js` | All 3 new actions (back to YAML string) |
| `getComponentByPath(structure, path)` | `yamlUtils.js` | `insert_child` (check if container) |

---

## Verification

1. Select a heading → chat "delete this heading" → heading removed, tree updates, undo works
2. Select a layout-column → chat "add a paragraph inside" → paragraph appears as last child
3. Select an image → chat "add a button below this" → button inserted after image
4. No selection → chat "delete this" → error message (LLM returns ACTION: error or frontend catches)
5. Select a heading (leaf) → chat "add inside this heading" → LLM uses insert_after instead or returns error
6. Existing actions (create, modify, explain, error, settings) → all still work unchanged
7. Run `python -m pytest ssr_python/tests/ -v` → all tests pass
