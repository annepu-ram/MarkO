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
 * 1. Include this script in your HTML via a script tag with src="swift-sites-runtime.js"
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
            // Initialize Lucide icons (replace data-lucide placeholders with inline SVGs)
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            this.initCarousels();
            this.initTabs();
            this.initAccordions();
            this.initTitlebars();
            this.initTickers();
            this.initCounterUps();
            this.initCountdowns();
            this.initPanoramaDisplays();
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

            const radios = tabsContainer.querySelectorAll('.tabs-nav input[type="radio"]');
            const tabContents = tabsContainer.querySelectorAll(':scope > .tab-content');

            radios.forEach((radio, index) => {
                radio.addEventListener('change', () => {
                    // Hide all content panels, show the selected one
                    tabContents.forEach(c => c.classList.remove('active'));
                    if (tabContents[index]) {
                        tabContents[index].classList.add('active');
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
         * Initialize all ticker components
         */
        initTickers: function() {
            document.querySelectorAll('.ticker').forEach(ticker => {
                this._initTicker(ticker);
            });
        },

        _tickerIntervals: [],

        _initTicker: function(tickerElement) {
            if (!tickerElement || tickerElement.dataset.ssInitialized === 'true') return;
            tickerElement.dataset.ssInitialized = 'true';

            var track = tickerElement.querySelector('.ticker-track');
            var items = tickerElement.querySelectorAll('.ticker-item:not(.ticker-item-duplicate)');
            if (!track || items.length === 0) return;

            var speed = parseInt(tickerElement.dataset.speed, 10) || 40;
            var mode = tickerElement.dataset.mode || 'continuous';
            var direction = tickerElement.dataset.direction || 'left';
            var pauseDuration = parseInt(tickerElement.dataset.pauseDuration, 10) || 3000;

            if (mode === 'continuous') {
                this._initContinuousTicker(tickerElement, track, speed);
            } else {
                this._initStepTicker(tickerElement, track, items, pauseDuration, direction);
            }
        },

        _initContinuousTicker: function(tickerEl, track, speed) {
            function updateDuration() {
                var items = track.querySelectorAll('.ticker-item:not(.ticker-item-duplicate)');
                var tickerGap = parseFloat(getComputedStyle(track).gap) || 0;
                var totalWidth = 0;
                items.forEach(function(item) { totalWidth += item.offsetWidth; });
                var offset = totalWidth + (items.length * tickerGap);
                track.style.setProperty('--ticker-offset', '-' + offset + 'px');
                track.style.animationDuration = (offset / speed) + 's';
            }
            updateDuration();

            var resizeTimeout;
            window.addEventListener('resize', function() {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(updateDuration, 150);
            }, { passive: true });
        },

        _initStepTicker: function(tickerElement, track, items, pauseDuration, direction) {
            var self = this;

            var currentIndex = 0;
            var totalItems = items.length;
            var gap = parseFloat(getComputedStyle(track).gap) || 0;

            function getStepDistance() {
                return items[0].offsetWidth + gap;
            }

            function moveToNext() {
                currentIndex++;
                if (currentIndex >= totalItems) {
                    track.style.transition = 'none';
                    track.style.transform = 'translateX(0)';
                    currentIndex = 0;
                    setTimeout(function() {
                        track.style.transition = 'transform 0.6s ease-in-out';
                    }, 50);
                } else {
                    var offset = getStepDistance() * currentIndex;
                    var dir = (direction === 'left') ? -offset : offset;
                    track.style.transform = 'translateX(' + dir + 'px)';
                }
            }

            var intervalId = setInterval(moveToNext, pauseDuration);
            this._tickerIntervals.push(intervalId);

            if (tickerElement.dataset.pauseOnHover === 'true') {
                tickerElement.addEventListener('mouseenter', function() {
                    clearInterval(intervalId);
                });
                tickerElement.addEventListener('mouseleave', function() {
                    intervalId = setInterval(moveToNext, pauseDuration);
                    self._tickerIntervals.push(intervalId);
                });
            }

            var resizeTimeout;
            window.addEventListener('resize', function() {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(function() {
                    gap = parseFloat(getComputedStyle(track).gap) || 0;
                }, 150);
            }, { passive: true });
        },

        cleanupTickers: function() {
            this._tickerIntervals.forEach(function(id) { clearInterval(id); });
            this._tickerIntervals = [];
        },

        /**
         * Initialize all counter-up components
         */
        initCounterUps: function() {
            document.querySelectorAll('.counter-up').forEach(counter => {
                this._initCounterUp(counter);
            });
        },

        /**
         * Initialize a single counter-up component
         * @param {HTMLElement} el - The counter-up element
         */
        _initCounterUp: function(el) {
            if (!el || el.dataset.ssInitialized === 'true') return;
            el.dataset.ssInitialized = 'true';

            const valueEl = el.querySelector('.counter-up__value');
            if (!valueEl) return;

            const endValue = parseInt(el.dataset.endValue, 10) || 0;
            const duration = parseInt(el.dataset.duration, 10) || 2000;
            const prefix = el.dataset.prefix || '';
            const suffix = el.dataset.suffix || '';

            function animateCount() {
                const startTime = performance.now();

                function tick(now) {
                    const elapsed = now - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    // Ease-out cubic
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const current = Math.round(eased * endValue);
                    valueEl.textContent = prefix + current.toLocaleString() + suffix;

                    if (progress < 1) {
                        requestAnimationFrame(tick);
                    }
                }

                requestAnimationFrame(tick);
            }

            // Use IntersectionObserver to trigger animation on viewport entry
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            animateCount();
                            observer.unobserve(el);
                        }
                    });
                }, { threshold: 0.2 });
                observer.observe(el);
            } else {
                // Fallback: animate immediately
                animateCount();
            }
        },

        /**
         * Initialize all countdown components
         */
        initCountdowns: function() {
            document.querySelectorAll('.countdown').forEach(countdown => {
                this._initCountdown(countdown);
            });
        },

        _countdownIntervals: [],

        /**
         * Initialize a single countdown component
         * @param {HTMLElement} el - The countdown element
         */
        _initCountdown: function(el) {
            if (!el || el.dataset.ssInitialized === 'true') return;
            el.dataset.ssInitialized = 'true';

            const targetDate = el.dataset.targetDate;
            const expiredText = el.dataset.expiredText || 'Expired';

            if (!targetDate) return;

            const target = new Date(targetDate).getTime();
            const segments = {
                days: el.querySelector('.countdown__days .countdown__number'),
                hours: el.querySelector('.countdown__hours .countdown__number'),
                minutes: el.querySelector('.countdown__minutes .countdown__number'),
                seconds: el.querySelector('.countdown__seconds .countdown__number')
            };

            function update() {
                const now = Date.now();
                let diff = Math.max(0, target - now);

                if (diff <= 0) {
                    // Show expired text
                    el.innerHTML = '<span class="countdown__expired" style="font: inherit; color: inherit;">' + expiredText + '</span>';
                    return true; // Signal to clear interval
                }

                const days = Math.floor(diff / 86400000);
                diff %= 86400000;
                const hours = Math.floor(diff / 3600000);
                diff %= 3600000;
                const minutes = Math.floor(diff / 60000);
                diff %= 60000;
                const seconds = Math.floor(diff / 1000);

                if (segments.days) segments.days.textContent = String(days).padStart(2, '0');
                if (segments.hours) segments.hours.textContent = String(hours).padStart(2, '0');
                if (segments.minutes) segments.minutes.textContent = String(minutes).padStart(2, '0');
                if (segments.seconds) segments.seconds.textContent = String(seconds).padStart(2, '0');

                return false;
            }

            // Initial update
            if (!update()) {
                const intervalId = setInterval(() => {
                    if (update()) {
                        clearInterval(intervalId);
                    }
                }, 1000);
                this._countdownIntervals.push(intervalId);
            }
        },

        /**
         * Clean up countdown intervals
         */
        cleanupCountdowns: function() {
            this._countdownIntervals.forEach(id => clearInterval(id));
            this._countdownIntervals = [];
        },

        // ---- Panorama Display ----

        _panoramaRAFs: [],

        initPanoramaDisplays: function() {
            var self = this;
            document.querySelectorAll('.panorama-display').forEach(function(el) {
                self._initPanoramaDisplay(el);
            });
        },

        _initPanoramaDisplay: function(el) {
            if (!el || el.dataset.ssInitialized === 'true') return;
            el.dataset.ssInitialized = 'true';

            var self = this;
            var track = el.querySelector('.pd-track');
            var leftArrow = el.querySelector('.pd-arrow-left');
            var rightArrow = el.querySelector('.pd-arrow-right');
            if (!track) return;

            var stepDistance = parseInt(el.dataset.stepDistance, 10) || 300;
            var autoScroll = el.dataset.autoScroll === 'true';
            var autoScrollSpeed = parseFloat(el.dataset.autoScrollSpeed) || 30;
            var pauseOnHover = el.dataset.pauseOnHover === 'true';
            var initialPosition = el.dataset.initialPosition || 'left';

            // --- Arrow visibility (smart boundary logic) ---
            function updateArrows() {
                var scrollLeft = track.scrollLeft;
                var maxScroll = track.scrollWidth - track.clientWidth;
                if (leftArrow)  leftArrow.classList.toggle('pd-arrow-hidden', scrollLeft <= 1);
                if (rightArrow) rightArrow.classList.toggle('pd-arrow-hidden', scrollLeft >= maxScroll - 1);
            }
            track.addEventListener('scroll', updateArrows, { passive: true });

            // --- Arrow click (precision stepping) ---
            if (leftArrow) {
                leftArrow.addEventListener('click', function(e) {
                    e.stopPropagation();
                    track.classList.remove('is-auto-scrolling');
                    track.scrollBy({ left: -stepDistance, behavior: 'smooth' });
                });
            }
            if (rightArrow) {
                rightArrow.addEventListener('click', function(e) {
                    e.stopPropagation();
                    track.classList.remove('is-auto-scrolling');
                    track.scrollBy({ left: stepDistance, behavior: 'smooth' });
                });
            }

            // --- Mouse drag ---
            var isDragging = false, startX = 0, startScrollLeft = 0;
            track.addEventListener('mousedown', function(e) {
                isDragging = true;
                startX = e.pageX;
                startScrollLeft = track.scrollLeft;
                track.classList.add('is-dragging');
                e.preventDefault();
            });
            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                track.scrollLeft = startScrollLeft - (e.pageX - startX);
            });
            document.addEventListener('mouseup', function() {
                if (!isDragging) return;
                isDragging = false;
                track.classList.remove('is-dragging');
            });

            // --- Touch swipe ---
            var touchStartX = 0, touchStartScroll = 0;
            track.addEventListener('touchstart', function(e) {
                touchStartX = e.touches[0].pageX;
                touchStartScroll = track.scrollLeft;
                track.classList.add('is-dragging');
            }, { passive: true });
            track.addEventListener('touchmove', function(e) {
                track.scrollLeft = touchStartScroll - (e.touches[0].pageX - touchStartX);
            }, { passive: true });
            track.addEventListener('touchend', function() {
                track.classList.remove('is-dragging');
            }, { passive: true });

            // --- Initial position (after image loads) ---
            var img = track.querySelector('.pd-image');
            function setInitialPosition() {
                var maxScroll = track.scrollWidth - track.clientWidth;
                if (initialPosition === 'center') {
                    track.scrollLeft = maxScroll / 2;
                } else if (initialPosition === 'right') {
                    track.scrollLeft = maxScroll;
                }
                updateArrows();
            }
            if (img && !img.complete) {
                img.addEventListener('load', setInitialPosition);
            } else {
                setInitialPosition();
            }

            // --- Auto-scroll (requestAnimationFrame) ---
            if (autoScroll) {
                var rafId = null, lastTime = null, isPaused = false;
                function tick(timestamp) {
                    if (isPaused) { lastTime = null; rafId = requestAnimationFrame(tick); return; }
                    if (lastTime === null) lastTime = timestamp;
                    var dt = timestamp - lastTime;
                    lastTime = timestamp;
                    track.classList.add('is-auto-scrolling');
                    track.scrollLeft += (autoScrollSpeed * dt) / 1000;
                    if (track.scrollLeft >= track.scrollWidth - track.clientWidth - 1) {
                        track.scrollLeft = 0;
                    }
                    rafId = requestAnimationFrame(tick);
                }
                rafId = requestAnimationFrame(tick);
                self._panoramaRAFs.push(rafId);
                if (pauseOnHover) {
                    el.addEventListener('mouseenter', function() { isPaused = true; });
                    el.addEventListener('mouseleave', function() { isPaused = false; });
                }
            }
        },

        cleanupPanoramaDisplays: function() {
            this._panoramaRAFs.forEach(function(id) { cancelAnimationFrame(id); });
            this._panoramaRAFs = [];
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
            this.cleanupCountdowns();
            this.cleanupTickers();
            this.cleanupPanoramaDisplays();
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
