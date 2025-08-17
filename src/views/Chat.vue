<template>
  <Page title="Chat" :back="false" :actions="[]" :showRightToggle="true">
    <section class="p-3">
      <ChatView />
    </section>
  </Page>
</template>

<script setup>
import Page from '@nonix/page/Page.vue'
import { ChatView } from '@nonix-chat'
</script>


