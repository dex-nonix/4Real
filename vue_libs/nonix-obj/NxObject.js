export class NxObject {
    constructor() {
        if (!this.constructor._isInitialized) {
            this.constructor.initialize();
        }
        // All instances get a reference to the same pre-computed hooks map.
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
                // --- Decorator Collection ---
                if (Object.prototype.hasOwnProperty.call(currentClass, 'decorators')) {
                    decoratorArrays.push(currentClass.decorators);
                }

                // --- Descriptor Processing ---
                const proto = currentClass.prototype;
                const propertyNames = Object.getOwnPropertyNames(proto);

                for (const propName of propertyNames) {
                    const value = proto[propName];
                    if (value && value.__descriptor__) {
                        // Define the property on the class's PROTOTYPE.
                        this._setupDescriptorProperty(this.prototype, propName, value);
                    }
                }
            }
            currentClass = Object.getPrototypeOf(currentClass);
        }

        // --- Finalize Decorator Application ---
        const allDecorators = decoratorArrays.reverse().flat();
        
        // Inherit hooks from the parent class to ensure they are additive.
        const parentHooks = Object.getPrototypeOf(this)._processedHooks;
        const processedHooks = new Map(parentHooks ? JSON.parse(JSON.stringify(Array.from(parentHooks))) : null);

        for (const decorator of allDecorators) {
            if (!decorator || !decorator.hook || !decorator.callback) continue;

            if (!processedHooks.has(decorator.hook)) {
                processedHooks.set(decorator.hook, []);
            }
            processedHooks.get(decorator.hook).push(decorator.callback);
        }
        
        // Cache the processed hooks and set the flag ON THE CLASS.
        this._processedHooks = processedHooks;
        this._isInitialized = true; // Prevents this method from ever running again for this class.
    }

    /**
     * Helper to set up a property with descriptor behavior on a given prototype.
     */
    static _setupDescriptorProperty(targetPrototype, propName, descriptor) {
        Object.defineProperty(targetPrototype, propName, {
            get: function() { return descriptor.get(this); },      
            set: function(value) { descriptor.set(this, value); },
            enumerable: true,
            configurable: true
        });
    }

    /**
     * The hook executor remains unchanged.
     */
    async _runHook(hookName) {
        const callbacks = this._hooks.get(hookName) || [];
        for (const callback of callbacks) {
            await callback(this);
        }
    }
}