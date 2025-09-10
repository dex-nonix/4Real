from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from ...services.rhyme_technique_service import RhymeTechniqueService


@router("/rhyme-techniques", tags=["Rhyme Techniques"])
class RhymeTechniqueRouter(NxWebServerCrudRouter):
    service: RhymeTechniqueService = NxInject(RhymeTechniqueService)
