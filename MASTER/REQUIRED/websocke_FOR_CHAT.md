# WebSocket Usage for Chat Service

## Overview

This document shows how the Chat Service uses the Generic WebSocket System to provide real-time updates for LangChain LLM chat activities, tool execution, and message processing stages.

## Chat Service WebSocket Usage

### **NO @expose_ws Decorators for Chat**

The Chat Service does NOT use `@expose_ws` decorators. It only uses the generic WebSocket methods from BaseApiService to emit events to existing channels.

```python
class ChatService(BaseApiService):
    """Chat service that uses generic WebSocket methods for real-time LLM chat updates."""
    
    # NO @expose_ws decorators!
    # Chat service only emits events, doesn't expose WebSocket channels
    
    def execute_tool(self, tool_name, args, session_id, history_id):
        """Execute tool and emit real-time updates via WebSocket."""
        
        # Execute tool via HTTP (already implemented)
        result = self.run_tool(tool_name, args, session_id, history_id)
        
        # Emit tool execution events using generic WebSocket methods
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='tool_execution_completed',
            data={
                'tool_name': tool_name,
                'result': result,
                'status': 'completed',
                'execution_time': datetime.utcnow().isoformat()
            }
        )
        
        return result
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
# When message processing starts
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='message_processing_started',
    data={
        'message_id': message.id,
        'status': 'processing',
        'stage': 'initial_processing',
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When LLM starts thinking/analyzing
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='llm_thinking',
    data={
        'message_id': message.id,
        'status': 'thinking',
        'stage': 'llm_analysis',
        'message': 'LLM is analyzing your request...',
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When LLM decides to call a tool
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='llm_tool_call_detected',
    data={
        'message_id': message.id,
        'tool_name': 'artist:list_albums',
        'status': 'tool_call_detected',
        'reason': 'LLM needs to fetch artist data to answer your question',
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When LLM is building final response
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='llm_building_response',
    data={
        'message_id': message.id,
        'status': 'building_response',
        'stage': 'final_response_generation',
        'message': 'LLM is building your response...',
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When response is complete
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='response_complete',
    data={
        'message_id': message.id,
        'status': 'complete',
        'final_response': response_text,
        'timestamp': datetime.utcnow().isoformat()
    }
)
```

#### 2. Tool Execution Events
```python
# When tool execution starts
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='tool_execution_started',
    data={
        'message_id': message.id,
        'tool_name': 'artist:list_albums',
        'status': 'started',
        'args': tool_args,
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When tool execution completes
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='tool_execution_completed',
    data={
        'message_id': message.id,
        'tool_name': 'artist:list_albums',
        'result': tool_result,
        'status': 'completed',
        'execution_time': '1.2s',
        'timestamp': datetime.utcnow().isoformat()
    }
)

# When tool execution fails
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='tool_execution_failed',
    data={
        'message_id': message.id,
        'tool_name': 'artist:list_albums',
        'error': 'Artist not found',
        'status': 'failed',
        'timestamp': datetime.utcnow().isoformat()
    }
)
```

#### 3. Message Status Events
```python
# When new message is received
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='message_received',
    data={
        'message_id': message.id,
        'role': message.role,
        'content': message.content_json,
        'timestamp': message.created_at.isoformat()
    }
)

# When message is fully processed
self.send_to_channel(
    channel=f'chat/{session_id}/{history_id}',
    event='message_processed',
    data={
        'message_id': message.id,
        'status': 'processed',
        'timestamp': datetime.utcnow().isoformat()
    }
)
```

## Implementation in Existing Chat Methods

### **1. Tool Execution Mixin Integration**

```python
# In backend/app/services/chat_service/tool_execution_mixin.py

def persona_tool_execute(self, req: Request, persona_id: int):
    """Execute a tool for a specific persona."""
    try:
        # ... existing tool execution logic ...
        
        # Emit tool execution started event
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='tool_execution_started',
            data={
                'message_id': user_message_id,
                'tool_name': tool_name,
                'status': 'started',
                'args': tool_args,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Execute tool
        exec_result = execute_tool(persona.id, tool_name, tool_args)
        
        # Emit WebSocket event for real-time UI updates
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='tool_execution_completed',
            data={
                'message_id': user_message_id,
                'tool_name': tool_name,
                'result': exec_result,
                'status': 'success' if exec_result.get('status') == 'success' else 'error',
                'execution_time': datetime.utcnow().isoformat()
            }
        )
        
        return jsonify({'data': exec_result})
        
    except Exception as exc:
        # Emit error event
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='tool_execution_failed',
            data={
                'message_id': user_message_id,
                'tool_name': tool_name,
                'error': str(exc),
                'status': 'failed',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        raise
```

### **2. Chat Message Mixin Integration**

