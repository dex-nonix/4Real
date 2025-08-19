# WebSocket Usage for Chat Service

## Overview

This document shows how the Chat Service uses the **EXISTING** Generic WebSocket System to provide real-time updates for LangChain LLM chat activities, tool execution, and message processing stages.

## Chat Service WebSocket Usage

### **NO @expose_ws Decorators for Chat**

The Chat Service does NOT use `@expose_ws` decorators. It only uses the **EXISTING** generic WebSocket methods from BaseApiService to emit events to existing channels.

```python
class ChatService(BaseApiService, ChatSessionMixin, ChatMessageMixin, ChatHistoryMixin, PersonaChatMixin, ToolExecutionMixin):
    """Chat service that uses EXISTING WebSocket methods for real-time LLM chat updates."""
    
    # NO @expose_ws decorators!
    # Chat service only emits events, doesn't expose WebSocket channels
    
    # ADD THESE METHODS to existing ChatService - NO NEW CLASSES!
    def emit_chat_event(self, session_id: int, history_id: int, event: str, data: dict):
        """Emit WebSocket event for chat session using EXISTING BaseApiService method."""
        channel = f'chat/{session_id}/{history_id}'
        self.send_to_channel(channel, event, data)

    def emit_llm_event(self, session_id: int, history_id: int, stage: str, message: str):
        """Emit LLM status event using EXISTING WebSocket method."""
        self.emit_chat_event(session_id, history_id, 'llm_status', {
            'stage': stage,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

    def emit_tool_event(self, session_id: int, history_id: int, tool_name: str, status: str, **extra):
        """Emit tool execution event using EXISTING WebSocket method."""
        self.emit_chat_event(session_id, history_id, 'tool_status', {
            'tool_name': tool_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **extra
        })
```

## Chat WebSocket Channels

### **Channel Structure**
```
chat/{session_id}/{history_id}
```

- **session_id**: Chat session identifier
- **history_id**: Message history within the session
- **Purpose**: All LLM chat activity for a specific session/history combination

### **Channel Events Emitted by Chat Service**

#### 1. LLM Message Processing Events
```python
# When message processing starts - use EXISTING ChatService method
self.emit_llm_event(session_id, history_id, 'message_processing', 'Processing your message...')

# When LLM starts thinking/analyzing - use EXISTING ChatService method
self.emit_llm_event(session_id, history_id, 'llm_thinking', 'LLM is analyzing your request...')

# When LLM decides to call a tool - use EXISTING ChatService method
self.emit_llm_event(session_id, history_id, 'tool_call_detected', f'LLM needs to call {tool_name}')

# When LLM is building final response - use EXISTING ChatService method
self.emit_llm_event(session_id, history_id, 'building_response', 'LLM is building your response...')

# When response is complete - use EXISTING ChatService method
self.emit_llm_event(session_id, history_id, 'response_complete', 'Response ready')
```

#### 2. Tool Execution Events
```python
# When tool execution starts - use EXISTING ChatService method
self.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)

# When tool execution completes - use EXISTING ChatService method
self.emit_tool_event(session_id, history_id, tool_name, 'completed', result=tool_result)

# When tool execution fails - use EXISTING ChatService method
self.emit_tool_event(session_id, history_id, tool_name, 'failed', error=str(exc))
```

#### 3. Message Status Events
```python
# When new message is received - use EXISTING ChatService method
self.emit_chat_event(session_id, history_id, 'message_received', {
    'message_id': message.id,
    'role': message.role,
    'content': message.content_json,
    'timestamp': message.created_at.isoformat()
})

# When message is fully processed - use EXISTING ChatService method
self.emit_chat_event(session_id, history_id, 'message_processed', {
    'message_id': message.id,
    'status': 'processed',
    'timestamp': datetime.utcnow().isoformat()
})
```

## Implementation in Existing Chat Methods

### **1. Tool Execution Mixin Integration**

