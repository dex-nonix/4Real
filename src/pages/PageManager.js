// src/pages/PageManager.js
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'
import { PAGES } from '@/pages/pages.js'

class PageManager extends BaseWidgetManager {
  constructor() {
    super(PAGES)
  }

  getDefaultWidget() {
    return { component: { header: { title: 'Page' }, widgets: [] }, props: {} }
  }
}

export default new PageManager()


