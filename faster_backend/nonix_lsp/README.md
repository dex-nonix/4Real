# LSP Instance Manager

A clean, professional Python class for managing Language Server Protocol (LSP) server instances.

## Installation

```bash
pip install python-lsp-server[all]
pip install sansio-lsp-client
```

## Quick Start

```python
from nonix_lsp.lsp_instance import LSPInstance

# Create LSP instance
config = {
    "port": 19998,
    "workspace_path": "/path/to/your/project"
}
lsp = LSPInstance(config)

# Start and initialize
lsp.start()
lsp.initialize("/path/to/your/project")

# Use organized API
lsp.file.open("main.py")
definition = lsp.code.get_definition("main.py", 10, 5)
references = lsp.code.find_references("main.py", 10, 5)
lsp.file.close("main.py")

# Clean up
lsp.stop()
```

## Architecture

The LSP implementation is organized into modular components for better maintainability:

### Main Instance (`lsp_instance.py`)
- Core LSP server lifecycle management
- Component coordination
- Server initialization and configuration

### Component Modules (`components/`)

#### `file_manager.py`
- File operations: open, close, change, save
- `lsp.file.open()`, `lsp.file.close()`, etc.

#### `code_intelligence.py`
- Code intelligence: definitions, references, hover, completions
- `lsp.code.get_definition()`, `lsp.code.find_references()`, etc.

#### `navigation.py`
- Navigation: go to declaration, type definition, implementation
- Document features: highlights, folding, selection ranges
- `lsp.navigation.go_to_declaration()`, etc.

#### `formatting.py`
- Code formatting: format document, format range
- Code actions: get available actions
- `lsp.formatting.format_document()`, etc.

#### `refactoring.py`
- Refactoring operations: rename, prepare rename
- `lsp.refactoring.rename_symbol()`, etc.

#### `advanced.py`
- Advanced LSP features: call hierarchy, semantic tokens, inlay hints
- `lsp.advanced.get_call_hierarchy()`, etc.

Each component maintains a reference to the main LSP instance and delegates core functionality through it.

## Features

### Lifecycle Management
- `start()` - Start LSP server process
- `stop()` - Stop server and cleanup
- `initialize(workspace_path)` - Initialize with workspace

### File Operations
- `lsp.file.open(file_path, content=None)` - Open file in LSP server
- `lsp.file.close(file_path)` - Close file
- `lsp.file.change(file_path, changes)` - Notify of file changes
- `lsp.file.save(file_path)` - Notify of file save

### Code Intelligence
- `lsp.code.get_definition(file_path, line, char)` - Find symbol definition
- `lsp.code.find_references(file_path, line, char)` - Find all references
- `lsp.code.get_hover_info(file_path, line, char)` - Get hover documentation
- `lsp.code.get_completions(file_path, line, char)` - Get autocomplete suggestions
- `lsp.code.get_signature_help(file_path, line, char)` - Get function signature help

### Navigation
- `lsp.navigation.go_to_declaration(file_path, line, char)` - Jump to declaration
- `lsp.navigation.go_to_type_definition(file_path, line, char)` - Jump to type definition
- `lsp.navigation.go_to_implementation(file_path, line, char)` - Jump to implementation

### Document Features
- `lsp.code.get_document_symbols(file_path)` - List symbols in file
- `lsp.code.get_workspace_symbols(query)` - Search workspace symbols
- `lsp.navigation.get_document_highlights(file_path, line, char)` - Highlight related symbols
- `lsp.navigation.get_folding_ranges(file_path)` - Get code folding regions
- `lsp.navigation.get_selection_ranges(file_path, positions)` - Get selection ranges

### Code Actions & Refactoring
- `lsp.formatting.get_code_actions(file_path, range_start, range_end)` - Get available code actions
- `lsp.refactoring.rename_symbol(file_path, line, char, new_name)` - Rename symbol
- `lsp.refactoring.prepare_rename(file_path, line, char)` - Check if rename is possible

### Formatting
- `lsp.formatting.format_document(file_path, options=None)` - Format entire file
- `lsp.formatting.format_range(file_path, range_start, range_end, options=None)` - Format range

### Advanced Features
- `lsp.advanced.get_call_hierarchy(file_path, line, char)` - Get call hierarchy
- `lsp.advanced.get_semantic_tokens(file_path)` - Get semantic highlighting
- `lsp.advanced.get_inlay_hints(file_path, range_start=None, range_end=None)` - Get inline hints
- `lsp.advanced.get_inline_completions(file_path, line, char, context=None)` - Get inline completions

### Utilities
- `lsp.get_server_capabilities()` - Get server capabilities
- `lsp.is_healthy()` - Check server health

## Error Handling

The class raises specific exceptions:
- `LSPInstanceError` - Base exception for LSP errors
- `LSPInstanceConnectionError` - Connection/server startup failures
- `LSPInstanceTimeoutError` - Request timeout errors

All exceptions are logged before being raised.

## Context Manager Support

```python
with LSPInstance(config) as lsp:
    lsp.initialize("/path/to/project")
    # Use LSP methods...
# Automatically stopped when exiting context
```

## Configuration

Required config parameters:
- `port` - Port number for LSP server
- `workspace_path` - Path to workspace root

Optional config parameters:
- `lsp_cmd` - Command to start LSP server (default: `['pylsp']`)
- `timeout` - Request timeout in seconds (default: 30)
- `log_level` - Logging level (default: 'INFO')
