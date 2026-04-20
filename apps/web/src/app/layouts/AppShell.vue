<template>
  <div class="shell">
    <aside class="shell__sidebar">
      <SidebarNav />
    </aside>
    <div class="shell__body">
      <TopBar :status="status" />
      <main class="shell__content">
        <section class="shell__main">
          <slot />
        </section>
        <aside class="shell__rail">
          <LogPanel :logs="logs" />
        </aside>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AutomationLogEntry, AutomationStatus } from "@/shared/types/api";
import LogPanel from "@/widgets/log-panel/LogPanel.vue";
import SidebarNav from "@/widgets/sidebar/SidebarNav.vue";
import TopBar from "@/widgets/topbar/TopBar.vue";

defineProps<{
  status: AutomationStatus | null;
  logs: AutomationLogEntry[];
}>();
</script>
