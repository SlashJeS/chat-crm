import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { TOKEN_KEY } from "@/api/http";
import type { AuthUser, UserRole } from "@/types/auth";

function parsePlaceholderRole(storedToken: string | null): UserRole | null {
  if (!storedToken?.startsWith("placeholder-")) {
    return null;
  }
  const parsed = storedToken.replace("placeholder-", "").toUpperCase();
  if (parsed === "CHATTER" || parsed === "TEAMLEAD" || parsed === "ADMIN") {
    return parsed;
  }
  return null;
}

function createPlaceholderUser(selectedRole: UserRole): AuthUser {
  return {
    id: 1,
    username: selectedRole === "CHATTER" ? "chatter_demo" : "teamlead_demo",
    email: `${selectedRole.toLowerCase()}@example.com`,
    role: selectedRole,
  };
}

const initialToken = localStorage.getItem(TOKEN_KEY);
const initialRole = parsePlaceholderRole(initialToken);

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(initialToken);
  const user = ref<AuthUser | null>(
    initialRole ? createPlaceholderUser(initialRole) : null,
  );
  const role = ref<UserRole | null>(initialRole);

  const isAuthenticated = computed(() => Boolean(token.value));

  function loginPlaceholder(selectedRole: UserRole): void {
    const placeholderToken = `placeholder-${selectedRole.toLowerCase()}`;
    token.value = placeholderToken;
    role.value = selectedRole;
    user.value = createPlaceholderUser(selectedRole);
    localStorage.setItem(TOKEN_KEY, placeholderToken);
  }

  function logout(): void {
    token.value = null;
    user.value = null;
    role.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  return {
    token,
    user,
    role,
    isAuthenticated,
    loginPlaceholder,
    logout,
  };
});
