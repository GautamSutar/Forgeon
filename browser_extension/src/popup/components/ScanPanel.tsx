interface ResumeSummary {
  id: string;
  filename: string;
  is_default: boolean;
}

interface Props {
  jobDescription: string;
  onJobDescriptionChange: (value: string) => void;
  resumes: ResumeSummary[];
  selectedResumeId: string | undefined;
  onSelectResume: (id: string | undefined) => void;
  onAnalyze: () => void;
  busy: boolean;
  fieldCount: number | null;
  platform: string | null;
}

export function ScanPanel({
  jobDescription,
  onJobDescriptionChange,
  resumes,
  selectedResumeId,
  onSelectResume,
  onAnalyze,
  busy,
  fieldCount,
  platform,
}: Props) {
  return (
    <div className="flex flex-col gap-3 p-4">
      <h1 className="text-lg font-semibold">Review this application</h1>

      {fieldCount !== null && (
        <p className="rounded bg-slate-100 px-2 py-1.5 text-xs text-slate-600">
          Detected <span className="font-medium">{platform}</span> form with{" "}
          <span className="font-medium">{fieldCount}</span> field{fieldCount === 1 ? "" : "s"}.
        </p>
      )}

      <label className="text-sm font-medium">
        Job description
        <textarea
          value={jobDescription}
          onChange={(e) => onJobDescriptionChange(e.target.value)}
          rows={6}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
          placeholder="Paste the job description here if it wasn't auto-detected…"
        />
      </label>

      {resumes.length > 0 && (
        <label className="text-sm font-medium">
          Resume
          <select
            value={selectedResumeId ?? ""}
            onChange={(e) => onSelectResume(e.target.value || undefined)}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
          >
            <option value="">Default resume</option>
            {resumes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.filename}
                {r.is_default ? " (default)" : ""}
              </option>
            ))}
          </select>
        </label>
      )}

      <button
        type="button"
        onClick={onAnalyze}
        disabled={busy || !jobDescription.trim()}
        className="rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {busy ? "Analyzing…" : "Generate answers for review"}
      </button>
    </div>
  );
}
