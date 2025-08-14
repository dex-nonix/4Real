import BaseWidgetManager from './BaseWidgetManager.js'
import {PAGES} from '@nonix/registries/pages.js'

class PageManager extends BaseWidgetManager {
    constructor() {
        super(PAGES)
    }

    getDefaultWidget() {
        return {component: {header: {title: 'Page'}, widgets: []}, props: {}}
    }
}

export default new PageManager()


