# AI_README: Nonix DI System API

## Requirements
- Python 3.8+
- No external dependencies

## Core Classes & Interfaces

### Dependency Injection
```python
class NxInject(Generic[T]):
    """Property descriptor for dependency injection"""
    def __init__(self, dependency: Type[T], required: bool = True) -> None
    def __get__(self, instance, owner) -> T | None: """Resolve dependency on first access"""
    # Public attributes
    dependency: Type[T]
    required: bool
```

### Container
```python
class Container:
    """Internal dependency container"""
    def register(self, dependency: InjectDependencyType, singleton: bool = True, intance: Any = None) -> None: """Register dependency"""
    def resolve(self, dependency: InjectDependencyType) -> T | None: """Resolve dependency instance"""
    # Private attributes
    _providers: Dict[Type[T], Dict[str, Any]]
    _singletons: Dict[Type[T], T]
```

### Type Definitions
```python
InjectDependencyType = Type[T] | Callable[[], T]
```

## Functions
```python
def di_register(dependency: InjectDependencyType, singleton: bool = True, instance: Any = None) -> InjectDependencyType:
    """Register dependency in container"""

def di_resolve(dependency: InjectDependencyType, required: bool = True) -> T | None:
    """Manually resolve dependency from container"""
```

## Decorators
```python
def injectables(classes: list) -> Callable:
    """Register multiple services with plugin system"""
```

## Integration Points
```python
# Property injection (most common)
class MyService:
    db = NxInject(DatabaseService)
    config = NxInject(AppConfig, required=False)

# Manual resolution
db_service = di_resolve(DatabaseService)
optional_service = di_resolve(OptionalService, required=False)

# Registration
di_register(DatabaseService)  # Singleton (default)
di_register(UserService, singleton=False)  # Transient
di_register(ConfigService, instance=my_config)  # Specific instance

# Plugin integration
@injectables([DatabaseService, CacheService])
class MyPlugin(BasePlugin):
    pass
```

## Configuration Schema
```json
{
  "name": "my-di-plugin",
  "class": "MyPlugin",
  "dependencies": []
}
```
