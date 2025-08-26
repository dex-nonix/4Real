from nonix_web.services.base_service import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .rhyme_technique_schemas import RhymeTechniqueCreate, RhymeTechniqueUpdate, RhymeTechniqueInDbModel
from ...models.rhyme_technique import RhymeTechnique


@routed_service("/rhyme-techniques", tags=["Rhyme Techniques"])
class RhymeTechniqueService(GenericCRUDService):
    config = CRUDConfig(
        model=RhymeTechnique,
        create_schema=RhymeTechniqueCreate,
        update_schema=RhymeTechniqueUpdate,
        response_schema=RhymeTechniqueInDbModel,
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
