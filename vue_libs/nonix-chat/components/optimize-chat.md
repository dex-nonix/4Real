# Nonix Chat Optimization Plan

## **Current Architecture Problems**

### **God Component Pattern (ChatWidget.vue)**
- Manages all state (`sessions`, `messages`, `currentSessionId`, `currentHistoryId`)
- Handles all API calls through `ChatRuntimeService`
- Orchestrates communication between child components
- Passes data down through props
- Receives events up through emits
- Controls session switching and message loading

### **Component Responsibilities (Current)**
1. **`ChatWidget.vue`** - God component managing everything
2. **`Chat.vue`** - Layout orchestrator, passes data down
3. **`ChatSessionBar.vue`** - Displays sessions, emits selection events
4. **`ChatMessages.vue`** - Displays messages, receives via props
5. **`ChatMessageInput.vue`** - Input field, emits send events
6. **`ChatHeader.vue`** - Header with session info
7. **`PersonaSelectionDialog.vue`** - Persona selection
8. **`HistoryManagementDialog.vue`** - History management

## **Refactoring Requirements**

### **1. Session Management Decentralization**
**Current Problem**: `ChatWidget` loads and manages all sessions
**Required Change**: `ChatSessionBar` should:
- Load its own sessions independently
- Manage session state internally
- Emit events when sessions are added/removed
- Control its own session switching

### **2. Message Management Consolidation**
**Current Problem**: Messages are managed in `ChatWidget` and passed down
**Required Change**: Create a unified `ChatMessageContainer` component that:
- Combines `ChatMessages` + `ChatMessageInput`
- Manages its own message state
- Handles message persistence per session
- Maintains input content when switching sessions

### **3. Event-Driven Architecture**
**Current Problem**: Top-down data flow with props drilling
**Required Change**: Components should communicate via events:
- `ChatSessionBar` emits: `session-added`, `session-removed`, `session-selected`
- `ChatMessageContainer` emits: `message-sent`, `message-received`
- Parent components listen and coordinate without managing internal state

## **New Simple Tab-Based Architecture**

### **Component Structure**
```
ChatView (page/view that uses Chat component)
└── Chat (manages selectedSession observable)
    ├── ChatSessionBar (loads sessions, emits session-selected)
    ├── ChatHeader (receives selectedSession, shows title/info)
    └── ChatMessageContainer[] (one per session, hide/show like tabs)
        ├── ChatMessages (displays messages for selectedSession)
        └── ChatMessageInput (input field for selectedSession)
```

### **How It Works**
1. **`Chat`** component has `selectedSession` observable variable
2. **`ChatSessionBar`** loads sessions and emits `session-selected` with session object
3. **`Chat`** updates `selectedSession` when event received
4. **All child components** automatically react to `selectedSession` changes
5. **No component destruction** - just CSS display: none/block
6. **All data stays in memory** - messages, input text, everything

### **Event Flow (Simple)**
```
ChatSessionBar emits: "session-selected" with full session object
Chat updates selectedSession observable variable
All child components automatically react to selectedSession changes
ChatMessageContainer emits: "message-sent" 
Chat forwards events up to parent
```

### **State Management (In Memory Only)**
- **Sessions**: In `ChatSessionBar` memory
- **selectedSession**: Observable variable in `Chat` component
- **Messages per session**: In each `ChatMessageContainer` memory  
- **Input text per session**: In each `ChatMessageContainer` memory
- **Current visible session**: Just CSS display property
- **All components**: React to `selectedSession` changes automatically

## **Why This Approach is Better**

1. **No overengineering** - Just hide/show components
2. **No data loss** - Everything stays in memory
3. **No complex state management** - Each component owns its data
4. **Tab-like behavior** - Exactly what you want
5. **Simple events** - Components just tell each other what happened

## **What Gets Removed**
- ❌ Local storage
- ❌ Complex state management  
- ❌ Data passing through props
- ❌ Component destruction/recreation
- ❌ Overcomplicated event bus

## **What Gets Added**
- ✅ Simple hide/show logic
- ✅ One container per session
- ✅ Direct service calls in components
- ✅ Basic event emission
- ✅ Memory-based data persistence

## **Implementation Steps**

### **Phase 1: Refactor ChatSessionBar**
- Move session loading logic from ChatWidget to ChatSessionBar
- Add session management methods (add, remove, select)
- Emit events for session changes

### **Phase 2: Create ChatMessageContainer**
- Combine ChatMessages + ChatMessageInput into one component
- Add session-specific data management
- Handle message loading per session
- React to selectedSession changes automatically

### **Phase 3: Update Chat Component**
- Add selectedSession observable variable
- Make all child components react to selectedSession changes
- Handle session-selected events from ChatSessionBar
- Coordinate visibility based on selectedSession

### **Phase 3.5: Transform ChatWidget to ChatView**
- Rename ChatWidget.vue to ChatView.vue
- Remove all component logic and state management
- Make it a simple page/view that uses Chat component
- Handle URL routing and page-level concerns
- Pass any necessary props to Chat component

### **Phase 4: Clean Up**
- Remove unused props and state
- Update event handling
- Test session switching behavior

## **Key Benefits**

1. **Separation of Concerns**: Each component manages its own domain
2. **Event-Driven**: Loose coupling between components
3. **State Persistence**: Messages and input content preserved per session
4. **Maintainability**: Easier to modify individual components
5. **Reusability**: Components can be used independently
6. **Testing**: Each component can be tested in isolation

## **No Magic, Just Simple Vue Patterns**
- Each component loads its own data
- Each component keeps data in memory
- `Chat` component has `selectedSession` observable
- All child components automatically react to session changes
- Parent just shows/hides like tabs
- Basic event emission for coordination
- No complex state management libraries

## **Architecture Benefits**
- **ChatView**: Handles routing, URL params, page-level concerns
- **Chat**: Pure chat functionality, reusable component
- **Separation of Concerns**: View logic vs. Chat logic
- **Reusability**: Chat component can be used in other views/pages
- **Clean URLs**: ChatView can handle /chat/:sessionId routing
