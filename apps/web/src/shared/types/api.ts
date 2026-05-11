export type AutomationStatus = {
  is_running: boolean;
  is_paused: boolean;
  current_run: number;
  max_runs: number;
  last_error: string | null;
  last_message: string;
  started_at: string | null;
  finished_at: string | null;
  current_gold: number | null;
  thread_alive: boolean;
};

export type AutomationLogEntry = {
  id: string;
  timestamp: string;
  level: string;
  scope: string;
  message: string;
  event_type: string;
  payload: Record<string, unknown>;
};

export type ActionResponse = {
  ok: boolean;
  message: string;
};

export type SettingsResponse = {
  api_host: string;
  api_port: number;
  resource_dir: string;
  emulator_keywords: string[];
  thresholds: Record<string, number>;
  timing: Record<string, number>;
  limits: Record<string, number>;
};

export type TemplateInfo = {
  key: string;
  filename: string;
  path: string;
  exists: boolean;
};

export type ScreenshotResponse = {
  captured_at: string;
  width: number;
  height: number;
  image_base64: string;
};
