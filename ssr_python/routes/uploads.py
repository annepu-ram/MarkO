"""
Image Upload, Download & Serving Routes — WebP conversion for all stored images.

- POST /api/images/upload — upload image, convert to WebP, store
- POST /api/images/download — download external image, convert to WebP, store
- POST /api/images/download-batch — batch download multiple images
- GET /uploads/<path:storage_path> — serve stored images (local backend)
"""
import io
import os
import re
import uuid
from urllib.parse import urlparse
from flask import Blueprint, current_app, jsonify, request, send_from_directory, abort, g
from PIL import Image
import requests as http_requests
from extensions import db, storage
from models import SiteImage, compute_orientation

uploads_bp = Blueprint('uploads', __name__)

# Allowed MIME types for upload
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'image/svg+xml',
}

# Filename pattern for stored files: UUID hex + extension
SAFE_FILENAME_RE = re.compile(r'^[0-9a-f]{32}\.(webp|svg)$')


def convert_to_webp(image_bytes, quality=85):
    """Convert any raster image to WebP format.

    Returns (webp_bytes, width, height).
    Raises ValueError if the image cannot be processed.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Preserve transparency for PNG/GIF
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')

    output = io.BytesIO()
    img.save(output, format='webp', quality=quality)
    return output.getvalue(), img.width, img.height


# =============================================================================
# Upload Endpoint
# =============================================================================

@uploads_bp.route('/api/images/upload', methods=['POST'])
def upload_image():
    """Upload an image, convert to WebP (except SVGs), and store.

    Request: multipart/form-data with 'file' field
    Optional query param: site_id (to associate with a site)
    Response: { id, filename, url, width, height, mime_type, file_size }
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected.'}), 400

    # Validate MIME type
    content_type = file.content_type or ''
    if content_type not in ALLOWED_MIME_TYPES:
        return jsonify({'error': f'File type "{content_type}" is not allowed. Use JPEG, PNG, GIF, WebP, or SVG.'}), 400

    original_name = file.filename
    file_bytes = file.read()

    if not file_bytes:
        return jsonify({'error': 'Empty file.'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
    file_id = uuid.uuid4().hex  # 32-char hex for filename

    # Optional site association
    site_id = request.form.get('site_id') or request.args.get('site_id')

    # Determine org_id for tenant-isolated storage path
    org_id = getattr(g, 'current_org_id', 'default')
    storage_site_id = site_id or '_shared'

    if content_type == 'image/svg+xml':
        # SVGs are stored as-is (vector format, no conversion)
        filename = f'{file_id}.svg'
        storage_path = storage.generate_path(org_id, storage_site_id, filename)
        url = storage.save(file_bytes, storage_path, content_type='image/svg+xml')
        width, height = None, None
        mime_type = 'image/svg+xml'
        file_size = len(file_bytes)
        orientation = None
    else:
        # Convert raster images to WebP
        try:
            webp_bytes, width, height = convert_to_webp(file_bytes)
        except Exception as e:
            current_app.logger.error(f'WebP conversion failed: {e}')
            return jsonify({'error': 'Failed to process image. Please try a different file.'}), 400

        filename = f'{file_id}.webp'
        storage_path = storage.generate_path(org_id, storage_site_id, filename)
        url = storage.save(webp_bytes, storage_path)
        mime_type = 'image/webp'
        file_size = len(webp_bytes)
        orientation = compute_orientation(width, height)

    # Derive alt text from original filename
    alt_text = os.path.splitext(original_name)[0].replace('-', ' ').replace('_', ' ')

    # Store metadata in DB
    image = SiteImage(
        site_id=site_id,
        filename=filename,
        storage_path=storage_path,
        original_name=original_name,
        mime_type=mime_type,
        file_size=file_size,
        width=width,
        height=height,
        orientation=orientation,
        source='upload',
        alt_text=alt_text,
    )
    db.session.add(image)
    db.session.commit()

    return jsonify({
        'id': image.id,
        'filename': image.filename,
        'url': url,
        'width': width,
        'height': height,
        'orientation': orientation,
        'mime_type': mime_type,
        'file_size': file_size,
        'original_name': original_name,
    }), 201


# =============================================================================
# Download External Images
# =============================================================================

ALLOWED_DOWNLOAD_DOMAINS = {
    'images.pexels.com', 'pixabay.com', 'cdn.pixabay.com', 'images.unsplash.com',
}
MAX_DOWNLOAD_SIZE = 15 * 1024 * 1024  # 15MB


def _download_and_store(url, site_id=None, alt_text='', photographer='', source='stock'):
    """Download an external image, convert to WebP, store via storage backend.

    Returns dict with image metadata on success.
    Raises ValueError with user-safe message on failure.
    """
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        raise ValueError('Only HTTPS URLs are allowed.')
    if parsed.hostname not in ALLOWED_DOWNLOAD_DOMAINS:
        raise ValueError(f'Domain "{parsed.hostname}" is not in the allowed list.')

    # Deduplication — skip if already downloaded
    existing = SiteImage.query.filter_by(source_url=url).first()
    if existing:
        img_url = f'/uploads/{existing.storage_path}' if existing.storage_path else f'/uploads/{existing.filename}'
        return {
            'id': existing.id,
            'filename': existing.filename,
            'url': img_url,
            'width': existing.width,
            'height': existing.height,
            'orientation': existing.orientation,
            'file_size': existing.file_size,
            'already_existed': True,
        }

    # Stream download with size limit
    resp = http_requests.get(url, timeout=15, stream=True)
    resp.raise_for_status()

    content_length = resp.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
        raise ValueError(f'Image too large ({int(content_length) // 1024 // 1024}MB). Max is 15MB.')

    content_type = resp.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f'URL did not return an image (got {content_type}).')

    chunks = []
    downloaded = 0
    for chunk in resp.iter_content(chunk_size=8192):
        downloaded += len(chunk)
        if downloaded > MAX_DOWNLOAD_SIZE:
            raise ValueError('Image exceeded 15MB size limit during download.')
        chunks.append(chunk)
    image_bytes = b''.join(chunks)

    # Convert to WebP
    webp_bytes, width, height = convert_to_webp(image_bytes)

    # Store via storage backend
    file_id = uuid.uuid4().hex
    filename = f'{file_id}.webp'
    org_id = getattr(g, 'current_org_id', 'default')
    storage_site_id = site_id or '_shared'
    storage_path = storage.generate_path(org_id, storage_site_id, filename)
    stored_url = storage.save(webp_bytes, storage_path)

    orientation = compute_orientation(width, height)

    image = SiteImage(
        site_id=site_id,
        filename=filename,
        storage_path=storage_path,
        original_name=alt_text.strip()[:100] if alt_text else os.path.basename(parsed.path) or 'downloaded',
        mime_type='image/webp',
        file_size=len(webp_bytes),
        width=width,
        height=height,
        orientation=orientation,
        source=source,
        source_url=url,
        photographer=photographer,
        alt_text=alt_text,
    )
    db.session.add(image)
    db.session.commit()

    return {
        'id': image.id,
        'filename': filename,
        'url': stored_url,
        'width': width,
        'height': height,
        'orientation': orientation,
        'file_size': len(webp_bytes),
        'already_existed': False,
    }


@uploads_bp.route('/api/images/download', methods=['POST'])
def download_image():
    """Download a single external image, convert to WebP, and store."""
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400

    try:
        result = _download_and_store(
            url=url,
            site_id=data.get('site_id'),
            alt_text=data.get('alt_text', ''),
            photographer=data.get('photographer', ''),
            source=data.get('source', 'stock'),
        )
        return jsonify(result), 200 if result.get('already_existed') else 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'Download timed out. Please try again.'}), 504
    except http_requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 502
        return jsonify({'error': f'Failed to download image (HTTP {status}).'}), 502
    except Exception as e:
        current_app.logger.error(f'Image download failed: {e}')
        return jsonify({'error': 'Failed to download image.'}), 500


