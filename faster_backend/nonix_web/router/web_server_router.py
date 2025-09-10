import logging
from abc import ABC
from dataclasses import asdict
from typing import Any, Optional, Callable, Awaitable

from fastapi import APIRouter
from starlette.responses import JSONResponse

from nonix_di.resolve import NxInject
from .decorators import _RoutedServiceDefinition, _RoutedServiceMethodDefinition
from ..server import NxWebServer


def _get_routed_service_definition(cls) -> _RoutedServiceDefinition:
    return getattr(cls, '_service_route_info', None)


def _get_route_info(cls) -> _RoutedServiceMethodDefinition:
    return getattr(cls, '_route_info', None)


class NxWebServerRouter(ABC):
    server: "NxWebServer" = NxInject(NxWebServer)
    router: APIRouter

    def __init__(self, router: APIRouter):
        self.router = router
        self._logger = logging.getLogger(self.__class__.__name__)

    async def send_ws_message(self, room: str, message: dict):
        try:
            event = message.get('event') if isinstance(message, dict) else None
            data = message.get('data') if isinstance(message, dict) else None
            if not event or data is None:
                self._logger.error(f"Invalid WS payload for room {room}: missing 'event' or 'data'")
                return
            await self.server.sio.emit(event, data, room=room)
        except Exception as e:
            self._logger.error(f"Failed to send message to room {room}: {e}")

    async def service_call_and_respond(
            self,
            service_method: Callable[..., Awaitable[Any]],
            service_args: tuple = (),
            service_kwargs: dict = {},
            response_converter: Optional[Callable[[Any], Any]] = None
    ) -> JSONResponse:
        """DRY unified method: calls service safely and formats response.

        Combines service call error handling with response formatting in one method.
        Used by all routes for consistent service calls and responses.

        Args:
            service_method: The async service method to call
            service_args: Tuple of positional arguments for the service method (default: ())
            service_kwargs: Dict of keyword arguments for the service method (default: {})
            response_converter: Optional converter that returns data dict (not JSONResponse)

        Returns:
            JSONResponse: Either error response (400/500) or success response

        Usage:
            # Simple case (70% of routes):
            return await self.service_call_and_respond(service.list_items)

            # With arguments:
            return await self.service_call_and_respond(
                service.get_item, service_args=(item_id,)
            )

            # With custom converter (return data dict):
            return await self.service_call_and_respond(
                service.get_item, service_args=(item_id,),
                response_converter=lambda r: {'data': r.to_dict()}
            )

            # With status code (return tuple: data_dict, status_code):
            return await self.service_call_and_respond(
                service.create_item, service_args=(data,),
                response_converter=lambda r: ({'data': r.to_dict()}, 201)
            )
        """
        try:
            # Call service method
            result = await service_method(*service_args, **service_kwargs)

            # Format response - converters return data dicts (or tuples for status codes)
            if response_converter:
                converter_result = response_converter(result)
                if isinstance(converter_result, tuple):
                    data, status_code = converter_result
                else:
                    data, status_code = converter_result, 200
            else:
                data, status_code = {'data': result}, 200
            return JSONResponse(data, status_code)

        except ValueError as e:
            # Business logic errors -> 400 Bad Request
            return JSONResponse({'error': str(e)}, 400)
        except Exception as e:
            # System errors -> 500 Internal Server Error
            return JSONResponse({'error': str(e)}, 500)

    @classmethod
    def to_router(cls, *args, **kwargs) -> APIRouter:
        router = APIRouter(**asdict(_get_routed_service_definition(cls)))
        inst = cls(router, *args, **kwargs)
        for method_name in dir(inst):
            method = getattr(inst, method_name)
            route_definition = _get_route_info(method)
            if route_definition:
                router.add_api_route(endpoint=method, **asdict(route_definition))
        return router
