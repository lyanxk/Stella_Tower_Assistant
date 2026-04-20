<template>
  <AppShell :status="null" :logs="logs">
    <section class="panel">
      <div class="panel__header">
        <strong>Full Logs</strong>
        <span>{{ logs.length }} entries</span>
      </div>
      <div class="log-list expanded">
        <article v-for="entry in logs" :key="entry.id" class="log-item">
          <div class="log-item__meta">
            <span>{{ entry.timestamp }}</span>
            <span>{{ entry.scope }}</span>
            <span>{{ entry.level }}</span>
          </div>
          <p>{{ entry.message }}</p>
        </article>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppShell from "@/app/layouts/AppShell.vue";
import { apiClient } from "@/shared/api/client";
import type { AutomationLogEntry } from "@/shared/types/api";

const logs = ref<AutomationLogEntry[]>([]);

onMounted(async () => {
  logs.value = await apiClient.getLogs();
});
</script>
