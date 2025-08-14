import { reactive } from 'vue'

// Shared header state written by Page and read by the layout
const headerState = reactive({
  title: undefined,
  back: false,
  actions: undefined, // PrimeVue Menu model
  showRightToggle: false,
  onBack: undefined
})

export function usePageHeader() {
  function setHeader(next = {}) {
    headerState.title = next.title
    headerState.back = !!next.back
    headerState.actions = next.actions
    headerState.showRightToggle = !!next.showRightToggle
    headerState.onBack = next.onBack
  }

  function resetHeader() {
    headerState.title = undefined
    headerState.back = false
    headerState.actions = undefined
    headerState.showRightToggle = false
    headerState.onBack = undefined
  }

  return { state: headerState, setHeader, resetHeader }
}


