<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";

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
const textRef = ref<HTMLTextAreaElement | null>(null);

function resetForm(): void {
  text.value = "";
  price.value = "19.99";
  validationError.value = null;
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      resetForm();
      await nextTick();
      textRef.value?.focus();
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
    <div class="ppv-modal__backdrop" aria-hidden="true" @click="emit('close')" />
    <div
      class="ppv-modal__panel panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="ppv-modal-title"
    >
      <h3 id="ppv-modal-title" class="ppv-modal__title">Send PPV message</h3>
      <p class="ppv-modal__subtitle muted">Paid message with a price attached.</p>

      <div class="form-group ppv-modal__field">
        <label class="form-label" for="ppv-text">Message</label>
        <textarea
          id="ppv-text"
          ref="textRef"
          v-model="text"
          class="textarea"
          rows="3"
          placeholder="Describe the PPV content…"
        />
      </div>

      <div class="form-group ppv-modal__field">
        <label class="form-label" for="ppv-price">Price</label>
        <div class="ppv-modal__price-wrap">
          <span class="ppv-modal__currency" aria-hidden="true">$</span>
          <input
            id="ppv-price"
            v-model="price"
            class="input ppv-modal__price-input"
            type="number"
            min="0.01"
            step="0.01"
            placeholder="19.99"
            inputmode="decimal"
          />
        </div>
      </div>

      <p v-if="validationError" class="form-error" role="alert">{{ validationError }}</p>

      <div class="ppv-modal__actions">
        <button type="button" class="btn btn-ghost" @click="emit('close')">Cancel</button>
        <button
          type="button"
          class="btn btn-primary"
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
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 10vh var(--space-4) var(--space-4);
}

.ppv-modal__backdrop {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--color-bg) 70%, transparent);
  backdrop-filter: blur(8px);
}

.ppv-modal__panel {
  position: relative;
  width: min(400px, 100%);
  padding: var(--space-5);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
}

.ppv-modal__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text);
}

.ppv-modal__subtitle {
  margin: var(--space-2) 0 0;
  font-size: 0.85rem;
}

.ppv-modal__field {
  margin-top: var(--space-4);
}

.ppv-modal__price-wrap {
  position: relative;
}

.ppv-modal__currency {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  font-weight: 600;
  pointer-events: none;
}

.ppv-modal__price-input {
  padding-left: 1.65rem;
}

.ppv-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-5);
}

@media (max-width: 520px) {
  .ppv-modal {
    padding: var(--space-4);
    align-items: center;
  }

  .ppv-modal__panel {
    max-height: calc(100vh - 2rem);
    overflow-y: auto;
  }

  .ppv-modal__actions {
    flex-wrap: wrap;
  }

  .ppv-modal__actions .btn {
    flex: 1;
    min-width: 7rem;
  }
}
</style>
