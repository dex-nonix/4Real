// src/pages/PageManager.js
import BaseWidgetManager from '@nonix/widget-manager/BaseWidgetManager.js'
import { PAGES } from '@nonix/page/pages.js'

class PageManager extends BaseWidgetManager {
  constructor() {
    super(PAGES)
  }

  getDefaultWidget() {
    return { component: { header: { title: 'Page' }, widgets: [] }, props: {} }
  }
}

export default new PageManager()


