<template>
  <section class="panel">
    <div class="panel__header">
      <strong>Runtime Settings</strong>
      <span>Read-only snapshot</span>
    </div>
    <div class="kv-grid">
      <div class="kv-row">
        <span>Resource Dir</span>
        <strong>{{ settings?.resource_dir ?? "--" }}</strong>
      </div>
      <div class="kv-row">
        <span>Emulator Keywords</span>
        <strong>{{ settings?.emulator_keywords.join(", ") ?? "--" }}</strong>
      </div>
      <div class="kv-row">
        <span>Thresholds</span>
        <strong>{{ settings ? Object.keys(settings.thresholds).length : 0 }} entries</strong>
      </div>
      <div class="kv-row">
        <span>Limits</span>
        <strong>{{ settings ? Object.keys(settings.limits).length : 0 }} entries</strong>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { SettingsResponse } from "@/shared/types/api";

defineProps<{
  settings: SettingsResponse | null;
}>();
</script>
