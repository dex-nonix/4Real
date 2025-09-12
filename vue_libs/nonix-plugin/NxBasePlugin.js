import { NxObject } from '@nonix-obj';

export class NxBasePlugin extends NxObject {
    constructor(config) {
        super();
        this.name = "Unnamed Plugin";
        this.version = "0.0.0";
        this.config = config;
    }

    async configure() {
        console.log(`[${this.name}] Running CONFIGURE hooks...`);
        await this._runHook('configure');
    }

    async startup() {
        console.log(`[${this.name}] Running STARTUP hooks...`);
        await this._runHook('startup');
    }

    async shutdown() {
        console.log(`[${this.name}] Running SHUTDOWN hooks...`);
        await this._runHook('shutdown');
    }
}