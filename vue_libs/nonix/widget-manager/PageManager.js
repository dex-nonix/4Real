import NxBaseWidgetManager from './NxBaseWidgetManager.js'
import {PAGES} from '@nonix/registries/pages.js'

class PageManager extends NxBaseWidgetManager {
    constructor() {
        super(PAGES)
    }

    getDefaultWidget() {
        return {component: {header: {title: 'Page'}, widgets: []}, props: {}}
    }
}

export default new PageManager()
