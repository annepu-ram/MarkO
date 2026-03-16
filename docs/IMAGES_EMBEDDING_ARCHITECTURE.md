# Image Embedding System Plan

## Context

Currently, Swift Sites uses external stock photo URLs (Pexels/Pixabay CDNs) directly in YAML templates. This causes problems:
- External URLs can break, have rate limits, and may violate hotlinking TOS
- LLM-generated templates use hardcoded placeholder URLs, not relevant images
- No workflow to download/store images locally for published sites
- No site-scoped image library

**Goal:** Download stock photos to local storage as WebP, associate them with sites, and integrate image selection into the website creation flow.

## Design Decisions
- **Resolution:** Use `regularUrl` (~1200px medium resolution) for downloads — good balance of quality and speed for web use
- **Images-first workflow:** Users always select/upload images **before** website creation or insertion. No post-creation replacement.
- **Storage:** Abstract storage backend supporting local filesystem, AWS S3, and Google GCS — swappable via config
- **Multi-tenant isolation:** Prefix-based path isolation `{org_id}/{site_id}/{filename}` — each site's images are stored in their own folder/prefix
- **Database:** Add `storage_path` column to `SiteImage` for full storage key, and `orientation` column (portrait/landscape/square) computed from dimensions

---

## Image Selection Workflow: Images-First Approach

All images are selected, uploaded, and downloaded to local storage **before** they are used in any template.

### Flow A: Before Website Creation
1. User searches stock photos or uploads images in the Images Panel / Media Library
2. Selected images are auto-downloaded to server as WebP
3. User asks LLM to "create a website"
4. LLM receives the downloaded images as context and uses their local `/uploads/` URLs in the generated YAML
5. If no images are selected, LLM prompts user: "Select some images first for a better result" (soft guidance, not blocking)

### Flow B: Adding Images to Existing Site (Chat-Driven)
1. User asks LLM to "add an image" or "add a hero section with an image"
2. LLM checks if user has downloaded images available in the Media Library
3. If **images available**: LLM uses them (matching by orientation + alt text)
4. If **no images available**: LLM responds with guidance: "Please select or upload images in the Images panel first, then I'll add them to your site."
5. User selects/uploads images → repeats the request → LLM uses the new images

---

## Phase 0: Storage Abstraction Layer & Multi-Tenant Isolation

### Why: Storage Backend Abstraction

Currently images are stored as flat files in `/instance/uploads/` with UUID filenames. This needs to change for two reasons:
1. **Cloud deployment**: Production should use S3 or GCS instead of local disk
2. **Tenant isolation**: Each org/site's images must be stored in isolated paths to prevent cross-tenant access

### Architecture: Strategy Pattern for Storage

Create a new file [storage.py](ssr_python/storage.py) with an abstract `StorageBackend` class and three implementations:

```
StorageBackend (abstract)
├── LocalStorage      — filesystem (dev/single-server)
├── S3Storage         — AWS S3 (production)
└── GCSStorage        — Google Cloud Storage (production)
```

All three share the same interface so upload/download/serve code never knows which backend is active.

### File: NEW [storage.py](ssr_python/storage.py)

