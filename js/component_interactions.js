const componentInitializers = {
    carousel: initializeCarousel,
    titlebar: initializeTitlebar
};

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

function initializeTitlebar(titlebarElement) {
    if (!titlebarElement) return;

    const mobileMenuButton = titlebarElement.querySelector('.mobile-menu-button');
    const navLinks = titlebarElement.querySelector('.titlebar-nav');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
}