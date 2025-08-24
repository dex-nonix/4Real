import uvicorn

from nonix_web import create_nx_app
from nonix_web.config import settings

app = create_nx_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
