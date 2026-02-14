from flask import Blueprint, jsonify, current_app
import yaml
import os

metadata_bp = Blueprint('metadata', __name__)


@metadata_bp.route('/api/schemas')
def get_schemas():
    """Serve component schemas as JSON"""
    schemas_path = current_app.config['SCHEMAS_PATH']
    if os.path.exists(schemas_path):
        with open(schemas_path, 'r') as f:
            schemas = yaml.safe_load(f)
        return jsonify(schemas or {})
    return jsonify({}), 404


@metadata_bp.route('/api/defaults')
def get_defaults():
    """Serve component defaults as JSON"""
    defaults_path = current_app.config['DEFAULTS_PATH']
    if os.path.exists(defaults_path):
        with open(defaults_path, 'r') as f:
            defaults = yaml.safe_load(f)
        return jsonify(defaults or {})
    return jsonify({}), 404


@metadata_bp.route('/api/tokens')
def get_schema_tokens():
    """Serve schema tokens as JSON"""
    tokens_path = current_app.config['SCHEMA_TOKENS_PATH']
    if os.path.exists(tokens_path):
        with open(tokens_path, 'r') as f:
            tokens = yaml.safe_load(f)
        return jsonify(tokens or {})
    return jsonify({}), 404
