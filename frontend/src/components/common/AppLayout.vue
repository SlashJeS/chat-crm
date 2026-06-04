<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import AppIcon from "@/components/common/AppIcon.vue";
import AppLogo from "@/components/common/AppLogo.vue";
import ThemeToggle from "@/components/common/ThemeToggle.vue";
import UserMenu from "@/components/common/UserMenu.vue";
import { useChatSocket } from "@/composables/useChatSocket";
import { useAuthStore } from "@/stores/auth.store";
import { getCurrentPageTitle } from "@/utils/page-title";
import { getConnectionTone, getRealtimeConnectionLabel } from "@/utils/status";

const SIDEBAR_COLLAPSED_KEY = "crm-sidebar-collapsed";
const MOBILE_BREAKPOINT = 901;

const route = useRoute();
const auth = useAuthStore();
const chatSocket = useChatSocket();

function readSidebarCollapsed(): boolean {
  const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
  if (stored !== null) {
    return stored === "true";
  }
  return window.innerWidth < MOBILE_BREAKPOINT;
}

const isSidebarCollapsed = ref(false);

const showChatterNav = computed(() => auth.user?.role === "CHATTER");
const showLeadNav = computed(
  () => auth.user?.role === "TEAMLEAD" || auth.user?.role === "ADMIN",
);
const showAdminUsersNav = computed(() => auth.user?.role === "ADMIN");

const isChatterPage = computed(() => route.path === "/chatter");
const pageTitle = computed(() => getCurrentPageTitle(route.path));

const sidebarToggleLabel = computed(() =>
  isSidebarCollapsed.value ? "Expand sidebar" : "Collapse sidebar",
);

const connectionPillClass = computed(() =>
  `status-pill--${getConnectionTone(chatSocket.connectionState.value, Boolean(chatSocket.lastError.value))}`,
);

function toggleSidebar(): void {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(isSidebarCollapsed.value));
}

onMounted(() => {
  isSidebarCollapsed.value = readSidebarCollapsed();
});
</script>

<template>
  <div
    class="app-shell"
    :class="{
      'app-shell--sidebar-collapsed': isSidebarCollapsed,
      'app-shell--full-height': isChatterPage,
    }"
  >
    <aside class="app-sidebar" aria-label="Application sidebar">
      <div class="app-sidebar__brand">
        <RouterLink to="/" class="app-sidebar__logo" aria-label="CRM Chatters home">
          <AppLogo :variant="isSidebarCollapsed ? 'mark' : 'full'" size="sm" />
        </RouterLink>
        <button
          type="button"
          class="app-sidebar__toggle"
          :aria-label="sidebarToggleLabel"
          :title="sidebarToggleLabel"
          @click="toggleSidebar"
        >
          <AppIcon name="chevron-left" size="sm" />
        </button>
      </div>

      <nav class="app-sidebar__nav" aria-label="Main navigation">
        <RouterLink
          v-if="showChatterNav"
          to="/chatter"
          class="sidebar-nav__link"
          :class="{ 'sidebar-nav__link--active': route.path === '/chatter' }"
          :title="isSidebarCollapsed ? 'Chatter Workspace' : undefined"
        >
          <AppIcon name="chat" size="md" class="sidebar-nav__icon" />
          <span class="sidebar-nav__label">Chatter Workspace</span>
        </RouterLink>

        <template v-if="showLeadNav">
          <RouterLink
            to="/teamlead"
            class="sidebar-nav__link"
            :class="{ 'sidebar-nav__link--active': route.path === '/teamlead' }"
            :title="isSidebarCollapsed ? 'Monitor' : undefined"
          >
            <AppIcon name="monitor" size="md" class="sidebar-nav__icon" />
            <span class="sidebar-nav__label">Monitor</span>
          </RouterLink>

          <RouterLink
            to="/lead/dialogs"
            class="sidebar-nav__link"
            :class="{ 'sidebar-nav__link--active': route.path === '/lead/dialogs' }"
            :title="isSidebarCollapsed ? 'Dialogs' : undefined"
          >
            <AppIcon name="dialogs" size="md" class="sidebar-nav__icon" />
            <span class="sidebar-nav__label">Dialogs</span>
          </RouterLink>

          <RouterLink
            v-if="showAdminUsersNav"
            to="/admin/users"
            class="sidebar-nav__link"
            :class="{ 'sidebar-nav__link--active': route.path === '/admin/users' }"
            :title="isSidebarCollapsed ? 'Users' : undefined"
          >
            <AppIcon name="users" size="md" class="sidebar-nav__icon" />
            <span class="sidebar-nav__label">Users</span>
          </RouterLink>
        </template>
      </nav>

      <div class="app-sidebar__footer">
        <ThemeToggle :compact="isSidebarCollapsed" />
      </div>
    </aside>

    <div class="app-shell__main">
      <header class="app-topbar">
        <div class="app-topbar__start">
          <h1 class="app-topbar__title">{{ pageTitle }}</h1>
          <span v-if="isChatterPage" class="status-pill" :class="connectionPillClass">
            <span class="status-dot" aria-hidden="true" />
            {{ getRealtimeConnectionLabel(chatSocket.connectionState.value) }}
          </span>
        </div>
        <div class="app-topbar__actions">
          <UserMenu />
        </div>
      </header>

      <main class="app-main" :class="{ 'app-main--full': isChatterPage }">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  overflow-x: clip;
}

