<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
  send: [payload: { text: string; ppvPrice: string }];
}>();

const text = ref("");
const price = ref("19.99");

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      text.value = "";
      price.value = "19.99";
    }
  },
);

function handleSubmit(): void {
  const trimmedText = text.value.trim();
  const trimmedPrice = price.value.trim();
  if (!trimmedText || !trimmedPrice) {
    return;
  }
  emit("send", { text: trimmedText, ppvPrice: trimmedPrice });
}
</script>

<template>
  <div v-if="open" class="ppv-modal">
    <div class="ppv-modal__backdrop" @click="emit('close')" />
    <div class="ppv-modal__panel">
      <h3>Send PPV Message</h3>
      <label>
        Message
        <textarea v-model="text" rows="3" />
      </label>
      <label>
        Price
        <input v-model="price" type="number" min="0.01" step="0.01" />
      </label>
      <div class="ppv-modal__actions">
        <button type="button" @click="emit('close')">Cancel</button>
        <button type="button" @click="handleSubmit">Send PPV</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ppv-modal {
  position: fixed;
  inset: 0;
  z-index: 100;
}

.ppv-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
}

.ppv-modal__panel {
  position: relative;
  width: min(420px, calc(100% - 2rem));
  margin: 10vh auto 0;
  padding: 1rem;
  background: #fff;
  border-radius: 0.5rem;
}

.ppv-modal__panel label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.75rem;
}

.ppv-modal__panel textarea,
.ppv-modal__panel input {
  padding: 0.5rem;
}

.ppv-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}
</style>
