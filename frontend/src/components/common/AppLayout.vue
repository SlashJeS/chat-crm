<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

function roleLabel(role: UserRole): string {
  switch (role) {
    case "CHATTER":
      return "Chatter";
    case "TEAMLEAD":
      return "Teamlead";
    case "ADMIN":
      return "Admin";
  }
}

const showChatterNav = computed(
  () => auth.user?.role === "CHATTER",
);

const showMonitorNav = computed(
  () => auth.user?.role === "TEAMLEAD" || auth.user?.role === "ADMIN",
);

function logout(): void {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="app-layout">
    <header class="app-layout__header">
      <div class="app-layout__brand">
        <RouterLink to="/" class="app-layout__title">CRM Chatters Demo</RouterLink>
        <nav v-if="auth.isAuthenticated" class="app-layout__nav">
          <RouterLink
            v-if="showChatterNav"
            to="/chatter"
            class="app-layout__nav-link"
            :class="{ 'app-layout__nav-link--active': route.path === '/chatter' }"
          >
            Chatter Workspace
          </RouterLink>
          <RouterLink
            v-if="showMonitorNav"
            to="/teamlead"
            class="app-layout__nav-link"
            :class="{ 'app-layout__nav-link--active': route.path === '/teamlead' }"
          >
            Teamlead Monitor
          </RouterLink>
        </nav>
      </div>

      <div v-if="auth.isAuthenticated && auth.user" class="app-layout__user">
        <div class="app-layout__user-info">
          <span class="app-layout__display-name">{{ auth.user.display_name }}</span>
          <span class="app-layout__username">@{{ auth.user.username }}</span>
        </div>
        <span class="app-layout__role">{{ roleLabel(auth.user.role) }}</span>
        <button type="button" class="app-layout__logout" @click="logout">Logout</button>
      </div>
    </header>
    <main class="app-layout__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f1f5f9;
}

.app-layout__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.app-layout__brand {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  min-width: 0;
}

.app-layout__title {
  font-weight: 700;
  font-size: 1.05rem;
  color: #0f172a;
  text-decoration: none;
  white-space: nowrap;
}

.app-layout__nav {
  display: flex;
  gap: 0.35rem;
}

.app-layout__nav-link {
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
  color: #475569;
  text-decoration: none;
  font-size: 0.9rem;
}

.app-layout__nav-link:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.app-layout__nav-link--active {
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.app-layout__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.app-layout__user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.2;
}

.app-layout__display-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.app-layout__username {
  font-size: 0.8rem;
  color: #64748b;
}

.app-layout__role {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #e0e7ff;
  color: #3730a3;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.app-layout__logout {
  padding: 0.4rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  color: #334155;
  cursor: pointer;
  font-size: 0.85rem;
}

.app-layout__logout:hover {
  background: #f8fafc;
}

@media (max-width: 720px) {
  .app-layout__header {
    flex-direction: column;
    align-items: stretch;
  }

  .app-layout__brand {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .app-layout__user {
    justify-content: space-between;
  }

  .app-layout__user-info {
    align-items: flex-start;
  }
}
</style>
