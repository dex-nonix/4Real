import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {LAYOUTS} from "@nonix/registries/layouts.js";
import NxPlainLayout from "@nonix/layout/NxPlainLayout.vue";

class NxLayoutManager extends NxBaseWidgetManager {
    constructor() {
        super(LAYOUTS)
    }

    getDefaultWidget() {
        return {
            component: NxPlainLayout,
            props: {} // TODO: not implemented yet
        }
    }
}

export default new NxLayoutManager()
