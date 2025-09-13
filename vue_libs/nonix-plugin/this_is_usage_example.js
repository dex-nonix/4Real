import { NxBasePlugin } from './NxBasePlugin.js'; 
import { NxPluginManager } from './NxPluginManager.js';


// core/decorators.js

export function withServices(servicesToInject) {
    return {
        hook: 'startup', // Binds to the 'startup' hook
        callback: async (pluginInstance) => { /* ... logic ... */ }
    };
}

export function withRoutes(routerClasses) {
    return {
        hook: 'configure', // Binds to the 'configure' hook
        callback: (pluginInstance) => { /* ... logic ... */ }
    };
}

//---------------------

class CorePlugin extends NxBasePlugin {
    static decorators = [
        withServices([/*...*/])
    ];
}

class WebAppPlugin extends CorePlugin {
    static decorators = [
        withRoutes([/*...*/])
    ];
}

const pluginDefinitions = [
    {
        name: "Core",
        version: "1.0.0",
        dependencies: [],
        // Type 1: String path for standard dynamic import.
        entryPoint: "./plugins/core-plugin/index.js"
    },
    {
        name: "WebApp",
        version: "1.0.0",
        dependencies: ["Core"],
        // Type 3: Lazy-load function for bundler-friendly code splitting.
        entryPoint: () => import('./plugins/web-app-plugin/index.js')
    },
    {
        name: "Logger",
        version: "2.0.0",
        dependencies: [],
        // Type 2: Direct class constructor for built-in plugins.
        entryPoint: BuiltInLoggerPlugin
    }
];




// --- Main Application Logic ---

async function runApplication() {
    const manager = new NxPluginManager();
    manager.registerPlugins(pluginDefinitions);

    const pluginsToLoad = [
        { name: 'WebApp', config: { port: 8080 } },
        { name: 'Logger', config: {} }
        // 'Core' will be loaded automatically as a dependency of 'WebApp'.
    ];

    await manager.loadAndStartPlugins(pluginsToLoad);

    console.log("\n✅ Application is running.");
    
    await manager.shutdownAll();
    console.log("\n✅ Application shut down gracefully.");
}

runApplication().catch(console.error);