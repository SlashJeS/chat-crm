<script setup lang="ts">
import { computed, ref } from "vue";

import type { UserInvite } from "@/types/admin";
import { formatDateTime } from "@/utils/date";

const props = defineProps<{
  invites: UserInvite[];
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  revoke: [id: number];
}>();

const copyFeedbackId = ref<number | null>(null);

function inviteStatus(invite: UserInvite): string {
  if (invite.is_accepted) {
    return "accepted";
  }
  if (invite.is_revoked) {
    return "revoked";
  }
  if (invite.is_expired) {
    return "expired";
  }
  return "active";
}

function statusBadgeClass(status: string): string {
  switch (status) {
    case "active":
      return "badge badge-success";
    case "accepted":
      return "badge badge-muted";
    case "revoked":
      return "badge badge-danger";
    case "expired":
      return "badge badge-warning";
    default:
      return "badge badge-muted";
  }
}

function emailLabel(invite: UserInvite): string {
  return invite.email || "Open invite";
}

async function copyLink(invite: UserInvite): Promise<void> {
  try {
    await navigator.clipboard.writeText(invite.invite_url);
    copyFeedbackId.value = invite.id;
    window.setTimeout(() => {
      if (copyFeedbackId.value === invite.id) {
        copyFeedbackId.value = null;
      }
    }, 2000);
  } catch {
    copyFeedbackId.value = null;
  }
}

const hasInvites = computed(() => props.invites.length > 0);
</script>

<template>
  <section class="invites-table panel">
    <header class="invites-table__header">
      <div>
        <h2 class="invites-table__title">Invite links</h2>
        <p class="invites-table__subtitle muted">Pending and historical invites</p>
      </div>
    </header>

    <div v-if="isLoading" class="invites-table__loading muted">Loading invites…</div>

    <div v-else-if="!hasInvites" class="invites-table__empty empty-state">
      <p class="empty-state__title">No invites yet</p>
      <span class="empty-state__text">Create an invite link to add a new team member.</span>
    </div>

    <div v-else class="invites-table__scroll">
      <table class="invites-table__table">
        <thead>
          <tr>
            <th scope="col">Invite</th>
            <th scope="col">Role</th>
            <th scope="col">Status</th>
            <th scope="col">Expires</th>
            <th scope="col">Created</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invite in invites" :key="invite.id">
            <td>
              <strong>{{ emailLabel(invite) }}</strong>
            </td>
            <td>{{ invite.role }}</td>
            <td>
              <span :class="statusBadgeClass(inviteStatus(invite))">
                {{ inviteStatus(invite) }}
              </span>
            </td>
            <td class="muted">{{ formatDateTime(invite.expires_at) }}</td>
            <td class="muted">{{ formatDateTime(invite.created_at) }}</td>
            <td>
              <div class="invites-table__actions">
                <button
                  v-if="invite.is_active_invite"
                  type="button"
                  class="btn btn-secondary btn-sm"
                  @click="copyLink(invite)"
                >
                  {{ copyFeedbackId === invite.id ? "Copied" : "Copy link" }}
                </button>
                <button
                  v-if="invite.is_active_invite"
                  type="button"
                  class="btn btn-secondary btn-sm"
                  @click="emit('revoke', invite.id)"
                >
                  Revoke
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.invites-table {
  overflow: hidden;
}

.invites-table__header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.invites-table__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
}

.invites-table__subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
}

.invites-table__loading,
.invites-table__empty {
  padding: var(--space-5);
}

.invites-table__scroll {
  overflow-x: auto;
}

.invites-table__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.invites-table__table th,
.invites-table__table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.invites-table__table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-soft);
  background: var(--color-bg-soft);
}

.invites-table__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
</style>
