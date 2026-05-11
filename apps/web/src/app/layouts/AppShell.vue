<template>
  <div class="shell">
    <div class="shell__body">
      <TopBar :status="status" />
      <main class="shell__content">
        <section class="shell__main">
          <slot />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AutomationStatus } from "@/shared/types/api";
import TopBar from "@/widgets/topbar/TopBar.vue";

defineProps<{
  status: AutomationStatus | null;
}>();
</script>
