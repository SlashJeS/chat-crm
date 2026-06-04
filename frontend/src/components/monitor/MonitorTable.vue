<script setup lang="ts">
import { computed } from "vue";

import AppIcon from "@/components/common/AppIcon.vue";
import MonitorRow from "@/components/monitor/MonitorRow.vue";
import type { MonitorChatter } from "@/types/monitor";

const props = defineProps<{
  chatters: MonitorChatter[];
}>();

const totalChatters = computed(() => props.chatters.length);
</script>

<template>
  <section class="monitor-table panel">
    <header class="monitor-table__header">
      <div class="monitor-table__intro">
        <h2 class="monitor-table__title">Chatter workload</h2>
        <p class="monitor-table__subtitle muted">
          {{ totalChatters }} chatter{{ totalChatters === 1 ? "" : "s" }} tracked
        </p>
      </div>
      <div class="monitor-table__legend" aria-label="Status legend">
        <span class="monitor-table__legend-item">
          <span class="status-dot status-dot--success" aria-hidden="true" />
          Healthy
        </span>
        <span class="monitor-table__legend-item">
          <span class="status-dot status-dot--warning" aria-hidden="true" />
          Waiting
        </span>
        <span class="monitor-table__legend-item">
          <span class="status-dot status-dot--danger" aria-hidden="true" />
          Overdue
        </span>
      </div>
    </header>

    <div v-if="!chatters.length" class="monitor-table__empty empty-state">
      <div class="empty-state__icon" aria-hidden="true">
        <AppIcon name="users-empty" size="xl" />
      </div>
      <p class="empty-state__title">No chatters available</p>
      <span class="empty-state__text">Chatters will appear here once they are assigned and active.</span>
    </div>

    <div v-else class="monitor-table__scroll">
      <table class="monitor-table__table">
        <colgroup>
          <col class="monitor-table__col monitor-table__col--chatter" />
          <col class="monitor-table__col monitor-table__col--presence" />
          <col class="monitor-table__col monitor-table__col--metric" />
          <col class="monitor-table__col monitor-table__col--metric" />
          <col class="monitor-table__col monitor-table__col--metric" />
          <col class="monitor-table__col monitor-table__col--last-seen" />
          <col class="monitor-table__col monitor-table__col--status" />
        </colgroup>
        <thead>
          <tr>
            <th scope="col">Chatter</th>
            <th scope="col">Presence</th>
            <th scope="col">Active</th>
            <th scope="col">Waiting</th>
            <th scope="col">Overdue</th>
            <th scope="col">Last seen</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          <MonitorRow v-for="chatter in chatters" :key="chatter.id" :chatter="chatter" />
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.monitor-table {
  padding: 0;
  overflow: hidden;
}

.monitor-table__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.monitor-table__intro {
  min-width: 0;
}

.monitor-table__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
}

.monitor-table__subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.8125rem;
}

.monitor-table__legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  justify-content: flex-end;
  flex-shrink: 0;
}

.monitor-table__legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-soft);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.monitor-table__scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.monitor-table__table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

.monitor-table__col--chatter {
  width: 28%;
}

.monitor-table__col--presence {
  width: 14%;
}

.monitor-table__col--metric {
  width: 13%;
}

.monitor-table__col--last-seen {
  width: 10%;
}

.monitor-table__col--status {
  width: 9%;
}

.monitor-table__table th {
  padding: 0.65rem 1rem;
  background: var(--color-bg-soft);
  border-bottom: 1px solid var(--color-border);
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
}

.monitor-table__table th:nth-child(3),
.monitor-table__table th:nth-child(4),
.monitor-table__table th:nth-child(5),
.monitor-table__table th:nth-child(7) {
  text-align: center;
}

.monitor-table__table tbody tr {
  border-bottom: 1px solid var(--color-border);
}

.monitor-table__table tbody tr:last-child {
  border-bottom: none;
}

.monitor-table__table tbody tr:hover {
  background: var(--color-surface-hover);
}

.monitor-table__empty {
  padding: var(--space-8) var(--space-4);
}

@media (max-width: 768px) {
  .monitor-table__header {
    flex-direction: column;
    align-items: stretch;
  }

  .monitor-table__legend {
    justify-content: flex-start;
  }

  .monitor-table__table thead {
    display: none;
  }

  .monitor-table__table,
  .monitor-table__table tbody,
  .monitor-table__table tr {
    display: block;
  }

  .monitor-table__table colgroup {
    display: none;
  }
}
</style>
