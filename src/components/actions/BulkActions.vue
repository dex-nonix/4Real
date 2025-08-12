<template>
  <div class="bulk-actions">
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
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'BulkActions',
  components: { Button },
  
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
    
    return { isMobile }
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
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-count {
  font-weight: 500;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.bulk-btn {
  min-width: 80px;
}

.bulk-btn.mobile {
  min-width: 40px;
  width: 40px;
  height: 40px;
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .bulk-actions {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .selected-count {
    text-align: center;
  }
  
  .action-buttons {
    justify-content: center;
    gap: 0.25rem;
  }
  
  .bulk-btn {
    min-width: 36px;
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 575px) {
  .bulk-btn {
    min-width: 32px;
    width: 32px;
    height: 32px;
  }
}
</style>
