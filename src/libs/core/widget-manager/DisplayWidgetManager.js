import BaseWidgetManager from '@/libs/core/widget-manager/BaseWidgetManager.js'
import { DISPLAY_WIDGETS } from '@/libs/core/registries/display-widgets.js'

class DisplayWidgetManager extends BaseWidgetManager {
  constructor() {
    super(DISPLAY_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
  }
}

export default DisplayWidgetManager


