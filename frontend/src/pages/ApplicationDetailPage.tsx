import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { applicationApi } from "@/api/endpoints";
import type { ApplicationStatus } from "@/api/types";
import { Badge, Button, Card, ErrorBanner, FieldLabel, Spinner } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";
import { statusTone } from "@/lib/status";

const STATUS_OPTIONS: ApplicationStatus[] = [
  "draft",
  "pending_approval",
  "approved",
  "rejected",
  "submitted",
  "failed",
];

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: application, loading, error, refetch } = useAsync(() => applicationApi.get(id!), [id]);
  const [actionError, setActionError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;
  if (!application) return null;

  async function handleStatusChange(status: ApplicationStatus) {
    setSaving(true);
    setActionError(null);
    try {
      await applicationApi.update(application!.id, { status });
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this application record? This cannot be undone.")) return;
    try {
      await applicationApi.remove(application!.id);
      navigate("/applications");
    } catch (err) {
      setActionError(describeError(err));
    }
  }

  return (
    <div className="max-w-2xl">
      <button onClick={() => navigate(-1)} className="mb-4 text-sm text-blue-600">
        ← Back
      </button>

      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">{application.role_title ?? "Untitled role"}</h1>
        <Badge tone={statusTone(application.status)}>{application.status.replace("_", " ")}</Badge>
      </div>

      <Card className="mb-4">
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-slate-500">ATS platform</dt>
            <dd>{application.ats_platform ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Source URL</dt>
            <dd className="truncate">
              {application.source_url ? (
                <a href={application.source_url} target="_blank" rel="noreferrer" className="text-blue-600">
                  {application.source_url}
                </a>
              ) : (
                "—"
              )}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Created</dt>
            <dd>{new Date(application.created_at).toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Last updated</dt>
            <dd>{new Date(application.updated_at).toLocaleString()}</dd>
          </div>
        </dl>
      </Card>

      <Card className="mb-4">
        <FieldLabel htmlFor="status">Status</FieldLabel>
        <select
          id="status"
          value={application.status}
          disabled={saving}
          onChange={(e) => handleStatusChange(e.target.value as ApplicationStatus)}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s.replace("_", " ")}
            </option>
          ))}
        </select>
      </Card>

      {actionError && <ErrorBanner message={actionError} />}

      <Button variant="danger" onClick={handleDelete}>
        Delete application
      </Button>
    </div>
  );
}
