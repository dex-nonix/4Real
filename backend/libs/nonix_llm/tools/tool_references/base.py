from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Callable
import logging

logger = logging.getLogger("nonix_llm.tools.tool_references.base")


class ToolReference(ABC):
    """
    Abstract base class for all tool source references.

    Provides the foundation for lazy loading, change detection, and tool resolution.
    """

    def __init__(self, source: Any, config_overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize tool reference.

        Args:
            source: The source data for this reference
            config_overrides: Optional configuration overrides
        """
        self.source = source
        self.config_overrides = config_overrides or {}
        self.cached_tools = None
        self.last_load_time = None
        self.error_state = None
        self.disabled = False  # Universal disabled property

    @abstractmethod
    def needs_reload(self) -> bool:
        """Check if this reference needs to be reloaded."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Reload tools from the source."""
        pass

    @abstractmethod
    def get_tools(self, context: Optional[Dict[str, Any]] = None,
                  partial_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tools from this reference with context and partial injection."""
        if self.disabled:
            return []  # Skip disabled tools

        if self.needs_reload():
            self.reload()

        if self.error_state:
            return []

        return [self._apply_context_and_partials(tool, context, partial_map)
                for tool in self.cached_tools or []]

    def _create_tool_container(self, name: str, description: str, function: Callable,
                             props: Optional[Dict[str, Any]] = None,
                             hidden_props: Optional[List[str]] = None,
                             param_descriptions: Optional[Dict[str, str]] = None,
                             partial: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a universal tool container.

        Args:
            name: Tool name
            description: Tool description
            function: Tool function
            props: Tool properties
            hidden_props: Properties to hide from LLM
            param_descriptions: Parameter descriptions
            partial: Arguments for partial binding

        Returns:
            Universal tool container
        """
        return {
            "name": name,
            "description": description,
            "function": function,
            "props": props or {},
            "hidden_props": hidden_props or [],
            "param_descriptions": param_descriptions or {},
            "partial": partial or [],
            "metadata": {
                "source_type": self.__class__.__name__.replace("Reference", "").lower(),
                "original_tool": None,
                "framework_specific": {}
            }
        }

    def _apply_context_and_partials(self, tool: Dict[str, Any],
                                  context: Optional[Dict[str, Any]] = None,
                                  partial_map: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply context-aware property resolution and partial binding.

        Args:
            tool: Tool container
            context: Runtime context
            partial_map: Partial injection map

        Returns:
            Tool with context and partials applied
        """
        resolved_tool = tool.copy()

        # Apply context-based property resolution
        if context:
            resolved_props = {}
            for key, value in tool["props"].items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    context_key = value[2:-1]
                    if context_key in context:
                        resolved_props[key] = context[context_key]
                    else:
                        resolved_props[key] = value
                else:
                    resolved_props[key] = value
            resolved_tool["props"] = resolved_props

        # Apply partial binding - POSITIONAL ONLY
        if tool["partial"]:
            original_function = tool["function"]
            partial_args = []

            for arg_name in tool["partial"]:
                if partial_map and arg_name in partial_map:
                    partial_args.append(partial_map[arg_name])
                else:
                    raise ValueError(f"Partial '{arg_name}' not found in partial_map for tool '{tool.get('name')}'")

            if partial_args:
                from functools import partial
                logger.debug(f"Binding partials {partial_args} positionally to {original_function} (tool: {tool.get('name')})")
                resolved_tool["function"] = partial(original_function, *partial_args)

        return resolved_tool
