# 🚀 **UNIFIED MESSAGE TYPES & TOOLS SYSTEM - CORRECTED BLUEPRINT**

## 🎯 **OVERVIEW**
Replace the broken separate tool execution architecture with a **UNIFIED MESSAGE TYPE SYSTEM** where all messages (chat, tools) flow through the same endpoints with the same WebSocket events and same response formats. **NO plain text support - ONLY object messages with explicit types!**

## 🚨 **CURRENT PROBLEMS TO FIX**

### **1. Separate Tool Execution Endpoint (OBSOLETE)**
```python
# ❌ DELETE THIS - OBSOLETE!
@expose('/personas/{persona_id}/tools/execute')
def persona_tool_execute(self, req: Request, persona_id: int):
    # This method is ARCHITECTURALLY WRONG
    # Personas cannot execute tools without session context
```

### **2. Frontend executeTool Method (OBSOLETE)**
```javascript
// ❌ DELETE THIS - OBSOLETE!
async executeTool(personaId, toolName, toolArgs, historyId, userMessageId, sessionId = null) {
    // This method signature is WRONG
    // messageId is NEVER needed for UI tool calls - they're direct user actions!
}
```

### **3. Plain Text Support (OBSOLETE)**
```python
# ❌ DELETE THIS - OBSOLETE!
# No plain text support - all messages must be objects with explicit types!
```

## ✅ **NEW CORRECTED ARCHITECTURE**

### **1. Two Message Endpoints (Current vs Specific History)**
```
POST /chat/sessions/{session_id}/send                    # Current history (extracted from session)
POST /chat/sessions/{session_id}/histories/{history_id}/send  # Specific history
```

### **2. ONLY Object Messages with Explicit Types**
```javascript
// ✅ CORRECT: Chat messages (explicit type)
{
  "content": {
    "type": "chat",
    "text": "Hello world"
  }
}

// ✅ CORRECT: Tool call messages (explicit type)
{
  "content": {
    "type": "tool_call",
    "tool": "tool_name",
    "args": {...}
  }
}

// ❌ WRONG: No plain text allowed
// "content": "Hello world"  // ❌ ERROR!
```

### **3. Unified Response Format for Everything**
```javascript
// Frontend gets same response structure for ALL message types
const response = await chatService.sendMessage(sessionId, historyId, content);

// Response is ALWAYS the same format:
{
  data: {
    message_id: 123,
    status: 'complete',
    // ... same structure for chat, tool, etc.
  }
}
```

### **4. Unified WebSocket Events for Everything**
```python
# All message types emit the same WebSocket events
self.emit_chat_event(session_id, history_id, 'message_received', {
    'message_id': message.id,
    'role': message.role,
    'message_type': message.message_type,
    'content': message.content_json,
    'timestamp': message.created_at.isoformat()
})
```

## 🔧 **IMPLEMENTATION: MESSAGE TYPE REGISTRY SYSTEM**

### **1. Create Message Type Handler Registry**
```python
# backend/app/services/chat_service/message_type_registry.py
from typing import Any, Callable, Dict
from abc import ABC, abstractmethod

class MessageTypeHandler(ABC):
    """Abstract base class for message type handlers."""
    
    @abstractmethod
    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a message of this type.
        
        Args:
            chat_service: ChatService instance for emit methods (MANDATORY!)
            session: Session object (MANDATORY!)
            persona: Persona object (MANDATORY DIRECT PARAMETER!)
            history_id: History ID (MANDATORY!)
            content: Message content object (MANDATORY!)
        """
        pass

class MessageTypeRegistry:
    """Dynamic registry for message type handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, MessageTypeHandler] = {}
    
    def register(self, message_type: str, handler: MessageTypeHandler) -> None:
        """Register a handler for a message type."""
        self._handlers[message_type] = handler
        print(f"Registered message type handler: {message_type}")
    
    def get_handler(self, message_type: str) -> MessageTypeHandler:
        """Get handler for message type."""
        return self._handlers.get(message_type)
    
    def has_handler(self, message_type: str) -> bool:
        """Check if a handler exists for the message type."""
        return message_type in self._handlers
    
    def list_types(self) -> list[str]:
        """List all registered message types."""
        return list(self._handlers.keys())

# Global registry instance
message_type_registry = MessageTypeRegistry()
```

