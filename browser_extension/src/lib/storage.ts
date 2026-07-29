import type { AuthTokens, ExtensionSettings } from "@/lib/types";

const AUTH_KEY = "auth_tokens";
const SETTINGS_KEY = "settings";

const DEFAULT_SETTINGS: ExtensionSettings = {
  apiBaseUrl: "http://localhost:8000/api/v1",
};

export async function getTokens(): Promise<AuthTokens | null> {
  const result = await chrome.storage.local.get(AUTH_KEY);
  return (result[AUTH_KEY] as AuthTokens | undefined) ?? null;
}

export async function setTokens(tokens: AuthTokens | null): Promise<void> {
  if (tokens === null) {
    await chrome.storage.local.remove(AUTH_KEY);
    return;
  }
  await chrome.storage.local.set({ [AUTH_KEY]: tokens });
}

export async function getSettings(): Promise<ExtensionSettings> {
  const result = await chrome.storage.local.get(SETTINGS_KEY);
  return { ...DEFAULT_SETTINGS, ...(result[SETTINGS_KEY] as Partial<ExtensionSettings> | undefined) };
}

export async function setSettings(settings: ExtensionSettings): Promise<void> {
  await chrome.storage.local.set({ [SETTINGS_KEY]: settings });
}
