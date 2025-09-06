from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_music_artist.services.track_service import TrackService


@router("/tracks", tags=["Tracks"])
class TrackRouter(NxWebServerCrudRouter):
    service: TrackService = Inject(TrackService)
