import os
import tempfile
from fastapi import UploadFile, HTTPException
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.stt_service import NxSttService


@router("/stt-configurations", tags=["STT"])
class NxSttRouter(NxWebServerCrudRouter):
    service: NxSttService = NxInject(NxSttService)

    @route("/status", methods=["GET"])
    async def get_status(self):
        return await self.service.get_server_status()

    @route("/health", methods=["GET"])
    async def get_health(self):
        healthy = await self.service.health_check()
        return {"healthy": healthy}

    @route("/service-info", methods=["GET"])
    async def get_service_info(self):
        return self.service.get_service_info()

    @route("/upload", methods=["POST"])
    async def upload_audio(self, audio_file: UploadFile, config_id: int):
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                result = await self.service.transcribe_file(temp_file.name, config_id)
                return {"transcription": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                os.unlink(temp_file.name)
