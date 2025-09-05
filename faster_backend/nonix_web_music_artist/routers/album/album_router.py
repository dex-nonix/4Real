from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .album_schemas import AlbumCreate, AlbumUpdate, AlbumInDbModel
from nonix_web_music_artist.models.album import Album


@router("/albums", tags=["Albums"])
class AlbumRouter(NxWebServerCrudRouter):
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
