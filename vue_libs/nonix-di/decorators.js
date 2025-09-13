import { di_register } from './di.js';

export function injectables(serviceClasses) {
  return {
    hook: 'configure',
    callback: () => {
      for (const serviceClass of serviceClasses) {
        di_register(serviceClass);
      }
    }
  };
}

export function NxInject(ClassOrFactory) {
  return { __inject__: true, ClassOrFactory };
}

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
