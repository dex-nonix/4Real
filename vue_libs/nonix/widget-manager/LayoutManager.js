import BaseWidgetManager from './BaseWidgetManager.js'
import {LAYOUTS} from "@nonix/registries/layouts.js";
import PlainLayout from "@nonix/layout/PlainLayout.vue";

class LayoutManager extends BaseWidgetManager {
    constructor() {
        super(LAYOUTS)
    }

    getDefaultWidget() {
        return {
            component: PlainLayout,
            props: {} // TODO: not implemented yet
        }
    }
}

export default new LayoutManager()
