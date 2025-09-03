from __future__ import annotations

from sqlalchemy import Column, String, Text, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship

from nonix_web_db import BaseModel


class Template(BaseModel):
    __tablename__ = "templates"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    context = Column(JSON)
    parent_template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Template id={self.id} name={self.name!r}>"


# Define self-referencing relationship after class definition to avoid forward reference issues
Template.parent_template = relationship(
    "Template",
    remote_side=lambda: Template.id,
    backref="child_templates"
)
