<template>
  <section class="panel">
    <div class="panel__header">
      <strong>日志</strong>
      <span>{{ logs.length }} 条</span>
    </div>
    <div ref="logList" class="log-list">
      <article v-for="entry in orderedLogs" :key="entry.id" class="log-item">
        <div class="log-item__meta">
          <span>{{ formatScope(entry.scope) }}</span>
          <span>{{ formatLevel(entry.level) }}</span>
          <span>{{ formatTime(entry.timestamp) }}</span>
        </div>
        <p>{{ entry.message }}</p>
      </article>
      <div v-if="!logs.length" class="empty-state">暂无日志</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import type { AutomationLogEntry } from "@/shared/types/api";

const props = defineProps<{
  logs: AutomationLogEntry[];
}>();

const logList = ref<HTMLElement | null>(null);
const orderedLogs = computed(() => props.logs.slice(0, 120).reverse());

watch(
  () => props.logs,
  async () => {
    await nextTick();
    if (logList.value) {
      logList.value.scrollTop = logList.value.scrollHeight;
    }
  },
  { deep: true, immediate: true },
);

function formatScope(scope: string) {
  const scopes: Record<string, string> = {
    automation: "自动化",
    service: "服务",
    vision: "视觉",
    shop: "商店",
    ocr: "识别",
    action: "操作",
  };

  return scopes[scope] ?? scope;
}

function formatLevel(level: string) {
  const levels: Record<string, string> = {
    debug: "调试",
    info: "信息",
    warning: "警告",
    error: "错误",
  };

  return levels[level] ?? level;
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "--:--:--";
  }

  return date.toLocaleTimeString("zh-CN", { hour12: false });
}
</script>
