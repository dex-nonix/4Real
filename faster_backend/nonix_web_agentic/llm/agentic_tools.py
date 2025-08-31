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
                tools.append((getattr(attr, "_tool_name"), attr))
        return tools


