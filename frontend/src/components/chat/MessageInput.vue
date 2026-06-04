<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  disabled?: boolean;
  socketError?: string | null;
}>();

const emit = defineEmits<{
  send: [text: string];
}>();

const text = ref("");
const localError = ref<string | null>(null);

const canSend = computed(() => !props.disabled && text.value.trim().length > 0);

function handleSubmit(): void {
  const value = text.value.trim();
  if (!value || props.disabled) {
    return;
  }
  localError.value = null;
  emit("send", value);
  text.value = "";
}

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSubmit();
  }
}

function setError(message: string): void {
  localError.value = message;
}

defineExpose({ setError });
</script>

<template>
  <form class="message-input" @submit.prevent="handleSubmit">
    <textarea
      v-model="text"
      rows="2"
      placeholder="Type a message… Enter to send, Shift+Enter for newline"
      :disabled="disabled"
      @keydown="handleKeydown"
    />
    <div class="message-input__footer">
      <p v-if="localError || socketError" class="message-input__error">
        {{ localError || socketError }}
      </p>
      <p v-else-if="disabled" class="message-input__hint">
        Messaging is unavailable while disconnected.
      </p>
      <button type="submit" class="message-input__send" :disabled="!canSend">
        Send
      </button>
    </div>
  </form>
</template>

<style scoped>
.message-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

.message-input textarea {
  width: 100%;
  min-height: 3.5rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  resize: vertical;
}

.message-input textarea:focus {
  outline: 2px solid #93c5fd;
  border-color: #60a5fa;
}

.message-input__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.message-input__send {
  padding: 0.45rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

.message-input__send:hover:not(:disabled) {
  background: #1d4ed8;
}

.message-input__error {
  margin: 0;
  color: #c0392b;
  font-size: 0.85rem;
}

.message-input__hint {
  margin: 0;
  color: #64748b;
  font-size: 0.85rem;
}
</style>
