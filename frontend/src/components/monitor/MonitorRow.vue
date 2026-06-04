<script setup lang="ts">
import OverdueBadge from "@/components/monitor/OverdueBadge.vue";
import type { MonitorChatter } from "@/types/monitor";
import { formatDateTime, formatRelativeTime } from "@/utils/date";

defineProps<{
  chatter: MonitorChatter;
}>();
</script>

<template>
  <tr
    class="monitor-row"
    :class="{
      'monitor-row--overdue': chatter.overdue_conversations_count > 0,
      'monitor-row--waiting':
        chatter.overdue_conversations_count === 0 && chatter.waiting_conversations_count > 0,
      'monitor-row--offline': !chatter.is_online,
    }"
  >
    <td>
      <div class="monitor-row__name">{{ chatter.display_name }}</div>
      <div class="monitor-row__username">@{{ chatter.username }}</div>
    </td>
    <td>
      <span
        class="monitor-row__status"
        :class="chatter.is_online ? 'monitor-row__status--online' : 'monitor-row__status--offline'"
      >
        {{ chatter.is_online ? "Online" : "Offline" }}
      </span>
    </td>
    <td>{{ chatter.active_conversations_count }}</td>
    <td>{{ chatter.waiting_conversations_count }}</td>
    <td>
      <OverdueBadge :count="chatter.overdue_conversations_count" />
    </td>
    <td>
      <span
        class="monitor-row__last-seen"
        :title="formatDateTime(chatter.last_seen_at)"
      >
        {{ chatter.last_seen_at ? formatRelativeTime(chatter.last_seen_at) : "Never" }}
      </span>
    </td>
  </tr>
</template>

<style scoped>
.monitor-row--overdue {
  background: #fff1f0;
}

.monitor-row--waiting:not(.monitor-row--overdue) {
  background: #fffbeb;
}

.monitor-row--offline {
  color: #64748b;
}

.monitor-row__name {
  font-weight: 600;
}

.monitor-row__username {
  font-size: 0.85rem;
  color: #64748b;
}

.monitor-row__status {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.monitor-row__status--online {
  background: #dcfce7;
  color: #15803d;
}

.monitor-row__status--offline {
  background: #e2e8f0;
  color: #64748b;
}

.monitor-row__last-seen {
  font-size: 0.85rem;
  color: #475569;
}
</style>
