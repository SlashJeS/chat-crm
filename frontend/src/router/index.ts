import { createRouter, createWebHistory } from "vue-router";

import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "@/api/http";
import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";
import AdminUsersView from "@/views/AdminUsersView.vue";
import ChatterWorkspaceView from "@/views/ChatterWorkspaceView.vue";
import InviteRegistrationView from "@/views/InviteRegistrationView.vue";
import LeadDialogsView from "@/views/LeadDialogsView.vue";
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

function hasStoredTokens(): boolean {
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY) || localStorage.getItem(REFRESH_TOKEN_KEY));
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
      path: "/invite/:token",
      name: "invite-registration",
      component: InviteRegistrationView,
      meta: { public: true },
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
    {
      path: "/lead/dialogs",
      name: "lead-dialogs",
      component: LeadDialogsView,
      meta: { requiresAuth: true, roles: ["TEAMLEAD", "ADMIN"] as UserRole[] },
    },
    {
      path: "/admin/users",
      name: "admin-users",
      component: AdminUsersView,
      meta: { requiresAuth: true, roles: ["ADMIN"] as UserRole[] },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const needsAuth = Boolean(to.meta.requiresAuth);
  const isGuestRoute = Boolean(to.meta.guest);
  const shouldRestore =
    !auth.user &&
    (!auth.hasTriedRestore || hasStoredTokens()) &&
    (needsAuth || (isGuestRoute && hasStoredTokens()));

  if (shouldRestore) {
    await auth.restoreSession();
  }

  if (isGuestRoute && auth.isAuthenticated) {
    return roleHomePath(auth.role);
  }

  if (needsAuth && !auth.isAuthenticated) {
    if (to.path === "/login") {
      return true;
    }
    return {
      path: "/login",
      query: { redirect: to.fullPath },
    };
  }

  const allowedRoles = to.meta.roles as UserRole[] | undefined;
  if (allowedRoles && auth.role && !allowedRoles.includes(auth.role)) {
    return roleHomePath(auth.role);
  }

  return true;
});

export function isPathAllowedForRole(path: string, role: UserRole): boolean {
  const resolved = router.resolve(path);
  if (resolved.meta.guest) {
    return false;
  }
  if (!resolved.meta.requiresAuth) {
    return true;
  }
  const roles = resolved.meta.roles as UserRole[] | undefined;
  if (!roles?.length) {
    return true;
  }
  return roles.includes(role);
}

export default router;
