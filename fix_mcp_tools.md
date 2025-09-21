# MCP Tool Integration Implementation Plan

**WARNING: NEVER USE INLINE IMPORTS**
**WARNING: NEVER USE hasattr**
**WARNING: NEVER CALL TERMINAL OR CONSOLE**

## Overview
Unify all MCP tools (internal registry + external MCP servers) into a single system. LLM gets flat array of structured tools. UI gets grouped-by-namespace data as array.

## Current Issues
- MCP tools from external servers are called separately from internal MCP tools
- LLM only sees internal MCP tools, not external MCP server tools
- UI has separate handling for internal vs external MCP tools
- Two different execution paths

## Target Architecture

### LLM Integration (Backend Task - MAJOR UPDATE REQUIRED)
- **CURRENT**: `agentic_tool_manager.create_langchain_tools()` handles ONLY internal tools
- **PROBLEM**: LLM cannot use external MCP server tools
- **SOLUTION**: Split into 3 functions (same pattern as UI):
  - `create_internal_langchain_tools()` - creates StructuredTool objects for internal tools
  - `create_external_langchain_tools()` - creates StructuredTool objects for external tools using `MultiServerMCPClient`
  - `create_langchain_tools()` - merges both (calls the two above)
- **Input**: `persona_id` and `available_tools_info`
- **Output**: Flat array of `StructuredTool` objects for both internal and external
- **Result**: LLM can now use both internal and external tools seamlessly

### UI Information (Backend Task - New Implementation)
- **PROBLEM**: UI needs grouped tool metadata for display
- **SOLUTION**: `get_tools(persona_id)` - returns array of namespaces with tools
- **Helpers**: `get_internal_tools()` and `get_external_tools()` - different extraction for each type
- **Internal**: Extract parameter info from registered functions (already structured)
- **External**: Extract parameter info from MCP `inputSchema`
- **Output**: `[{namespace: "...", tools: [{name, description, parameters}]}]` for UI display

### Tool Execution (Backend Task - Already Works)
- Routes execution: check internal registry first, then external MCP servers
- Namespaced tool calls: `namespace:function_name` format

### Frontend Task (Almost Perfect)
- Update to consume `/personas/{id}/tools` endpoint
- Display grouped-by-namespace data in expanders/accordions

## Required Changes

### 1. ToolExecutionService - ADD get_tools() method

**File**: `faster_backend/nonix_web_agentic/services/tool_execution_service.py`

**Location**: Add after line 45 (after `list_registry_tools()`)

**Code to Add**:
```python
async def get_tools(self, persona_id: int):
    """Get all tools grouped by namespace for UI display (public method)."""

    # Get grouped data from internal helpers
    internal_namespaces = await self.get_internal_tools(persona_id)
    external_namespaces = await self.get_external_tools(persona_id)

    # Merge the arrays
    all_namespaces = internal_namespaces + external_namespaces

    return all_namespaces

async def get_internal_tools(self, persona_id: int):
    """Get internal tools grouped by namespace (internal helper)."""

    # Get internal tools (already structured with namespace:function_name)
    internal_tools = await self.agentic_tool_manager.list_persona_tools(persona_id)

    # Group internal tools by namespace
    namespace_map = {}
    for tool in internal_tools:
        namespace, function_name = tool['name'].split(':', 1)
        if namespace not in namespace_map:
            namespace_map[namespace] = {
                'namespace': namespace,
                'description': f'{namespace} operations',
                'is_external': False,
                'tools': []
            }
        namespace_map[namespace]['tools'].append({
            'name': function_name,
            'description': tool['description'],
            'parameters': tool['parameters']
        })

    # Return as array of namespaces
    return list(namespace_map.values())

async def get_external_tools(self, persona_id: int):
    """Get external tools grouped by namespace (internal helper)."""

    # Get external tools and group by namespace (server name)
    external_servers = await self.get_external_servers(persona_id)

    namespace_map = {}
    for server in external_servers:
        namespace = server['mcp_server_name']
        if namespace not in namespace_map:
            namespace_map[namespace] = {
                'namespace': namespace,
                'description': f'{namespace} operations',
                'is_external': True,
                'tools': []
            }

        # Enhance tools with full schemas
        for tool in server['tools']:
            full_tool_info = await self.get_tool_schema(server['mcp_server_id'], tool['name'])
            namespace_map[namespace]['tools'].append({
                'name': tool['name'],
                'description': full_tool_info['description'],
                'parameters': full_tool_info['parameters']
            })

    # Return as array of namespaces
    return list(namespace_map.values())

async def get_external_servers(self, persona_id: int):
    """Get external servers for a persona."""
    async with AsyncSessionLocal() as db_session:
        stmt = select(PersonaMCPServer).options(
            joinedload(PersonaMCPServer.mcp_server)
        ).where(PersonaMCPServer.persona_id == persona_id,
               PersonaMCPServer.is_active)
        result = await db_session.execute(stmt)
        links = result.scalars().all()

    out = []
    for link in links:
        tools = await list_mcp_server_tools_by_server_id(link.mcp_server_id)
        out.append({
            'persona_mcp_server_id': link.id,
            'mcp_server_id': link.mcp_server_id,
            'mcp_server_name': link.mcp_server.name if link.mcp_server else None,
            'tools': tools
        })
    return out

async def get_tool_schema(self, server_id: int, tool_name: str) -> Dict[str, Any]:
    """Get complete tool schema including parameters from MCP server."""
    return await get_external_tool_schema(server_id, tool_name)
```

