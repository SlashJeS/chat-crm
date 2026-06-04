import { defineStore } from "pinia";
import { ref } from "vue";

import {
  ADMIN_INVITES,
  ADMIN_USERS,
  adminInviteRevoke,
  adminUserActivate,
  adminUserDeactivate,
} from "@/api/endpoints";
import { http } from "@/api/http";
import type {
  AdminUser,
  AdminUserListResponse,
  CreateInvitePayload,
  UserInvite,
  UserInviteListResponse,
} from "@/types/admin";

export const useAdminStore = defineStore("admin", () => {
  const users = ref<AdminUser[]>([]);
  const usersCount = ref(0);
  const invites = ref<UserInvite[]>([]);
  const invitesCount = ref(0);
  const isLoadingUsers = ref(false);
  const isLoadingInvites = ref(false);
  const isCreatingInvite = ref(false);
  const error = ref<string | null>(null);

  async function loadUsers(): Promise<void> {
    isLoadingUsers.value = true;
    error.value = null;
    try {
      const { data } = await http.get<AdminUserListResponse>(ADMIN_USERS, {
        params: { limit: 100 },
      });
      users.value = data.results;
      usersCount.value = data.count;
    } catch {
      error.value = "Failed to load users";
      throw new Error(error.value);
    } finally {
      isLoadingUsers.value = false;
    }
  }

  async function loadInvites(): Promise<void> {
    isLoadingInvites.value = true;
    error.value = null;
    try {
      const { data } = await http.get<UserInviteListResponse>(ADMIN_INVITES, {
        params: { limit: 100 },
      });
      invites.value = data.results;
      invitesCount.value = data.count;
    } catch {
      error.value = "Failed to load invites";
      throw new Error(error.value);
    } finally {
      isLoadingInvites.value = false;
    }
  }

  async function createInvite(payload: CreateInvitePayload): Promise<UserInvite> {
    isCreatingInvite.value = true;
    error.value = null;
    try {
      const { data } = await http.post<UserInvite>(ADMIN_INVITES, payload);
      invites.value = [data, ...invites.value];
      invitesCount.value += 1;
      return data;
    } catch {
      error.value = "Failed to create invite";
      throw new Error(error.value);
    } finally {
      isCreatingInvite.value = false;
    }
  }

  async function revokeInvite(id: number): Promise<void> {
    error.value = null;
    try {
      const { data } = await http.post<UserInvite>(adminInviteRevoke(id));
      const index = invites.value.findIndex((invite) => invite.id === id);
      if (index !== -1) {
        invites.value[index] = data;
      }
    } catch {
      error.value = "Failed to revoke invite";
      throw new Error(error.value);
    }
  }

  async function deactivateUser(id: number): Promise<void> {
    error.value = null;
    try {
      const { data } = await http.post<AdminUser>(adminUserDeactivate(id));
      const index = users.value.findIndex((user) => user.id === id);
      if (index !== -1) {
        users.value[index] = data;
      }
    } catch {
      error.value = "Failed to deactivate user";
      throw new Error(error.value);
    }
  }

  async function activateUser(id: number): Promise<void> {
    error.value = null;
    try {
      const { data } = await http.post<AdminUser>(adminUserActivate(id));
      const index = users.value.findIndex((user) => user.id === id);
      if (index !== -1) {
        users.value[index] = data;
      }
    } catch {
      error.value = "Failed to activate user";
      throw new Error(error.value);
    }
  }

  function clear(): void {
    users.value = [];
    usersCount.value = 0;
    invites.value = [];
    invitesCount.value = 0;
    isLoadingUsers.value = false;
    isLoadingInvites.value = false;
    isCreatingInvite.value = false;
    error.value = null;
  }

  return {
    users,
    usersCount,
    invites,
    invitesCount,
    isLoadingUsers,
    isLoadingInvites,
    isCreatingInvite,
    error,
    loadUsers,
    loadInvites,
    createInvite,
    revokeInvite,
    deactivateUser,
    activateUser,
    clear,
  };
});
