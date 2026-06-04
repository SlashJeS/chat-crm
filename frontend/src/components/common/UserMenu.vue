<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";

import AppIcon from "@/components/common/AppIcon.vue";
import { useAuthStore } from "@/stores/auth.store";
import type { UserRole } from "@/types/auth";

withDefaults(
  defineProps<{
    compact?: boolean;
  }>(),
  {
    compact: false,
  },
);

const auth = useAuthStore();
const router = useRouter();
const menuOpen = ref(false);
const menuRoot = ref<HTMLElement | null>(null);

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

function toggleMenu(): void {
  menuOpen.value = !menuOpen.value;
}

function closeMenu(): void {
  menuOpen.value = false;
}

function handleDocumentClick(event: MouseEvent): void {
  if (!menuOpen.value || !menuRoot.value) {
    return;
  }
  if (!menuRoot.value.contains(event.target as Node)) {
    closeMenu();
  }
}

function handleDocumentKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    closeMenu();
  }
}

function logout(): void {
  closeMenu();
  auth.logout();
  router.push("/login");
}

onMounted(() => {
  document.addEventListener("click", handleDocumentClick);
  document.addEventListener("keydown", handleDocumentKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", handleDocumentClick);
  document.removeEventListener("keydown", handleDocumentKeydown);
});
</script>

<template>
  <div v-if="auth.user" ref="menuRoot" class="user-menu">
    <button
      type="button"
      class="user-menu__trigger"
      :aria-expanded="menuOpen"
      aria-haspopup="menu"
      @click.stop="toggleMenu"
    >
      <span class="avatar avatar--sm user-menu__avatar">{{ userInitials }}</span>
      <span v-if="!compact" class="user-menu__info">
        <span class="user-menu__name">{{ auth.user.display_name }}</span>
        <span class="user-menu__role">{{ roleLabel(auth.user.role) }}</span>
      </span>
      <AppIcon
        name="chevron-down"
        size="sm"
        class="user-menu__chevron"
        :class="{ 'user-menu__chevron--open': menuOpen }"
      />
    </button>

    <div v-if="menuOpen" class="user-menu__dropdown" role="menu">
      <div class="user-menu__dropdown-header">
        <strong>{{ auth.user.display_name }}</strong>
        <span class="muted">@{{ auth.user.username }}</span>
        <span v-if="auth.user.email" class="user-menu__email muted">{{ auth.user.email }}</span>
        <span class="role-badge">{{ roleLabel(auth.user.role) }}</span>
      </div>
      <hr class="divider user-menu__divider" />
      <button type="button" class="user-menu__logout" role="menuitem" @click="logout">
        Log out
      </button>
    </div>
  </div>
</template>

<style scoped>
.user-menu {
  position: relative;
}

.user-menu__trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0.25rem 0.5rem 0.25rem 0.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast);
}

.user-menu__trigger:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.user-menu__trigger:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.user-menu__avatar {
  flex-shrink: 0;
}

.user-menu__info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.25;
  min-width: 0;
  text-align: left;
}

.user-menu__name {
  font-size: 0.8125rem;
  font-weight: 500;
  max-width: 9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-menu__role {
  font-size: 0.6875rem;
  color: var(--color-text-soft);
}

.user-menu__chevron {
  color: var(--color-text-soft);
  transition: transform var(--transition-fast);
}

.user-menu__chevron--open {
  transform: rotate(180deg);
}

.user-menu__dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  z-index: 60;
  min-width: 14rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
}

.user-menu__dropdown-header {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.8125rem;
}

.user-menu__dropdown-header strong {
  color: var(--color-text);
}

.user-menu__email {
  font-size: 0.75rem;
}

.user-menu__divider {
  margin: var(--space-3) 0;
}

.user-menu__logout {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text);
  font-size: 0.8125rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
}

.user-menu__logout:hover {
  background: var(--color-surface-hover);
}

.user-menu__logout:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

@media (max-width: 520px) {
  .user-menu__info {
    display: none;
  }
}
</style>