### 2. ToolExecutionService - MODIFY execute_tool_for_persona() EXECUTION LOGIC

**File**: `faster_backend/nonix_web_agentic/services/tool_execution_service.py`

**Location**: Replace lines 71-76 (the tool execution logic)

**Current Code** (lines 71-76):
```python
# Execute the actual tool using the agentic tool manager
tool_result = await self.agentic_tool_manager.execute_tool(
    persona_id=persona_id,
    tool_name=tool_name,
    parameters=parameters
)
```

**Replace With**:
```python
# Route execution: check internal first, then external
if self.agentic_tool_manager.get(tool_name) is not None:
    # Internal tool - execute from registry
    tool_result = await self.agentic_tool_manager.execute_tool(
        persona_id=persona_id,
        tool_name=tool_name,
        parameters=parameters
    )
else:
    # External tool - execute via external server (namespace:name)
    tool_result = await self.execute_external_tool(
        persona_id, tool_name, parameters
    )
```

**File**: `faster_backend/nonix_web_agentic/utils/mcp_client.py`

**Location**: Add after existing functions

**Code to Add**:
```python
async def get_external_tool_schema(server_id: int, tool_name: str) -> Dict[str, Any]:
    """Get complete tool schema with parameters from MCP server."""
    server = await _load_server(server_id)
    if not server:
        return {'name': tool_name, 'description': '', 'parameters': []}

    server_config = {
        "command": server.command,
        "args": server.args_json or [],
        "env": server.env_json or {},
        "transport": "stdio"
    }

    client = MultiServerMCPClient({f"server_{server_id}": server_config})

    tools = await client.get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)

    if not tool:
        return {'name': tool_name, 'description': '', 'parameters': []}

    # Extract parameters from tool schema (all MCP tools are structured)
    parameters = []
    if tool.inputSchema and 'properties' in tool.inputSchema:
        schema = tool.inputSchema
        for param_name, param_schema in schema['properties'].items():
            parameters.append({
                'name': param_name,
                'type': param_schema.get('type', 'string'),
                'required': param_name in schema.get('required', []),
                'default': param_schema.get('default'),
                'description': param_schema.get('description', '')
            })

    return {
        'name': tool.name,
        'description': tool.description or '',
        'parameters': parameters
    }
```

### 3. ToolExecutionService.execute_external_tool() - NEW METHOD

**File**: `faster_backend/nonix_web_agentic/services/tool_execution_service.py`

**Location**: Add after line 161 (end of file)

