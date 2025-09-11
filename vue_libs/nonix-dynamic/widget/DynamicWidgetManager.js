import NxBaseWidgetManager from '@nonix/widget-manager/NxBaseWidgetManager.js'
import {DYNAMIC_WIDGETS} from '@nonix-dynamic/widget/dynamic-widgets.js'

class DynamicWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(DYNAMIC_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'div', props: {class: 'text-sm', innerHTML: 'Unknown widget'}}
    }
}

export default new DynamicWidgetManager()


