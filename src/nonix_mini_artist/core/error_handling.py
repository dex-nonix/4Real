"""
Comprehensive error handling and logging for the chat system
"""
import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ChatSystemError(Exception):
    """Base exception for chat system errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            'error': True,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class PersonaError(ChatSystemError):
    """Exception for persona-related errors"""
    pass

class ChatSessionError(ChatSystemError):
    """Exception for chat session errors"""
    pass

class ToolExecutionError(ChatSystemError):
    """Exception for tool execution errors"""
    pass

class AIResponseError(ChatSystemError):
    """Exception for AI response generation errors"""
    pass

class PermissionError(ChatSystemError):
    """Exception for permission-related errors"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        """Initialize error handler"""
        self.error_counts = {}
        self.error_history = []
        self.max_history = 1000
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log an error with context"""
        error_type = type(error).__name__
        
        # Count errors by type
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Add to history
        error_entry = {
            'timestamp': datetime.now(),
            'error_type': error_type,
            'message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_entry)
        
        # Keep history size manageable
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Log to file
        logger.error(f"Error: {error_type} - {error}")
        if context:
            logger.error(f"Context: {context}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_counts': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_counts.clear()

class UserFriendlyError:
    """Convert technical errors to user-friendly messages"""
    
    @staticmethod
    def get_user_message(error: Exception) -> str:
        """Get user-friendly error message"""
        if isinstance(error, PersonaError):
            return "There was an issue with the persona. Please try again or contact support."
        
        elif isinstance(error, ChatSessionError):
            return "Unable to manage the chat session. Please refresh and try again."
        
        elif isinstance(error, ToolExecutionError):
            return "The requested tool encountered an error. Please try a different approach."
        
        elif isinstance(error, AIResponseError):
            return "The AI is having trouble responding right now. Please try again in a moment."
        
        elif isinstance(error, PermissionError):
            return "You don't have permission to perform this action. Please check your settings."
        
        elif isinstance(error, ValueError):
            return "The provided information is invalid. Please check your input and try again."
        
        elif isinstance(error, ConnectionError):
            return "Unable to connect to the service. Please check your internet connection."
        
        else:
            return "An unexpected error occurred. Please try again or contact support if the problem persists."
    
    @staticmethod
    def get_suggestion(error: Exception) -> Optional[str]:
        """Get helpful suggestion for the error"""
        if isinstance(error, PersonaError):
            return "Try refreshing the persona list or creating a new persona."
        
        elif isinstance(error, ChatSessionError):
            return "Try closing and reopening the chat session."
        
        elif isinstance(error, ToolExecutionError):
            return "Check if the tool parameters are correct and try again."
        
        elif isinstance(error, AIResponseError):
            return "Wait a moment and try sending your message again."
        
        elif isinstance(error, PermissionError):
            return "Check your persona's tool permissions in the settings."
        
        return None

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        
        except Exception as e:
            # Log the error
            error_handler.log_error(e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            
            # Re-raise as appropriate error type
            if isinstance(e, ChatSystemError):
                raise
            
            # Convert to appropriate error type
            if 'persona' in func.__name__.lower():
                raise PersonaError(str(e), 'PERSONA_ERROR')
            elif 'session' in func.__name__.lower():
                raise ChatSessionError(str(e), 'SESSION_ERROR')
            elif 'tool' in func.__name__.lower():
                raise ToolExecutionError(str(e), 'TOOL_ERROR')
            elif 'ai' in func.__name__.lower():
                raise AIResponseError(str(e), 'AI_ERROR')
            else:
                raise ChatSystemError(str(e), 'GENERAL_ERROR')
    
    return wrapper

def graceful_degradation(fallback_value: Any = None):
    """Decorator for graceful degradation on errors"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            
            except Exception as e:
                # Log the error
                error_handler.log_error(e, {
                    'function': func.__name__,
                    'fallback_used': True
                })
                
                # Return fallback value
                if fallback_value is not None:
                    return fallback_value
                
                # Return empty result based on function name
                if 'list' in func.__name__.lower():
                    return []
                elif 'get' in func.__name__.lower():
                    return None
                elif 'create' in func.__name__.lower():
                    return False
                else:
                    return None
        
        return wrapper
    return decorator

def validate_input(validation_func: Callable) -> Callable:
    """Decorator to validate input parameters"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Validate input
                validation_func(*args, **kwargs)
                return await func(*args, **kwargs)
            
            except ValueError as e:
                raise ChatSystemError(f"Invalid input: {e}", 'VALIDATION_ERROR')
            except Exception as e:
                raise ChatSystemError(f"Input validation failed: {e}", 'VALIDATION_ERROR')
        
        return wrapper
    return decorator

# Global error handler instance
error_handler = ErrorHandler()

# Error handling utilities
def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log an error with context"""
    error_handler.log_error(error, context)

def get_error_stats() -> Dict[str, Any]:
    """Get error statistics"""
    return error_handler.get_error_stats()

def get_user_friendly_message(error: Exception) -> str:
    """Get user-friendly error message"""
    return UserFriendlyError.get_user_message(error)

def get_error_suggestion(error: Exception) -> Optional[str]:
    """Get helpful suggestion for the error"""
    return UserFriendlyError.get_suggestion(error)

def clear_error_history():
    """Clear error history"""
    error_handler.clear_error_history()
