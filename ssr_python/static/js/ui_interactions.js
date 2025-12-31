document.addEventListener('DOMContentLoaded', () => {
    const sidebarNavItems = Array.from(document.querySelectorAll('.sidebar-nav-item'));
    const sidebarPanels = Array.from(document.querySelectorAll('.sidebar-panel'));
    const resizer = document.getElementById('resizer');
    const editor = document.getElementById('codeEditor');
    const sidebarResizer = document.getElementById('sidebarResizer');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarNavItems.length > 0 && sidebarPanels.length > 0) {
        const activateNavItem = targetId => {
            sidebarNavItems.forEach(navItem => {
                const isActive = navItem.dataset.target === targetId;
                navItem.classList.toggle('active', isActive);
                navItem.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });

            sidebarPanels.forEach(panel => {
                const isActive = panel.id === targetId;
                panel.classList.toggle('active', isActive);
                panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
            });
        };

        sidebarNavItems.forEach(navItem => {
            navItem.addEventListener('click', () => {
                const targetId = navItem.dataset.target;
                if (targetId) {
                    activateNavItem(targetId);
                }
            });
        });
    }

    if (resizer && editor) {
        initializeResizer(resizer, editor);
    }

    if (sidebarResizer && sidebar) {
        initializeSidebarResizer(sidebarResizer, sidebar);
    }
});


function initializeSidebarResizer(sidebarResizer, sidebar) {
    let isResizing = false;
    let initialX;
    let initialWidth;

    const minWidth = 250;
    const maxWidth = 500;

    const appContainer = document.getElementById('appContainer');

    const storedWidth = localStorage.getItem('sidebarWidth');
    if (storedWidth) {
        appContainer.style.setProperty('--sidebar-width', `${storedWidth}px`);
    }

    const startResizing = (e) => {
        e.stopPropagation(); // Prevent event bubbling
        isResizing = true;
        initialX = e.clientX;
        initialWidth = sidebar.offsetWidth;
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResizing);
        document.body.style.cursor = 'ew-resize'; 
        sidebar.style.userSelect = 'none'; 
        sidebar.style.pointerEvents = 'none'; 
    };

    const resize = (e) => {
        if (!isResizing) return;
        const dx = e.clientX - initialX;
        let newWidth = initialWidth + dx;

        if (newWidth < minWidth) {
            newWidth = minWidth;
        } else if (newWidth > maxWidth) {
            newWidth = maxWidth;
        }

        appContainer.style.setProperty('--sidebar-width', `${newWidth}px`);
    };

    const stopResizing = () => {
        isResizing = false;
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResizing);
        document.body.style.cursor = ''; 
        sidebar.style.userSelect = ''; 
        sidebar.style.pointerEvents = ''; 
        localStorage.setItem('sidebarWidth', sidebar.offsetWidth);
    };

    sidebarResizer.addEventListener('mousedown', startResizing);
}

function initializeResizer(resizer, editor) {
    let isResizing = false; // Add isResizing flag
    let initialEditorHeight = 0;
    let initialMouseY = 0;

    const handleMouseMove = event => {
        if (!isResizing) return; // Add guard clause
        const deltaY = event.clientY - initialMouseY;
        const newHeight = initialEditorHeight + deltaY;
        if (newHeight > 120) {
            editor.style.height = `${newHeight}px`;
        }
    };

    const handleMouseUp = () => {
        isResizing = false; // Unset flag
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
    };

    resizer.addEventListener('mousedown', event => {
        event.preventDefault();
        event.stopPropagation(); // Prevent event bubbling
        isResizing = true; // Set flag
        initialEditorHeight = editor.clientHeight;
        initialMouseY = event.clientY;
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
    });
}
