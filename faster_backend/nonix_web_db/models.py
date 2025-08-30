from __future__ import annotations

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
        base_dict = {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        for column in self.__table__.columns:
            if column.name not in ['id', 'created_at', 'updated_at']:
                value = getattr(self, column.name)
                if hasattr(value, 'isoformat'):  # Handle datetime fields
                    base_dict[column.name] = value.isoformat() if value else None
                else:
                    base_dict[column.name] = value
        
        return base_dict
    
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if hasattr(self, 'name'):
            return f"<{class_name} id={self.id} name={getattr(self, 'name', 'N/A')!r}>"
        elif hasattr(self, 'title'):
            return f"<{class_name} id={self.id} title={getattr(self, 'title', 'N/A')!r}>"
        else:
            return f"<{class_name} id={self.id}>"
