# ASYNC IMPLEMENTATION PHASES
## Simple File & Function Conversion List

### PHASE 1: BASE FRAMEWORK ASYNC ✅
- `backend/config.py` ✅
  - `SOCKETIO_ASYNC_MODE = 'asyncio'` ✅
  - `GUNICORN_WORKER_CLASS = 'uvicorn.workers.UvicornWorker'` ✅

- `backend/requirements.txt` ✅
  - ✅ uvicorn[standard]==0.27.1 (ALREADY PRESENT)

- `backend/app/__init__.py` ✅
  - `socketio = SocketIO(async_mode='asyncio')` ✅
  - `handle_connect()` → `async def handle_connect()` ✅
  - `handle_disconnect()` → `async def handle_disconnect()` ✅
  - `handle_join_room(room)` → `async def handle_join_room(room)` ✅
  - `handle_leave_room(room)` → `async def handle_leave_room(room)` ✅

- `backend/gunicorn.conf.py` ✅
  - `worker_class = 'uvicorn.workers.UvicornWorker'` ✅

### PHASE 2: BASE API SERVICE ASYNC ✅
- `backend/app/services/base_api_service.py` ✅
  - `send_to_channel()` → `async def send_to_channel()` ✅
  - `_websocket_emit()` → `async def _websocket_emit()` ✅
  - `get_exposed_ws_methods()` → `async def get_exposed_methods()` ✅
  - `to_swagger()` → `async def to_swagger()` ✅
  - `get_exposed_methods()` → `async def get_exposed_methods()` ✅
  - `method_to_swagger()` → `async def method_to_swagger()` ✅

### ✅ PHASE 3: CHAT SERVICE ASYNC [COMPLETED]
- ✅ `backend/app/services/chat_service/chat_service.py`
  - ✅ `emit_chat_event()` → `async def emit_chat_event()`
  - ✅ `emit_llm_event()` → `async def emit_llm_event()`
  - ✅ `emit_tool_event()` → `async def emit_tool_event()`
  - ✅ `submit_async_task()` → `async def submit_async_task()`
  - ✅ `get_thread_pool_health()` → `async def get_thread_pool_health()`
  - ✅ `get_thread_pool_stats()` → `async def get_thread_pool_stats()`
  - ✅ `thread_pool_health()` → `async def thread_pool_health()`

- ✅ `backend/app/services/chat_service/chat_session_mixin.py`
  - ✅ `_get_sessions_with_history_counts()` → `async def _get_sessions_with_history_counts()`
  - ✅ `create_session()` → `async def create_session()`
  - ✅ `list_sessions()` → `async def list_sessions()`
  - ✅ `get_session()` → `async def get_session()`
  - ✅ `update_session()` → `async def update_session()`
  - ✅ `delete_session()` → `async def delete_session()`
  - ✅ `get_persona_sessions()` → `async def get_persona_sessions()`
  - ✅ `start_chat_with_persona()` → `async def start_chat_with_persona()`

- ✅ `backend/app/services/chat_service/chat_message_mixin.py`
  - ✅ `_select_chat_model()` → `async def _select_chat_model()`
  - ✅ `_validate_session_history()` → `async def _validate_session_history()`
  - ✅ `_create_user_message()` → `async def _create_user_message()`
  - ✅ `_create_assistant_placeholder()` → `async def _create_assistant_placeholder()`
  - ✅ `_build_chat_history()` → `async def _build_chat_history()`
  - ✅ `_resolve_ai_model()` → `async def _resolve_ai_model()`
  - ✅ `_execute_tool_call()` → `async def _execute_tool_call()`
  - ✅ `_create_assistant_message()` → `async def _create_assistant_message()`
  - ✅ `_format_error_response()` → `async def _format_error_response()`
  - ✅ `emit_llm_event()` → `async def emit_llm_event()`
  - ✅ `list_messages()` → `async def list_messages()`
  - ✅ `send_message()` → `async def send_message()`
  - ✅ `_submit_message_for_async_processing()` → `async def _submit_message_for_async_processing()`
  - ✅ `list_history_messages()` → `async def list_history_messages()`
  - ✅ `delete_message()` → `async def delete_message()`

