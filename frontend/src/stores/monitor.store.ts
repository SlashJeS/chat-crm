import { defineStore } from "pinia";
import { ref } from "vue";

import type { MonitorChatter } from "@/types/monitor";

export const useMonitorStore = defineStore("monitor", () => {
  const chatters = ref<MonitorChatter[]>([]);

  return {
    chatters,
  };
});
