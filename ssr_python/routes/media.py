"""
Media Library API — browse and manage images per site.

Endpoints:
- GET    /api/sites/<site_id>/media              — list images (filterable by page, orientation, search)
- PATCH  /api/sites/<site_id>/media/<image_id>   — update image metadata
- DELETE /api/sites/<site_id>/media/<image_id>   — delete image
- POST   /api/sites/<site_id>/media/bulk         — bulk delete
"""
from flask import Blueprint, g, jsonify, request
from extensions import db, storage
from models import SiteImage, Organization
from guards import get_site_or_404

media_bp = Blueprint('media', __name__)


@media_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


@media_bp.route('/api/sites/<site_id>/media')
def list_media(site_id):
    """List all images for a site, with optional filters."""
    site = get_site_or_404(site_id)

    query = SiteImage.query.filter(
        db.or_(SiteImage.site_id == site.id, SiteImage.site_id.is_(None))
    )

    # Filter by page
    page_id = request.args.get('page_id')
    if page_id:
        query = query.filter_by(page_id=page_id)

    # Filter by orientation
    orientation = request.args.get('orientation')
    if orientation in ('landscape', 'portrait', 'square'):
        query = query.filter_by(orientation=orientation)

    # Search by alt_text or filename
    search = request.args.get('q', '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                SiteImage.alt_text.ilike(like),
                SiteImage.original_name.ilike(like),
                SiteImage.photographer.ilike(like),
            )
        )

    # Filter by source
    source = request.args.get('source')
    if source:
        query = query.filter_by(source=source)

    images = query.order_by(SiteImage.created_at.desc()).all()

    return jsonify({
        'images': [_serialize_image(img) for img in images],
        'total': len(images),
    })


@media_bp.route('/api/sites/<site_id>/media/<image_id>', methods=['PATCH'])
def update_image(site_id, image_id):
    """Update image metadata (alt_text, page_id, etc.)."""
    site = get_site_or_404(site_id)
    image = SiteImage.query.filter_by(id=image_id, site_id=site.id).first()
    if not image:
        return jsonify({'error': 'Image not found.'}), 404

    data = request.get_json() or {}

    if 'alt_text' in data:
        image.alt_text = str(data['alt_text'])[:500]
    if 'photographer' in data:
        image.photographer = str(data['photographer'])[:255]
    if 'page_id' in data:
        image.page_id = data['page_id']  # None to unassign

    db.session.commit()
    return jsonify(_serialize_image(image))


@media_bp.route('/api/sites/<site_id>/media/<image_id>', methods=['DELETE'])
def delete_image(site_id, image_id):
    """Delete an image from storage and database."""
    site = get_site_or_404(site_id)
    image = SiteImage.query.filter_by(id=image_id, site_id=site.id).first()
    if not image:
        return jsonify({'error': 'Image not found.'}), 404

    # Remove from storage
    if image.storage_path and storage:
        try:
            storage.delete(image.storage_path)
        except Exception:
            pass  # Storage deletion is best-effort

    db.session.delete(image)
    db.session.commit()
    return jsonify({'deleted': True, 'id': image_id})


@media_bp.route('/api/sites/<site_id>/media/bulk', methods=['POST'])
def bulk_action(site_id):
    """Bulk delete images."""
    site = get_site_or_404(site_id)
    data = request.get_json() or {}

    action = data.get('action')
    image_ids = data.get('image_ids', [])

    if not image_ids:
        return jsonify({'error': 'No image_ids provided.'}), 400
    if len(image_ids) > 50:
        return jsonify({'error': 'Maximum 50 images per bulk operation.'}), 400

    if action == 'delete':
        images = SiteImage.query.filter(
            SiteImage.id.in_(image_ids),
            SiteImage.site_id == site.id,
        ).all()

        for image in images:
            if image.storage_path and storage:
                try:
                    storage.delete(image.storage_path)
                except Exception:
                    pass
            db.session.delete(image)

        db.session.commit()
        return jsonify({'deleted': len(images)})

    return jsonify({'error': f'Unknown action: {action}'}), 400


def _serialize_image(img):
    """Serialize a SiteImage to dict for JSON response."""
    url = f'/uploads/{img.storage_path}' if img.storage_path else f'/uploads/{img.filename}'
    return {
        'id': img.id,
        'url': url,
        'filename': img.filename,
        'original_name': img.original_name,
        'alt_text': img.alt_text,
        'orientation': img.orientation,
        'width': img.width,
        'height': img.height,
        'file_size': img.file_size,
        'photographer': img.photographer,
        'source': img.source,
        'mime_type': img.mime_type,
        'page_id': img.page_id,
        'created_at': img.created_at.isoformat() if img.created_at else None,
    }
