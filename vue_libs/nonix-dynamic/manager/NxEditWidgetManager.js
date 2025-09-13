import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {NX_EDIT_WIDGETS} from '@nonix-dynamic/registries/edit-widgets.js'

class NxEditWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_EDIT_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'input', props: {class: 'w-full'}}
    }
}

export default new NxEditWidgetManager()


