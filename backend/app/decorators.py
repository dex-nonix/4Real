from typing import Callable, List, Optional, Dict, Any


def expose(
    path: str, 
    methods: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status_codes: Optional[Dict[int, str]] = None,
    # 🚀 Direct schema definition
    request_schema: Optional[Dict[str, Any]] = None,
    response_schema: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Enhanced decorator to expose service method as API route with OpenAPI metadata.
    
    Args:
        path: API path (e.g., '/{id}', '/search')
        methods: HTTP methods (default: ['GET'])
        summary: Short description for OpenAPI
        description: Detailed description for OpenAPI
        tags: API grouping tags (e.g., ['Artists'])
        status_codes: HTTP status codes and descriptions
        request_schema: Direct OpenAPI schema for request body
        response_schema: Direct OpenAPI schema for response body
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
        setattr(func, '_status_codes', status_codes or {200: 'Success'})
        
        # 🚀 Direct schema support
        setattr(func, '_request_schema', request_schema)
        setattr(func, '_response_schema', response_schema)
        
        return func
    
    return decorator

