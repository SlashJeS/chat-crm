import { defineStore } from "pinia";
import { ref } from "vue";

export const usePresenceStore = defineStore("presence", () => {
  const onlineUserIds = ref<number[]>([]);

  return {
    onlineUserIds,
  };
});
