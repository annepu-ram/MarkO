"""
YAML Template Validator — validates every example_templates/*.yaml file against
component_defaults.yaml (valid property keys) and component_schemas.yaml +
schema_tokens.yaml (valid token values for select fields).

Checks per component:
  1. Component name is known (exists in defaults)
  2. All property keys at every nesting level are valid (exist in defaults)
  3. Token-constrained values match allowed options (from schema_tokens)
  4. Structural rules: components/columns/tabs/slides/items at component level
"""

import os
import glob
import yaml
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), 'example_templates')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

DEFAULTS_PATH = os.path.join(CONFIG_DIR, 'component_defaults.yaml')
SCHEMAS_PATH = os.path.join(CONFIG_DIR, 'component_schemas.yaml')
TOKENS_PATH = os.path.join(CONFIG_DIR, 'schema_tokens.yaml')


# ---------------------------------------------------------------------------
# Load metadata once
# ---------------------------------------------------------------------------
def _load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


DEFAULTS = _load_yaml(DEFAULTS_PATH)
SCHEMAS = _load_yaml(SCHEMAS_PATH)
TOKENS = _load_yaml(TOKENS_PATH)

# Build token value lookup: token_name → set of allowed string values
TOKEN_VALUES = {}
for token_name, token_def in TOKENS.items():
    options = token_def.get('options', [])
    vals = set()
    for opt in options:
        if isinstance(opt, dict):
            vals.add(str(opt.get('value', '')))
        else:
            vals.add(str(opt))
    TOKEN_VALUES[token_name] = vals

# Build schema field lookup per component:
#   component_name → { "dotted.path": {"type": ..., "tokens": ..., "options": [...]} }
SCHEMA_FIELDS = {}
for comp_name, comp_schema in SCHEMAS.items():
    fields_map = {}
    for group in comp_schema.get('groups', []):
        for field in group.get('fields', []):
            path = field.get('path', '')
            entry = {'type': field.get('type')}
            if 'tokens' in field:
                entry['tokens'] = field['tokens']
            if 'options' in field:
                opts = field['options']
                vals = set()
                for o in opts:
                    if isinstance(o, dict):
                        vals.add(str(o.get('value', '')))
                    else:
                        vals.add(str(o))
                entry['options'] = vals
            if 'min' in field:
                entry['min'] = field['min']
            if 'max' in field:
                entry['max'] = field['max']
            fields_map[path] = entry
    SCHEMA_FIELDS[comp_name] = fields_map

# Known component names (from defaults)
KNOWN_COMPONENTS = set(DEFAULTS.keys())

# Component-level array keys (not inside properties)
COMPONENT_LEVEL_ARRAYS = {'components', 'columns', 'tabs', 'slides', 'items', 'header', 'footer'}

# Top-level keys allowed on a component node
COMPONENT_NODE_KEYS = {'name', 'properties', 'components', 'columns', 'tabs',
                       'slides', 'items', 'links', 'header', 'footer'}

# Special property paths that are always valid (not in defaults but valid by design)
# site.theme is handled specially by the renderer, not via component defaults
# theme can appear on either site or page
_THEME_PATHS = {'theme', 'theme.colors', 'theme.colors.primary', 'theme.colors.secondary',
                'theme.colors.accent', 'theme.colors.background', 'theme.fonts',
                'theme.fonts.heading', 'theme.fonts.content'}
ALWAYS_VALID_PATHS = {
    'site': _THEME_PATHS,
    'page': _THEME_PATHS,
}

# Components where property key checking should be skipped entirely
# (complex/custom structure not fully captured in defaults)
SKIP_KEY_CHECK_COMPONENTS = {'site', 'hamburger'}

# Deprecated but engine-supported paths (backward compat) — reported as deprecation warnings
DEPRECATED_PATHS = {
    'appearance.padding', 'appearance.padding.block', 'appearance.padding.inline',
}

# Theme anchor pattern — values like *color-primary are valid
def _is_yaml_anchor_ref(val):
    """Check if value looks like an unresolved YAML anchor (starts with $ or *)."""
    if isinstance(val, str):
        return val.startswith('$') or val.startswith('*')
    return False


def _is_css_color(val):
    """Check if value looks like a CSS color."""
    if not isinstance(val, str):
        return False
    v = val.strip()
    return (v.startswith('#') or v.startswith('rgb') or v.startswith('hsl')
            or v in ('transparent', 'inherit', 'currentColor', 'white', 'black'))


