<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import ErrorState from "@/components/common/ErrorState.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import MonitorTable from "@/components/monitor/MonitorTable.vue";
import AppLayout from "@/components/common/AppLayout.vue";
import { useMonitorSocket } from "@/composables/useMonitorSocket";
import { useMonitorStore } from "@/stores/monitor.store";
import { formatDateTime } from "@/utils/date";
import { formatThresholdSeconds, getConnectionTone, getRealtimeConnectionLabel } from "@/utils/status";

const monitorStore = useMonitorStore();
const monitorSocket = useMonitorSocket();
const refreshLoading = ref(false);

const lastUpdatedLabel = computed(() => {
  if (!monitorStore.lastUpdatedAt) {
    return "Not updated yet";
  }
  return formatDateTime(monitorStore.lastUpdatedAt);
});

const slaLabel = computed(() => {
  const seconds = monitorStore.snapshot?.sla_seconds;
  if (seconds === undefined) {
    return "—";
  }
  return formatThresholdSeconds(seconds);
});

const presenceGraceLabel = computed(() => {
  const seconds = monitorStore.snapshot?.presence_grace_seconds;
  if (seconds === undefined) {
    return "—";
  }
  return formatThresholdSeconds(seconds);
});

const connectionTone = computed(() =>
  getConnectionTone(monitorSocket.connectionState.value, Boolean(monitorSocket.lastError.value)),
);

const connectionPillClass = computed(() => `status-pill--${connectionTone.value}`);

const showWsWarning = computed(
  () =>
    !monitorSocket.isConnected.value &&
    Boolean(monitorStore.snapshot) &&
    !monitorStore.error,
);

const hasOverdue = computed(() => monitorStore.totalOverdueConversations > 0);

async function handleRefresh(): Promise<void> {
  refreshLoading.value = true;
  try {
    await monitorStore.loadSnapshot();
    monitorSocket.refresh();
  } finally {
    refreshLoading.value = false;
  }
}

async function handleRetryLoad(): Promise<void> {
  await monitorStore.loadSnapshot();
}

onMounted(async () => {
  await monitorStore.loadSnapshot();
  monitorSocket.connect();
});

onUnmounted(() => {
  monitorSocket.disconnect();
  monitorStore.clear();
});
</script>

