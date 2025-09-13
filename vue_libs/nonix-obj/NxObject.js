export class NxObject {
    constructor() {
        if (!this.constructor._isInitialized) {
            this.constructor.initialize();
        }
        this._hooks = this.constructor._processedHooks;
    }

    static initialize() {
        const parent = Object.getPrototypeOf(this);
        if (parent.initialize && !parent._isInitialized) {
            parent.initialize();
        }

        const decoratorArrays = [];
        let currentClass = this;

        while (currentClass && currentClass !== NxObject) {
            if (!Object.prototype.hasOwnProperty.call(currentClass, '_isInitialized')) {
                if (Object.prototype.hasOwnProperty.call(currentClass, 'decorators')) {
                    decoratorArrays.push(currentClass.decorators);
                }

                const proto = currentClass.prototype;
                const propertyNames = Object.getOwnPropertyNames(proto);

                for (const propName of propertyNames) {
                    const value = proto[propName];
                    if (value && value.__descriptor__) {
                        this._setupDescriptorProperty(this.prototype, propName, value);
                    }
                }
            }
            currentClass = Object.getPrototypeOf(currentClass);
        }

        const allDecorators = decoratorArrays.reverse().flat();
        const parentHooks = Object.getPrototypeOf(this)._processedHooks;
        const processedHooks = new Map(parentHooks ? JSON.parse(JSON.stringify(Array.from(parentHooks))) : null);

        for (const decorator of allDecorators) {
            if (!decorator || !decorator.hook || !decorator.callback) continue;

            if (!processedHooks.has(decorator.hook)) {
                processedHooks.set(decorator.hook, []);
            }
            processedHooks.get(decorator.hook).push(decorator.callback);
        }

        this._processedHooks = processedHooks;
        this._isInitialized = true;
    }

    static _setupDescriptorProperty(targetPrototype, propName, descriptor) {
        Object.defineProperty(targetPrototype, propName, {
            get: function () { return descriptor.get(this); },
            set: function (value) { descriptor.set(this, value); },
            enumerable: true,
            configurable: true
        });
    }

    async _runHook(hookName) {
        const callbacks = this._hooks.get(hookName) || [];
        for (const callback of callbacks) {
            await callback(this);
        }
    }
}