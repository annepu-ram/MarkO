/**
 * Swift Sites Component Runtime
 *
 * Standalone JavaScript for interactive components.
 * Include this file in exported sites for component functionality.
 *
 * Features:
 * - Carousel with autoplay, navigation, and dots
 * - Tabs with click-to-switch functionality
 * - Accordion with optional multi-open support
 * - Titlebar with sticky scroll behavior and mobile menu
 *
 * Usage:
 * 1. Include this script in your HTML: <script src="swift-sites-runtime.js"></script>
 * 2. Components auto-initialize on DOMContentLoaded
 * 3. Call SwiftSites.init() to re-initialize after dynamic content updates
 */
(function(global) {
    'use strict';

    const SwiftSites = {
        version: '1.0.0',

        /**
         * Initialize all interactive components on the page
         */
        init: function() {
            this.initCarousels();
            this.initTabs();
            this.initAccordions();
            this.initTitlebars();
        },

        /**
         * Initialize all carousel components
         */
        initCarousels: function() {
            document.querySelectorAll('.carousel').forEach(carousel => {
                this._initCarousel(carousel);
            });
        },

        /**
         * Initialize a single carousel
         * @param {HTMLElement} carouselElement - The carousel container
         */
        _initCarousel: function(carouselElement) {
            if (!carouselElement || carouselElement.dataset.ssInitialized === 'true') return;
            carouselElement.dataset.ssInitialized = 'true';

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

            const autoplay = carouselElement.dataset.autoplay === 'true';
            const delay = parseInt(carouselElement.dataset.delay, 10) || 3000;

            function updateCarousel() {
                if (slidesContainer) {
                    slidesContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
                }
                dots.forEach((dot, index) => {
                    dot.classList.toggle('active', index === currentIndex);
                });
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
                if (autoplayInterval) {
                    clearInterval(autoplayInterval);
                    autoplayInterval = null;
                }
            }

            if (nextButton) {
                nextButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    nextSlide();
                    startAutoplay();
                });
            }

            if (prevButton) {
                prevButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    prevSlide();
                    startAutoplay();
                });
            }

            dots.forEach(dot => {
                dot.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const slideIndex = parseInt(e.target.dataset.slideTo, 10);
                    if (!isNaN(slideIndex)) {
                        currentIndex = slideIndex;
                        updateCarousel();
                        startAutoplay();
                    }
                });
            });

            carouselElement.addEventListener('mouseenter', stopAutoplay);
            carouselElement.addEventListener('mouseleave', startAutoplay);

            updateCarousel();
            startAutoplay();
        },

        /**
         * Initialize all tab components
         */
        initTabs: function() {
            document.querySelectorAll('.tabs').forEach(tabs => {
                this._initTabs(tabs);
            });
        },

        /**
         * Initialize a single tabs component
         * @param {HTMLElement} tabsContainer - The tabs container
         */
        _initTabs: function(tabsContainer) {
            if (!tabsContainer || tabsContainer.dataset.ssInitialized === 'true') return;
            tabsContainer.dataset.ssInitialized = 'true';

            const tabButtons = tabsContainer.querySelectorAll('.tab-label');
            const tabContents = tabsContainer.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const targetId = button.dataset.tab;

                    // Update active states
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));

                    button.classList.add('active');
                    const targetContent = tabsContainer.querySelector(`#${targetId}`);
                    if (targetContent) {
                        targetContent.classList.add('active');
                    }
                });
            });
        },

        /**
         * Initialize all accordion components
         */
        initAccordions: function() {
            document.querySelectorAll('.accordion-container').forEach(accordion => {
                this._initAccordion(accordion);
            });
        },

        /**
         * Initialize a single accordion component
         * @param {HTMLElement} accordionContainer - The accordion container
         */
        _initAccordion: function(accordionContainer) {
            if (!accordionContainer || accordionContainer.dataset.ssInitialized === 'true') return;
            accordionContainer.dataset.ssInitialized = 'true';

            const allowMultiple = accordionContainer.dataset.allowMultiple === 'true';

            if (!allowMultiple) {
                const details = accordionContainer.querySelectorAll('details.accordion');

                details.forEach(detail => {
                    detail.addEventListener('toggle', () => {
                        if (detail.open) {
                            // Close other accordions when one opens
                            details.forEach(other => {
                                if (other !== detail && other.open) {
                                    other.open = false;
                                }
                            });
                        }
                    });
                });
            }
        },

        /**
         * Initialize all titlebar components
         */
        initTitlebars: function() {
            document.querySelectorAll('.titlebar').forEach(titlebar => {
                this._initTitlebar(titlebar);
            });

            // Set up global scroll handler if we have titlebars
            if (document.querySelectorAll('.titlebar').length > 0) {
                this._setupTitlebarScrollHandler();
            }
        },

        _titlebarScrollHandlerAttached: false,

        /**
         * Set up the global scroll handler for titlebar shrink effect
         */
        _setupTitlebarScrollHandler: function() {
            if (this._titlebarScrollHandlerAttached) return;
            this._titlebarScrollHandlerAttached = true;

            const handleScroll = () => {
                const scrolled = window.scrollY > 50;
                document.querySelectorAll('.titlebar').forEach(titlebar => {
                    titlebar.classList.toggle('scrolled', scrolled);
                });
                document.querySelectorAll('.titlebar-clone').forEach(clone => {
                    clone.classList.toggle('scrolled', scrolled);
                });
            };

            window.addEventListener('scroll', handleScroll, { passive: true });
            handleScroll();
        },

        /**
         * Initialize a single titlebar component
         * @param {HTMLElement} titlebarElement - The titlebar element
         */
        _initTitlebar: function(titlebarElement) {
            if (!titlebarElement || titlebarElement.dataset.ssInitialized === 'true') return;
            titlebarElement.dataset.ssInitialized = 'true';

            // Find the page component parent to insert clone
            const pageComponent = titlebarElement.closest('.page');

            // Create clone for sticky behavior
            const clone = titlebarElement.cloneNode(true);
            clone.classList.add('titlebar-clone');
            clone.classList.remove('chrome-target'); // Don't make clone selectable in builder
            clone.removeAttribute('data-component-id'); // Remove component ID from clone
            clone.dataset.ssInitialized = 'true'; // Mark clone as initialized

            // Copy inline styles
            clone.style.cssText = titlebarElement.style.cssText;

            // Insert clone at the beginning of page component (or body if no page)
            if (pageComponent) {
                pageComponent.insertAdjacentElement('afterbegin', clone);
            } else {
                document.body.insertAdjacentElement('afterbegin', clone);
            }

            // Mobile menu toggle
            const mobileMenuButton = titlebarElement.querySelector('.mobile-menu-button');
            const navLinks = titlebarElement.querySelector('.titlebar-nav');

            if (mobileMenuButton && navLinks) {
                mobileMenuButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    navLinks.classList.toggle('active');
                });
            }

            // Also set up mobile menu on clone
            const cloneMobileMenuButton = clone.querySelector('.mobile-menu-button');
            const cloneNavLinks = clone.querySelector('.titlebar-nav');

            if (cloneMobileMenuButton && cloneNavLinks) {
                cloneMobileMenuButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    cloneNavLinks.classList.toggle('active');
                });
            }

            // Handle scroll effect - show clone when original out of view
            const handleTitlebarVisibility = () => {
                const rect = titlebarElement.getBoundingClientRect();
                const isOutOfView = rect.bottom < 0;
                clone.classList.toggle('visible', isOutOfView);
            };

            window.addEventListener('scroll', handleTitlebarVisibility, { passive: true });
            handleTitlebarVisibility();
        },

        /**
         * Clean up titlebar clones (useful before re-rendering)
         */
        cleanupTitlebarClones: function() {
            document.querySelectorAll('.titlebar-clone').forEach(clone => {
                clone.remove();
            });
        },

        /**
         * Reset initialization state (useful for re-initialization)
         */
        reset: function() {
            document.querySelectorAll('[data-ss-initialized]').forEach(el => {
                delete el.dataset.ssInitialized;
            });
            this._titlebarScrollHandlerAttached = false;
            this.cleanupTitlebarClones();
        }
    };

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => SwiftSites.init());
    } else {
        SwiftSites.init();
    }

    // Expose globally
    global.SwiftSites = SwiftSites;

})(typeof window !== 'undefined' ? window : this);
