<template>
  <div class="bulk-actions">
    <span class="selected-count">{{ selectedCount }} items selected</span>
    <div class="action-buttons">
      <Button 
        v-for="action in actions" 
        :key="action"
        :label="action"
        :size="'small'"
        :severity="'danger'"
        @click="handleAction(action)"
        class="bulk-btn"
      />
    </div>
  </div>
</template>

<script>
import Button from 'primevue/button'

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
  
  methods: {
    handleAction(action) {
      this.$emit('action', action)
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
</style>
