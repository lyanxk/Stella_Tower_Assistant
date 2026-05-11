import { createRouter, createWebHashHistory } from "vue-router";

import DashboardPage from "@/pages/dashboard/DashboardPage.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/dashboard", component: DashboardPage },
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
  ],
});

export default router;
