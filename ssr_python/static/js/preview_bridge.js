/**
 * Preview Bridge Script
 *
 * This script runs inside the preview iframe and handles:
 * - Receiving content updates from parent via postMessage
 * - Relaying click events to parent for component selection
 * - Managing selection highlighting
 * - Initializing interactive components (carousel, accordion, tabs)
 *
 * SECURITY: All postMessage communication validates origin to prevent XSS attacks.
 */

(function() {
    'use strict';

    // Security: Get trusted origin (same as parent since we're same-origin)
    const TRUSTED_ORIGIN = window.location.origin;

    // Allowed message types (whitelist)
    const ALLOWED_MESSAGE_TYPES = {
        UPDATE_CONTENT: 'UPDATE_CONTENT',
        SET_SELECTION: 'SET_SELECTION',
        CLEAR_SELECTION: 'CLEAR_SELECTION'
    };

    // Current selection state
    let currentSelection = null;

    /**
     * Validate component ID format to prevent injection
     * Format: comp_0, comp_0_components_1, comp_0_columns_0_components_2
     */
    function isValidComponentId(id) {
        return typeof id === 'string' && /^comp_[\d_a-z]+$/.test(id);
    }

    /**
     * Handle incoming messages from parent
     */
    function handleMessage(event) {
        // SECURITY: Validate origin first
        if (event.origin !== TRUSTED_ORIGIN) {
            console.warn('[Preview Bridge] Blocked message from untrusted origin:', event.origin);
            return;
        }

        // Validate message structure
        if (!event.data || typeof event.data.type !== 'string') {
            console.warn('[Preview Bridge] Invalid message format');
            return;
        }

        // Process only known message types
        switch (event.data.type) {
            case ALLOWED_MESSAGE_TYPES.UPDATE_CONTENT:
                handleUpdateContent(event.data);
                break;
            case ALLOWED_MESSAGE_TYPES.SET_SELECTION:
                handleSetSelection(event.data);
                break;
            case ALLOWED_MESSAGE_TYPES.CLEAR_SELECTION:
                handleClearSelection();
                break;
            default:
                console.warn('[Preview Bridge] Unknown message type:', event.data.type);
        }
    }

    /**
     * Handle content update from parent
     */
    function handleUpdateContent(data) {
        const container = document.getElementById('preview-content');
        if (!container) {
            console.error('[Preview Bridge] Preview content container not found');
            return;
        }

        // Validate html is a string
        if (typeof data.html !== 'string') {
            console.warn('[Preview Bridge] Invalid HTML content');
            return;
        }

        // Clean up existing titlebar clones before updating
        document.querySelectorAll('.titlebar-clone').forEach(clone => {
            clone.remove();
        });

        // Update content (HTML comes from trusted Flask server)
        container.innerHTML = data.html;

        // Clear any previous selection
        currentSelection = null;

        // Notify parent of available components
        notifyParentOfComponents();

        // Initialize interactive components
        initializeInteractiveComponents();
    }

    /**
     * Handle selection request from parent
     */
    function handleSetSelection(data) {
        if (!data.componentId) return;

        // Validate component ID format
        if (!isValidComponentId(data.componentId)) {
            console.warn('[Preview Bridge] Invalid component ID format:', data.componentId);
            return;
        }

        highlightComponent(data.componentId);
    }

    /**
     * Handle clear selection request from parent
     */
    function handleClearSelection() {
        clearHighlight();
    }

    /**
     * Highlight a component by adding 'selected' class
     */
    function highlightComponent(componentId) {
        clearHighlight();

        const element = document.querySelector(`[data-component-id="${componentId}"]`);
        if (element) {
            element.classList.add('selected');
            currentSelection = element;

            // Scroll into view smoothly
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /**
     * Clear current selection highlight
     */
    function clearHighlight() {
        if (currentSelection) {
            currentSelection.classList.remove('selected');
            currentSelection = null;
        }

        // Also clear any other selected elements (in case of stale state)
        document.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }

    /**
     * Notify parent of all available component IDs
     */
    function notifyParentOfComponents() {
        const components = document.querySelectorAll('[data-component-id]');
        const componentIds = Array.from(components).map(el => el.dataset.componentId);

        console.log('[Preview Bridge] Components in DOM:', componentIds);

        // SECURITY: Always specify exact origin
        window.parent.postMessage({
            type: 'COMPONENTS_READY',
            componentIds: componentIds
        }, TRUSTED_ORIGIN);
    }

    /**
     * Handle click events and relay to parent
     */
    function handleClick(event) {
        console.log('[Preview Bridge] Click event on:', event.target);
        const target = event.target.closest('[data-component-id]');
        console.log('[Preview Bridge] Closest component:', target);

        if (target) {
            const componentId = target.dataset.componentId;
            console.log('[Preview Bridge] Component ID:', componentId);

            // Validate component ID before sending
            if (isValidComponentId(componentId)) {
                console.log('[Preview Bridge] Sending COMPONENT_CLICKED to parent');
                // SECURITY: Always specify exact origin
                window.parent.postMessage({
                    type: 'COMPONENT_CLICKED',
                    componentId: componentId
                }, TRUSTED_ORIGIN);
            } else {
                console.warn('[Preview Bridge] Invalid component ID format:', componentId);
            }
        } else {
            console.log('[Preview Bridge] No component found at click target');
        }
    }

    /**
     * Initialize interactive components (carousel, accordion, tabs, titlebar)
     */
    function initializeInteractiveComponents() {
        // Initialize carousels
        document.querySelectorAll('.carousel').forEach(carousel => {
            initializeCarousel(carousel);
        });

        // Initialize accordions
        document.querySelectorAll('.accordion-container').forEach(accordion => {
            initializeAccordion(accordion);
        });

        // Initialize tabs
        document.querySelectorAll('.tabs').forEach(tabs => {
            initializeTabs(tabs);
        });

        // Initialize titlebars
        document.querySelectorAll('.titlebar').forEach(titlebar => {
            initializeTitlebar(titlebar);
        });
    }

    /**
     * Initialize carousel functionality
     */
    function initializeCarousel(carouselElement) {
        if (!carouselElement || carouselElement.dataset.initialized === 'true') return;
        carouselElement.dataset.initialized = 'true';

        const slidesContainer = carouselElement.querySelector('.carousel-slides');
        const slides = carouselElement.querySelectorAll('.carousel-slide');
        const prevButton = carouselElement.querySelector('.prev');
        const nextButton = carouselElement.querySelector('.next');
        const dots = carouselElement.querySelectorAll('.carousel-dots span');
        const totalSlides = slides.length;

        if (totalSlides < 2) return;

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
            clearInterval(autoplayInterval);
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
                currentIndex = parseInt(e.target.dataset.slideTo, 10);
                updateCarousel();
                startAutoplay();
            });
        });

        carouselElement.addEventListener('mouseenter', stopAutoplay);
        carouselElement.addEventListener('mouseleave', startAutoplay);

        updateCarousel();
        startAutoplay();
    }

    /**
     * Initialize accordion functionality
     */
    function initializeAccordion(accordionContainer) {
        if (!accordionContainer || accordionContainer.dataset.initialized === 'true') return;
        accordionContainer.dataset.initialized = 'true';

        const allowMultiple = accordionContainer.dataset.allowMultiple === 'true';

        if (!allowMultiple) {
            const details = accordionContainer.querySelectorAll('details.accordion');

            details.forEach(detail => {
                detail.addEventListener('toggle', () => {
                    if (detail.open) {
                        details.forEach(other => {
                            if (other !== detail && other.open) {
                                other.open = false;
                            }
                        });
                    }
                });
            });
        }
    }

    /**
     * Initialize tabs functionality
     */
    function initializeTabs(tabsContainer) {
        if (!tabsContainer || tabsContainer.dataset.initialized === 'true') return;
        tabsContainer.dataset.initialized = 'true';

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
    }

    /**
     * Initialize titlebar functionality with clone for sticky behavior
     */
    function initializeTitlebar(titlebarElement) {
        if (!titlebarElement || titlebarElement.dataset.initialized === 'true') return;
        titlebarElement.dataset.initialized = 'true';

        // Find the page component parent to insert clone
        const pageComponent = titlebarElement.closest('.page');

        // Create clone for sticky behavior
        const clone = titlebarElement.cloneNode(true);
        clone.classList.add('titlebar-clone');
        clone.classList.remove('chrome-target'); // Don't make clone selectable
        clone.removeAttribute('data-component-id'); // Remove component ID from clone
        clone.dataset.initialized = 'true'; // Mark as initialized
        clone.style.cssText = titlebarElement.style.cssText; // Copy inline styles

        // Insert clone at the beginning of page component (or body if no page)
        if (pageComponent) {
            pageComponent.insertAdjacentElement('afterbegin', clone);
        } else {
            document.body.insertAdjacentElement('afterbegin', clone);
        }

        // Setup mobile menu toggle for original titlebar
        const mobileMenuButton = titlebarElement.querySelector('.mobile-menu-button');
        const navLinks = titlebarElement.querySelector('.titlebar-nav');

        if (mobileMenuButton && navLinks) {
            mobileMenuButton.addEventListener('click', (e) => {
                e.stopPropagation();
                navLinks.classList.toggle('active');
            });
        }

        // Setup mobile menu toggle for cloned titlebar
        const cloneMobileMenuButton = clone.querySelector('.mobile-menu-button');
        const cloneNavLinks = clone.querySelector('.titlebar-nav');

        if (cloneMobileMenuButton && cloneNavLinks) {
            cloneMobileMenuButton.addEventListener('click', (e) => {
                e.stopPropagation();
                cloneNavLinks.classList.toggle('active');
            });
        }

        // Handle scroll effect - show clone when original out of view
        function handleScroll() {
            const scrolled = window.scrollY > 50;
            titlebarElement.classList.toggle('scrolled', scrolled);
            clone.classList.toggle('scrolled', scrolled);

            // Check if original titlebar is out of view
            const rect = titlebarElement.getBoundingClientRect();
            const isOutOfView = rect.bottom < 0;

            // Show/hide clone based on original visibility
            clone.classList.toggle('visible', isOutOfView);
        }

        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
    }

    // Handshake state - track if parent acknowledged our IFRAME_READY
    let readyAcknowledged = false;

    /**
     * Handle acknowledgment message from parent
     * This is separate from the main message handler to ensure it's always processed
     */
    function handleAcknowledgment(event) {
        // SECURITY: Validate origin
        if (event.origin !== TRUSTED_ORIGIN) return;

        if (event.data && event.data.type === 'IFRAME_READY_ACK') {
            readyAcknowledged = true;
            console.log('[Preview Bridge] Ready acknowledged by parent');
        }
    }

    /**
     * Send IFRAME_READY with retry until acknowledged
     * This handles the race condition where the iframe loads before the parent's
     * message listener is set up (module scripts are deferred)
     */
    function sendReadySignal() {
        if (readyAcknowledged) return;

        // SECURITY: Always specify exact origin
        window.parent.postMessage({
            type: 'IFRAME_READY'
        }, TRUSTED_ORIGIN);

        console.log('[Preview Bridge] Sent IFRAME_READY, waiting for acknowledgment...');

        // Retry after 100ms if not acknowledged (max ~30 retries = 3 seconds)
        setTimeout(() => {
            if (!readyAcknowledged) {
                sendReadySignal();
            }
        }, 100);
    }

    // Set up event listeners
    window.addEventListener('message', handleMessage);
    window.addEventListener('message', handleAcknowledgment);
    document.addEventListener('click', handleClick);

    // Start handshake with retry pattern
    sendReadySignal();

    console.log('[Preview Bridge] Initialized with trusted origin:', TRUSTED_ORIGIN);
})();
