import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {EDIT_WIDGETS} from '@nonix/registries/edit-widgets.js'

class EditWidgetManager extends NxBaseWidgetManager {
    constructor() {
        super(EDIT_WIDGETS)
    }

    getDefaultWidget() {
        return {component: 'input', props: {class: 'w-full'}}
    }
}

export default new EditWidgetManager()


