"""
Marketing CMS Media Library API.

Media is organization-scoped, not site-scoped. Assets can be reused by brands,
products, campaigns, content, and generated websites.

Endpoints:
- GET    /api/media              List media assets with filters
- PATCH  /api/media/<asset_id>   Update asset metadata
- DELETE /api/media/<asset_id>   Delete asset
- POST   /api/media/bulk         Bulk delete assets
"""
import json

from flask import Blueprint, abort, g, jsonify, request

from extensions import db, storage
from guards import require_role
from models import Brand, MediaAsset, Organization, Product, Site, SitePage

media_bp = Blueprint('media', __name__)


@media_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


@media_bp.route('/api/media')
def list_org_media():
    """List reusable organization media with CMS-style filters."""
    query = MediaAsset.query.filter_by(org_id=g.current_org_id)

    search = request.args.get('q', '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(
            MediaAsset.filename.ilike(like),
            MediaAsset.original_name.ilike(like),
            MediaAsset.alt_text.ilike(like),
            MediaAsset.photographer.ilike(like),
            MediaAsset.tags.ilike(like),
        ))

    source = request.args.get('source', '').strip()
    if source:
        query = query.filter_by(source=source)

    orientation = request.args.get('orientation', '').strip()
    if orientation in ('landscape', 'portrait', 'square'):
        query = query.filter_by(orientation=orientation)

    assets = query.order_by(MediaAsset.created_at.desc()).all()
    serialized = [_serialize_media_asset(asset) for asset in assets]

    usage_filter = request.args.get('usage', '').strip()
    if usage_filter == 'used':
        serialized = [item for item in serialized if item['is_used']]
    elif usage_filter == 'unused':
        serialized = [item for item in serialized if not item['is_used']]

    return jsonify({
        'images': serialized,
        'total': len(serialized),
        'stats': _media_stats(serialized),
    })


@media_bp.route('/api/media/<asset_id>', methods=['PATCH'])
@require_role('editor')
def update_media_asset(asset_id):
    asset = _get_asset_or_404(asset_id)
    data = request.get_json() or {}

    if 'alt_text' in data:
        asset.alt_text = str(data['alt_text'] or '').strip()[:500] or None
    if 'photographer' in data:
        asset.photographer = str(data['photographer'] or '').strip()[:255] or None
    if 'license_label' in data:
        asset.license_label = str(data['license_label'] or '').strip()[:120] or None
    if 'tags' in data:
        tags = data['tags']
        if isinstance(tags, str):
            tags = [part.strip() for part in tags.replace('\n', ',').split(',')]
        if not isinstance(tags, list):
            return jsonify({'error': 'tags must be a list or comma-separated string.'}), 400
        asset.set_tags(tags)

    db.session.commit()
    return jsonify(_serialize_media_asset(asset))


@media_bp.route('/api/media/<asset_id>', methods=['DELETE'])
@require_role('editor')
def delete_media_asset(asset_id):
    asset = _get_asset_or_404(asset_id)
    if asset.storage_path and storage:
        try:
            storage.delete(asset.storage_path)
        except Exception:
            pass
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'deleted': True, 'id': asset_id})


@media_bp.route('/api/media/bulk', methods=['POST'])
@require_role('editor')
def bulk_media_action():
    data = request.get_json() or {}
    action = data.get('action')
    asset_ids = data.get('asset_ids') or data.get('image_ids') or []
    if not asset_ids:
        return jsonify({'error': 'No asset_ids provided.'}), 400
    if len(asset_ids) > 50:
        return jsonify({'error': 'Maximum 50 assets per bulk operation.'}), 400

    assets = MediaAsset.query.filter(
        MediaAsset.org_id == g.current_org_id,
        MediaAsset.id.in_(asset_ids),
    ).all()

    if action == 'delete':
        for asset in assets:
            if asset.storage_path and storage:
                try:
                    storage.delete(asset.storage_path)
                except Exception:
                    pass
            db.session.delete(asset)
        db.session.commit()
        return jsonify({'deleted': len(assets)})

    return jsonify({'error': f'Unknown action: {action}'}), 400


def _get_asset_or_404(asset_id):
    asset = MediaAsset.query.filter_by(id=asset_id, org_id=g.current_org_id).first()
    if not asset:
        abort(404)
    return asset


def _asset_url(asset):
    return asset.url or (f'/uploads/{asset.storage_path}' if asset.storage_path else '')


def _parse_tags(raw):
    try:
        tags = json.loads(raw) if raw else []
    except (TypeError, json.JSONDecodeError):
        tags = []
    return tags if isinstance(tags, list) else []


def _media_usage(asset):
    url = _asset_url(asset)
    probes = [value for value in (asset.id, url, asset.storage_path) if value]
    labels = []
    count = 0

    brand_count = Brand.query.filter(
        Brand.org_id == g.current_org_id,
        db.or_(
            Brand.logo_media_id == asset.id,
            Brand.favicon_media_id == asset.id,
            Brand.logo_url == url,
        ),
    ).count()
    if brand_count:
        labels.append(f'{brand_count} brand reference{"s" if brand_count != 1 else ""}')
        count += brand_count

    product_count = Product.query.filter(
        Product.org_id == g.current_org_id,
        db.or_(
            Product.default_media_id == asset.id,
            Product.default_image_url == url,
        ),
    ).count()
    if product_count:
        labels.append(f'{product_count} product reference{"s" if product_count != 1 else ""}')
        count += product_count

    page_count = 0
    if probes:
        page_query = SitePage.query.join(Site, SitePage.site_id == Site.id).filter(Site.org_id == g.current_org_id)
        page_filters = []
        for probe in probes:
            page_filters.extend([
                SitePage.yaml_content.contains(probe),
                SitePage.body_yaml_content.contains(probe),
            ])
        page_count = page_query.filter(db.or_(*page_filters)).count()
    if page_count:
        labels.append(f'{page_count} website page reference{"s" if page_count != 1 else ""}')
        count += page_count

    return {
        'count': count,
        'labels': labels,
        'is_used': count > 0,
    }


def _media_stats(items):
    stats = {
        'used': sum(1 for item in items if item['is_used']),
        'unused': sum(1 for item in items if not item['is_used']),
        'sources': {},
    }
    for item in items:
        source = item.get('source') or 'unknown'
        stats['sources'][source] = stats['sources'].get(source, 0) + 1
    return stats


def _serialize_media_asset(asset):
    url = _asset_url(asset)
    usage = _media_usage(asset)
    return {
        'id': asset.id,
        'type': 'media_asset',
        'url': url,
        'filename': asset.filename,
        'original_name': asset.original_name,
        'alt_text': asset.alt_text,
        'orientation': asset.orientation,
        'width': asset.width,
        'height': asset.height,
        'file_size': asset.file_size,
        'photographer': asset.photographer,
        'source': asset.source,
        'source_url': asset.source_url,
        'license_label': asset.license_label,
        'mime_type': asset.mime_type,
        'tags': asset.get_tags(),
        'focal_point': {
            'x': asset.focal_point_x,
            'y': asset.focal_point_y,
        },
        'usage_count': usage['count'],
        'usage_labels': usage['labels'],
        'is_used': usage['is_used'],
        'created_at': asset.created_at.isoformat() if asset.created_at else None,
    }
