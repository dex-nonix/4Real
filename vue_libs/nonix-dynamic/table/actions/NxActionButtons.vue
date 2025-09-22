<template>
  <div class="action-buttons flex gap-2 justify-content-start">
    <template v-for="action in actions" :key="action">
      <NxConfirmIconButton
        v-if="confirmActiveAction === action"
        :icon="getActionIcon(action)"
        :confirmText="`${action}?`"
        :size="'small'"
        :severity="getActionSeverity(action)"
        :showConfirmInitially="true"
        @confirm="() => emitRowAction(action)"
        @cancel="onCancelConfirm"
      />
      <Button
        v-else-if="!confirmActiveAction"
        :label="getActionLabel(action)"
        :icon="getActionIcon(action)"
        :size="'small'"
        :severity="getActionSeverity(action)"
        @click="onActionClick(action)"
        class="action-btn"
        :class="{ 'mobile': isMobile }"
        :title="getActionTitle(action)"
      />
    </template>
  </div>
</template>

<script>
import Button from 'primevue/button'
import { ref, onMounted, onUnmounted, computed } from 'vue'
import NxConfirmIconButton from '@nonix-common/components/NxConfirmIconButton.vue'

export default {
  name: 'NxActionButtons',
  components: { Button, NxConfirmIconButton },
  
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
    },
    confirmActions: {
      type: Array,
      default: () => ['delete']
    }
  },
  
  setup(props) {
    const isMobile = ref(false)
    const confirmActiveAction = ref(null)

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

    return { isMobile, confirmActiveAction }
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
    usesInlineConfirm(action) {
      return this.confirmActions.includes(action)
    },
    onActionClick(action) {
      if (this.usesInlineConfirm(action)) {
        this.confirmActiveAction = action
        return
      }
      this.$emit('action', action, this.rowData)
    },
    onCancelConfirm() {
      this.confirmActiveAction = null
    },
    emitRowAction(action) {
      this.confirmActiveAction = null
      this.$emit('action', action, this.rowData)
    },
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
