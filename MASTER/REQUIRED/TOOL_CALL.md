# TOOL CALL SYSTEM REQUIREMENTS & IMPLEMENTATION

## 🎯 **OVERVIEW**
The system needs to show ALL tool calls the same way - whether executed by AI/LLM or directly by the user from the UI. The only difference should be marking who executed it.

## 🔧 **CURRENT IMPLEMENTATION STATUS**

### **1. Backend Tool Execution (tool_execution_mixin.py)**
- ✅ **Direct UI tool calls**: Creates messages with `message_type='tool'`
- ✅ **Metadata structure**: `{toolName, toolParams, executionStatus, result, executedBy, executionTime}`
- ✅ **Executor marking**: Marks as `'user'` for direct UI calls
- ✅ **ToolInvocationLog**: Logs execution details

### **2. Frontend Tool Display (ToolMessage.vue)**
- ✅ **Enhanced component**: Shows executor, parameters, result, status, time
- ✅ **Metadata support**: Handles both old and new metadata formats
- ✅ **Executor display**: Shows "Executed by User" vs "Executed by AI"

### **3. Frontend Tool Execution (ChatMessageContainer.vue)**
- ✅ **Immediate display**: Shows tool results in chat immediately
- ✅ **Local message creation**: Creates tool messages locally before backend refresh
- ✅ **Error handling**: Shows error messages for failed tool executions

## ❌ **CRITICAL GAPS & ISSUES**

### **1. Backend Message Type Inconsistency (CRITICAL)**
- **tool_execution_mixin.py**: Uses `message_type='tool'` ✅
- **chat_message_mixin.py**: Still uses `message_type='tool_result'` ❌
- **Database model**: Only supports `tool_call|tool_result`, not `tool` ❌

### **2. Missing Real-Time Tool Status Tracking**
- **No "started" status**: User doesn't see when tool execution begins
- **No progress updates**: No real-time status updates during execution
- **No async handling**: Tool calls are async but frontend only sees final result

### **3. Content Structure Mismatch**
- **AI tool calls**: Use old format `{type: 'tool_result', tool, input, output}`
- **Direct tool calls**: Use new format `{toolName, toolParams, executionStatus, result}`
- **Frontend expects**: New format but backend AI calls use old format

## 🚀 **REQUIRED IMPLEMENTATION**

### **1. Fix Backend Message Types**
```python
# Update database model to support 'tool' message type
message_type = db.Column(db.String(50), nullable=False)  # text|tool_call|tool_result|tool|image|file

# Update chat_message_mixin.py to use 'tool' instead of 'tool_result'
message_type='tool'  # Standardize all tool messages

# Ensure all tool executions create consistent metadata structure
content_json = {
    'toolName': tool_name,
    'toolParams': tool_args,
    'executionStatus': 'started|running|success|error',
    'result': exec_result,
    'executedBy': 'ai|user',
    'executionTime': timestamp,
    'startedAt': start_timestamp,
    'completedAt': completion_timestamp
}
```

### **2. Implement Real-Time Tool Status Tracking**
```python
# Backend: Create immediate "started" message
tool_msg = ChatMessage(
    history_id=history_id,
    role='tool',
    message_type='tool',
    content_json={
        'toolName': tool_name,
        'toolParams': tool_args,
        'executionStatus': 'started',
        'executedBy': 'user',
        'startedAt': datetime.utcnow().isoformat()
    }
)

# After execution, update the message with result
tool_msg.content_json.update({
    'executionStatus': 'success' if success else 'error',
    'result': exec_result,
    'completedAt': datetime.utcnow().isoformat()
})
```

### **3. Frontend Real-Time Updates**
```javascript
// Show "started" status immediately
const startedMessage = {
  id: Date.now(),
  message_type: 'tool',
  role: 'tool',
  content_json: {
    toolName: selectedTool.value.name,
    toolParams: args,
    executionStatus: 'started',
    executedBy: 'user',
    startedAt: new Date().toISOString()
  }
};
messages.value.push(startedMessage);

// Update status to "running" during execution
// Update status to "success/error" when complete
```

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Fix Message Type Consistency**
- [ ] Update database model to support `tool` message type
- [ ] Fix chat_message_mixin.py to use `tool` instead of `tool_result`
- [ ] Standardize all tool message metadata structure
- [ ] Test both AI and direct tool calls use same format

### **Phase 2: Implement Real-Time Status Tracking**
- [ ] Create immediate "started" message when tool execution begins
- [ ] Update message status to "running" during execution
- [ ] Update message status to "success/error" when complete
- [ ] Frontend shows real-time status updates

### **Phase 3: Enhanced Tool Display**
- [ ] Show execution start time
- [ ] Show execution completion time
- [ ] Show execution duration
- [ ] Show progress indicators for long-running tools

## 🎯 **EXPECTED RESULT**

### **Tool Execution Flow:**
```
1. User clicks "Execute Tool" → Shows "started" message immediately
2. Tool runs → Status updates to "running" 
3. Tool completes → Status updates to "success/error" with result
4. All tool calls look identical except executor label
```

### **Chat Display:**
```
🔧 Tool Started: track:list_by_album - Status: started (Executed by User)
⏳ Tool Running: track:list_by_album - Status: running (Executed by User)  
✅ Tool Completed: track:list_by_album - Status: success (Executed by User)
```

## 🚨 **CURRENT STATUS**
- **Direct tool calls**: Partially working, show results but no status progression
- **AI tool calls**: Broken, use old format incompatible with new frontend
- **Real-time updates**: Not implemented, only see final results
- **Message consistency**: Broken, two different formats in use

**PRIORITY: Fix backend message type consistency first, then implement real-time status tracking.**
