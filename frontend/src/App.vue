<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";

const route = useRoute();

const transitionName = computed(() => {
  if (route.path === "/login") {
    return "page-fade";
  }
  return "page-slide";
});

const isFullHeightPage = computed(() => route.path === "/chatter");
</script>

<template>
  <div class="app-root" :class="{ 'app-root--full-height': isFullHeightPage }">
    <RouterView v-slot="{ Component }">
      <Transition :name="transitionName" mode="out-in">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}

.app-root--full-height {
  min-height: 100vh;
}

@media (min-width: 901px) {
  .app-root--full-height {
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
  }
}

.page-fade-enter-active,
.page-fade-leave-active,
.page-slide-enter-active,
.page-slide-leave-active {
  transition:
    opacity var(--transition-normal),
    transform var(--transition-normal);
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
