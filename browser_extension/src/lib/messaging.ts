import type { BackgroundRequest, ContentRequest } from "@/lib/types";

interface Envelope<T> {
  ok: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export class MessagingError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "MessagingError";
  }
}

export async function callBackground<T>(message: BackgroundRequest): Promise<T> {
  const envelope = (await chrome.runtime.sendMessage(message)) as Envelope<T>;
  if (!envelope?.ok) {
    throw new MessagingError(envelope?.error ?? "Unknown background error", envelope?.status);
  }
  return envelope.data as T;
}

async function getActiveTabId(): Promise<number> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new MessagingError("No active tab found");
  return tab.id;
}

/** Ensures the content script is present on the active tab. Declarative
 * `content_scripts` matches already cover the known ATS domains; this
 * on-demand injection via `scripting` + `activeTab` is what makes arbitrary
 * "Custom HTML forms" (the site is not in manifest.json's match list) work
 * too, without requesting a broad <all_urls> host permission.
 */
async function ensureContentScript(tabId: number): Promise<void> {
  try {
    await chrome.tabs.sendMessage(tabId, { type: "PING" } satisfies ContentRequest);
    return;
  } catch {
    // Not injected yet — fall through to inject.
  }
  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"],
  });
}

export async function callContentScript<T>(message: ContentRequest): Promise<T> {
  const tabId = await getActiveTabId();
  await ensureContentScript(tabId);
  const envelope = (await chrome.tabs.sendMessage(tabId, message)) as Envelope<T>;
  if (!envelope?.ok) {
    throw new MessagingError(envelope?.error ?? "Unknown content script error");
  }
  return envelope.data as T;
}