### **2. Create ONLY the Handlers We Need**
```python
# backend/app/services/chat_service/message_handlers.py
from .message_type_registry import MessageTypeHandler
from ..models.chat_message import ChatMessage
from ..tool_runtime import execute_tool
from ... import db
from datetime import datetime

class ChatMessageHandler(MessageTypeHandler):
    """Handle chat messages - explicit text messages."""
    
    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ ALL VALUES ARE MANDATORY AND DIRECT - NO SESSION LOOKUPS!
        
        message_text = content.get('text', '')
        if not message_text:
            return self._format_error_response('Text content is required for chat messages', 400)
        
        # Create chat message
        chat_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='user',
            message_type='chat',
            content_json=content,
            status='complete'
        )
        db.session.add(chat_msg)
        db.session.commit()
        
        # Emit WebSocket events
        session_id = session.id             # ✅ Direct from session
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': chat_msg.id,
            'role': chat_msg.role,
            'content': chat_msg.content_json,
            'timestamp': chat_msg.created_at.isoformat()
        })
        
        # Start AI processing - persona is DIRECT PARAMETER!
        asst_msg = chat_service._create_assistant_placeholder(history_id)
        chat_service._submit_message_for_async_processing(
            chat_msg.id, asst_msg.id, session_id, history_id, persona.id  # ✅ DIRECT persona.id!
        )
        
        return {
            'chat_message_id': chat_msg.id,
            'assistant_message_id': asst_msg.id,
            'status': 'processing',
            'websocket_channel': f'chat/{session_id}/{history_id}'
        }

class ToolCallMessageHandler(MessageTypeHandler):
    """Handle tool call messages - direct tool execution."""
    
    def handle(self, chat_service, session, persona, history_id: int, content: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ ALL VALUES ARE MANDATORY AND DIRECT - NO SESSION LOOKUPS!
        
        tool_name = content.get('tool')
        tool_args = content.get('args', {})
        
        # Create tool call message
        tool_call_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='user',
            message_type='tool_call',
            content_json=content,
            status='complete'
        )
        db.session.add(tool_call_msg)
        db.session.commit()
        
        # Emit WebSocket event for tool call received
        session_id = session.id             # ✅ Direct from session
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_call_msg.id,
            'role': tool_call_msg.role,
            'message_type': 'tool_call',
            'content': tool_call_msg.content_json,
            'timestamp': tool_call_msg.created_at.isoformat()
        })
        
        # Emit WebSocket event for tool execution started
        chat_service.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)
        
        # Execute tool - persona is DIRECT PARAMETER!
        exec_result = execute_tool(persona.id, tool_name, tool_args)  # ✅ DIRECT persona.id!
        
        # Emit WebSocket event for tool execution completed
        chat_service.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)
        
        # Create tool result message
        tool_result_msg = ChatMessage(
            history_id=history_id,          # ✅ Direct value
            role='tool',
            message_type='tool',
            content_json={
                'toolName': tool_name,
                'toolParams': tool_args,
                'executionStatus': 'success' if exec_result.get('status') == 'success' else 'error',
                'result': exec_result,
                'executedBy': 'user',
                'executionTime': datetime.utcnow().isoformat()
            }
        )
        db.session.add(tool_result_msg)
        db.session.commit()
        
        # Emit WebSocket event for tool result message
        chat_service.emit_chat_event(session_id, history_id, 'message_received', {
            'message_id': tool_result_msg.id,
            'role': tool_result_msg.role,
            'message_type': 'tool',
            'content': tool_result_msg.content_json,
            'timestamp': tool_result_msg.created_at.isoformat()
        })
        
        return {
            'tool_call_message_id': tool_call_msg.id,
            'tool_result_message_id': tool_result_msg.id,
            'status': 'completed',
            'result': exec_result
        }

# ❌ NO ImageMessageHandler - not needed!
# ❌ NO FileMessageHandler - not needed!
```

