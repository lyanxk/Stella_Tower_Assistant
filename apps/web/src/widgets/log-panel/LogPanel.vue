<template>
  <section class="panel">
    <div class="panel__header">
      <strong>Event Feed</strong>
      <span>{{ logs.length }} items</span>
    </div>
    <div class="log-list">
      <article v-for="entry in logs.slice(0, 24)" :key="entry.id" class="log-item">
        <div class="log-item__meta">
          <span>{{ entry.scope }}</span>
          <span>{{ entry.level }}</span>
        </div>
        <p>{{ entry.message }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { AutomationLogEntry } from "@/shared/types/api";

defineProps<{
  logs: AutomationLogEntry[];
}>();
</script>
