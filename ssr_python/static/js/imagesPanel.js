/**
 * Images Panel - Alpine.js component for browsing, searching, and selecting photos.
 * Connects to Pexels / Pixabay APIs via server proxy.
 * Images stored in DB (MediaAsset) — DB is single source of truth.
 */

const RESULTS_PER_PAGE = 30;

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message) {
    const existing = document.querySelector('.images-toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'images-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

/**
 * Alpine component definition for the images panel.
 * Usage: x-data="imagesPanel()" on the panel container.
 */
function imagesPanel() {
    return {
        searchQuery: '',
        searchResults: [],
        selectedImages: [],
        currentPage: 1,
        totalPages: 1,
        resultMode: 'library',
        isLoading: false,
        hasSearched: false,
        initialized: false,

        init() {
            // Load images from DB on first init
            if (!this.initialized) {
                this.initialized = true;
                this.loadSelectedImages();
            }
        },

        async loadSelectedImages() {
            try {
                const resp = await fetch('/api/media');
                if (!resp.ok) return;
                const data = await resp.json();
                this.selectedImages = (data.images || []).map(img => ({
                    id: img.id,
                    url: img.url,
                    thumbUrl: img.url,
                    altText: img.alt_text || img.original_name || '',
                    photographer: img.photographer || '',
                    orientation: img.orientation || null,
                    source: img.source || 'stock',
                    width: img.width,
                    height: img.height,
                    tags: Array.isArray(img.tags) ? img.tags : [],
                }));
            } catch (e) {
                console.warn('[ImagesPanel] Failed to load images from API:', e);
            }
        },

        async searchLibraryImages() {
            if (this.isLoading) return;
            this.isLoading = true;
            this.hasSearched = true;
            this.resultMode = 'library';
            this.currentPage = 1;
            this.totalPages = 1;
            this.searchResults = [];

            try {
                const params = new URLSearchParams();
                const query = this.searchQuery.trim();
                if (query) params.set('q', query);

                const response = await fetch(`/api/media${params.toString() ? `?${params}` : ''}`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `Library search failed (${response.status})`);
                }

                const data = await response.json();
                this.searchResults = (data.images || []).map(img => ({
                    id: img.id,
                    url: img.url,
                    fullUrl: img.url,
                    thumbUrl: img.url,
                    smallUrl: img.url,
                    photographer: img.photographer || '',
                    photographerUrl: '',
                    altText: img.alt_text || img.original_name || '',
                    source: img.source || 'library',
                    width: img.width,
                    height: img.height,
                    tags: Array.isArray(img.tags) ? img.tags : [],
                    isLibraryAsset: true,
                }));
            } catch (error) {
                console.error('[ImagesPanel] Library search failed:', error);
                this.searchResults = [];
            } finally {
                this.isLoading = false;
            }
        },

        async searchStockImages(append = false) {
            if (this.isLoading) return;
            if (!this.searchQuery.trim()) return;

            this.isLoading = true;
            this.hasSearched = true;
            this.resultMode = 'stock';
            if (!append) {
                this.currentPage = 1;
                this.searchResults = [];
            }

            try {
                const params = new URLSearchParams({
                    q: this.searchQuery.trim(),
                    page: this.currentPage,
                    per_page: RESULTS_PER_PAGE,
                });

                const response = await fetch(`/api/images/search?${params}`);
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `Search failed (${response.status})`);
                }

                const data = await response.json();
                const newResults = (data.results || []).map(photo => ({
                    id: photo.id,
                    url: photo.regularUrl || photo.fullUrl,
                    fullUrl: photo.fullUrl || photo.regularUrl,
                    thumbUrl: photo.thumbUrl || photo.smallUrl,
                    smallUrl: photo.smallUrl,
                    photographer: photo.photographer || 'Unknown',
                    photographerUrl: photo.photographerUrl || '',
                    altText: photo.altText || this.searchQuery,
                    source: photo.source || 'unknown',
                    width: photo.width,
                    height: photo.height,
                    tags: Array.isArray(photo.tags) ? photo.tags : [],
                }));

                if (append) {
                    this.searchResults = [...this.searchResults, ...newResults];
                } else {
                    this.searchResults = newResults;
                }
                this.totalPages = data.total_pages || 1;
            } catch (error) {
                console.error('[ImagesPanel] Search failed:', error);
                if (!append) this.searchResults = [];
            } finally {
                this.isLoading = false;
            }
        },

        searchImages(append = false) {
            return this.searchStockImages(append);
        },

        isPhotoSelected(photoId) {
            return this.selectedImages.some(s => s.id === photoId);
        },

        async toggleImageSelection(photo) {
            const existing = this.selectedImages.find(s => s.id === photo.id);
            if (photo.isLibraryAsset) {
                if (!existing) {
                    this.selectedImages = [
                        photo,
                        ...this.selectedImages,
                    ];
                }
                showToast('Image available in library');
                return;
            }
            if (existing) {
                await this.removeSelectedImage(existing.id);
                return;
            }
            // Download to server
            try {
                const resp = await fetch('/api/images/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: photo.fullUrl || photo.url,
                        alt_text: photo.altText || '',
                        photographer: photo.photographer || '',
                        source: photo.source || 'stock',
                        tags: photo.tags || [],
                    }),
                });
                if (!resp.ok) return;
                await this.loadSelectedImages();
                showToast('Image downloaded');
            } catch (e) {
                console.warn('[ImagesPanel] Download failed:', e);
            }
        },

        async removeSelectedImage(imageId) {
            try {
                await fetch(`/api/media/${imageId}`, { method: 'DELETE' });
            } catch (e) {
                console.warn('[ImagesPanel] Failed to delete image:', e);
            }
            await this.loadSelectedImages();
        },

        async copyImageUrl(imageId) {
            const img = this.selectedImages.find(s => s.id === imageId);
            if (!img) return;
            try {
                await navigator.clipboard.writeText(img.url);
                showToast('Image URL copied to clipboard');
            } catch (e) {
                const textarea = document.createElement('textarea');
                textarea.value = img.url;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('Image URL copied to clipboard');
            }
        },

        loadMore() {
            this.currentPage++;
            if (this.resultMode === 'stock') this.searchStockImages(true);
        },

        get hasMore() {
            return this.resultMode === 'stock' && this.searchResults.length > 0 && this.currentPage < this.totalPages;
        },

        handleUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            this._uploadFile(file);
            event.target.value = '';
        },

        async _uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            try {
                const resp = await fetch('/api/images/upload', {
                    method: 'POST',
                    body: formData,
                });
                if (!resp.ok) { showToast('Upload failed'); return; }
                await this.loadSelectedImages();
                showToast(`"${file.name}" uploaded`);
            } catch (e) {
                console.warn('[ImagesPanel] Upload failed:', e);
                showToast('Upload failed');
            }
        },

        esc(text) { return escapeHtml(text); },
    };
}

// Register Alpine component globally
document.addEventListener('alpine:init', () => {
    Alpine.data('imagesPanel', imagesPanel);
});

/**
 * renderImagesPanel — called by panel toggle when images panel opens.
 * With Alpine, the template is already in index.html. We just need to
 * trigger a data refresh (selected images from DB).
 */
export function renderImagesPanel() {
    // Alpine component handles its own init/load via init().
    // If the component is already initialized, re-fetch selected images.
    const el = document.getElementById('imagesContent');
    if (el && el._x_dataStack) {
        const data = el._x_dataStack[0];
        if (data && data.loadSelectedImages) {
            data.loadSelectedImages();
        }
    }
}
