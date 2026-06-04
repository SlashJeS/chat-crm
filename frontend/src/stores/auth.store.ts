import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { AUTH_TOKEN, ME } from "@/api/endpoints";
import { ACCESS_TOKEN_KEY, http, REFRESH_TOKEN_KEY } from "@/api/http";
import type { AuthUser, TokenResponse, UserRole } from "@/types/auth";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_TOKEN_KEY));
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY));
  const user = ref<AuthUser | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => Boolean(accessToken.value));
  const role = computed<UserRole | null>(() => user.value?.role ?? null);

  async function loadMe(): Promise<void> {
    const { data } = await http.get<AuthUser>(ME);
    user.value = data;
  }

  async function login(username: string, password: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const { data } = await http.post<TokenResponse>(AUTH_TOKEN, {
        username,
        password,
      });
      accessToken.value = data.access;
      refreshToken.value = data.refresh;
      localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
      await loadMe();
    } catch {
      error.value = "Invalid username or password";
      throw new Error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  function logout(): void {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    error.value = null;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  async function restoreSession(): Promise<void> {
    accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY);
    refreshToken.value = localStorage.getItem(REFRESH_TOKEN_KEY);

    if (!accessToken.value) {
      return;
    }

    try {
      await loadMe();
    } catch {
      logout();
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    error,
    isAuthenticated,
    role,
    login,
    loadMe,
    logout,
    restoreSession,
  };
});
