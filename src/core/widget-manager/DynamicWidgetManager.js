import BaseWidgetManager from '@/core/widget-manager/BaseWidgetManager.js'
import { DYNAMIC_WIDGETS } from '@/core/registries/dynamic-widgets.js'

class DynamicWidgetManager extends BaseWidgetManager {
  constructor() {
    super(DYNAMIC_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'div', props: { class: 'text-sm', innerHTML: 'Unknown widget' } }
  }
}

export default DynamicWidgetManager


