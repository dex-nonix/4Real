from nonix_web.router.decorators import router
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di import NxInject
from nonix_web_agentic.services.persona_tool_access_service import PersonaToolAccessService


@router("/persona-tool-access", tags=["Persona Tool Access"])
class PersonaToolAccessRouter(NxWebServerCrudRouter):
    service: PersonaToolAccessService = NxInject(PersonaToolAccessService)
