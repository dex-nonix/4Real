// src/widgets/DynamicWidgetManager.js
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'
import { DYNAMIC_WIDGETS } from '@/widgets/dynamic-widgets.js'

class DynamicWidgetManager extends BaseWidgetManager {
  constructor() {
    super(DYNAMIC_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'div', props: { class: 'text-sm', innerHTML: 'Unknown widget' } }
  }
}

export default DynamicWidgetManager


