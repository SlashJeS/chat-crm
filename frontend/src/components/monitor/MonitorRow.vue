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
    <td class="monitor-row__cell monitor-row__cell--chatter" data-label="Chatter">
      <div class="monitor-row__chatter">
        <span class="avatar monitor-row__avatar">{{ initials }}</span>
        <div class="monitor-row__identity">
          <div class="monitor-row__name" :title="chatter.display_name">{{ chatter.display_name }}</div>
          <div class="monitor-row__username" :title="chatter.username">@{{ chatter.username }}</div>
        </div>
      </div>
    </td>
    <td class="monitor-row__cell monitor-row__cell--presence" data-label="Presence">
      <span
        class="monitor-row__presence"
        :class="chatter.is_online ? 'monitor-row__presence--online' : 'monitor-row__presence--offline'"
      >
        <span
          class="status-dot"
          :class="{ 'status-dot--success': chatter.is_online }"
          aria-hidden="true"
        />
        {{ chatter.is_online ? "Online" : "Offline" }}
      </span>
    </td>
    <td class="monitor-row__cell monitor-row__cell--metric" data-label="Active dialogs">
      <span class="monitor-row__metric">{{ chatter.active_conversations_count }}</span>
    </td>
    <td class="monitor-row__cell monitor-row__cell--metric" data-label="Waiting">
      <OverdueBadge
        v-if="chatter.waiting_conversations_count > 0"
        :count="chatter.waiting_conversations_count"
        :label="`${chatter.waiting_conversations_count} waiting`"
        tone="warning"
      />
      <span v-else class="monitor-row__zero">0</span>
    </td>
    <td class="monitor-row__cell monitor-row__cell--metric" data-label="Overdue">
      <OverdueBadge
        v-if="chatter.overdue_conversations_count > 0"
        :count="chatter.overdue_conversations_count"
      />
      <span v-else class="monitor-row__zero">0</span>
    </td>
    <td class="monitor-row__cell monitor-row__cell--last-seen" data-label="Last seen">
      <span
        class="monitor-row__last-seen"
        :title="chatter.last_seen_at ? formatDateTime(chatter.last_seen_at) : 'Never seen'"
      >
        {{ chatter.last_seen_at ? formatRelativeTime(chatter.last_seen_at) : "Never" }}
      </span>
    </td>
    <td class="monitor-row__cell monitor-row__cell--status" data-label="Status">
      <OverdueBadge
        :count="0"
        :label="rowStatus"
        :tone="rowStatusTone"
        :show-dot="false"
      />
    </td>
  </tr>
</template>

<style scoped>
.monitor-row {
  transition: background var(--transition-fast);
}

.monitor-row--overdue {
  background: color-mix(in srgb, var(--color-danger-soft) 28%, transparent);
}

.monitor-row--overdue .monitor-row__cell--chatter {
  box-shadow: inset 2px 0 0 color-mix(in srgb, var(--color-danger) 42%, transparent);
}

.monitor-row--waiting:not(.monitor-row--overdue) {
  background: color-mix(in srgb, var(--color-warning-soft) 22%, transparent);
}

.monitor-row--waiting:not(.monitor-row--overdue) .monitor-row__cell--chatter {
  box-shadow: inset 2px 0 0 color-mix(in srgb, var(--color-warning) 42%, transparent);
}

.monitor-row--offline .monitor-row__name,
.monitor-row--offline .monitor-row__metric,
.monitor-row--offline .monitor-row__last-seen {
  color: var(--color-text-muted);
}

.monitor-row__cell {
  padding: 0.75rem 1rem;
  vertical-align: middle;
}

.monitor-row__cell--metric,
.monitor-row__cell--status {
  text-align: center;
}

.monitor-row__cell--last-seen {
  text-align: left;
}

.monitor-row__chatter {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.monitor-row__avatar {
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  font-size: 0.6875rem;
}

.monitor-row__identity {
  min-width: 0;
  flex: 1;
  line-height: 1.3;
}

.monitor-row__name {
  font-weight: 600;
  font-size: 0.8125rem;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monitor-row__username {
  margin-top: 0.1rem;
  font-size: 0.75rem;
  color: var(--color-text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monitor-row__presence {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 4.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.monitor-row__presence--online {
  color: var(--color-text);
}

.monitor-row__presence--offline {
  color: var(--color-text-soft);
}

.monitor-row__metric {
  display: inline-block;
  min-width: 1.25rem;
  font-size: 0.8125rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-text);
}

.monitor-row__zero {
  display: inline-block;
  min-width: 1.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-soft);
}

.monitor-row__last-seen {
  display: inline-block;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.monitor-row__cell--metric :deep(.overdue-badge),
.monitor-row__cell--status :deep(.overdue-badge) {
  vertical-align: middle;
}

@media (max-width: 768px) {
  .monitor-row {
    display: block;
    padding: var(--space-4);
    border-bottom: 1px solid var(--color-border);
  }

  .monitor-row--overdue .monitor-row__cell--chatter,
  .monitor-row--waiting .monitor-row__cell--chatter {
    box-shadow: none;
  }

  .monitor-row--overdue {
    border-left: 2px solid color-mix(in srgb, var(--color-danger) 42%, transparent);
  }

  .monitor-row--waiting:not(.monitor-row--overdue) {
    border-left: 2px solid color-mix(in srgb, var(--color-warning) 42%, transparent);
  }

  .monitor-row__cell {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-3);
    padding: 0.45rem 0;
    text-align: right;
  }

  .monitor-row__cell--chatter {
    flex-direction: column;
    align-items: stretch;
    text-align: left;
  }

  .monitor-row__cell::before {
    content: attr(data-label);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-soft);
    flex-shrink: 0;
    text-align: left;
  }

  .monitor-row__cell--chatter::before {
    margin-bottom: var(--space-2);
  }

  .monitor-row__cell:first-child {
    padding-top: 0;
  }

  .monitor-row__cell:last-child {
    padding-bottom: 0;
  }

  .monitor-row__chatter {
    width: 100%;
  }
}
</style>
