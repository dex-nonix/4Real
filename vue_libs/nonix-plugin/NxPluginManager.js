export class NxPluginManager {
    constructor() {
        this.availablePlugins = new Map(); // name -> definition
        this.loadedPlugins = new Map();    // name -> instance
    }

    registerPlugins(definitions) {
        console.log("Registering plugin definitions...");
        for (const definition of definitions) {
            this.availablePlugins.set(definition.name, definition);
        }
        console.log(`${this.availablePlugins.size} plugins available.`);
    }

    _resolveDependencies(pluginsToLoad) {
        const resolved = [];
        const visiting = new Set();
        const visit = (pluginName) => {
            if (resolved.includes(pluginName)) return;
            if (visiting.has(pluginName)) throw new Error(`Circular dependency: ${pluginName}`);
            const definition = this.availablePlugins.get(pluginName);
            if (!definition) throw new Error(`Dependency not found: ${pluginName}`);
            visiting.add(pluginName);
            definition.dependencies.forEach(visit);
            visiting.delete(pluginName);
            resolved.push(pluginName);
        };
        pluginsToLoad.forEach(visit);
        return resolved;
    }

    async loadAndStartPlugins(pluginsToLoadConfig) {
        const pluginNames = pluginsToLoadConfig.map(p => p.name);
        console.log("\n--- Starting Plugin Loading ---");

        const loadOrder = this._resolveDependencies(pluginNames);
        console.log(`Load order: ${loadOrder.join(' -> ')}`);

        console.log("\n--- CONFIGURE PHASE ---");
        for (const pluginName of loadOrder) {
            if (this.loadedPlugins.has(pluginName)) continue;

            const definition = this.availablePlugins.get(pluginName);
            const userConfig = pluginsToLoadConfig.find(p => p.name === pluginName)?.config || {};
            
            let PluginClass;
            const entryPoint = definition.entryPoint;

            console.log(`Loading plugin module: '${pluginName}'`);

            if (typeof entryPoint === 'string') {
                // Case 1: Entry point is a path string for dynamic import
                console.log(`  -> from path: ${entryPoint}`);
                const pluginModule = await import(entryPoint);
                PluginClass = pluginModule.default;

            } else if (typeof entryPoint === 'function') {
                // Could be a direct class or a lazy-load function
                if (entryPoint.prototype instanceof BasePlugin) {
                    // Case 2: Entry point is a direct reference to the plugin class constructor
                    console.log(`  -> from direct class reference.`);
                    PluginClass = entryPoint;
                } else {
                    // Case 3: Entry point is a lazy-loading function, e.g., () => import(...)
                    console.log(`  -> from lazy-load function.`);
                    const modulePromise = entryPoint();
                    if (!(modulePromise instanceof Promise)) {
                        throw new Error(`Entry point for '${pluginName}' is a function but did not return a Promise.`);
                    }
                    const pluginModule = await modulePromise;
                    PluginClass = pluginModule.default;
                }
            } else {
                throw new Error(`Unsupported entryPoint type for plugin '${pluginName}': ${typeof entryPoint}`);
            }
            // --- End of Resolver ---

            if (!PluginClass || !(PluginClass.prototype instanceof BasePlugin)) {
                 console.error(`Error: Entry point for '${pluginName}' did not resolve to a valid Plugin class.`);
                 continue;
            }

            const instance = new PluginClass(userConfig);
            instance.name = definition.name;
            instance.version = definition.version;

            await instance.configure();
            this.loadedPlugins.set(pluginName, instance);
        }

        console.log("\n--- STARTUP PHASE ---");
        for (const pluginName of loadOrder) {
            await this.loadedPlugins.get(pluginName).startup();
        }

        console.log("\n--- All plugins loaded and started successfully! ---");
    }
    
    // shutdownAll and other methods remain the same
    async shutdownAll() {
        console.log("\n--- SHUTDOWN PHASE ---");
        for (const pluginName of Array.from(this.loadedPlugins.keys()).reverse()) {
            await this.loadedPlugins.get(pluginName).shutdown();
        }
        this.loadedPlugins.clear();
    }
}