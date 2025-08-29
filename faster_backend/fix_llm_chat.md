# LLM Chat Connection Error Handling Fix Plan

## Overview
This document outlines the comprehensive fixes needed to properly handle connection errors between the AI provider and the UI, ensuring users are informed when providers are unreachable.

## Current Issues Identified

### 1. **Critical Gap in Error Flow** ❌
- **Problem**: `ChatService` catches provider errors and yields `StreamingChunk` with error content, but `StreamingEventManager` treats these as normal completion chunks
- **Result**: Connection errors never reach the UI as `streaming_error` events
- **Impact**: Users wait indefinitely without knowing the AI provider is unreachable

### 2. **Missing Error Detection Logic** ❌
- **Problem**: No mechanism to detect when a `StreamingChunk` contains error information
- **Result**: Error content is processed as normal text content
- **Impact**: Error messages appear as normal AI responses instead of error notifications

### 3. **Poor Error Message Quality** ❌
- **Problem**: Raw exception messages are sent to users (e.g., "Connection error.")
- **Result**: Users see technical error messages instead of user-friendly explanations
- **Impact**: Poor user experience and confusion about what went wrong

### 4. **No Retry Mechanism** ❌
- **Problem**: Failed connections result in immediate failure without retry attempts
- **Result**: Transient network issues cause permanent failures
- **Impact**: Reduced reliability and user frustration

## Required Changes

### Phase 1: Fix StreamingEventManager Error Detection

#### 1.1 Modify `StreamingEventManager.emit_chunk_event()`
**File**: `faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py`

**Changes**:
- Add error content detection logic
- Convert error chunks to `streaming_error` events
- Preserve original chunk emission for non-error cases

**Code Changes**:
```python
async def emit_chunk_event(self, session_id: int, history_id: int, chunk: StreamingChunk, message_id: int):
    """Emit chunk event via WebSocket with error detection."""
    
    # Check if this chunk contains error information
    if self._is_error_chunk(chunk):
        await self.emit_streaming_error(
            session_id, 
            history_id, 
            chunk.content, 
            "provider_error", 
            message_id
        )
        return
    
    # Original logic for normal chunks...
    if chunk.chunk_type == "text":
        # ... existing code ...
    
def _is_error_chunk(self, chunk: StreamingChunk) -> bool:
    """Detect if a StreamingChunk contains error information."""
    if not chunk.content:
        return False
    
    error_indicators = [
        "Provider error:", 
        "Provider import error:", 
        "Connection error",
        "All connection attempts failed",
        "APIConnectionError",
        "ConnectError"
    ]
    
    return any(indicator in chunk.content for indicator in error_indicators)
```

#### 1.2 Add Error Type Classification
**File**: `faster_backend/nonix_web_agentic/services/chat/streaming_event_manager.py`

**Changes**:
- Add method to classify error types
- Provide specific error categories for better UI handling

**Code Changes**:
```python
def _classify_error_type(self, error_content: str) -> str:
    """Classify error type for better UI handling."""
    if "Connection error" in error_content or "All connection attempts failed" in error_content:
        return "connection_error"
    elif "Provider import error" in error_content:
        return "provider_config_error"
    elif "APIConnectionError" in error_content:
        return "api_connection_error"
    else:
        return "general_error"
```

### Phase 2: Enhance StreamingChunk for Error Handling

#### 2.1 Modify `StreamingChunk` Data Structure
**File**: `faster_backend/nonix_web_agentic/services/chat/streaming_interface.py`

**Changes**:
- Add error-related fields to `StreamingChunk`
- Support error metadata and classification

**Code Changes**:
```python
@dataclass
class StreamingChunk:
    content: str
    chunk_type: str  # 'text', 'tool_start', 'tool_end', 'complete', 'error'
    metadata: Optional[Dict[str, Any]] = None
    is_final: bool = False
    is_error: bool = False
    error_type: Optional[str] = None
    error_code: Optional[str] = None
```

#### 2.2 Update ChatService Error Handling
**File**: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`

**Changes**:
- Create proper error chunks instead of using "complete" type
- Add error classification and metadata

**Code Changes**:
```python
except Exception as exc:
    self._logger.error(f"Provider error: {exc}", exc_info=True)
    
    # Create proper error chunk
    error_type = self._classify_provider_error(exc)
    error_message = self._format_user_friendly_error(exc, error_type)
    
    yield StreamingChunk(
        content=error_message,
        chunk_type="error",
        is_final=True,
        is_error=True,
        error_type=error_type,
        error_code=self._get_error_code(exc),
        metadata={
            "original_error": str(exc),
            "error_class": type(exc).__name__
        }
    )

