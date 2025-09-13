class Container {
  constructor() {
    this._providers = new Map();
    this._singletons = new Map();
  }

  register(dependency, singleton = true, instance = null) {
    const key = dependency;

    if (typeof dependency !== 'function') {
      throw new TypeError("The dependency must be a class or a callable function.");
    }

    if (instance !== null) {
      this._singletons.set(dependency, instance);
    }

    this._providers.set(key, {
      provider: dependency,
      singleton: singleton
    });
  }

  resolve(dependency) {
    if (!this._providers.has(dependency)) {
      return null;
    }

    const config = this._providers.get(dependency);
    const provider = config.provider;
    const isSingleton = config.singleton;

    if (isSingleton) {
      if (!this._singletons.has(dependency)) {
        const instance = typeof provider.prototype !== 'undefined'
          ? new provider()
          : provider();
        this._singletons.set(dependency, instance);
      }
      return this._singletons.get(dependency);
    } else {
      return typeof provider.prototype !== 'undefined'
        ? new provider()
        : provider();
    }
  }
}

const _container = new Container();

export function di_register(dependency, singleton = true, instance = null) {
  _container.register(dependency, singleton, instance);
  return dependency;
}

export function di_resolve(dependency, required = true) {
  const resolved = _container.resolve(dependency);
  if (resolved === null && required) {
    throw new TypeError(`Dependency '${dependency.name || dependency}' is not registered.`);
  }
  return resolved;
}
