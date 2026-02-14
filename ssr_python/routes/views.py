from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    return render_template('index.html')


@views_bp.route('/preview-frame')
def preview_frame():
    """Serve the preview iframe content"""
    return render_template('preview_frame.html')
