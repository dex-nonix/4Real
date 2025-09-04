from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from nonix_web.services.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class AIAnalysisResultBase(BaseModel):
    track_id: int = Field(..., gt=0)
    provider_id: int = Field(..., gt=0)
    model_name: Optional[str] = Field(None, max_length=255)
    analysis_type: str = Field(..., max_length=255)
    result_json: Optional[Dict[str, Any]] = None


class AIAnalysisResultCreate(AIAnalysisResultBase):
    pass


class AIAnalysisResultUpdate(BaseUpdateModel, base_model=AIAnalysisResultBase):
    pass


class AIAnalysisResultInDbModel(AIAnalysisResultBase, BaseDbModelMixin):
    pass
