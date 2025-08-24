from .album_schemas import AlbumCreate, AlbumUpdate, AlbumInDB
from ..base_service import routed_service
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import Album


@routed_service("/albums", tags=["Albums"])
class AlbumService(GenericCRUDService):
    config = CRUDConfig(
        model=Album,
        create_schema=AlbumCreate,
        update_schema=AlbumUpdate,
        response_schema=AlbumInDB,
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
