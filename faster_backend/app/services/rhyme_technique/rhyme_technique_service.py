from .rhyme_technique_schemas import RhymeTechniqueCreate, RhymeTechniqueUpdate, RhymeTechniqueInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import RhymeTechnique


@routed_service("/rhyme_techniques", tags=["Rhyme Techniques"])
class RhymeTechniqueService(GenericCRUDService):
    config = CRUDConfig(
        model=RhymeTechnique,
        create_schema=RhymeTechniqueCreate,
        update_schema=RhymeTechniqueUpdate,
        response_schema=RhymeTechniqueInDB,
        filters=FilterConfig(
            allowed_fields=['name']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name'],
            display_format='{name}',
            search_fields=['name']
        )
    )
