import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {NX_LAYOUTS} from "@nonix-dynamic/registries/layouts.js";
import NxPlainLayout from "@nonix/layout/NxPlainLayout.vue";

class NxLayoutManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_LAYOUTS)
    }

    getDefaultWidget() {
        return {
            component: NxPlainLayout,
            props: {}
        }
    }
}

export default new NxLayoutManager()
