"""
ssr_python/rag/scripts/seed_industry_config.py
──────────────────────────────────────────────
Seeds (or re-seeds) the `industry_configs` DB table from
`rag/industry_defaults.py`.

Usage as CLI (full re-seed / overwrite existing rows):
    cd ssr_python
    python -m rag.scripts.seed_industry_config           # seed only if empty
    python -m rag.scripts.seed_industry_config --force   # overwrite all rows

Usage from app startup:
    from rag.scripts.seed_industry_config import seed_industry_config
    seed_industry_config(force=False)   # no-op if rows already exist

The table has one row per config_key: 'industries', 'section_questions',
'recommendations', 'page_purposes'.
"""
from __future__ import annotations

import sys
import os

# Ensure ssr_python is on the Python path when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


CONFIG_KEYS = ("industries", "section_questions", "recommendations", "page_purposes")


def _build_payloads():
    """Return a {config_key → dict} mapping of all seed data."""
    from rag.industry_defaults import (
        INDUSTRY_REGISTRY,
        SECTION_QUESTIONS,
        SECTION_RECOMMENDATIONS,
        CATEGORY_FLOWS,
        PAGE_PURPOSES,
    )
    return {
        "industries": INDUSTRY_REGISTRY,
        "section_questions": SECTION_QUESTIONS,
        "recommendations": {
            "section_pairs": SECTION_RECOMMENDATIONS,
            "category_flows": CATEGORY_FLOWS,
        },
        "page_purposes": {"purposes": PAGE_PURPOSES},
    }


def seed_industry_config(force: bool = False) -> dict:
    """
    Seed the `industry_configs` table from `rag/industry_defaults.py`.

    Args:
        force: If True, overwrite existing rows. If False (default), only
               insert rows that don't already exist.

    Returns:
        {"inserted": int, "updated": int, "skipped": int}

    Must be called within a Flask app context (so `db.session` is bound).
    """
    from extensions import db
    from models import IndustryConfig

    payloads = _build_payloads()
    result = {"inserted": 0, "updated": 0, "skipped": 0}

    for key in CONFIG_KEYS:
        data = payloads[key]
        row = IndustryConfig.query.filter_by(config_key=key).first()
        if row is None:
            row = IndustryConfig(config_key=key)
            row.set_data(data)
            db.session.add(row)
            result["inserted"] += 1
        elif force:
            row.set_data(data)
            result["updated"] += 1
        else:
            result["skipped"] += 1

    db.session.commit()
    return result


def main():
    """CLI entry point."""
    from app import create_app

    force = "--force" in sys.argv

    app = create_app()
    with app.app_context():
        result = seed_industry_config(force=force)

    print(f"IndustryConfig seed result: {result}")
    if result["skipped"] > 0 and not force:
        print("  (use --force to overwrite existing rows)")


if __name__ == "__main__":
    main()
