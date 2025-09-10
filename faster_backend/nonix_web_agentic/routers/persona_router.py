from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.di import Inject
from nonix_web_agentic.services.persona_service import PersonaService


@router("/personas", tags=["Personas"])
class PersonaRouter(NxWebServerCrudRouter):
    service: PersonaService = Inject(PersonaService)
