# Nonix DI - Dependency Injection System

## Quick Start

```python
from nonix_di import di_register, NxInject

# Register dependencies
di_register(DatabaseService)
di_register(UserService)

# Use as class attributes (descriptors)
class UserController:
    user_service = NxInject(UserService)
    
    def get_users(self):
        return self.user_service.get_all()
```

## Key Features

- **Descriptors**: `NxInject` works as class attributes, not in constructors
- **Lazy Loading**: Dependencies are resolved only when first accessed
- **Singleton/Transient**: Control instance lifecycle
- **Plugin Integration**: Bulk register services with `@injectables`
- **Optional Dependencies**: Use `required=False` for optional services

## Registration

```python
from nonix_di import di_register

# Singleton (default)
di_register(DatabaseService)

# Transient (new instance each time)
di_register(UserService, singleton=False)

# Specific instance
di_register(DatabaseService, instance=my_db_instance)
```

## Property Injection

```python
from nonix_di import NxInject

class MyService:
    # Class attribute - not in __init__!
    db = NxInject(DatabaseService)
    config = NxInject(AppConfig)
    optional_service = NxInject(OptionalService, required=False)
    
    def do_work(self):
        return self.db.query()  # Resolved on first access
```

## Plugin Integration

```python
from nonix_di import injectables

@injectables([DatabaseService, UserService, EmailService])
class MyPlugin:
    pass
```

## Manual Resolution

```python
from nonix_di import di_resolve

# Get dependency manually
db = di_resolve(DatabaseService)

# With error handling
try:
    service = di_resolve(SomeService)
except TypeError:
    print("Service not registered")
```

## Common Patterns

### Service Layer
```python
di_register(DatabaseService)
di_register(UserRepository)
di_register(UserService)

class UserController:
    user_service = NxInject(UserService)
    
    def create_user(self, data):
        return self.user_service.create(data)
```

### Configuration
```python
class Config:
    def __init__(self):
        self.debug = True

di_register(Config)

class Service:
    config = NxInject(Config)
    
    def run(self):
        if self.config.debug:
            print("Debug mode")
```

### Circular Dependencies
```python
# Works automatically - all dependencies are lazy
class ServiceA:
    service_b = NxInject(ServiceB)
    
class ServiceB:
    service_a = NxInject(ServiceA)
```

## API Reference

### di_register(dependency, singleton=True, instance=None)
Register a dependency in the container.

### NxInject(dependency, required=True)
Descriptor for property injection.

### di_resolve(dependency, required=True)
Manually resolve a dependency.

### injectables(classes)
Decorator for bulk service registration in plugins.