from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..router.template_schemas import TemplateCreate, TemplateUpdate, TemplateInDbModel
from ..models.template import Template


class TemplateService(BaseCrudService):
    """
    Internal service for template CRUD operations.
    Contains all business logic for template management.
    """
    config = CRUDConfig(
        model=Template,
        create_schema=TemplateCreate,
        update_schema=TemplateUpdate,
        response_schema=TemplateInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'description']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at', 'updated_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name', 'description']
        )
    )

    # Custom business logic methods can be added here
    async def get_template_by_name(self, name: str):
        """Get template by name"""
        query_params = {
            "filters": [self.model.name == name]
        }
        result = await self.get_all(query_params)
        templates = result.get("data", [])
        return templates[0] if templates else None

    async def get_child_templates(self, parent_id: int):
        """Get all child templates for a parent template"""
        query_params = {
            "filters": [self.model.parent_template_id == parent_id]
        }
        return await self.get_all(query_params)

    async def get_template_hierarchy(self, template_id: int):
        """Get template with its parent chain"""
        template = await self.get_one(template_id)
        if not template:
            return None

        hierarchy = [template]
        current = template

        # Walk up the parent chain
        while current.parent_template_id:
            current = await self.get_one(current.parent_template_id)
            if current:
                hierarchy.insert(0, current)
            else:
                break

        return hierarchy
