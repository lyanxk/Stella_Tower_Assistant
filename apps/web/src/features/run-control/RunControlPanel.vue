<template>
  <section class="panel">
    <div class="panel__header">
      <strong>运行控制</strong>
      <span>后端动作</span>
    </div>
    <div class="button-row">
      <button class="btn primary" @click="$emit('start')">启动</button>
      <button class="btn" @click="$emit('pause')">暂停</button>
      <button class="btn" @click="$emit('resume')">继续</button>
      <button class="btn danger" @click="$emit('stop')">停止</button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  start: [];
  pause: [];
  resume: [];
  stop: [];
}>();
</script>
