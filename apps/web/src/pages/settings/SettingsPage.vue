<template>
  <AppShell :status="status" :logs="logs">
    <section class="panel">
      <div class="panel__header">
        <strong>Settings Snapshot</strong>
        <span>Served by backend</span>
      </div>
      <pre class="code-block">{{ pretty }}</pre>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AppShell from "@/app/layouts/AppShell.vue";
import { apiClient } from "@/shared/api/client";
import { useRuntimeEvents } from "@/shared/api/useRuntimeEvents";
import type { SettingsResponse } from "@/shared/types/api";

const settings = ref<SettingsResponse | null>(null);
const pretty = computed(() => JSON.stringify(settings.value, null, 2));
const { status, logs } = useRuntimeEvents();

onMounted(async () => {
  settings.value = await apiClient.getSettings();
});
</script>
