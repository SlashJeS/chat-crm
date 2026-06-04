<template>
  <span v-if="overdue" class="overdue-badge">Overdue</span>
</template>

<script setup lang="ts">
defineProps<{
  overdue: boolean;
}>();
</script>

<style scoped>
.overdue-badge {
  display: inline-block;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: #fdecea;
  color: #c0392b;
  font-size: 0.7rem;
  font-weight: 600;
}
</style>
