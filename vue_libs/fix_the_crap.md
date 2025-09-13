# CLEAN & CORRECT: HOW TO PASS 0-N ARGUMENTS TO DESCRIPTORS

## ✅ **CORRECT APPROACH: Pass Arguments When Calling Descriptor Functions**

```javascript
// Each descriptor function can take 0-N arguments as parameters
export function NxSimple() {  // 0 arguments
    return createDescriptor(() => "simple value");
}

export function NxInject(ServiceClass) {  // 1 argument
    let instance = null;
    return createDescriptor(() => {
        if (!instance) {
            instance = di_resolve(ServiceClass);  // Uses the passed ServiceClass
        }
        return instance;
    });
}

export function NxComplex(...args) {  // N arguments using rest parameters
    return createDescriptor(() => processArgs(...args));
}

export function NxConfig(options = {}) {  // 1 argument (options object)
    return createDescriptor(() => useOptions(options));
}

// USAGE: Pass arguments when you CALL the descriptor functions
export class MyPlugin extends NxObject {
    // PASS YOUR 0-N ARGUMENTS HERE (in the function calls):
    simple = NxSimple();                              // ← 0 arguments
    service = NxInject(MyService);                     // ← 1 argument (service class)
    complex = NxComplex(1, 'hello', true, [1,2,3]);   // ← N arguments
    config = NxConfig({multiplier: 2, offset: 5});    // ← 1 argument (options object)
}
```

## 🎯 **KEY POINT: Arguments Go in Function Calls**

**You pass your 0-N arguments when you CALL the descriptor function:**

```javascript
// PASS ARGUMENTS HERE (in the function call):
simple = NxSimple();                    // 0 args - no parameters
service = NxInject(MyService);           // 1 arg - service class
complex = NxComplex(a, b, c, d);        // N args - multiple parameters
config = NxConfig({key: 'value'});      // 1 arg - options object
```

## ✅ **EACH DESCRIPTOR CAN TAKE WHATEVER ARGUMENTS IT NEEDS:**

- **0 args**: `NxSimple()` → No parameters needed
- **1 arg**: `NxInject(ServiceClass)` → Single service class
- **N args**: `NxComplex(a, b, c, ...)` → Multiple parameters via rest
- **Options**: `NxConfig({settings})` → Configuration object

**No property detection, no magic - just normal JavaScript function arguments passed in function calls!** 🎯

**Clean, correct, and simple!** ✅

---

# 0. CHANGES NEEDED TO NxObject.js

## ✅ **ADD DESCRIPTOR SUPPORT TO NxObject:**

### **1. Add _processDescriptors() call in constructor:**
```javascript
export class NxObject {
    constructor() {
        this._hooks = new Map();
        this._applyDecorators();
        this._processDescriptors();  // ← ADD THIS LINE
    }
    // ... rest of existing code
}
```

### **2. Add descriptor processing methods:**

```javascript
export class NxObject {
    constructor() {
        this._hooks = new Map();
        this._applyDecorators();
        this._processDescriptors();
    }

    // ... existing _applyDecorators() method stays the same

    /**
     * Process descriptors by scanning prototype chain for descriptor properties
     */
    _processDescriptors() {
        let currentClass = this.constructor;

        // Walk prototype chain
        while (currentClass && currentClass !== NxObject) {
            const proto = currentClass.prototype;
            const propertyNames = Object.getOwnPropertyNames(proto);

            // Check each property for descriptor marker
            for (const propName of propertyNames) {
                const value = proto[propName];

                // If it's a descriptor (has __descriptor__ marker), set it up
                if (value && value.__descriptor__) {
                    this._setupDescriptorProperty(propName, value);
                }
            }

            currentClass = Object.getPrototypeOf(currentClass);
        }
    }

    /**
     * Set up a property with descriptor behavior
     */
    _setupDescriptorProperty(propName, descriptor) {
        Object.defineProperty(this, propName, {
            get: () => descriptor.get(this),      // ← Descriptor's get method
            set: (value) => descriptor.set(this, value), // ← Descriptor's set method
            enumerable: true,
            configurable: true
        });
    }

    // ... existing _runHook() method stays the same
}
```

## 🎯 **WHAT THESE CHANGES DO:**

1. **`this._processDescriptors()`** - Scans prototype chain for descriptor properties
2. **`_setupDescriptorProperty()`** - Sets up property with descriptor behavior using `Object.defineProperty()`
3. **Walks inheritance hierarchy** - Just like existing `_applyDecorators()` does
4. **Detects descriptors by `__descriptor__` marker** - Automatic detection
5. **Calls descriptor methods** - `descriptor.get(this)` and `descriptor.set(this, value)`

## ✅ **RESULT:**

After these changes, NxObject will automatically:
- Detect descriptor properties on class prototypes
- Set up lazy descriptor behavior for those properties
- Handle inheritance properly (parent descriptors processed first)
- Work alongside existing decorator system

**NxObject now supports both traditional decorators AND new descriptors!** 🎯

---

# 0. SUGAR FUNCTION FOR EASY DESCRIPTOR CREATION

```javascript
// ✅ SWEET SUGAR: createDescriptor(getter, setter, extraProps)
export function createDescriptor(getterFn, setterFn = null, extraProps = {}) {
    return {
        __descriptor__: true,
        ...extraProps,  // Merge extra properties
        get(instance) {
            if (instance === undefined) return this;
            return getterFn.call(this, instance);
        },
        set(instance, value) {
            if (instance !== undefined && setterFn) {
                setterFn.call(this, instance, value);
            }
        }
    };
}
```