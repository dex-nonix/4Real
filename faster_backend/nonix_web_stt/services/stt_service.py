from typing import Dict
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, BaseCrudService
from nonix_di.resolve import NxInject
from nonix_web.web_socket_service import NxWebServerWebSocketService
from ..models.stt_configuration import NxSttConfiguration
from ..schemas.stt_configuration_schemas import NxSttConfigurationCreate, NxSttConfigurationUpdate, NxSttConfigurationInDbModel


class NxSttService(BaseCrudService):
    config = CRUDConfig(
        model=NxSttConfiguration,
        create_schema=NxSttConfigurationCreate,
        update_schema=NxSttConfigurationUpdate,
        response_schema=NxSttConfigurationInDbModel,
        filters=FilterConfig(allowed_fields=['name', 'is_active']),
        sorting=SortingConfig(default_sort='name', allowed_fields=['name', 'created_at']),
        validation=ValidationConfig(unique_fields=['name']),
        selector=SelectorConfig(fields=['name'], display_format='{name}', search_fields=['name'])
    )

    ws_service: NxWebServerWebSocketService = NxInject(NxWebServerWebSocketService)

    def __init__(self):
        super().__init__()
        self._connections: Dict[str, Dict] = {}

    async def transcribe_file(self, file_path: str, config_id: int) -> str:
        config = await self.get_by_id(config_id)

    async def handle_connect(self, connection_id: str):
        self._connections[connection_id] = {
            'audio_buffer': b'',
            'config_id': None
        }

    async def handle_disconnect(self, connection_id: str):
        if connection_id in self._connections:
            del self._connections[connection_id]

    async def handle_start_streaming(self, connection_id: str, config_id: int):
        if connection_id in self._connections:
            self._connections[connection_id]['config_id'] = config_id

    async def handle_audio_chunk(self, connection_id: str, data: bytes):
        if connection_id not in self._connections:
            return
            
        self._connections[connection_id]['audio_buffer'] += data
        
        config_id = self._connections[connection_id]['config_id']
        if not config_id:
            raise ValueError("Connection must choose a config before processing audio!")
        
        config = await self.get_by_id(config_id)
