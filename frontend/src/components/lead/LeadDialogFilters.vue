<script setup lang="ts">
import { ref, watch } from "vue";

import { useLeadStore } from "@/stores/lead.store";

const leadStore = useLeadStore();
const searchInput = ref(leadStore.filters.search ?? "");

let searchTimer: ReturnType<typeof setTimeout> | null = null;

function applyFilters(partial: Parameters<typeof leadStore.setFilters>[0]): void {
  leadStore.setFilters(partial);
  void leadStore.loadConversations();
}

function onSearchInput(): void {
  if (searchTimer) {
    clearTimeout(searchTimer);
  }
  searchTimer = setTimeout(() => {
    applyFilters({ search: searchInput.value });
  }, 300);
}

function onSearchKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter") {
    if (searchTimer) {
      clearTimeout(searchTimer);
    }
    applyFilters({ search: searchInput.value });
  }
}

function onStatusChange(event: Event): void {
  const value = (event.target as HTMLSelectElement).value as "" | "ACTIVE" | "CLOSED";
  applyFilters({ status: value });
}

function onChatterChange(event: Event): void {
  const value = (event.target as HTMLSelectElement).value;
  applyFilters({
    assigned_chatter_id: value === "" ? "" : Number(value),
  });
}

function clearFilters(): void {
  searchInput.value = "";
  applyFilters({
    search: "",
    status: "",
    assigned_chatter_id: "",
  });
}

watch(
  () => leadStore.filters.search,
  (value) => {
    if (value !== searchInput.value) {
      searchInput.value = value ?? "";
    }
  },
);
</script>

<template>
  <div class="lead-filters panel">
    <div class="lead-filters__row">
      <div class="form-group lead-filters__search">
        <label class="form-label" for="lead-search">Search</label>
        <input
          id="lead-search"
          v-model="searchInput"
          class="input"
          type="search"
          placeholder="Search fan name or external ID"
          @input="onSearchInput"
          @keydown="onSearchKeydown"
        />
      </div>

      <div class="form-group lead-filters__field">
        <label class="form-label" for="lead-status">Status</label>
        <select
          id="lead-status"
          class="input"
          :value="leadStore.filters.status ?? ''"
          @change="onStatusChange"
        >
          <option value="">All</option>
          <option value="ACTIVE">Active</option>
          <option value="CLOSED">Closed</option>
        </select>
      </div>

      <div class="form-group lead-filters__field">
        <label class="form-label" for="lead-chatter">Assigned chatter</label>
        <select
          id="lead-chatter"
          class="input"
          :value="leadStore.filters.assigned_chatter_id ?? ''"
          @change="onChatterChange"
        >
          <option value="">All chatters</option>
          <option v-for="chatter in leadStore.workload" :key="chatter.id" :value="chatter.id">
            {{ chatter.display_name }}
          </option>
        </select>
      </div>

      <button type="button" class="btn btn-ghost lead-filters__clear" @click="clearFilters">
        Clear filters
      </button>
    </div>
  </div>
</template>

<style scoped>
.lead-filters {
  padding: var(--space-3) var(--space-4);
}

.lead-filters__row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: var(--space-3);
}

.lead-filters__search {
  flex: 1 1 minmax(220px, 1fr);
  min-width: 0;
}

.lead-filters__field {
  flex: 0 1 160px;
  min-width: 140px;
}

.lead-filters__clear {
  flex-shrink: 0;
  margin-bottom: 0.1rem;
}
</style>
