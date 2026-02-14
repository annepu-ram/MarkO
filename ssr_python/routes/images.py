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


def _search_pexels(query, color, page, per_page, orientation):
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
        results.append({
            'id': str(photo['id']),
            'thumbUrl': src.get('tiny', src.get('small', '')),
            'smallUrl': src.get('small', ''),
            'regularUrl': src.get('medium', src.get('large', '')),
            'fullUrl': src.get('original', ''),
            'photographer': photo.get('photographer', 'Unknown'),
            'photographerUrl': photo.get('photographer_url', ''),
            'altText': photo.get('alt', query),
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


def _search_pixabay(query, color, page, per_page, orientation):
    """Search via Pixabay API. Returns normalized results dict."""
    api_key = os.environ.get('PIXABAY_API_KEY', '')
    if not api_key:
        return None

    params = {
        'key': api_key,
        'q': query,
        'page': page,
        'per_page': min(per_page, 200),
        'image_type': 'photo',
    }
    if color:
        params['colors'] = PIXABAY_COLOR_MAP.get(color, color)
    if orientation:
        params['orientation'] = orientation

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
        results.append({
            'id': str(hit['id']),
            'thumbUrl': hit.get('previewURL', ''),
            'smallUrl': hit.get('webformatURL', ''),
            'regularUrl': hit.get('webformatURL', ''),
            'fullUrl': hit.get('largeImageURL', ''),
            'photographer': hit.get('user', 'Unknown'),
            'photographerUrl': f"https://pixabay.com/users/{hit.get('user', '')}-{hit.get('user_id', '')}/" if hit.get('user') else '',
            'altText': hit.get('tags', query),
            'width': hit.get('imageWidth', 0),
            'height': hit.get('imageHeight', 0),
            'source': 'pixabay',
        })

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

    if not query and not color:
        return jsonify({'results': [], 'total': 0, 'total_pages': 0})

    search_query = query or 'wallpaper'

    # Build list of available providers and pick one randomly
    providers = []
    if pexels_key:
        providers.append(_search_pexels)
    if pixabay_key:
        providers.append(_search_pixabay)
    random.shuffle(providers)

    # Try each provider in shuffled order; fall back on failure
    for provider in providers:
        try:
            result = provider(search_query, color, page, per_page, orientation)
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
        result = providers[0](search_query, color, page, per_page, orientation)
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