def _classify_provider_error(self, exc: Exception) -> str:
    """Classify provider errors for better handling."""
    if "Connection error" in str(exc) or "All connection attempts failed" in str(exc):
        return "connection_error"
    elif "Provider import error" in str(exc):
        return "provider_config_error"
    elif "APIConnectionError" in str(exc):
        return "api_connection_error"
    else:
        return "general_error"

def _format_user_friendly_error(self, exc: Exception, error_type: str) -> str:
    """Format error messages for end users."""
    error_messages = {
        "connection_error": "Unable to connect to AI service. Please check your internet connection and try again.",
        "provider_config_error": "AI service configuration error. Please contact support.",
        "api_connection_error": "AI service is currently unavailable. Please try again later.",
        "general_error": "An error occurred while processing your request. Please try again."
    }
    return error_messages.get(error_type, "An unexpected error occurred. Please try again.")
```

### Phase 3: Implement Retry Mechanism

#### 3.1 Add Retry Logic to ChatService
**File**: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`

**Changes**:
- Implement exponential backoff retry for connection errors
- Add retry configuration options
- Handle transient vs permanent failures

**Code Changes**:
```python
import asyncio
from typing import Optional

class RetryConfig:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

async def run_chat_streaming_with_retry(self, provider, mapping, messages, available_tools_info, persona_id, retry_config: Optional[RetryConfig] = None):
    """Run chat streaming with automatic retry for connection errors."""
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            async for chunk in self.run_chat_streaming(provider, mapping, messages, available_tools_info, persona_id):
                yield chunk
            return  # Success, exit retry loop
            
        except Exception as exc:
            last_exception = exc
            
            # Check if this is a retryable error
            if not self._is_retryable_error(exc):
                break
            
            # Don't retry on last attempt
            if attempt >= retry_config.max_retries:
                break
            
            # Calculate delay with exponential backoff
            delay = min(retry_config.base_delay * (2 ** attempt), retry_config.max_delay)
            
            # Log retry attempt
            self._logger.warning(f"Retry attempt {attempt + 1}/{retry_config.max_retries} after {delay}s for error: {exc}")
            
            # Wait before retry
            await asyncio.sleep(delay)
    
    # All retries exhausted, yield error chunk
    error_message = f"Service unavailable after {retry_config.max_retries} attempts. Please try again later."
    yield StreamingChunk(
        content=error_message,
        chunk_type="error",
        is_final=True,
        is_error=True,
        error_type="retry_exhausted",
        metadata={
            "retry_attempts": retry_config.max_retries,
            "last_error": str(last_exception)
        }
    )

def _is_retryable_error(self, exc: Exception) -> bool:
    """Determine if an error is retryable."""
    retryable_errors = [
        "Connection error",
        "All connection attempts failed",
        "APIConnectionError",
        "ConnectError",
        "TimeoutError"
    ]
    
    error_str = str(exc)
    return any(retryable in error_str for retryable in retryable_errors)
```

#### 3.2 Update Message Processing to Use Retry
**File**: `faster_backend/nonix_web_agentic/services/chat/mixins/chat_message_mixin.py`

**Changes**:
- Use retry-enabled streaming method
- Handle retry-related events

**Code Changes**:
```python
# Replace the existing streaming call with retry-enabled version
async for message in self.run_chat_streaming_with_retry(
        provider,
        mapping_obj,
        chat_history,
        available_tools_info,
        persona_id,
        retry_config=RetryConfig(max_retries=2, base_delay=1.0)
):
    # ... existing message handling logic ...
```

### Phase 4: Enhance Frontend Error Handling

#### 4.1 Improve Error Display in ChatMessageContainer
**File**: `vue_libs/nonix-chat/components/ChatMessageContainer.vue`

**Changes**:
- Enhanced error handling for different error types
- Better error message display
- Retry button for retryable errors

**Code Changes**:
```javascript
const handleStreamingError = (data) => {
  console.log('🎯 Streaming Error event:', data);
  const { message_id, error_message, error_type, error_code } = data || {};
  
  if (!message_id) return;
  
  // Update message status to error
  const messageIndex = messages.value.findIndex(m => m.id === message_id);
  if (messageIndex !== -1) {
    messages.value[messageIndex].status = 'error';
    messages.value[messageIndex].error_details = {
      type: error_type,
      code: error_code,
      message: error_message
    };
  }
  
  // Update streaming state
  streamingStatus.value.set(message_id, 'error');
  const streamingData = streamingMessages.value.get(message_id) || {};
  streamingData.status = 'error';
  streamingData.error_details = data;
  streamingMessages.value.set(message_id, streamingData);
  
  // Show user-friendly error message
  showErrorMessage(error_message, error_type);
};

const showErrorMessage = (message, errorType) => {
  // Use toast or other notification system
  if (toast) {
    const severity = errorType === 'retry_exhausted' ? 'warn' : 'error';
    const summary = errorType === 'retry_exhausted' ? 'Service Unavailable' : 'Error';
    
    toast.add({
      severity,
      summary,
      detail: message,
      life: 8000,
      closable: true
    });
  }
};
```

