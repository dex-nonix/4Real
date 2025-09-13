# Frontend Plugin System Analysis

## Overview
This document analyzes how to implement a plugin system for the Vue.js frontend that mirrors the backend plugin architecture while adapting to frontend technologies.

## Backend Plugin Architecture (Reference)

### Framework Packages
- `nonix_di/decorator.py` - Dependency injection decorators (`injectables`)
- `nonix_web/decorator.py` - Web/routing decorators (`web_routers`)
- `nonix_plugin/` - Base plugin system (no decorators)

### Plugin Packages Can Define Decorators
- `nonix_web_agentic/llm/decorator.py` - Specialized LLM decorators (`llm_tools`)
- Other plugin packages can extend the decorator system

### Plugin Loading
- Filesystem discovery of `plugin.json`
- Dependency resolution
- Lifecycle: configure → startup → shutdown
- Decorator pattern: functions returning `{hook, callback}` objects

## Frontend Plugin Architecture (Adapted)

### Existing Frontend Packages
- `vue_libs/nonix/` - Base framework (widget managers, registries)
- `vue_libs/nonix-dynamic/` - Dynamic components/widgets
- `vue_libs/nonix-router/` - Vue routing system
- `vue_libs/nonix-plugin/` - Base plugin system
- Individual plugin packages: `nonix-chat/`, `nonix-crud/`, etc.

### Required Framework Packages
- `vue_libs/nonix-di/` - Dependency injection decorators (needs creation)
- Existing packages can contain decorators:
  - `vue_libs/nonix-router/decorator.js` - Route decorators
  - `vue_libs/nonix-dynamic/decorator.js` - Component/widget decorators

### Decorator Pattern (Vanilla JavaScript - Backend Compatible)
```javascript
// injectables - ONLY registers services
export function injectables(serviceClasses) {
  return {
    hook: 'configure',
    callback: () => {
      // ONLY register services
      for (const serviceClass of serviceClasses) {
        diContainer.register(serviceClass);
      }
    }
  };
}


// di_register - Registration function (main app only - not for plugins)
export function di_register(serviceClass, singleton = true, instance = null) {
  diContainer.register(serviceClass, singleton, instance);
  return serviceClass;
}

// di_resolve - Manual resolution
export function di_resolve(serviceClass) {
  return diContainer.resolve(serviceClass);
}
```

### Plugin Structure (Static Decorators Array)
```javascript
// vue_libs/nonix-chat/plugin.js
import { NxBasePlugin } from '@nonix-plugin';
import { injectables, di_resolve } from '@nonix-di';
import { routes } from '@nonix-router';
import { displayWidgets } from '@nonix-dynamic';

export class NxChatPlugin extends NxBasePlugin {
  static decorators = [
    injectables([NxChatService, NxChatSessionService]), // ONLY WAY
    routes([{type: 'crud', entity: 'chat-sessions'}]),
    displayWidgets(['NxLlmTool'])
  ];

  constructor(config) {
    super(config);
    this.name = 'chat';
    this.version = '0.5.0';
  }

  async startup() {
    // Manual resolution
    const chatService = di_resolve(NxChatService);
    const sessionService = di_resolve(NxChatSessionService);

    await chatService.initialize();
    await sessionService.loadAll();
  }
}
```

## Technology Adaptations

| Backend Technology | Frontend Equivalent |
|-------------------|-------------------|
| Python DI container | JavaScript DI container (same logic) |
| FastAPI route registration | Vue router configuration |
| Database service instances | Client-side service instances |
| HTTP server | Client-side app |
| Filesystem scanning | Filesystem scanning (same) |
| Python importlib | JavaScript dynamic imports |
| Python descriptors (NxInject) | Descriptor-like injection (NxInject function) |
| injectables decorator | injectables decorator (exact same API) |
| di_register function | di_register function (main app only) |
| di_resolve function | di_resolve function (exact same API) |

## Dependency Injection (Descriptor-like Injection)

**Backend Plugins**: `@injectables([...])` + `NxInject` descriptors
**Frontend Plugins**: `injectables([...])` + `NxInject()` function (descriptor-like)
**Main App**: `di_register(...)` function calls allowed

Exact backend plugin pattern - decorator registration + descriptor injection

