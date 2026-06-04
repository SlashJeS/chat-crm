<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  close: [];
  send: [payload: { text: string; ppvPrice: string }];
}>();

const text = ref("");
const price = ref("19.99");
const validationError = ref<string | null>(null);

function resetForm(): void {
  text.value = "";
  price.value = "19.99";
  validationError.value = null;
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      resetForm();
    }
  },
);

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && props.open) {
    emit("close");
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});

function handleSubmit(): void {
  const trimmedText = text.value.trim();
  const trimmedPrice = price.value.trim();
  const numericPrice = Number(trimmedPrice);

  if (!trimmedText) {
    validationError.value = "Message text is required.";
    return;
  }
  if (!trimmedPrice || Number.isNaN(numericPrice) || numericPrice <= 0) {
    validationError.value = "Price must be greater than 0.";
    return;
  }

  validationError.value = null;
  emit("send", { text: trimmedText, ppvPrice: trimmedPrice });
  resetForm();
  emit("close");
}
</script>

<template>
  <div v-if="open" class="ppv-modal">
    <div class="ppv-modal__backdrop" @click="emit('close')" />
    <div class="ppv-modal__panel" role="dialog" aria-modal="true" aria-labelledby="ppv-modal-title">
      <h3 id="ppv-modal-title">Send PPV Message</h3>
      <p class="ppv-modal__subtitle">Paid content message with a custom price.</p>
      <label class="ppv-modal__field">
        <span>Message</span>
        <textarea v-model="text" rows="3" placeholder="Describe the PPV content..." />
      </label>
      <label class="ppv-modal__field">
        <span>Price (USD)</span>
        <input v-model="price" type="number" min="0.01" step="0.01" placeholder="19.99" />
      </label>
      <p v-if="validationError" class="ppv-modal__error">{{ validationError }}</p>
      <div class="ppv-modal__actions">
        <button type="button" class="ppv-modal__cancel" @click="emit('close')">Cancel</button>
        <button
          type="button"
          class="ppv-modal__submit"
          :disabled="disabled"
          @click="handleSubmit"
        >
          Send PPV
        </button>
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
  background: rgba(15, 23, 42, 0.45);
}

.ppv-modal__panel {
  position: relative;
  width: min(420px, calc(100% - 2rem));
  margin: 10vh auto 0;
  padding: 1.25rem;
  background: #fff;
  border-radius: 0.75rem;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.15);
}

.ppv-modal__panel h3 {
  margin: 0;
}

.ppv-modal__subtitle {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 0.85rem;
}

.ppv-modal__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 0.85rem;
  font-size: 0.9rem;
  color: #334155;
}

.ppv-modal__field textarea,
.ppv-modal__field input {
  padding: 0.55rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
}

.ppv-modal__error {
  margin: 0.75rem 0 0;
  color: #c0392b;
  font-size: 0.85rem;
}

.ppv-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.ppv-modal__cancel {
  padding: 0.45rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  background: #fff;
  cursor: pointer;
}

.ppv-modal__submit {
  padding: 0.45rem 0.85rem;
  border: none;
  border-radius: 0.375rem;
  background: #7c3aed;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.ppv-modal__submit:hover:not(:disabled) {
  background: #6d28d9;
}
</style>
