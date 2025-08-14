import BaseWidgetManager from '@nonix/widget-manager/BaseWidgetManager.js'
import { DISPLAY_WIDGETS } from '@nonix/registries/display-widgets.js'

class DisplayWidgetManager extends BaseWidgetManager {
  constructor() {
    super(DISPLAY_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
  }
}

export default DisplayWidgetManager


