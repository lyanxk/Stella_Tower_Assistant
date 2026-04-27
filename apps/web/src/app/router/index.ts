import { createRouter, createWebHashHistory } from "vue-router";

import DashboardPage from "@/pages/dashboard/DashboardPage.vue";
import TemplatesPage from "@/pages/templates/TemplatesPage.vue";
import SettingsPage from "@/pages/settings/SettingsPage.vue";
import LogsPage from "@/pages/logs/LogsPage.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/dashboard", component: DashboardPage },
    { path: "/templates", component: TemplatesPage },
    { path: "/settings", component: SettingsPage },
    { path: "/logs", component: LogsPage },
  ],
});

export default router;
