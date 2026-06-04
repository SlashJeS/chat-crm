<script setup lang="ts">
import { computed } from "vue";

import { useThemeStore } from "@/stores/theme.store";

const themeStore = useThemeStore();

const isDark = computed(() => themeStore.theme === "dark");

const ariaLabel = computed(() =>
  isDark.value ? "Switch to light theme" : "Switch to dark theme",
);
</script>

<template>
  <button
    type="button"
    class="theme-toggle"
    :aria-label="ariaLabel"
    :title="ariaLabel"
    @click="themeStore.toggleTheme()"
  >
    <span class="theme-toggle__track" aria-hidden="true">
      <span class="theme-toggle__option" :class="{ 'theme-toggle__option--active': isDark }">
        Dark
      </span>
      <span class="theme-toggle__option" :class="{ 'theme-toggle__option--active': !isDark }">
        Light
      </span>
      <span class="theme-toggle__thumb" :class="{ 'theme-toggle__thumb--light': !isDark }" />
    </span>
  </button>
</template>

<style scoped>
.theme-toggle {
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.theme-toggle__track {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  min-width: 6.75rem;
  padding: 0.15rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-soft);
}

.theme-toggle__option {
  position: relative;
  z-index: 1;
  padding: 0.25rem 0.45rem;
  font-size: 0.6875rem;
  font-weight: 500;
  text-align: center;
  color: var(--color-text-soft);
  user-select: none;
}

.theme-toggle__option--active {
  color: var(--color-text);
}

.theme-toggle__thumb {
  position: absolute;
  top: 0.15rem;
  left: 0.15rem;
  width: calc(50% - 0.15rem);
  height: calc(100% - 0.3rem);
  border-radius: calc(var(--radius-md) - 2px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: transform var(--transition-normal);
}

.theme-toggle__thumb--light {
  transform: translateX(100%);
}

.theme-toggle:focus-visible .theme-toggle__track {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
</style>
