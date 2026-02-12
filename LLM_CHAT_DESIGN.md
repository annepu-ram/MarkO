# LLM Chat Feature Design Document

**Feature:** AI-powered chat window for website creation and modification
**Version:** 2.0
**Last Updated:** February 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Current Architecture](#2-current-architecture)
3. [Issues Analysis](#3-issues-analysis)
4. [Root Cause Analysis](#4-root-cause-analysis)
5. [Improvement Options](#5-improvement-options)
6. [Implementation Plan](#6-implementation-plan)
7. [File Specifications](#7-file-specifications)
8. [Verification Steps](#8-verification-steps)
9. [Future Enhancements](#9-future-enhancements)

---

## 1. Overview

### 1.1 Purpose

Add an LLM-powered chat interface to Swift Sites that enables users to:
- Create complete websites from natural language descriptions
- Modify specific components through conversation
- Get context-aware assistance when a component is selected in the preview

### 1.2 Current Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider | Ollama (local/cloud) | Privacy, no API costs for local |
| Streaming | Disabled | Simpler implementation |
| Selection Context | Enabled | Better UX for targeted edits |
| API Key Location | Server-side only | Security best practice |
| Conversation History | Not sent to LLM | Stateless requests |
| Send Trigger | Button only | Prevents accidental sends |

### 1.3 Analysis Summary (v2.0)

Comprehensive analysis revealed **27 issues** across 3 areas:
- **9 high-severity** problems
- **12 medium-severity** issues
- **6 low-severity** improvements

**Selected Approach:** Option B (Moderate Improvements) with Generation Quality Focus

---

## 2. Current Architecture

### 2.1 Data Flow

```
User Message in Chat UI
        ↓
chatService.sendMessage() [chatService.js]
        ↓
POST /api/chat {message, currentYaml, selectedComponent}
        ↓
Flask endpoint [app.py]
        ↓
llm_service.chat() [llm_service.py]
        ↓
Build System Prompt (includes 1,620-line component guide)
        ↓
Build User Prompt (YAML state + selected component + message)
        ↓
Call Ollama API
        ↓
Parse Response (extract ACTION comment + YAML block)
        ↓
Return {response, yaml, action}
        ↓
Chat UI displays response + "Apply Changes" button
        ↓
User clicks Apply → onYamlApply() [index.html]
        ↓
Create: Replace editor content
Modify: Merge at component path
        ↓
Trigger render → Preview updates
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `ssr_python/llm_service.py` | Ollama API integration, prompt building, response parsing |
| `ssr_python/app.py` | Flask `/api/chat` endpoint |
| `ssr_python/static/js/chat.js` | Chat UI component |
| `ssr_python/static/js/chatService.js` | API communication (60s timeout) |
| `ssr_python/templates/index.html` | YAML application logic (onYamlApply) |
| `LLM_COMPONENT_GUIDE.md` | Component reference (1,620 lines, ~7,500 tokens) |

### 2.3 Current Prompt Structure

**System Prompt:**
```
1. Role definition (5 lines)
2. Component guide (1,620 lines) ← VERY LARGE
3. Output rules (30 lines)
4. ACTION comment requirement
```

**User Prompt:**
```
[CURRENT YAML STATE]
{full editor content}

[SELECTED COMPONENT]
name: {name} at path {path}
Component ID: {id}
← MISSING: Current component's actual YAML structure

[USER REQUEST]
{message}
```

---

## 3. Issues Analysis

### 3.1 LLM Service Issues (`llm_service.py`)

| Severity | Issue | Location | Impact |
|----------|-------|----------|--------|
| **HIGH** | ACTION comment placement not enforced | line 132 | LLM can put comment anywhere; user sees orphaned text |
| **HIGH** | No YAML structure validation | line 148 | Invalid YAML reaches frontend; errors appear in preview |
| **HIGH** | Multiple YAML blocks silently dropped | lines 140-143 | If LLM outputs example + solution, only first used |
| **HIGH** | Missing component context in modify mode | lines 94-121 | LLM doesn't see current component structure when modifying |
| MEDIUM | Overwhelming system prompt (1,620 lines) | lines 49-92 | Higher token cost, diluted critical instructions |
| MEDIUM | No "error" action from LLM | line 135 | LLM cannot signal "I can't help with this request" |

### 3.2 LLM Component Guide Issues (`LLM_COMPONENT_GUIDE.md`)

| Severity | Issue | Impact |
|----------|-------|--------|
| **HIGH** | Property path mismatch: `layout.shrinkPercent` vs actual `scroll.shrinkPercentage` | LLM generates invalid YAML for titlebar |
| **HIGH** | Deprecated features still documented (brighten/darken hover effects) | Inconsistent with implementation |
| MEDIUM | Form fields incomplete (missing 20+ properties vs schema) | Incomplete form YAML generated |
| MEDIUM | Redundant YAML rules (repeated 3+ times in document) | Wastes tokens, may confuse LLM |
| MEDIUM | Missing property validation table | LLM doesn't know which token values are valid |
| LOW | Missing quick reference card at top | LLM must search through 1,600 lines |

**Token Analysis:**
- Current: ~7,500 tokens
- Target: <5,500 tokens (after consolidation)

### 3.3 Chat UI & YAML Application Issues

| Severity | Issue | Location | Impact |
|----------|-------|----------|--------|
| **HIGH** | No YAML validation before apply | index.html:237 | Broken YAML silently applied to editor |
| **HIGH** | Silent fallback to broken YAML | index.html:252-256 | Error caught but broken YAML used anyway |
| **HIGH** | No feedback when render fails | chat.js:348 | Chat says "success" but preview shows error |
| MEDIUM | Broken YAML pushed to history | index.html:264 | Cannot undo to valid state |
| MEDIUM | Fragile array handling for modify | index.html:241-242 | Multi-component responses break merge |
| MEDIUM | 500ms hardcoded delay after apply | chat.js:343 | May be too short/long for complex pages |
| LOW | No confirmation before "create" action | index.html:229 | Replaces all content without warning |

---

## 4. Root Cause Analysis

### 4.1 Why YAML Generation Fails

```
LLM Prompt Too Large (7,500 tokens)
        ↓
Critical Rules Diluted by Verbose Examples
        ↓
LLM Outputs Invalid Structure
        ↓
No Server-Side Validation
        ↓
Invalid YAML Reaches Client
        ↓
No Client-Side Validation
        ↓
Preview Fails, But Chat Shows "Success"
```

### 4.2 Missing Context for Modifications

**Example Scenario:**
```
User: "Add a 4th FAQ item to this accordion"

Context Currently Given to LLM:
- Component name: "accordion"
- Component path: [0, 'components', 2]
- Component ID: "comp_0_components_2"

Context MISSING:
- Current accordion's 3 existing items
- Current item titles and content
- Valid properties for accordion component
```

**Result:** LLM may output only the new item, or completely restructure the accordion, losing existing content.

---

## 5. Improvement Options

### 5.1 Option A: Quick Fixes (Low Effort)

**Scope:** Fix critical bugs only (~2-3 hours)

1. Enforce ACTION comment at response start
2. Add YAML syntax validation before returning
3. Add client-side YAML validation before apply
4. Fix property path inconsistencies in guide

**Addresses:** 4 high-severity issues
**Token Impact:** None
**Risk:** Low

---

### 5.2 Option B: Moderate Improvements (SELECTED)

**Scope:** Quick fixes + context enhancement + guide optimization (~6-8 hours)

1. Include selected component's current YAML in context
2. Add component-specific schema for modify mode
3. Consolidate redundant guide sections
4. Add property validation rules table
5. Improve error feedback loop to chat

**Addresses:** 7 high-severity issues, 5 medium issues
**Token Impact:** -2,000 tokens (net reduction)
**Risk:** Medium

---

### 5.3 Option C: Comprehensive Overhaul (High Effort)

**Scope:** Full rewrite of prompt system and validation (~15-20 hours)

1. Create condensed LLM guide (~3,000 tokens)
2. Dynamic context injection based on task type
3. Multi-turn conversation for complex modifications
4. Real-time YAML validation with suggestions
5. Diff preview before apply
6. Rollback mechanism on render failure

**Addresses:** All 27 issues
**Token Impact:** -4,500 tokens (major reduction)
**Risk:** High (significant refactoring)

---

## 6. Implementation Plan

### 6.1 Phase 1: Fix Critical Generation Issues

#### 6.1.1 Add Component Context for Modify Mode

**File:** `ssr_python/llm_service.py`

**Problem:** LLM doesn't see current component structure when modifying.

**Solution:** Extract and include selected component's YAML in user prompt.

```python
# Add new method to LLMService class
def _extract_component_yaml(self, yaml_content: str, path: list) -> str:
    """Extract a component's YAML from the full document by path."""
    import yaml
    try:
        structure = yaml.safe_load(yaml_content)
        component = self._navigate_to_path(structure, path)
        return yaml.dump(component, default_flow_style=False, allow_unicode=True)
    except:
        return None

def _navigate_to_path(self, structure: any, path: list) -> any:
    """Navigate to a component by path array."""
    current = structure
    for key in path:
        if isinstance(current, list) and isinstance(key, int):
            current = current[key]
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current
```

**Update `_build_prompt()` method:**
```python
# In _build_prompt(), add after selected component context:
if selected_component:
    # Extract current component YAML from editor content
    component_yaml = self._extract_component_yaml(current_yaml, selected_component['path'])
    if component_yaml:
        prompt_parts.append(f"""
[CURRENT COMPONENT STRUCTURE]
```yaml
{component_yaml}
```
Modify this component based on the user's request. Preserve existing structure (items, tabs, slides, columns) unless asked to change them.""")
```

#### 6.1.2 Add YAML Validation in Response Parsing

**File:** `ssr_python/llm_service.py`

**Problem:** Invalid YAML reaches frontend without validation.

**Solution:** Validate extracted YAML before returning.

```python
def _validate_yaml(self, yaml_content: str) -> dict:
    """Validate YAML syntax and basic structure."""
    import yaml
    try:
        parsed = yaml.safe_load(yaml_content)

        # Check for required 'name' field in components
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and 'name' not in item:
                    return {'valid': False, 'error': 'Component missing required "name" field'}
        elif isinstance(parsed, dict) and 'name' not in parsed:
            return {'valid': False, 'error': 'Component missing required "name" field'}

        return {'valid': True, 'error': None}
    except yaml.YAMLError as e:
        return {'valid': False, 'error': str(e)}
```

**Update `_parse_response()` method:**
```python
def _parse_response(self, response_text: str) -> dict:
    result = {
        "response": response_text,
        "yaml": None,
        "action": "explain"
    }

    # Extract action type from comment (check first 150 chars)
    action_match = re.search(r'<!--\s*ACTION:\s*(\w+)\s*-->', response_text[:150], re.IGNORECASE)
    if not action_match:
        # Fallback: search entire response
        action_match = re.search(r'<!--\s*ACTION:\s*(\w+)\s*-->', response_text, re.IGNORECASE)

    if action_match:
        action = action_match.group(1).lower()
        if action in ('create', 'modify', 'explain', 'error'):
            result["action"] = action

    # Extract YAML from code blocks
    yaml_pattern = r'```yaml\s*([\s\S]*?)```'
    yaml_matches = re.findall(yaml_pattern, response_text)

    if yaml_matches:
        yaml_content = yaml_matches[0].strip()
        if yaml_content:
            # VALIDATE YAML before returning
            validation = self._validate_yaml(yaml_content)
            if validation['valid']:
                result["yaml"] = yaml_content
            else:
                result["yaml"] = None
                result["action"] = "error"
                result["response"] = f"Generated YAML has errors: {validation['error']}\n\nPlease try again with a more specific request."

    return result
```

#### 6.1.3 Add Output Examples to System Prompt

**File:** `ssr_python/llm_service.py`

**Update `_build_system_prompt()` to include explicit examples:**

```python
# Add after output rules section:
"""
### Output Format Examples

**CORRECT - Create action:**
<!-- ACTION: create -->
Here's your landing page with a hero section:

```yaml
- name: page
  properties:
    appearance: { background: { color: '#ffffff' } }
  components:
    - name: heading
      properties:
        text: Welcome
        typography: { size: xxxl, weight: bold }
```

**CORRECT - Modify action:**
<!-- ACTION: modify -->
I've updated the heading to be red and larger:

```yaml
- name: heading
  properties:
    text: Welcome
    typography: { size: xxxl, weight: bold, color: '#ff0000' }
```

**WRONG - Never output multiple YAML blocks:**
<!-- ACTION: create -->
Here's option 1:
```yaml
...
```
Here's option 2:
```yaml
...
```
← This is WRONG! Only include ONE yaml block.
"""
```

---

### 6.2 Phase 2: Optimize LLM Component Guide

#### 6.2.1 Fix Property Path Inconsistencies

**File:** `LLM_COMPONENT_GUIDE.md`

| Find | Replace With |
|------|--------------|
| `layout.shrinkPercent` | `scroll.shrinkPercentage` |
| `hoverEffect: brighten` | `hoverEffect: zoom` |
| `hoverEffect: darken` | `hoverEffect: lift` |

#### 6.2.2 Add Quick Reference Card at Top of Guide

**Insert after title:**
```markdown
## CRITICAL QUICK REFERENCE

### Component Structure Rule
```yaml
- name: component-name
  properties:           # ← All configuration HERE
    spacing: {...}
    typography: {...}
    appearance: {...}
  components: [...]     # ← Arrays at COMPONENT LEVEL
```

### Special Array Properties (NEVER inside properties)
| Component | Array Property | Example |
|-----------|----------------|---------|
| accordion | `items:` | `items: [{ title: "Q1", components: [...] }]` |
| tabs | `tabs:` | `tabs: [{ title: "Tab 1", components: [...] }]` |
| carousel | `slides:` | `slides: [{ components: [...] }]` |
| columnsgrid | `columns:` | `columns: [{ components: [...] }]` |
| containers | `components:` | `components: [...]` |

### Valid Design Tokens
| Property | Valid Values |
|----------|-------------|
| **Spacing** | none, xxs, xs, sm, md, lg, xl, xxl, xxxl, auto |
| **Typography sizes** | xxs, xs, sm, md, lg, xl, xxl, xxxl, auto |
| **Font weights** | light, regular, medium, semibold, bold, extrabold |
| **Shadow** | none, soft, medium, elevated, dramatic, retro |
| **Border radius** | none, xs, sm, md, lg, xl, xxl, pill |
| **Hover effects** | none, zoom, lift |
```

#### 6.2.3 Consolidate Redundant Sections

**Remove duplicates:**
- Lines 1055-1159: Duplicate YAML structure rules (keep reference to main section)
- Merge "Common Mistakes" sections into one location
- Remove redundant component examples

**Estimated token reduction:** ~2,000 tokens

---

### 6.3 Phase 3: Improve Error Feedback

#### 6.3.1 Client-Side Validation Before Apply

**File:** `ssr_python/templates/index.html`

**Update `onYamlApply` function:**
```javascript
async function onYamlApply(yaml, action) {
    // Validate YAML syntax before applying
    try {
        window.jsyaml.load(yaml);
    } catch (e) {
        throw new Error(`Invalid YAML syntax: ${e.message}`);
    }

    // ... rest of existing logic
}
```

#### 6.3.2 Render Error Feedback to Chat

**File:** `ssr_python/static/js/chat.js`

**Update `applyYamlChanges` to catch render errors:**
```javascript
async applyYamlChanges() {
    try {
        await this.onYamlApply(this.pendingYaml, this.pendingAction);
        this.addMessage('ai', `Changes applied successfully! (${this.pendingAction})`);
    } catch (error) {
        this.addMessage('ai', `Failed to apply: ${error.message}`, { isError: true });
        return; // Don't clear pendingYaml - allow retry
    }

    this.pendingYaml = null;
    this.pendingAction = null;
}
```

---

## 7. File Specifications

### 7.1 Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `ssr_python/llm_service.py` | Add component context extraction, YAML validation, output examples | HIGH |
| `LLM_COMPONENT_GUIDE.md` | Fix property paths, add quick reference, consolidate sections | HIGH |
| `ssr_python/templates/index.html` | Add client-side YAML validation | MEDIUM |
| `ssr_python/static/js/chat.js` | Improve error feedback on apply | MEDIUM |

### 7.2 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OLLAMA_API_KEY` | Yes (cloud) | - | Ollama cloud API key |
| `OLLAMA_BASE_URL` | No | `https://ollama.com` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3:latest` | Model to use |
| `LLM_MAX_TOKENS` | No | `4096` | Max response tokens |
| `LLM_TEMPERATURE` | No | `0.7` | Response creativity (0-2) |

---

## 8. Verification Steps

### 8.1 Test Component Context (Modify Mode)

**Steps:**
1. Create a page with an accordion containing 3 FAQ items
2. Select the accordion component
3. In chat, ask: "Add a 4th question about pricing"
4. Verify the LLM response includes all 4 items (not just the new one)
5. Click "Apply Changes"
6. Verify preview shows 4 FAQ items

**Expected:** LLM sees current 3 items in context and adds a 4th.

### 8.2 Test YAML Validation

**Steps:**
1. Temporarily modify `_parse_response()` to return invalid YAML
2. Send a chat message
3. Verify error message appears in chat (not "success")
4. Verify broken YAML is NOT applied to editor

**Expected:** Validation catches errors before they reach frontend.

### 8.3 Test Property Paths

**Steps:**
1. Create a titlebar with scroll/shrink settings
2. Verify `scroll.shrinkPercentage` property works correctly
3. Try old path `layout.shrinkPercent` and verify it fails gracefully

**Expected:** Updated property paths work correctly.

### 8.4 Test Token Reduction

**Steps:**
1. Log system prompt token count before changes
2. Apply guide consolidation
3. Log system prompt token count after changes
4. Verify reduction of ~2,000 tokens

**Expected:** Prompt size reduced without losing critical information.

---

## 9. Future Enhancements

### 9.1 Phase 2 Features

- [ ] Streaming responses (Server-Sent Events)
- [ ] Voice input support
- [ ] Image upload for design inspiration
- [ ] Template suggestions

### 9.2 Phase 3 Features

- [ ] Multi-turn refinement memory
- [ ] Undo specific AI changes
- [ ] Diff preview before apply
- [ ] Custom prompt templates
- [ ] Multiple LLM provider support

---

## 10. Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| YAML syntax errors reaching client | ~15% | <2% |
| Modify actions preserving existing structure | ~60% | >90% |
| System prompt token count | ~7,500 | <5,500 |
| "Chat said success but preview failed" | Common | Rare |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2025 | Initial design document |
| 2.0 | February 2026 | Added issues analysis, improvement options, implementation plan |
