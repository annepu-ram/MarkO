"""
Form Submissions API — list, update, delete, CSV export for dashboard.

Org-scoped via guards. Pre-auth stub sets g.current_org_id until real auth.
"""
import csv
import io
import json
from flask import Blueprint, g, jsonify, request, abort, Response
from extensions import db
from models import Organization, Site, FormSubmission
from guards import get_site_or_404, require_role

submissions_bp = Blueprint('submissions', __name__)


# =============================================================================
# Pre-Auth Stub (same pattern as site_bp)
# =============================================================================

@submissions_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


# =============================================================================
# List Submissions
# =============================================================================

@submissions_bp.route('/api/submissions', methods=['GET'])
def list_submissions():
    """List submissions across all org sites with optional filters.

    Query params: site_id, filter (all|unread|spam), page, per_page
    """
    site_ids = [s.id for s in Site.query.filter_by(org_id=g.current_org_id).all()]
    if not site_ids:
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0})

    query = FormSubmission.query.filter(FormSubmission.site_id.in_(site_ids))

    # Filter by specific site
    site_filter = request.args.get('site_id')
    if site_filter and site_filter in site_ids:
        query = query.filter_by(site_id=site_filter)

    # Filter by status
    status_filter = request.args.get('filter', 'all')
    if status_filter == 'unread':
        query = query.filter_by(is_read=False, is_spam=False)
    elif status_filter == 'spam':
        query = query.filter_by(is_spam=True)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 25, type=int), 100)

    paginated = query.order_by(FormSubmission.submitted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Get site names for display
    sites_map = {s.id: s.name for s in Site.query.filter(Site.id.in_(site_ids)).all()}

    return jsonify({
        'items': [
            {
                'id': sub.id,
                'site_id': sub.site_id,
                'site_name': sites_map.get(sub.site_id, ''),
                'page_slug': sub.page_slug,
                'form_name': sub.form_name,
                'data': json.loads(sub.data) if sub.data else {},
                'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None,
                'is_spam': sub.is_spam,
                'is_read': sub.is_read,
            }
            for sub in paginated.items
        ],
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
    })


# =============================================================================
# Update Submission (mark read/spam)
# =============================================================================

@submissions_bp.route('/api/submissions/<submission_id>', methods=['PATCH'])
@require_role('editor')
def update_submission(submission_id):
    """Mark submission as read/unread or spam/not-spam."""
    sub = FormSubmission.query.get(submission_id)
    if not sub:
        abort(404)
    get_site_or_404(sub.site_id)  # IDOR check

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if 'is_read' in data:
        sub.is_read = bool(data['is_read'])
    if 'is_spam' in data:
        sub.is_spam = bool(data['is_spam'])

    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Delete Submission
# =============================================================================

@submissions_bp.route('/api/submissions/<submission_id>', methods=['DELETE'])
@require_role('admin')
def delete_submission(submission_id):
    """Delete a single submission."""
    sub = FormSubmission.query.get(submission_id)
    if not sub:
        abort(404)
    get_site_or_404(sub.site_id)  # IDOR check
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# CSV Export
# =============================================================================

@submissions_bp.route('/api/submissions/export', methods=['GET'])
def export_submissions_csv():
    """Export filtered submissions as CSV download.

    Query params: site_id (optional), filter (optional)
    """
    site_ids = [s.id for s in Site.query.filter_by(org_id=g.current_org_id).all()]
    if not site_ids:
        return Response('', mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=submissions.csv'})

    query = FormSubmission.query.filter(FormSubmission.site_id.in_(site_ids))

    site_filter = request.args.get('site_id')
    if site_filter and site_filter in site_ids:
        query = query.filter_by(site_id=site_filter)

    status_filter = request.args.get('filter', 'all')
    if status_filter == 'unread':
        query = query.filter_by(is_read=False, is_spam=False)
    elif status_filter == 'spam':
        query = query.filter_by(is_spam=True)

    submissions = query.order_by(FormSubmission.submitted_at.desc()).all()

    # Collect all data keys across submissions for CSV headers
    all_keys = set()
    rows = []
    for sub in submissions:
        data = json.loads(sub.data) if sub.data else {}
        all_keys.update(data.keys())
        rows.append({
            'id': sub.id,
            'site_id': sub.site_id,
            'form_name': sub.form_name,
            'page_slug': sub.page_slug,
            'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else '',
            'is_spam': sub.is_spam,
            'is_read': sub.is_read,
            **data,
        })

    fieldnames = ['id', 'site_id', 'form_name', 'page_slug', 'submitted_at',
                  'is_spam', 'is_read'] + sorted(all_keys)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=submissions.csv'},
    )
