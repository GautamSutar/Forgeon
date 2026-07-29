interface Props {
  status: string | null;
  fillFailures: string[];
  onStartOver: () => void;
}

export function ResultPanel({ status, fillFailures, onStartOver }: Props) {
  const submitted = status === "submitted";
  const rejected = status === "rejected" || status === "draft";

  return (
    <div className="flex flex-col gap-3 p-4">
      <h1 className="text-lg font-semibold">
        {submitted ? "Fields filled in" : rejected ? "Application discarded" : "Run finished"}
      </h1>

      {submitted && (
        <p className="text-sm text-slate-600">
          Approved answers were written into the page's form fields and the submit button was highlighted. Review
          everything on the page, then click Submit yourself — this extension never clicks it for you.
        </p>
      )}

      {rejected && <p className="text-sm text-slate-600">No fields were filled and nothing was submitted.</p>}

      {fillFailures.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800">
          <p className="font-medium">Some fields could not be auto-filled — fill these manually:</p>
          <ul className="list-disc pl-4">
            {fillFailures.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="button"
        onClick={onStartOver}
        className="rounded border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700"
      >
        Start over
      </button>
    </div>
  );
}
