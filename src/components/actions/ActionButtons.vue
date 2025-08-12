<template>
  <div class="action-buttons">
    <Button 
      v-for="action in actions" 
      :key="action"
      :label="action"
      :size="'small'"
      :severity="'secondary'"
      @click="handleAction(action)"
      class="action-btn"
    />
  </div>
</template>

<script>
import Button from 'primevue/button'

export default {
  name: 'ActionButtons',
  components: { Button },
  
  props: {
    actions: {
      type: Array,
      default: () => ['view', 'edit', 'delete']
    },
    rowData: {
      type: Object,
      required: true
    }
  },
  
  methods: {
    handleAction(action) {
      this.$emit('action', action, this.rowData)
    }
  }
}
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  min-width: 60px;
}
</style>