```javascript
// Plugin registers services + uses descriptor-like injection
export class ChatPlugin extends NxInjectable {
  static decorators = [
    injectables([ChatService, SessionService]) // Registration decorator
  ];

  // Descriptor-like injection (lazy + cached like Python NxInject)
  chatService = NxInject(ChatService);
  sessionService = NxInject(SessionService);

  async startup() {
    // Direct access - getter resolves lazily like Python descriptors
    await this.chatService.initialize();
    await this.sessionService.loadAll();
  }
}

// Main app can use direct di_register calls
export class MainApp {
  constructor() {
    // Direct registration allowed here
    di_register(SomeGlobalService, false, someInstance);
    di_register(AnotherService);
  }
}

// Components can also use descriptor-like injection
export class ChatComponent extends NxInjectable {
  // Descriptor-like injection (lazy + cached)
  chatService = NxInject(ChatService);

  async loadMessages() {
    // Direct access - getter resolves lazily
    return await this.chatService.getMessages();
  }
}
```

## Key Principles

1. **Same Plugin Loading Logic** - Discovery, dependencies, lifecycle
2. **Static Decorator Arrays** - `static decorators = []` with `{hook, callback}` objects
3. **Vanilla JavaScript** - No @ syntax decorators, no descriptors, no transpilation needed
4. **Framework vs Plugin Decorators** - Base framework provides generic decorators, plugin packages can provide specialized ones
5. **Technology Adaptation** - Backend server concepts adapted to frontend client concepts
6. **Package Structure** - Mirror backend multi-package architecture

## Implementation Steps

1. Create `vue_libs/nonix-di/` package with DI container, `injectables()` decorator, `di_register()` and `di_resolve()` functions
2. Add `decorator.js` to `vue_libs/nonix-router/` for route decorators
3. Add `decorator.js` to `vue_libs/nonix-dynamic/` for component/widget decorators
4. Plugin manager already supports static decorator arrays (NxObject system)
5. Update plugins to use `injectables([...])` ONLY for registration (like backend plugins)
6. Main app uses `di_register()` for direct registration (like backend web server)
7. Test plugin loading and DI resolution

## DI Container Structure

```javascript
// vue_libs/nonix-di/
// ├── di.js            # Container class (internal), di_register/di_resolve functions
// ├── decorators.js    # injectables(), NxInject() functions, NxInjectable class
// └── index.js         # Export functions only
```

## NxInject Descriptor-like Injection

NxInject provides descriptor-like injection in vanilla JavaScript:

```javascript
// NxInject() - Descriptor-like injection function (mimics Python NxInject)
export function NxInject(ClassOrFactory) {
  return { __inject__: true, ClassOrFactory };
}

// NxInjectable - Base class with descriptor-like injection support
export class NxInjectable {
  constructor() {
    this._setupInjections();
  }

  _setupInjections() {
    for (const key of Object.keys(this)) {
      const val = this[key];
      if (val && val.__inject__) {
        const Cls = val.ClassOrFactory;
        let cached;
        Object.defineProperty(this, key, {
          configurable: true,
          enumerable: true,
          get() {
            if (cached === undefined) {
              // Support class or factory function
              cached = typeof Cls === 'function' && Cls.prototype
                ? new Cls()
                : Cls();
            }
            return cached;
          },
          set(v) {
            cached = v; // Allow manual override
          },
        });
      }
    }
  }
}

// Usage - Descriptor-like injection
export class ChatPlugin extends NxInjectable {
  static decorators = [
    injectables([ChatService, SessionService]) // Registration decorator
  ];

  // Descriptor-like injection (lazy + cached like Python NxInject)
  chatService = NxInject(ChatService);
  sessionService = NxInject(SessionService);

  async startup() {
    // Direct access - getter resolves lazily like Python descriptors
    await this.chatService.initialize();
    await this.sessionService.loadAll();
  }
}
```

## Plugin Agnosticism

- **Base Plugin System**: No decorator definitions (clean separation)
- **Framework Packages**: Provide generic decorators (`injectables`, `routes`, etc.)
- **Plugin Packages**: Can provide specialized decorators for unique features
- **Plugin Classes**: Use `injectables([...])` + `NxInject()` for registration + injection (like backend)
- **Main App**: Uses `di_register()` for direct registration (like backend web server)
- **Frontend Adaptation**: Descriptor-like injection with `NxInject()` (mimics Python descriptors)
- **Same Interface**: Property access like backend `self.service` (lazy + cached)

Provides the **exact backend plugin pattern** in vanilla JavaScript.


