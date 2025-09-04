from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin


# ============================================================================
# CHAT SESSION SCHEMAS
# ============================================================================

class CreateSessionRequest(BaseModel):
    persona_id: int = Field(..., gt=0, description="Persona ID")
    session_name: Optional[str] = Field(None, max_length=255, description="Session name")
    session_icon: Optional[str] = Field(None, max_length=512, description="Session icon")


class UpdateSessionRequest(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    session_icon: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None


class SessionBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    session_name: Optional[str] = Field(None, max_length=255)
    session_icon: Optional[str] = Field(None, max_length=512)
    current_history_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True


class SessionResponse(SessionBase, BaseDbModelMixin):
    pass


class SessionListResponse(BaseModel):
    data: List[SessionResponse]
    total: int


class SessionWithHistoryResponse(SessionResponse):
    history_count: int = 0


class DeleteSessionResponse(BaseModel):
    message: str = Field(..., description="Success message")


# ============================================================================
# CHAT MESSAGE SCHEMAS
# ============================================================================

class SendMessageRequest(BaseModel):
    role: str = Field(..., description="Message role: system|user|assistant|tool")
    message_type: str = Field(..., description="Message type: text|tool_call|tool_result|image|file")
    content_json: Optional[Dict[str, Any]] = Field(None, description="Structured content")


class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")


class MessageBase(BaseModel):
    history_id: int = Field(..., gt=0)
    role: str = Field(..., max_length=50)
    message_type: str = Field(..., max_length=50)
    content_json: Optional[Dict[str, Any]] = None
    status: str = Field(..., max_length=50)


class MessageResponse(MessageBase, BaseDbModelMixin):
    pass


class StreamingChunkResponse(BaseModel):
    chunk_type: str = Field(..., description="Type of chunk: text|tool_call|complete")
    content: str = Field(..., description="Chunk content")
    message_id: Optional[int] = Field(None, description="Message ID if available")
    is_complete: bool = Field(default=False, description="Whether this is the final chunk")


class ToolExecutionResponse(BaseModel):
    tool_name: str = Field(..., description="Name of the executed tool")
    status: str = Field(..., description="Execution status: success|error|timeout")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: Optional[int] = Field(None, ge=0, description="Execution duration in milliseconds")


# ============================================================================
# CHAT HISTORY SCHEMAS
# ============================================================================

class CreateHistoryRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="History title")
    summary: Optional[str] = Field(None, description="AI-generated summary")


class UpdateHistoryRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = None


class HistoryBase(BaseModel):
    session_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = None
    message_count: int = Field(default=0, ge=0)


class HistoryResponse(HistoryBase, BaseDbModelMixin):
    pass


class HistoryListResponse(BaseModel):
    data: List[HistoryResponse]
    total: int


class HistoryWithMessagesResponse(HistoryResponse):
    messages: List[MessageResponse] = Field(default_factory=list)


class DeleteHistoryResponse(BaseModel):
    message: str = Field(..., description="Success message")
    deleted_history_id: int = Field(..., description="ID of deleted history")


# ============================================================================
# MESSAGE MANAGEMENT SCHEMAS
# ============================================================================

class MessageListResponse(BaseModel):
    data: List[MessageResponse]
    total: int


class SendMessageToHistoryRequest(BaseModel):
    message_type: str = Field(..., description="Meta-type: user|tool_call|system")
    content: Dict[str, Any] = Field(..., description="Message content in JSON format")


class DeleteMessageResponse(BaseModel):
    message: str = Field(..., description="Success message")
    deleted_message_id: int = Field(..., description="ID of deleted message")


# ============================================================================
# TOOL MANAGEMENT SCHEMAS
# ============================================================================

class PersonaToolsResponse(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of available tools")


class MCPServerStatusResponse(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="List of MCP server statuses")


# ============================================================================
# PERSONA SCHEMAS
# ============================================================================

class PersonaChatRequest(BaseModel):
    persona_id: int = Field(..., gt=0, description="Persona ID to chat with")


class PersonaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    is_active: bool = True
    system_prompt: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    artist_id: Optional[int] = Field(None, gt=0)
    ai_model_mapping_id: int = Field(..., gt=0)


class PersonaChatResponse(PersonaBase, BaseDbModelMixin):
    pass


class PersonaListResponse(BaseModel):
    data: List[PersonaChatResponse]
    total: int


# ============================================================================
# TOOL EXECUTION SCHEMAS
# ============================================================================

class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool execution parameters")
    session_id: int = Field(..., gt=0, description="Chat session ID")
    history_id: int = Field(..., gt=0, description="Chat history ID")


class MCPRequest(BaseModel):
    server_name: str = Field(..., description="MCP server name")
    method: str = Field(..., description="MCP method to call")
    params: Dict[str, Any] = Field(..., description="Method parameters")


class MCPResponse(BaseModel):
    server_name: str = Field(..., description="MCP server name")
    method: str = Field(..., description="MCP method called")
    result: Optional[Dict[str, Any]] = Field(None, description="Method result")
    error: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# HEALTH AND STATUS SCHEMAS
# ============================================================================

class TaskManagerStats(BaseModel):
    active_tasks: int = Field(..., description="Number of active tasks")
    max_concurrent_tasks: int = Field(..., description="Maximum concurrent tasks")
    utilization: str = Field(..., description="Current utilization percentage")
    failure_rate: str = Field(..., description="Current failure rate")
    total_submissions: int = Field(..., description="Total task submissions")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class TaskManagerHealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    stats: TaskManagerStats = Field(..., description="Task manager statistics")


# ============================================================================
# WEBSOCKET EVENT SCHEMAS
# ============================================================================

class ChatEventData(BaseModel):
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: str = Field(..., description="Event timestamp")


class LLMStatusEvent(BaseModel):
    stage: str = Field(..., description="LLM processing stage")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Event timestamp")


class ToolStatusEvent(BaseModel):
    tool_name: str = Field(..., description="Tool name")
    status: str = Field(..., description="Tool status")
    timestamp: str = Field(..., description="Event timestamp")
    extra: Optional[Dict[str, Any]] = Field(None, description="Additional data")
