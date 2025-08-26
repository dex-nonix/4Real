from nonix_web.services.base_service import routed_service
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, \
    GenericCRUDService
from .track_schemas import TrackCreate, TrackUpdate, TrackInDbModel
from ...models.track import Track


@routed_service("/tracks", tags=["Tracks"])
class TrackService(GenericCRUDService):
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
