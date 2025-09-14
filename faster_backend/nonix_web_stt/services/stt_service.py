from typing import Dict

import numpy as np
from faster_whisper import WhisperModel

from nonix_di.resolve import NxInject
from nonix_web.web_socket_service import NxWebServerWebSocketService
from nonix_web_db.crud import CRUDConfig, FilterConfig, SortingConfig, ValidationConfig, SelectorConfig, BaseCrudService
from ..models.stt_configuration import NxSttConfiguration
from ..schemas.stt_configuration_schemas import NxSttConfigurationCreate, NxSttConfigurationUpdate, \
    NxSttConfigurationInDbModel


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
        self._models: Dict[str, WhisperModel] = {}

    def _get_model(self, model_name: str) -> WhisperModel:
        if model_name not in self._models:
            self._models[model_name] = WhisperModel(model_name, device="cpu", compute_type="int8")
        return self._models[model_name]

    async def _get_config(self, config_id: int):
        config = await self.get_one(config_id)
        if not config:
            raise ValueError(f"Configuration with id {config_id} not found")
        return config

    async def transcribe_file(self, file_path: str, config_id: int) -> str:
        config = await self._get_config(config_id)
        model = self._get_model(config.whisper_model)
        segments, info = model.transcribe(file_path)
        transcribed_text = ""
        for segment in segments:
            transcribed_text += segment.text + " "
        return transcribed_text.strip()

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

        connection = self._connections[connection_id]
        connection['audio_buffer'] += data

        config_id = connection['config_id']
        if not config_id:
            raise ValueError("Connection must choose a config before processing audio!")

        config = await self._get_config(config_id)

        chunk_size_bytes = config.sample_rate * 2 * 2
        if len(connection['audio_buffer']) >= chunk_size_bytes:
            model = self._get_model(config.whisper_model)

            process_chunk_bytes = connection['audio_buffer'][:chunk_size_bytes]
            connection['audio_buffer'] = connection['audio_buffer'][chunk_size_bytes:]

            audio_np = np.frombuffer(process_chunk_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            segments, info = model.transcribe(audio_np)
            transcribed_text = ""
            for segment in segments:
                transcribed_text += segment.text

            return {
                'text': transcribed_text.strip(),
                'language': info.language if hasattr(info, 'language') else 'unknown',
                'confidence': segments[0].avg_logprob if segments else 0
            }
