// Swagger UI initialization - loads on the swagger page
(function () {
    var loaded = false;

    function loadSwaggerUI() {
        var container = document.getElementById('swagger-ui');
        if (!container) return;
        if (loaded && container.children.length > 0) return;

        var script = document.createElement('script');
        script.src = 'https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js';
        script.onload = function () {
            SwaggerUIBundle({
                url: '../openapi.json',
                dom_id: '#swagger-ui',
                presets: [SwaggerUIBundle.presets.apis],
                layout: 'BaseLayout',
            });
            loaded = true;
        };
        document.head.appendChild(script);
    }

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadSwaggerUI);
    } else {
        loadSwaggerUI();
    }

    // Re-run after instant navigation
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function () {
            loaded = false;
            loadSwaggerUI();
        });
    }
})();
