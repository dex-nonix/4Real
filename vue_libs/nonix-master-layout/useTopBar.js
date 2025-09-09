import {reactive} from 'vue'

const headerState = reactive({
    title: undefined,
    back: false,
    actions: undefined, // PrimeVue Menu model
    showRightToggle: false,
    onBack: undefined
})

export const useTopBar = () => ({
    state: headerState,
    setHeader: (next = {}) => {
        headerState.title = next.title
        headerState.back = !!next.back
        headerState.actions = next.actions
        headerState.showRightToggle = !!next.showRightToggle
        headerState.onBack = next.onBack
    },
    resetHeader: () => {
        headerState.title = undefined
        headerState.back = false
        headerState.actions = undefined
        headerState.showRightToggle = false
        headerState.onBack = undefined
    }
});


