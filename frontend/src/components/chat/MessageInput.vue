<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{
  send: [text: string];
}>();

const text = ref("");
const error = ref<string | null>(null);

defineProps<{
  disabled?: boolean;
  socketError?: string | null;
}>();

function handleSubmit(): void {
  const value = text.value.trim();
  if (!value) {
    return;
  }
  error.value = null;
  emit("send", value);
  text.value = "";
}

function setError(message: string): void {
  error.value = message;
}

defineExpose({ setError });
</script>

<template>
  <form class="message-input" @submit.prevent="handleSubmit">
    <input
      v-model="text"
      type="text"
      placeholder="Type a message..."
      :disabled="disabled"
    />
    <button type="submit" :disabled="disabled || !text.trim()">Send</button>
    <p v-if="error || socketError" class="message-input__error">{{ error || socketError }}</p>
  </form>
</template>

<style scoped>
.message-input {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid #ddd;
}

.message-input input {
  flex: 1;
  min-width: 200px;
  padding: 0.5rem 0.75rem;
}

.message-input button {
  padding: 0.5rem 1rem;
}

.message-input__error {
  width: 100%;
  margin: 0;
  color: #c0392b;
  font-size: 0.85rem;
}
</style>