### **3. Single send_message Function with Optional History ID**
```python
# chat_message_mixin.py - ONE function, optional history_id extraction
@expose('/sessions/{session_id}/send')
@expose('/sessions/{session_id}/histories/{history_id}/send')
def send_message(self, req: Request, session_id: int, history_id: int = None):
    """Send message to session - history_id is OPTIONAL in URL."""
    try:
        session = self._get_session(session_id)
        if not session:
            return self._format_error_response('Session not found', 404)
        
        # ✅ EXTRACT persona DIRECTLY from session
        persona = session.persona
        if not persona:
            return self._format_error_response('Session has no persona', 400)
        if not persona.is_active:
            return self._format_error_response('Persona is not active', 400)
        
        # ✅ OPTIONAL EXTRACTION: If no history_id provided, extract from session
        if history_id is None:
            history_id = session.current_history_id
            if not history_id:
                return self._format_error_response('No current history', 400)
        else:
            # Validate provided history_id belongs to session
            history = self._get_history(history_id)
            if not history or history.session_id != session_id:
                return self._format_error_response('History not found or invalid', 404)
        
        # Get user content - MUST be object with type
        payload = req.get_json(silent=True) or {}
        user_content = payload.get('content')
        if not user_content:
            return self._format_error_response('content required', 400)
        
        # ✅ MANDATORY: Content MUST be object with explicit type
        if not isinstance(user_content, dict) or 'type' not in user_content:
            return self._format_error_response('Content must be object with explicit type', 400)
        
        # Get message type
        message_type = user_content.get('type')
        if not message_type:
            return self._format_error_response('Message type is required', 400)
        
        # Get handler from registry
        handler = message_type_registry.get_handler(message_type)
        if not handler:
            return self._format_error_response(f'Unknown message type: {message_type}', 400)
        
        # ✅ PASS persona as DIRECT PARAMETER to handler
        result = handler.handle(
            chat_service=self,
            session=session,           # Session object
            persona=persona,           # ✅ PERSONA as DIRECT PARAMETER!
            history_id=history_id,     # ALWAYS provided (extracted or from URL)
            content=user_content
        )
        return jsonify({'data': result})
            
    except Exception as exc:
        db.session.rollback()
        return self._format_error_response(str(exc), 500)
```

### **4. Register ONLY the Handlers We Need**
```python
# chat_message_mixin.py - Register ONLY what we need
from .message_type_registry import message_type_registry
from .message_handlers import (
    ChatMessageHandler,           # ✅ Explicit chat messages
    ToolCallMessageHandler        # ✅ Tool calls
)

class ChatMessageMixin(WebSocketProtocol):
    def __init__(self):
        # Register ONLY the message type handlers we actually need
        message_type_registry.register('chat', ChatMessageHandler())           # ✅ Explicit chat
        message_type_registry.register('tool_call', ToolCallMessageHandler())  # ✅ Tool calls
        
        # ❌ NO image/file handlers - not needed yet!
        # ❌ NO DEFAULT HANDLER - all messages must have explicit type!
```

## 🎯 **FRONTEND IMPLEMENTATION**

### **1. UNIFIED sendMessage Method with Mandatory History ID**
```javascript
// ChatService.js - ONE method with mandatory historyId
async sendMessage(sessionId, historyId, content) {
    // historyId is MANDATORY parameter
    let url;
    if (historyId) {
        // Specific history
        url = `/chat/sessions/${sessionId}/histories/${historyId}/send`;
    } else {
        // Current history (extracted by backend)
        url = `/chat/sessions/${sessionId}/send`;
    }
    
    const response = await this.post(url, { content: content });
    return response.data;
}

// ❌ DELETE: sendMessageToHistory is now OBSOLETE!
// async sendMessageToHistory(sessionId, historyId, content) { ... }
```

