from nonix_web.router.web_server_router import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_web.utils.di import Inject
from nonix_web_music_artist.services.rhyme_technique_service import RhymeTechniqueService


@router("/rhyme-techniques", tags=["Rhyme Techniques"])
class RhymeTechniqueRouter(NxWebServerCrudRouter):
    service: RhymeTechniqueService = Inject(RhymeTechniqueService)
