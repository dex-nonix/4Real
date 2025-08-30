from __future__ import annotations

from sqlalchemy import Column, Integer, JSON, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from nonix_web_db import BaseModel


class AIAnalysisResult(BaseModel):
    __tablename__ = 'ai_analysis_results'

    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('ai_providers.id'), nullable=False)
    model_name = Column(String(255))
    analysis_type = Column(String(255), nullable=False)
    result_json = Column(JSON)

    # Relationships
    track = relationship('Track', foreign_keys=[track_id], backref=backref('analysis_results', lazy=True))
    provider = relationship('AIProvider', foreign_keys=[provider_id], backref=backref('analysis_results', lazy=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIAnalysisResult id={self.id} type={self.analysis_type!r}>"
