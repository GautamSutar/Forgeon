/** Sets a value on a live form element and dispatches the events frameworks
 * (React, Angular, etc.) listen for, so controlled-input state actually
 * updates rather than only the raw DOM value.
 */
function dispatchInputEvents(el: HTMLElement): void {
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
  el.dispatchEvent(new Event("blur", { bubbles: true }));
}

/** React tracks input values via a custom setter; writing straight to
 * `.value` gets silently overwritten on the next render unless we go
 * through the native setter first. This is the standard workaround.
 */
function setNativeValue(el: HTMLInputElement | HTMLTextAreaElement, value: string): void {
  const prototype = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
  const setter = descriptor?.set;
  if (setter) {
    setter.call(el, value);
  } else {
    el.value = value;
  }
}

export interface FillResult {
  selector: string;
  ok: boolean;
  reason?: string;
}

function fillTextLike(el: HTMLInputElement | HTMLTextAreaElement, value: string): void {
  el.focus();
  setNativeValue(el, value);
  dispatchInputEvents(el);
}

function fillSelect(el: HTMLSelectElement, value: string): boolean {
  const options = Array.from(el.options);
  const match =
    options.find((o) => o.value === value) ??
    options.find((o) => o.textContent?.trim().toLowerCase() === value.trim().toLowerCase()) ??
    options.find((o) => o.textContent?.trim().toLowerCase().includes(value.trim().toLowerCase()));
  if (!match) return false;
  el.value = match.value;
  dispatchInputEvents(el);
  return true;
}

function fillRadioOrCheckboxGroup(name: string, value: string): boolean {
  const group = Array.from(document.querySelectorAll<HTMLInputElement>(`input[name="${CSS.escape(name)}"]`));
  const target = group.find((input) => {
    const label = input.closest("label")?.textContent?.trim() ?? input.nextSibling?.textContent?.trim() ?? "";
    return (
      input.value.trim().toLowerCase() === value.trim().toLowerCase() ||
      label.toLowerCase() === value.trim().toLowerCase()
    );
  });
  if (!target) return false;
  target.checked = true;
  dispatchInputEvents(target);
  return true;
}

/** Fills a single field identified by CSS selector with an approved answer.
 * Never touches the submit button — that stays a deliberate, separate human
 * action even after approval.
 */
export function fillField(selector: string, fieldName: string | null, value: string): FillResult {
  const el = document.querySelector<HTMLElement>(selector);
  if (!el) {
    return { selector, ok: false, reason: "Element not found on page" };
  }

  try {
    if (el instanceof HTMLInputElement) {
      if (el.type === "radio" || el.type === "checkbox") {
        const name = el.getAttribute("name") ?? fieldName;
        if (!name) return { selector, ok: false, reason: "No group name for radio/checkbox" };
        const ok = fillRadioOrCheckboxGroup(name, value);
        return { selector, ok, reason: ok ? undefined : "No matching option" };
      }
      fillTextLike(el, value);
      return { selector, ok: true };
    }
    if (el instanceof HTMLTextAreaElement) {
      fillTextLike(el, value);
      return { selector, ok: true };
    }
    if (el instanceof HTMLSelectElement) {
      const ok = fillSelect(el, value);
      return { selector, ok, reason: ok ? undefined : "No matching option" };
    }
    return { selector, ok: false, reason: `Unsupported element: ${el.tagName}` };
  } catch (err) {
    return { selector, ok: false, reason: err instanceof Error ? err.message : String(err) };
  }
}

/** Scrolls to and briefly highlights the submit button so the user can find
 * it easily — but never clicks it. Submission is always a manual human
 * action, even after backend approval.
 */
export function highlightSubmitButton(): boolean {
  const submit = document.querySelector<HTMLElement>(
    'button[type="submit"], input[type="submit"], button[class*="submit" i]',
  );
  if (!submit) return false;
  submit.scrollIntoView({ behavior: "smooth", block: "center" });
  const originalOutline = submit.style.outline;
  const originalOffset = submit.style.outlineOffset;
  submit.style.outline = "3px solid #2563eb";
  submit.style.outlineOffset = "2px";
  window.setTimeout(() => {
    submit.style.outline = originalOutline;
    submit.style.outlineOffset = originalOffset;
  }, 4000);
  return true;
}
