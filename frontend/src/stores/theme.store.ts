import { defineStore } from "pinia";
import { ref } from "vue";

export type ThemeMode = "dark" | "light";

const STORAGE_KEY = "crm-theme";

function applyTheme(theme: ThemeMode): void {
  document.documentElement.dataset.theme = theme;
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<ThemeMode>("dark");

  function initTheme(): void {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      theme.value = stored;
    } else {
      theme.value = "dark";
    }
    applyTheme(theme.value);
  }

  function setTheme(nextTheme: ThemeMode): void {
    theme.value = nextTheme;
    localStorage.setItem(STORAGE_KEY, nextTheme);
    applyTheme(nextTheme);
  }

  function toggleTheme(): void {
    setTheme(theme.value === "dark" ? "light" : "dark");
  }

  return {
    theme,
    initTheme,
    setTheme,
    toggleTheme,
  };
});
