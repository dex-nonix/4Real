import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {NX_PAGES} from '@nonix/registries/pages.js'

class NxPageManager extends NxBaseWidgetManager {
    constructor() {
        super(NX_PAGES)
    }

    getDefaultWidget() {
        return {component: {header: {title: 'Page'}, widgets: []}, props: {}}
    }
}

export default new NxPageManager()
