from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ...services.track_service import TrackService


@router("/tracks", tags=["Tracks"])
class TrackRouter(NxWebServerCrudRouter):
    service: TrackService = NxInject(TrackService)
