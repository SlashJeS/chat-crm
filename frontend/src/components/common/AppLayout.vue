<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
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

const showChatterNav = computed(() => auth.user?.role === "CHATTER");
const showMonitorNav = computed(
  () => auth.user?.role === "TEAMLEAD" || auth.user?.role === "ADMIN",
);

const isChatterPage = computed(() => route.path === "/chatter");

const userInitials = computed(() => {
  if (!auth.user) {
    return "";
  }
  const name = auth.user.display_name || auth.user.username;
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0]![0]}${parts[1]![0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

function logout(): void {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="app-layout" :class="{ 'app-layout--full-height': isChatterPage }">
    <header class="app-layout__header">
      <div class="app-layout__header-inner">
        <div class="app-layout__brand">
          <RouterLink to="/" class="app-layout__logo-link" aria-label="CRM Chatters home">
            <AppLogo variant="full" size="sm" />
          </RouterLink>

          <nav
            v-if="auth.isAuthenticated"
            class="app-layout__nav"
            aria-label="Main navigation"
          >
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

        <div class="app-layout__actions toolbar">
          <ThemeToggle />
          <template v-if="auth.isAuthenticated && auth.user">
            <div class="app-layout__user">
              <span class="avatar avatar--sm" :aria-label="`${auth.user.display_name} avatar`">
                {{ userInitials }}
              </span>
              <div class="app-layout__user-info">
                <span class="app-layout__display-name">{{ auth.user.display_name }}</span>
                <span class="app-layout__username muted">@{{ auth.user.username }}</span>
              </div>
              <span class="role-badge">{{ roleLabel(auth.user.role) }}</span>
              <button type="button" class="btn btn-ghost" aria-label="Log out" @click="logout">
                Logout
              </button>
            </div>
          </template>
        </div>
      </div>
    </header>

    <main class="app-layout__main" :class="{ 'app-layout__main--full': isChatterPage }">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: clip;
}

.app-layout--full-height {
  min-height: 100vh;
}

@media (min-width: 901px) {
  .app-layout--full-height {
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
  }

  .app-layout--full-height .app-layout__header {
    flex: 0 0 var(--header-height);
  }

  .app-layout__main--full {
    overflow: hidden;
  }
}

.app-layout__header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: var(--header-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.app-layout__header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  height: 100%;
  max-width: 100%;
  padding: 0 var(--space-5);
}

.app-layout__brand {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  min-width: 0;
  flex: 1;
}

.app-layout__logo-link {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  text-decoration: none;
}

.app-layout__nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  overflow-x: auto;
}

.app-layout__nav-link {
  position: relative;
  padding: 0.4rem 0.65rem;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.app-layout__nav-link:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.app-layout__nav-link--active {
  color: var(--color-primary);
  background: var(--color-primary-soft);
}

.app-layout__nav-link--active::after {
  content: "";
  position: absolute;
  left: 0.65rem;
  right: 0.65rem;
  bottom: -0.55rem;
  height: 2px;
  background: var(--color-primary);
  border-radius: 1px;
}

.app-layout__actions {
  flex-shrink: 0;
}

.app-layout__user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-left: var(--space-3);
  margin-left: var(--space-2);
  border-left: 1px solid var(--color-border);
}

.app-layout__user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}

.app-layout__display-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 9rem;
}

.app-layout__username {
  font-size: 0.6875rem;
}

.app-layout__main {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-5);
}

.app-layout__main--full {
  max-width: none;
  flex: 1 1 auto;
  min-height: 0;
  padding: var(--space-2) var(--space-5);
}

.app-layout__main--full > * {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

@media (max-width: 900px) {
  .app-layout__main--full {
    overflow: visible;
    min-height: auto;
  }

  .app-layout__main--full > * {
    flex: none;
    min-height: auto;
  }

  .app-layout__header-inner {
    flex-wrap: wrap;
    height: auto;
    min-height: var(--header-height);
    padding-block: var(--space-2);
  }

  .app-layout__brand {
    flex-wrap: wrap;
    width: 100%;
  }

  .app-layout__actions {
    width: 100%;
    justify-content: space-between;
  }

  .app-layout__user {
    border-left: none;
    margin-left: 0;
    padding-left: 0;
  }
}

@media (max-width: 520px) {
  .app-layout__header-inner {
    padding-inline: var(--space-3);
  }

  .app-layout__user-info {
    display: none;
  }
}
</style>
