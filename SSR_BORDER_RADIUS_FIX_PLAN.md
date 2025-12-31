# Border Radius Fix Plan

## Problem
Border radius is not working for components in the SSR implementation. The `build_styles` macro has logic to handle `appearance.radius`, but it's not being applied correctly.

## Root Cause Analysis

### Current Implementation
In `ssr_python/templates/macros/_components.html` line 692:
```jinja2
{% if appearance.radius and tokens and tokens.border_radius and appearance.radius in tokens.border_radius %}
    {% set _ = styles.append('border-radius: ' ~ tokens.border_radius[appearance.radius] ~ ';') %}
{% endif %}
```

### Potential Issues

1. **Condition Logic**: The condition `appearance.radius and ...` might fail if:
   - `appearance.radius` is `None` (Python None, not string 'none')
   - `appearance.radius` is an empty string `''`
   - `appearance.radius` is `0` (falsy number)
   - The token lookup fails silently

2. **Token Lookup**: The `in` operator checks if a key exists in a dict, which should work, but:
   - If `appearance.radius` is not exactly matching the token keys, it fails
   - Case sensitivity issues
   - Type mismatches (string vs number)

3. **Style Application**: Even if the style is generated, it might not be applied if:
   - The style string is empty or malformed
   - CSS overrides are happening
   - The style attribute is not being set correctly

## Investigation Steps

1. ✅ Verify tokens are loaded correctly (`border_radius` exists with keys: `none`, `sm`, `md`, `lg`, `pill`)
2. ⏳ Test with sample YAML to see what values `appearance.radius` actually has
3. ⏳ Check if the condition is evaluating correctly
4. ⏳ Verify the generated CSS is correct
5. ⏳ Check for CSS overrides

## Fix Strategy

### Option 1: Improve Condition Logic
Make the condition more robust to handle edge cases:
```jinja2
{% if props.appearance and props.appearance.radius is defined and props.appearance.radius is not none %}
    {% set radius_value = props.appearance.radius %}
    {% if tokens and tokens.border_radius and radius_value in tokens.border_radius %}
        {% set _ = styles.append('border-radius: ' ~ tokens.border_radius[radius_value] ~ ';') %}
    {% elif radius_value is number %}
        {% set _ = styles.append('border-radius: ' ~ radius_value ~ 'px;') %}
    {% elif radius_value is string and radius_value %}
        {% set _ = styles.append('border-radius: ' ~ radius_value ~ ';') %}
    {% endif %}
{% endif %}
```

### Option 2: Simplify and Make More Explicit
```jinja2
{% if props.appearance %}
    {% set appearance = props.appearance %}
    {% if appearance.radius is defined %}
        {% set radius_token = appearance.radius %}
        {% if radius_token and tokens and tokens.border_radius %}
            {% if radius_token in tokens.border_radius %}
                {% set _ = styles.append('border-radius: ' ~ tokens.border_radius[radius_token] ~ ';') %}
            {% elif radius_token is number %}
                {% set _ = styles.append('border-radius: ' ~ radius_token ~ 'px;') %}
            {% elif radius_token is string and radius_token|trim %}
                {% set _ = styles.append('border-radius: ' ~ radius_token ~ ';') %}
            {% endif %}
        {% endif %}
    {% endif %}
{% endif %}
```

### Option 3: Match Client-Side Logic
The client-side code uses `resolveBorderRadiusToken` which:
- Returns `null` for undefined/null/empty
- Looks up in `BORDER_RADIUS_MAP`
- Handles numeric values (converts to px)
- Handles string values (returns as-is if valid)

We should replicate this logic in Jinja2.

## Recommended Fix

Use **Option 2** with additional debugging/logging to ensure it works:

```jinja2
{# Appearance (Background, Border, Radius, Shadow, Padding) #}
{% if props.appearance %}
    {% set appearance = props.appearance %}
    {% if appearance.background and appearance.background.color %}
        {% set _ = styles.append('background-color: ' ~ appearance.background.color ~ ';') %}
    {% endif %}
    {% if appearance.border %}
        {% set border = appearance.border %}
        {% set _ = styles.append('border: ' ~ (border.width | default(1)) ~ 'px ' ~ (border.style | default('solid')) ~ ' ' ~ (border.color | default('#e5e7eb')) ~ ';') %}
    {% endif %}
    {# Border Radius - Improved logic #}
    {% if appearance.radius is defined %}
        {% set radius_value = appearance.radius %}
        {% if radius_value is not none and radius_value != '' %}
            {% if tokens and tokens.border_radius and radius_value in tokens.border_radius %}
                {% set _ = styles.append('border-radius: ' ~ tokens.border_radius[radius_value] ~ ';') %}
            {% elif radius_value is number %}
                {% set _ = styles.append('border-radius: ' ~ radius_value ~ 'px;') %}
            {% elif radius_value is string and radius_value|trim %}
                {% set _ = styles.append('border-radius: ' ~ radius_value ~ ';') %}
            {% endif %}
        {% endif %}
    {% endif %}
    {% if appearance.shadow %}
        {% set _ = styles.append('box-shadow: ' ~ appearance.shadow ~ ';') %}
    {% endif %}
    {# ... rest of appearance handling ... #}
{% endif %}
```

## Testing

After implementing the fix, test with:

1. **Token values**: `none`, `sm`, `md`, `lg`, `pill`
2. **Numeric values**: `5`, `10`, `20` (should convert to px)
3. **String values**: `'5px'`, `'1rem'`, `'50%'` (should use as-is)
4. **Edge cases**: `null`, `undefined`, empty string, `0`

## Files to Modify

- `ssr_python/templates/macros/_components.html` - Update `build_styles` macro (line ~692)

## Expected Outcome

Border radius should work for all components that have `appearance.radius` set in their properties, matching the behavior of the client-side implementation.


