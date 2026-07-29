import type { GeneratedAnswerEntry } from "@/lib/types";

interface Props {
  answers: Record<string, GeneratedAnswerEntry>;
  edited: Record<string, string>;
  onEdit: (fieldKey: string, value: string) => void;
  validationErrors: string[];
  onApprove: () => void;
  onReject: () => void;
  busy: boolean;
}

function sourceBadge(entry: GeneratedAnswerEntry) {
  if (entry.refused) {
    return <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">refused</span>;
  }
  if (entry.source === "profile") {
    return <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-medium text-emerald-800">profile</span>;
  }
  return <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-800">generated</span>;
}

export function PreviewPanel({ answers, edited, onEdit, validationErrors, onApprove, onReject, busy }: Props) {
  const entries = Object.entries(answers);

  return (
    <div className="flex flex-col gap-3 p-4">
      <h1 className="text-lg font-semibold">Review before submitting</h1>
      <p className="text-xs text-slate-500">
        Nothing is submitted until you approve. Edit any answer below before approving — the agent never invents
        experience that isn't in your resume or profile.
      </p>

      {validationErrors.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800">
          <p className="font-medium">Validation warnings:</p>
          <ul className="list-disc pl-4">
            {validationErrors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex max-h-64 flex-col gap-3 overflow-y-auto">
        {entries.length === 0 && <p className="text-sm text-slate-500">No fields required generated answers.</p>}
        {entries.map(([fieldKey, entry]) => (
          <div key={fieldKey} className="rounded border border-slate-200 p-2">
            <div className="mb-1 flex items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-700">{fieldKey}</span>
              {sourceBadge(entry)}
            </div>
            <textarea
              value={edited[fieldKey] ?? entry.answer}
              onChange={(e) => onEdit(fieldKey, e.target.value)}
              rows={entry.answer.length > 80 ? 3 : 1}
              className="w-full rounded border border-slate-300 px-2 py-1 text-sm"
            />
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={onReject}
          disabled={busy}
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
        >
          Reject
        </button>
        <button
          type="button"
          onClick={onApprove}
          disabled={busy}
          className="flex-1 rounded bg-emerald-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Submitting…" : "Approve & fill form"}
        </button>
      </div>
    </div>
  );
}
