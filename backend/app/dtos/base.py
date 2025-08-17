from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BaseDTO(ABC, BaseModel):
    """Abstract base class for all DTOs with common functionality"""
    
    class Config:
        from_attributes = True  # Allow ORM model conversion
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @classmethod
    @abstractmethod
    def from_model(cls, model: Any) -> 'BaseDTO':
        """Convert database model to DTO - MUST be implemented by subclasses"""
        pass
    
    @classmethod
    @abstractmethod
    def to_model_data(cls) -> Dict[str, Any]:
        """Convert DTO to model-compatible data - MUST be implemented by subclasses"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for JSON responses)"""
        return self.model_dump()

class CreateDTO(BaseDTO):
    """Base class for creation DTOs (no ID, no timestamps)"""
    pass

class UpdateDTO(BaseDTO):
    """Base class for update DTOs (partial updates, no timestamps)"""
    pass

class ResponseDTO(BaseDTO):
    """Base class for response DTOs (full data, read-only)"""
    pass

class ListResponseDTO(ResponseDTO):
    """Base class for list response DTOs (pagination, filtering)"""
    data: List[ResponseDTO]
    total: int
    page: int
    per_page: int
