<script setup lang="ts">
import { computed } from "vue";

import { getIconSvg, type IconName } from "@/utils/icons";

const props = withDefaults(
  defineProps<{
    name: IconName | string;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
    decorative?: boolean;
    label?: string;
  }>(),
  {
    size: "md",
    decorative: true,
  },
);

const markup = computed(() => getIconSvg(props.name));
</script>

<template>
  <span
    class="app-icon"
    :class="`app-icon--${size}`"
    :aria-hidden="decorative ? 'true' : undefined"
    :role="decorative ? undefined : 'img'"
    :aria-label="decorative ? undefined : label"
    v-html="markup"
  />
</template>

<style scoped>
.app-icon {
  display: inline-flex;
  flex-shrink: 0;
  vertical-align: middle;
  line-height: 0;
}

.app-icon :deep(svg) {
  display: block;
  width: 100%;
  height: 100%;
}

.app-icon--xs {
  width: 0.75rem;
  height: 0.75rem;
}

.app-icon--sm {
  width: 1rem;
  height: 1rem;
}

.app-icon--md {
  width: 1.25rem;
  height: 1.25rem;
}

.app-icon--lg {
  width: 1.5rem;
  height: 1.5rem;
}

.app-icon--xl {
  width: 3rem;
  height: 3rem;
}
</style>
