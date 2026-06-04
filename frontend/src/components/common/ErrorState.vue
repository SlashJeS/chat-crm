<script setup lang="ts">
defineProps<{
  title?: string;
  message: string;
  retryLabel?: string;
}>();

const emit = defineEmits<{
  retry: [];
}>();
</script>

<template>
  <div class="error-state">
    <strong v-if="title" class="error-state__title">{{ title }}</strong>
    <p class="error-state__message">{{ message }}</p>
    <button
      v-if="retryLabel"
      type="button"
      class="error-state__retry"
      @click="emit('retry')"
    >
      {{ retryLabel }}
    </button>
  </div>
</template>

<style scoped>
.error-state {
  padding: 1rem 1.25rem;
  border: 1px solid #f5c2c0;
  background: #fdecea;
  color: #c0392b;
  border-radius: 0.5rem;
}

.error-state__title {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.95rem;
}

.error-state__message {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.error-state__retry {
  margin-top: 0.75rem;
  padding: 0.4rem 0.85rem;
  border: 1px solid #c0392b;
  border-radius: 0.375rem;
  background: #fff;
  color: #c0392b;
  cursor: pointer;
  font-size: 0.85rem;
}

.error-state__retry:hover {
  background: #fff5f5;
}
</style>
