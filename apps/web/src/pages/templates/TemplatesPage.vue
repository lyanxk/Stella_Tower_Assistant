<template>
  <AppShell :status="null" :logs="[]">
    <section class="panel">
      <div class="panel__header">
        <strong>Template Inventory</strong>
        <span>{{ templates.length }} files</span>
      </div>
      <div class="template-list">
        <article v-for="item in templates" :key="item.key" class="template-row">
          <div>
            <strong>{{ item.key }}</strong>
            <small>{{ item.filename }}</small>
          </div>
          <span :data-exists="item.exists" class="template-badge">
            {{ item.exists ? "ready" : "missing" }}
          </span>
        </article>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppShell from "@/app/layouts/AppShell.vue";
import { apiClient } from "@/shared/api/client";
import type { TemplateInfo } from "@/shared/types/api";

const templates = ref<TemplateInfo[]>([]);

onMounted(async () => {
  templates.value = await apiClient.getTemplates();
});
</script>
