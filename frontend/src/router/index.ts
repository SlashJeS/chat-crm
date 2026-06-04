import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";
import ChatterWorkspaceView from "@/views/ChatterWorkspaceView.vue";
import LoginView from "@/views/LoginView.vue";
import TeamleadMonitorView from "@/views/TeamleadMonitorView.vue";

function roleHomePath(role: UserRole | null): string {
  if (role === "TEAMLEAD") {
    return "/teamlead";
  }
  if (role === "CHATTER") {
    return "/chatter";
  }
  return "/login";
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: "/chatter",
      name: "chatter",
      component: ChatterWorkspaceView,
      meta: { requiresAuth: true, roles: ["CHATTER"] as UserRole[] },
    },
    {
      path: "/teamlead",
      name: "teamlead",
      component: TeamleadMonitorView,
      meta: { requiresAuth: true, roles: ["TEAMLEAD"] as UserRole[] },
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.guest && auth.isAuthenticated) {
    return roleHomePath(auth.role);
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return "/login";
  }

  const allowedRoles = to.meta.roles as UserRole[] | undefined;
  if (allowedRoles && auth.role && !allowedRoles.includes(auth.role)) {
    return roleHomePath(auth.role);
  }

  return true;
});

export default router;
