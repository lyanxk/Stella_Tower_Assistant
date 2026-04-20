import type { AutomationLogEntry, AutomationStatus } from "@/shared/types/api";

export type EventMessage =
  | { type: "status"; data: AutomationStatus }
  | { type: "logs"; data: AutomationLogEntry[] }
  | { type: "event"; data: AutomationLogEntry };

export function createEventSocket(onMessage: (message: EventMessage) => void): WebSocket {
  const socket = new WebSocket("ws://127.0.0.1:8765/ws/events");
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data) as EventMessage);
  };
  return socket;
}
