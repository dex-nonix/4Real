from typing import Optional
from pydantic import BaseModel, Field
from nonix_web.router.base_db_model_mixin import BaseDbModelMixin, BaseUpdateModel


class NxSttConfigurationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    whisper_model: str = 'base'
    device: str = 'cpu'
    sample_rate: int = 16000
    vad_enabled: bool = False
    language: Optional[str] = None
    is_active: bool = True


class NxSttConfigurationCreate(NxSttConfigurationBase):
    pass


class NxSttConfigurationUpdate(BaseUpdateModel, base_model=NxSttConfigurationBase):
    pass


class NxSttConfigurationInDbModel(NxSttConfigurationBase, BaseDbModelMixin):
    pass
