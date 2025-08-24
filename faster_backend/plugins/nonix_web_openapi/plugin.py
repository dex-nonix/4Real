from fastapi import APIRouter, FastAPI

router = APIRouter()

@router.get("/status")
async def get_status():
    return {"status": "All systems are operational from the Admin Plugin."}

class NxWebOpenApiPlugin(BasePlugin):
    async def load_plugin(self, app: FastAPI):
        app.include_router(router, prefix="/admin", tags=["Admin Plugin"])
        print(f"'{self.name} v{self.version}' loaded and registered its '/admin' routes.")