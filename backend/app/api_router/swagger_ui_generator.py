from __future__ import annotations

class SwaggerUIGenerator:
    """Handles Swagger UI HTML generation for the API documentation."""

    def __init__(self) -> None:
        pass

    def generate_swagger_ui(self) -> str:
        """Generate Swagger UI HTML page with service filtering"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Music Metadata API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin:0; background: #fafafa; }}
        
        /* Hide the default Swagger UI header */
        .swagger-ui .topbar {{
            display: none !important;
        }}
        
        /* Custom filter bar - positioned above Swagger UI content */
        .custom-filter-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: #1b1b1b;
            color: white;
            padding: 10px 20px;
            border-bottom: 2px solid #4990e2;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .filter-content {{
            display: flex;
            align-items: center;
            gap: 15px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .filter-label {{
            font-weight: bold;
            color: #4990e2;
            white-space: nowrap;
        }}
        
        .filter-input {{
            flex: 1;
            max-width: 400px;
            padding: 8px 12px;
            border: 1px solid #444;
            border-radius: 4px;
            background: #2d2d2d;
            color: white;
            font-size: 14px;
        }}
        
        .filter-input:focus {{
            outline: none;
            border-color: #4990e2;
            box-shadow: 0 0 0 2px rgba(73, 144, 226, 0.2);
        }}
        
        .filter-input::placeholder {{
            color: #888;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            background: #4990e2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }}
        
        .filter-btn:hover {{
            background: #357abd;
        }}
        
        .filter-btn.secondary {{
            background: #666;
        }}
        
        .filter-btn.secondary:hover {{
            background: #555;
        }}
        
        .quick-filters {{
            display: flex;
            gap: 8px;
        }}
        
        .quick-filter-btn {{
            padding: 6px 12px;
            background: #333;
            border: 1px solid #555;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
            color: #ccc;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        
        .quick-filter-btn:hover {{
            background: #4990e2;
            color: white;
            border-color: #4990e2;
        }}
        
        .quick-filter-btn.active {{
            background: #4990e2;
            color: white;
            border-color: #4990e2;
            box-shadow: 0 0 0 2px rgba(73, 144, 226, 0.3);
        }}
        
        .current-filter {{
            padding: 6px 12px;
            background: #2d4a6b;
            border: 1px solid #4990e2;
            border-radius: 15px;
            color: #b3d9ff;
            font-size: 12px;
            white-space: nowrap;
        }}
        
        /* Add top margin to Swagger UI to account for fixed filter bar */
        #swagger-ui {{
            margin-top: 70px;
        }}
    </style>
</head>
<body>
    <div class="custom-filter-bar">
        <div class="filter-content">
            <span class="filter-label">🎯 Filter Services:</span>
            
            <input type="text" 
                   class="filter-input" 
                   id="serviceFilter" 
                   placeholder="e.g., chat,artists,albums"
                   value="">
            
            <button class="filter-btn" onclick="applyFilter()">Apply</button>
            <button class="filter-btn secondary" onclick="clearFilter()">Clear</button>
            
            <div class="quick-filters" id="quickFilters">
                <!-- Dynamic quick filter buttons will be generated here -->
            </div>
            
            <div class="current-filter" id="currentFilter" style="display: none;">
                <span id="filterText"></span>
            </div>
        </div>
    </div>
    
    <div id="swagger-ui"></div>
    
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    
    <script>
        let currentSwaggerUI = null;
        let currentFilter = '';
        
        // Load initial Swagger UI
        window.onload = function() {{
            loadSwaggerUI();
        }};
        
        function loadSwaggerUI(serviceFilter = '') {{
            const url = serviceFilter ? `/api/openapi.json?services=${{serviceFilter}}` : '/api/openapi.json';
            console.log('Loading Swagger UI with URL:', url);
            
            // Destroy existing instance if it exists
            if (currentSwaggerUI) {{
                currentSwaggerUI.destroy();
            }}
            
            // Create new instance
            currentSwaggerUI = SwaggerUIBundle({{
                url: url,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                onComplete: function() {{
                    console.log('✅ Swagger UI loaded with filter:', serviceFilter);
                    updateFilterDisplay(serviceFilter);
                    
                    // Refresh quick filter buttons to show current state
                    if (serviceFilter) {{
                        highlightActiveFilter(serviceFilter);
                    }} else {{
                        clearActiveFilterHighlights();
                    }}
                }},
                onFailure: function(data) {{
                    console.error('❌ Failed to load Swagger UI:', data);
                }}
            }});
        }}
        
        function applyFilter() {{
            const filterValue = document.getElementById('serviceFilter').value.trim();
            if (filterValue) {{
                currentFilter = filterValue;
                console.log('Applying filter:', filterValue);
                loadSwaggerUI(filterValue);
                localStorage.setItem('swaggerServiceFilter', filterValue);
            }}
        }}
        
        function clearFilter() {{
            document.getElementById('serviceFilter').value = '';
            currentFilter = '';
            console.log('Clearing filter');
            loadSwaggerUI();
            localStorage.removeItem('swaggerServiceFilter');
        }}
        
        function quickFilter(services) {{
            document.getElementById('serviceFilter').value = services;
            currentFilter = services;
            console.log('Quick filter:', services);
            loadSwaggerUI(services);
            localStorage.setItem('swaggerServiceFilter', services);
        }}
        
        function updateFilterDisplay(filter) {{
            const filterDiv = document.getElementById('currentFilter');
            const filterText = document.getElementById('filterText');
            
            if (filter) {{
                filterText.textContent = `Active: ${{filter}}`;
                filterDiv.style.display = 'block';
            }} else {{
                filterDiv.style.display = 'none';
            }}
        }}
        
        // Load saved filter from localStorage on page load
        document.addEventListener('DOMContentLoaded', function() {{
            const savedFilter = localStorage.getItem('swaggerServiceFilter');
            if (savedFilter) {{
                document.getElementById('serviceFilter').value = savedFilter;
                currentFilter = savedFilter;
                console.log('Loading saved filter:', savedFilter);
                setTimeout(() => loadSwaggerUI(savedFilter), 100);
            }}
            
            // Generate dynamic quick filter buttons
            generateQuickFilterButtons();
        }});
        
        // Generate quick filter buttons based on available services
        async function generateQuickFilterButtons() {{
            try {{
                // Get the list of available services from the OpenAPI spec
                const response = await fetch('/api/openapi.json');
                const spec = await response.json();
                
                if (spec.tags && spec.tags.length > 0) {{
                    const quickFiltersContainer = document.getElementById('quickFilters');
                    quickFiltersContainer.innerHTML = '';
                    
                    // Get individual services
                    const serviceGroups = groupServicesByCategory(spec.tags);
                    
                    // Create buttons for each service
                    serviceGroups.forEach(group => {{
                        const button = document.createElement('div');
                        button.className = 'quick-filter-btn';
                        button.onclick = () => quickFilter(group.services.join(','));
                        button.textContent = group.name;
                        button.setAttribute('data-filter', group.services.join(','));
                        quickFiltersContainer.appendChild(button);
                    }});
                    
                    console.log('✅ Generated quick filter buttons for services:', serviceGroups);
                }}
            }} catch (error) {{
                console.error('❌ Failed to generate quick filter buttons:', error);
                // Fallback to basic buttons if API call fails
                generateFallbackButtons();
            }}
        }}
        
        // Create dynamic service groups based on actual services
        function groupServicesByCategory(tags) {{
            // Just return individual services - no hardcoded categories
            return tags.map(tag => ({{
                name: tag.name,
                services: [tag.name]
            }}));
        }}
        
        // Fallback if dynamic generation fails
        function generateFallbackButtons() {{
            const quickFiltersContainer = document.getElementById('quickFilters');
            quickFiltersContainer.innerHTML = '<div style="color: #999; font-style: italic;">Loading services...</div>';
        }}
        
        // Highlight the active filter button
        function highlightActiveFilter(activeFilter) {{
            const buttons = document.querySelectorAll('.quick-filter-btn');
            buttons.forEach(button => {{
                button.classList.remove('active');
                // Check if this button's filter matches the active filter
                const buttonFilter = button.getAttribute('data-filter');
                if (buttonFilter && buttonFilter === activeFilter) {{
                    button.classList.add('active');
                }}
            }});
        }}
        
        // Clear all active filter highlights
        function clearActiveFilterHighlights() {{
            const buttons = document.querySelectorAll('.quick-filter-btn');
            buttons.forEach(button => {{
                button.classList.remove('active');
            }});
        }}
        
        // Handle Enter key in filter input
        document.getElementById('serviceFilter').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                applyFilter();
            }}
        }});
    </script>
</body>
</html>
        """