```python
import io
import os
import uuid
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """Abstract interface for image storage."""

    @abstractmethod
    def save(self, file_bytes: bytes, storage_path: str, content_type: str = 'image/webp') -> str:
        """Save bytes to storage. Returns the public URL for the file."""
        ...

    @abstractmethod
    def delete(self, storage_path: str) -> bool:
        """Delete a file from storage. Returns True if deleted."""
        ...

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        """Get a public/servable URL for the given storage path."""
        ...

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Check if a file exists at the given path."""
        ...

    def generate_path(self, org_id: str, site_id: str, filename: str) -> str:
        """Generate a tenant-isolated storage path.
        Format: {org_id}/{site_id}/{uuid}.webp
        """
        return f'{org_id}/{site_id}/{filename}'


class LocalStorage(StorageBackend):
    """Store files on the local filesystem."""

    def __init__(self, base_dir: str, url_prefix: str = '/uploads'):
        self.base_dir = base_dir
        self.url_prefix = url_prefix

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        full_path = os.path.join(self.base_dir, storage_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(file_bytes)
        return self.get_url(storage_path)

    def delete(self, storage_path):
        full_path = os.path.join(self.base_dir, storage_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_url(self, storage_path):
        # Returns /uploads/org_id/site_id/filename.webp
        return f'{self.url_prefix}/{storage_path}'

    def exists(self, storage_path):
        return os.path.exists(os.path.join(self.base_dir, storage_path))


class S3Storage(StorageBackend):
    """Store files in AWS S3."""

    def __init__(self, bucket: str, region: str = 'us-east-1',
                 access_key: str = '', secret_key: str = '',
                 cdn_domain: str = ''):
        import boto3
        self.bucket = bucket
        self.cdn_domain = cdn_domain  # Optional CloudFront domain
        self.s3 = boto3.client('s3',
            region_name=region,
            aws_access_key_id=access_key or None,
            aws_secret_access_key=secret_key or None,
        )

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=storage_path,
            Body=file_bytes,
            ContentType=content_type,
            CacheControl='public, max-age=31536000',  # 1 year cache
        )
        return self.get_url(storage_path)

    def delete(self, storage_path):
        self.s3.delete_object(Bucket=self.bucket, Key=storage_path)
        return True

    def get_url(self, storage_path):
        if self.cdn_domain:
            return f'https://{self.cdn_domain}/{storage_path}'
        return f'https://{self.bucket}.s3.amazonaws.com/{storage_path}'

    def exists(self, storage_path):
        try:
            self.s3.head_object(Bucket=self.bucket, Key=storage_path)
            return True
        except self.s3.exceptions.ClientError:
            return False


class GCSStorage(StorageBackend):
    """Store files in Google Cloud Storage."""

    def __init__(self, bucket: str, credentials_path: str = '', cdn_domain: str = ''):
        from google.cloud import storage as gcs
        if credentials_path:
            self.client = gcs.Client.from_service_account_json(credentials_path)
        else:
            self.client = gcs.Client()  # Uses GOOGLE_APPLICATION_CREDENTIALS env var
        self.bucket_obj = self.client.bucket(bucket)
        self.bucket = bucket
        self.cdn_domain = cdn_domain

    def save(self, file_bytes, storage_path, content_type='image/webp'):
        blob = self.bucket_obj.blob(storage_path)
        blob.upload_from_string(file_bytes, content_type=content_type)
        blob.cache_control = 'public, max-age=31536000'
        blob.patch()
        return self.get_url(storage_path)

    def delete(self, storage_path):
        blob = self.bucket_obj.blob(storage_path)
        blob.delete()
        return True

    def get_url(self, storage_path):
        if self.cdn_domain:
            return f'https://{self.cdn_domain}/{storage_path}'
        return f'https://storage.googleapis.com/{self.bucket}/{storage_path}'

    def exists(self, storage_path):
        return self.bucket_obj.blob(storage_path).exists()


def create_storage(app_config) -> StorageBackend:
    """Factory function — creates the right backend from config."""
    backend = app_config.get('STORAGE_BACKEND', 'local')

    if backend == 's3':
        return S3Storage(
            bucket=app_config['S3_BUCKET'],
            region=app_config.get('S3_REGION', 'us-east-1'),
            access_key=app_config.get('S3_ACCESS_KEY', ''),
            secret_key=app_config.get('S3_SECRET_KEY', ''),
            cdn_domain=app_config.get('S3_CDN_DOMAIN', ''),
        )
    elif backend == 'gcs':
        return GCSStorage(
            bucket=app_config['GCS_BUCKET'],
            credentials_path=app_config.get('GCS_CREDENTIALS_PATH', ''),
            cdn_domain=app_config.get('GCS_CDN_DOMAIN', ''),
        )
    else:
        return LocalStorage(
            base_dir=app_config.get('UPLOAD_FOLDER', 'instance/uploads'),
            url_prefix='/uploads',
        )
```

### File: [extensions.py](ssr_python/extensions.py)

Add a module-level `storage` variable (same pattern as `db`, `TOKENS`, etc.):

```python
storage = None  # Set by app.py after create_storage()
```

### File: [app.py](ssr_python/app.py)

Initialize storage in `create_app()`:

```python
from storage import create_storage
import extensions

# Inside create_app(), after db.init_app(app):
extensions.storage = create_storage(app.config)
```

### File: [config.py](ssr_python/config.py)

Add storage config to base `Config` and environment-specific overrides:

```python
class Config:
    # ... existing ...
    STORAGE_BACKEND = 'local'  # 'local' | 's3' | 'gcs'

    # S3 settings (only used when STORAGE_BACKEND='s3')
    S3_BUCKET = os.environ.get('S3_BUCKET', '')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', '')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', '')
    S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN', '')  # CloudFront

    # GCS settings (only used when STORAGE_BACKEND='gcs')
    GCS_BUCKET = os.environ.get('GCS_BUCKET', '')
    GCS_CREDENTIALS_PATH = os.environ.get('GCS_CREDENTIALS_PATH', '')
    GCS_CDN_DOMAIN = os.environ.get('GCS_CDN_DOMAIN', '')

class DevelopmentConfig(Config):
    STORAGE_BACKEND = 'local'

class ProductionConfig(Config):
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
```

### Multi-Tenant Image Isolation

**Storage path format:** `{org_id}/{site_id}/{uuid}.webp`

Example paths:
```
default/abc-site-123/a1b2c3d4e5f6.webp     # Site-specific image
default/_shared/f7e8d9c0b1a2.webp            # Org-level shared image (site_id=None)
```

**Isolation enforced at 3 layers:**

| Layer | How |
|-------|-----|
| **Storage path** | Images physically stored under `{org_id}/{site_id}/` prefix — can't access without knowing the path |
| **Database query** | All image queries filtered by `site_id` via `get_site_or_404()` IDOR guard (already exists) |
| **Serving route** | `/uploads/<path:storage_path>` validates the requesting user's org owns the site |

### File: [models.py](ssr_python/models.py)

Add two new columns to `SiteImage` (migration in `app.py`):

```python
class SiteImage(db.Model):
    # ... existing columns (id, site_id, filename, width, height, etc.) ...
    storage_path = db.Column(db.String(500), nullable=True)   # "org_id/site_id/uuid.webp"
    orientation = db.Column(db.String(20), nullable=True)      # "landscape" | "portrait" | "square"
```

