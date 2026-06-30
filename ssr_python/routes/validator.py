"""ssr_python/routes/validator.py — Template visual validator (browser carousel)."""
import glob
import os

from flask import Blueprint, render_template, jsonify, send_file

from config import Config

validator_bp = Blueprint('validator', __name__)

TEMPLATES_DIR = os.path.join(Config.BASE_DIR, '..', 'example_templates')


def _get_template_files():
    """Return sorted list of template paths relative to example_templates/."""
    files = glob.glob(os.path.join(TEMPLATES_DIR, '**', '*.yaml'), recursive=True)
    rel = [os.path.relpath(f, TEMPLATES_DIR).replace('\\', '/') for f in sorted(files)]
    return rel


@validator_bp.route('/validator')
def validator_page():
    return render_template('validator.html')


@validator_bp.route('/api/validator/templates')
def list_templates():
    return jsonify(_get_template_files())


@validator_bp.route('/api/validator/templates/<int:index>')
def get_template(index):
    files = _get_template_files()
    if index < 0 or index >= len(files):
        return 'Index out of range', 404
    filepath = os.path.join(TEMPLATES_DIR, files[index])
    return send_file(filepath, mimetype='text/plain')
