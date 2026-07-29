import type { WorkExperienceEntry } from "@/api/types";
import { Button, FieldLabel, Input, Textarea } from "@/components/ui";

const EMPTY_ENTRY: WorkExperienceEntry = {
  job_title: "",
  company: "",
  location: null,
  is_current: false,
  start_month: null,
  start_year: null,
  end_month: null,
  end_year: null,
  description: null,
};

interface Props {
  entries: WorkExperienceEntry[];
  onChange: (entries: WorkExperienceEntry[]) => void;
}

/** Mirrors the "Work Experience 1 / Work Experience 2 / Add Another" pattern
 * used by Workday and similar ATSes — a repeatable list of structured
 * entries, not a single flat field.
 */
export function WorkExperienceEditor({ entries, onChange }: Props) {
  function update(index: number, patch: Partial<WorkExperienceEntry>) {
    onChange(entries.map((entry, i) => (i === index ? { ...entry, ...patch } : entry)));
  }

  function remove(index: number) {
    onChange(entries.filter((_, i) => i !== index));
  }

  function add() {
    onChange([...entries, { ...EMPTY_ENTRY }]);
  }

  return (
    <div className="flex flex-col gap-4">
      {entries.map((entry, index) => (
        <div key={index} className="rounded border border-slate-200 p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">Work Experience {index + 1}</span>
            <button
              type="button"
              onClick={() => remove(index)}
              className="text-xs text-red-600 hover:underline"
            >
              Delete
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <FieldLabel>Job title</FieldLabel>
              <Input
                required
                value={entry.job_title}
                onChange={(e) => update(index, { job_title: e.target.value })}
              />
            </div>
            <div>
              <FieldLabel>Company</FieldLabel>
              <Input
                required
                value={entry.company}
                onChange={(e) => update(index, { company: e.target.value })}
              />
            </div>
            <div>
              <FieldLabel>Location</FieldLabel>
              <Input
                value={entry.location ?? ""}
                onChange={(e) => update(index, { location: e.target.value })}
              />
            </div>
            <div className="flex items-end pb-2">
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={entry.is_current}
                  onChange={(e) => update(index, { is_current: e.target.checked })}
                />
                I currently work here
              </label>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <FieldLabel>From (month)</FieldLabel>
                <Input
                  type="number"
                  min={1}
                  max={12}
                  value={entry.start_month ?? ""}
                  onChange={(e) => update(index, { start_month: e.target.value ? Number(e.target.value) : null })}
                />
              </div>
              <div>
                <FieldLabel>From (year)</FieldLabel>
                <Input
                  type="number"
                  value={entry.start_year ?? ""}
                  onChange={(e) => update(index, { start_year: e.target.value ? Number(e.target.value) : null })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <FieldLabel>To (month)</FieldLabel>
                <Input
                  type="number"
                  min={1}
                  max={12}
                  disabled={entry.is_current}
                  value={entry.end_month ?? ""}
                  onChange={(e) => update(index, { end_month: e.target.value ? Number(e.target.value) : null })}
                />
              </div>
              <div>
                <FieldLabel>To (year)</FieldLabel>
                <Input
                  type="number"
                  disabled={entry.is_current}
                  value={entry.end_year ?? ""}
                  onChange={(e) => update(index, { end_year: e.target.value ? Number(e.target.value) : null })}
                />
              </div>
            </div>
          </div>

          <div className="mt-3">
            <FieldLabel>Role description</FieldLabel>
            <Textarea
              rows={3}
              value={entry.description ?? ""}
              onChange={(e) => update(index, { description: e.target.value })}
            />
          </div>
        </div>
      ))}

      <Button type="button" variant="secondary" onClick={add} className="w-fit">
        Add Another
      </Button>
    </div>
  );
}