#### 4.2 Add Retry Button Component
**File**: `vue_libs/nonix-chat/components/ErrorRetryButton.vue` (New File)

**Purpose**: Provide retry functionality for failed messages

**Features**:
- Retry button for retryable errors
- Different styling for different error types
- Loading state during retry

### Phase 5: Add Error Monitoring and Logging

#### 5.1 Enhanced Error Logging
**File**: `faster_backend/nonix_web_agentic/services/chat/chat_service.py`

**Changes**:
- Structured error logging
- Error metrics collection
- Performance monitoring

**Code Changes**:
```python
import time
from datetime import datetime

class ErrorMetrics:
    def __init__(self):
        self.error_counts = {}
        self.error_timestamps = []
        self.retry_success_rates = {}
    
    def record_error(self, error_type: str, error_details: dict):
        """Record error occurrence for monitoring."""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        self.error_timestamps.append({
            'timestamp': datetime.utcnow(),
            'error_type': error_type,
            'details': error_details
        })
        
        # Keep only last 1000 errors
        if len(self.error_timestamps) > 1000:
            self.error_timestamps = self.error_timestamps[-1000:]
    
    def get_error_summary(self) -> dict:
        """Get error summary for monitoring."""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_counts': self.error_counts.copy(),
            'recent_errors': len([e for e in self.error_timestamps if (datetime.utcnow() - e['timestamp']).seconds < 3600])
        }

# Add to ChatService class
def __init__(self, ...):
    # ... existing init code ...
    self.error_metrics = ErrorMetrics()

# Update error handling
except Exception as exc:
    error_type = self._classify_provider_error(exc)
    self.error_metrics.record_error(error_type, {
        'exception': str(exc),
        'exception_type': type(exc).__name__,
        'timestamp': datetime.utcnow().isoformat()
    })
    # ... rest of error handling ...
```

## Implementation Order

### Priority 1 (Critical - Fix UI Notification) - **30 minutes**
1. Fix `StreamingEventManager.emit_chunk_event()` error detection
2. Update `StreamingChunk` data structure  
3. Test error flow from backend to frontend

### Priority 2 (High - Improve User Experience) - **1 hour**
1. Implement user-friendly error messages
2. Add error type classification
3. Enhance frontend error display

### Priority 3 (Medium - Add Reliability) - **2-3 hours**
1. Implement retry mechanism
2. Add error monitoring
3. Create retry UI components

### Priority 4 (Low - Monitoring and Analytics) - **1 hour**
1. Add error metrics dashboard
2. Implement alerting for high error rates
3. Performance optimization

## Testing Strategy

### Backend Testing
1. **Unit Tests**: Test error detection logic in `StreamingEventManager`
2. **Integration Tests**: Verify error flow from `ChatService` to WebSocket events
3. **Error Simulation**: Test with mocked connection failures

### Frontend Testing
1. **Error Event Handling**: Verify `streaming_error` events are properly processed
2. **UI Updates**: Test error message display and status updates
3. **Retry Functionality**: Test retry button behavior

### End-to-End Testing
1. **Connection Failure Scenarios**: Test with actual unreachable providers
2. **Retry Scenarios**: Verify retry mechanism works correctly
3. **User Experience**: Ensure users understand what went wrong and what to do

## Success Criteria

1. ✅ **UI Notification**: Users see clear error messages when AI providers are unreachable
2. ✅ **Error Classification**: Different error types are handled appropriately
3. ✅ **Retry Mechanism**: Transient failures are automatically retried
4. ✅ **User Experience**: Error messages are user-friendly and actionable
5. ✅ **Monitoring**: Error rates and patterns are tracked for system health

## Risk Assessment

### Low Risk
- Error detection logic changes (well-contained)
- Frontend error display enhancements (UI only)

### Medium Risk
- `StreamingChunk` data structure changes (affects multiple components)
- Retry mechanism implementation (new async logic)

### Mitigation Strategies
1. **Incremental Implementation**: Implement changes in phases
2. **Comprehensive Testing**: Test each phase thoroughly before proceeding
3. **Rollback Plan**: Keep original code paths as fallbacks during transition
4. **Feature Flags**: Use configuration to enable/disable new features


## Dependencies

1. **Backend Changes**: Must be completed before frontend enhancements
2. **Data Structure Updates**: Required before retry mechanism
3. **Error Classification**: Needed for proper retry logic
4. **Frontend Updates**: Dependent on backend error event changes

## Notes

- All changes should maintain backward compatibility
- Error messages should be internationalization-ready
- Retry configuration should be configurable per environment
- Error monitoring should not impact performance
- User experience should be consistent across all error types