```python
# In backend/app/services/chat_service/tool_execution_mixin.py
# NO NEW SIGNATURES - just add WebSocket calls to existing method

def persona_tool_execute(self, req: Request, persona_id: int):
    """Execute a tool for a specific persona - ADD WebSocket events to existing method."""
    try:
        payload = req.get_json(silent=True) or {}
        tool_name = payload.get('tool_name')
        tool_args = payload.get('args') or {}
        history_id = payload.get('history_id')
        user_message_id = payload.get('message_id')
        
        # Get session_id from request or derive it
        session_id = payload.get('session_id')  # Add this to request payload
        
        # Emit tool execution started event using EXISTING ChatService method
        self.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)
        
        # ... existing tool execution logic ...
        
        exec_result = execute_tool(persona.id, tool_name, tool_args)
        
        # Emit tool execution completed event using EXISTING ChatService method
        self.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)
        
        return jsonify({'data': exec_result})
        
    except Exception as exc:
        # Emit error event using EXISTING ChatService method
        self.emit_tool_event(session_id, history_id, tool_name, 'failed', error=str(exc))
        raise
```

### **2. Chat Message Mixin Integration**

```python
# In backend/app/services/chat_service/chat_message_mixin.py
# NO NEW SIGNATURES - just add WebSocket calls to existing method

def send_message(self, req: Request, id: int):
    """Send a message to a chat session - ADD WebSocket events to existing method."""
    try:
        # ... existing message sending logic ...
        
        # Get session_id and history_id from existing logic
        session_id = id  # This is already available
        history_id = history.id  # This is already available
        
        # Emit message processing started event using EXISTING ChatService method
        self.emit_llm_event(session_id, history_id, 'message_processing', 'Processing your message...')
        
        # When LLM calls a tool
        if isinstance(assistant_output, dict) and (assistant_output.get('type') == 'tool_call' or 'tool' in assistant_output):
            tool_name = assistant_output.get('tool')
            
            # Emit LLM tool call detected event using EXISTING ChatService method
            self.emit_llm_event(session_id, history_id, 'tool_call_detected', f'LLM needs to call {tool_name}')
            
            # ... existing tool execution logic ...
            
            # Emit tool execution started event using EXISTING ChatService method
            self.emit_tool_event(session_id, history_id, tool_name, 'started', args=tool_args)
            
            # Execute tool...
            exec_result = execute_tool(persona.id, tool_name, tool_args)
            
            # Emit tool execution completed event using EXISTING ChatService method
            self.emit_tool_event(session_id, history_id, tool_name, 'completed', result=exec_result)
            
            # Emit LLM building response event using EXISTING ChatService method
            self.emit_llm_event(session_id, history_id, 'building_response', 'LLM is building your response...')
        
        # Emit response complete event using EXISTING ChatService method
        self.emit_llm_event(session_id, history_id, 'response_complete', 'Response ready')
        
        return jsonify({'data': asst_msg.to_dict()})
        
    except Exception as exc:
        # ... error handling ...
```

## Frontend WebSocket Integration

### **1. Connect to Chat Channel - Use EXISTING ChatService**

```javascript
// In ChatMessageContainer.vue - NO NEW CLASSES
// ChatService ALREADY has WebSocket methods from BaseApiService

import { inject } from 'vue';

// Service injection for session management
const chatService = inject('chat-service');

// Join chat channel when component mounts using EXISTING ChatService method
onMounted(() => {
    if (props.selectedSession && props.historyId) {
        const channel = `chat/${props.selectedSession.id}/${props.historyId}`;
        
        // Use EXISTING ChatService WebSocket method
        chatService.joinChannel(channel);
    }
});
```

### **2. Listen to LLM Chat Events - Use EXISTING ChatService**

