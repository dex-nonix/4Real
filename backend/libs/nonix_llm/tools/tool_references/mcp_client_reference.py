import asyncio
from typing import Union, Dict, Any, Optional, List

import time

from .base import ToolReference


class MCPClientReference(ToolReference):
    """Reference to MCP client tools."""

    def __init__(self, source: Union[Dict[str, Any], Any], config_overrides: Optional[Dict[str, Any]] = None):
        super().__init__(source, config_overrides)

        if isinstance(source, dict) and "mcp_client" in source:
            client_config = source["mcp_client"]
            if isinstance(client_config, dict):
                # MCP server configuration
                self.mcp_config = client_config
                self.mcp_client = None
            else:
                # MCP client instance
                self.mcp_client = client_config
                self.mcp_config = None
        else:
            # Direct MCP client instance
            self.mcp_client = source
            self.mcp_config = None

    def needs_reload(self) -> bool:
        """MCP tools can change if server changes."""
        return True  # Always check for changes

    def reload(self) -> None:
        """Load tools from MCP client."""
        # This will be handled by get_tools since MCP loading is async
        pass

    def get_tools(self, context: Optional[Dict[str, Any]] = None,
                  partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tools from MCP client with async handling."""
        if self.disabled:
            return []

        try:
            # Import here to avoid circular imports
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # No event loop in current thread
                return self._get_tools_sync(context, partial_map)

            if loop.is_running():
                # We're in an async context, but can't await
                # Return cached tools or empty list
                return self.cached_tools or []
            else:
                # We can run async code
                return asyncio.run(self._get_tools_async(context, partial_map))

        except Exception as e:
            print(f"Error loading MCP tools: {str(e)}")
            return []

    async def _get_tools_async(self, context: Optional[Dict[str, Any]] = None,
                               partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Async tool loading for MCP."""
        try:
            if self.mcp_client is None and self.mcp_config:
                # Create MCP client from config
                self.mcp_client = await self._create_mcp_client(self.mcp_config)

            if self.mcp_client is None:
                return []

            # Get tools from MCP client
            mcp_tools = await self.mcp_client.get_tools()

            # Convert to universal containers
            tools = []
            for mcp_tool in mcp_tools:
                tool = self._convert_mcp_tool(mcp_tool)
                if tool:
                    tools.append(self._apply_context_and_partials(tool, context, partial_map))

            self.cached_tools = tools
            self.last_load_time = time.time()
            self.error_state = None

            return tools

        except Exception as e:
            self.error_state = f"Failed to load MCP tools: {str(e)}"
            return []

    def _get_tools_sync(self, context: Optional[Dict[str, Any]] = None,
                        partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Synchronous fallback for MCP tools."""
        # Return cached tools if available
        if self.cached_tools:
            return [self._apply_context_and_partials(tool, context, partial_map)
                    for tool in self.cached_tools]
        return []

    async def _create_mcp_client(self, config: Dict[str, Any]):
        """Create MCP client from configuration."""
        try:
            # Import langchain-mcp-adapters
            from langchain_mcp_adapters.client import MultiServerMCPClient

            # Create client with server config
            servers = {config.get("server", "default"): config}
            client = MultiServerMCPClient(servers)

            return client

        except ImportError:
            raise ImportError("langchain-mcp-adapters not installed. Install with: pip install langchain-mcp-adapters")
        except Exception as e:
            raise Exception(f"Failed to create MCP client: {str(e)}")

    def _convert_mcp_tool(self, mcp_tool) -> Optional[Dict[str, Any]]:
        """Convert MCP tool to universal container."""
        try:
            # Extract metadata from MCP tool (this depends on the MCP tool format)
            name = getattr(mcp_tool, 'name', 'unknown_mcp_tool')
            description = getattr(mcp_tool, 'description', 'No description available')
            func = getattr(mcp_tool, 'func', None)

            if not func:
                return None

            # Create universal container
            tool = self._create_tool_container(
                name=name,
                description=description,
                function=func
            )

            # Store original MCP tool in metadata
            tool["metadata"]["original_tool"] = mcp_tool
            tool["metadata"]["framework_specific"]["mcp"] = {
                "server_config": self.mcp_config
            }

            return tool

        except Exception as e:
            print(f"Error converting MCP tool: {str(e)}")
            return None
