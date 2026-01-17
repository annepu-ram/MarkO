export async function loadSvgSprite({
    mountSelector = '#svgSpriteRoot',
    spritePath = 'assets/icon-sprite.svg',
} = {}) {
    if (typeof document === 'undefined') {
        return;
    }

    const mountPoint = document.querySelector(mountSelector);
    if (!mountPoint) {
        return;
    }

    if (mountPoint.dataset.spriteLoaded === 'true') {
        return;
    }

    if (typeof fetch !== 'function') {
        console.warn('Fetch API is not available; skipping SVG sprite load.');
        return;
    }

    try {
        const response = await fetch(spritePath, { cache: 'force-cache' });
        if (!response.ok) {
            throw new Error(`Failed to fetch sprite: ${response.status} ${response.statusText}`);
        }

        const spriteMarkup = await response.text();
        mountPoint.innerHTML = spriteMarkup;
        mountPoint.dataset.spriteLoaded = 'true';
        mountPoint.dataset.spritePath = spritePath;
        mountPoint.hidden = false;
        mountPoint.setAttribute('aria-hidden', 'true');
    } catch (error) {
        console.error('Failed to load SVG sprite:', error);
    }
}