```javascript
// Listen for LLM message processing events using EXISTING ChatService method
onMounted(() => {
    if (props.selectedSession && props.historyId) {
        const channel = `chat/${props.selectedSession.id}/${props.historyId}`;
        
        // Use EXISTING ChatService WebSocket methods
        chatService.joinChannel(channel);
        
        // Listen for events using EXISTING methods
        chatService.onChannelEvent(channel, 'llm_status', handleLLMStatus);
        chatService.onChannelEvent(channel, 'tool_status', handleToolStatus);
        chatService.onChannelEvent(channel, 'message_received', handleMessageReceived);
        chatService.onChannelEvent(channel, 'message_processed', handleMessageProcessed);
    }
});

// Event handlers - NO NEW CLASSES
const handleLLMStatus = (data) => {
    const { stage, message, status, timestamp } = data;
    console.log('LLM Status:', stage, message, status);
    // Update UI state based on LLM stage
    updateLLMStatus(stage, message, status);
};

const handleToolStatus = (data) => {
    const { tool_name, status, result, error, timestamp } = data;
    console.log('Tool Status:', tool_name, status);
    // Update UI state based on tool status
    updateToolStatus(tool_name, status, result, error);
};

const handleMessageReceived = (data) => {
    const { message_id, role, content, timestamp } = data;
    console.log('Message Received:', message_id, role);
    // Add message to chat
    addMessageToChat(data);
};

const handleMessageProcessed = (data) => {
    const { message_id, status, timestamp } = data;
    console.log('Message Processed:', message_id, status);
    // Update message status
    updateMessageStatus(message_id, status);
};
```

## WebSocket Event Flow

### **1. LLM Chat Message Flow**

```
User sends message → Processing started → LLM thinking → Tool call detected → Tool execution → Response building → Complete
     ↓                ↓                  ↓            ↓               ↓               ↓              ↓
1. message_received → 2. llm_status → 3. llm_status → 4. llm_status → 5. tool_status → 6. llm_status → 7. llm_status
```

### **2. Tool Execution Flow**

```
LLM detects tool need → Tool execution started → Tool runs → Tool completed → LLM builds response
     ↓                    ↓                      ↓           ↓               ↓
1. llm_status → 2. tool_status → 3. tool_running → 4. tool_status → 5. llm_status
```

## Benefits for LLM Chat Service

### **1. Real-time LLM Status**
- **Users see LLM thinking progress** in real-time
- **No need to wait** for complete response
- **Immediate feedback** on each processing stage

### **2. Real-time Tool Execution**
- **Users see tool calls** as they happen
- **Live tool execution status** - started, running, completed
- **Real-time tool results** integration

### **3. Better User Experience**
- **Progressive response building** - see LLM working
- **No polling required** - events push to UI
- **Responsive interface** - immediate feedback on each stage

### **4. LangChain Integration**
- **Standard LLM chat events** - thinking, tool calls, processing
- **Event-based architecture** - listen to each processing stage
- **Asynchronous message extension** - build response progressively

## Integration Points

### **1. Existing HTTP Endpoints**
- **No changes needed** to current HTTP API endpoints
- **WebSocket events emitted** after successful HTTP operations
- **Same request/response flow** maintained

### **2. Database Operations**
- **WebSocket events emitted** after database commits
- **Real-time updates** reflect actual database state
- **No race conditions** between HTTP and WebSocket

### **3. Error Handling**
- **WebSocket error events** for failed operations
- **Consistent error reporting** across HTTP and WebSocket
- **User feedback** for all operation outcomes

## Implementation Checklist

### **Backend Changes Required:**
- [ ] **ADD WebSocket event methods to existing ChatService** (NO NEW CLASSES)
- [ ] **ADD WebSocket calls to existing tool_execution_mixin.py** (NO NEW SIGNATURES)
- [ ] **ADD WebSocket calls to existing chat_message_mixin.py** (NO NEW SIGNATURES)
- [ ] **Test WebSocket event emission** using existing methods

### **Frontend Changes Required:**
- [ ] **Use EXISTING ChatService WebSocket methods** in ChatMessageContainer.vue
- [ ] **Implement real-time event handlers** using existing methods
- [ ] **Add reactive state for real-time updates** (NO NEW CLASSES)
- [ ] **Test real-time functionality** using existing infrastructure

### **Key Principles:**
- **NO NEW CLASSES** - use existing ChatService
- **NO NEW SIGNATURES** - just add WebSocket calls to existing methods
- **NO NEW SERVICES** - ChatService already has everything needed
- **Use EXISTING BaseApiService WebSocket methods** - they're already there
- **Frontend uses existing ChatService** - no new injection needed

This implementation leverages the **100% complete WebSocket infrastructure** and requires only **adding WebSocket event emission calls** to existing chat methods and **using existing ChatService WebSocket methods** in the frontend. No new infrastructure, no new classes, no new services - just use what we already have!
