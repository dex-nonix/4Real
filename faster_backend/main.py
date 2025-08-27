import uvicorn

from nonix_web.config import settings
from nonix_web.server import NxWebServer

if __name__ == "__main__":
    uvicorn.run(
        lambda: NxWebServer(settings),
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        factory=True
    )
