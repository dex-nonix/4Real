export class NxObject {
    constructor() {
        this._hooks = new Map();
        this._applyDecorators();
    }

        /**
         * The private engine that walks the prototype chain (MRO-style) to
         * collect and apply all decorators from the inheritance hierarchy.
         */
    _applyDecorators() {
        const decoratorArrays = [];
        let currentClass = this.constructor;

        // Walk up the prototype chain until we hit the base Decoratable class.
        while (currentClass && currentClass !== Decoratable) {
            // Only read the property if it's directly on the class, not inherited.
            if (Object.prototype.hasOwnProperty.call(currentClass, 'decorators')) {
                decoratorArrays.push(currentClass.decorators);
            }
            currentClass = Object.getPrototypeOf(currentClass);
        }

        // Reverse to ensure parent decorators are processed first, then flatten the list.
        const allDecorators = decoratorArrays.reverse().flat();
        
        for (const decorator of allDecorators) {
            if (!decorator || !decorator.hook || !decorator.callback) continue;

            if (!this._hooks.has(decorator.hook)) {
                this._hooks.set(decorator.hook, []);
            }
            this._hooks.get(decorator.hook).push(decorator.callback);
        }
    }

    /**
     * The generic, agnostic hook executor.
     * @param {string} hookName The name of the hook to run (e.g., 'startup', 'render', etc.).
     */
    async _runHook(hookName) {
        const callbacks = this._hooks.get(hookName) || [];
        for (const callback of callbacks) {
            await callback(this); // Pass the instance for context.
        }
    }
}   