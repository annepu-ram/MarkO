/**
 * Images Panel - Browse, search, and select stock photos
 * Connects to Pexels / Pixabay APIs via server proxy to hide API keys
 */

import { debounce } from './utils/timing.js';

// Module state
let searchQuery = '';
let activeColor = null;
let activeOrientation = null; // null | 'horizontal' | 'vertical' | 'square'
let searchResults = [];
let selectedImages = [];
let currentPage = 1;
let totalPages = 1;
let isLoading = false;
let hasSearched = false;

// Constants
const DEBOUNCE_MS = 300;
const RESULTS_PER_PAGE = 30;
const STORAGE_KEY = 'swift_sites_selected_images';

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

/**
 * Load selected images from localStorage
 */
function loadSelectedImages() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            selectedImages = JSON.parse(stored);
        }
    } catch (e) {
        console.warn('[ImagesPanel] Failed to load selected images:', e);
        selectedImages = [];
    }
}

/**
 * Save selected images to localStorage
 */
function saveSelectedImages() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedImages));
    } catch (e) {
        console.warn('[ImagesPanel] Failed to save selected images:', e);
    }
}

/**
 * Show a toast notification
 */
function showToast(message) {
    const existing = document.querySelector('.images-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'images-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('visible');
    });

    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

/**
 * Search for images via the server proxy (Pexels / Pixabay)
 */
