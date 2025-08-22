from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, JSON, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from ..database import Base


class AIAnalysisResult(Base):
    __tablename__ = 'ai_analysis_results'

    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('ai_providers.id'), nullable=False)
    model_name = Column(String(255))
    analysis_type = Column(String(255), nullable=False)
    result_json = Column(JSON)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    track = relationship('Track', backref=backref('analysis_results', lazy=True))
    provider = relationship('AIProvider', backref=backref('analysis_results', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'track_id': self.track_id,
            'provider_id': self.provider_id,
            'model_name': self.model_name,
            'analysis_type': self.analysis_type,
            'result_json': self.result_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIAnalysisResult id={self.id} type={self.analysis_type!r}>"
