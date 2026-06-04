<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import AddUserInviteModal from "@/components/admin/AddUserInviteModal.vue";
import InvitesTable from "@/components/admin/InvitesTable.vue";
import AppLayout from "@/components/common/AppLayout.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import { useAdminStore } from "@/stores/admin.store";
import { useAuthStore } from "@/stores/auth.store";
import type { CreateInvitePayload, UserInvite } from "@/types/admin";
import { formatDateTime, formatRelativeTime } from "@/utils/date";

const adminStore = useAdminStore();
const auth = useAuthStore();

const inviteModalOpen = ref(false);
const createdInvite = ref<UserInvite | null>(null);
const actionLoadingId = ref<number | null>(null);

const currentUserId = computed(() => auth.user?.id ?? null);

function roleBadgeClass(role: string): string {
  switch (role) {
    case "ADMIN":
      return "badge badge-primary";
    case "TEAMLEAD":
      return "badge badge-warning";
    default:
      return "badge badge-muted";
  }
}

async function loadAll(): Promise<void> {
  await Promise.all([adminStore.loadUsers(), adminStore.loadInvites()]);
}

function openInviteModal(): void {
  createdInvite.value = null;
  inviteModalOpen.value = true;
}

function closeInviteModal(): void {
  inviteModalOpen.value = false;
  createdInvite.value = null;
}

async function handleCreateInvite(payload: CreateInvitePayload): Promise<void> {
  try {
    const invite = await adminStore.createInvite(payload);
    createdInvite.value = invite;
  } catch {
    // error in store
  }
}

async function handleRevokeInvite(id: number): Promise<void> {
  actionLoadingId.value = id;
  try {
    await adminStore.revokeInvite(id);
  } finally {
    actionLoadingId.value = null;
  }
}

async function handleDeactivateUser(id: number): Promise<void> {
  actionLoadingId.value = id;
  try {
    await adminStore.deactivateUser(id);
  } finally {
    actionLoadingId.value = null;
  }
}

async function handleActivateUser(id: number): Promise<void> {
  actionLoadingId.value = id;
  try {
    await adminStore.activateUser(id);
  } finally {
    actionLoadingId.value = null;
  }
}

onMounted(async () => {
  await loadAll();
});

onUnmounted(() => {
  adminStore.clear();
});
</script>

<template>
  <AppLayout>
    <div class="admin-users page">
      <header class="admin-users__header page-header">
        <div>
          <h1 class="page-title">Users</h1>
          <p class="page-subtitle">
            Manage team access and invite new chatters or teamleads
          </p>
        </div>
        <button type="button" class="btn btn-primary" @click="openInviteModal">
          Add user
        </button>
      </header>

      <ErrorState
        v-if="adminStore.error && !adminStore.users.length && !adminStore.isLoadingUsers"
        title="Could not load admin data"
        :message="adminStore.error"
        retry-label="Retry"
        @retry="loadAll"
      />

      <template v-else>
        <section class="admin-users__section panel">
          <header class="admin-users__section-header">
            <div>
              <h2 class="admin-users__section-title">Team members</h2>
              <p class="admin-users__section-subtitle muted">
                {{ adminStore.usersCount }} user{{ adminStore.usersCount === 1 ? "" : "s" }}
              </p>
            </div>
          </header>

          <LoadingState v-if="adminStore.isLoadingUsers" message="Loading users…" />

          <div v-else class="admin-users__scroll">
            <table class="admin-users__table">
              <thead>
                <tr>
                  <th scope="col">User</th>
                  <th scope="col">Role</th>
                  <th scope="col">Status</th>
                  <th scope="col">Last seen</th>
                  <th scope="col">Joined</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in adminStore.users" :key="user.id">
                  <td>
                    <div class="admin-users__user-cell">
                      <strong>{{ user.display_name }}</strong>
                      <span class="muted">{{ user.username }}</span>
                      <span v-if="user.email" class="muted">{{ user.email }}</span>
                    </div>
                  </td>
                  <td>
                    <span :class="roleBadgeClass(user.role)">{{ user.role }}</span>
                  </td>
                  <td>
                    <span :class="user.is_active ? 'badge badge-success' : 'badge badge-danger'">
                      {{ user.is_active ? "Active" : "Inactive" }}
                    </span>
                  </td>
                  <td class="muted">
                    {{ user.last_seen_at ? formatRelativeTime(user.last_seen_at) : "—" }}
                  </td>
                  <td class="muted">{{ formatDateTime(user.date_joined) }}</td>
                  <td>
                    <div class="admin-users__actions">
                      <button
                        v-if="user.is_active && user.id !== currentUserId"
                        type="button"
                        class="btn btn-secondary btn-sm"
                        :disabled="actionLoadingId === user.id"
                        @click="handleDeactivateUser(user.id)"
                      >
                        Deactivate
                      </button>
                      <button
                        v-else-if="!user.is_active"
                        type="button"
                        class="btn btn-secondary btn-sm"
                        :disabled="actionLoadingId === user.id"
                        @click="handleActivateUser(user.id)"
                      >
                        Activate
                      </button>
                      <span v-else class="muted admin-users__self-note">You</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <InvitesTable
          :invites="adminStore.invites"
          :is-loading="adminStore.isLoadingInvites"
          @revoke="handleRevokeInvite"
        />
      </template>
    </div>

    <AddUserInviteModal
      :open="inviteModalOpen"
      :is-submitting="adminStore.isCreatingInvite"
      :created-invite="createdInvite"
      @close="closeInviteModal"
      @create="handleCreateInvite"
    />
  </AppLayout>
</template>

<style scoped>
.admin-users {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.admin-users__header {
  align-items: flex-start;
}

.admin-users__section {
  overflow: hidden;
}

.admin-users__section-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.admin-users__section-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
}

.admin-users__section-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
}

.admin-users__scroll {
  overflow-x: auto;
}

.admin-users__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.admin-users__table th,
.admin-users__table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.admin-users__table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-soft);
  background: var(--color-bg-soft);
}

.admin-users__user-cell {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.admin-users__user-cell strong {
  color: var(--color-text);
}

.admin-users__actions {
  display: flex;
  gap: var(--space-2);
}

.admin-users__self-note {
  font-size: 0.75rem;
}
</style>
