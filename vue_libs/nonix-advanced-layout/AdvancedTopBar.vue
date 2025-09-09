<template>
  <div class="the-top-bar" :class="{ collapsed: collapsed }">
    <!-- Left Section - Navigation -->
    <div class="flex align-items-center gap-3">
      <Button
        icon="pi pi-bars"
        severity="secondary"
        text
        rounded
        @click="$emit('toggle-nav')"
        class="p-2"
        v-tooltip.top="'Toggle Navigation'"
      />

      <div class="flex align-items-center gap-2">
        <span class="page-title font-semibold text-lg">{{ title }}</span>
      </div>
    </div>

    <!-- Center Section - Professional Layout -->
    <div class="flex-1 flex justify-content-center">
      <div class="flex align-items-center gap-2 text-600">
        <i class="pi pi-home text-primary"></i>
        <span class="text-sm">Advanced Layout</span>
      </div>
    </div>

    <!-- Right Section - Actions -->
    <div class="flex align-items-center gap-2">
      <!-- Menu Actions -->
      <Button
        icon="pi pi-list"
        severity="secondary"
        text
        rounded
        class="p-2"
        v-tooltip.top="'Menu'"
      />

      <Button
        icon="pi pi-ellipsis-h"
        severity="secondary"
        text
        rounded
        class="p-2"
        v-tooltip.top="'More Options'"
      />

      <!-- Chat Toggle -->
      <Button
        icon="pi pi-comments"
        severity="info"
        text
        rounded
        @click.stop="$emit('toggle-chat')"
        class="p-2"
        v-tooltip.top="'Toggle Chat'"
      />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Page Name'
  }
})

defineEmits(['toggle-nav', 'toggle-chat'])
</script>

<style scoped>
.the-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: var(--surface-card, #ffffff);
  border-bottom: 1px solid var(--surface-border, #e9ecef);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 56px;
  position: relative;
}

.the-top-bar.collapsed {
  height: 0;
  padding: 0;
  border: 0;
  overflow: hidden;
  box-shadow: none;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #495057);
  margin: 0;
}

/* Professional button styling */
:deep(.p-button) {
  transition: all 0.2s ease;
}

:deep(.p-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

:deep(.p-button:focus) {
  box-shadow: 0 0 0 2px var(--primary-color, #007bff);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .the-top-bar {
    padding: 0.5rem 1rem;
    min-height: 48px;
  }

  .page-title {
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .the-top-bar {
    padding: 0.5rem;
  }

  .page-title {
    font-size: 1rem;
  }
}
</style>
