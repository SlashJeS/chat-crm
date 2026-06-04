<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import AppLayout from "@/components/common/AppLayout.vue";
import ErrorState from "@/components/common/ErrorState.vue";
import AssignmentPanel from "@/components/lead/AssignmentPanel.vue";
import LeadDialogFilters from "@/components/lead/LeadDialogFilters.vue";
import LeadDialogTable from "@/components/lead/LeadDialogTable.vue";
import { useLeadStore } from "@/stores/lead.store";

const leadStore = useLeadStore();
const refreshLoading = ref(false);

const onlineChattersCount = computed(
  () => leadStore.workload.filter((chatter) => chatter.is_online).length,
);

async function loadAll(): Promise<void> {
  await Promise.all([leadStore.loadConversations(), leadStore.loadWorkload()]);
}

async function handleRefresh(): Promise<void> {
  refreshLoading.value = true;
  try {
    await loadAll();
  } finally {
    refreshLoading.value = false;
  }
}

onMounted(async () => {
  await loadAll();
});

onUnmounted(() => {
  leadStore.clear();
});
</script>

<template>
  <AppLayout>
    <div class="lead-page page">
      <header class="lead-page__header page-header">
        <div>
          <h1 class="page-title">Dialog Assignment</h1>
          <p class="page-subtitle">
            Review fan dialogs and assign them to available chatters
          </p>
        </div>
        <button
          type="button"
          class="btn btn-secondary lead-page__refresh"
          :disabled="refreshLoading"
          aria-label="Refresh dialogs and workload"
          @click="handleRefresh"
        >
          {{ refreshLoading ? "Refreshing…" : "Refresh" }}
        </button>
      </header>

      <section class="lead-page__cards" aria-label="Summary metrics">
        <article class="kpi-card kpi-card--primary">
          <div class="kpi-card__body">
            <span class="kpi-card__label">Total dialogs</span>
            <strong class="kpi-card__value">{{ leadStore.count }}</strong>
          </div>
        </article>
        <article class="kpi-card kpi-card--warning">
          <div class="kpi-card__body">
            <span class="kpi-card__label">Waiting fans</span>
            <strong class="kpi-card__value">{{ leadStore.waitingDialogsCount }}</strong>
          </div>
        </article>
        <article class="kpi-card kpi-card--danger">
          <div class="kpi-card__body">
            <span class="kpi-card__label">Overdue</span>
            <strong class="kpi-card__value">{{ leadStore.overdueDialogsCount }}</strong>
          </div>
        </article>
        <article class="kpi-card kpi-card--success">
          <div class="kpi-card__body">
            <span class="kpi-card__label">Online chatters</span>
            <strong class="kpi-card__value">{{ onlineChattersCount }}</strong>
          </div>
        </article>
      </section>

      <ErrorState
        v-if="leadStore.error && !leadStore.conversations.length"
        title="Could not load dialogs"
        :message="leadStore.error"
        retry-label="Retry"
        @retry="loadAll"
      />

      <template v-else>
        <LeadDialogFilters />

        <div class="lead-page__content">
          <div class="lead-page__table-panel">
            <LeadDialogTable />
          </div>
          <AssignmentPanel />
        </div>
      </template>
    </div>
  </AppLayout>
</template>

<style scoped>
.lead-page {
  overflow-x: hidden;
  min-width: 0;
}

.lead-page__header {
  flex-shrink: 0;
}

.lead-page__refresh {
  flex-shrink: 0;
}

.lead-page__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-3);
}

.lead-page__content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: var(--space-4);
  align-items: start;
  min-width: 0;
}

.lead-page__table-panel {
  min-width: 0;
}

@media (max-width: 1100px) {
  .lead-page__content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .lead-page__header {
    flex-direction: column;
  }

  .lead-page__refresh {
    width: 100%;
  }
}
</style>
