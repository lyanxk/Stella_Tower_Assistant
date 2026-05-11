import type {
  ActionResponse,
  AutomationLogEntry,
  AutomationStatus,
  ScreenshotResponse,
  SettingsResponse,
  TemplateInfo,
} from "@/shared/types/api";

const API_BASE = "http://127.0.0.1:8765";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  getStatus: () => request<AutomationStatus>("/api/automation/status"),
  getLogs: async (limit = 100) =>
    (await request<{ items: AutomationLogEntry[] }>(`/api/automation/logs?limit=${limit}`)).items,
  start: () => request<ActionResponse>("/api/automation/start", { method: "POST" }),
  pause: () => request<ActionResponse>("/api/automation/pause", { method: "POST" }),
  resume: () => request<ActionResponse>("/api/automation/resume", { method: "POST" }),
  stop: () => request<ActionResponse>("/api/automation/stop", { method: "POST" }),
  exit: () => request<ActionResponse>("/api/system/exit", { method: "POST" }),
  getSettings: () => request<SettingsResponse>("/api/settings"),
  getTemplates: async () => (await request<{ items: TemplateInfo[] }>("/api/templates")).items,
  getScreenshot: () => request<ScreenshotResponse>("/api/emulator/screenshot"),
  getWindow: () => request<Record<string, unknown>>("/api/emulator/window"),
  getHealth: () => request<Record<string, unknown>>("/health"),
};
