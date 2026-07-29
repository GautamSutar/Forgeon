import type { FormField } from "@/lib/types";

/** Maps the field key the backend uses in `generated_answers`
 * (`field.name || field.label`, per `generate_answers_node`) back to the
 * live element's CSS selector, so approved answers can be written into the
 * actual page.
 */
export function buildSelectorMap(fields: FormField[]): Record<string, string> {
  const map: Record<string, string> = {};
  for (const field of fields) {
    const key = field.name || field.label;
    if (!key) continue;
    map[key] = field.cssSelector;
  }
  return map;
}
