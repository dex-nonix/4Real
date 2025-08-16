<!-- ChatSessionBar.vue -->
<script setup>
import Button from 'primevue/button';
import Divider from 'primevue/divider';
import Avatar from 'primevue/avatar';

defineProps({
  sessions: {
    type: Array,
    required: true,
    default: () => []
  },
  selectedSessionId: {
    type: [String, Number],
    required: true
  }
});

const emit = defineEmits(['sessionSelected', 'addSession']);
</script>

<template>
  <aside class="h-full surface-section flex-shrink-0 surface-border select-none">
    <div class="flex flex-column h-full">
      <div class="flex flex-shrink-0 flex-grow-1">
        <ul class="flex flex-column list-none p-0 m-0 w-full">
          <li v-for="session in sessions" :key="session.id">
            <a
                class="cursor-pointer flex align-items-center justify-content-center border-right-2 border-transparent p-2 hover:border-300 transition-colors transition-duration-150"
                :class="selectedSessionId === session.id
                ? 'border-blue-500 surface-200'
                : ''"
                @click="emit('sessionSelected', session.id)"
            >
              <Avatar :image="session.user.avatarUrl" size="large" shape="circle"/>
            </a>
          </li>
        </ul>
      </div>
      <div class="mt-auto flex-shrink-0">
        <Divider class="mb-1"/>
        <div class="p-2 mx-auto">
          <!-- opens menu with options to add a persona to chat with (new session) -->
          <Button
              icon="pi pi-plus"
              rounded
              severity="secondary"
              @click="emit('addSession')"
          />
        </div>
      </div>
    </div>
  </aside>
</template>
