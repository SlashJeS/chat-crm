<template>
  <span
    class="overdue-badge"
    :class="{ 'overdue-badge--alert': count > 0, 'overdue-badge--neutral': count === 0 }"
  >
    {{ count > 0 ? `${count} overdue` : "OK" }}
  </span>
</template>

<script setup lang="ts">
defineProps<{
  count: number;
}>();
</script>

<style scoped>
.overdue-badge {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.overdue-badge--alert {
  background: #fdecea;
  color: #c0392b;
}

.overdue-badge--neutral {
  background: #eef2f7;
  color: #64748b;
}
</style>
