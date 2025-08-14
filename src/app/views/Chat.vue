<template>
  <Page title="Chat" :back="false" :actions="[]" :showRightToggle="true">
    <section class="p-3">
      <ChatWidget instance-id="main" />
    </section>
  </Page>
</template>

<script setup>
import Page from '@/app/components/page/Page.vue'
import ChatWidget from '@/libs/chat/ChatWidget.vue'
</script>


