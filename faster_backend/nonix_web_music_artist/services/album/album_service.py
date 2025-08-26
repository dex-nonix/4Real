from nonix_web.services.base_service import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .album_schemas import AlbumCreate, AlbumUpdate, AlbumInDbModel
from ...models.album import Album


@routed_service("/albums", tags=["Albums"])
class AlbumService(GenericCRUDService):
    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumInDbModel,
        filters=FilterConfig(
            allowed_fields=['title', 'release_date', 'artist_id']
        ),
        sorting=SortingConfig(
            default_sort='release_date',
            allowed_fields=['title', 'release_date', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'release_date'],
            display_format='{title}',
            search_fields=['title']
        )
    )
