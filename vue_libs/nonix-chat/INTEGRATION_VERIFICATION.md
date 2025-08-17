# CHAT SYSTEM INTEGRATION VERIFICATION

## OVERVIEW
This document tracks the complete backend schema restructuring and frontend UI adaptations needed to implement the new chat system architecture.

## CURRENT BROKEN STRUCTURE vs DESIRED STRUCTURE

### CURRENT (WRONG):
- **Multiple ChatSessions** per persona (confusing)
- **Session = Chat** (wrong concept)
- **History = Messages within one session** (limited)
- **Multiple tabs/sessions** to manage (UI nightmare)

### DESIRED (CORRECT):
- **Multiple Sessions per Persona** (can have 10+ sessions with same persona)
- **Session = Active Chat with Persona** (clear concept)
- **Multiple Histories per Session** (previous conversations)
- **Switch between histories** within the same session (clean UI)

## BACKEND SCHEMA CHANGES REQUIRED

### 1. PERSONA TABLE (Enhanced)
```python
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    avatar_url = db.Column(db.String(512), nullable=True)  # NEW: Optional avatar
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    system_prompt = db.Column(db.Text)
    metadata_json = db.Column(db.JSON)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=True)
    ai_model_mapping_id = db.Column(db.Integer, db.ForeignKey('ai_model_mappings.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # NEW: Multiple sessions per persona
    chat_sessions = db.relationship('ChatSession', backref='persona', lazy=True)
```

**CHANGES NEEDED:**
- [ ] Add `avatar_url` column (nullable, optional)
- [ ] Keep relationship as `chat_sessions` (one-to-many)
- [ ] Add avatar fallback logic: if no avatar_url, use first 2 characters of name

### 2. CHAT_SESSION TABLE (Major Restructure)
```python
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)  # NOT unique - multiple sessions per persona
    session_name = db.Column(db.String(255))  # NEW: Optional custom name
    session_icon = db.Column(db.String(512))  # NEW: Optional custom icon
    current_history_id = db.Column(db.Integer, db.ForeignKey('chat_histories.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('1'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    persona = db.relationship('Persona', backref=db.backref('chat_sessions', lazy=True))
    current_history = db.relationship('ChatHistory', foreign_keys=[current_history_id])
    histories = db.relationship('ChatHistory', backref='session', lazy=True)
```

**CHANGES NEEDED:**
- [ ] Remove `title` column (replaced by `session_name`)
- [ ] Remove `created_by` column (not needed)
- [ ] Add `session_name` column
- [ ] Add `session_icon` column
- [ ] Add `current_history_id` column
- [ ] Add `is_active` column
- [ ] Keep `persona_id` NOT unique (allow multiple sessions per persona)
- [ ] Keep relationship as `persona` (one-to-many)
- [ ] Add new relationships for histories

### 3. NEW CHAT_HISTORY TABLE (Replaces old session concept)
```python
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)  # "Chat about music", "Album discussion"
    summary = db.Column(db.Text)  # AI-generated summary
    message_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = db.relationship('ChatSession', backref=db.backref('histories', lazy=True))
    messages = db.relationship('ChatMessage', backref='history', lazy=True)
```

**CHANGES NEEDED:**
- [ ] Create new table
- [ ] Add all columns and relationships

### 4. CHAT_MESSAGE TABLE (Restructure)
```python
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('chat_histories.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # system|user|assistant|tool
    message_type = db.Column(db.String(50), nullable=False)  # text|tool_call|tool_result|image|file
    content_json = db.Column(db.JSON)  # Structured content
    parent_message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    history = db.relationship('ChatHistory', backref=db.backref('messages', lazy=True))
    parent_message = db.relationship('ChatMessage', remote_side=[id], backref='child_messages')
```

**CHANGES NEEDED:**
- [ ] Change `session_id` to `history_id`
- [ ] Add `message_type` column
- [ ] Add `parent_message_id` column
- [ ] Update relationships from `session` to `history`
- [ ] Add self-referencing relationship for threading