**Orientation is auto-computed from dimensions:**
```python
def compute_orientation(width, height):
    """Determine image orientation from dimensions."""
    if width is None or height is None:
        return None
    ratio = width / height
    if ratio > 1.2:
        return 'landscape'
    elif ratio < 0.8:
        return 'portrait'
    else:
        return 'square'
```

This is called during upload/download and stored in the DB. It enables:
- **LLM context**: Tell the LLM "Image X is landscape" so it places it in a hero banner vs. sidebar
- **Image panel filtering**: Filter selected images by orientation
- **Smart assignment**: Planner agent can match landscape images to hero sections, portrait to sidebars, square to cards

Migration in `app.py._run_migrations()`:
```python
# Add storage_path and orientation columns if missing
for col, col_type in [('storage_path', 'VARCHAR(500)'), ('orientation', 'VARCHAR(20)')]:
    try:
        db.session.execute(text(f"SELECT {col} FROM site_images LIMIT 1"))
    except:
        db.session.rollback()
        db.session.execute(text(f"ALTER TABLE site_images ADD COLUMN {col} {col_type}"))
        db.session.commit()
```

### File: [uploads.py](ssr_python/routes/uploads.py) — Refactor existing upload + serve

**Refactor `upload_image()`** to use storage backend:
```python
from extensions import storage

# In upload_image():
# OLD: filepath = os.path.join(upload_folder, filename)
# NEW:
org_id = g.current_org_id  # from guards
site_id = request.form.get('site_id') or '_shared'
storage_path = storage.generate_path(org_id, site_id, filename)
url = storage.save(webp_bytes, storage_path)
# Store storage_path in SiteImage record
```

**Refactor `serve_upload()`** to support tenant-scoped paths:
```python
@uploads_bp.route('/uploads/<path:storage_path>')
def serve_upload(storage_path):
    """Serve stored image — local backend only. S3/GCS use direct URLs."""
    # Validate path components (org_id/site_id/filename.webp)
    parts = storage_path.split('/')
    if len(parts) != 3:
        abort(404)
    org_id, site_id, filename = parts
    if not SAFE_FILENAME_RE.match(filename):
        abort(404)
    # For local storage, serve from filesystem
    full_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], org_id, site_id)
    return send_from_directory(full_dir, filename)
```

> **Note:** For S3/GCS backends, images are served directly from CDN/bucket URLs — the Flask serve route is only used for local storage. The `SiteImage.url` stored in YAML will point directly to the cloud URL.

### Dependencies (add to requirements.txt)

```
# Only install the one you need:
boto3>=1.34.0       # For S3 backend
google-cloud-storage>=2.14.0  # For GCS backend
```

These are **optional** — only needed if `STORAGE_BACKEND` is set to `s3` or `gcs`. Local storage uses no extra dependencies.

---

## Phase 1: Backend Download Endpoints

### File: [uploads.py](ssr_python/routes/uploads.py)

Add a shared helper function and three new endpoints, reusing the existing `convert_to_webp()` function (line 28) and the new storage backend from Phase 0.

#### 1a. Shared Helper: `_download_and_store(url, site_id, alt_text, photographer, source)`

Core logic extracted into a reusable function (called by all three endpoints):

```python
import requests as http_requests
from urllib.parse import urlparse

ALLOWED_DOWNLOAD_DOMAINS = ['images.pexels.com', 'pixabay.com', 'cdn.pixabay.com', 'images.unsplash.com']
MAX_DOWNLOAD_SIZE = 15 * 1024 * 1024  # 15MB

def _download_and_store(url, site_id=None, alt_text='', photographer='', source='stock'):
    """Download an external image, convert to WebP, store locally.

    Returns dict with {id, filename, url, width, height, file_size} on success.
    Raises ValueError with user-safe message on failure.
    """
    # 1. Validate URL domain
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        raise ValueError('Only HTTPS URLs are allowed.')
    if parsed.hostname not in ALLOWED_DOWNLOAD_DOMAINS:
        raise ValueError(f'Domain "{parsed.hostname}" is not in the allowed list.')

    # 2. Deduplication check — skip if already downloaded
    existing = SiteImage.query.filter_by(source_url=url).first()
    if existing:
        return {
            'id': existing.id,
            'filename': existing.filename,
            'url': f'/uploads/{existing.filename}',
            'width': existing.width,
            'height': existing.height,
            'file_size': existing.file_size,
            'already_existed': True,
        }

    # 3. Stream download with size limit
    resp = http_requests.get(url, timeout=15, stream=True)
    resp.raise_for_status()

    # Check Content-Length header first (fast reject)
    content_length = resp.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
        raise ValueError(f'Image too large ({int(content_length) // 1024 // 1024}MB). Max is 15MB.')

    # Check Content-Type header
    content_type = resp.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        raise ValueError(f'URL did not return an image (got {content_type}).')

    # Stream download with running size check
    chunks = []
    downloaded = 0
    for chunk in resp.iter_content(chunk_size=8192):
        downloaded += len(chunk)
        if downloaded > MAX_DOWNLOAD_SIZE:
            raise ValueError('Image exceeded 15MB size limit during download.')
        chunks.append(chunk)
    image_bytes = b''.join(chunks)

    # 4. Convert to WebP (reuse existing function at line 28)
    webp_bytes, width, height = convert_to_webp(image_bytes)

    # 5. Store via storage backend (tenant-isolated path)
    from extensions import storage
    from flask import g
    file_id = uuid.uuid4().hex
    filename = f'{file_id}.webp'
    org_id = getattr(g, 'current_org_id', 'default')
    storage_site_id = site_id or '_shared'
    storage_path = storage.generate_path(org_id, storage_site_id, filename)
    url = storage.save(webp_bytes, storage_path)

    # 6. Compute orientation from dimensions
    orientation = compute_orientation(width, height)

    # 7. Create DB record
    image = SiteImage(
        site_id=site_id,
        filename=filename,
        storage_path=storage_path,
        original_name=os.path.basename(parsed.path) or 'downloaded.jpg',
        mime_type='image/webp',
        file_size=len(webp_bytes),
        width=width,
        height=height,
        orientation=orientation,   # 'landscape' | 'portrait' | 'square'
        source=source,             # 'pexels' | 'pixabay'
        source_url=url_param,      # original CDN URL for dedup + attribution
        photographer=photographer,
        alt_text=alt_text,
    )
    db.session.add(image)
    db.session.commit()

    return {
        'id': image.id,
        'filename': filename,
        'url': url,                # local path or cloud URL depending on backend
        'width': width,
        'height': height,
        'orientation': orientation,
        'file_size': len(webp_bytes),
        'already_existed': False,
    }
```

