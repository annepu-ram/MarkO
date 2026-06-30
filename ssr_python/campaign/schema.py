"""
Campaign schema — lightweight validation primitives (no external deps).

Plain helpers used by validators.py. We deliberately avoid Pydantic/jsonschema
in V1 per the brief; PyYAML + simple Python is enough.
"""


class CampaignValidationError(Exception):
    """Raised when a campaign / recipe / section-purpose document is invalid.

    Carries a list of human-readable error strings.
    """

    def __init__(self, errors):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = list(errors)
        super().__init__('; '.join(self.errors))


def require_keys(obj, keys, where):
    """Return a list of error strings for any missing/empty required keys."""
    errors = []
    if not isinstance(obj, dict):
        return [f'{where} must be a mapping/object.']
    for key in keys:
        if key not in obj or obj[key] in (None, '', [], {}):
            errors.append(f'{where} is missing required key "{key}".')
    return errors


def check_enum(value, allowed, field, where, errors, *, allow_empty=True):
    """Append an error if value (when present) is not in `allowed`."""
    if value in (None, ''):
        if not allow_empty:
            errors.append(f'{where}.{field} is required.')
        return
    if value not in allowed:
        sample = ', '.join(sorted(allowed)[:8])
        errors.append(
            f'{where}.{field} = "{value}" is not a valid value '
            f'(expected one of: {sample}, ...).'
        )


def check_enum_list(values, allowed, field, where, errors):
    """Validate a list whose every member must be in `allowed`."""
    if values in (None, ''):
        return
    if not isinstance(values, list):
        errors.append(f'{where}.{field} must be a list.')
        return
    for v in values:
        if v not in allowed:
            errors.append(f'{where}.{field} contains invalid value "{v}".')
