import {NxPluginManager} from "@nonix-plugin";
import {NxObject} from "@nonix-obj";
import {NxInject} from "../nonix-di/index.js";


export class NxApp extends NxObject {
    static decorators = [
        services([
            NxPluginManager
        ]),
    ]

    pluginManager = NxInject(NxPluginManager);

    constructor(settings) {
        super();
        this.settings = settings;
    }


    configAndStart = async () => {
        await this.pluginManager.loadAndStartPlugins();
    };
}