from .track_schemas import TrackCreate, TrackUpdate, TrackInDB
from ..base_service import routed_service, route
from ...crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, GenericCRUDService
from ...models import Track


@routed_service("/tracks", tags=["Tracks"])
class TrackService(GenericCRUDService):
    config = CRUDConfig(
        model=Track,
        create_schema=TrackCreate,
        update_schema=TrackUpdate,
        response_schema=TrackInDB,
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
