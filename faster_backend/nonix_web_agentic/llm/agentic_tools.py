from typing import List, Tuple, Callable


def tool(name: str):
    def decorator(func):
        setattr(func, "_tool_name", name)
        return func
    return decorator


class AgenticTools:
    """Pure tool base with no DB/CRUD knowledge.

    - Use @tool("namespace:name") to mark methods
    - to_agentic_tools() extracts (name, func) pairs for registration
    """

    def to_agentic_tools(self) -> List[Tuple[str, Callable]]:
        tools: List[Tuple[str, Callable]] = []
        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_tool_name"):
                tool_name = getattr(attr, "_tool_name")
                # Auto-prefix if prefix is set and name doesn't already contain ':'
                if hasattr(self, 'prefix') and self.prefix and ':' not in tool_name:
                    tool_name = f"{self.prefix}:{tool_name}"
                tools.append((tool_name, attr))
        return tools


