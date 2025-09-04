from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Union
import copy


class BaseDbModelMixin(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BaseUpdateModel(BaseModel):
    """Automatically converts all inherited fields to optional for partial updates"""

    def __init_subclass__(cls, base_model=None, **kwargs):
        super().__init_subclass__(**kwargs)

        if base_model:
            # Get all fields from the base model
            base_fields = base_model.model_fields

            # Create optional versions for any missing fields
            for field_name, field_info in base_fields.items():
                if field_name not in cls.__annotations__:
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

                    # Create new field
                    new_field = Field(default=field_default, **field_kwargs)

                    # Add to class
                    if not hasattr(cls, '__annotations__'):
                        cls.__annotations__ = {}
                    cls.__annotations__[field_name] = optional_type
                    setattr(cls, field_name, new_field)
