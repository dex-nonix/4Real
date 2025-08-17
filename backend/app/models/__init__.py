# Models package init (kept minimal for MVP)

# Import all models to ensure they are registered with SQLAlchemy
from .chat_history import ChatHistory
from .chat_message import ChatMessage
from .chat_session import ChatSession
from .persona import Persona
from .ai_model_mapping import AIModelMapping
from .ai_provider import AIProvider
from .tool_invocation_log import ToolInvocationLog
from .internal_tool import InternalTool
from .persona_tool_access import PersonaToolAccess
from .mcp_server import MCPServer
from .persona_mcp_server import PersonaMCPServer
from .artist import Artist
from .album import Album
from .track import Track
from .style import Style
from .rhyme_technique import RhymeTechnique
from .file import File
from .file_category import FileCategory
from .file_link import FileLink
from .associations import TrackStyle, TrackRhymeTechnique

