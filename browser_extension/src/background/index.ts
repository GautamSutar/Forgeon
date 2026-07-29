import { ApiClient, ApiError } from "@/lib/api";
import { getSettings, getTokens, setSettings, setTokens } from "@/lib/storage";
import type { BackgroundRequest } from "@/lib/types";

async function buildClient(): Promise<ApiClient> {
  const [settings, tokens] = await Promise.all([getSettings(), getTokens()]);
  return new ApiClient(settings.apiBaseUrl, tokens, setTokens);
}

type Handler = (message: Extract<BackgroundRequest, { type: string }>) => Promise<unknown>;

const handlers: Record<BackgroundRequest["type"], Handler> = {
  LOGIN: async (message) => {
    if (message.type !== "LOGIN") return;
    const client = await buildClient();
    const tokens = await client.login(message.email, message.password);
    await setTokens(tokens);
    return { ok: true };
  },

  LOGOUT: async () => {
    await setTokens(null);
    return { ok: true };
  },

  GET_AUTH_STATE: async () => {
    const tokens = await getTokens();
    return { authenticated: Boolean(tokens) };
  },

  GET_SETTINGS: async () => {
    return getSettings();
  },

  SET_SETTINGS: async (message) => {
    if (message.type !== "SET_SETTINGS") return;
    await setSettings(message.settings);
    return { ok: true };
  },

  LIST_RESUMES: async () => {
    const client = await buildClient();
    return client.listResumes();
  },

  RUN_AGENT: async (message) => {
    if (message.type !== "RUN_AGENT") return;
    const client = await buildClient();
    return client.runAgent(message.html, message.jobDescription, message.resumeId);
  },

  APPROVE_RUN: async (message) => {
    if (message.type !== "APPROVE_RUN") return;
    const client = await buildClient();
    return client.approveRun(message.runId, message.editedAnswers);
  },

  REJECT_RUN: async (message) => {
    if (message.type !== "REJECT_RUN") return;
    const client = await buildClient();
    return client.rejectRun(message.runId, message.reason);
  },
};

chrome.runtime.onMessage.addListener((message: BackgroundRequest, _sender, sendResponse) => {
  const handler = handlers[message.type];
  if (!handler) {
    sendResponse({ ok: false, error: `Unknown message type: ${message.type}` });
    return false;
  }

  handler(message)
    .then((data) => sendResponse({ ok: true, data }))
    .catch((err: unknown) => {
      const message_ = err instanceof ApiError ? err.message : err instanceof Error ? err.message : String(err);
      const status = err instanceof ApiError ? err.status : undefined;
      sendResponse({ ok: false, error: message_, status });
    });

  return true; // keep the message channel open for the async response
});
