import { onBeforeUnmount, onMounted, ref } from "vue";
import { apiClient } from "@/shared/api/client";
import { createEventSocket, type EventMessage } from "@/shared/api/events";
import type { AutomationLogEntry, AutomationStatus } from "@/shared/types/api";

type RuntimeEventsOptions = {
  logLimit?: number;
  refreshIntervalMs?: number;
};

export function useRuntimeEvents(options: RuntimeEventsOptions = {}) {
  const logLimit = options.logLimit ?? 100;
  const refreshIntervalMs = options.refreshIntervalMs ?? 1000;
  const status = ref<AutomationStatus | null>(null);
  const logs = ref<AutomationLogEntry[]>([]);
  const isLive = ref(false);
  let socket: WebSocket | null = null;
  let refreshTimer: number | null = null;
  let reconnectTimer: number | null = null;
  let refreshInFlight = false;
  let isUnmounted = false;

  function applyEventMessage(message: EventMessage) {
    if (message.type === "status") {
      status.value = message.data;
      return;
    }

    if (message.type === "logs") {
      logs.value = message.data.slice(0, logLimit);
      return;
    }

    logs.value = [message.data, ...logs.value].slice(0, logLimit);
  }

  async function loadRuntimeSnapshot() {
    if (refreshInFlight) {
      return;
    }

    refreshInFlight = true;
    try {
      const [nextStatus, nextLogs] = await Promise.all([apiClient.getStatus(), apiClient.getLogs(logLimit)]);
      status.value = nextStatus;
      logs.value = nextLogs.slice(0, logLimit);
    } catch (error) {
      console.warn("[StellaTowerAssistant] Failed to refresh runtime snapshot", error);
    } finally {
      refreshInFlight = false;
    }
  }

  function clearReconnectTimer() {
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function connectSocket() {
    clearReconnectTimer();
    socket?.close();
    try {
      socket = createEventSocket(applyEventMessage);
    } catch (error) {
      console.warn("[StellaTowerAssistant] Failed to open event stream", error);
      isLive.value = false;
      if (!isUnmounted) {
        reconnectTimer = window.setTimeout(connectSocket, 1500);
      }
      return;
    }

    socket.onopen = () => {
      isLive.value = true;
    };

    socket.onerror = () => {
      isLive.value = false;
    };

    socket.onclose = () => {
      isLive.value = false;
      socket = null;
      if (!isUnmounted) {
        reconnectTimer = window.setTimeout(connectSocket, 1500);
      }
    };
  }

  onMounted(async () => {
    await loadRuntimeSnapshot();
    connectSocket();
    refreshTimer = window.setInterval(loadRuntimeSnapshot, refreshIntervalMs);
  });

  onBeforeUnmount(() => {
    isUnmounted = true;
    clearReconnectTimer();
    if (refreshTimer !== null) {
      window.clearInterval(refreshTimer);
      refreshTimer = null;
    }
    socket?.close();
  });

  return {
    status,
    logs,
    isLive,
    loadRuntimeSnapshot,
  };
}
