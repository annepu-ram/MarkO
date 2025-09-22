const componentInitializers = {
    carousel: initializeCarousel,
    titlebar: initializeTitlebar
};

let titlebarScrollHandlerAttached = false;

function handleTitlebarScroll() {
    const scrolled = window.scrollY > 50;
    document.querySelectorAll('.titlebar').forEach(titlebar => {
        titlebar.classList.toggle('scrolled', scrolled);
    });
}


function initializeCarousel(carouselElement, props = {}) {
    if (!carouselElement) return;

    const slidesContainer = carouselElement.querySelector('.carousel-slides');
    const slides = carouselElement.querySelectorAll('.carousel-slide');
    const prevButton = carouselElement.querySelector('.prev');
    const nextButton = carouselElement.querySelector('.next');
    const dotsContainer = carouselElement.querySelector('.carousel-dots');
    const dots = carouselElement.querySelectorAll('.carousel-dots span');
    const totalSlides = slides.length;

    if (totalSlides < 2) {
        if (prevButton) prevButton.style.display = 'none';
        if (nextButton) nextButton.style.display = 'none';
        if (dotsContainer) dotsContainer.style.display = 'none';
        return;
    }

    let currentIndex = 0;
    let autoplayInterval = null;

    const autoplay = props.autoplay === true || props.autoplay === 'true';
    const delay = parseInt(props.delay) || 3000;

    function updateCarousel() {
        if(slidesContainer) {
            slidesContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
        }
        if(dots) {
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % totalSlides;
        updateCarousel();
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateCarousel();
    }

    function startAutoplay() {
        if (autoplay) {
            stopAutoplay();
            autoplayInterval = setInterval(nextSlide, delay);
        }
    }

    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }

    if(nextButton) {
        nextButton.addEventListener('click', () => {
            nextSlide();
            startAutoplay();
        });
    }

    if(prevButton) {
        prevButton.addEventListener('click', () => {
            prevSlide();
            startAutoplay();
        });
    }

    if(dots) {
        dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                currentIndex = parseInt(e.target.dataset.slideTo);
                updateCarousel();
                startAutoplay();
            });
        });
    }

    carouselElement.addEventListener('mouseenter', stopAutoplay);
    carouselElement.addEventListener('mouseleave', startAutoplay);

    updateCarousel();
    startAutoplay();
}

function initializeTitlebar(titlebarElement, props = {}) {
    if (!titlebarElement) return;

    const mobileMenuButton = titlebarElement.querySelector('.mobile-menu-button');
    const navLinks = titlebarElement.querySelector('.titlebar-nav');

    if (mobileMenuButton && navLinks && !mobileMenuButton.dataset.initialized) {
        mobileMenuButton.dataset.initialized = 'true';
        mobileMenuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    const resolveRem = (value, fallback) => {
        if (typeof value === 'number' && !Number.isNaN(value)) {
            return `${value / 10}rem`;
        }
        if (typeof value === 'string') {
            const trimmed = value.trim();
            if (!trimmed && fallback !== undefined) {
                return resolveRem(fallback, undefined);
            }
            if (trimmed.endsWith('rem')) {
                return trimmed;
            }
            const numeric = parseFloat(trimmed);
            if (!Number.isNaN(numeric)) {
                return `${numeric / 10}rem`;
            }
        }
        if (fallback !== undefined) {
            return resolveRem(fallback, undefined);
        }
        return null;
    };

    const ensureRemVar = (variable, value, fallback) => {
        if (titlebarElement.style.getPropertyValue(variable)) return;
        const remValue = resolveRem(value, fallback);
        if (remValue) {
            titlebarElement.style.setProperty(variable, remValue);
        }
    };

    const resolveScale = (value, fallback = 0.5) => {
        const numeric = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isNaN(numeric)) {
            return Math.min(1, Math.max(0.1, numeric / 100));
        }
        return fallback;
    };

    if (!titlebarElement.style.getPropertyValue('--base-height')) {
        const dataHeight = parseFloat(titlebarElement.getAttribute('data-base-height'));
        const propHeight = typeof props.height === 'number' ? props.height : parseFloat(props.height);
        const resolvedHeight = !Number.isNaN(dataHeight) ? dataHeight : (!Number.isNaN(propHeight) ? propHeight : null);
        const heightRem = resolveRem(resolvedHeight, 60);
        if (heightRem) {
            titlebarElement.style.setProperty('--base-height', heightRem);
        }
    }

    ensureRemVar('--title-font-size', props.titleFontSize, 24);
    ensureRemVar('--menu-font-size', props.menuFontSize, 16);

    if (!titlebarElement.style.getPropertyValue('--shrink-scale')) {
        const scale = resolveScale(props.shrinkPercent);
        titlebarElement.style.setProperty('--shrink-scale', `${scale}`);
    }

    if (!titlebarScrollHandlerAttached) {
        titlebarScrollHandlerAttached = true;
        window.addEventListener('scroll', handleTitlebarScroll, { passive: true });
    }

    handleTitlebarScroll();
}


