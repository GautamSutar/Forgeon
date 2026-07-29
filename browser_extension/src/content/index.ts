import { detectPlatform } from "@/content/detect";
import { fillField, highlightSubmitButton, type FillResult } from "@/content/dom-fill";
import { findFormRoot, guessJobDescription, parseFormFields } from "@/content/parser";
import type { ContentRequest, ExtractedForm } from "@/lib/types";

function extractForm(): ExtractedForm {
  const root = findFormRoot();
  const fields = parseFormFields(root);
  const html = root instanceof Document ? document.body.outerHTML : (root as Element).outerHTML;

  return {
    platform: detectPlatform(),
    url: window.location.href,
    html,
    fields,
    jobDescriptionGuess: guessJobDescription(),
  };
}

chrome.runtime.onMessage.addListener((message: ContentRequest, _sender, sendResponse) => {
  switch (message.type) {
    case "PING": {
      sendResponse({ ok: true });
      return false;
    }
    case "EXTRACT_FORM": {
      try {
        sendResponse({ ok: true, data: extractForm() });
      } catch (err) {
        sendResponse({ ok: false, error: err instanceof Error ? err.message : String(err) });
      }
      return false;
    }
    case "FILL_FIELDS": {
      try {
        const results: FillResult[] = [];
        for (const [selector, value] of Object.entries(message.fieldsBySelector)) {
          results.push(fillField(selector, null, value));
        }
        highlightSubmitButton();
        sendResponse({ ok: true, data: results });
      } catch (err) {
        sendResponse({ ok: false, error: err instanceof Error ? err.message : String(err) });
      }
      return false;
    }
    default:
      return false;
  }
});
