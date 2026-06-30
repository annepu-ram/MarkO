from flask import Blueprint, request, jsonify, current_app
import os
import random
import math
import requests as http_requests

images_bp = Blueprint('images', __name__)

# Color mapping from our UI values to each API's accepted values
PEXELS_COLOR_MAP = {
    'red': 'red', 'orange': 'orange', 'yellow': 'yellow', 'green': 'green',
    'blue': 'blue', 'purple': 'violet', 'black': 'black', 'white': 'white',
}
PIXABAY_COLOR_MAP = {
    'red': 'red', 'orange': 'orange', 'yellow': 'yellow', 'green': 'green',
    'blue': 'blue', 'purple': 'lilac', 'black': 'black', 'white': 'white',
}
TAG_STOP_WORDS = {'and', 'the', 'for', 'with', 'from', 'image', 'photo', 'picture'}
STOCK_PROVIDERS = {'', 'pexels', 'pixabay'}
VISUAL_TYPE_TERMS = {
    'lifestyle_photo': 'lifestyle photography real people natural light',
    'product_photo': 'product photography ecommerce clean background',
    'vector': 'vector graphic clean scalable design',
    'illustration': 'digital illustration artwork',
    'studio_shot': 'studio photography clean lighting',
    'flat_lay': 'flat lay top view product photography',
    'render_3d': '3d render product visualization',
    'editorial': 'editorial magazine photography',
}
PIXABAY_IMAGE_TYPE_BY_VISUAL_TYPE = {
    'vector': 'vector',
    'illustration': 'illustration',
}
PIXABAY_ORIENTATION_MAP = {
    'landscape': 'horizontal',
    'portrait': 'vertical',
}


def _tags_from_text(*values):
    text = ' '.join(str(value or '') for value in values)
    tags = []
    for token in text.replace(',', ' ').replace('-', ' ').replace('_', ' ').split():
        tag = ''.join(ch for ch in token.lower() if ch.isalnum())
        if len(tag) >= 3 and tag not in TAG_STOP_WORDS:
            tags.append(tag[:60])
    return list(dict.fromkeys(tags[:30]))


def _compose_search_query(query, visual_type):
    base = str(query or '').strip()
    visual_terms = VISUAL_TYPE_TERMS.get(str(visual_type or '').strip(), '')
    if base and visual_terms:
        return f'{base} {visual_terms}'
    return base or visual_terms or 'wallpaper'


def _normalize_provider(provider):
    provider = str(provider or '').strip().lower()
    return provider if provider in STOCK_PROVIDERS else ''


def _is_squareish(width, height):
    try:
        width = int(width or 0)
        height = int(height or 0)
    except (TypeError, ValueError):
        return False
    if width <= 0 or height <= 0:
        return False
    return abs(width - height) / max(width, height) <= 0.08


def _filter_square_results(results, orientation):
    if orientation != 'square':
        return results
    return [item for item in results if _is_squareish(item.get('width'), item.get('height'))]


def _build_provider_plan(provider, visual_type, pexels_key, pixabay_key):
    if visual_type in PIXABAY_IMAGE_TYPE_BY_VISUAL_TYPE:
        if provider == 'pexels':
            return [], 'Pexels does not support vector or illustration searches. Choose Pixabay or Any source.'
        if not pixabay_key:
            return [], 'Pixabay is required for vector and illustration searches.'
        return [_search_pixabay], ''

    if provider == 'pexels':
        return ([_search_pexels], '') if pexels_key else ([], 'Pexels search is not configured.')
    if provider == 'pixabay':
        return ([_search_pixabay], '') if pixabay_key else ([], 'Pixabay search is not configured.')

    providers = []
    if pexels_key:
        providers.append(_search_pexels)
    if pixabay_key:
        providers.append(_search_pixabay)
    random.shuffle(providers)
    return providers, ''


