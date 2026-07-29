import { useState, type KeyboardEvent } from "react";
import { Badge, Input } from "@/components/ui";

interface Props {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
}

/** A real multi-entry input: type a value, press Enter (or click Add) to add
 * it as its own chip, click a chip's × to remove it. Replaces cramming
 * multiple entries into one comma-separated text box, which makes it easy
 * to lose track of what's already there or mis-split entries containing
 * commas (e.g. "Backend Engineer, Senior").
 */
export function TagListInput({ label, values, onChange, placeholder }: Props) {
  const [draft, setDraft] = useState("");

  function commit() {
    const trimmed = draft.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setDraft("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      commit();
    }
  }

  function remove(value: string) {
    onChange(values.filter((v) => v !== value));
  }

  return (
    <div>
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      {values.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1">
          {values.map((value) => (
            <span key={value} className="inline-flex items-center gap-1">
              <Badge tone="blue">
                {value}
                <button
                  type="button"
                  onClick={() => remove(value)}
                  aria-label={`Remove ${value}`}
                  className="ml-1 text-blue-900 hover:text-red-600"
                >
                  ×
                </button>
              </Badge>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-2">
        <Input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? "Type a value and press Enter"}
        />
        <button
          type="button"
          onClick={commit}
          className="shrink-0 rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
        >
          Add
        </button>
      </div>
    </div>
  );
}
