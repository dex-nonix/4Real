from pydantic import BaseModel, ConfigDict, Field
from pydantic._internal._model_construction import ModelMetaclass
from datetime import datetime
from typing import Optional, Union, Type


class BaseDbModelMixin(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BaseUpdateModelMeta(ModelMetaclass):
    """Metaclass that converts all inherited fields to optional"""

    def __new__(cls, name, bases, namespace, base_model=None, **kwargs):
        # annotations = dict(namespace.get('__annotations__', {}))
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)



        if base_model:
            # Get all fields from the base model
            base_fields = base_model.model_fields

            # Add optional versions of all fields to the class
            for field_name, field_info in base_fields.items():
                # Check if field is already optional
                original_type = field_info.annotation

                # Handle Union types (Optional[T] is Union[T, None])
                if (hasattr(original_type, '__origin__') and
                    original_type.__origin__ is Union and
                    type(None) in original_type.__args__):
                    # Already Optional, use as-is
                    optional_type = original_type
                    field_default = field_info.default
                elif field_info.is_required():
                    # Convert required field to optional
                    optional_type = Optional[original_type]
                    field_default = None
                else:
                    # Keep optional fields as-is
                    optional_type = original_type
                    field_default = field_info.default

                # Create the field with all original constraints but optional
                field_kwargs = {}
                if hasattr(field_info, '_attributes_set'):
                    field_kwargs.update(field_info._attributes_set)

                # Remove 'default' from kwargs if it exists (we set it separately)
                field_kwargs.pop('default', None)


                new_field = Field(default=None, **field_kwargs)

                # Add to class
                setattr(new_class, field_name, new_field)
                # Set annotation for this field
                if not hasattr(new_class, '__annotations__'):
                    new_class.__annotations__ = {}
                new_class.__annotations__[field_name] = optional_type


        # namespace['__annotations__'] = annotations
        # new_class = super().__new__(cls, name, bases, namespace, **kwargs)
        return new_class


class BaseUpdateModel(BaseModel, metaclass=BaseUpdateModelMeta):
    """Automatically converts all inherited fields to optional for partial updates"""
    pass

