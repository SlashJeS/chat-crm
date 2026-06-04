import { ref } from "vue";

export function useInfiniteMessages() {
  const isLoading = ref(false);
  const hasMore = ref(false);

  return {
    isLoading,
    hasMore,
  };
}