async function searchImages(append = false) {
    if (isLoading) return;
    if (!searchQuery.trim() && !activeColor) return;

    isLoading = true;
    hasSearched = true;

    if (!append) {
        currentPage = 1;
        searchResults = [];
    }

    updateResultsUI();

    try {
        const params = new URLSearchParams({
            q: searchQuery.trim() || 'wallpaper',
            page: currentPage,
            per_page: RESULTS_PER_PAGE,
        });

        if (activeColor) {
            params.set('color', activeColor);
        }

        if (activeOrientation) {
            const orientationMap = { horizontal: 'landscape', vertical: 'portrait', square: 'square' };
            params.set('orientation', orientationMap[activeOrientation]);
        }

        const response = await fetch(`/api/images/search?${params}`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Search failed (${response.status})`);
        }

        const data = await response.json();

        // Server returns normalized format from either Pexels or Pixabay
        const newResults = (data.results || []).map(photo => ({
            id: photo.id,
            url: photo.regularUrl || photo.fullUrl,
            thumbUrl: photo.thumbUrl || photo.smallUrl,
            smallUrl: photo.smallUrl,
            photographer: photo.photographer || 'Unknown',
            photographerUrl: photo.photographerUrl || '',
            altText: photo.altText || searchQuery,
            source: photo.source || 'unknown',
            width: photo.width,
            height: photo.height,
        }));

        if (append) {
            searchResults = [...searchResults, ...newResults];
        } else {
            searchResults = newResults;
        }

        totalPages = data.total_pages || 1;
    } catch (error) {
        console.error('[ImagesPanel] Search failed:', error);
        if (!append) {
            searchResults = [];
        }
    } finally {
        isLoading = false;
        updateResultsUI();
        updateLoadMoreUI();
    }
}

/**
 * Render color filter pills HTML
 */
function renderColorPills() {
    return COLOR_OPTIONS.map(c => {
        const isActive = activeColor === c.value;
        const borderStyle = c.value === 'white' ? 'border-color: var(--border)' : '';
        return `<button class="images-color-pill ${isActive ? 'active' : ''}"
                    data-color="${c.value}"
                    style="background: ${c.hex}; ${borderStyle}"
                    title="${c.label}"></button>`;
    }).join('');
}

const ORIENTATION_OPTIONS = [
    { value: 'horizontal', label: 'Horizontal', icon: '#icon-rectangle-horizontal' },
    { value: 'vertical', label: 'Vertical', icon: '#icon-rectangle-vertical' },
    { value: 'square', label: 'Square', icon: '#icon-square' },
];

/**
 * Render orientation filter pills HTML
 */
function renderOrientationPills() {
    return ORIENTATION_OPTIONS.map(o => {
        const isActive = activeOrientation === o.value;
        return `<button class="images-orientation-pill ${isActive ? 'active' : ''}"
                    data-orientation="${o.value}" title="${o.label}">
                    <svg aria-hidden="true"><use href="${o.icon}"></use></svg>
                </button>`;
    }).join('');
}

/**
 * Render skeleton loading cards
 */
function renderSkeletons(count = 9) {
    let html = '';
    for (let i = 0; i < count; i++) {
        html += '<div class="images-skeleton"></div>';
    }
    return html;
}

/**
 * Render search result cards
 */
function renderResults() {
    if (isLoading && searchResults.length === 0) {
        return renderSkeletons();
    }

    if (searchResults.length === 0) {
        if (hasSearched) {
            return `<div class="images-empty">
                <svg class="images-empty-icon" aria-hidden="true"><use href="#icon-image"></use></svg>
                <div>No results found</div>
            </div>`;
        }
        return `<div class="images-empty">
            <svg class="images-empty-icon" aria-hidden="true"><use href="#icon-search"></use></svg>
            <div>Search for photos above</div>
        </div>`;
    }

    return searchResults.map(photo => {
        const isSelected = selectedImages.some(s => s.id === photo.id);
        return `<div class="images-result-card ${isSelected ? 'selected' : ''}" data-photo-id="${photo.id}">
            <img src="${photo.thumbUrl}" alt="${escapeHtml(photo.altText)}" loading="lazy">
            <div class="images-result-overlay">
                <a class="images-result-credit" href="${escapeHtml(photo.photographerUrl)}" target="_blank" rel="noopener" title="${escapeHtml(photo.photographer)}">${escapeHtml(photo.photographer)}</a>
                <button class="images-select-btn" title="${isSelected ? 'Remove' : 'Select'}">${isSelected ? '\u2713' : '+'}</button>
            </div>
        </div>`;
    }).join('');
}

/**
 * Render the load-more button HTML (placed inside results grid)
 */
function renderLoadMoreHtml() {
    return `<div class="images-load-more" id="imagesLoadMore" style="display: none;">
        <button class="images-load-more-btn">Load More</button>
    </div>`;
}

/**
 * Render selected images section with upload button
 */
function renderSelectedImages() {
    if (selectedImages.length === 0) {
        return '<span class="images-selected-empty">No images selected</span>';
    }

    return selectedImages.map(img => `
        <div class="images-selected-item" data-selected-id="${img.id}">
            <div class="images-selected-thumb" title="Click to copy URL">
                <img src="${img.thumbUrl}" alt="${escapeHtml(img.altText)}">
                <button class="images-remove-btn" title="Remove">\u00d7</button>
            </div>
            <span class="images-selected-label">${escapeHtml(img.altText || img.photographer)}</span>
        </div>
    `).join('');
}

/**
 * Update just the results grid (avoids full re-render)
 */
function updateResultsUI() {
    const grid = document.getElementById('imagesResults');
    if (grid) {
        if (isLoading && searchResults.length === 0) {
            grid.innerHTML = renderSkeletons() + renderLoadMoreHtml();
        } else {
            grid.innerHTML = renderResults() + renderLoadMoreHtml();
            attachResultCardEvents(grid);
        }
        attachLoadMoreEvent();
    }
}

/**
 * Update the load more button visibility
 */
function updateLoadMoreUI() {
    const loadMoreContainer = document.getElementById('imagesLoadMore');
    if (loadMoreContainer) {
        if (searchResults.length > 0 && currentPage < totalPages) {
            loadMoreContainer.style.display = 'block';
            const btn = loadMoreContainer.querySelector('.images-load-more-btn');
            if (btn) btn.disabled = isLoading;
        } else {
            loadMoreContainer.style.display = 'none';
        }
    }
}

/**
 * Update the selected images section
 */
function updateSelectedUI() {
    const header = document.querySelector('.images-selected-header');
    if (header) {
        header.textContent = `Selected (${selectedImages.length})`;
    }

    const grid = document.getElementById('imagesSelectedGrid');
    if (grid) {
        grid.innerHTML = renderSelectedImages();
        attachSelectedImageEvents(grid);
    }

    // Also update result cards to reflect selection state
    const resultCards = document.querySelectorAll('.images-result-card');
    resultCards.forEach(card => {
        const photoId = card.dataset.photoId;
        const isSelected = selectedImages.some(s => s.id === photoId);
        card.classList.toggle('selected', isSelected);
        const btn = card.querySelector('.images-select-btn');
        if (btn) {
            btn.textContent = isSelected ? '\u2713' : '+';
            btn.title = isSelected ? 'Remove' : 'Select';
        }
    });
}

/**
 * Toggle selection of an image
 */
function toggleImageSelection(photoId) {
    const existingIndex = selectedImages.findIndex(s => s.id === photoId);

    if (existingIndex >= 0) {
        selectedImages.splice(existingIndex, 1);
    } else {
        const photo = searchResults.find(r => r.id === photoId);
        if (photo) {
            selectedImages.push({
                id: photo.id,
                url: photo.url,
                thumbUrl: photo.thumbUrl,
                smallUrl: photo.smallUrl,
                photographer: photo.photographer,
                photographerUrl: photo.photographerUrl,
                altText: photo.altText,
                source: photo.source,
                orientation: activeOrientation || 'all',
            });
        }
    }

    saveSelectedImages();
    updateSelectedUI();
}

/**
 * Remove an image from selection by ID
 */
function removeSelectedImage(imageId) {
    selectedImages = selectedImages.filter(s => s.id !== imageId);
    saveSelectedImages();
    updateSelectedUI();
}

/**
 * Copy image URL to clipboard
 */
async function copyImageUrl(imageId) {
    const img = selectedImages.find(s => s.id === imageId);
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
}

/**
 * Attach events to result cards
 */
function attachResultCardEvents(container) {
    container.querySelectorAll('.images-result-card').forEach(card => {
        const selectBtn = card.querySelector('.images-select-btn');
        if (selectBtn) {
            selectBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleImageSelection(card.dataset.photoId);
            });
        }

        const credit = card.querySelector('.images-result-credit');
        if (credit) {
            credit.addEventListener('click', (e) => e.stopPropagation());
        }

        card.addEventListener('click', () => {
            toggleImageSelection(card.dataset.photoId);
        });
    });
}

/**
 * Attach click event to the load-more button (called after each grid re-render)
 */
function attachLoadMoreEvent() {
    const btn = document.querySelector('#imagesLoadMore .images-load-more-btn');
    if (btn) {
        btn.addEventListener('click', () => {
            currentPage++;
            searchImages(true);
        });
    }
}

/**
 * Attach events to selected image thumbnails
 */
function attachSelectedImageEvents(container) {
    container.querySelectorAll('.images-selected-item').forEach(item => {
        const imageId = item.dataset.selectedId;

        const removeBtn = item.querySelector('.images-remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                removeSelectedImage(imageId);
            });
        }

        const thumb = item.querySelector('.images-selected-thumb');
        if (thumb) {
            thumb.addEventListener('click', () => {
                copyImageUrl(imageId);
            });
        }
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle file upload - creates object URL and adds to selected images
 */
function handleFileUpload(file) {
    const objectUrl = URL.createObjectURL(file);
    const uploadedImage = {
        id: 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        url: objectUrl,
        thumbUrl: objectUrl,
        smallUrl: objectUrl,
        photographer: 'Uploaded',
        photographerUrl: '',
        altText: file.name.replace(/\.[^/.]+$/, ''),
        source: 'upload',
        orientation: 'all',
    };

    selectedImages.push(uploadedImage);
    saveSelectedImages();
    updateSelectedUI();
    showToast(`"${file.name}" added to selected images`);
}

/**
 * Render the full images panel (called when panel opens)
 */
export function renderImagesPanel() {
    const container = document.getElementById('imagesContent');
    if (!container) return;

    loadSelectedImages();

    container.innerHTML = `
        <!-- Search Bar -->
        <div class="images-search">
            <input type="text" class="images-search-input"
                   placeholder="Search photos..."
                   value="${escapeHtml(searchQuery)}">
            <svg class="images-search-icon" aria-hidden="true"><use href="#icon-search"></use></svg>
        </div>

        <!-- Color Filters -->
        <div class="images-colors">
            <span class="images-colors-label">Colors</span>
            <div class="images-color-pills">
                ${renderColorPills()}
            </div>
        </div>

        <!-- Orientation Filters -->
        <div class="images-orientation">
            <span class="images-orientation-label">Orientation</span>
            <div class="images-orientation-pills">
                ${renderOrientationPills()}
            </div>
        </div>

        <!-- Results Grid (load-more button lives inside grid, spans all columns) -->
        <div class="images-results" id="imagesResults">
            ${renderResults()}
            ${renderLoadMoreHtml()}
        </div>

        <!-- Selected / Uploaded Images -->
        <div class="images-selected-section">
            <div class="images-selected-header-row">
                <span class="images-selected-header">Selected (${selectedImages.length})</span>
                <button class="images-upload-btn" id="imagesUploadBtn" title="Upload image">
                    <svg aria-hidden="true"><use href="#icon-upload"></use></svg>
                    Upload
                </button>
                <input type="file" id="imagesUploadInput" accept="image/*" hidden>
            </div>
            <div class="images-selected-grid" id="imagesSelectedGrid">
                ${renderSelectedImages()}
            </div>
        </div>
    `;

    attachImagesPanelEvents(container);
}

/**
 * Attach all event handlers to the images panel
 */
function attachImagesPanelEvents(container) {
    // Search input with debounce
    const searchInput = container.querySelector('.images-search-input');
    if (searchInput) {
        const debouncedSearch = debounce((value) => {
            searchQuery = value;
            searchImages();
        }, DEBOUNCE_MS);

        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                searchQuery = e.target.value;
                searchImages();
            }
        });
    }

    // Color pill clicks
    container.querySelectorAll('.images-color-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const color = pill.dataset.color;
            activeColor = activeColor === color ? null : color;

            container.querySelectorAll('.images-color-pill').forEach(p => {
                p.classList.toggle('active', p.dataset.color === activeColor);
            });

            if (searchQuery.trim() || activeColor) {
                searchImages();
            }
        });
    });

    // Orientation pill clicks (toggle like color pills)
    container.querySelectorAll('.images-orientation-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const orientation = pill.dataset.orientation;
            activeOrientation = activeOrientation === orientation ? null : orientation;

            container.querySelectorAll('.images-orientation-pill').forEach(p => {
                p.classList.toggle('active', p.dataset.orientation === activeOrientation);
            });

            if (searchQuery.trim() || activeColor) {
                searchImages();
            }
        });
    });

    // Result card events
    const resultsGrid = container.querySelector('#imagesResults');
    if (resultsGrid) {
        attachResultCardEvents(resultsGrid);
    }

    // Selected image events
    const selectedGrid = container.querySelector('#imagesSelectedGrid');
    if (selectedGrid) {
        attachSelectedImageEvents(selectedGrid);
    }

    // Load More button (event re-attached by updateResultsUI after each grid render)
    attachLoadMoreEvent();

    // Upload button
    const uploadBtn = container.querySelector('#imagesUploadBtn');
    const uploadInput = container.querySelector('#imagesUploadInput');

    if (uploadBtn && uploadInput) {
        uploadBtn.addEventListener('click', () => {
            uploadInput.click();
        });

        uploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
                uploadInput.value = '';
            }
        });
    }
}