**Key design choices:**
- **Deduplication by `source_url`**: If the same Pexels/Pixabay URL is downloaded twice, returns the existing record instead of re-downloading. Prevents storage bloat.
- **Streaming download**: Uses `iter_content()` with 8KB chunks — never loads full image into memory until all chunks are collected. Running size check aborts early if limit exceeded.
- **Content-Type validation**: Rejects non-image responses before downloading the full body.
- **`already_existed` flag**: Lets the frontend know whether this was a fresh download or a cache hit.

#### 1b. Endpoint: `POST /api/images/download`

Single image download. Thin wrapper around `_download_and_store()`.

```python
@uploads_bp.route('/api/images/download', methods=['POST'])
def download_image():
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
```

#### 1c. Endpoint: `POST /api/images/download-batch`

Multiple images. Loops through and reports per-image results.

```python
@uploads_bp.route('/api/images/download-batch', methods=['POST'])
def download_batch():
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
                'error': None,
            })
            downloaded += 1
        except Exception as e:
            results.append({'original_url': url, 'error': str(e), 'local_url': None, 'id': None})
            failed += 1

    return jsonify({'results': results, 'downloaded': downloaded, 'failed': failed})
```

**Key design choices:**
- **Max 20 images per batch**: Prevents abuse. Typical page has 5-15 images.
- **Partial failures**: Each image reports success/error independently. Frontend can retry failed ones.
- **No threading for MVP**: Sequential download is simpler and ~20 images × 2s = 40s worst case. Can add `ThreadPoolExecutor(max_workers=3)` later if needed.

### File: [config.py](ssr_python/config.py)

Add to both `DevelopmentConfig` and `ProductionConfig`:
```python
ALLOWED_DOWNLOAD_DOMAINS = ['images.pexels.com', 'pixabay.com', 'cdn.pixabay.com', 'images.unsplash.com']
MAX_DOWNLOAD_SIZE = 15 * 1024 * 1024  # 15MB
```

### No model changes needed
Existing `SiteImage` model already has: `site_id`, `source`, `source_url`, `photographer`, `alt_text`, `width`, `height`.

### Error Handling Summary

| Error Case | Response Code | Message |
|------------|---------------|---------|
| Empty/missing URL | 400 | "No URL provided." |
| Non-HTTPS URL | 400 | "Only HTTPS URLs are allowed." |
| Domain not in allowlist | 400 | "Domain X is not in the allowed list." |
| Content-Length > 15MB | 400 | "Image too large. Max is 15MB." |
| Non-image Content-Type | 400 | "URL did not return an image." |
| Size exceeded during stream | 400 | "Image exceeded 15MB size limit." |
| Download timeout (15s) | 504 | "Download timed out." |
| Upstream HTTP error | 502 | "Failed to download image (HTTP N)." |
| WebP conversion failure | 400 | "Failed to process image." (from `convert_to_webp`) |
| Unexpected error | 500 | "Failed to download image." (logged server-side) |
| Batch > 20 images | 400 | "Maximum 20 images per batch." |
| Duplicate URL (dedup hit) | 200 | Returns existing record with `already_existed: true` |

---

## Phase 2: Frontend — Download Selected Images

### File: [imagesPanel.js](ssr_python/static/js/imagesPanel.js)

1. **Add "Download to Site" button** in the selected images section header
   - Calls `POST /api/images/download-batch` with all selected images that aren't already local
   - Shows progress: "Downloading 2/5..."
   - On success, updates each selected image entry: replaces `url` with `/uploads/xxx.webp`, sets `downloaded: true`
   - Saves updated state to localStorage

2. **Auto-download on select** (toggle option)
   - When user clicks "+" on a stock photo, immediately trigger background download
   - Show spinner on thumbnail until complete
   - Replace URL with local path when done

