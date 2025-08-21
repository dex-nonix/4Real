import re
from abc import ABC
from typing import Dict, Any, List, Callable


class BaseApiService(ABC):
    """Base class for all API services with Swagger documentation capability."""

    def __init__(self):
        """Initialize WebSocket integration."""
        self._socketio = None  # Will be set by APIRouter during registration
        self._logger = None  # Will be set by subclasses

    def set_socketio(self, socketio_instance):
        """Set SocketIO instance for WebSocket communication."""
        self._socketio = socketio_instance

    def send_to_channel(self, channel: str, event: str, data: dict):
        """
        Send event to a specific WebSocket channel.

        Args:
            channel: Channel path (e.g., 'service/channel/123')
            event: Event name (e.g., 'status_updated')
            data: Event data payload
            room: Optional room name (defaults to channel)
        """
        self._websocket_emit(event, data, channel)


    def _websocket_emit(self, event, data: dict, target: str = None):
        _socketio = self._socketio
        if not self._socketio:
            self._logger.error(f"CRITICAL ERROR: SocketIO not initialized for {self.__class__.__name__} - WebSocket communication disabled!")
            return
        
        self._logger.debug(f"Emitting event '{event}' to room '{target}' with data: {data}")
        
        try:
            if hasattr(_socketio, 'server') and hasattr(_socketio.server, 'manager'):
                manager = _socketio.server.manager
                
                self._logger.info(f"=== WebSocket Connection Status ===")
                
                try:
                    all_rooms = manager.rooms
                    self._logger.info(f"Total rooms: {len(all_rooms)}")
                    
                    if all_rooms:
                        self._logger.info(f"Active rooms: {list(all_rooms.keys())}")
                        
                        for room_name, room_data in all_rooms.items():
                            try:
                                if hasattr(room_data, 'sids'):
                                    room_sids = list(room_data.sids)
                                    self._logger.info(f"Room '{room_name}': {len(room_sids)} connections - SIDs: {room_sids}")
                                elif hasattr(room_data, '__iter__'):
                                    room_sids = list(room_data)
                                    self._logger.info(f"Room '{room_name}': {len(room_sids)} connections - SIDs: {room_sids}")
                                else:
                                    self._logger.info(f"Room '{room_name}': {room_data}")
                            except Exception as room_error:
                                self._logger.warning(f"Could not process room '{room_name}': {room_error}")
                    
                    if target and target in all_rooms:
                        target_room = all_rooms[target]
                        try:
                            if hasattr(target_room, 'sids'):
                                target_sids = list(target_room.sids)
                                self._logger.info(f"Target room '{target}': {len(target_sids)} connections - SIDs: {target_sids}")
                            elif hasattr(target_room, '__iter__'):
                                target_sids = list(target_room)
                                self._logger.info(f"Target room '{target}': {len(target_sids)} connections - SIDs: {target_sids}")
                            else:
                                self._logger.info(f"Target room '{target}': {target_room}")
                        except Exception as target_error:
                            self._logger.warning(f"Could not process target room '{target}': {target_error}")
                    elif target:
                        self._logger.info(f"Target room '{target}' not found in active rooms")
                        
                except Exception as rooms_error:
                    self._logger.warning(f"Could not access rooms: {rooms_error}")
                
                try:
                    if hasattr(manager, 'get_participants'):
                        participants = manager.get_participants()
                        self._logger.info(f"Total participants: {len(participants) if participants else 0}")
                    elif hasattr(manager, 'get_sids'):
                        sids = manager.get_sids()
                        self._logger.info(f"Total SIDs: {len(sids) if sids else 0}")
                        if sids:
                            self._logger.info(f"Active SIDs: {list(sids)[:10]}...")  # Show first 10
                    else:
                        self._logger.info("Manager does not have get_participants or get_sids method")
                except Exception as sids_error:
                    self._logger.warning(f"Could not get SIDs: {sids_error}")
                
                self._logger.info(f"=== End WebSocket Status ===")
            
            self._socketio.emit(event, data, room=target, namespace='/')
            self._logger.debug(f"Successfully emitted event '{event}' to room '{target}'")
        except Exception as e:
            self._logger.error(f"Failed to emit event '{event}' to room '{target}': {e}")
            raise

    def get_exposed_ws_methods(self) -> List[Dict[str, Any]]:
        """Get all @expose_ws methods with their metadata."""
        exposed_ws_methods = []

        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, '_expose_ws'):
                method_info = {
                    'name': attr_name,
                    'channel': getattr(method, '_channel'),
                    'summary': getattr(method, '_summary'),
                    'description': getattr(method, '_description')
                }
                exposed_ws_methods.append(method_info)

        return exposed_ws_methods

    def to_swagger(self, service_name: str = None) -> Dict[str, Any]:
        """
        Return Swagger/OpenAPI definitions for this service.
        Each service can override this to provide custom documentation.
        
        Args:
            service_name: The name of the service (e.g., 'chat', 'artists')
        
        Returns:
            Dict containing OpenAPI components, paths, and schemas
        """
        # Default implementation using the working method_to_swagger
        exposed_methods = self.get_exposed_methods()

        paths = {}
        schemas = {}

        for method_info in exposed_methods:
            method = getattr(self, method_info['name'])
            swagger_info = self.method_to_swagger(method, service_name)

            # Add service prefix to path for Swagger (matching API Router behavior)
            raw_path = swagger_info['path']
            if service_name:
                full_path = f"/{service_name}{raw_path}" if not raw_path.startswith(f"/{service_name}") else raw_path
            else:
                full_path = raw_path

            if full_path not in paths:
                paths[full_path] = {}

            for method_name in swagger_info['methods']:
                paths[full_path][method_name.lower()] = swagger_info['operation']

            schemas.update(swagger_info.get('schemas', {}))

        return {
            'schemas': schemas,
            'paths': paths,
            'tags': [service_name]  # ONLY ONE TAG - THE SERVICE NAME
        }

    def get_exposed_methods(self) -> List[Dict[str, Any]]:
        """Get all @expose methods with their metadata."""
        exposed_methods = []

        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, '_exposed'):
                method_info = {
                    'name': attr_name,
                    'path': getattr(method, '_path'),
                    'methods': getattr(method, '_methods', ['GET']),
                    'summary': getattr(method, '_summary'),
                    'description': getattr(method, '_description'),
                    'tags': getattr(method, '_tags', []),
                    'status_codes': getattr(method, '_status_codes', {}),
                    'request_schema': getattr(method, '_request_schema'),
                    'response_schema': getattr(method, '_response_schema')
                }
                exposed_methods.append(method_info)

        return exposed_methods

    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """Extract path parameters from URL pattern like {param_name}."""
        parameters = []

        # Find all {param_name} patterns in the path
        param_pattern = r'\{([^}]+)\}'
        matches = re.findall(param_pattern, path)

        for param_name in matches:
            # Determine parameter type based on common naming conventions
            param_type = "integer"  # Default to integer for IDs
            if param_name in ['name', 'title', 'description', 'content', 'session_name', 'session_icon']:
                param_type = "string"
            elif param_name in ['is_active', 'allow']:
                param_type = "boolean"

            parameter = {
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": param_type},
                "description": f"{param_name.replace('_', ' ').title()}"
            }
            parameters.append(parameter)

        return parameters

    def method_to_swagger(self, method: Callable, service_name: str) -> Dict[str, Any]:
        """DEFAULT: Convert @expose method to Swagger format. ALL subclasses use this by default."""

        # Extract ALL info from @expose decorator
        path = getattr(method, '_path')
        methods = getattr(method, '_methods', ['GET'])
        summary = getattr(method, '_summary')
        description = getattr(method, '_description')
        tags = getattr(method, '_tags', [])
        status_codes = getattr(method, '_status_codes', {})
        request_schema = getattr(method, '_request_schema')
        response_schema = getattr(method, '_response_schema')

        # Provide sensible defaults for missing decorator info
        if not summary:
            summary = f"{method.__name__.replace('_', ' ').title()}"
        if not description:
            description = f"Endpoint for {method.__name__.replace('_', ' ')}"
        # SERVICE NAME IS THE ONLY TAG - ALL SERVICES HAVE A NAME
        tags = [service_name]
        if not status_codes:
            status_codes = {200: 'Success', 400: 'Bad Request', 500: 'Internal Server Error'}

        # Extract path parameters from URL pattern
        path_parameters = self._extract_path_parameters(path)

        # Build operation object
        operation = {
            "tags": tags,
            "summary": summary,
            "description": description,
            "responses": {}
        }

        # Add path parameters if any exist
        if path_parameters:
            operation["parameters"] = path_parameters

        # Add request body if schema provided
        if request_schema:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": request_schema
                    }
                }
            }

        # Add responses with schemas if provided
        for status_code, description_text in status_codes.items():
            response_obj = {"description": description_text}

            # Add response schema if provided
            if response_schema and status_code in [200, 201]:
                response_obj["content"] = {
                    "application/json": {
                        "schema": response_schema
                    }
                }

            operation["responses"][str(status_code)] = response_obj

        return {
            'path': path,
            'methods': methods,
            'operation': operation,
            'tags': tags,
            'schemas': {}  # Empty by default - subclasses can override to add schemas
        }
