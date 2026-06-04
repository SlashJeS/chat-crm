<script setup lang="ts">
import MonitorRow from "@/components/monitor/MonitorRow.vue";
import type { MonitorChatter } from "@/types/monitor";

defineProps<{
  chatters: MonitorChatter[];
}>();
</script>

<template>
  <div class="monitor-table">
    <div v-if="!chatters.length" class="monitor-table__empty">
      <p>No chatters found</p>
      <span>Chatters will appear here once they are assigned and active.</span>
    </div>
    <table v-else>
      <thead>
        <tr>
          <th>Chatter</th>
          <th>Status</th>
          <th>Active dialogs</th>
          <th>Fans waiting</th>
          <th>Overdue</th>
          <th>Last seen</th>
        </tr>
      </thead>
      <tbody>
        <MonitorRow v-for="chatter in chatters" :key="chatter.id" :chatter="chatter" />
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.monitor-table {
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  background: #fff;
}

.monitor-table__empty {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748b;
}

.monitor-table__empty p {
  margin: 0 0 0.35rem;
  font-weight: 600;
  color: #475569;
}

.monitor-table__empty span {
  font-size: 0.85rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

tbody tr:last-child td {
  border-bottom: none;
}

th {
  background: #f8fafc;
  font-size: 0.8rem;
  color: #475569;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
</style>