3. **Export `getSelectedImages()` function** for use by chat module:
   ```javascript
   export function getSelectedImages() { return [...selectedImages]; }
   ```

4. **Visual indicators**
   - Downloaded images show a green checkmark badge
   - Non-downloaded images show cloud icon

### File: [images-panel.css](ssr_python/static/css/images-panel.css)
- Styles for download button, progress bar, downloaded/pending badges

---

## Phase 3: LLM Integration — Pre-Creation Image Context

### File: [chat.js](ssr_python/static/js/chat.js)
- Import `getSelectedImages()` from imagesPanel
- Before sending chat message, get downloaded images (those with `/uploads/` URLs)
- Pass to chatService as `selectedImages` array
- Also query `/api/sites/<site_id>/media` to get all site images from the Media Library (not just panel selection)

### File: [chatService.js](ssr_python/static/js/chatService.js)
- Add `selectedImages` to POST body in `sendMessage()`

### File: [chat.py](ssr_python/routes/chat.py)
- Extract `selected_images` from request JSON
- Pass to `llm_service.chat()`

### File: [llm_service.py](ssr_python/llm_service.py)
- Accept `selected_images` parameter in `chat()` and `_build_prompt()`
- **When images are available**, add to user prompt:
  ```
  [AVAILABLE IMAGES - You MUST use these URLs in image components]
  1. /uploads/org/site/abc123.webp — "Mountain landscape" [landscape] (Photo by John Doe)
  2. /uploads/org/site/def456.webp — "Modern office interior" [landscape] (Photo by Jane Smith)
  3. /uploads/org/site/ghi789.webp — "Professional headshot" [portrait] (Photo by Alex Kim)
  Match images to sections by their descriptions and orientation:
  - Use [landscape] images for hero banners, full-width sections, backgrounds
  - Use [portrait] images for sidebars, team cards, testimonial avatars
  - Use [square] images for product cards, grid items, logos
  Do NOT use any external URLs. Only use the images listed above.
  ```
- **When NO images are available** and user requests image-related content (create page, add image, add hero):
  - Add to system prompt: "If the user asks to create a page or add image components but no images are provided in the [AVAILABLE IMAGES] section, respond with action 'explain' and ask the user to select or upload images in the Images panel or Media Library first. Do not use external/placeholder image URLs."

### File: [rag_agent.py](ssr_python/rag/agent/rag_agent.py)
- Pass `selected_images` through to planner and builder agents

### File: [planner_agent.py](ssr_python/rag/agent/planner_agent.py)
- Include available images in planner prompt
- Planner assigns image URLs to sections in its JSON outline

### File: [builder_agent.py](ssr_python/rag/agent/builder_agent.py)
- Accept assigned images per section
- Include in builder prompt so generated YAML uses local URLs

---

---

## Phase 4: Media Library UI (Dashboard + Designer)

A dedicated Media Library for browsing, organizing, and managing all images/videos per site. Available in two places:
1. **Dashboard** — full-page media management view for the site
2. **Designer** — sidebar panel for quick access while editing

### 4a. Data Model: Collections (Folders)

Add a new model to group images into user-defined collections (e.g. "Product Photos", "Hero Banners", "Team"):

### File: [models.py](ssr_python/models.py)

```python
class ImageCollection(db.Model):
    __tablename__ = 'image_collections'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)       # "Product Photos"
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('SiteImage', backref='collection', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('site_id', 'name', name='uq_site_collection_name'),
    )
```

Add `collection_id` FK to `SiteImage`:
```python
class SiteImage(db.Model):
    # ... existing columns ...
    collection_id = db.Column(db.String(36), db.ForeignKey('image_collections.id'), nullable=True, index=True)
```

Images without a collection appear in "Uncategorized". Collections cascade-delete with the site.

### 4b. Backend API: Media Library Endpoints

### File: NEW [routes/media.py](ssr_python/routes/media.py)

New blueprint `media_bp` for media library CRUD:

**Collection Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sites/<site_id>/media/collections` | GET | List all collections for site (with image counts) |
| `/api/sites/<site_id>/media/collections` | POST | Create new collection `{ "name": "Product Photos" }` |
| `/api/sites/<site_id>/media/collections/<id>` | PATCH | Rename collection |
| `/api/sites/<site_id>/media/collections/<id>` | DELETE | Delete collection (images move to uncategorized) |

**Image Management Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sites/<site_id>/media` | GET | List all images for site, filterable by `?collection=`, `?orientation=`, `?q=` search |
| `/api/sites/<site_id>/media/<image_id>` | PATCH | Update image metadata (alt_text, collection_id, rename) |
| `/api/sites/<site_id>/media/<image_id>` | DELETE | Delete image (remove from storage + DB) |
| `/api/sites/<site_id>/media/bulk` | POST | Bulk operations `{ "action": "move"|"delete", "image_ids": [...], "collection_id": "..." }` |

