from typing import Callable, List, Optional, Dict, Any, Type


def expose(
    path: str, 
    methods: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    request_dto: Optional[Type] = None,
    response_dto: Optional[Type] = None,
    status_codes: Optional[Dict[int, str]] = None
) -> Callable:
    """
    Enhanced decorator to expose service method as API route with OpenAPI metadata.
    
    Args:
        path: API path (e.g., '/{id}', '/search')
        methods: HTTP methods (default: ['GET'])
        summary: Short description for OpenAPI
        description: Detailed description for OpenAPI
        tags: API grouping tags (e.g., ['Artists'])
        request_dto: DTO class for request validation
        response_dto: DTO class for response schema
        status_codes: HTTP status codes and descriptions
    """
    if methods is None:
        methods = ['GET']
    
    def decorator(func: Callable) -> Callable:
        # Set basic route info (existing functionality)
        setattr(func, '_exposed', True)
        setattr(func, '_path', path)
        setattr(func, '_methods', methods)
        
        # Set OpenAPI metadata (new functionality)
        setattr(func, '_summary', summary)
        setattr(func, '_description', description)
        setattr(func, '_tags', tags or [])
        setattr(func, '_request_dto', request_dto)
        setattr(func, '_response_dto', response_dto)
        setattr(func, '_status_codes', status_codes or {200: 'Success'})
        
        return func
    
    return decorator

