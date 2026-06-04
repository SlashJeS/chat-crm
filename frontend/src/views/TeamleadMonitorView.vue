<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import ErrorState from "@/components/common/ErrorState.vue";
import LoadingState from "@/components/common/LoadingState.vue";
import MonitorTable from "@/components/monitor/MonitorTable.vue";
import AppLayout from "@/components/common/AppLayout.vue";
import { useMonitorSocket } from "@/composables/useMonitorSocket";
import { useMonitorStore } from "@/stores/monitor.store";
import { formatDateTime } from "@/utils/date";

const monitorStore = useMonitorStore();
const monitorSocket = useMonitorSocket();
const refreshLoading = ref(false);

const lastUpdatedLabel = computed(() => {
  if (!monitorStore.lastUpdatedAt) {
    return "Not updated yet";
  }
  return formatDateTime(monitorStore.lastUpdatedAt);
});

const slaSeconds = computed(() => monitorStore.snapshot?.sla_seconds ?? "-");

const connectionStatusClass = computed(() => {
  const state = monitorSocket.connectionState.value;
  if (state === "connected") {
    return "monitor-page__status--connected";
  }
  if (state === "reconnecting" || state === "connecting") {
    return "monitor-page__status--reconnecting";
  }
  if (monitorSocket.lastError.value) {
    return "monitor-page__status--error";
  }
  return "monitor-page__status--disconnected";
});

const showWsWarning = computed(
  () =>
    !monitorSocket.isConnected.value &&
    Boolean(monitorStore.snapshot) &&
    !monitorStore.error,
);

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
    <div class="monitor-page">
      <header class="monitor-page__header">
        <div>
          <h1>Teamlead Monitor</h1>
          <p class="monitor-page__meta">
            Connection:
            <span class="monitor-page__status" :class="connectionStatusClass">
              {{ monitorSocket.connectionLabel.value }}
            </span>
            <span v-if="monitorSocket.lastError.value" class="monitor-page__status-error">
              · {{ monitorSocket.lastError.value }}
            </span>
            · Last updated: {{ lastUpdatedLabel }}
          </p>
        </div>
        <button
          type="button"
          class="monitor-page__refresh"
          :disabled="refreshLoading"
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
        message="Loading monitor snapshot..."
      />

      <template v-else-if="monitorStore.snapshot">
        <p v-if="showWsWarning" class="monitor-page__warning">
          Live updates are unavailable. REST refresh still works — use the Refresh button above.
        </p>

        <section class="monitor-page__cards">
          <article class="monitor-card">
            <span class="monitor-card__label">Online chatters</span>
            <strong class="monitor-card__value">{{ monitorStore.onlineChattersCount }}</strong>
          </article>
          <article class="monitor-card">
            <span class="monitor-card__label">Active conversations</span>
            <strong class="monitor-card__value">{{ monitorStore.totalActiveConversations }}</strong>
          </article>
          <article class="monitor-card monitor-card--waiting">
            <span class="monitor-card__label">Fans waiting</span>
            <strong class="monitor-card__value">{{ monitorStore.totalWaitingConversations }}</strong>
          </article>
          <article class="monitor-card monitor-card--warning">
            <span class="monitor-card__label">Overdue fans</span>
            <strong class="monitor-card__value">{{ monitorStore.totalOverdueConversations }}</strong>
          </article>
          <article class="monitor-card">
            <span class="monitor-card__label">SLA seconds</span>
            <strong class="monitor-card__value">{{ slaSeconds }}</strong>
          </article>
        </section>

        <MonitorTable :chatters="monitorStore.chatters" />
      </template>

      <div v-else class="monitor-page__empty">
        <p>No monitor data available</p>
        <button type="button" @click="handleRetryLoad">Load snapshot</button>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.monitor-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.monitor-page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.monitor-page__header h1 {
  margin: 0;
  font-size: 1.35rem;
}

.monitor-page__meta {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 0.9rem;
}

.monitor-page__status {
  font-weight: 600;
}

.monitor-page__status--connected {
  color: #15803d;
}

.monitor-page__status--reconnecting {
  color: #b45309;
}

.monitor-page__status--disconnected {
  color: #64748b;
}

.monitor-page__status--error {
  color: #c0392b;
}

.monitor-page__status-error {
  color: #c0392b;
}

.monitor-page__refresh {
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  font-weight: 600;
  cursor: pointer;
}

.monitor-page__refresh:hover:not(:disabled) {
  background: #f8fafc;
}

.monitor-page__warning {
  margin: 0;
  padding: 0.75rem 1rem;
  border: 1px solid #fde68a;
  border-radius: 0.375rem;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.9rem;
}

.monitor-page__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.75rem;
}

.monitor-card {
  padding: 1rem 1.1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  background: #fff;
}

.monitor-card--waiting {
  border-color: #fde68a;
  background: #fffbeb;
}

.monitor-card--warning {
  border-color: #fecaca;
  background: #fff1f0;
}

.monitor-card__label {
  display: block;
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.monitor-card__value {
  display: block;
  margin-top: 0.35rem;
  font-size: 1.6rem;
  color: #0f172a;
}

.monitor-page__empty {
  padding: 2.5rem;
  text-align: center;
  color: #64748b;
  border: 1px dashed #cbd5e1;
  border-radius: 0.5rem;
  background: #fff;
}

.monitor-page__empty p {
  margin: 0 0 0.75rem;
  font-weight: 600;
  color: #475569;
}

.monitor-page__empty button {
  padding: 0.45rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  cursor: pointer;
}
</style>