**Code to Add**:
```python
async def execute_external_tool(self, persona_id: int, tool_name: str, parameters: Dict[str, Any]):
    """Execute external MCP server tool by parsing namespace from full name (namespace:name)."""

    if ':' not in tool_name:
        raise ValueError('Tool name must have namespace: server_name:tool_name')

    server_name, actual_tool_name = tool_name.split(':', 1)

    # Find MCP server by name for this persona (explicit join for filtering)
    async with AsyncSessionLocal() as db_session:
        stmt = (
            select(PersonaMCPServer)
            .join(MCPServer, PersonaMCPServer.mcp_server)
            .options(joinedload(PersonaMCPServer.mcp_server))
            .where(
                PersonaMCPServer.persona_id == persona_id,
                PersonaMCPServer.is_active,
                MCPServer.name == server_name,
                MCPServer.is_active
            )
        )
        result = await db_session.execute(stmt)
        link = result.scalar_one_or_none()

        if not link:
            raise ValueError(f'External server {server_name} not assigned to persona {persona_id}')

    # Call the MCP tool
    return await call_mcp_tool_by_server_id(link.mcp_server_id, actual_tool_name, parameters)
```

### 4. ChatRouter - MODIFY EXISTING UI TOOLS ENDPOINT

**File**: `faster_backend/nonix_web_agentic/routers/chat_router.py`

**Location**: Replace the existing `/personas/{persona_id}/tools` handler body

**Replace With**:
```python
@route('/personas/{persona_id}/tools', methods=['GET'])
async def persona_tools(self, req: Request, persona_id: int):
    """Get all tools grouped by namespace for UI display."""
    return await self.service_call_and_respond(
        self.tool_service.get_tools,
        service_args=(persona_id,)
    )
```

### 5. AgenticToolManager - SPLIT create_langchain_tools() INTO 3 FUNCTIONS

**File**: `faster_backend/nonix_web_agentic/llm/agentic_tool_manager.py`

**Location**: Replace `create_langchain_tools()` with 3 separate functions

**New Functions**:
```python
async def create_internal_langchain_tools(
        self,
        persona_id: int,
        available_tools_info: List[Dict[str, Any]]
) -> List[StructuredTool]:
    """Create LangChain StructuredTool objects from internal persona tools only."""
    # Existing logic from current create_langchain_tools()
    persona_tools = await self.build_persona_tool_map(persona_id)

    langchain_tools = []
    for tool_name, tool_func in persona_tools.items():
        # ... existing internal tool creation logic (lines 244-306) ...
    return langchain_tools

async def create_external_langchain_tools(self, persona_id: int) -> List[StructuredTool]:
    """Create LangChain StructuredTool objects from external MCP servers only."""

    langchain_tools = []

    # Get external servers for this persona
    async with AsyncSessionLocal() as db_session:
        stmt = select(PersonaMCPServer).options(
            joinedload(PersonaMCPServer.mcp_server)
        ).where(PersonaMCPServer.persona_id == persona_id, PersonaMCPServer.is_active)
        result = await db_session.execute(stmt)
        external_servers = result.scalars().all()

    # For each external server, get tools and create StructuredTool objects
    for server_link in external_servers:
        server = server_link.mcp_server
        server_config = {
            "command": server.command,
            "args": server.args_json or [],
            "env": server.env_json or {},
            "transport": "stdio"
        }

        client = MultiServerMCPClient({f"server_{server.id}": server_config})

        try:
            external_tools = await client.get_tools()
            for tool in external_tools:
                # Convert MCP tool to StructuredTool
                # Create Pydantic schema from tool.inputSchema
                # Name must be f"{server.name}:{tool.name}" for routing
                # Create StructuredTool wrapper
                langchain_tools.append(external_langchain_tool)
        except Exception as e:
            self._logger.error(f"Failed to load tools from MCP server {server.name}: {e}")

    return langchain_tools

async def create_langchain_tools(
        self,
        persona_id: int,
        available_tools_info: List[Dict[str, Any]]
) -> List[StructuredTool]:
    """Create LangChain StructuredTool objects from both internal and external tools."""
    # Merge internal and external tools
    internal_tools = await self.create_internal_langchain_tools(persona_id, available_tools_info)
    external_tools = await self.create_external_langchain_tools(persona_id)

    return internal_tools + external_tools
```

### 6. ToolExecutionService - IMPORTS

No additional imports needed if `select`, `joinedload`, `PersonaMCPServer`, and `MCPServer` are already imported (they currently are).

