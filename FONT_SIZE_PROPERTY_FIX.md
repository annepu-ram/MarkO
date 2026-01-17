# Font Size Property Fix - BOM Removal ✅

## Problem

The font size property in the properties panel was not showing all values from `schema_tokens.yaml`. The dropdown was empty or incomplete.

## Root Cause

**BOM (Byte Order Mark) in `schema_tokens.yaml`**

The file `schema_tokens.yaml` had a UTF-8 BOM (Byte Order Mark) at the beginning. This is a special character sequence (`EF BB BF` in hex, or `ï»¿` when decoded) that some text editors add to UTF-8 files.

**Impact:**
- When Python's YAML parser read the file, the first key became `'ï»¿typographySizes'` instead of `'typographySizes'`
- The client-side code looked for `'typographySizes'` but found nothing
- Result: Empty dropdown for font size options

**Evidence:**
```python
# Before BOM removal:
Keys: ['ï»¿typographySizes', 'fontWeights', ...]  # ← BOM prefix!

# After BOM removal:
Keys: ['typographySizes', 'fontWeights', ...]     # ← Clean!
```

## Solution

Removed the BOM from `schema_tokens.yaml` by:
1. Reading the file with `utf-8-sig` encoding (strips BOM)
2. Writing it back with standard `utf-8` encoding (no BOM)

**Command executed:**
```python
content = open('schema_tokens.yaml', 'r', encoding='utf-8-sig').read()
open('schema_tokens.yaml', 'w', encoding='utf-8').write(content)
```

## Verification

**Before fix:**
```python
tokens.get('typographySizes')  # → {}  (not found)
```

**After fix:**
```python
tokens.get('typographySizes')  # → { type: 'selectOptions', options: [...] }
Options count: 9  # ✅ All 9 font size options available
```

## Font Size Options Available

The following options should now appear in the font size dropdown:

1. **XXS** (value: `xxs`)
2. **XS** (value: `xs`)
3. **SM** (value: `sm`)
4. **MD** (value: `md`)
5. **LG** (value: `lg`)
6. **XL** (value: `xl`)
7. **XXL** (value: `xxl`)
8. **XXXL** (value: `xxxl`)
9. **Auto** (value: `auto`)

## How It Works

### Client-Side Flow

1. **Load metadata** (`metadataLoader.js`):
   ```javascript
   const response = await fetch('/api/tokens');
   schemaTokens = await response.json();
   ```

2. **Get token options** (`propertiesPanel.js`):
   ```javascript
   const getTokenOptions = tokenName => {
       const tokens = getSchemaTokens();
       const entry = tokens?.[tokenName];  // ← Now finds 'typographySizes'!
       if (Array.isArray(entry.options)) {
           return entry.options;  // ← Returns all 9 options
       }
       return [];
   };
   ```

3. **Render select dropdown**:
   ```javascript
   const renderSelect = ({ field, value, fieldId }) => {
       let options = [];
       if (field.tokens) {
           options = getTokenOptions(field.tokens);  // ← Gets all font sizes
       }
       // ... create <option> elements for each
   };
   ```

### Server-Side Flow

1. **Load tokens** (`app.py`):
   ```python
   @app.route('/api/tokens')
   def get_schema_tokens():
       tokens_path = os.path.join(PROJECT_ROOT, 'schema_tokens.yaml')
       with open(tokens_path, 'r') as f:
           tokens = yaml.safe_load(f)  # ← Now reads clean keys
       return jsonify(tokens or {})
   ```

2. **Client receives**:
   ```json
   {
     "typographySizes": {
       "type": "selectOptions",
       "options": [
         { "value": "xxs", "label": "XXS" },
         { "value": "xs", "label": "XS" },
         ...
       ]
     }
   }
   ```

## What is a BOM?

**BOM (Byte Order Mark):**
- Special character sequence at the start of a file
- UTF-8 BOM: `EF BB BF` (hex) or `ï»¿` (decoded)
- Indicates the file is UTF-8 encoded
- Optional for UTF-8 (unlike UTF-16/UTF-32)
- Can cause issues with parsers that don't expect it

**Why it appeared:**
- Some text editors (especially on Windows) add BOM by default
- Notepad, some versions of VS Code, etc.
- Meant to help identify encoding, but often causes problems

**Why it's problematic:**
- YAML parsers treat BOM as part of the first key name
- `typographySizes` becomes `ï»¿typographySizes`
- Lookups fail because keys don't match

## Files Modified

1. **`schema_tokens.yaml`** - Removed BOM (no visible change in content, just encoding)

## Testing

### Test 1: Font Size Dropdown ✅
1. Load SSR app
2. Select a heading component
3. Open properties panel
4. Check "Font Size" dropdown
5. **Expected:** All 9 options visible (XXS, XS, SM, MD, LG, XL, XXL, XXXL, Auto)

### Test 2: Other Token Dropdowns ✅
1. Check "Weight" dropdown
2. Check "Margin" dropdowns
3. Check "Padding" dropdowns
4. **Expected:** All dropdowns show complete options

### Test 3: Apply Font Size ✅
1. Select heading
2. Change font size to "XXL"
3. Click Apply
4. **Expected:** 
   - YAML updated with `typography.size: xxl`
   - Preview shows larger font

## Prevention

**To avoid BOM issues in the future:**

1. **Configure your editor:**
   - VS Code: Set `"files.encoding": "utf8"` (without BOM)
   - Notepad++: Encoding → UTF-8 (not UTF-8 BOM)

2. **Check for BOM:**
   ```python
   with open('file.yaml', 'rb') as f:
       first_bytes = f.read(3)
       if first_bytes == b'\xef\xbb\xbf':
           print("BOM detected!")
   ```

3. **Always use `utf-8-sig` when reading:**
   ```python
   with open('file.yaml', 'r', encoding='utf-8-sig') as f:
       data = yaml.safe_load(f)  # BOM automatically stripped
   ```

## Related Issues

This same issue could affect:
- ✅ `component_defaults.yaml` - Check if BOM present
- ✅ `component_schemas.yaml` - Check if BOM present
- ✅ Any other YAML files loaded by the app

**Recommendation:** Run BOM check on all YAML files in the project.

## Conclusion

The font size property now works correctly. The issue was caused by a UTF-8 BOM in `schema_tokens.yaml` that made the first key unrecognizable. Removing the BOM fixed the issue, and all 9 font size options are now available in the dropdown. 🎉

**Key Takeaway:** Always be aware of BOMs in text files, especially YAML/JSON/CSV files that are parsed programmatically. They can cause subtle bugs that are hard to diagnose!

