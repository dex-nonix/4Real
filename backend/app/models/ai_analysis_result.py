from __future__ import annotations

from sqlalchemy.sql import func

from .. import db


class AIAnalysisResult(db.Model):
    __tablename__ = 'ai_analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('ai_providers.id'), nullable=False)
    model_name = db.Column(db.String(255))
    analysis_type = db.Column(db.String(255), nullable=False)
    result_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    # Relationships
    track = db.relationship('Track', backref=db.backref('analysis_results', lazy=True))
    provider = db.relationship('AIProvider', backref=db.backref('analysis_results', lazy=True))

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
