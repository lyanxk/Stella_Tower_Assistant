<template>
  <AppShell :status="status" :logs="logs">
    <div class="page-grid">
      <StatusCards :status="status" />
      <RunControlPanel
        @start="runAction(apiClient.start)"
        @pause="runAction(apiClient.pause)"
        @resume="runAction(apiClient.resume)"
        @stop="runAction(apiClient.stop)"
        @skip="runAction(apiClient.skipInitial)"
      />
      <HealthPanel :health="health" :emulator-connected="Boolean(windowInfo?.connected)" />
      <SettingsPanel :settings="settings" />
      <ScreenshotPreview :image-base64="screenshotBase64" @refresh="loadScreenshot" />
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import AppShell from "@/app/layouts/AppShell.vue";
import SettingsPanel from "@/features/config-editor/SettingsPanel.vue";
import HealthPanel from "@/features/live-status/HealthPanel.vue";
import RunControlPanel from "@/features/run-control/RunControlPanel.vue";
import ScreenshotPreview from "@/features/screenshot-preview/ScreenshotPreview.vue";
import { apiClient } from "@/shared/api/client";
import { createEventSocket } from "@/shared/api/events";
import type { AutomationLogEntry, AutomationStatus, SettingsResponse } from "@/shared/types/api";
import StatusCards from "@/widgets/status-cards/StatusCards.vue";

const status = ref<AutomationStatus | null>(null);
const logs = ref<AutomationLogEntry[]>([]);
const settings = ref<SettingsResponse | null>(null);
const screenshotBase64 = ref<string | null>(null);
const health = ref<Record<string, unknown> | null>(null);
const windowInfo = ref<Record<string, unknown> | null>(null);
let socket: WebSocket | null = null;

async function loadBaseData() {
  status.value = await apiClient.getStatus();
  logs.value = await apiClient.getLogs();
  settings.value = await apiClient.getSettings();
  health.value = await apiClient.getHealth();
  windowInfo.value = await apiClient.getWindow();
}

async function loadScreenshot() {
  try {
    const screenshot = await apiClient.getScreenshot();
    screenshotBase64.value = screenshot.image_base64;
  } catch {
    screenshotBase64.value = null;
  }
}

async function runAction(action: () => Promise<unknown>) {
  await action();
  await loadBaseData();
}

onMounted(async () => {
  await loadBaseData();
  await loadScreenshot();
  socket = createEventSocket((message) => {
    if (message.type === "status") {
      status.value = message.data;
    } else if (message.type === "logs") {
      logs.value = message.data;
    } else {
      logs.value = [message.data, ...logs.value].slice(0, 100);
    }
  });
});

onBeforeUnmount(() => {
  socket?.close();
});
</script>