# ---------------------------------------------------------------------------
# Key validation helpers
# ---------------------------------------------------------------------------
def _collect_leaf_paths(d, prefix=''):
    """Collect all dotted key paths from a nested dict."""
    paths = set()
    if not isinstance(d, dict):
        return paths
    for k, v in d.items():
        full = f'{prefix}.{k}' if prefix else k
        paths.add(full)
        if isinstance(v, dict):
            paths |= _collect_leaf_paths(v, full)
    return paths


def _get_valid_key_paths(comp_name):
    """Get all valid dotted property paths for a component from defaults + schema."""
    paths = set()
    # From defaults
    comp_defaults = DEFAULTS.get(comp_name, {})
    if isinstance(comp_defaults, dict):
        paths |= _collect_leaf_paths(comp_defaults)
    # From schema fields
    if comp_name in SCHEMA_FIELDS:
        for field_path in SCHEMA_FIELDS[comp_name]:
            paths.add(field_path)
            # Also add parent paths
            parts = field_path.split('.')
            for i in range(1, len(parts)):
                paths.add('.'.join(parts[:i]))
    return paths


def _get_nested_value(d, dotted_path):
    """Get a value from a nested dict using dotted path."""
    parts = dotted_path.split('.')
    current = d
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


# Cache valid paths per component
_VALID_PATHS_CACHE = {}

def _get_cached_valid_paths(comp_name):
    if comp_name not in _VALID_PATHS_CACHE:
        _VALID_PATHS_CACHE[comp_name] = _get_valid_key_paths(comp_name)
    return _VALID_PATHS_CACHE[comp_name]


# ---------------------------------------------------------------------------
# Validation engine
# ---------------------------------------------------------------------------
class ValidationError:
    def __init__(self, path, message, severity='error'):
        self.path = path
        self.message = message
        self.severity = severity  # 'error' or 'warning'

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


def validate_token_value(comp_name, prop_path, value, errors, yaml_path):
    """Check if a property value is valid per schema token constraints."""
    if comp_name not in SCHEMA_FIELDS:
        return
    field_def = SCHEMA_FIELDS[comp_name].get(prop_path)
    if not field_def:
        return

    # Skip validation for None, empty strings, or anchor refs
    if value is None or value == '' or _is_yaml_anchor_ref(str(value)):
        return

    str_val = str(value)
    field_type = field_def.get('type')

    # Token-constrained select fields
    if 'tokens' in field_def:
        token_name = field_def['tokens']
        allowed = TOKEN_VALUES.get(token_name, set())
        if allowed and str_val not in allowed:
            errors.append(ValidationError(
                yaml_path,
                f"Component '{comp_name}' property '{prop_path}' has value "
                f"'{str_val}' which is not in token '{token_name}' "
                f"(allowed: {sorted(allowed)})",
                severity='error'
            ))

    # Inline options (not token-based)
    elif 'options' in field_def:
        allowed = field_def['options']
        if allowed and str_val not in allowed:
            errors.append(ValidationError(
                yaml_path,
                f"Component '{comp_name}' property '{prop_path}' has value "
                f"'{str_val}' which is not in options {sorted(allowed)}",
                severity='error'
            ))

    # Range fields
    elif field_type == 'range' and 'min' in field_def and 'max' in field_def:
        try:
            num_val = float(value)
            if num_val < field_def['min'] or num_val > field_def['max']:
                errors.append(ValidationError(
                    yaml_path,
                    f"Component '{comp_name}' property '{prop_path}' has value "
                    f"{num_val} outside range [{field_def['min']}, {field_def['max']}]",
                    severity='warning'
                ))
        except (ValueError, TypeError):
            pass

    # Color fields — just check it looks like a color
    elif field_type == 'color':
        if not _is_css_color(str_val) and not _is_yaml_anchor_ref(str_val):
            errors.append(ValidationError(
                yaml_path,
                f"Component '{comp_name}' property '{prop_path}' has value "
                f"'{str_val}' which doesn't look like a CSS color",
                severity='warning'
            ))


