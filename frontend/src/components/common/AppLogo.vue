<script setup lang="ts">
import { computed } from "vue";

import logoFullLight from "@/assets/brand/logo-full-light.svg";
import logoFull from "@/assets/brand/logo-full.svg";
import logoMarkLight from "@/assets/brand/logo-mark-light.svg";
import logoMark from "@/assets/brand/logo-mark.svg";
import { useThemeStore } from "@/stores/theme.store";

const props = withDefaults(
  defineProps<{
    variant?: "mark" | "full";
    size?: "sm" | "md" | "lg";
  }>(),
  {
    variant: "full",
    size: "md",
  },
);

const themeStore = useThemeStore();

const dimensions = computed(() => {
  if (props.variant === "mark") {
    switch (props.size) {
      case "sm":
        return { width: 28, height: 28 };
      case "lg":
        return { width: 48, height: 48 };
      default:
        return { width: 36, height: 36 };
    }
  }
  switch (props.size) {
    case "sm":
      return { width: 140, height: 32 };
    case "lg":
      return { width: 220, height: 48 };
    default:
      return { width: 180, height: 40 };
  }
});

const src = computed(() => {
  const isDark = themeStore.theme === "dark";
  if (props.variant === "mark") {
    return isDark ? logoMark : logoMarkLight;
  }
  return isDark ? logoFull : logoFullLight;
});

const altText = computed(() =>
  props.variant === "mark" ? "CRM Chatters logo mark" : "CRM Chatters",
);
</script>

<template>
  <span class="app-logo-wrap" :style="{ width: `${dimensions.width}px`, height: `${dimensions.height}px` }">
    <img
      :src="src"
      :alt="altText"
      class="app-logo"
      :width="dimensions.width"
      :height="dimensions.height"
      decoding="async"
    />
  </span>
</template>

<style scoped>
.app-logo-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  flex-shrink: 0;
  overflow: hidden;
}

.app-logo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: left center;
}
</style>
