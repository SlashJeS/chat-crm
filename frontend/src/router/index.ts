import { createRouter, createWebHistory } from "vue-router";

import { ACCESS_TOKEN_KEY } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";
import ChatterWorkspaceView from "@/views/ChatterWorkspaceView.vue";
import LoginView from "@/views/LoginView.vue";
import TeamleadMonitorView from "@/views/TeamleadMonitorView.vue";

function roleHomePath(role: UserRole | null): string {
  if (role === "TEAMLEAD" || role === "ADMIN") {
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
      meta: { requiresAuth: true, roles: ["TEAMLEAD", "ADMIN"] as UserRole[] },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (localStorage.getItem(ACCESS_TOKEN_KEY) && !auth.user) {
    await auth.restoreSession();
  }

  if (to.meta.guest && auth.isAuthenticated && auth.user) {
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
