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

export function NxInject(ServiceClass) {
    let instance = null;
    return {
        __descriptor__: true,
        get(target) {
            if (!instance) {
                instance = di_resolve(ServiceClass);
            }
            return instance;
        },
        set(target, value) {
            instance = value;
        }
    };
}

