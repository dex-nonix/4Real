<template>
  <div class="flex align-items-center gap-2 p-2 ml-2">
    <!-- Normal state -->
    <div v-if="!showConfirm" class="flex align-items-center gap-2 cursor-pointer" @click.stop="showConfirm = true">
      <i :class="item.icon"></i>
      <span>{{ item.label }}</span>
    </div>

    <!-- Confirmation state -->
    <div v-else class="flex align-items-center gap-2">
      <span class="text-sm text-red-500 mr-2">{{ item.label }}?</span>
      <Button
          icon="pi pi-check"
          severity="danger"
          text
          rounded
          @click.stop="confirm"
          class="tiny-button"
      />
      <Button
          icon="pi pi-times"
          severity="secondary"
          text
          rounded
          @click.stop="cancel"
          class="tiny-button"
      />
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button';
import {ref} from 'vue';

const props = defineProps({
  item: {type: Object, required: true}
});

const emit = defineEmits(['close-menu']);

const showConfirm = ref(false);

const confirm = () => {
  props.item.command();
  showConfirm.value = false;
  emit('close-menu');
};

const cancel = () => {
  showConfirm.value = false;
};
</script>

<style scoped>
.tiny-button {
  width: 24px !important;
  height: 24px !important;
  min-width: 24px !important;
  padding: 0 !important;
}
</style>
