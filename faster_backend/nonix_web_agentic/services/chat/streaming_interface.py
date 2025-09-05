from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Any, Optional, List


@dataclass
class StreamingChunk:
    content: str
    chunk_type: str  # 'text', 'tool_start', 'tool_end', 'complete'
    metadata: Optional[Dict[str, Any]] = None
    is_final: bool = False


class StreamingResponseInterface(ABC):
    """Abstract interface for streaming responses."""

    @abstractmethod
    async def stream_response(self, messages: List[Dict], tools: List[Dict]) -> AsyncGenerator[StreamingChunk, None]:
        """Stream response chunks asynchronously."""
        pass

    @abstractmethod
    async def handle_tool_calls(self, tool_name: str, args: Dict) -> Dict[str, Any]:
        """Handle tool execution during streaming."""
        pass
