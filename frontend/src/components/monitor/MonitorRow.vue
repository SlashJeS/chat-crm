<script setup lang="ts">
import { computed } from "vue";

import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import type { MonitorChatter } from "@/types/monitor";
import { formatDateTime, formatRelativeTime } from "@/utils/date";
import { getInitials } from "@/utils/initials";
import { getMonitorChatterStatus, monitorStatusTone } from "@/utils/status";

const props = defineProps<{
  chatter: MonitorChatter;
}>();

const initials = computed(() => getInitials(props.chatter.display_name));
const rowStatus = computed(() => getMonitorChatterStatus(props.chatter));
const rowStatusTone = computed(() => monitorStatusTone(rowStatus.value));

const rowClass = computed(() => {
  if (props.chatter.overdue_conversations_count > 0) {
    return "monitor-row--overdue";
  }
  if (props.chatter.waiting_conversations_count > 0) {
    return "monitor-row--waiting";
  }
  if (!props.chatter.is_online) {
    return "monitor-row--offline";
  }
  return "monitor-row--healthy";
});
</script>

<template>
  <tr class="monitor-row" :class="rowClass">
    <td data-label="Chatter">
      <div class="monitor-row__chatter">
        <span class="avatar avatar--md monitor-row__avatar">{{ initials }}</span>
        <div>
          <div class="monitor-row__name">{{ chatter.display_name }}</div>
          <div class="monitor-row__username muted">@{{ chatter.username }}</div>
        </div>
      </div>
    </td>
    <td data-label="Presence">
      <span
        class="monitor-row__presence"
        :class="chatter.is_online ? 'monitor-row__presence--online' : 'monitor-row__presence--offline'"
      >
        <span
          class="status-dot"
          :class="{
            'status-dot--success': chatter.is_online,
          }"
          aria-hidden="true"
        />
        {{ chatter.is_online ? "Online" : "Offline" }}
      </span>
    </td>
    <td data-label="Active dialogs">
      <span class="monitor-row__metric">{{ chatter.active_conversations_count }}</span>
    </td>
    <td data-label="Waiting">
      <OverdueBadge
        v-if="chatter.waiting_conversations_count > 0"
        :count="chatter.waiting_conversations_count"
        :label="`${chatter.waiting_conversations_count} waiting`"
        tone="warning"
      />
      <span v-else class="monitor-row__metric monitor-row__metric--muted">0</span>
    </td>
    <td data-label="Overdue">
      <OverdueBadge
        v-if="chatter.overdue_conversations_count > 0"
        :count="chatter.overdue_conversations_count"
      />
      <span v-else class="monitor-row__metric monitor-row__metric--muted">0</span>
    </td>
    <td data-label="Last seen">
      <span
        class="monitor-row__last-seen"
        :title="chatter.last_seen_at ? formatDateTime(chatter.last_seen_at) : 'Never seen'"
      >
        {{ chatter.last_seen_at ? formatRelativeTime(chatter.last_seen_at) : "Never" }}
      </span>
    </td>
    <td data-label="Status">
      <OverdueBadge
        :count="0"
        :label="rowStatus"
        :tone="rowStatusTone"
      />
    </td>
  </tr>
</template>

<style scoped>
.monitor-row--overdue {
  box-shadow: inset 2px 0 0 var(--color-danger);
}

.monitor-row--waiting:not(.monitor-row--overdue) {
  box-shadow: inset 2px 0 0 var(--color-warning);
}

.monitor-row--offline {
  color: var(--color-text-muted);
}

.monitor-row--healthy {
  box-shadow: none;
}

.monitor-row__chatter {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.monitor-row__avatar {
  flex-shrink: 0;
}

.monitor-row__name {
  font-weight: 600;
  color: var(--color-text);
}

.monitor-row__username {
  font-size: 0.82rem;
  margin-top: 0.1rem;
}

.monitor-row__presence {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.monitor-row__presence--online {
  color: var(--color-text);
}

.monitor-row__presence--offline {
  color: var(--color-text-soft);
}

.monitor-row__metric {
  font-weight: 600;
  color: var(--color-text);
}

.monitor-row__metric--muted {
  color: var(--color-text-soft);
  font-weight: 500;
}

.monitor-row__last-seen {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .monitor-row {
    display: block;
    padding: var(--space-4);
    border-bottom: 1px solid var(--color-border);
  }

  .monitor-row td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border: none;
  }

  .monitor-row td::before {
    content: attr(data-label);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-text-soft);
    flex-shrink: 0;
  }

  .monitor-row td:first-child {
    padding-top: 0;
  }

  .monitor-row td:last-child {
    padding-bottom: 0;
  }

  .monitor-row__chatter {
    flex: 1;
    justify-content: flex-end;
  }
}
</style>
