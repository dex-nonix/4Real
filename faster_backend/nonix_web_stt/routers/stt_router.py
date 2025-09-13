from fastapi import UploadFile
from nonix_web.router.decorators import router, route
from nonix_web_db.crud import NxWebServerCrudRouter
from nonix_di.resolve import NxInject
from ..services.stt_service import NxSttService


@router("/stt", tags=["STT"])
class NxSttRouter(NxWebServerCrudRouter):
    stt_service: NxSttService = NxInject(NxSttService)

    @route("/upload", methods=["POST"])
    async def upload_audio(self, audio_file: UploadFile, config_id: int):
        return await self.stt_service.transcribe_file(audio_file, config_id)

    @route("/stream", methods=["GET"])
    async def get_stream_info(self):
        return {"stream_url": "/stt/stream", "supported_formats": ["wav", "mp3", "flac"]}
