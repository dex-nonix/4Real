import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {NX_PAGES} from '@nonix-dynamic/registries/pages.js'

class NxPageManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_PAGES)
    }

    getDefaultWidget() {
        return {component: {header: {title: 'NxPage'}, widgets: []}, props: {}}
    }
}

export default new NxPageManager()
