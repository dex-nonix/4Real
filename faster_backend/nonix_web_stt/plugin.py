from typing import Dict, Any

from nonix_di.decorator import injectables
from nonix_di.resolve import NxInject
from nonix_plugin.base import BasePlugin
from nonix_web.decorator import web_routers
from nonix_web.server import AsyncServer
from .routers.stt_router import NxSttRouter
from .services.stt_service import NxSttService


@web_routers([
    NxSttRouter
])
@injectables([
    NxSttService
])
class NxWebSttPlugin(BasePlugin):
    stt_service: NxSttService = NxInject(NxSttService)
    sio: AsyncServer = NxInject(AsyncServer)

    async def _startup(self, config: Dict[str, Any]):
        self._register_websocket_handlers()

    def _register_websocket_handlers(self):
        @self.sio.event
        async def stt_connect(sid, environ):
            await self.sio.emit('stt_connected', {'socket_id': sid}, room=sid)

        @self.sio.event
        async def stt_disconnect(sid):
            await self.stt_service.handle_disconnect(sid)

        @self.sio.on('stt_start_streaming')
        async def stt_start_streaming(sid, data):
            connection_id = data.get('connection_id')
            config_id = data.get('config_id')
            if not connection_id or not config_id:
                await self.sio.emit('stt_error', {'error': 'connection_id and config_id are required'}, room=sid)
                return
            await self.stt_service.handle_start_streaming(connection_id, config_id)
            await self.sio.emit('stt_streaming_started', {'connection_id': connection_id, 'config_id': config_id}, room=connection_id)

        @self.sio.on('stt_audio_chunk')
        async def stt_audio_chunk(sid, data):
            connection_id = data.get('connection_id')
            audio_data = data.get('audio_data')
            if not connection_id or not audio_data:
                await self.sio.emit('stt_error', {'error': 'connection_id and audio_data are required'}, room=sid)
                return
            try:
                result = await self.stt_service.handle_audio_chunk(connection_id, audio_data)
                if result:
                    await self.sio.emit('stt_transcription', result, room=connection_id)
            except Exception as e:
                await self.sio.emit('stt_error', {'error': str(e)}, room=connection_id)

        @self.sio.on('stt_stop_streaming')
        async def stt_stop_streaming(sid, data):
            connection_id = data.get('connection_id')
            if not connection_id:
                await self.sio.emit('stt_error', {'error': 'connection_id is required'}, room=sid)
                return
            await self.stt_service.handle_disconnect(connection_id)
            await self.sio.emit('stt_streaming_stopped', {'connection_id': connection_id}, room=connection_id)
