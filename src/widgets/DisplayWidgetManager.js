// src/widgets/DisplayWidgetManager.js
import BaseWidgetManager from '@/widgets/BaseWidgetManager.js'
import { DISPLAY_WIDGETS } from '@/widgets/display-widgets.js'

class DisplayWidgetManager extends BaseWidgetManager {
  constructor() {
    super(DISPLAY_WIDGETS)
  }

  getDefaultWidget() {
    return { component: 'span', props: { class: 'text-sm' } }
  }
}

export default DisplayWidgetManager


