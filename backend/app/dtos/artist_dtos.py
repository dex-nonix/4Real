from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import Field
from .base import CreateDTO, UpdateDTO, ResponseDTO, ListResponseDTO
from ..models.artist import Artist

# DTO for creating a new artist
class ArtistCreateDTO(CreateDTO):
    name: str = Field(..., min_length=1, max_length=255, description="Artist name")
    abbreviation: Optional[str] = Field(None, max_length=50, description="Artist abbreviation")
    persona: Optional[str] = Field(None, description="Artist persona description")
    birth_date: Optional[datetime] = Field(None, description="Artist birth date")
    
    @classmethod
    def from_model(cls, model: Any) -> 'ArtistCreateDTO':
        """Convert Artist model to ArtistCreateDTO"""
        return cls(
            name=model.name,
            abbreviation=model.abbreviation,
            persona=model.persona,
            birth_date=model.birth_date
        )
    
    def to_model_data(self) -> Dict[str, Any]:
        """Convert DTO to model-compatible data (exclude computed fields)"""
        return self.model_dump()

# DTO for updating an existing artist
class ArtistUpdateDTO(UpdateDTO):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    persona: Optional[str] = None
    birth_date: Optional[datetime] = None
    
    @classmethod
    def from_model(cls, model: Any) -> 'ArtistUpdateDTO':
        """Convert Artist model to ArtistUpdateDTO"""
        return cls(
            name=model.name,
            abbreviation=model.abbreviation,
            persona=model.persona,
            birth_date=model.birth_date
        )
    
    def to_model_data(self) -> Dict[str, Any]:
        """Convert DTO to model-compatible data (exclude computed fields)"""
        return self.model_dump(exclude_unset=True)

# DTO for artist responses
class ArtistResponseDTO(ResponseDTO):
    id: int = Field(..., description="Artist ID")
    name: str = Field(..., description="Artist name")
    abbreviation: Optional[str] = Field(None, description="Artist abbreviation")
    persona: Optional[str] = Field(None, description="Artist persona description")
    birth_date: Optional[datetime] = Field(None, description="Artist birth date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @classmethod
    def from_model(cls, model: Artist) -> 'ArtistResponseDTO':
        """Convert Artist model to ArtistResponseDTO"""
        return cls(
            id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            persona=model.persona,
            birth_date=model.birth_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def to_model_data(self) -> Dict[str, Any]:
        """Convert DTO to model-compatible data (exclude computed fields)"""
        return self.model_dump(exclude={'id', 'created_at', 'updated_at'})

# DTO for list responses
class ArtistListResponseDTO(ListResponseDTO):
    data: List[ArtistResponseDTO]
