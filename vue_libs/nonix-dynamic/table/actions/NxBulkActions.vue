<template>
  <div class="bulk-actions flex justify-content-between align-items-center">
    <span class="selected-count">{{ selectedCount }} items selected</span>
    <div class="action-buttons">
      <Button
          v-for="action in actions"
          :key="action"
          :label="isMobile ? undefined : action"
          :icon="getActionIcon(action)"
          :size="'small'"
          :severity="getActionSeverity(action)"
          @click="handleAction(action)"
          class="bulk-btn"
          :class="{ 'mobile': isMobile }"
          :title="isMobile ? action : undefined"
      />
    </div>
  </div>
</template>

<script>
import Button from 'primevue/button'
import {onMounted, onUnmounted, ref} from 'vue'

export default {
  name: 'NxBulkActions',
  components: {Button},

  props: {
    actions: {
      type: Array,
      default: () => ['delete', 'export']
    },
    selectedCount: {
      type: Number,
      required: true
    }
  },

  setup() {
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

    return {isMobile}
  },

  methods: {
    handleAction(action) {
      this.$emit('action', action)
    },

    getActionIcon(action) {
      const iconMap = {
        'delete': 'pi pi-trash',
        'export': 'pi pi-download',
        'import': 'pi pi-upload',
        'archive': 'pi pi-archive',
        'restore': 'pi pi-refresh',
        'move': 'pi pi-arrows-alt',
        'copy': 'pi pi-copy',
        'duplicate': 'pi pi-clone',
        'merge': 'pi pi-objects-column',
        'split': 'pi pi-objects-row'
      }
      return iconMap[action] || 'pi pi-circle'
    },

    getActionSeverity(action) {
      const severityMap = {
        'delete': 'danger',
        'archive': 'warning',
        'export': 'info',
        'import': 'info',
        'restore': 'success',
        'move': 'secondary',
        'copy': 'secondary',
        'duplicate': 'secondary',
        'merge': 'info',
        'split': 'info'
      }
      return severityMap[action] || 'secondary'
    }
  }
}
</script>

<style scoped>
/* Using PrimeFlex for layout and spacing. */
</style>
