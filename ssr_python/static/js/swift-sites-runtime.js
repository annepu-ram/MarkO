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
            // Support both old and new button selectors
            const prevButton = carouselElement.querySelector('.carousel-prev') || carouselElement.querySelector('.prev');
            const nextButton = carouselElement.querySelector('.carousel-next') || carouselElement.querySelector('.next');
            // Support both old dots and new indicators
            const indicatorsContainer = carouselElement.querySelector('.carousel-indicators') || carouselElement.querySelector('.carousel-dots');
            const indicators = carouselElement.querySelectorAll('.carousel-indicator') || carouselElement.querySelectorAll('.carousel-dots span');
            const pauseButton = carouselElement.querySelector('.carousel-pause');
            const totalSlides = slides.length;

            if (totalSlides < 2) {
                if (prevButton) prevButton.style.display = 'none';
                if (nextButton) nextButton.style.display = 'none';
                if (indicatorsContainer) indicatorsContainer.style.display = 'none';
                if (pauseButton) pauseButton.style.display = 'none';
                return;
            }

            let currentIndex = 0;
            let autoplayInterval = null;
            let isPaused = false;

            // Read configuration from data attributes
            const autoplay = carouselElement.dataset.autoplay === 'true';
            const delay = parseInt(carouselElement.dataset.delay, 10) || 3000;
            const loop = carouselElement.dataset.loop !== 'false'; // Default true
            const pauseOnHover = carouselElement.dataset.pauseOnHover !== 'false'; // Default true
            const swipeEnabled = carouselElement.dataset.swipeEnabled !== 'false'; // Default true
            const swipeThreshold = parseInt(carouselElement.dataset.swipeThreshold, 10) || 50;
            const keyboardNav = carouselElement.dataset.keyboardNav !== 'false'; // Default true
            const animDuration = parseInt(carouselElement.dataset.animationDuration, 10) || 300;

            // Set CSS variable for animation duration
            carouselElement.style.setProperty('--carousel-duration', `${animDuration}ms`);

            // Check if fade transition
            const isFade = carouselElement.classList.contains('carousel-fade');

            function updateCarousel() {
                // For slide transition
                if (!isFade && slidesContainer) {
                    slidesContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
                }

                // Update active slide class (for fade and accessibility)
                slides.forEach((slide, index) => {
                    const isActive = index === currentIndex;
                    slide.classList.toggle('active', isActive);
                    slide.setAttribute('aria-hidden', !isActive);
                });

                // Update indicators
                indicators.forEach((indicator, index) => {
                    const isActive = index === currentIndex;
                    indicator.classList.toggle('active', isActive);
                    indicator.setAttribute('aria-selected', isActive);
                });
            }

            function goToSlide(index) {
                if (loop) {
                    currentIndex = ((index % totalSlides) + totalSlides) % totalSlides;
                } else {
                    currentIndex = Math.max(0, Math.min(index, totalSlides - 1));
                }
                updateCarousel();
            }

            function nextSlide() {
                if (!loop && currentIndex >= totalSlides - 1) return;
                goToSlide(currentIndex + 1);
            }

            function prevSlide() {
                if (!loop && currentIndex <= 0) return;
                goToSlide(currentIndex - 1);
            }

            function startAutoplay() {
                if (autoplay && !isPaused) {
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

            // Pause button functionality (WCAG 2.2.2)
            if (pauseButton) {
                const pauseIcon = pauseButton.querySelector('.pause-icon');
                const playIcon = pauseButton.querySelector('.play-icon');

                pauseButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    isPaused = !isPaused;
                    pauseButton.dataset.playing = !isPaused;
                    pauseButton.setAttribute('aria-label', isPaused ? 'Play carousel' : 'Pause carousel');

                    if (pauseIcon) pauseIcon.style.display = isPaused ? 'none' : 'inline';
                    if (playIcon) playIcon.style.display = isPaused ? 'inline' : 'none';

                    if (isPaused) {
                        stopAutoplay();
                    } else {
                        startAutoplay();
                    }
                });
            }

            // Navigation button handlers
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

            // Indicator click handlers
            indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', (e) => {
                    e.stopPropagation();
                    goToSlide(index);
                    startAutoplay();
                });
            });

            // Pause on hover
            if (pauseOnHover && autoplay) {
                carouselElement.addEventListener('mouseenter', () => {
                    if (!isPaused) stopAutoplay();
                });
                carouselElement.addEventListener('mouseleave', () => {
                    if (!isPaused) startAutoplay();
                });
            }

            // Touch swipe support
            if (swipeEnabled && slidesContainer) {
                let touchStartX = 0;
                let touchStartY = 0;
                let isSwiping = false;

                slidesContainer.addEventListener('touchstart', (e) => {
                    touchStartX = e.changedTouches[0].screenX;
                    touchStartY = e.changedTouches[0].screenY;
                    isSwiping = true;

                    // Pause autoplay during swipe
                    if (autoplay && !isPaused) {
                        stopAutoplay();
                    }
                }, { passive: true });

                slidesContainer.addEventListener('touchmove', (e) => {
                    if (!isSwiping) return;

                    // Calculate horizontal vs vertical movement
                    const deltaX = Math.abs(e.changedTouches[0].screenX - touchStartX);
                    const deltaY = Math.abs(e.changedTouches[0].screenY - touchStartY);

                    // If horizontal movement is greater, prevent vertical scroll
                    if (deltaX > deltaY && deltaX > 10) {
                        e.preventDefault();
                    }
                }, { passive: false });

                slidesContainer.addEventListener('touchend', (e) => {
                    if (!isSwiping) return;
                    isSwiping = false;

                    const touchEndX = e.changedTouches[0].screenX;
                    const swipeDistance = touchEndX - touchStartX;

                    // Check if swipe distance exceeds threshold
                    if (Math.abs(swipeDistance) >= swipeThreshold) {
                        if (swipeDistance < 0) {
                            // Swipe left - go to next slide
                            nextSlide();
                        } else {
                            // Swipe right - go to previous slide
                            prevSlide();
                        }
                    }

                    // Resume autoplay after swipe
                    if (autoplay && !isPaused) {
                        startAutoplay();
                    }
                }, { passive: true });

                // Cancel swipe if touch leaves element
                slidesContainer.addEventListener('touchcancel', () => {
                    isSwiping = false;
                    if (autoplay && !isPaused) {
                        startAutoplay();
                    }
                }, { passive: true });
            }

            // Keyboard navigation support
            if (keyboardNav) {
                // Make carousel focusable
                carouselElement.setAttribute('tabindex', '0');

                carouselElement.addEventListener('keydown', (e) => {
                    switch (e.key) {
                        case 'ArrowLeft':
                            e.preventDefault();
                            prevSlide();
                            startAutoplay();
                            break;
                        case 'ArrowRight':
                            e.preventDefault();
                            nextSlide();
                            startAutoplay();
                            break;
                        case 'Home':
                            e.preventDefault();
                            goToSlide(0);
                            startAutoplay();
                            break;
                        case 'End':
                            e.preventDefault();
                            goToSlide(totalSlides - 1);
                            startAutoplay();
                            break;
                        case ' ':  // Spacebar
                        case 'Enter':
                            // Toggle play/pause if pause button exists
                            if (pauseButton && autoplay) {
                                e.preventDefault();
                                pauseButton.click();
                            }
                            break;
                    }
                });

                // Add focus styles
                carouselElement.addEventListener('focus', () => {
                    carouselElement.classList.add('carousel-focused');
                });
                carouselElement.addEventListener('blur', () => {
                    carouselElement.classList.remove('carousel-focused');
                });
            }

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

            // Mobile menu toggle with hamburger/X animation
            const mobileMenuButton = titlebarElement.querySelector('.mobile-menu-button');
            const navLinks = titlebarElement.querySelector('.titlebar-nav');

            if (mobileMenuButton && navLinks) {
                mobileMenuButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const isOpen = navLinks.classList.toggle('active');
                    mobileMenuButton.classList.toggle('open', isOpen);
                });
            }

            // Also set up mobile menu on clone
            const cloneMobileMenuButton = clone.querySelector('.mobile-menu-button');
            const cloneNavLinks = clone.querySelector('.titlebar-nav');

            if (cloneMobileMenuButton && cloneNavLinks) {
                cloneMobileMenuButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const isOpen = cloneNavLinks.classList.toggle('active');
                    cloneMobileMenuButton.classList.toggle('open', isOpen);
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