### **2. Update ChatMessageContainer.vue (MANDATORY historyId)**
```javascript
// ChatMessageContainer.vue - REPLACE executeToolWithForm

// ❌ DELETE: Direct tool execution
const response = await chatService.executeTool(
    props.selectedSession.persona_id,
    selectedTool.value.name,
    args,
    props.historyId,
    null,
    props.selectedSession.id
);

// ✅ REPLACE WITH: UNIFIED message-based tool calls
const response = await chatService.sendMessage(
    props.selectedSession.id,           // sessionId
    props.historyId,                    // ✅ historyId as separate parameter
    {
        type: 'tool_call',              // MESSAGE TYPE
        tool: selectedTool.value.name,
        args: args
        // ✅ NO history_id in payload!
    }
);

// ✅ WebSocket events automatically handle:
// - message_received (tool call)
// - tool_status started
// - tool_status completed  
// - message_received (tool result)
```

### **3. Usage Examples (MANDATORY historyId)**
```javascript
// ✅ CORRECT: Chat messages (explicit type)
await chatService.sendMessage(sessionId, historyId, {
    type: 'chat',
    text: 'Hello world'
});

// ✅ CORRECT: Tool calls (explicit type)
await chatService.sendMessage(sessionId, historyId, {
    type: 'tool_call',
    tool: 'artist:list_albums',
    args: { artist_id: 123 }
});

// ❌ WRONG: No plain text allowed
// await chatService.sendMessage(sessionId, historyId, "Hello world");  // ❌ ERROR!
```

## 🚨 **WHAT TO DELETE (ALL OBSOLETE!)**

### **1. Backend: Delete Separate Tool Endpoint**
```python
# ❌ DELETE THIS ENTIRE METHOD from tool_execution_mixin.py
@expose('/personas/{persona_id}/tools/execute')
def persona_tool_execute(self, req: Request, persona_id: int):
    # This method is ARCHITECTURALLY WRONG
    # Personas cannot execute tools without session context
```

### **2. Frontend: Delete executeTool Method**
```javascript
// ❌ DELETE THIS ENTIRE METHOD from ChatService.js
async executeTool(personaId, toolName, toolArgs, historyId, userMessageId, sessionId = null) {
    // This method signature is WRONG
    // messageId is NEVER needed for UI tool calls - they're direct user actions!
}
```

### **3. Frontend: Delete Direct Tool Execution Calls**
```javascript
// ❌ DELETE ALL THESE from ChatMessageContainer.vue
const response = await chatService.executeTool(
    props.selectedSession.persona_id,
    selectedTool.value.name,
    args,
    props.historyId,
    null,
    props.selectedSession.id
);
```

### **4. Delete Plain Text Support**
```python
# ❌ DELETE: No plain text support
# ❌ DELETE: No TextMessageHandler
# ❌ DELETE: No default handler fallback
```

## ✅ **WHAT TO KEEP AND USE (CORRECTED!)**

### **1. Keep: UNIFIED Message Endpoints**
```python
# ✅ KEEP: UNIFIED send_message (handles ALL message types)
@expose('/sessions/{session_id}/send')                    # Current history
@expose('/sessions/{session_id}/histories/{history_id}/send')  # Specific history

# ❌ DELETE: send_message_to_history is now OBSOLETE!
```

### **2. Keep: Existing WebSocket Infrastructure**
```python
# ✅ KEEP: All existing WebSocket methods
self.emit_chat_event(session_id, history_id, 'message_received', data)
self.emit_llm_event(session_id, history_id, stage, message)
self.emit_tool_event(session_id, history_id, tool_name, status, **kwargs)
```

