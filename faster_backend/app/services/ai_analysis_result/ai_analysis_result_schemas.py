from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from ..base_schemas import BaseDBMixin

class AIAnalysisResultBase(BaseModel):
    track_id: int = Field(..., gt=0)
    provider_id: int = Field(..., gt=0)
    model_name: Optional[str] = Field(None, max_length=255)
    analysis_type: str = Field(..., max_length=255)
    result_json: Optional[Dict[str, Any]] = None

class AIAnalysisResultCreate(AIAnalysisResultBase):
    pass

class AIAnalysisResultUpdate(AIAnalysisResultBase):
    pass

class AIAnalysisResultInDB(AIAnalysisResultBase, BaseDBMixin):
    pass