- ✅ `backend/app/services/chat_service/chat_history_mixin.py`
  - ✅ `list_session_histories()` → `async def list_session_histories()`
  - ✅ `create_session_history()` → `async def create_session_history()`
  - ✅ `get_session_history()` → `async def get_session_history()`
  - ✅ `update_session_history()` → `async def update_session_history()`
  - ✅ `delete_session_history()` → `async def delete_session_history()`
  - ✅ `clear_history_messages()` → `async def clear_history_messages()`

- ✅ `backend/app/services/chat_service/persona_chat_mixin.py`
  - ✅ `_build_persona_query()` → `async def _build_persona_query()`
  - ✅ `list_personas()` → `async def list_personas()`
  - ✅ `get_persona_by_id()` → `async def get_persona_by_id()`

- ✅ `backend/app/services/chat_service/tool_execution_mixin.py`
  - ✅ `persona_tools()` → `async def persona_tools()`
  - ✅ `mcp_status()` → `async def mcp_status()`

- ✅ `backend/app/services/chat_service/streaming_message_handler.py`
  - ✅ `finalize_assistant_message()` → `async def finalize_assistant_message()`
  - ✅ `mark_as_error()` → `async def mark_as_error()`
  - ✅ `update_content_safely()` → `async def update_content_safely()`
  - ✅ `ensure_message_exists()` → `async def ensure_message_exists()`
  - ✅ `cleanup_on_error()` → `async def cleanup_on_error()`

- ✅ `backend/app/services/chat_service/thread_pool_manager.py`
  - ✅ `submit_task()` → `async def submit_task()`
  - ✅ `submit_async_task()` → `async def submit_async_task()`
  - ✅ `get_stats()` → `async def get_stats()`
  - ✅ `get_health_status()` → `async def get_health_status()`
  - ✅ `_task_completed_callback()` → `async def _task_completed_callback()`
  - ✅ `_monitor_thread_pool()` → `async def _monitor_thread_pool()`
  - ✅ `get_executor_context()` → `async def get_executor_context()`
  - ✅ `shutdown()` → `async def shutdown()`

- ✅ `backend/app/services/chat_service/streaming_event_manager.py`
  - ✅ `emit_chunk_event()` → `async def emit_chunk_event()`
  - ✅ `emit_tool_event()` → `async def emit_tool_event()`
  - ✅ `emit_llm_status_event()` → `async def emit_llm_status_event()`
  - ✅ `emit_streaming_error()` → `async def emit_streaming_error()`
  - ✅ `_get_timestamp()` → `async def _get_timestamp()`

- ✅ `backend/app/services/chat_service/websocket_protocol.py`
  - ✅ `submit_async_task()` → `async def submit_async_task()`
  - ✅ `emit_chat_event()` → `async def emit_chat_event()`
  - ✅ `emit_llm_event()` → `async def emit_llm_event()`
  - ✅ `emit_tool_event()` → `async def emit_tool_event()`

- ✅ `backend/app/services/chat_service/message_handlers.py`
  - ✅ `handle()` → `async def handle()` (both instances)

- ✅ `backend/app/services/chat_service/message_type_registry.py`
  - ✅ `handle()` → `async def handle()`
  - ✅ `register()` → `async def register()`
  - ✅ `get_handler()` → `async def get_handler()`
  - ✅ `has_handler()` → `async def has_handler()`
  - ✅ `list_types()` → `async def list_types()`

### ✅ PHASE 4: API ROUTER ASYNC [COMPLETED]
- ✅ `backend/app/api_router/api_router.py`
  - ✅ `register_service()` → `async def register_service()`
  - ✅ `_discover_websocket_channels()` → `async def _discover_websocket_channels()`
  - ✅ `_normalize_path()` → `async def _normalize_path()`
  - ✅ `_create_route()` → `async def _create_route()`
  - ✅ `handler_factory()` → `async def handler_factory()`
  - ✅ `handler()` → `async def handler()`
  - ✅ `list_services()` → `async def list_services()`
  - ✅ `get_service()` → `async def get_service()`
  - ✅ `get_websocket_channels()` → `async def get_websocket_channels()`

