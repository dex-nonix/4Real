from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .rhyme_technique_schemas import RhymeTechniqueCreate, RhymeTechniqueUpdate, RhymeTechniqueInDbModel
from nonix_web_music_artist.models.rhyme_technique import RhymeTechnique


@router("/rhyme-techniques", tags=["Rhyme Techniques"])
class RhymeTechniqueRouter(NxWebServerCrudRouter):
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