**Response format for image list:**
```json
{
  "images": [
    {
      "id": "uuid",
      "url": "/uploads/org/site/abc.webp",
      "alt_text": "Mountain landscape",
      "orientation": "landscape",
      "width": 1200, "height": 800,
      "file_size": 245000,
      "photographer": "John Doe",
      "source": "pexels",
      "collection_id": "uuid-or-null",
      "collection_name": "Hero Images",
      "created_at": "2026-03-12T..."
    }
  ],
  "collections": [
    { "id": "uuid", "name": "Hero Images", "count": 5 },
    { "id": "uuid", "name": "Products", "count": 12 }
  ],
  "total": 17
}
```

### 4c. Dashboard: Media View

### File: [dashboard.html](ssr_python/templates/dashboard.html) + [dashboard.js](ssr_python/static/js/dashboard.js)

Add a third sidebar nav button `[data-view="media"]` alongside "Sites" and "Submissions":

```
.dashboard-sidebar-nav
├── Sites button (existing)
├── Submissions button (existing)
└── Media button (NEW) ← icon: image/photo
```

**Media View Layout (when a site is selected):**

```
.media-view
├── .media-header
│   ├── Site selector dropdown (switch between sites)
│   ├── Search bar (search by alt_text, filename, photographer)
│   ├── Orientation filter pills (All | Landscape | Portrait | Square)
│   └── View toggle (Grid | List)
├── .media-body (flex row)
│   ├── .media-sidebar (200px, left)
│   │   ├── "All Images" (count)
│   │   ├── "Uncategorized" (count)
│   │   ├── Collection list (sortable)
│   │   │   ├── "Hero Images" (5)
│   │   │   ├── "Products" (12)
│   │   │   └── "Team" (3)
│   │   └── "+ New Collection" button
│   └── .media-grid (flex: 1, right)
│       ├── Grid of image cards (responsive: 4-6 columns)
│       │   └── Each card:
│       │       ├── Thumbnail (aspect-ratio preserved)
│       │       ├── Checkbox overlay (for multi-select)
│       │       ├── Orientation badge (landscape/portrait/square icon)
│       │       ├── File size label
│       │       └── Hover: alt text + photographer credit
│       └── Empty state: "No images yet. Upload or search stock photos."
└── .media-footer (sticky bottom, shown when images selected)
    ├── "N selected" label
    ├── Move to Collection dropdown
    ├── Delete button
    └── Copy URL button
```

**Key interactions:**
- **Upload**: Drag-and-drop zone on the grid area + "Upload" button in header
- **Multi-select**: Shift+click for range, Ctrl+click for toggle, checkbox overlay
- **Drag to collection**: Drag image cards to collection sidebar items
- **Right-click context menu**: Copy URL, Edit alt text, Move to collection, Delete
- **Image detail modal**: Click image → modal with full preview, editable alt_text, metadata, URL copy, and "Use in Page" button

### 4d. Designer: Enhanced Images Panel (Sidebar)

### File: [imagesPanel.js](ssr_python/static/js/imagesPanel.js) + [index.html](ssr_python/templates/index.html)

Refactor the existing Images Panel into **two tabs** within the same sidebar panel:

```
.images-panel
├── .panel-tab-bar
│   ├── [Search] tab — Stock photo search (existing functionality)
│   └── [Library] tab — Site's media library (NEW)
└── .panel-content
    ├── [Search tab content] — existing search + filters + results
    └── [Library tab content] — NEW
        ├── Collection filter dropdown (All | Hero Images | Products | ...)
        ├── Orientation filter pills
        ├── Image grid (from /api/sites/<id>/media)
        ├── Each image card:
        │   ├── Thumbnail
        │   ├── Orientation badge
        │   └── Click → copies URL to clipboard (existing behavior)
        │   └── Click + alt → inserts image component at selection point
        └── Upload button at bottom
```

**Key difference from Dashboard Media View:**
- Designer panel is compact (350px sidebar width) — single column or 2-column grid
- Focused on quick access: click to copy URL, drag to insert into YAML
- No multi-select, no bulk operations — those are in the Dashboard
- Shows same data from same API, just a lighter UI

### 4e. Connecting Media Library to Image Components

When user clicks an image in the Library tab (designer sidebar):
1. If a component is selected AND it's an image component → auto-fill `source.url` with the image URL and `source.altText` with the alt_text
2. If no selection or non-image component → copy URL to clipboard with toast notification
3. Optional "Insert Image" action → creates a new image component at the current selection point with the library image's URL and alt text pre-filled

### 4f. Files for Phase 5

| File | Action |
|------|--------|
| [models.py](ssr_python/models.py) | Add `ImageCollection` model, add `collection_id` FK to `SiteImage` |
| **NEW** [routes/media.py](ssr_python/routes/media.py) | Media library CRUD endpoints (collections + images) |
| [routes/__init__.py](ssr_python/routes/__init__.py) | Register `media_bp` blueprint |
| [dashboard.html](ssr_python/templates/dashboard.html) | Add "Media" nav button |
| [dashboard.js](ssr_python/static/js/dashboard.js) | Add `renderMediaView()`, collection management, image grid |
| [dashboard.css](ssr_python/static/css/dashboard.css) | Media view grid, sidebar, bulk action bar styles |
| [imagesPanel.js](ssr_python/static/js/imagesPanel.js) | Add "Library" tab, render site images from API |
| [images-panel.css](ssr_python/static/css/images-panel.css) | Tab bar styles, library grid styles |
| [index.html](ssr_python/templates/index.html) | Tab bar HTML in images panel |
| [app.py](ssr_python/app.py) | Migration for `image_collections` table + `collection_id` column |

