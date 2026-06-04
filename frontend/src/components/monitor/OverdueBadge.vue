<script setup lang="ts">
import { computed } from "vue";

import type { StatusTone } from "@/utils/status";

const props = withDefaults(
  defineProps<{
    count: number;
    label?: string;
    tone?: StatusTone;
  }>(),
  {},
);

const displayLabel = computed(() => {
  if (props.label) {
    return props.label;
  }
  if (props.count > 0) {
    return `${props.count} overdue`;
  }
  return "On track";
});

const effectiveTone = computed((): StatusTone => {
  if (props.tone) {
    return props.tone;
  }
  return props.count > 0 ? "danger" : "muted";
});

const showDot = computed(() => effectiveTone.value === "danger" || effectiveTone.value === "warning");
</script>

<template>
  <span
    class="overdue-badge"
    :class="`overdue-badge--${effectiveTone}`"
  >
    <span
      v-if="showDot"
      class="status-dot"
      :class="{
        'status-dot--danger': effectiveTone === 'danger',
        'status-dot--warning': effectiveTone === 'warning',
      }"
      aria-hidden="true"
    />
    {{ displayLabel }}
  </span>
</template>

<style scoped>
.overdue-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-sm);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  border: 1px solid transparent;
}

.overdue-badge--danger {
  background: var(--color-danger-soft);
  color: var(--color-danger);
  border-color: color-mix(in srgb, var(--color-danger) 25%, transparent);
}

.overdue-badge--warning {
  background: var(--color-warning-soft);
  color: var(--color-warning);
  border-color: color-mix(in srgb, var(--color-warning) 25%, transparent);
}

.overdue-badge--success {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.overdue-badge--muted {
  background: var(--color-bg-soft);
  color: var(--color-text-soft);
  border-color: var(--color-border);
}
</style>
