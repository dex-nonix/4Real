from sqlalchemy import Boolean, Column, Integer, String
from nonix_web_db import BaseModel


class NxSttConfiguration(BaseModel):
    __tablename__ = 'stt_configurations'

    name = Column(String(255), unique=True, nullable=False)
    whisper_model = Column(String(50), default='base')
    device = Column(String(20), default='cpu')
    sample_rate = Column(Integer, default=16000)
    vad_enabled = Column(Boolean, default=False)
    language = Column(String(10))
    is_active = Column(Boolean, nullable=False, server_default='1')

    def __repr__(self) -> str:
        return f"<NxSttConfiguration id={self.id} name={self.name!r}>"
