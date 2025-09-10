from copy import deepcopy
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict
from pydantic._internal._model_construction import ModelMetaclass


class BaseDbModelMixin(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BaseUpdateModelMeta(ModelMetaclass):
    """Metaclass that converts all inherited fields to optional"""

    def __new__(cls, name, bases, namespace, base_model=None, **kwargs):
        annotations = dict(namespace.get('__annotations__', {}))
        if base_model:
            base_fields = base_model.model_fields
            for field_name, field_info in base_fields.items():
                original_type = field_info.annotation
                if (hasattr(original_type, '__origin__') and
                        original_type.__origin__ is Union and
                        type(None) in original_type.__args__):
                    optional_type = original_type
                elif field_info.is_required():
                    optional_type = Optional[original_type]
                else:
                    optional_type = original_type

                new_field = deepcopy(field_info)
                new_field.default = None
                annotations[field_name] = optional_type
                namespace[field_name] = new_field

        namespace['__annotations__'] = annotations
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)
        return new_class


class BaseUpdateModel(BaseModel, metaclass=BaseUpdateModelMeta):
    """Automatically converts all inherited fields to optional for partial updates"""
    pass
