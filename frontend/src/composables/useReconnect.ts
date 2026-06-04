import { ref } from "vue";

export function useReconnect() {
  const isReconnecting = ref(false);

  return {
    isReconnecting,
  };
}
