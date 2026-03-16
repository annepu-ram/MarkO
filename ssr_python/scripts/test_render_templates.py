#!/usr/bin/env python
"""
Template Render Test — loads each example_templates/*.yaml file, parses it,
and runs it through render_yaml_structure() to verify it renders without errors.

Usage:
    cd ssr_python
    python scripts/test_render_templates.py                       # test all
    python scripts/test_render_templates.py banner_announcement   # test one folder
    python scripts/test_render_templates.py hero/14_food_delivery.yaml  # one file
"""
import sys
import os
import glob
import yaml

# Add ssr_python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from renderer import render_yaml_structure
from extensions import TOKENS, COMPONENT_DEFAULTS

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "example_templates")


def collect_files(filter_arg=None):
    """Collect YAML files to test, optionally filtered by folder or file path."""
    if filter_arg:
        # Check if it's a direct file path
        candidate = os.path.join(TEMPLATES_DIR, filter_arg)
        if os.path.isfile(candidate):
            return [candidate]
        # Check if it's a folder name
        if os.path.isdir(candidate):
            return sorted(glob.glob(os.path.join(candidate, "**", "*.yaml"), recursive=True))
        # Try as glob pattern
        matches = sorted(glob.glob(os.path.join(TEMPLATES_DIR, filter_arg, "**", "*.yaml"), recursive=True))
        if matches:
            return matches
        print(f"{RED}No files found matching: {filter_arg}{RESET}")
        sys.exit(1)

    return sorted(glob.glob(os.path.join(TEMPLATES_DIR, "**", "*.yaml"), recursive=True))


def rel_path(filepath):
    """Get path relative to example_templates/."""
    return os.path.relpath(filepath, TEMPLATES_DIR)


def test_file(filepath, app):
    """Test a single YAML file. Returns (passed: bool, error_msg: str|None)."""
    # Step 1: Parse YAML
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            structure = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {e}"

    if not isinstance(structure, list) or not structure:
        return False, "Invalid structure: root is not a non-empty list"

    # Step 2: Render
    try:
        with app.app_context():
            html = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    except Exception as e:
        return False, f"Render error: {e}"

    # Step 3: Check for error markers in output
    if html.strip().startswith("<!-- Invalid YAML:"):
        return False, f"Renderer returned error: {html.strip()[:120]}"

    if not html.strip():
        return False, "Renderer returned empty HTML"

    return True, None


def main():
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None

    # Create Flask app to load shared data and provide app context
    app = create_app()

    files = collect_files(filter_arg)
    print(f"\n{BOLD}Testing {len(files)} template files...{RESET}\n")

    passed = 0
    failed = 0
    failures = []

    for filepath in files:
        name = rel_path(filepath)
        ok, error = test_file(filepath, app)
        if ok:
            passed += 1
            print(f"  {GREEN}[PASS]{RESET} {name}")
        else:
            failed += 1
            failures.append((name, error))
            print(f"  {RED}[FAIL]{RESET} {name}")
            print(f"         {DIM}{error}{RESET}")

    # Summary
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    if failed == 0:
        print(f"  {GREEN}{BOLD}All {passed} templates passed!{RESET}")
    else:
        print(f"  {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET} ({passed + failed} total)")
        print(f"\n  {RED}{BOLD}Failures:{RESET}")
        for name, error in failures:
            print(f"    {RED}- {name}{RESET}")
            print(f"      {DIM}{error}{RESET}")
    print()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
