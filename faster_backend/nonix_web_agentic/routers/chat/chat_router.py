from fastapi import Request

from nonix_web.router.web_server_router import NxWebServerRouter, router, route
from nonix_web.utils.di import Inject
from ..chat_session.chat_session_schemas import ChatSessionCreate
from ..chat_history.chat_history_schemas import CreateHistoryRequest, UpdateHistoryRequest
from ..chat_message.chat_message_schemas import SendMessageToHistoryRequest
from ...services.chat_session_service import ChatSessionService
from ...services.chat_message_service import ChatMessageService
from ...services.chat_history_service import ChatHistoryService
from ...services.persona_service import PersonaService
from ...services.tool_execution_service import ToolExecutionService


@router("/chat", tags=["Chat"])
class ChatRouter(NxWebServerRouter):
    """Unified chat service using dependency injection and DRY patterns.

    This router uses the base class service_call_and_respond method for:
    - Consistent error handling (400/500 responses)
    - DRY response formatting (defaults to {'data': result})
    - Optional custom converters for special cases

    Services:
    - ChatSessionService: Session CRUD operations
    - ChatMessageService: Message handling and LLM integration
    - ChatHistoryService: History management
    - PersonaService: Persona operations
    - ToolExecutionService: Tool execution and MCP operations
    """

    # Dependency injection for all services
    session_service: ChatSessionService = Inject(ChatSessionService)
    message_service: ChatMessageService = Inject(ChatMessageService)
    history_service: ChatHistoryService = Inject(ChatHistoryService)
    persona_service: PersonaService = Inject(PersonaService)
    tool_service: ToolExecutionService = Inject(ToolExecutionService)

    # ==========================================
    # SESSION ROUTES
    # ==========================================

    @route('/sessions', methods=['POST'])
    async def create_session(self, req: Request, payload: ChatSessionCreate):
        """Create a new chat session."""
        return await self.service_call_and_respond(
            self.session_service.create_session_with_history,
            payload.persona_id, payload.session_name, payload.session_icon,
            response_converter=lambda r: {'data': r.to_dict()}
        )

    @route('/sessions', methods=['GET'])
    async def list_sessions(self, req: Request):
        """List all active chat sessions."""
        return await self.service_call_and_respond(
            self.session_service.get_sessions_with_counts,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/sessions/{id}', methods=['GET'])
    async def get_session(self, req: Request, id: int):
        """Get a specific chat session by ID."""
        return await self.service_call_and_respond(self.session_service.get_session_with_count, id)

    @route('/sessions/{id}', methods=['PUT'])
    async def update_session(self, req: Request, payload: ChatSessionCreate, id: int):
        """Update a chat session."""
        return await self.service_call_and_respond(
            self.session_service.update_session,
            id, payload.session_name, payload.session_icon, payload.is_active,
            response_converter=lambda r: {'data': r.to_dict()}
        )

    @route('/sessions/{id}', methods=['DELETE'])
    async def delete_session(self, req: Request, id: int):
        """Delete a chat session."""
        return await self.service_call_and_respond(self.session_service.delete_session, id)

    @route('/personas/{persona_id}/sessions', methods=['GET'])
    async def get_persona_sessions(self, req: Request, persona_id: int):
        """Get all sessions for a specific persona."""
        return await self.service_call_and_respond(
            self.session_service.get_persona_sessions, persona_id,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/personas/{persona_id}/start-chat', methods=['POST'])
    async def start_chat_with_persona(self, req: Request, payload: ChatSessionCreate, persona_id: int):
        """Start a new chat session with a persona."""
        return await self.service_call_and_respond(
            self.session_service.start_chat_with_persona,
            persona_id, payload.session_name, payload.session_icon,
            response_converter=lambda r: ({'data': r.to_dict()}, 201)
        )

    # ==========================================
    # HISTORY ROUTES
    # ==========================================

    @route('/sessions/{id}/histories', methods=['GET'])
    async def list_session_histories(self, req: Request, id: int):
        """List all histories for a specific session."""
        return await self.service_call_and_respond(
            self.history_service.list_session_histories, id,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/sessions/{id}/histories', methods=['POST'])
    async def create_session_history(self, req: Request, payload: CreateHistoryRequest, id: int):
        """Create a new history for a specific session."""
        return await self.service_call_and_respond(
            self.history_service.create_session_history, id, payload.title,
            response_converter=lambda r: ({'data': r.to_dict()}, 201)
        )

    @route('/sessions/{id}/histories/{history_id}', methods=['GET'])
    async def get_session_history(self, req: Request, id: int, history_id: int):
        """Get a specific history within a session."""
        return await self.service_call_and_respond(self.history_service.get_session_history, id, history_id)

    @route('/sessions/{id}/histories/{history_id}', methods=['PUT'])
    async def update_session_history(self, req: Request, payload: UpdateHistoryRequest, id: int, history_id: int):
        """Update a specific history within a session."""
        return await self.service_call_and_respond(
            self.history_service.update_session_history, id, history_id, payload.title,
            response_converter=lambda r: {'data': r.to_dict()}
        )

    @route('/sessions/{id}/histories/{history_id}', methods=['DELETE'])
    async def delete_session_history(self, req: Request, id: int, history_id: int):
        """Delete a specific history within a session."""
        return await self.service_call_and_respond(self.history_service.delete_session_history, id, history_id)

    # ==========================================
    # MESSAGE ROUTES
    # ==========================================

    @route('/sessions/{id}/messages', methods=['GET'])
    async def list_messages(self, req: Request, id: int):
        """List messages from a chat session's current history."""
        return await self.service_call_and_respond(
            self.message_service.list_messages, id,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/sessions/{session_id}/histories/{history_id}/send', methods=['POST'])
    async def send_message(self, req: Request, payload: SendMessageToHistoryRequest, session_id: int, history_id: int):
        """Send message to session."""
        return await self.service_call_and_respond(self.message_service.send_message, session_id, history_id, payload)

    @route('/sessions/{session_id}/histories/{history_id}/messages', methods=['GET'])
    async def list_history_messages(self, req: Request, session_id: int, history_id: int):
        """Get messages from a specific history within a session."""
        # This method doesn't exist in the service yet, using list_messages for now
        return await self.service_call_and_respond(
            self.message_service.list_messages, session_id,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    # ==========================================
    # PERSONA ROUTES
    # ==========================================

    @route('/personas', methods=['GET'])
    async def list_personas(self, req: Request):
        """List all available personas with active session counts."""
        return await self.service_call_and_respond(
            self.persona_service.list_personas_with_session_counts,
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/personas/{persona_id}', methods=['GET'])
    async def get_persona(self, req: Request, persona_id: int):
        """Get a single persona by ID with active session count."""
        return await self.service_call_and_respond(self.persona_service.get_persona_with_session_count, persona_id)

    # ==========================================
    # TOOL ROUTES
    # ==========================================

    @route('/personas/{persona_id}/tools', methods=['GET'])
    async def persona_tools(self, req: Request, persona_id: int):
        """Get available tools for a specific persona."""
        return await self.service_call_and_respond(self.tool_service.list_persona_tools, persona_id)

    @route('/tools/registry', methods=['GET'])
    async def registry_tools(self, req: Request):
        """List all registered LLM tools from the in-memory registry."""
        return await self.service_call_and_respond(self.tool_service.list_registry_tools)

    @route('/mcp/servers/status', methods=['GET'])
    async def mcp_status(self, req: Request):
        """Get status of all MCP servers."""
        return await self.service_call_and_respond(self.tool_service.get_mcp_servers_status)
