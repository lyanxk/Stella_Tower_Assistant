<template>
  <section class="panel screenshot">
    <div class="panel__header">
      <strong>Live Preview</strong>
      <button class="btn subtle" @click="$emit('refresh')">Refresh</button>
    </div>
    <div v-if="imageBase64" class="screenshot__frame">
      <img :src="`data:image/png;base64,${imageBase64}`" alt="Emulator preview" />
    </div>
    <div v-else class="empty-state">Preview unavailable. Start the emulator and capture again.</div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  imageBase64: string | null;
}>();

defineEmits<{
  refresh: [];
}>();
</script>
