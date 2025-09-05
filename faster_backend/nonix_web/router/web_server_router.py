import logging
from abc import ABC
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Type, List, Dict, Any, Optional, Union, Sequence, Callable, TYPE_CHECKING, Awaitable

from fastapi import APIRouter, params, routing, utils, types
from fastapi.datastructures import Default
from starlette.responses import Response, JSONResponse
from starlette.routing import (
    BaseRoute,
)
from starlette.types import ASGIApp, Lifespan

from nonix_web.utils.di import Inject


@dataclass
class _RoutedServiceDefinition:
    prefix: Optional[str]
    tags: Optional[List[Union[str, Enum]]]
    dependencies: Optional[Sequence[params.Depends]]
    default_response_class: Type[Response]
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]]
    callbacks: Optional[List[BaseRoute]]
    routes: Optional[List[BaseRoute]]
    redirect_slashes: bool
    default: Optional[ASGIApp]
    dependency_overrides_provider: Optional[Any]
    route_class: Type[routing.APIRoute]
    on_startup: Optional[Sequence[Callable[[], Any]]]
    on_shutdown: Optional[Sequence[Callable[[], Any]]]
    lifespan: Optional[Lifespan[Any]]
    deprecated: Optional[bool]
    include_in_schema: bool
    generate_unique_id_function: Callable[[routing.APIRoute], str]


@dataclass
class _RoutedServiceMethodDefinition:
    path: str
    response_model: Any
    status_code: Optional[int]
    tags: Optional[List[Union[str, Enum]]]
    dependencies: Optional[Sequence[params.Depends]]
    summary: Optional[str]
    description: Optional[str]
    response_description: str
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]]
    deprecated: Optional[bool]
    methods: Optional[List[str]]
    operation_id: Optional[str]
    response_model_include: Optional[types.IncEx]
    response_model_exclude: Optional[types.IncEx]
    response_model_by_alias: bool
    response_model_exclude_unset: bool
    response_model_exclude_defaults: bool
    response_model_exclude_none: bool
    include_in_schema: bool
    response_class: Type[Response]
    name: Optional[str]
    callbacks: Optional[List[BaseRoute]]
    openapi_extra: Optional[Dict[str, Any]]
    generate_unique_id_function: Callable[[routing.APIRoute], str]


def router(
        prefix: Optional[str] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        routes: Optional[List[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[routing.APIRoute] = routing.APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(utils.generate_unique_id)
):
    def decorator(func):
        setattr(func, '_service_route_info', _RoutedServiceDefinition(
            prefix,
            tags,
            dependencies,
            default_response_class,
            responses,
            callbacks,
            routes,
            redirect_slashes,
            default,
            dependency_overrides_provider,
            route_class,
            on_startup,
            on_shutdown,
            lifespan,
            deprecated,
            include_in_schema,
            generate_unique_id_function
        ))
        return func

    return decorator


def route(
        path: str,
        *,
        response_model: Any = dict,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        methods: Optional[List[str]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[types.IncEx] = None,
        response_model_exclude: Optional[types.IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = Default(JSONResponse),
        name: Optional[str] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(utils.generate_unique_id)
):
    def decorator(func):
        setattr(func, '_route_info', _RoutedServiceMethodDefinition(
            path,
            response_model,
            status_code,
            tags,
            dependencies,
            summary,
            description,
            response_description,
            responses,
            deprecated,
            methods,
            operation_id,
            response_model_include,
            response_model_exclude,
            response_model_by_alias,
            response_model_exclude_unset,
            response_model_exclude_defaults,
            response_model_exclude_none,
            include_in_schema,
            response_class,
            name,
            callbacks,
            openapi_extra,
            generate_unique_id_function
        ))
        return func

    return decorator


def _get_routed_service_definition(cls) -> _RoutedServiceDefinition:
    return getattr(cls, '_service_route_info', None)


def _get_route_info(cls) -> _RoutedServiceMethodDefinition:
    return getattr(cls, '_route_info', None)



from nonix_web.server import NxWebServer


class NxWebServerRouter(ABC):
    server: "NxWebServer" = Inject(NxWebServer)
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
        *args,
        response_converter: Optional[Callable[[Any], JSONResponse]] = None,
        **kwargs
    ) -> JSONResponse:
        """DRY unified method: calls service safely and formats response.

        Combines service call error handling with response formatting in one method.
        Used by all routes for consistent service calls and responses.

        Args:
            service_method: The async service method to call
            *args: Positional arguments for the service method
            response_converter: Optional converter for custom response formatting
            **kwargs: Keyword arguments for the service method

        Returns:
            JSONResponse: Either error response (400/500) or success response

        Usage:
            # Simple case (70% of routes):
            return await self.service_call_and_respond(service.list_items)

            # With custom converter:
            return await self.service_call_and_respond(
                service.get_item, item_id,
                response_converter=lambda r: JSONResponse({'data': r.to_dict()})
            )
        """
        try:
            # Call service method
            result = await service_method(*args, **kwargs)

            # Format response
            if response_converter:
                return response_converter(result)
            return JSONResponse({'data': result})

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
