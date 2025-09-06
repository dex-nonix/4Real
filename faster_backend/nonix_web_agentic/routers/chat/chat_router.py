from fastapi import Request

from nonix_web.router.web_server_router import NxWebServerRouter
from nonix_web.router.decorators import router, route
from nonix_web.utils.di import Inject
from nonix_web_agentic.schemas.chat_session_schemas import ChatSessionCreate
from nonix_web_agentic.schemas.chat_history_schemas import ChatHistoryCreate, ChatHistoryUpdate
from nonix_web_agentic.schemas.chat_message_schemas import SendMessageToHistoryRequest
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
            service_args=(payload.persona_id, payload.session_name, payload.session_icon),
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
        return await self.service_call_and_respond(
            self.session_service.get_session_with_count,
            service_args=(id,)
        )

    @route('/sessions/{id}', methods=['PUT'])
    async def update_session(self, req: Request, payload: ChatSessionCreate, id: int):
        """Update a chat session."""
        return await self.service_call_and_respond(
            self.session_service.update_session,
            service_args=(id, payload.session_name, payload.session_icon, payload.is_active),
            response_converter=lambda r: {'data': r.to_dict()}
        )

    @route('/sessions/{id}', methods=['DELETE'])
    async def delete_session(self, req: Request, id: int):
        """Delete a chat session."""
        return await self.service_call_and_respond(
            self.session_service.delete_session,
            service_args=(id,)
        )

    @route('/personas/{persona_id}/sessions', methods=['GET'])
    async def get_persona_sessions(self, req: Request, persona_id: int):
        """Get all sessions for a specific persona."""
        return await self.service_call_and_respond(
            self.session_service.get_persona_sessions,
            service_args=(persona_id,),
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/personas/{persona_id}/start-chat', methods=['POST'])
    async def start_chat_with_persona(self, req: Request, payload: ChatSessionCreate, persona_id: int):
        """Start a new chat session with a persona."""
        return await self.service_call_and_respond(
            self.session_service.start_chat_with_persona,
            service_args=(persona_id, payload.session_name, payload.session_icon),
            response_converter=lambda r: ({'data': r.to_dict()}, 201)
        )

    # ==========================================
    # HISTORY ROUTES
    # ==========================================

    @route('/sessions/{id}/histories', methods=['GET'])
    async def list_session_histories(self, req: Request, id: int):
        """List all histories for a specific session."""
        return await self.service_call_and_respond(
            self.history_service.list_session_histories,
            service_args=(id,),
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/sessions/{id}/histories', methods=['POST'])
    async def create_session_history(self, req: Request, payload: ChatHistoryCreate, id: int):
        """Create a new history for a specific session."""
        return await self.service_call_and_respond(
            self.history_service.create_session_history,
            service_args=(id, payload.title),
            response_converter=lambda r: ({'data': r.to_dict()}, 201)
        )

    @route('/sessions/{id}/histories/{history_id}', methods=['GET'])
    async def get_session_history(self, req: Request, id: int, history_id: int):
        """Get a specific history within a session."""
        return await self.service_call_and_respond(
            self.history_service.get_session_history,
            service_args=(id, history_id)
        )

    @route('/sessions/{id}/histories/{history_id}', methods=['PUT'])
    async def update_session_history(self, req: Request, payload: ChatHistoryUpdate, id: int, history_id: int):
        """Update a specific history within a session."""
        return await self.service_call_and_respond(
            self.history_service.update_session_history,
            service_args=(id, history_id, payload.title),
            response_converter=lambda r: {'data': r.to_dict()}
        )

    @route('/sessions/{id}/histories/{history_id}', methods=['DELETE'])
    async def delete_session_history(self, req: Request, id: int, history_id: int):
        """Delete a specific history within a session."""
        return await self.service_call_and_respond(
            self.history_service.delete_session_history,
            service_args=(id, history_id)
        )

    # ==========================================
    # MESSAGE ROUTES
    # ==========================================

    @route('/sessions/{id}/messages', methods=['GET'])
    async def list_messages(self, req: Request, id: int):
        """List messages from a chat session's current history."""
        return await self.service_call_and_respond(
            self.message_service.list_messages,
            service_args=(id,),
            response_converter=lambda r: {'data': r, 'total': len(r)}
        )

    @route('/sessions/{session_id}/histories/{history_id}/send', methods=['POST'])
    async def send_message(self, req: Request, payload: SendMessageToHistoryRequest, session_id: int, history_id: int):
        """Send message to session."""
        return await self.service_call_and_respond(
            self.message_service.send_message,
            service_args=(session_id, history_id, payload)
        )

    @route('/sessions/{session_id}/histories/{history_id}/messages', methods=['GET'])
    async def list_history_messages(self, req: Request, session_id: int, history_id: int):
        """Get messages from a specific history within a session."""
        return await self.service_call_and_respond(
            self.message_service.list_history_messages,
            service_args=(session_id, history_id),
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
        return await self.service_call_and_respond(
            self.persona_service.get_persona_with_session_count,
            service_args=(persona_id,)
        )

    # ==========================================
    # TOOL ROUTES
    # ==========================================

    @route('/personas/{persona_id}/tools', methods=['GET'])
    async def persona_tools(self, req: Request, persona_id: int):
        """Get available tools for a specific persona."""
        return await self.service_call_and_respond(
            self.tool_service.list_persona_tools,
            service_args=(persona_id,)
        )

    @route('/tools/registry', methods=['GET'])
    async def registry_tools(self, req: Request):
        """List all registered LLM tools from the in-memory registry."""
        return await self.service_call_and_respond(self.tool_service.list_registry_tools)

    @route('/mcp/servers/status', methods=['GET'])
    async def mcp_status(self, req: Request):
        """Get status of all MCP servers."""
        return await self.service_call_and_respond(self.tool_service.get_mcp_servers_status)

    @route('/personas/{persona_id}/tools/execute', methods=['POST'])
    async def execute_tool(self, req: Request, payload: dict, persona_id: int):
        """Execute a tool for a specific persona."""
        return await self.service_call_and_respond(
            self.tool_service.execute_tool_for_persona,
            service_args=(persona_id, payload.get('tool_name'), payload.get('tool_args', {}))
        )

    # ==========================================
    # DELETE MESSAGE ROUTES
    # ==========================================

    @route('/sessions/{session_id}/histories/{history_id}/messages', methods=['DELETE'])
    async def clear_history_messages(self, req: Request, session_id: int, history_id: int):
        """Clear all messages from a specific history."""
        return await self.service_call_and_respond(
            self.message_service.clear_history_messages,
            service_args=(session_id, history_id)
        )

    @route('/sessions/{session_id}/histories/{history_id}/messages/{message_id}', methods=['DELETE'])
    async def delete_message(self, req: Request, session_id: int, history_id: int, message_id: int):
        """Delete a specific message from a history."""
        return await self.service_call_and_respond(
            self.message_service.delete_message_with_validation,
            service_args=(session_id, history_id, message_id)
        )

    @route('/sessions/{session_id}/histories/{history_id}/messages/{assistant_message_id}/cancel', methods=['POST'])
    async def cancel_message_streaming(self, req: Request, session_id: int, history_id: int, assistant_message_id: int):
        """Cancel streaming for a single assistant message."""
        return await self.service_call_and_respond(
            self.message_service.cancel_message_streaming,
            service_args=(session_id, history_id, assistant_message_id)
        )

    @route('/sessions/{session_id}/retry', methods=['POST'])
    async def retry_last_message(self, req: Request, session_id: int):
        """Retry the last user message in a session."""
        return await self.service_call_and_respond(
            self.message_service.retry_last_message,
            service_args=(session_id,)
        )

    @route('/sessions/{session_id}/last-message', methods=['GET'])
    async def get_last_user_message(self, req: Request, session_id: int):
        """Get the last user message content for retry functionality."""
        return await self.service_call_and_respond(
            self.message_service.get_last_user_message,
            service_args=(session_id,)
        )