- ✅ `backend/app/api_router/compact_api_generator.py`
  - ✅ `_add_routes()` → `async def _add_routes()`
  - ✅ `get_compact_overview()` → `async def get_compact_overview()`
  - ✅ `_convert_openapi_to_compact_yaml()` → `async def _convert_openapi_to_compact_yaml()`
  - ✅ `_count_total_endpoints()` → `async def _count_total_endpoints()`
  - ✅ `_group_paths_by_service()` → `async def _group_paths_by_service()`
  - ✅ `_group_paths_by_section()` → `async def _group_paths_by_section()`

- ✅ `backend/app/api_router/swagger_ui_generator.py`
  - ✅ `generate_swagger_ui()` → `async def generate_swagger_ui()`

- ✅ `backend/app/api_router/documentation_router.py`
  - ✅ `_add_documentation_routes()` → `async def _add_documentation_routes()`
  - ✅ `openapi_spec()` → `async def openapi_spec()`
  - ✅ `swagger_ui()` → `async def swagger_ui()`
  - ✅ `generate_openapi_spec()` → `async def generate_openapi_spec()`

- ✅ `backend/app/api_router/openapi_generator.py`
  - ✅ `generate_openapi_spec()` → `async def generate_openapi_spec()`
  - ✅ `_generate_path_info()` → `async def _generate_path_info()`
  - ✅ `_extract_path_parameters()` → `async def _extract_path_parameters()`
  - ✅ `_normalize_path()` → `async def _normalize_path()`

### PHASE 5: OTHER SERVICES ASYNC
- `backend/app/services/artist_service.py`
  - `get_artists()` → `async def get_artists()`
  - `get_artist()` → `async def get_artist()`
  - `create_artist()` → `async def create_artist()`
  - `update_artist()` → `async def update_artist()`
  - `delete_artist()` → `async def delete_artist()`

- `backend/app/services/album_service.py`
  - `get_albums()` → `async def get_albums()`
  - `get_album()` → `async def get_album()`
  - `create_album()` → `async def create_album()`
  - `update_album()` → `async def update_album()`
  - `delete_album()` → `async def delete_album()`

- `backend/app/services/track_service.py`
  - `get_tracks()` → `async def get_tracks()`
  - `get_track()` → `async def get_track()`
  - `create_track()` → `async def create_track()`
  - `update_track()` → `async def update_track()`
  - `delete_track()` → `async def delete_track()`

- `backend/app/services/persona_service.py`
  - `get_personas()` → `async def get_personas()`
  - `get_persona()` → `async def get_persona()`
  - `create_persona()` → `async def create_persona()`
  - `update_persona()` → `async def update_persona()`
  - `delete_persona()` → `async def delete_persona()`

- `backend/app/services/internal_tool_service.py`
  - `get_tools()` → `async def get_tools()`
  - `get_tool()` → `async def get_tool()`
  - `create_tool()` → `async def create_tool()`
  - `update_tool()` → `async def update_tool()`
  - `delete_tool()` → `async def delete_tool()`

- `backend/app/services/llm_client.py`
  - `create_langchain_tools()` → `async def create_langchain_tools()`
  - `_get_field_type()` → `async def _get_field_type()`
  - `run_chat_streaming()` → `async def run_chat_streaming()` (already async)

