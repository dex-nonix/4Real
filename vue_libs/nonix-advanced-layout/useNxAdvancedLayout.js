import { reactive, computed } from 'vue'

const layoutState = reactive({
  // Header state
  header: {
    title: 'Advanced Layout',
    subtitle: null,
    showTitle: true,
    back: false,
    actions: [],
    breadcrumbs: [],
    onBack: null
  },

  // Layout state
  leftCollapsed: false,
  rightOpen: false,
  rightPinned: false,
  sidebarWidth: 450,
  isMobile: false,

  // UI state
  loading: false,
  notifications: []
})

// Update mobile state
const updateMobileState = () => {
  if (typeof window !== 'undefined') {
    layoutState.isMobile = window.innerWidth < 768
  }
}

// Computed properties
const isDesktop = computed(() => !layoutState.isMobile)
const hasNotifications = computed(() => layoutState.notifications.length > 0)

// Initialize
updateMobileState()
if (typeof window !== 'undefined') {
  window.addEventListener('resize', updateMobileState)
}

const useNxAdvancedLayout = () => {
  return {
    // State access
    state: layoutState,
    isDesktop,
    hasNotifications,

    // Header methods - simplified for NxAdvancedTopBar
    setTitle: (title) => {
      layoutState.header.title = title
    },

    addAction: (action) => {
      layoutState.header.actions.push(action)
    },

    removeAction: (actionId) => {
      const index = layoutState.header.actions.findIndex(a => a.id === actionId)
      if (index > -1) {
        layoutState.header.actions.splice(index, 1)
      }
    },

    clearActions: () => {
      layoutState.header.actions = []
    },

    getActions: () => {
      return layoutState.header.actions
    },

    // Layout methods
    toggleLeft: () => {
      layoutState.leftCollapsed = !layoutState.leftCollapsed
    },

    toggleRight: () => {
      layoutState.rightOpen = !layoutState.rightOpen
    },

    // Computed getters for template
    title: computed(() => layoutState.header.title),
    actions: computed(() => layoutState.header.actions),

    // UI methods
    setLoading: (loading) => {
      layoutState.loading = loading
    },

    addNotification: (notification) => {
      layoutState.notifications.push(notification)
    },

    clearNotifications: () => {
      layoutState.notifications = []
    }
  }
}

export { useNxAdvancedLayout }
