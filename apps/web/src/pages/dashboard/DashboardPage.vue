<template>
  <AppShell :status="status">
    <div class="dashboard">
      <StatusCards :status="status" />
      <RunControlPanel
        @start="runAction(apiClient.start)"
        @pause="runAction(apiClient.pause)"
        @resume="runAction(apiClient.resume)"
        @stop="runAction(apiClient.stop)"
      />
      <LogPanel :logs="logs" />
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from "@/app/layouts/AppShell.vue";
import RunControlPanel from "@/features/run-control/RunControlPanel.vue";
import { apiClient } from "@/shared/api/client";
import { useRuntimeEvents } from "@/shared/api/useRuntimeEvents";
import LogPanel from "@/widgets/log-panel/LogPanel.vue";
import StatusCards from "@/widgets/status-cards/StatusCards.vue";

const { status, logs, loadRuntimeSnapshot } = useRuntimeEvents({
  logLimit: 120,
  refreshIntervalMs: 1000,
});

async function runAction(action: () => Promise<unknown>) {
  await action();
  await loadRuntimeSnapshot();
}
</script>