def _search_pexels(query, color, page, per_page, orientation, visual_type=None):
    """Search via Pexels API. Returns normalized results dict."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        return None

    params = {'query': query, 'page': page, 'per_page': min(per_page, 80)}
    if color:
        params['color'] = PEXELS_COLOR_MAP.get(color, color)
    if orientation:
        params['orientation'] = orientation

    resp = http_requests.get(
        'https://api.pexels.com/v1/search',
        params=params,
        headers={'Authorization': api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    total = data.get('total_results', 0)
    results = []
    for photo in data.get('photos', []):
        src = photo.get('src', {})
        alt_text = photo.get('alt', query)
        results.append({
            'id': str(photo['id']),
            'thumbUrl': src.get('tiny', src.get('small', '')),
            'smallUrl': src.get('small', ''),
            'regularUrl': src.get('medium', src.get('large', '')),
            'fullUrl': src.get('original', ''),
            'photographer': photo.get('photographer', 'Unknown'),
            'photographerUrl': photo.get('photographer_url', ''),
            'altText': alt_text,
            'tags': _tags_from_text(query, alt_text),
            'width': photo.get('width', 0),
            'height': photo.get('height', 0),
            'source': 'pexels',
        })

    return {
        'results': results,
        'total': total,
        'total_pages': math.ceil(total / max(per_page, 1)),
        'source': 'pexels',
    }


def _search_pixabay(query, color, page, per_page, orientation, visual_type=None):
    """Search via Pixabay API. Returns normalized results dict."""
    api_key = os.environ.get('PIXABAY_API_KEY', '')
    if not api_key:
        return None

    params = {
        'key': api_key,
        'q': query,
        'page': page,
        'per_page': min(per_page, 200),
        'image_type': PIXABAY_IMAGE_TYPE_BY_VISUAL_TYPE.get(visual_type, 'photo'),
    }
    if color:
        params['colors'] = PIXABAY_COLOR_MAP.get(color, color)
    pixabay_orientation = PIXABAY_ORIENTATION_MAP.get(orientation, '')
    if pixabay_orientation:
        params['orientation'] = pixabay_orientation

    resp = http_requests.get(
        'https://pixabay.com/api/',
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    total = data.get('totalHits', 0)
    results = []
    for hit in data.get('hits', []):
        raw_tags = hit.get('tags', query)
        results.append({
            'id': str(hit['id']),
            'thumbUrl': hit.get('previewURL', ''),
            'smallUrl': hit.get('webformatURL', ''),
            'regularUrl': hit.get('webformatURL', ''),
            'fullUrl': hit.get('largeImageURL', ''),
            'photographer': hit.get('user', 'Unknown'),
            'photographerUrl': f"https://pixabay.com/users/{hit.get('user', '')}-{hit.get('user_id', '')}/" if hit.get('user') else '',
            'altText': raw_tags,
            'tags': _tags_from_text(query, raw_tags),
            'width': hit.get('imageWidth', 0),
            'height': hit.get('imageHeight', 0),
            'source': 'pixabay',
        })

    results = _filter_square_results(results, orientation)
    total = len(results) if orientation == 'square' else total

    return {
        'results': results,
        'total': total,
        'total_pages': math.ceil(total / max(per_page, 1)),
        'source': 'pixabay',
    }


@images_bp.route('/api/images/search')
def search_images():
    """Proxy stock photo search — randomly picks Pexels or Pixabay to spread rate limits."""
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    pixabay_key = os.environ.get('PIXABAY_API_KEY', '')

    if not pexels_key and not pixabay_key:
        return jsonify({'error': 'Image search is not configured. Please contact the administrator.'}), 503

    query = request.args.get('q', '')
    color = request.args.get('color', '')
    page = request.args.get('page', 1, type=int)
    orientation = request.args.get('orientation', '')
    per_page = request.args.get('per_page', 30, type=int)
    visual_type = request.args.get('visual_type', '').strip()
    if visual_type not in VISUAL_TYPE_TERMS:
        visual_type = ''
    provider = _normalize_provider(request.args.get('provider', ''))

    if not query and not color and not orientation and not visual_type:
        return jsonify({'results': [], 'total': 0, 'total_pages': 0})

    search_query = _compose_search_query(query, visual_type)

    providers, provider_error = _build_provider_plan(provider, visual_type, pexels_key, pixabay_key)
    if provider_error:
        status = 400 if provider == 'pexels' and visual_type in PIXABAY_IMAGE_TYPE_BY_VISUAL_TYPE else 503
        return jsonify({'error': provider_error}), status
    if not providers:
        return jsonify({'error': 'Image search is not configured. Please contact the administrator.'}), 503

    # Try each provider in shuffled order; fall back on failure
    for provider in providers:
        try:
            result = provider(search_query, color, page, per_page, orientation, visual_type)
            if result and result.get('results'):
                return jsonify(result)
        except http_requests.exceptions.Timeout:
            continue
        except http_requests.exceptions.HTTPError:
            continue
        except Exception:
            continue

    # All providers failed — try once more with explicit error reporting
    try:
        result = providers[0](search_query, color, page, per_page, orientation, visual_type)
        if result is not None:
            return jsonify(result)
    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'Image search timed out. Please try again.'}), 504
    except http_requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        return jsonify({'error': f'Image API error ({status})'}), status
    except Exception as e:
        # Log full error server-side — never send raw exception to frontend (may contain API keys in URLs)
        current_app.logger.error(f"Image search failed: {e}")
        return jsonify({'error': 'Image search failed. Please try again later.'}), 500

    return jsonify({'results': [], 'total': 0, 'total_pages': 0})
