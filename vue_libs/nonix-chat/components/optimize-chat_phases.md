# Nonix Chat Refactoring - Implementation Phases

## **Phase 0: Service Registration and Dependency Injection Setup**
**Goal**: Ensure all chat services are properly registered as singletons before refactoring

### **0.1 Verify Backend Service Registration**
- [x] Confirm `ChatSessionService`, `ChatMessageService`, `ChatHistoryService` are registered in `backend/app/__init__.py`
- [x] Verify `ChatService` is registered with `api_router.register_service('chat', ChatService)`
- [x] Ensure all services extend `CrudService` with proper config

### **0.2 Frontend Service Registration**
- [x] Add `ChatRuntimeService` to `src/appConfig.js` service registry:
  ```js
  "chat-runtime": () => new ChatRuntimeService()
  ```
- [x] Verify service is provided via `app.provide('chat-runtime', new ChatRuntimeService())`
- [x] Ensure service follows singleton pattern (one instance per app)

### **0.3 Service Injection in Components**
- [x] Update all components to use `inject('chat-runtime')` instead of `new ChatRuntimeService()`
- [x] Verify async Proxy pattern is handled correctly
- [x] Test service injection works in all components

---

## **Phase 1: Create ChatMessageContainer Component**
**Goal**: Create the unified message container before removing old components

### **1.1 Create New Component**
- Create `ChatMessageContainer.vue` in `components/` directory
- Combine `ChatMessages.vue` + `ChatMessageInput.vue` functionality
- Add session-specific data management
- Add message loading per session
- Add input text persistence per session
- Use `inject('chat-runtime')` for service access

### **1.2 Test New Component**
- Test message display functionality
- Test input functionality
- Test session-specific data isolation
- Ensure no breaking changes to existing functionality

### **1.3 Update Chat.vue to Use New Component**
- Import `ChatMessageContainer` instead of separate components
- Pass necessary props to `ChatMessageContainer`
- Test that messages and input still work

---

## **Phase 2: Refactor ChatSessionBar Component**
**Goal**: Make ChatSessionBar self-contained before removing session management from ChatWidget

### **2.1 Add Session Management to ChatSessionBar**
- Move session loading logic from ChatWidget to ChatSessionBar
- Add `sessions` ref in ChatSessionBar
- Add `loadSessions()` method in ChatSessionBar
- Add session CRUD methods (create, delete, update)
- Use `inject('chat-runtime')` for service access instead of direct instantiation

### **2.2 Add Event Emission**
- Emit `session-selected` with full session object
- Emit `session-added` when new session created
- Emit `session-removed` when session deleted
- Test event emission works correctly

### **2.3 Test ChatSessionBar Independence**
- Verify ChatSessionBar loads sessions on mount
- Verify events are emitted correctly
- Ensure no breaking changes to existing functionality

---

## **Phase 3: Update Chat Component with selectedSession**
**Goal**: Add selectedSession observable before removing state from ChatWidget

### **3.1 Add selectedSession to Chat Component**
- Add `selectedSession` ref in Chat component
- Add computed properties that depend on selectedSession
- Update template to use selectedSession instead of props

### **3.2 Handle Session Events**
- Listen to `session-selected` from ChatSessionBar
- Update selectedSession when event received
- Test that selectedSession changes trigger component updates

### **3.3 Update Child Components**
- Pass selectedSession to ChatHeader
- Pass selectedSession to ChatMessageContainer
- Ensure all components react to selectedSession changes

### **3.4 Test Chat Component Independence**
- Verify selectedSession updates trigger child component updates
- Test session switching works correctly
- Ensure no breaking changes

---

## **Phase 4: Transform ChatWidget to ChatView**
**Goal**: Convert ChatWidget to a view after all functionality is moved to Chat

### **4.1 Create ChatView.vue**
- Copy ChatWidget.vue to ChatView.vue
- Remove all component logic and state management
- Remove all API calls and service usage
- Remove all event handlers

### **4.2 Simplify ChatView**
- Make it a simple page/view that uses Chat component
- Pass any necessary props to Chat component
- Handle URL routing if needed
- Keep only view-specific logic

### **4.3 Test ChatView**
- Verify ChatView renders Chat component correctly
- Test that no functionality is broken
- Ensure ChatView is just a wrapper

---

## **Phase 5: Remove Old Components and Clean Up**
**Goal**: Clean up after all functionality is working in new architecture

### **5.1 Remove Old Message Components**
- Remove `ChatMessages.vue` (functionality moved to ChatMessageContainer)
- Remove `ChatMessageInput.vue` (functionality moved to ChatMessageContainer)
- Update imports in all files

### **5.2 Remove Old ChatWidget**
- Delete `ChatWidget.vue` (replaced by ChatView.vue)
- Update any imports or references
- Update documentation

### **5.3 Clean Up Props and Events**
- Remove unused props from Chat component
- Remove unused event handlers
- Clean up any dead code

---

## **Phase 6: Final Testing and Integration**
**Goal**: Ensure everything works together perfectly

### **6.1 Integration Testing**
- Test complete session switching flow
- Test message persistence across sessions
- Test input text preservation
- Test all events and communication

### **6.2 Performance Testing**
- Verify no memory leaks
- Test with multiple sessions
- Ensure smooth switching between sessions

### **6.3 Documentation Update**
- Update component documentation
- Update usage examples
- Update any API documentation

---

## **Critical Success Factors**

### **Order Dependencies**
0. **ALL services MUST be registered and injectable before any refactoring**
1. **ChatMessageContainer MUST be created before removing old components**
2. **ChatSessionBar MUST be self-contained before removing session logic**
3. **Chat component MUST have selectedSession before removing ChatWidget state**
4. **ChatView MUST be created before deleting ChatWidget**

### **Service Injection Requirements**
- **ChatRuntimeService** must be registered in `appConfig.js` service registry
- **All components** must use `inject('chat-runtime')` instead of `new ChatRuntimeService()`
- **Service must be singleton** - one instance per app lifecycle
- **Async Proxy pattern** must be handled correctly in service calls

### **Testing Checkpoints**
- Test each phase before moving to next
- Ensure no functionality is broken between phases
- Keep old components working until new ones are fully tested

### **Rollback Plan**
- Each phase should be reversible
- Keep backups of working components
- Test rollback procedures

### **Integration Points**
- Events between components must be properly defined
- Props must be correctly passed down
- State changes must trigger proper updates

---

## **Phase Completion Checklist**

- [x] Phase 0: Service registration and dependency injection setup complete
- [ ] Phase 1: ChatMessageContainer created and tested
- [ ] Phase 2: ChatSessionBar self-contained and tested  
- [ ] Phase 3: Chat component has selectedSession and tested
- [ ] Phase 4: ChatView created and tested
- [ ] Phase 5: Old components removed and cleaned up
- [ ] Phase 6: Final integration testing complete

**DO NOT PROCEED TO NEXT PHASE UNTIL CURRENT PHASE IS 100% COMPLETE AND TESTED**
