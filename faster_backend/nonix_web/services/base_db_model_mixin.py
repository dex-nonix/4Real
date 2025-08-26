from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BaseDbModelMixin(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
