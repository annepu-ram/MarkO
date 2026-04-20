/**
 * Images Panel - Alpine.js component for browsing, searching, and selecting stock photos.
 * Connects to Pexels / Pixabay APIs via server proxy.
 * Images stored in DB (SiteImage) — DB is single source of truth.
 */

const RESULTS_PER_PAGE = 30;

const COLOR_OPTIONS = [
    { value: 'red', label: 'Red', hex: '#EF4444' },
    { value: 'orange', label: 'Orange', hex: '#F97316' },
    { value: 'yellow', label: 'Yellow', hex: '#EAB308' },
    { value: 'green', label: 'Green', hex: '#22C55E' },
    { value: 'blue', label: 'Blue', hex: '#3B82F6' },
    { value: 'purple', label: 'Purple', hex: '#A855F7' },
    { value: 'black', label: 'Black', hex: '#1A1A1A' },
    { value: 'white', label: 'White', hex: '#FFFFFF' },
];

const ORIENTATION_OPTIONS = [
    { value: 'horizontal', label: 'Horizontal', icon: '#icon-rectangle-horizontal' },
    { value: 'vertical', label: 'Vertical', icon: '#icon-rectangle-vertical' },
    { value: 'square', label: 'Square', icon: '#icon-square' },
];

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
        activeColor: null,
        activeOrientation: null,
        searchResults: [],
        selectedImages: [],
        currentPage: 1,
        totalPages: 1,
        isLoading: false,
        hasSearched: false,
        initialized: false,

        // Constants exposed to template
        colorOptions: COLOR_OPTIONS,
        orientationOptions: ORIENTATION_OPTIONS,

        init() {
            // Load images from DB on first init
            if (!this.initialized) {
                this.initialized = true;
                this.loadSelectedImages();
            }
        },

        async loadSelectedImages() {
            const siteId = window.SITE_ID;
            if (!siteId) {
                this.selectedImages = [];
                return;
            }
            try {
                const resp = await fetch(`/api/sites/${siteId}/media`);
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
                }));
            } catch (e) {
                console.warn('[ImagesPanel] Failed to load images from API:', e);
            }
        },

        async searchImages(append = false) {
            if (this.isLoading) return;
            if (!this.searchQuery.trim() && !this.activeColor) return;

            this.isLoading = true;
            this.hasSearched = true;
            if (!append) {
                this.currentPage = 1;
                this.searchResults = [];
            }

            try {
                const params = new URLSearchParams({
                    q: this.searchQuery.trim() || 'wallpaper',
                    page: this.currentPage,
                    per_page: RESULTS_PER_PAGE,
                });
                if (this.activeColor) params.set('color', this.activeColor);
                if (this.activeOrientation) {
                    const map = { horizontal: 'landscape', vertical: 'portrait', square: 'square' };
                    params.set('orientation', map[this.activeOrientation]);
                }

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

        toggleColor(color) {
            this.activeColor = this.activeColor === color ? null : color;
            if (this.searchQuery.trim() || this.activeColor) this.searchImages();
        },

        toggleOrientation(orientation) {
            this.activeOrientation = this.activeOrientation === orientation ? null : orientation;
            if (this.searchQuery.trim() || this.activeColor) this.searchImages();
        },

        isPhotoSelected(photoId) {
            return this.selectedImages.some(s => s.id === photoId);
        },

        async toggleImageSelection(photo) {
            const existing = this.selectedImages.find(s => s.id === photo.id);
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
                        site_id: window.SITE_ID || undefined,
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
            const siteId = window.SITE_ID;
            if (siteId) {
                try {
                    await fetch(`/api/sites/${siteId}/media/${imageId}`, { method: 'DELETE' });
                } catch (e) {
                    console.warn('[ImagesPanel] Failed to delete image:', e);
                }
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
            this.searchImages(true);
        },

        get hasMore() {
            return this.searchResults.length > 0 && this.currentPage < this.totalPages;
        },

        handleUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            this._uploadFile(file);
            event.target.value = '';
        },

        async _uploadFile(file) {
            const siteId = window.SITE_ID;
            if (!siteId) {
                showToast('Save your site first before uploading images');
                return;
            }
            const formData = new FormData();
            formData.append('file', file);
            try {
                const resp = await fetch(`/api/images/upload?site_id=${siteId}`, {
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
