<script setup lang="ts">
import { computed } from "vue";

import type { StatusTone } from "@/utils/status";

const props = withDefaults(
  defineProps<{
    count: number;
    label?: string;
    tone?: StatusTone;
    showDot?: boolean;
  }>(),
  {
    showDot: undefined,
  },
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

const showDotResolved = computed(() => {
  if (props.showDot !== undefined) {
    return props.showDot;
  }
  return (
    props.count > 0 &&
    (effectiveTone.value === "danger" || effectiveTone.value === "warning")
  );
});
</script>

<template>
  <span
    class="overdue-badge"
    :class="`overdue-badge--${effectiveTone}`"
  >
    <span
      v-if="showDotResolved"
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
  justify-content: center;
  gap: 0.35rem;
  min-height: 1.5rem;
  min-width: 2.5rem;
  padding: 0 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: 0.01em;
  white-space: nowrap;
  border: 1px solid transparent;
}

.overdue-badge--danger {
  background: var(--color-danger-soft);
  color: var(--color-danger);
  border-color: color-mix(in srgb, var(--color-danger) 18%, transparent);
}

.overdue-badge--warning {
  background: var(--color-warning-soft);
  color: var(--color-warning);
  border-color: color-mix(in srgb, var(--color-warning) 18%, transparent);
}

.overdue-badge--success {
  background: var(--color-success-soft);
  color: var(--color-success);
  border-color: color-mix(in srgb, var(--color-success) 18%, transparent);
}

.overdue-badge--muted {
  background: var(--color-bg-soft);
  color: var(--color-text-soft);
  border-color: var(--color-border);
}
</style>
