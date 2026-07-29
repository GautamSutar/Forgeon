import type { FormField } from "@/lib/types";

const SKIPPED_INPUT_TYPES = new Set(["hidden", "submit", "button", "image", "reset"]);

function cssEscape(value: string): string {
  return typeof CSS !== "undefined" && CSS.escape ? CSS.escape(value) : value.replace(/[^a-zA-Z0-9_-]/g, "\\$&");
}

/** Builds a selector that's stable enough to re-find this exact element:
 * prefers #id, falls back to a tag+nth-of-type path from the nearest form
 * (or body), which survives re-renders better than a fully absolute path.
 */
function buildCssSelector(el: Element): string {
  if (el.id) return `#${cssEscape(el.id)}`;

  const parts: string[] = [];
  const root = el.closest("form") ?? document.body;

  let node: Element | null = el;
  while (node && node !== root && node.parentElement) {
    const current: Element = node;
    const parent: Element = node.parentElement;
    const siblingsOfType = Array.from(parent.children).filter((c) => c.tagName === current.tagName);
    const index = siblingsOfType.indexOf(current) + 1;
    parts.unshift(`${current.tagName.toLowerCase()}:nth-of-type(${index})`);
    node = parent;
  }

  const rootSelector = root === document.body ? "body" : root.id ? `#${cssEscape(root.id)}` : "form";
  return [rootSelector, ...parts].join(" > ");
}

function buildXPath(el: Element): string {
  if (el.id) return `//*[@id="${el.id}"]`;

  const parts: string[] = [];
  let node: Element | null = el;
  while (node && node.nodeType === Node.ELEMENT_NODE) {
    let index = 1;
    let sibling = node.previousElementSibling;
    while (sibling) {
      if (sibling.tagName === node.tagName) index += 1;
      sibling = sibling.previousElementSibling;
    }
    parts.unshift(`${node.tagName.toLowerCase()}[${index}]`);
    node = node.parentElement;
  }
  return `/${parts.join("/")}`;
}

function findLabelFor(el: HTMLElement): string | null {
  const id = el.id;
  if (id) {
    const labelTag = document.querySelector(`label[for="${cssEscape(id)}"]`);
    if (labelTag?.textContent?.trim()) return labelTag.textContent.trim();
  }
  const parentLabel = el.closest("label");
  if (parentLabel?.textContent?.trim()) return parentLabel.textContent.trim();

  const ariaLabel = el.getAttribute("aria-label");
  if (ariaLabel?.trim()) return ariaLabel.trim();

  const ariaLabelledBy = el.getAttribute("aria-labelledby");
  if (ariaLabelledBy) {
    const referenced = document.getElementById(ariaLabelledBy);
    if (referenced?.textContent?.trim()) return referenced.textContent.trim();
  }

  const placeholder = el.getAttribute("placeholder");
  if (placeholder?.trim()) return placeholder.trim();

  // Bare text sitting next to the input with no semantic label wrapper —
  // common for hand-rolled radio/checkbox groups.
  const next = el.nextSibling;
  if (next?.nodeType === Node.TEXT_NODE && next.textContent?.trim()) {
    return next.textContent.trim();
  }

  return null;
}

function isVisible(el: HTMLElement): boolean {
  if (el.hidden) return false;
  const style = window.getComputedStyle(el);
  return style.display !== "none" && style.visibility !== "hidden";
}

/** Extracts structured form fields from the live DOM within `root`
 * (defaults to the whole document), mirroring the backend's
 * `html_form_parser.py` semantics for consistency between server-side and
 * extension-side extraction.
 */
export function parseFormFields(root: ParentNode = document): FormField[] {
  const fields: FormField[] = [];
  const seenRadioGroups = new Set<string>();
  const elements = root.querySelectorAll<HTMLElement>("input, textarea, select");

  for (const el of Array.from(elements)) {
    const tagName = el.tagName.toLowerCase();
    const elType = tagName === "input" ? (el.getAttribute("type") || "text").toLowerCase() : tagName;

    if (SKIPPED_INPUT_TYPES.has(elType)) continue;
    if (!isVisible(el)) continue;

    const name = el.getAttribute("name");

    if (elType === "radio" && name) {
      if (seenRadioGroups.has(name)) continue;
      seenRadioGroups.add(name);
    }

    const label = findLabelFor(el);
    const required = el.hasAttribute("required") || el.getAttribute("aria-required") === "true";
    const placeholder = el.getAttribute("placeholder");

    let options: string[] = [];
    if (tagName === "select") {
      options = Array.from(el.querySelectorAll("option"))
        .map((opt) => opt.textContent?.trim() ?? "")
        .filter(Boolean);
    } else if ((elType === "radio" || elType === "checkbox") && name) {
      const siblings = root.querySelectorAll<HTMLElement>(
        `input[type="${elType}"][name="${cssEscape(name)}"]`,
      );
      options = Array.from(siblings).map((sib) => findLabelFor(sib) ?? sib.getAttribute("value") ?? "");
    }

    fields.push({
      name,
      label,
      cssSelector: buildCssSelector(el),
      xpath: buildXPath(el),
      type: elType,
      required,
      options,
      placeholder,
      tagId: el.id || null,
    });
  }

  return fields;
}

/** Picks the most likely application-form root: the <form> with the most
 * fillable fields, or the whole document if the page has no <form> wrapper
 * (common in SPA-heavy ATS UIs like Workday/LinkedIn's Easy Apply modal).
 */
export function findFormRoot(): ParentNode {
  const forms = Array.from(document.querySelectorAll("form"));
  if (forms.length === 0) return document;

  let best: HTMLFormElement = forms[0];
  let bestCount = -1;
  for (const form of forms) {
    const count = form.querySelectorAll("input, textarea, select").length;
    if (count > bestCount) {
      bestCount = count;
      best = form;
    }
  }
  return bestCount > 0 ? best : document;
}

/** Best-effort heuristic guess at the job description text on the page, used
 * to pre-fill the popup's JD field so the user usually just has to confirm
 * rather than paste it manually.
 */
export function guessJobDescription(): string {
  const candidates = [
    '[class*="job-description"]',
    '[class*="jobDescription"]',
    '[data-testid*="job-description"]',
    "#job-description",
    'section[class*="description"]',
  ];
  for (const selector of candidates) {
    const el = document.querySelector(selector);
    const text = el?.textContent?.trim();
    if (text && text.length > 100) return text.slice(0, 8000);
  }
  return "";
}