.app-shell--full-height {
  min-height: 100vh;
}

@media (min-width: 901px) {
  .app-shell--full-height {
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
  }
}

.app-sidebar {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  width: var(--sidebar-width);
  height: 100vh;
  position: sticky;
  top: 0;
  border-right: 1px solid var(--color-border);
  background: var(--color-surface);
  transition: width var(--transition-normal);
  overflow: hidden;
}

.app-shell--sidebar-collapsed .app-sidebar {
  width: var(--sidebar-width-collapsed);
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  min-height: var(--topbar-height);
  padding: 0 var(--space-3);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.app-shell--sidebar-collapsed .app-sidebar__brand {
  flex-direction: column;
  justify-content: center;
  padding-block: var(--space-3);
  gap: var(--space-2);
}

.app-sidebar__logo {
  display: inline-flex;
  align-items: center;
  min-width: 0;
  text-decoration: none;
}

.app-shell--sidebar-collapsed .app-sidebar__logo {
  justify-content: center;
}

.app-sidebar__toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  color: var(--color-text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
}

.app-sidebar__toggle .app-icon {
  transition: transform var(--transition-normal);
}

.app-shell--sidebar-collapsed .app-sidebar__toggle .app-icon {
  transform: rotate(180deg);
}

.app-sidebar__toggle:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.app-sidebar__nav {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-3) var(--space-2);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.sidebar-nav__link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-md);
  border-left: 2px solid transparent;
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.8125rem;
  font-weight: 500;
  transition:
    background var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.app-shell--sidebar-collapsed .sidebar-nav__link {
  justify-content: center;
  padding-inline: 0.5rem;
}

.sidebar-nav__link:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.sidebar-nav__link--active {
  color: var(--color-primary);
  background: var(--color-primary-soft);
  border-left-color: var(--color-primary);
  font-weight: 600;
}

.sidebar-nav__icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.sidebar-nav__label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-shell--sidebar-collapsed .sidebar-nav__label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.app-sidebar__footer {
  flex-shrink: 0;
  padding: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.app-shell--sidebar-collapsed .app-sidebar__footer {
  display: flex;
  justify-content: center;
}

.app-shell__main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-shell--full-height .app-shell__main {
  min-height: 0;
  height: 100vh;
  overflow: hidden;
}

.app-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  height: var(--topbar-height);
  flex-shrink: 0;
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.app-topbar__start {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.app-topbar__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-topbar__actions {
  flex-shrink: 0;
}

.app-main {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-5);
}

.app-main--full {
  max-width: none;
  padding: var(--space-2) var(--space-5);
  overflow: hidden;
}

.app-main--full > * {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

@media (min-width: 901px) {
  .app-shell--full-height .app-main--full {
    overflow: hidden;
  }
}

@media (max-width: 900px) {
  .app-shell--full-height .app-shell__main {
    height: auto;
    overflow: visible;
  }

  .app-main--full {
    overflow: visible;
  }

  .app-main--full > * {
    flex: none;
    min-height: auto;
  }

  .app-topbar {
    padding-inline: var(--space-3);
  }

  .app-main {
    padding-inline: var(--space-3);
  }
}
</style>