- `backend/app/services/crud_service.py`
  - `create()` → `async def create()`
  - `list_all()` → `async def list_all()`
  - `read_one()` → `async def read_one()`
  - `update()` → `async def update()`
  - `delete()` → `async def delete()`
  - `search()` → `async def search()`
  - `bulk_operations()` → `async def bulk_operations()`
  - `selector()` → `async def selector()`
  - `single_selector()` → `async def single_selector()`
  - `_handle_create()` → `async def _handle_create()`
  - `_handle_list()` → `async def _handle_list()`
  - `_handle_read()` → `async def _handle_read()`
  - `_handle_update()` → `async def _handle_update()`
  - `_handle_delete()` → `async def _handle_delete()`
  - `_handle_search()` → `async def _handle_search()`
  - `_handle_bulk()` → `async def _handle_bulk()`
  - `_handle_selector()` → `async def _handle_selector()`
  - `_handle_single_selector()` → `async def _handle_single_selector()`
  - `_apply_filters()` → `async def _apply_filters()`
  - `_apply_sorting()` → `async def _apply_sorting()`

- `backend/app/services/crud_swagger_generator.py`
  - `method_to_swagger()` → `async def method_to_swagger()`
  - `_generate_model_schemas()` → `async def _generate_model_schemas()`
  - `_build_create_schema()` → `async def _build_create_schema()`
  - `_build_update_schema()` → `async def _build_update_schema()`
  - `_build_response_schema()` → `async def _build_response_schema()`
  - `_column_to_openapi_schema()` → `async def _column_to_openapi_schema()`
  - `_generate_crud_paths()` → `async def _generate_crud_paths()`
  - `_extract_path_parameters()` → `async def _extract_path_parameters()`
  - `generate_swagger()` → `async def generate_swagger()`

- `backend/app/services/file_service.py`
  - `upload()` → `async def upload()`
  - `_file_sha256()` → `async def _file_sha256()`

- `backend/app/services/internal_tool_registry.py`
  - `register()` → `async def register()`
  - `get()` → `async def get()`
  - `list()` → `async def list()`
  - `execute()` → `async def execute()`
  - `_admin_system_info()` → `async def _admin_system_info()`

- `backend/app/services/tool_runtime.py`
  - `llm_tool_wrapper()` → `async def llm_tool_wrapper()`
  - `wrapper()` → `async def wrapper()`
  - `_pattern_matches()` → `async def _pattern_matches()`
  - `build_persona_tool_map()` → `async def build_persona_tool_map()`
  - `list_persona_tools()` → `async def list_persona_tools()`
  - `execute_tool()` → `async def execute_tool()`

- `backend/app/services/ai_model_mapping_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/ai_provider_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/ai_analysis_result_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/style_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/rhyme_technique_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/file_category_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/file_link_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/persona_mcp_server_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/mcp_server_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/persona_tool_access_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/tool_invocation_log_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/chat_session_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/chat_message_service.py`
  - All CRUD methods (inherited from base)

- `backend/app/services/chat_history_service.py`
  - All CRUD methods (inherited from base)

### PHASE 6: FRONTEND WEBSOCKET ASYNC
- `src/services/WebSocketManager.js`
  - `joinRoom()` → `async joinRoom()`
  - `leaveRoom()` → `async leaveRoom()`
  - `emit()` → `async emit()`
  - `emitToRoom()` → `async emitToRoom()`

- `vue_libs/nonix/services/BaseApiService.js`
  - `joinRoom()` → `async joinRoom()`
  - `leaveRoom()` → `async leaveRoom()`
  - `onWebSocketEvent()` → `async onWebSocketEvent()`
  - `emitWebSocketEvent()` → `async emitWebSocketEvent()`
  - `emitWebSocketEventToRoom()` → `async emitWebSocketEventToRoom()`

- `vue_libs/nonix-chat/services/ChatService.js`
  - `getSessions()` → `async getSessions()`
  - `getSession()` → `async getSession()`
  - `createSession()` → `async createSession()`
  - `updateSession()` → `async updateSession()`
  - `deleteSession()` → `async deleteSession()`
  - `sendMessage()` → `async sendMessage()`

### PHASE 7: TESTING & VERIFICATION
- Test WebSocket connection
- Test room joining
- Test event delivery
- Test LangChain integration
- Test production stability

### PHASE 8: PRODUCTION DEPLOY
- Deploy with full async architecture
- Monitor WebSocket stability
- Monitor LangChain performance
- Monitor worker health
