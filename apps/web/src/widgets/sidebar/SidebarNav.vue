<template>
  <nav class="sidebar">
    <div class="sidebar__brand">
      <span class="sidebar__eyebrow">Local Console</span>
      <strong>Stella Tower</strong>
    </div>
    <RouterLink v-for="item in items" :key="item.to" :to="item.to" class="sidebar__link">
      <span>{{ item.label }}</span>
      <small>{{ item.meta }}</small>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

const items = [
  { to: "/dashboard", label: "Dashboard", meta: "Run control" },
  { to: "/templates", label: "Templates", meta: "Asset health" },
  { to: "/settings", label: "Settings", meta: "Runtime config" },
  { to: "/logs", label: "Logs", meta: "Event stream" },
];
</script>
