<template>
  <section class="panel">
    <div class="panel__header">
      <strong>Run Control</strong>
      <span>Backend actions</span>
    </div>
    <div class="button-row">
      <button class="btn primary" @click="$emit('start')">Start</button>
      <button class="btn" @click="$emit('pause')">Pause</button>
      <button class="btn" @click="$emit('resume')">Resume</button>
      <button class="btn danger" @click="$emit('stop')">Stop</button>
      <button class="btn subtle" @click="$emit('skip')">Skip Initial</button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  start: [];
  pause: [];
  resume: [];
  stop: [];
  skip: [];
}>();
</script>
