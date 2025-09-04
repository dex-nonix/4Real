from nonix_web.router.web_server_router import router
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    NxWebServerCrudRouter
from .track_schemas import TrackCreate, TrackUpdate, TrackInDbModel
from ...models.track import Track


@router("/tracks", tags=["Tracks"])
class TrackService(NxWebServerCrudRouter):
    config = CRUDConfig(
        model=Track,
        create_schema=TrackCreate,
        update_schema=TrackUpdate,
        response_schema=TrackInDbModel,
        filters=FilterConfig(
            allowed_fields=['title', 'album_id', 'track_number']
        ),
        sorting=SortingConfig(
            default_sort='track_number',
            allowed_fields=['title', 'track_number', 'created_at']
        ),
        validation=ValidationConfig(
            unique_fields=[]
        ),
        selector=SelectorConfig(
            fields=['title', 'track_number'],
            display_format='{title}',
            search_fields=['title']
        )
    )
