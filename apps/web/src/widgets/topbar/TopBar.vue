<template>
  <header class="topbar">
    <div>
      <div class="topbar__title">Automation Control Surface</div>
      <div class="topbar__subtitle">{{ subtitle }}</div>
    </div>
    <div class="topbar__pill" :data-running="Boolean(status?.is_running)">
      {{ status?.is_running ? "Running" : "Idle" }}
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { AutomationStatus } from "@/shared/types/api";

const props = defineProps<{
  status: AutomationStatus | null;
}>();

const subtitle = computed(() => props.status?.last_message ?? "Waiting for backend");
</script>