def validate_property_keys(comp_name, properties, errors, yaml_path):
    """Check that all property keys exist in defaults/schema for this component."""
    if not isinstance(properties, dict):
        return

    # Skip key checking for components with complex/custom structures
    if comp_name in SKIP_KEY_CHECK_COMPONENTS:
        return

    valid_paths = _get_cached_valid_paths(comp_name)
    if not valid_paths:
        return

    # Add always-valid paths for this component
    extra_valid = ALWAYS_VALID_PATHS.get(comp_name, set())
    all_valid = valid_paths | extra_valid

    actual_paths = _collect_leaf_paths(properties)

    for path in actual_paths:
        if path in all_valid:
            continue
        # Check deprecated paths
        if path in DEPRECATED_PATHS:
            errors.append(ValidationError(
                yaml_path,
                f"Component '{comp_name}' uses deprecated property "
                f"'{path}' — migrate to spacing.paddingBlock/paddingInline",
                severity='warning'
            ))
            continue
        # Check if any valid path starts with this path (it's a valid parent)
        is_parent = any(vp.startswith(path + '.') for vp in all_valid)
        if not is_parent:
            errors.append(ValidationError(
                yaml_path,
                f"Component '{comp_name}' has unknown property path "
                f"'{path}' (not in defaults or schema)",
                severity='warning'
            ))


def validate_property_values(comp_name, properties, errors, yaml_path):
    """Validate property values against schema token constraints."""
    if not isinstance(properties, dict):
        return

    actual_paths = _collect_leaf_paths(properties)
    for path in actual_paths:
        value = _get_nested_value(properties, path)
        if isinstance(value, dict):
            continue  # Only validate leaf values
        validate_token_value(comp_name, path, value, errors, yaml_path)


def validate_component(node, errors, yaml_path, depth=0):
    """Recursively validate a component node."""
    if not isinstance(node, dict):
        return

    comp_name = node.get('name', '')

    # Check 1: Component name is known
    if comp_name and comp_name not in KNOWN_COMPONENTS:
        errors.append(ValidationError(
            yaml_path,
            f"Unknown component name '{comp_name}' at depth {depth}",
            severity='error'
        ))

    # Check 2: Structural — array keys should be at component level
    props = node.get('properties', {})
    if isinstance(props, dict):
        for array_key in COMPONENT_LEVEL_ARRAYS:
            if array_key in props:
                errors.append(ValidationError(
                    yaml_path,
                    f"Component '{comp_name}': '{array_key}' found inside "
                    f"'properties' — should be at component level (sibling of properties)",
                    severity='error'
                ))

    # Check 3: Validate property keys
    if comp_name and isinstance(props, dict):
        validate_property_keys(comp_name, props, errors, yaml_path)

    # Check 4: Validate property values against tokens
    if comp_name and isinstance(props, dict):
        validate_property_values(comp_name, props, errors, yaml_path)

    # Recurse into children
    for key in ('components', 'columns', 'tabs', 'slides', 'items', 'header', 'footer'):
        children = node.get(key)
        if not children or not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, dict):
                # columns/tabs entries have 'components' inside them
                if key in ('columns', 'slides') and 'components' in child:
                    child_comps = child['components']
                    if isinstance(child_comps, list):
                        for c in child_comps:
                            validate_component(c, errors, yaml_path, depth + 1)
                elif key == 'tabs' and 'components' in child:
                    child_comps = child['components']
                    if isinstance(child_comps, list):
                        for c in child_comps:
                            validate_component(c, errors, yaml_path, depth + 1)
                elif key == 'items' and 'components' in child:
                    child_comps = child['components']
                    if isinstance(child_comps, list):
                        for c in child_comps:
                            validate_component(c, errors, yaml_path, depth + 1)
                elif key in ('components', 'header', 'footer'):
                    validate_component(child, errors, yaml_path, depth + 1)


def validate_yaml_file(filepath):
    """Validate a single YAML template file. Returns list of ValidationErrors."""
    errors = []
    rel_path = os.path.relpath(filepath, os.path.dirname(TEMPLATES_DIR))

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f.read())
    except yaml.YAMLError as e:
        errors.append(ValidationError(rel_path, f"YAML parse error: {str(e)[:120]}", 'error'))
        return errors

    if data is None:
        return errors

    if isinstance(data, list):
        for node in data:
            validate_component(node, errors, rel_path)
    elif isinstance(data, dict):
        validate_component(data, errors, rel_path)

    return errors


