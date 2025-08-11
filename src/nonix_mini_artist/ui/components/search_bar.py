"""
Search bar component for searching across entities
"""
from nicegui import ui
from typing import Callable, List, Dict, Any, Optional

class SearchBar:
    """Reusable search bar component"""
    
    def __init__(self, 
                 placeholder: str = "Search...",
                 on_search: Optional[Callable] = None,
                 search_types: List[str] = None,
                 width: str = "w-full"):
        """Initialize search bar"""
        self.placeholder = placeholder
        self.on_search = on_search
        self.search_types = search_types or ["all"]
        self.width = width
        self.search_input = None
        self.type_selector = None
        self._build_search_bar()
    
    def _build_search_bar(self):
        """Build the search bar structure"""
        with ui.row().classes(f'{self.width} gap-2 items-center'):
            # Search type selector (if multiple types)
            if len(self.search_types) > 1:
                self.type_selector = ui.select(
                    options=self.search_types,
                    value=self.search_types[0]
                ).classes('w-32')
            
            # Search input
            self.search_input = ui.input(
                value='',
                placeholder=self.placeholder,
                on_change=self._handle_search
            ).classes('flex-1')
            
            # Search button
            ui.button('🔍', on_click=self._handle_search).classes('px-3 py-2 bg-blue-500 text-white hover:bg-blue-600')
    
    def _handle_search(self, event=None):
        """Handle search input or button click"""
        if self.on_search:
            search_text = self.search_input.value or ""
            search_type = self.type_selector.value if self.type_selector else "all"
            self.on_search(search_text, search_type)
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_input.value or ""
    
    def get_search_type(self) -> str:
        """Get current search type"""
        return self.type_selector.value if self.type_selector else "all"
    
    def set_search_text(self, text: str):
        """Set search text"""
        if self.search_input:
            self.search_input.value = text
    
    def clear_search(self):
        """Clear search input"""
        if self.search_input:
            self.search_input.value = ""
            self._handle_search()

class GlobalSearchBar(SearchBar):
    """Global search bar for searching across all entities"""
    
    def __init__(self, 
                 on_search: Callable,
                 placeholder: str = "Search artists, albums, tracks...",
                 width: str = "w-full"):
        """Initialize global search bar"""
        super().__init__(
            placeholder=placeholder,
            on_search=on_search,
            search_types=["all", "artists", "albums", "tracks", "styles"],
            width=width
        )

class EntitySearchBar(SearchBar):
    """Search bar for a specific entity type"""
    
    def __init__(self, 
                 entity_type: str,
                 on_search: Callable,
                 placeholder: str = None,
                 width: str = "w-full"):
        """Initialize entity-specific search bar"""
        if placeholder is None:
            placeholder = f"Search {entity_type}..."
        
        super().__init__(
            placeholder=placeholder,
            on_search=on_search,
            search_types=[entity_type],
            width=width
        )
