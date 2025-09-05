from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.artist.artist_schemas import ArtistCreate, ArtistUpdate, ArtistInDbModel
from ..models.artist import Artist


class ArtistService(BaseCrudService):
    config = CRUDConfig(
        model=Artist,
        create_schema=ArtistCreate,
        update_schema=ArtistUpdate,
        response_schema=ArtistInDbModel,
        filters=FilterConfig(
            allowed_fields=['name', 'abbreviation']
        ),
        sorting=SortingConfig(
            default_sort='name',
            allowed_fields=['name', 'abbreviation', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=['name']
        ),
        selector=SelectorConfig(
            fields=['name', 'abbreviation'],
            display_format='{name}',
            search_fields=['name', 'abbreviation']
        )
    )