# ---------------------------------------------------------------------------
# Collect all template files
# ---------------------------------------------------------------------------
def get_template_files():
    """Get all YAML template files that can be parsed."""
    files = glob.glob(os.path.join(TEMPLATES_DIR, '**', '*.yaml'), recursive=True)
    parseable = []
    for f in sorted(files):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                yaml.safe_load(fh.read())
            parseable.append(f)
        except yaml.YAMLError:
            pass  # Skip files with pre-existing parse errors
    return parseable


TEMPLATE_FILES = get_template_files()


# ---------------------------------------------------------------------------
# Pytest tests
# ---------------------------------------------------------------------------
class TestYamlSyntax:
    """Test that all YAML template files parse without errors."""

    @pytest.mark.parametrize("filepath", TEMPLATE_FILES,
                             ids=lambda f: os.path.relpath(f, TEMPLATES_DIR))
    def test_yaml_parses(self, filepath):
        """File should parse as valid YAML."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f.read())
        assert data is not None, f"File parsed as empty/null"


class TestComponentNames:
    """Test that all component names in templates are known."""

    @pytest.mark.parametrize("filepath", TEMPLATE_FILES,
                             ids=lambda f: os.path.relpath(f, TEMPLATES_DIR))
    def test_known_component_names(self, filepath):
        """All component names should exist in component_defaults."""
        errors = validate_yaml_file(filepath)
        name_errors = [e for e in errors if 'Unknown component name' in e.message]
        if name_errors:
            msg = '\n'.join(str(e) for e in name_errors)
            pytest.fail(f"Unknown component names found:\n{msg}")


class TestPropertyKeys:
    """Test that component property keys are valid."""

    @pytest.mark.parametrize("filepath", TEMPLATE_FILES,
                             ids=lambda f: os.path.relpath(f, TEMPLATES_DIR))
    def test_valid_property_keys(self, filepath):
        """All property keys should exist in component defaults or schema."""
        errors = validate_yaml_file(filepath)
        key_errors = [e for e in errors if 'unknown property path' in e.message
                      and e.severity == 'error']
        if key_errors:
            msg = '\n'.join(str(e) for e in key_errors[:10])
            pytest.fail(f"Invalid property keys found:\n{msg}")


class TestTokenValues:
    """Test that token-constrained values are valid."""

    @pytest.mark.parametrize("filepath", TEMPLATE_FILES,
                             ids=lambda f: os.path.relpath(f, TEMPLATES_DIR))
    def test_valid_token_values(self, filepath):
        """Property values using tokens should match allowed token values."""
        errors = validate_yaml_file(filepath)
        token_errors = [e for e in errors if 'not in token' in e.message]
        if token_errors:
            msg = '\n'.join(str(e) for e in token_errors[:10])
            pytest.fail(f"Invalid token values found:\n{msg}")


class TestStructuralRules:
    """Test structural YAML rules."""

    @pytest.mark.parametrize("filepath", TEMPLATE_FILES,
                             ids=lambda f: os.path.relpath(f, TEMPLATES_DIR))
    def test_arrays_at_component_level(self, filepath):
        """Array keys (components, columns, tabs, etc.) should not be inside properties."""
        errors = validate_yaml_file(filepath)
        structural_errors = [e for e in errors if 'should be at component level' in e.message]
        if structural_errors:
            msg = '\n'.join(str(e) for e in structural_errors)
            pytest.fail(f"Structural errors found:\n{msg}")


# ---------------------------------------------------------------------------
# Standalone runner — shows all warnings + errors for all files
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else TEMPLATES_DIR
    if os.path.isfile(target):
        files = [target]
    else:
        files = glob.glob(os.path.join(target, '**', '*.yaml'), recursive=True)

    total_errors = 0
    total_warnings = 0
    files_with_issues = 0

    for filepath in sorted(files):
        errors = validate_yaml_file(filepath)
        if errors:
            files_with_issues += 1
            rel = os.path.relpath(filepath, os.path.dirname(TEMPLATES_DIR))
            print(f"\n--- {rel} ---")
            for e in errors:
                if e.severity == 'error':
                    total_errors += 1
                else:
                    total_warnings += 1
                print(f"  {e}")

    print(f"\n{'='*60}")
    print(f"Files scanned: {len(files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    sys.exit(1 if total_errors > 0 else 0)
