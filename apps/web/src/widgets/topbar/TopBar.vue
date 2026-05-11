<template>
  <header class="topbar">
    <div>
      <div class="topbar__title">监控面板</div>
      <div class="topbar__subtitle">{{ subtitle }}</div>
    </div>
    <div class="topbar__actions">
      <button class="topbar__exit" :disabled="exiting" @click="exitApplication">
        {{ exiting ? "退出中" : "退出" }}
      </button>
      <div class="topbar__pill" :data-running="Boolean(status?.is_running)">
        {{ status?.is_running ? "运行中" : "待机" }}
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { apiClient } from "@/shared/api/client";
import type { AutomationStatus } from "@/shared/types/api";

const props = defineProps<{
  status: AutomationStatus | null;
}>();

const subtitle = computed(() => props.status?.last_message ?? "等待后端连接");
const exiting = ref(false);

async function exitApplication() {
  if (exiting.value) {
    return;
  }

  exiting.value = true;
  try {
    await apiClient.exit();
  } catch (error) {
    console.warn("[StellaTowerAssistant] Exit request failed", error);
  } finally {
    if (window.stellaTower) {
      await window.stellaTower.closeWindow();
      return;
    }

    window.close();
  }
}
</script>
