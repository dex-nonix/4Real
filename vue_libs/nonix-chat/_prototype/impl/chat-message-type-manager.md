# ChatMessageTypeManager Architecture

## Overview
The `ChatMessageTypeManager` is a registry-based system for managing different types of chat messages. It extends the `BaseWidgetManager` pattern to provide dynamic message rendering capabilities.

## File Structure
```
impl/
├── ChatMessageTypeManager.js          # Main registry manager
├── ChatMessages.vue                   # Updated container component
└── message-types/                     # Message type components
    ├── TextMessage.vue                # Basic text messages
    ├── SystemMessage.vue              # System notifications
    ├── ToolMessage.vue                # Tool execution results
    └── UserMessage.vue                # User input messages
```

## Core Components

### 1. ChatMessageTypeManager.js
- **Inherits from:** `BaseWidgetManager`
- **Purpose:** Registry for message type components
- **Key Methods:**
  - `registerMessageType(type, component)`
  - `getMessageType(type)`
  - `getAllMessageTypes()`
  - `renderMessage(message, currentUserId)`

### 2. Message Type Components
Each message type component should:
- Accept `message` and `currentUserId` props
- Handle its own rendering logic
- Be self-contained and reusable
- Follow consistent styling patterns

#### TextMessage.vue
- Renders standard text messages
- Includes copy/edit/delete menu
- Shows delivery status indicators
- Displays timestamps

#### SystemMessage.vue
- Renders system notifications
- Different visual styling
- No user interaction options
- Centered layout

#### ToolMessage.vue
- Renders tool execution results
- Shows tool name and parameters
- Displays execution status
- May include result data

#### UserMessage.vue
- Renders user input messages
- User-specific styling
- Avatar/identifier display
- Input validation indicators

### 3. Updated ChatMessages.vue
- Simplified container component
- Uses registry to determine which component to render
- Handles message iteration and delegation
- Maintains scroll behavior and layout

## Message Object Structure
```javascript
{
  id: "unique_id",
  type: "text|system|tool|user",  // Determines which component to use
  senderId: "user_id",
  text: "message content",
  timestamp: "2024-01-01T00:00:00Z",
  status: "pending|sent|delivered|read",
  metadata: {} // Additional data for specific message types
}
```

## Benefits
- **Modularity:** Each message type is self-contained
- **Extensibility:** Easy to add new message types
- **Maintainability:** Clean separation of concerns
- **Reusability:** Components can be used elsewhere
- **Dynamic Rendering:** Messages render based on type

## Implementation Steps
1. Create `ChatMessageTypeManager.js` extending `BaseWidgetManager`
2. Create individual message type components
3. Update `ChatMessages.vue` to use the registry
4. Register default message types
5. Test with different message types

## Future Extensions
- Rich media message types (images, videos, files)
- Interactive message types (polls, forms)
- Custom message type plugins
- Message type validation and sanitization
