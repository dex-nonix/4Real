import NxBaseWidgetManager from '@nonix-dynamic/manager/NxBaseWidgetManager.js'
import {NX_DISPLAY_WIDGETS} from '@nonix-dynamic/registries/display-widgets.js'

class NxDisplayWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_DISPLAY_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'span', props: {class: 'text-sm'}}
    }
}

export default new NxDisplayWidgetManager()


