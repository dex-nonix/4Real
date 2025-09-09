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

const useAdvancedLayout = () => {
  return {
    // State access
    state: layoutState,
    isDesktop,
    hasNotifications,

    // Header methods
    setHeader: (config) => {
      if (config.title !== undefined) layoutState.header.title = config.title
      if (config.subtitle !== undefined) layoutState.header.subtitle = config.subtitle
      if (config.showTitle !== undefined) layoutState.header.showTitle = config.showTitle
      if (config.back !== undefined) layoutState.header.back = config.back
      if (config.actions !== undefined) layoutState.header.actions = config.actions
      if (config.breadcrumbs !== undefined) layoutState.header.breadcrumbs = config.breadcrumbs
      if (config.onBack !== undefined) layoutState.header.onBack = config.onBack
    },

    setTitle: (title) => {
      layoutState.header.title = title
    },

    setSubtitle: (subtitle) => {
      layoutState.header.subtitle = subtitle
    },

    addAction: (action) => {
      layoutState.header.actions.push(action)
    },

    clearActions: () => {
      layoutState.header.actions = []
    },

    resetHeader: () => {
      layoutState.header.title = 'Advanced Layout'
      layoutState.header.subtitle = null
      layoutState.header.showTitle = true
      layoutState.header.back = false
      layoutState.header.actions = []
      layoutState.header.breadcrumbs = []
      layoutState.header.onBack = null
    },

    // Layout methods
    toggleLeft: () => {
      layoutState.leftCollapsed = !layoutState.leftCollapsed
    },

    toggleRight: () => {
      layoutState.rightOpen = !layoutState.rightOpen
    },

    toggleRightPin: () => {
      layoutState.rightPinned = !layoutState.rightPinned
    },

    openLeft: () => {
      layoutState.leftCollapsed = false
    },

    closeLeft: () => {
      layoutState.leftCollapsed = true
    },

    openRight: () => {
      layoutState.rightOpen = true
    },

    closeRight: () => {
      layoutState.rightOpen = false
    },

    setSidebarWidth: (width) => {
      layoutState.sidebarWidth = Math.max(300, Math.min(1200, width))
    },

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

export { useAdvancedLayout }