### **3. Keep: UNIFIED Frontend Method**
```javascript
// ✅ KEEP: UNIFIED sendMessage method
async sendMessage(sessionId, historyId, content)
// This method handles:
// - Current history (no history_id in URL)
// - Specific history (history_id in URL)

// ❌ DELETE: sendMessageToHistory is now OBSOLETE!
```

## 🎯 **BENEFITS OF CORRECTED SYSTEM**

### **1. Consistency**
- **All messages** go through same endpoints
- **All messages** get same WebSocket events
- **All messages** get same response format
- **All messages** use same validation and security

### **2. Simplicity**
- **One method** for all message types
- **No duplicate logic** between message types
- **Easy to add** new message types
- **Clean API design**

### **3. Maintainability**
- **Single code path** for all messages
- **Centralized message handling**
- **Easy to test** individual handlers
- **Clear separation of concerns**

### **4. Extensibility**
- **Add new message types** without touching core code
- **Register handlers** at runtime
- **Frontend automatically works** with new types
- **Consistent architecture** for future features

## 🚀 **IMPLEMENTATION ORDER**

### **Priority 1 (CRITICAL)**
1. Create MessageTypeRegistry and MessageTypeHandler classes
2. Create ChatMessageHandler and ToolCallMessageHandler
3. Modify send_message to detect message types
4. Register handlers in ChatMessageMixin
5. Add sendMessage method to ChatService

### **Priority 2 (HIGH)**
1. Update ChatMessageContainer.vue to use sendMessage
2. Test tool calls via message types
3. Verify WebSocket events work for tool calls
4. Test message flow in chat

### **Priority 3 (MEDIUM)**
1. Clean up old tool execution code
2. Update documentation
3. Performance testing

## ⚠️ **BREAKING CHANGES**

### **1. API Endpoint Changes**
- **OLD**: `POST /personas/{persona_id}/tools/execute`
- **NEW**: `POST /sessions/{session_id}/send` with `type: 'tool_call'`
- **Impact**: All frontend tool execution calls must be updated

### **2. Service Method Changes**
- **OLD**: `executeTool(personaId, toolName, args, historyId, messageId, sessionId)`
- **NEW**: `sendMessage(sessionId, historyId, { type: 'tool_call', tool: toolName, args: args })`
- **Impact**: All frontend service calls must be updated

### **3. Message Structure Changes**
- **OLD**: Direct tool execution with separate API
- **NEW**: Tool calls as message types through unified endpoint
- **Impact**: Frontend must send tool calls as message content

### **4. Plain Text Support Removed**
- **OLD**: Plain text messages supported
- **NEW**: Only object messages with explicit types allowed
- **Impact**: All messages must have explicit type field

## 🎯 **EXPECTED OUTCOMES**

### **1. Cleaner Architecture**
- **Unified message handling** for all types
- **No duplicate logic** between message types
- **Clear separation** of concerns

### **2. Better User Experience**
- **Real-time updates** for all message types
- **Consistent behavior** across message types
- **No polling required** - events push to UI

### **3. Maintainable Code**
- **Single code path** for all messages
- **Easy to add** new message types
- **Consistent API** contracts

### **4. Extensible System**
- **Add new message types** without touching core code
- **Frontend automatically works** with new types
- **Unified architecture** for future features

## 📝 **NOTES**

- **DO NOT** implement this incrementally - implement the complete system
- **DO** test thoroughly before deploying to production
- **DO** update all documentation and examples
- **DO** ensure WebSocket events work for all message types
- **DO NOT** support plain text messages - only objects with explicit types
- **DO** use existing WebSocket infrastructure
- **DO** follow the existing message flow patterns
- **DO** pass persona as direct parameter to handlers
- **DO** extract history_id from session if not provided in URL

This corrected unified message type system will result in a **CLEAN, MAINTAINABLE, and EXTENSIBLE** architecture where all message types (chat, tools) flow through the same endpoints with the same WebSocket events and same response formats. **NO plain text support - ONLY object messages with explicit types!**
