import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {NX_LAYOUTS} from "@nonix/registries/layouts.js";
import NxPlainLayout from "@nonix/layout/NxPlainLayout.vue";

class NxLayoutManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_LAYOUTS)
    }

    getDefaultWidget() {
        return {
            component: NxPlainLayout,
            props: {} // TODO: not implemented yet
        }
    }
}

export default new NxLayoutManager()
