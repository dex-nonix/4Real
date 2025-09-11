<template>
  <div class="the-top-bar" :class="{ collapsed: collapsed }">
    <!-- Left Section - Navigation (optional) -->
    <div class="flex align-items-center gap-3">
      <Button
        v-if="showNavToggle"
        icon="pi pi-bars"
        severity="secondary"
        text
        rounded
        @click="$emit('toggle-nav')"
        class="p-2"
        v-tooltip.bottom="'Toggle Navigation'"
      />

      <div class="flex align-items-center gap-2">
        <span v-if="title" class="page-title font-semibold text-lg">{{ title }}</span>
      </div>
    </div>

    <!-- Center Section -->
    <div class="flex-1"></div>

    <!-- Right Section - Optional Actions + Permanent Chat -->
    <div class="flex align-items-center gap-2">
      <!-- Optional Actions (side by side, collapse to ellipsis on mobile) -->
      <div v-if="actions && actions.length" class="flex align-items-center gap-1">
        <!-- Desktop: Show all actions side by side -->
        <div class="hidden md:flex gap-1">
          <Button
            v-for="action in visibleActions"
            :key="action.id || action.label"
            :icon="action.icon"
            :severity="action.severity || 'secondary'"
            text
            rounded
            @click="action.command"
            class="p-2"
            :v-tooltip.bottom="action.tooltip"
          />
          <Button
            v-if="hasHiddenActions"
            icon="pi pi-ellipsis-h"
            severity="secondary"
            text
            rounded
            @click="showMenu = !showMenu"
            class="p-2"
            v-tooltip.bottom="'More Options'"
          />
        </div>

        <!-- Mobile: Always show ellipsis for all actions -->
        <Button
          v-if="isMobile"
          icon="pi pi-ellipsis-h"
          severity="secondary"
          text
          rounded
          @click="showMenu = !showMenu"
          class="p-2 md:hidden"
          v-tooltip.bottom="'Menu'"
        />
      </div>

      <!-- Permanent Chat Toggle (always visible) -->
      <Button
        icon="pi pi-comments"
        severity="info"
        text
        rounded
        @click.stop="$emit('toggle-chat')"
        class="p-2"
        v-tooltip.bottom="'Toggle Chat'"
      />
    </div>

    <!-- Mobile Menu Overlay -->
    <div v-if="showMenu && isMobile" class="mobile-menu-overlay" @click="showMenu = false">
      <div class="mobile-menu-content" @click.stop>
        <div class="flex flex-column gap-2 p-3">
          <h6 class="mt-0 mb-2">Menu</h6>
          <Button
            v-for="action in actions"
            :key="action.id || action.label"
            :icon="action.icon"
            :label="action.label"
            :severity="action.severity || 'secondary'"
            text
            @click="handleAction(action)"
            class="w-full justify-start"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Button from 'primevue/button'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: null
  },
  showNavToggle: {
    type: Boolean,
    default: true
  },
  actions: {
    type: Array,
    default: () => []
  },
  maxVisibleActions: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['toggle-nav', 'toggle-chat'])

// Mobile detection
const isMobile = ref(false)
const updateMobileState = () => {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth < 768
  }
}
updateMobileState()
if (typeof window !== 'undefined') {
  window.addEventListener('resize', updateMobileState)
}

// Menu state
const showMenu = ref(false)

// Computed properties
const visibleActions = computed(() => {
  if (isMobile.value) return []
  return props.actions.slice(0, props.maxVisibleActions)
})

const hasHiddenActions = computed(() => {
  return !isMobile.value && props.actions.length > props.maxVisibleActions
})

// Handle action click
const handleAction = (action) => {
  if (action.command) {
    action.command()
  }
  showMenu.value = false
}
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

/* Mobile menu overlay */
.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 4rem 1rem 1rem;
}

.mobile-menu-content {
  background: var(--surface-card, #ffffff);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  max-width: 300px;
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
