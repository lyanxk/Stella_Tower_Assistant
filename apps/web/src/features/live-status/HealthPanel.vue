<template>
  <section class="panel">
    <div class="panel__header">
      <strong>Health</strong>
      <span>API and window state</span>
    </div>
    <div class="kv-grid">
      <div class="kv-row">
        <span>API</span>
        <strong>{{ health ? "Reachable" : "Unknown" }}</strong>
      </div>
      <div class="kv-row">
        <span>Emulator</span>
        <strong>{{ emulatorConnected ? "Detected" : "Missing" }}</strong>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  health: Record<string, unknown> | null;
  emulatorConnected: boolean;
}>();
</script>
