import {h} from 'vue'

export const NX_DYNAMIC_WIDGETS = {
    persona_tools: {component: () => import('@nonix-chat/widgets/NxPersonaLlmToolsViewer.vue'), defaultProps: {}},
    text_block: {
        component: {
            props: {text: {type: String, default: ''}},
            render() {
                return h('div', this.text)
            }
        }, defaultProps: {}
    },
    json_view: {
        component: {
            props: {value: [Object, Array, String, null]},
            render() {
                let text = ''
                try {
                    if (typeof this.value === 'string') text = this.value
                    else if (this.value != null) text = JSON.stringify(this.value, null, 2)
                } catch {
                    text = ''
                }
                return h('pre', {class: 'text-sm font-mono whitespace-pre-wrap'}, text)
            }
        }, defaultProps: {}
    }
}


