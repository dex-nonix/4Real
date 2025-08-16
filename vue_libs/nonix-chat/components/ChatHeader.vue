<!-- ChatHeader.vue -->
<script setup>
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';

defineProps({
  user: {
    type: Object,
    required: true,
    default: () => ({ name: 'John Doe', avatarUrl: '' })
  }
});

const emit = defineEmits(['viewHistory', 'closeChat']);
</script>

<template>
  <header class="flex justify-content-between align-items-center surface-section border-bottom-1 surface-border flex-shrink-0" style="height: 60px;">
    <div class="flex align-items-center gap-3 ">
      <Avatar class="m-2" :image="user.avatarUrl" size="large" shape="circle" />
      <div class="flex flex-column">
        <span class="font-bold text-900">{{ user.name }}</span>
        <span class="text-sm text-500">Chat-Name( Date if hisotry if unnamed) has to be editable on inlick(inline)</span>
      </div>
    </div>

    <div class="flex align-items-center gap-1">
      <!-- opens a popdown(not dialog)  with the list odf  histry, also to  telete there and rename the history, so  here are all the chans in the current session, wit hall its messages per chat, the header has to show the history name if changed as history(chats has to have name too keep ) -->
       <Button icon="pi pi-history" text rounded severity="secondary" @click="emit('viewHistory')" v-tooltip.bottom="'View History'" />
      <!-- optional as its for use when  in a sidepane  so its optionaly shown, but normally ideen -->
       <Button icon="pi pi-times" text rounded severity="secondary" @click="emit('closeChat')" v-tooltip.bottom="'Close Chat'"/>
    </div>
  </header>
</template>