<template>
  <AppLayout>
    <div class="monitor-page page">
      <header class="monitor-page__header page-header">
        <div>
          <h1 class="page-title">Teamlead Monitor</h1>
          <p class="page-subtitle">
            Track chatter workload, presence, and overdue fan replies in realtime
          </p>
          <div class="monitor-page__meta meta-row">
            <span class="status-pill" :class="connectionPillClass">
              <span class="status-dot" aria-hidden="true" />
              {{ getRealtimeConnectionLabel(monitorSocket.connectionState.value) }}
            </span>
            <span class="monitor-page__updated muted">
              Last updated: <time>{{ lastUpdatedLabel }}</time>
            </span>
            <span class="monitor-page__sla muted">
              SLA {{ slaLabel }} · Grace {{ presenceGraceLabel }}
            </span>
            <span v-if="monitorSocket.lastError.value" class="monitor-page__error-text" role="alert">
              {{ monitorSocket.lastError.value }}
            </span>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-secondary monitor-page__refresh"
          :disabled="refreshLoading"
          aria-label="Refresh monitor snapshot"
          @click="handleRefresh"
        >
          {{ refreshLoading ? "Refreshing…" : "Refresh" }}
        </button>
      </header>

      <ErrorState
        v-if="monitorStore.error && !monitorStore.snapshot"
        title="Could not load monitor snapshot"
        :message="monitorStore.error"
        retry-label="Retry"
        @retry="handleRetryLoad"
      />

      <LoadingState
        v-else-if="monitorStore.isLoading && !monitorStore.snapshot"
        message="Loading monitor snapshot…"
      />

      <template v-else-if="monitorStore.snapshot">
        <div v-if="showWsWarning" class="monitor-page__warning" role="status">
          <span class="status-dot status-dot--warning" aria-hidden="true" />
          Realtime disconnected. Manual refresh is still available.
        </div>

        <section class="monitor-page__cards" aria-label="Summary metrics">
          <article class="kpi-card kpi-card--success">
            <div class="kpi-card__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2" />
                <path d="M4 20 C4 16 7.5 13 12 13 C16.5 13 20 16 20 20" stroke="currentColor" stroke-width="2" />
              </svg>
            </div>
            <div class="kpi-card__body">
              <span class="kpi-card__label">Online chatters</span>
              <strong class="kpi-card__value">{{ monitorStore.onlineChattersCount }}</strong>
              <span class="kpi-card__hint muted">Currently connected and available</span>
            </div>
          </article>

          <article class="kpi-card kpi-card--primary">
            <div class="kpi-card__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="5" width="18" height="14" rx="3" stroke="currentColor" stroke-width="2" />
                <path d="M8 19 L12 15 L8 15 Z" fill="currentColor" opacity="0.35" />
              </svg>
            </div>
            <div class="kpi-card__body">
              <span class="kpi-card__label">Active dialogs</span>
              <strong class="kpi-card__value">{{ monitorStore.totalActiveConversations }}</strong>
              <span class="kpi-card__hint muted">Open dialogs across all chatters</span>
            </div>
          </article>

          <article class="kpi-card kpi-card--warning">
            <div class="kpi-card__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
                <path d="M12 7 V12 L15 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </div>
            <div class="kpi-card__body">
              <span class="kpi-card__label">Fans waiting</span>
              <strong class="kpi-card__value">{{ monitorStore.totalWaitingConversations }}</strong>
              <span class="kpi-card__hint muted">Awaiting a chatter reply</span>
            </div>
          </article>

          <article class="kpi-card" :class="{ 'kpi-card--danger': hasOverdue }">
            <div class="kpi-card__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3 L22 20 H2 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
                <path d="M12 9 V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                <circle cx="12" cy="17" r="1" fill="currentColor" />
              </svg>
            </div>
            <div class="kpi-card__body">
              <span class="kpi-card__label">Overdue fans</span>
              <strong class="kpi-card__value">{{ monitorStore.totalOverdueConversations }}</strong>
              <span class="kpi-card__hint muted">Past SLA threshold — needs attention</span>
            </div>
          </article>
        </section>

        <MonitorTable :chatters="monitorStore.chatters" />
      </template>

      <div v-else class="monitor-page__empty panel empty-state">
        <div class="empty-state__icon" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="10" width="36" height="28" rx="6" stroke="currentColor" stroke-width="2" />
            <path d="M14 22 H34 M14 28 H26" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </div>
        <p class="empty-state__title">No monitor data available</p>
        <button type="button" class="btn btn-secondary" @click="handleRetryLoad">Load snapshot</button>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.monitor-page {
  overflow-x: hidden;
}

.monitor-page__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.monitor-page__sla {
  font-size: 0.8125rem;
}

.monitor-page__refresh {
  flex-shrink: 0;
}

.monitor-page__updated {
  font-size: 0.82rem;
}

.monitor-page__error-text {
  font-size: 0.82rem;
  color: var(--color-danger);
  font-weight: 600;
}

.monitor-page__warning {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
  padding: var(--space-2) var(--space-3);
  border: 1px solid color-mix(in srgb, var(--color-warning) 25%, var(--color-border));
  border-radius: var(--radius-md);
  background: var(--color-warning-soft);
  color: var(--color-text-muted);
  font-size: 0.8125rem;
  font-weight: 500;
}

.monitor-page__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}

.monitor-page__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

@media (max-width: 640px) {
  .monitor-page__header {
    flex-direction: column;
  }

  .monitor-page__refresh {
    width: 100%;
  }
}
</style>
