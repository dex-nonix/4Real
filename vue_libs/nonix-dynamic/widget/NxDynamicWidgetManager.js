import NxBaseWidgetManager from '@nonix/widget-manager/NxBaseWidgetManager.js'
import {NX_DYNAMIC_WIDGETS} from '@nonix-dynamic/widget/dynamic-widgets.js'

class NxDynamicWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_DYNAMIC_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'div', props: {class: 'text-sm', innerHTML: 'Unknown widget'}}
    }
}

export default new NxDynamicWidgetManager()


