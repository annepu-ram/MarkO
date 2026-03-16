import yaml
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

storage = None  # Set by app.py after create_storage()

TOKENS = {}
COMPONENT_DEFAULTS = {}


def load_shared_data(app):
    """Load design tokens and component defaults into shared module-level state.

    Uses .clear() + .update() to mutate the existing dict objects in-place,
    so any module that imported TOKENS or COMPONENT_DEFAULTS keeps a valid reference.
    """
    tokens_path = app.config.get('TOKENS_PATH', '')
    if os.path.exists(tokens_path):
        with open(tokens_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f) or {}
        TOKENS.clear()
        TOKENS.update(loaded)
        app.logger.info(f"Loaded tokens from {tokens_path}")
        app.logger.info(f"Tokens keys: {list(TOKENS.keys()) if TOKENS else 'None'}")
    else:
        app.logger.warning(f"tokens.yaml not found at {tokens_path}")

    defaults_path = app.config.get('DEFAULTS_PATH', '')
    if os.path.exists(defaults_path):
        with open(defaults_path, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f) or {}
        COMPONENT_DEFAULTS.clear()
        COMPONENT_DEFAULTS.update(loaded)
        app.logger.info(f"Loaded component defaults from {defaults_path}")
        app.logger.info(f"Available components: {list(COMPONENT_DEFAULTS.keys()) if COMPONENT_DEFAULTS else 'None'}")
    else:
        app.logger.warning(f"component_defaults.yaml not found at {defaults_path}")
