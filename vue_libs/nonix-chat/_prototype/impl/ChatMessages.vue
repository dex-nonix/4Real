<!-- ChatMessages.vue -->
<!--

 important this file has to be split! as we need  a simple message type registry so we have
 them dynamic also can later add other types like system messages, or the
 tools and such !! has to be basesd on the the registry has to be based on the *BaseWidgetManager* and has to be named  *ChatMessageTypeManager*


 -->
<script setup>
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import Menu from 'primevue/menu';
import { ref } from 'vue';

defineProps({
  messages: {
    type: Array,
    required: true,
    default: () => []
  },
  currentUserId: {
    type: [String, Number],
    required: true
  }
});

const menu = ref();
const selectedMessage = ref(null);
const menuItems = ref([
    { label: 'Copy', icon: 'pi pi-copy', command: () => console.log('Copy:', selectedMessage.value) },
    { label: 'Edit', icon: 'pi pi-pencil', command: () => console.log('Edit:', selectedMessage.value) },
    { separator: true },
    { label: 'Delete', icon: 'pi pi-trash', command: () => console.log('Delete:', selectedMessage.value) }
]);

const toggleMenu = (event, message) => {
    selectedMessage.value = message;
    menu.value.toggle(event);
};
</script>

<template>
  <div class="flex-1 p-4 overflow-y-auto surface-ground">
    <div v-for="message in messages" :key="message.id" class="flex mb-4" :class="message.senderId === currentUserId ? 'justify-content-end' : 'justify-content-start'">
      <div class="flex flex-column" style="max-width: 80%;">
        <div
            class="p-3 text-color-secondary border-round-xl"
            :class="{
                'surface-card shadow-1': message.senderId === currentUserId,
                'surface-200': message.senderId !== currentUserId
            }"
        >
          <div class="flex align-items-start">
            <p class="m-0 text-normal" style="hyphens: auto; word-break: break-word;">{{ message.text }}</p>
            <Button
              icon="pi pi-ellipsis-v"
              text rounded severity="secondary"
              class="p-button-sm ml-2 flex-shrink-0"
              @click="toggleMenu($event, message)"
            />
          </div>
        </div>

        <div
          class="flex align-items-center mt-1 px-2"
          :class="{
            'justify-content-end': message.senderId === currentUserId,
            'justify-content-start': message.senderId !== currentUserId
          }"
        >
           <span class="text-xs text-color-secondary">{{ message.timestamp }}</span>
           <i v-if="message.senderId === currentUserId && message.status === 'sent'" class="pi pi-check ml-1 text-color-secondary text-sm"></i>
           <i v-if="message.senderId === currentUserId && message.status === 'delivered'" class="pi pi-check-circle ml-1 text-color-secondary text-sm"></i>
           <ProgressSpinner
              v-if="message.senderId === currentUserId && message.status === 'pending'"
              style="width: 14px; height: 14px"
              strokeWidth="8"
              class="ml-1"
            />
        </div>
      </div>
    </div>
    <Menu ref="menu" :model="menuItems" :popup="true" />
  </div>
</template>