### 7. ChatMessageService - LLM TOOL FETCHING (NO CHANGE NEEDED)

**File**: `faster_backend/nonix_web_agentic/services/chat_message_service.py`

- Keep passing `available_tools_info` to `run_chat_streaming_with_retry`.
- Tools are built inside `run_chat_streaming` via `agentic_tool_manager.create_langchain_tools(...)`, which now returns merged internal + external tools after implementing step 5.

## Execution Flow After Changes

### LLM Integration (UPDATED):
- `run_chat_streaming` builds tools by calling `agentic_tool_manager.create_langchain_tools(persona_id, available_tools_info)`
- Gets flat array of StructuredTool objects for both internal and external tools

### Tool Execution:
1. LLM calls MCP tool "filesystem:list_dir"
2. `execute_tool_for_persona()` checks `agentic_tool_manager.get("filesystem:list_dir")` → None (not internal)
3. Routes to `execute_external_tool()` → parses "filesystem" + "list_dir"
4. Looks up MCP server by name (joined to filter), creates MCP client, calls tool

### UI Display:
1. Frontend calls `/personas/{id}/tools` → gets array of namespaces:
```python
[
  {
    "namespace": "database",
    "description": "Database operations",
    "is_external": false,
    "tools": [
      {"name": "query_users", "description": "...", "parameters": [...]},
      {"name": "insert_user", "description": "...", "parameters": [...]}
    ]
  },
  {
    "namespace": "filesystem",
    "description": "File system operations",
    "is_external": true,
    "tools": [
      {"name": "list_dir", "description": "...", "parameters": [...]}
    ]
  }
]
```
2. UI displays using expanders/accordions by namespace

## Testing Checklist

- [ ] LLM gets merged internal + external tools from updated `create_langchain_tools()`
- [ ] UI gets array of namespaces with grouped tools from `/personas/{id}/tools`
- [ ] Tool execution routes correctly: internal tools first, then external via `execute_external_tool`
- [ ] Internal MCP tools work in LLM (database:query_users)
- [ ] External MCP server tools work in LLM (filesystem:list_dir)
- [ ] UI displays grouped tools correctly with expanders/accordions
- [ ] Error handling works for both internal and external MCP tool failures
- [ ] WebSocket events work for both MCP tool types

## Files Modified

1. `faster_backend/nonix_web_agentic/llm/agentic_tool_manager.py`
   - Split `create_langchain_tools()` into 3 functions:
     - `create_internal_langchain_tools()` - for internal tools
     - `create_external_langchain_tools()` - for external tools using `MultiServerMCPClient`
     - `create_langchain_tools()` - merges both (calls the two above)

2. `faster_backend/nonix_web_agentic/services/tool_execution_service.py`
   - Add `get_tools()` method - groups tools by namespace for UI (public method)
   - Add internal helpers: `get_internal_tools()`, `get_external_tools()`
   - Add `get_external_servers()` method
   - Add `get_tool_schema()` method (imports `get_external_tool_schema`)
   - Modify `execute_tool_for_persona()` to route execution: internal → external
   - Add `execute_external_tool()` method (namespace:name)

3. `faster_backend/nonix_web_agentic/utils/mcp_client.py`
   - Add `get_external_tool_schema()` function

4. `faster_backend/nonix_web_agentic/routers/chat_router.py`
   - Modify `/personas/{persona_id}/tools` endpoint to return grouped tools via `tool_service.get_tools`

5. `faster_backend/nonix_web_agentic/services/chat_message_service.py`
   - No signature changes; tools are built inside `run_chat_streaming`

## No Changes Needed

- Database models - no changes needed
- UI components - will adapt to new grouped-by-namespace API response

**WARNING: NEVER USE INLINE IMPORTS**
**WARNING: NEVER USE hasattr**
**WARNING: NEVER CALL TERMINAL OR CONSOLE**
**WARNING: NEVER USE INLINE IMPORTS**
**WARNING: NEVER USE hasattr**
**WARNING: NEVER CALL TERMINAL OR CONSOLE**
**WARNING: NEVER USE INLINE IMPORTS**
**WARNING: NEVER USE hasattr**
**WARNING: NEVER CALL TERMINAL OR CONSOLE**
