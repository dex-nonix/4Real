// src/pages/PageManager.js
import BaseWidgetManager from '@/libs/core/widget-manager/BaseWidgetManager.js'
import { PAGES } from '@/libs/core/page/pages.js'

class PageManager extends BaseWidgetManager {
  constructor() {
    super(PAGES)
  }

  getDefaultWidget() {
    return { component: { header: { title: 'Page' }, widgets: [] }, props: {} }
  }
}

export default new PageManager()


