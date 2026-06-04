<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <RouterView />
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: #0f172a;
  background: #f1f5f9;
}

button,
input,
textarea {
  font: inherit;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
