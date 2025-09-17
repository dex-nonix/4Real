<template>
  <div class="flex flex-column surface-card border-round-lg" :style="{ height: treeHeight }">
    <div class="flex justify-content-between align-items-center p-2 border-bottom-1 surface-border bg-surface-section border-round-top-lg">
      <span class="text-lg font-medium">Categories</span>
      <Button
        v-if="allowCreateCategory"
        icon="pi pi-plus"
        size="small"
        text
        rounded
        @click="showCreateDialog = true"
        v-tooltip.top="'Create Category'"
        class="ml-2"
      />
    </div>

    <!-- Flat Categories View (initial implementation) -->
    <div v-if="!hierarchical" class="flex flex-column gap-1 p-2 overflow-y-auto">
      <div
        v-for="category in categories"
        :key="category.id"
        :class="['flex align-items-center p-2 cursor-pointer border-radius-lg transition-all transition-duration-200 hover:surface-hover', { 'bg-primary-50 border-primary-200 border-1 text-primary-700 shadow-2': selectedCategories.includes(category.id) }]"
        @click="toggleCategory(category.id)"
      >
        <i :class="getCategoryIcon(category)" class="text-primary-500 mr-3"></i>
        <span class="flex-1 text-sm font-medium">{{ category.name }}</span>
        <Badge v-if="showCounts" :value="category.file_count || 0" severity="info" class="ml-auto text-xs" />
      </div>
    </div>

    <!-- Hierarchical Tree View (future implementation) -->
    <Tree
      v-else
      :value="treeData"
      :selectionMode="selectionMode"
      v-model:selectionKeys="selectedKeys"
      @selection-change="handleTreeSelectionChange"
    >
      <template #default="slotProps">
        <span class="tree-node">
          <i :class="getCategoryIcon(slotProps.node)" class="mr-2"></i>
          {{ slotProps.node.label }}
          <small v-if="showCounts" class="ml-auto text-muted">
            {{ slotProps.node.fileCount || 0 }}
          </small>
        </span>
      </template>
    </Tree>

    <!-- Create Category Dialog -->
    <Dialog
      v-model:visible="showCreateDialog"
      modal
      header="Create Category"
      :style="{ width: '400px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="categoryName">Category Name</label>
          <InputText
            id="categoryName"
            v-model="newCategoryName"
            @keyup.enter="createCategory"
          />
        </div>
      </div>
      <template #footer>
        <Button
          label="Cancel"
          icon="pi pi-times"
          class="p-button-text"
          @click="showCreateDialog = false"
        />
        <Button
          label="Create"
          icon="pi pi-check"
          :loading="creating"
          @click="createCategory"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject, defineProps, defineEmits } from 'vue'
import Tree from 'primevue/tree'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Badge from 'primevue/badge'

// Props
const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  selectedCategories: {
    type: Array,
    default: () => []
  },
  selectionMode: {
    type: String,
    default: 'single',
    validator: value => ['single', 'multiple'].includes(value)
  },
  hierarchical: {
    type: Boolean,
    default: false // Start with flat categories, set to true when parent_id is implemented
  },
  showCounts: {
    type: Boolean,
    default: true // Show file count per category
  },
  treeData: {
    type: Array,
    default: () => [] // For hierarchical tree structure (future use)
  },
  allowCreateCategory: {
    type: Boolean,
    default: true
  },
  treeHeight: { type: String, default: '100%' }
})

// Emits
const emit = defineEmits(['category-select', 'category-unselect', 'selection-change', 'category-created', 'update:selectedCategories', 'category-count-updated'])

// Services
const fileManagerService = inject('file-manager')

// Reactive state
const selectedKeys = ref({})
const showCreateDialog = ref(false)
const newCategoryName = ref('')
const creating = ref(false)

// Methods
const toggleCategory = (categoryId) => {
  if (props.selectionMode === 'single') {
    // For single selection, just select this category (replace current selection)
    if (props.selectedCategories[0] !== categoryId) {
      const oldCategory = props.selectedCategories[0]
      if (oldCategory) {
        emit('category-unselect', oldCategory)
      }
      emit('category-select', categoryId)
      emit('update:selectedCategories', [categoryId])
    }
  } else {
    // For multiple selection, toggle the category
    const isSelected = props.selectedCategories.includes(categoryId)
    let newSelectedCategories

    if (isSelected) {
      // Remove category
      newSelectedCategories = props.selectedCategories.filter(id => id !== categoryId)
      emit('category-unselect', categoryId)
    } else {
      // Add category
      newSelectedCategories = [...props.selectedCategories, categoryId]
      emit('category-select', categoryId)
    }

    // Emit v-model update
    emit('update:selectedCategories', newSelectedCategories)
  }
}

const handleTreeSelectionChange = (event) => {
  // event contains the new selectionKeys object from PrimeVue Tree
  selectedKeys.value = event

  // Convert selectedKeys back to selectedCategories array
  const newSelectedCategories = Object.keys(selectedKeys.value).filter(key => selectedKeys.value[key])

  // For single selection, ensure only one category is selected
  if (props.selectionMode === 'single' && newSelectedCategories.length > 1) {
    // Keep only the last selected category
    const lastSelected = newSelectedCategories[newSelectedCategories.length - 1]
    selectedKeys.value = { [lastSelected]: true }
    newSelectedCategories.splice(0, newSelectedCategories.length - 1)
  }

  emit('update:selectedCategories', newSelectedCategories)
}

const getCategoryIcon = (category) => {
  // Simple icon logic - can be enhanced
  return 'pi pi-folder'
}





const createCategory = async () => {
  if (!newCategoryName.value.trim()) return

  creating.value = true
  try {
    const result = await fileManagerService.createCategory(newCategoryName.value.trim())
    if (result.success) {
      emit('category-created', result.data)
      showCreateDialog.value = false
      newCategoryName.value = ''
    }
  } catch (error) {
    console.error('Create category error:', error)
  } finally {
    creating.value = false
  }
}

// Watchers

watch(() => props.selectedCategories, (newVal) => {
  if (!props.hierarchical) return
  // Convert array to tree selection keys for hierarchical mode
  selectedKeys.value = {}
  newVal.forEach(id => {
    selectedKeys.value[id] = true
  })
}, { immediate: true })


</script>

<style scoped>
.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
}

.tree-node i {
  font-size: 1rem;
  color: var(--primary-500);
}

.tree-node span {
  flex: 1;
  font-size: 0.875rem;
}

.tree-node small {
  font-size: 0.75rem;
  opacity: 0.7;
}
</style>
