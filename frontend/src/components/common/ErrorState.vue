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
  <div class="error-state section-card" role="alert">
    <div class="error-state__icon" aria-hidden="true">!</div>
    <div class="error-state__body">
      <strong v-if="title" class="error-state__title">{{ title }}</strong>
      <p class="error-state__message">{{ message }}</p>
      <button
        v-if="retryLabel"
        type="button"
        class="btn btn-danger error-state__retry"
        @click="emit('retry')"
      >
        {{ retryLabel }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.error-state {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
  border-color: color-mix(in srgb, var(--color-danger) 35%, var(--color-border));
  background: color-mix(in srgb, var(--color-danger-soft) 80%, var(--color-surface));
}

.error-state__icon {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  font-weight: 800;
  flex-shrink: 0;
}

.error-state__body {
  min-width: 0;
}

.error-state__title {
  display: block;
  margin-bottom: var(--space-2);
  font-size: 0.95rem;
  color: var(--color-text);
}

.error-state__message {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.error-state__retry {
  margin-top: var(--space-4);
}
</style>
