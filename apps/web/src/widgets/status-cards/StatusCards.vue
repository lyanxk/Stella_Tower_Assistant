<template>
  <section class="status-grid">
    <article class="status-card accent">
      <span>自动化状态</span>
      <strong>{{ status?.is_running ? "运行中" : "待机" }}</strong>
      <small>{{ status?.last_message ?? "暂无运行数据" }}</small>
    </article>
    <article class="status-card">
      <span>运行进度</span>
      <strong>{{ status ? `${status.current_run}/${status.max_runs || 0}` : "--" }}</strong>
      <small>当前轮次 / 最大轮次</small>
    </article>
    <article class="status-card">
      <span>暂停状态</span>
      <strong>{{ status?.is_paused ? "已暂停" : "实时" }}</strong>
      <small>运行暂停 / 继续状态</small>
    </article>
    <article class="status-card">
      <span>当前金币</span>
      <strong>{{ formatValue(status?.current_gold) }}</strong>
      <small>最新 OCR 金币读数</small>
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
