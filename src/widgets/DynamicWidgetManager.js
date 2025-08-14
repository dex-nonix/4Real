// src/widgets/DynamicWidgetManager.js
import { DYNAMIC_WIDGETS } from '@/widgets/dynamic-widgets.js'

export default class DynamicWidgetManager {
  constructor(widgetMap = DYNAMIC_WIDGETS) {
    this.widgets = widgetMap || {}
  }

  get(type, userProps = {}) {
    const entry = this.widgets[type]
    if (!entry) {
      return { component: 'div', props: { class: 'text-sm', innerHTML: `Unknown widget: ${String(type)}` } }
    }
    const baseProps = entry.defaultProps || {}
    return { component: entry.component, props: { ...baseProps, ...userProps } }
  }
}


