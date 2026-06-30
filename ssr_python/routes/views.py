from flask import Blueprint, render_template, g
from models import Organization

views_bp = Blueprint('views', __name__)


@views_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


@views_bp.route('/')
def dashboard():
    """Serve the dashboard/welcome page."""
    return render_template('dashboard.html', user_role=g.current_role)


@views_bp.route('/editor/<site_id>')
def editor(site_id):
    """Serve the editor for a specific site."""
    return render_template('index.html', site_id=site_id, user_role=g.current_role)


@views_bp.route('/campaign-studio/<campaign_id>')
def campaign_studio(campaign_id):
    """Serve the Campaign Studio workspace."""
    return render_template('campaign_studio.html', campaign_id=campaign_id, user_role=g.current_role)


@views_bp.route('/preview-frame')
def preview_frame():
    """Serve the preview iframe content"""
    return render_template('preview_frame.html')
