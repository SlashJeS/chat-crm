<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string;
    size?: "sm" | "md" | "lg";
  }>(),
  {
    message: "Loading...",
    size: "md",
  },
);
</script>

<template>
  <div
    class="loading-state"
    :class="`loading-state--${size}`"
    role="status"
    aria-live="polite"
    :aria-label="message"
  >
    <span class="loading-state__spinner" aria-hidden="true" />
    <span class="loading-state__message">{{ message }}</span>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  text-align: center;
  color: var(--color-text-muted);
}

.loading-state--sm {
  padding: var(--space-4);
}

.loading-state--md {
  padding: var(--space-6);
}

.loading-state--lg {
  padding: var(--space-8);
}

.loading-state__spinner {
  border-radius: 50%;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  animation: spin 0.75s linear infinite;
}

.loading-state--sm .loading-state__spinner {
  width: 1rem;
  height: 1rem;
}

.loading-state--md .loading-state__spinner {
  width: 1.35rem;
  height: 1.35rem;
}

.loading-state--lg .loading-state__spinner {
  width: 1.75rem;
  height: 1.75rem;
}

.loading-state__message {
  font-size: 0.9rem;
  font-weight: 500;
}

.loading-state--sm .loading-state__message {
  font-size: 0.8rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .loading-state__spinner {
    animation: pulse 1.2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.45;
    }
  }
}
</style>
