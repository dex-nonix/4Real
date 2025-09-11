<template>
  <div class="action-buttons flex gap-2 justify-content-start">
    <Button 
      v-for="action in actions" 
      :key="action"
      :label="getActionLabel(action)"
      :icon="getActionIcon(action)"
      :size="'small'"
      :severity="getActionSeverity(action)"
      @click="handleAction(action)"
      class="action-btn"
      :class="{ 'mobile': isMobile }"
      :title="getActionTitle(action)"
    />
  </div>
</template>

<script>
import Button from 'primevue/button'
import { ref, onMounted, onUnmounted, computed } from 'vue'

export default {
  name: 'NxActionButtons',
  components: { Button },
  
  props: {
    actions: {
      type: Array,
      default: () => ['view', 'edit', 'delete']
    },
    rowData: {
      type: Object,
      required: true
    },
    actionsDisplay: {
      type: String,
      default: 'responsive', // 'responsive', 'icons-only', 'text-only', 'both'
      validator: value => ['responsive', 'icons-only', 'text-only', 'both'].includes(value)
    }
  },
  
  setup(props) {
    const isMobile = ref(false)
    
    const checkMobile = () => {
      isMobile.value = window.innerWidth < 768 // md breakpoint
    }
    
    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })
    
    return { isMobile }
  },
  
  computed: {
    displayMode() {
      if (this.actionsDisplay === 'responsive') {
        return this.isMobile ? 'icons-only' : 'both'
      }
      return this.actionsDisplay
    }
  },
  
  methods: {
    handleAction(action) {
      this.$emit('action', action, this.rowData)
    },
    
    getActionLabel(action) {
      if (this.displayMode === 'icons-only') return undefined
      if (this.displayMode === 'text-only') return action
      if (this.displayMode === 'both') return action
      return action // fallback
    },
    
    getActionIcon(action) {
      if (this.displayMode === 'text-only') return undefined
      
      const iconMap = {
        'view': 'pi pi-eye',
        'edit': 'pi pi-pencil',
        'delete': 'pi pi-trash',
        'add': 'pi pi-plus',
        'save': 'pi pi-check',
        'cancel': 'pi pi-times',
        'export': 'pi pi-download',
        'import': 'pi pi-upload',
        'refresh': 'pi pi-refresh',
        'search': 'pi pi-search',
        'filter': 'pi pi-filter',
        'sort': 'pi pi-sort',
        'print': 'pi pi-print',
        'share': 'pi pi-share-alt',
        'settings': 'pi pi-cog',
        'help': 'pi pi-question-circle',
        'info': 'pi pi-info-circle',
        'warning': 'pi pi-exclamation-triangle',
        'error': 'pi pi-times-circle',
        'success': 'pi pi-check-circle'
      }
      return iconMap[action] || 'pi pi-circle'
    },
    
    getActionTitle(action) {
      if (this.displayMode === 'icons-only') return action
      return undefined
    },
    
    getActionSeverity(action) {
      const severityMap = {
        'delete': 'danger',
        'cancel': 'secondary',
        'view': 'info',
        'edit': 'warning',
        'add': 'success',
        'save': 'success',
        'export': 'info',
        'import': 'info'
      }
      return severityMap[action] || 'secondary'
    }
  }
}
</script>

<style scoped>
/* Using PrimeFlex for layout and spacing. */
</style>