### 5. TOOL_INVOCATION_LOG TABLE (Fix relationships)
```python
class ToolInvocationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('chat_histories.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=False)
    tool_name = db.Column(db.String(255), nullable=False)
    input_json = db.Column(db.JSON)
    output_json = db.Column(db.JSON)
    status = db.Column(db.String(50), nullable=False)  # started|success|error|timeout
    started_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    
    # Relationships
    history = db.relationship('ChatHistory', backref=db.backref('tool_logs', lazy=True))
    message = db.relationship('ChatMessage', backref=db.backref('tool_logs', lazy=True))
```

**CHANGES NEEDED:**
- [ ] Change `session_id` to `history_id`
- [ ] Make `message_id` required (not nullable)
- [ ] Update relationships

## NEW API ENDPOINTS REQUIRED

### 1. PERSONA MANAGEMENT
- [ ] `GET /api/personas` - List all available personas
- [ ] `GET /api/personas/{id}` - Get persona details
- [ ] `POST /api/personas/{id}/start-chat` - Create/activate session for persona

### 2. SESSION MANAGEMENT
- [ ] `GET /api/chat-sessions` - List active sessions (personas)
- [ ] `GET /api/chat-sessions/{id}` - Get session details
- [ ] `PUT /api/chat-sessions/{id}` - Update session name/icon
- [ ] `DELETE /api/chat-sessions/{id}` - End session

### 3. HISTORY MANAGEMENT
- [ ] `GET /api/chat-sessions/{id}/histories` - List conversation histories
- [ ] `POST /api/chat-sessions/{id}/histories` - Start new conversation
- [ ] `GET /api/chat-sessions/{id}/histories/{history_id}` - Get specific history
- [ ] `PUT /api/chat-sessions/{id}/histories/{history_id}` - Rename history
- [ ] `DELETE /api/chat-sessions/{id}/histories/{history_id}` - Delete history

### 4. MESSAGE MANAGEMENT
- [ ] `GET /api/chat-sessions/{id}/histories/{history_id}/messages` - Get messages
- [ ] `POST /api/chat-sessions/{id}/histories/{history_id}/send` - Send message
- [ ] `POST /api/chat-sessions/{id}/histories/{history_id}/retry` - Retry last message

## BACKEND SERVICE CHANGES

### 1. ChatService.py
**CHANGES NEEDED:**
- [ ] Restructure all methods to use new schema
- [ ] Update session creation logic
- [ ] Add history management methods
- [ ] Fix message handling for histories
- [ ] Update tool execution logic

### 2. ChatSessionService.py
**CHANGES NEEDED:**
- [ ] Update to handle new session structure
- [ ] Add history management
- [ ] Update CRUD operations

### 3. ChatMessageService.py
**CHANGES NEEDED:**
- [ ] Update to work with histories instead of sessions
- [ ] Add message threading support
- [ ] Update message retrieval logic

### 4. PersonaService.py
**CHANGES NEEDED:**
- [ ] Add session creation logic
- [ ] Update persona retrieval to include session info

## FRONTEND UI COMPONENT ADAPTATIONS

### 1. Chat.vue (Main Container)
**CHANGES NEEDED:**
- [ ] Change props from `sessions` to `personas` (available personas)
- [ ] Change state from `selectedSessionId` to `selectedPersonaId` + `selectedSessionId`
- [ ] Update logic to load sessions for selected persona, then histories for selected session
- [ ] Update emit handlers for new structure

### 2. ChatHeader.vue (Header with Persona Info)
**CHANGES NEEDED:**
- [ ] Change props from `user` to `persona` + `currentHistory`
- [ ] Add editable history title (inline editing)
- [ ] Add history management dropdown
- [ ] Update display logic for persona vs history info

