import axios from "axios";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { AUTH_REFRESH, AUTH_TOKEN, ME } from "@/api/endpoints";
import { ACCESS_TOKEN_KEY, http, REFRESH_TOKEN_KEY } from "@/api/http";
import type { AuthUser, TokenResponse, UserRole } from "@/types/auth";

interface RefreshTokenResponse {
  access: string;
  refresh?: string;
}

let restorePromise: Promise<boolean> | null = null;

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const user = ref<AuthUser | null>(null);
  const isLoading = ref(false);
  const isRestoringSession = ref(false);
  const error = ref<string | null>(null);
  const hasTriedRestore = ref(false);

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value));
  const role = computed<UserRole | null>(() => user.value?.role ?? null);

  function canAccessRole(requiredRoles: UserRole[]): boolean {
    return role.value !== null && requiredRoles.includes(role.value);
  }

  function setTokens(access: string, refresh?: string | null): void {
    accessToken.value = access;
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh !== undefined && refresh !== null) {
      refreshToken.value = refresh;
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }
  }

  function clearTokens(): void {
    accessToken.value = null;
    refreshToken.value = null;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  function loadTokensFromStorage(): void {
    accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY);
    refreshToken.value = localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken.value) {
      return false;
    }

    try {
      const { data } = await axios.post<RefreshTokenResponse>(
        `${http.defaults.baseURL}${AUTH_REFRESH}`,
        { refresh: refreshToken.value },
      );
      setTokens(data.access, data.refresh ?? refreshToken.value);
      return true;
    } catch {
      return false;
    }
  }

  async function loadMe(): Promise<AuthUser> {
    try {
      const { data } = await http.get<AuthUser>(ME);
      user.value = data;
      return data;
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 401 && refreshToken.value) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          const { data } = await http.get<AuthUser>(ME);
          user.value = data;
          return data;
        }
      }
      throw err;
    }
  }

  async function login(username: string, password: string): Promise<AuthUser> {
    isLoading.value = true;
    error.value = null;
    hasTriedRestore.value = true;
    try {
      const { data } = await http.post<TokenResponse>(AUTH_TOKEN, {
        username,
        password,
      });
      setTokens(data.access, data.refresh);
      return await loadMe();
    } catch {
      error.value = "Invalid username or password";
      logout();
      throw new Error(error.value);
    } finally {
      isLoading.value = false;
    }
  }

  function logout(): void {
    clearTokens();
    user.value = null;
    error.value = null;
    isRestoringSession.value = false;
  }

  async function restoreSession(): Promise<boolean> {
    if (hasTriedRestore.value && user.value) {
      return true;
    }

    if (restorePromise) {
      return restorePromise;
    }

    restorePromise = (async () => {
      isRestoringSession.value = true;
      loadTokensFromStorage();

      if (!accessToken.value && !refreshToken.value) {
        hasTriedRestore.value = true;
        return false;
      }

      try {
        if (accessToken.value) {
          await loadMe();
        } else {
          const refreshed = await refreshAccessToken();
          if (!refreshed) {
            throw new Error("Unable to refresh session");
          }
          await loadMe();
        }
        hasTriedRestore.value = true;
        return true;
      } catch {
        logout();
        hasTriedRestore.value = true;
        return false;
      } finally {
        isRestoringSession.value = false;
      }
    })();

    try {
      return await restorePromise;
    } finally {
      restorePromise = null;
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    isRestoringSession,
    error,
    hasTriedRestore,
    isAuthenticated,
    role,
    canAccessRole,
    setTokens,
    clearTokens,
    loadTokensFromStorage,
    refreshAccessToken,
    login,
    loadMe,
    logout,
    restoreSession,
  };
});
