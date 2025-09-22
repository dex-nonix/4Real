<template>
  <div class="flex align-items-center gap-2 p-2 ml-2">
    <div v-if="!showConfirm" class="flex align-items-center gap-2 cursor-pointer" @click.stop="showConfirm = true">
      <i :class="item.icon"></i>
      <span>{{ item.label }}</span>
    </div>
    <div v-else class="flex align-items-center gap-2">
      <NxConfirmIconButton
        :icon="'pi pi-trash'"
        :confirmText="`${item.label}?`"
        :size="'small'"
        :severity="'danger'"
        :showConfirmInitially="true"
        @confirm="handleConfirm"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NxConfirmIconButton from '@nonix-common/components/NxConfirmIconButton.vue';

const props = defineProps({
  item: {type: Object, required: true}
});

const emit = defineEmits(['close-menu']);

const showConfirm = ref(false);

const handleConfirm = () => {
  if (props.item && typeof props.item.command === 'function') {
    props.item.command();
  }
  showConfirm.value = false;
  emit('close-menu');
};

const handleCancel = () => {
  showConfirm.value = false;
};
</script>
