import {markRaw} from 'vue'

class NxBaseWidgetManager {
    constructor(widgetMap = {}) {
        // Mark all components as raw to prevent Vue reactivity
        this.widgets = Object.fromEntries(
            Object.entries(widgetMap).map(([key, widget]) => [
                key,
                {
                    ...widget,
                    component: markRaw(widget.component)
                }
            ])
        )
    }

    getWidget(typeOrComponent, userProps = {}) {
        if (typeof typeOrComponent === 'string') {
            const widget = this.widgets[typeOrComponent]
            if (!widget) return this.getDefaultWidget()

            return {
                component: widget.component,
                props: {...widget.defaultProps, ...userProps}
            }
        }

        const comp = markRaw(typeOrComponent)
        return { component: comp, props: {...userProps} }
    }

    // Register new widget
    registerWidget(type, component, defaultProps = {}) {
        this.widgets[type] = {
            component: markRaw(component),
            defaultProps
        }
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

export default NxBaseWidgetManager