---

## Phase 5: Content Moderation — NSFW Image Detection

Automatically detect and flag obscene/inappropriate images during upload and download to prevent harmful content from being used in published sites.

### Architecture: Tiered Detection

```
Image Upload/Download
  ↓
Tier 1: On-device classifier (fast, free, no API calls)
  ↓ flagged?
  → Block upload + return error to user
  → OR mark as flagged in DB for admin review
```

**Recommended library:** [`opennsfw2`](https://pypi.org/project/opennsfw2/) — Keras implementation of Yahoo's Open NSFW model
- Lightweight (~25MB model)
- No external API calls needed (runs locally)
- Returns a score 0.0 (safe) → 1.0 (explicit)
- Threshold: **0.8** = block, **0.4-0.8** = flag for review, **<0.4** = safe
- Works with PIL Image objects (already used in `convert_to_webp()`)

**Alternative:** [`Falconsai/nsfw_image_detection`](https://huggingface.co/Falconsai/nsfw_image_detection) on Hugging Face — ViT-based, more accurate but heavier (~350MB)

### File: [models.py](ssr_python/models.py)

Add moderation columns to `SiteImage`:

```python
class SiteImage(db.Model):
    # ... existing columns ...
    nsfw_score = db.Column(db.Float, nullable=True)         # 0.0 to 1.0
    moderation_status = db.Column(db.String(20), nullable=True)  # 'safe' | 'flagged' | 'blocked'
```

### File: NEW [moderation.py](ssr_python/moderation.py)

```python
import io
from PIL import Image

# Lazy-load model (only imported when first image is checked)
_model = None

def _get_model():
    global _model
    if _model is None:
        import opennsfw2 as n2
        _model = n2
    return _model

def check_image(image_bytes: bytes) -> dict:
    """Run NSFW detection on image bytes.

    Returns: { 'score': float, 'status': 'safe'|'flagged'|'blocked' }
    """
    n2 = _get_model()
    img = Image.open(io.BytesIO(image_bytes))

    # opennsfw2 expects PIL Image, returns NSFW probability
    score = n2.predict_image(img)

    if score >= 0.8:
        status = 'blocked'
    elif score >= 0.4:
        status = 'flagged'
    else:
        status = 'safe'

    return {'score': round(score, 4), 'status': status}
```

### Integration Points

**1. Upload endpoint** ([uploads.py](ssr_python/routes/uploads.py) `upload_image()`):
```python
from moderation import check_image

# After reading file_bytes, before convert_to_webp:
moderation = check_image(file_bytes)
if moderation['status'] == 'blocked':
    return jsonify({'error': 'This image was flagged as inappropriate and cannot be uploaded.'}), 400

# Store moderation data in SiteImage record:
image.nsfw_score = moderation['score']
image.moderation_status = moderation['status']
```

**2. Download endpoint** ([uploads.py](ssr_python/routes/uploads.py) `_download_and_store()`):
```python
# After downloading image_bytes, before convert_to_webp:
moderation = check_image(image_bytes)
if moderation['status'] == 'blocked':
    raise ValueError('This image was flagged as inappropriate and cannot be used.')
# Store in SiteImage record
```

**3. Media Library API** ([routes/media.py](ssr_python/routes/media.py)):
- Include `nsfw_score` and `moderation_status` in image list responses
- Add filter `?moderation=flagged` to list only flagged images for admin review
- Admin can override: PATCH to change `moderation_status` to `safe` or `blocked`

### Configuration

### File: [config.py](ssr_python/config.py)
```python
class Config:
    NSFW_DETECTION_ENABLED = True       # Toggle on/off
    NSFW_BLOCK_THRESHOLD = 0.8          # Score >= this → blocked
    NSFW_FLAG_THRESHOLD = 0.4           # Score >= this → flagged for review
```

### File: .env
```
NSFW_DETECTION_ENABLED=true    # Set to false to skip (e.g. dev environment)
```

### Dependencies (add to requirements.txt)
```
opennsfw2>=0.3.0    # NSFW image detection (Yahoo Open NSFW model)
```

### UX Behavior

| Scenario | Behavior |
|----------|----------|
| Score < 0.4 (safe) | Upload proceeds normally |
| Score 0.4-0.8 (flagged) | Upload succeeds but image shows warning badge in Media Library. Admin can review. |
| Score >= 0.8 (blocked) | Upload rejected with error message: "This image was flagged as inappropriate." |
| Detection disabled | All uploads proceed, no scoring |
| Model not installed | Graceful fallback — log warning, allow upload with `moderation_status=None` |

### Files for Phase 5

| File | Action |
|------|--------|
| **NEW** [moderation.py](ssr_python/moderation.py) | NSFW detection with lazy model loading |
| [models.py](ssr_python/models.py) | Add `nsfw_score`, `moderation_status` to `SiteImage` |
| [uploads.py](ssr_python/routes/uploads.py) | Call `check_image()` in upload + download flows |
| [config.py](ssr_python/config.py) | Add `NSFW_DETECTION_ENABLED`, threshold configs |
| [routes/media.py](ssr_python/routes/media.py) | Add moderation filter + admin override endpoint |
| [app.py](ssr_python/app.py) | Migration for new columns |
| [requirements.txt](ssr_python/requirements.txt) | Add `opennsfw2` |

---

## Phase 6 (Future): Auto-Search During Generation

This is a future enhancement — not part of initial implementation:
- During page creation, auto-search stock APIs based on planner's section descriptions
- Download top results automatically
- Embed local URLs in generated YAML without user intervention
- Requires refactoring search functions into importable module (`image_search.py`)

---

## Files to Modify (Summary)

| File | Phase | Changes |
|------|-------|---------|
| **NEW** [storage.py](ssr_python/storage.py) | 0 | Abstract `StorageBackend` + `LocalStorage`, `S3Storage`, `GCSStorage` implementations |
| [models.py](ssr_python/models.py) | 0 | Add `storage_path` and `orientation` columns to `SiteImage` |
| [extensions.py](ssr_python/extensions.py) | 0 | Add `storage = None` module-level variable |
| [app.py](ssr_python/app.py) | 0 | Initialize storage backend, add DB migrations for new columns |
| [config.py](ssr_python/config.py) | 0,1 | Add `STORAGE_BACKEND`, S3/GCS config, `ALLOWED_DOWNLOAD_DOMAINS`, `MAX_DOWNLOAD_SIZE` |
| [uploads.py](ssr_python/routes/uploads.py) | 0,1 | Refactor to use storage backend; add `/download`, `/download-batch` endpoints |
| [imagesPanel.js](ssr_python/static/js/imagesPanel.js) | 2 | Download button, auto-download, export `getSelectedImages()` |
| [images-panel.css](ssr_python/static/css/images-panel.css) | 2 | Download button, progress, badge styles |
| [chat.js](ssr_python/static/js/chat.js) | 3 | Pass selected + library images with orientation to LLM |
| [chatService.js](ssr_python/static/js/chatService.js) | 3 | Add `selectedImages` to POST body |
| [chat.py](ssr_python/routes/chat.py) | 3 | Pass `selected_images` to LLM service |
| [llm_service.py](ssr_python/llm_service.py) | 3 | Accept & inject image context with orientation into prompts |
| [rag_agent.py](ssr_python/rag/agent/rag_agent.py) | 3 | Pass images through pipeline |
| [planner_agent.py](ssr_python/rag/agent/planner_agent.py) | 3 | Assign images to sections using orientation matching |
| [builder_agent.py](ssr_python/rag/agent/builder_agent.py) | 3 | Use assigned image URLs |
| [requirements.txt](ssr_python/requirements.txt) | 0 | Add optional `boto3`, `google-cloud-storage` |
| **NEW** [routes/media.py](ssr_python/routes/media.py) | 4 | Media library CRUD (collections + image management) |
| [routes/__init__.py](ssr_python/routes/__init__.py) | 4 | Register `media_bp` blueprint |
| [dashboard.html](ssr_python/templates/dashboard.html) | 4 | Add "Media" nav button + media view HTML |
| [dashboard.js](ssr_python/static/js/dashboard.js) | 4 | `renderMediaView()`, collection management, image grid |
| [dashboard.css](ssr_python/static/css/dashboard.css) | 4 | Media view grid, sidebar, bulk action bar styles |
| [index.html](ssr_python/templates/index.html) | 4 | Tab bar HTML in images panel |
| **NEW** [moderation.py](ssr_python/moderation.py) | 5 | NSFW detection with lazy model loading |

---

## Verification

1. **Phase 0 (Storage)**: Switch `STORAGE_BACKEND` between `local`/`s3`/`gcs` → upload an image → verify it's stored in the right location with tenant-isolated path `org_id/site_id/uuid.webp`
2. **Phase 1 (Download)**: `curl -X POST /api/images/download -d '{"url":"https://images.pexels.com/..."}' ` → returns local URL with orientation, file exists in storage
3. **Phase 1 (Dedup)**: Download same URL twice → second call returns `already_existed: true`, no new file created
4. **Phase 2 (Frontend)**: Select stock photos in Images Panel → click "Download to Site" → URLs change to `/uploads/` paths → images render in preview
5. **Phase 3 (LLM with images)**: Select & download images → ask LLM "create a bakery website" → generated YAML uses `/uploads/` URLs with correct orientation matching (landscape→hero, portrait→sidebar)
6. **Phase 3 (LLM without images)**: Ask LLM "create a website" with no images selected → LLM responds: "Please select or upload images first"
7. **Phase 4 (Dashboard Media)**: Go to Dashboard → Media tab → see all site images → create collection "Products" → drag images into it → filter by orientation → bulk delete
8. **Phase 4 (Designer Library)**: In designer → Images Panel → Library tab → see site images by collection → click image → URL auto-fills into selected image component
9. **Phase 5 (Moderation block)**: Upload an explicit image → rejected with "flagged as inappropriate" error, not stored
10. **Phase 5 (Moderation flag)**: Upload a borderline image (score 0.4-0.8) → upload succeeds but shows warning badge in Media Library
11. **Phase 5 (Moderation disabled)**: Set `NSFW_DETECTION_ENABLED=false` → all uploads proceed without scoring
12. **End-to-end**: Publish site → published pages serve images from storage (no external dependencies, no blocked content)
