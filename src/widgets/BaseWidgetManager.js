// BaseWidgetManager.js - GENERIC base class!
class BaseWidgetManager {
  constructor(widgetMap = {}) {
    this.widgets = widgetMap
  }

  // Get widget with resolved props
  getWidget(type, userProps = {}) {
    const widget = this.widgets[type]
    if (!widget) return this.getDefaultWidget() // fallback
    
    return {
      component: widget.component,
      props: { ...widget.defaultProps, ...userProps }
    }
  }

  // Register new widget
  registerWidget(type, component, defaultProps = {}) {
    this.widgets[type] = { component, defaultProps }
  }

  // Get available widget types
  getAvailableTypes() {
    return Object.keys(this.widgets)
  }

  // Abstract method - subclasses must implement
  getDefaultWidget() {
    throw new Error('Subclasses must implement getDefaultWidget()')
  }
}

export default BaseWidgetManager
