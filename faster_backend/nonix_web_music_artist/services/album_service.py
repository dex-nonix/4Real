from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    BaseCrudService
from ..routers.album.album_schemas import AlbumCreate, AlbumUpdate, AlbumInDbModel
from ..models.album import Album


class AlbumService(BaseCrudService):
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
