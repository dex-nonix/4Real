from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_agentic.services.persona_service import PersonaService


@router("/personas", tags=["Personas"])
class PersonaRouter(NxWebServerCrudRouter):
    service: PersonaService = NxInject(PersonaService)