@uploads_bp.route('/api/images/download-batch', methods=['POST'])
def download_batch():
    """Download multiple external images. Returns per-image results."""
    data = request.get_json() or {}
    images = data.get('images', [])
    site_id = data.get('site_id')

    if not images:
        return jsonify({'error': 'No images provided.'}), 400
    if len(images) > 20:
        return jsonify({'error': 'Maximum 20 images per batch.'}), 400

    results = []
    downloaded = 0
    failed = 0

    for img in images:
        url = img.get('url', '').strip()
        if not url:
            results.append({'original_url': url, 'error': 'Empty URL', 'local_url': None, 'id': None})
            failed += 1
            continue
        try:
            result = _download_and_store(
                url=url,
                site_id=site_id,
                alt_text=img.get('alt_text', ''),
                photographer=img.get('photographer', ''),
                source=img.get('source', 'stock'),
            )
            results.append({
                'original_url': url,
                'local_url': result['url'],
                'id': result['id'],
                'orientation': result.get('orientation'),
                'error': None,
            })
            downloaded += 1
        except Exception as e:
            results.append({'original_url': url, 'error': str(e), 'local_url': None, 'id': None})
            failed += 1

    return jsonify({'results': results, 'downloaded': downloaded, 'failed': failed})


# =============================================================================
# Serve Stored Images
# =============================================================================

@uploads_bp.route('/uploads/<path:storage_path>')
def serve_upload(storage_path):
    """Serve a stored image file (local backend only). S3/GCS use direct URLs.

    Supports both legacy flat paths (uuid.webp) and tenant-scoped paths (org/site/uuid.webp).
    """
    parts = storage_path.split('/')

    if len(parts) == 1:
        # Legacy flat path: uuid.webp
        filename = parts[0]
        if not SAFE_FILENAME_RE.match(filename):
            abort(404)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
        return send_from_directory(upload_folder, filename)

    elif len(parts) == 3:
        # Tenant-scoped path: org_id/site_id/uuid.webp
        org_id, site_id, filename = parts
        if not SAFE_FILENAME_RE.match(filename):
            abort(404)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
        full_dir = os.path.join(upload_folder, org_id, site_id)
        return send_from_directory(full_dir, filename)

    else:
        abort(404)
