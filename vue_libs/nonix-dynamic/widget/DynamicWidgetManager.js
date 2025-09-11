import BaseWidgetManager from '@nonix/widget-manager/BaseWidgetManager.js'
import {DYNAMIC_WIDGETS} from '@nonix-dynamic/widget/dynamic-widgets.js'

class DynamicWidgetManager extends BaseWidgetManager {
    constructor() {
        super(DYNAMIC_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'div', props: {class: 'text-sm', innerHTML: 'Unknown widget'}}
    }
}

export default new DynamicWidgetManager()


