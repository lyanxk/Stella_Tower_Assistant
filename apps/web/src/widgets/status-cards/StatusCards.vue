<template>
  <section class="status-grid">
    <article class="status-card accent">
      <span>Automation</span>
      <strong>{{ status?.is_running ? "Running" : "Standby" }}</strong>
      <small>{{ status?.last_message ?? "No runtime data" }}</small>
    </article>
    <article class="status-card">
      <span>Progress</span>
      <strong>{{ status ? `${status.current_run}/${status.max_runs || 0}` : "--" }}</strong>
      <small>Current run / configured max runs</small>
    </article>
    <article class="status-card">
      <span>Pause State</span>
      <strong>{{ status?.is_paused ? "Paused" : "Live" }}</strong>
      <small>Skip initial: {{ status?.skip_initial_wait ? "enabled" : "off" }}</small>
    </article>
    <article class="status-card">
      <span>Elevator Floor</span>
      <strong>{{ formatValue(status?.elevator_floor) }}</strong>
      <small>Latest OCR floor reading</small>
    </article>
    <article class="status-card">
      <span>Money</span>
      <strong>{{ formatValue(status?.current_money) }}</strong>
      <small>Latest OCR money reading</small>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { AutomationStatus } from "@/shared/types/api";

defineProps<{
  status: AutomationStatus | null;
}>();

function formatValue(value: number | null | undefined) {
  return value ?? "--";
}
</script>
