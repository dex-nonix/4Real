from typing import Callable, List, Optional


def expose(path: str, methods: Optional[List[str]] = None) -> Callable:
    if methods is None:
        methods = ['GET']

    def decorator(func: Callable) -> Callable:
        setattr(func, '_exposed', True)
        setattr(func, '_path', path)
        setattr(func, '_methods', methods)
        return func

    return decorator