### 3. ChatSessionBar.vue (Left Sidebar)
**CHANGES NEEDED:**
- [ ] Change props from `sessions` to `personas` (available personas)
- [ ] Update display to show persona avatars (with fallback to 2-character initials)
- [ ] Update add button to open persona selection dialog
- [ ] Change from session selection to persona selection
- [ ] Add session management within persona (multiple sessions per persona)

### 4. ChatMessages.vue (Message Display)
**CHANGES NEEDED:**
- [ ] Update to load messages from current history
- [ ] Add loading states when history changes
- [ ] Update message context handling

### 5. ChatMessageInput.vue (Input Area)
**CHANGES NEEDED:**
- [ ] Add context awareness for current history
- [ ] Update send logic to target current history
- [ ] Add tools menu integration

### 6. ChatRuntimeService.js (Backend Communication)
**CHANGES NEEDED:**
- [ ] Complete restructure for new endpoints
- [ ] Add new methods:
  - `getPersonas()`
  - `getSessions(personaId)` - Get all sessions for a persona
  - `createSession(personaId, sessionName?, sessionIcon?)` - Create new session with persona
  - `getHistories(sessionId)` - Get histories within a session
  - `createHistory(sessionId, title)` - Create new history within session
  - `sendMessage(historyId, content)` - Send message to specific history
- [ ] Update existing methods for new schema

## DATA FLOW IMPLEMENTATION

### 1. User selects Persona
- [ ] System shows existing sessions for that persona OR creates new session
- [ ] User can have multiple sessions with same persona (e.g., "Music Chat", "Album Discussion")
- [ ] Each session has its own histories and current conversation
- [ ] Updates UI to show selected persona and available sessions

### 2. User starts new conversation
- [ ] Creates new ChatHistory within the existing session
- [ ] Updates session.current_history_id to point to new history
- [ ] All new messages go to this history
- [ ] Updates UI to show new history

### 3. User switches to old conversation
- [ ] Changes session.current_history_id to point to existing history
- [ ] Loads messages from that history
- [ ] No new session needed
- [ ] Updates UI to show selected history

### 4. Session Bar shows
- [ ] Persona avatars (can have multiple sessions per persona)
- [ ] Each session can have custom name/icon
- [ ] List of histories within selected session
- [ ] Current active history (highlighted)

## MIGRATION STEPS

### Phase 1: Database Schema
- [ ] Create new ChatHistory table
- [ ] Update existing tables with new columns
- [ ] Migrate existing data to new structure
- [ ] Update all foreign key relationships

### Phase 2: Backend Services
- [ ] Update all model relationships
- [ ] Restructure ChatService
- [ ] Update all CRUD services
- [ ] Add new API endpoints

### Phase 3: Frontend Integration
- [ ] Update ChatRuntimeService
- [ ] Modify all Vue components
- [ ] Update data flow logic
- [ ] Test UI interactions

### Phase 4: Testing & Validation
- [ ] Test all new endpoints
- [ ] Validate UI functionality
- [ ] Test data persistence
- [ ] Performance testing

## BENEFITS OF NEW STRUCTURE

1. **Cleaner UI**: Multiple sessions per persona, multiple histories within each session
2. **Better UX**: Easy to switch between conversation topics and different session contexts
3. **Proper relationships**: Clear parent-child structure (Persona → Sessions → Histories → Messages)
4. **Scalable**: Can handle many sessions per persona, many conversations per session
5. **Logical**: Session = specific chat context, History = conversation thread within session
6. **Flexible naming**: Persona defaults + optional custom names/icons per session
7. **Avatar fallback**: Automatic 2-character initials if no avatar_url set

## NOTES

- **No backward compatibility** - complete schema redesign
- **All existing data** needs migration to new structure
- **Frontend UI** is mostly ready, needs backend connection
- **Tool integration** needs complete restructuring
- **MCP server integration** needs updating for new schema