```python
# In backend/app/services/chat_service/chat_message_mixin.py

def send_message(self, req: Request, id: int):
    """Send a message to a chat session."""
    try:
        # ... existing message sending logic ...
        
        # Emit message processing started event
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='message_processing_started',
            data={
                'message_id': user_msg.id,
                'status': 'processing',
                'stage': 'initial_processing',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # When LLM calls a tool
        if isinstance(assistant_output, dict) and (assistant_output.get('type') == 'tool_call' or 'tool' in assistant_output):
            # Emit LLM tool call detected event
            self.send_to_channel(
                channel=f'chat/{session_id}/{history_id}',
                event='llm_tool_call_detected',
                data={
                    'message_id': user_msg.id,
                    'tool_name': tool_name,
                    'status': 'tool_call_detected',
                    'reason': 'LLM needs to fetch data to answer your question',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # ... existing tool execution logic ...
            
            # Emit tool execution started event
            self.send_to_channel(
                channel=f'chat/{session_id}/{history_id}',
                event='tool_execution_started',
                data={
                    'message_id': user_msg.id,
                    'tool_name': tool_name,
                    'status': 'started',
                    'args': tool_args,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Execute tool...
            exec_result = execute_tool(persona.id, tool_name, tool_args)
            
            # Emit tool execution completed event
            self.send_to_channel(
                channel=f'chat/{session_id}/{history_id}',
                event='tool_execution_completed',
                data={
                    'message_id': user_msg.id,
                    'tool_name': tool_name,
                    'result': exec_result,
                    'status': 'completed',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Emit LLM building response event
            self.send_to_channel(
                channel=f'chat/{session_id}/{history_id}',
                event='llm_building_response',
                data={
                    'message_id': user_msg.id,
                    'status': 'building_response',
                    'stage': 'final_response_generation',
                    'message': 'LLM is building your response...',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
        
        # Emit response complete event
        self.send_to_channel(
            channel=f'chat/{session_id}/{history_id}',
            event='response_complete',
            data={
                'message_id': user_msg.id,
                'status': 'complete',
                'final_response': asst_msg.content_json,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return jsonify({'data': asst_msg.to_dict()})
        
    except Exception as exc:
        # ... error handling ...
```

## Frontend WebSocket Integration

### **1. Connect to Chat Channel**

```javascript
// In ChatMessageContainer.vue or similar component
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000/api/ws/');

// Join chat channel when component mounts
onMounted(() => {
    if (props.selectedSession && props.historyId) {
        const channel = `chat/${props.selectedSession.id}/${props.historyId}`;
        socket.emit('join_channel', { channel });
    }
});
```

### **2. Listen to LLM Chat Events**

```javascript
// Listen for LLM message processing events
socket.on('chat/123/456:message_processing_started', (data) => {
    console.log('Message processing started:', data);
    // Show processing indicator
    showMessageProcessingStatus(data.message_id, 'processing');
});

socket.on('chat/123/456:llm_thinking', (data) => {
    console.log('LLM thinking:', data);
    // Show thinking indicator with message
    showLLMThinkingStatus(data.message_id, data.message);
});

socket.on('chat/123/456:llm_tool_call_detected', (data) => {
    console.log('LLM tool call detected:', data);
    // Show tool call indicator
    showToolCallDetected(data.message_id, data.tool_name, data.reason);
});

socket.on('chat/123/456:llm_building_response', (data) => {
    console.log('LLM building response:', data);
    // Show response building indicator
    showResponseBuildingStatus(data.message_id, data.message);
});

socket.on('chat/123/456:response_complete', (data) => {
    console.log('Response complete:', data);
    // Hide all indicators, show final response
    hideAllProcessingIndicators(data.message_id);
    showFinalResponse(data);
});

// Listen for tool execution events
socket.on('chat/123/456:tool_execution_started', (data) => {
    console.log('Tool execution started:', data);
    // Show tool execution loading indicator
    showToolExecutionStatus(data.message_id, data.tool_name, 'started');
});

socket.on('chat/123/456:tool_execution_completed', (data) => {
    console.log('Tool execution completed:', data);
    // Hide loading indicator, show tool results
    hideToolExecutionStatus(data.message_id);
    showToolResults(data.message_id, data);
});

socket.on('chat/123/456:tool_execution_failed', (data) => {
    console.log('Tool execution failed:', data);
    // Show error message
    showToolExecutionError(data.message_id, data.error);
});

// Listen for message events
socket.on('chat/123/456:message_received', (data) => {
    console.log('Message received:', data);
    // Add message to chat
    addMessageToChat(data);
});

socket.on('chat/123/456:message_processed', (data) => {
    console.log('Message processed:', data);
    // Update message status
    updateMessageStatus(data.message_id, 'processed');
});
```

## WebSocket Event Flow

### **1. LLM Chat Message Flow**

```
User sends message → Processing started → LLM thinking → Tool call detected → Tool execution → Response building → Complete
     ↓                ↓                  ↓            ↓               ↓               ↓              ↓
1. message_received → 2. processing_started → 3. llm_thinking → 4. tool_call_detected → 5. tool_execution → 6. building_response → 7. response_complete
```

### **2. Tool Execution Flow**

```
LLM detects tool need → Tool execution started → Tool runs → Tool completed → LLM builds response
     ↓                    ↓                      ↓           ↓               ↓
1. tool_call_detected → 2. tool_execution_started → 3. tool_running → 4. tool_execution_completed → 5. llm_building_response
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

This implementation shows how the Chat Service uses the Generic WebSocket System to provide real-time LLM chat updates, including thinking stages, tool calls, and progressive response building, without needing to implement custom WebSocket logic or use @expose_ws decorators.
