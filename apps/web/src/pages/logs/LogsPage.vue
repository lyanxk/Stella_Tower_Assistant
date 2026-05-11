<template>
  <AppShell :status="status" :logs="logs">
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
import AppShell from "@/app/layouts/AppShell.vue";
import { useRuntimeEvents } from "@/shared/api/useRuntimeEvents";

const { status, logs } = useRuntimeEvents({ logLimit: 300 });
</script>
