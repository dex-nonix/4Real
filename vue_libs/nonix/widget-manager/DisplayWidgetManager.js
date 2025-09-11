import NxBaseWidgetManager from '@nonix/widget-manager/NxBaseWidgetManager.js'
import {DISPLAY_WIDGETS} from '@nonix/registries/display-widgets.js'

class DisplayWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(DISPLAY_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'span', props: {class: 'text-sm'}}
    }
}

export default new DisplayWidgetManager()


