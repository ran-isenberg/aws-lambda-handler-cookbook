// Mermaid diagram zoom functionality
(function () {
    // Create overlay element
    function createOverlay() {
        if (document.querySelector('.mermaid-overlay')) return;
        const overlay = document.createElement('div');
        overlay.className = 'mermaid-overlay';
        document.body.appendChild(overlay);

        overlay.addEventListener('click', function () {
            closeZoom();
        });
    }

    function closeZoom() {
        document.querySelectorAll('.mermaid.zoomed, pre.mermaid.zoomed').forEach(function (diagram) {
            diagram.classList.remove('zoomed');
        });
        const overlay = document.querySelector('.mermaid-overlay');
        if (overlay) overlay.classList.remove('active');
    }

    // Use event delegation on document body
    document.addEventListener('click', function (e) {
        const mermaidDiv = e.target.closest('.mermaid, pre.mermaid');
        if (mermaidDiv) {
            e.preventDefault();
            e.stopPropagation();

            const overlay = document.querySelector('.mermaid-overlay');
            if (mermaidDiv.classList.contains('zoomed')) {
                mermaidDiv.classList.remove('zoomed');
                if (overlay) overlay.classList.remove('active');
            } else {
                // Close any other zoomed diagrams first
                closeZoom();
                mermaidDiv.classList.add('zoomed');
                if (overlay) overlay.classList.add('active');
            }
        }
    });

    // Close on escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeZoom();
        }
    });

    // Create overlay when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createOverlay);
    } else {
        createOverlay();
    }

    // Re-create overlay after MkDocs Material navigation
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function () {
            createOverlay();
        });
    }
})();

// External links open in new tab
(function () {
    function setupExternalLinks() {
        document.querySelectorAll('a[href^="http"]').forEach(function (link) {
            if (!link.hostname.includes(window.location.hostname)) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupExternalLinks);
    } else {
        setupExternalLinks();
    }

    // Re-setup after MkDocs Material navigation
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function () {
            setTimeout(setupExternalLinks, 100);
        });
    }
})();
