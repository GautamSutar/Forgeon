import type { EducationEntry } from "@/api/types";
import { Button, FieldLabel, Input } from "@/components/ui";

const EMPTY_ENTRY: EducationEntry = {
  school: "",
  degree: null,
  field_of_study: null,
  gpa: null,
  start_year: null,
  end_year: null,
};

interface Props {
  entries: EducationEntry[];
  onChange: (entries: EducationEntry[]) => void;
}

/** Mirrors the "Education 1 / Education 2 / Add Another" repeatable pattern
 * used by Workday and similar ATSes.
 */
export function EducationHistoryEditor({ entries, onChange }: Props) {
  function update(index: number, patch: Partial<EducationEntry>) {
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
        <div key={index} className="rounded border border-line p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-fg-muted">Education {index + 1}</span>
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
              <FieldLabel>School or university</FieldLabel>
              <Input required value={entry.school} onChange={(e) => update(index, { school: e.target.value })} />
            </div>
            <div>
              <FieldLabel>Degree</FieldLabel>
              <Input
                value={entry.degree ?? ""}
                onChange={(e) => update(index, { degree: e.target.value })}
              />
            </div>
            <div>
              <FieldLabel>Field of study</FieldLabel>
              <Input
                value={entry.field_of_study ?? ""}
                onChange={(e) => update(index, { field_of_study: e.target.value })}
              />
            </div>
            <div>
              <FieldLabel>Overall result (GPA / %)</FieldLabel>
              <Input value={entry.gpa ?? ""} onChange={(e) => update(index, { gpa: e.target.value })} />
            </div>
            <div>
              <FieldLabel>Start year</FieldLabel>
              <Input
                type="number"
                value={entry.start_year ?? ""}
                onChange={(e) => update(index, { start_year: e.target.value ? Number(e.target.value) : null })}
              />
            </div>
            <div>
              <FieldLabel>End year</FieldLabel>
              <Input
                type="number"
                value={entry.end_year ?? ""}
                onChange={(e) => update(index, { end_year: e.target.value ? Number(e.target.value) : null })}
              />
            </div>
          </div>
        </div>
      ))}

      <Button type="button" variant="secondary" onClick={add} className="w-fit">
        Add Another
      </Button>
    </div>
  );
}
