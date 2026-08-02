import { Trash2 } from "lucide-react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { applicationApi } from "@/api/endpoints";
import type { ApplicationStatus } from "@/api/types";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Badge, Button, Card, ErrorBanner, FieldLabel } from "@/components/ui";
import { PageLoader } from "@/components/PageLoader";
import { describeError, useAsync } from "@/lib/useAsync";
import { statusTone } from "@/lib/status";
import { useToast } from "@/lib/toast";

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
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  if (loading) return <PageLoader label="Loading application" />;
  if (error) return <ErrorBanner message={error} />;
  if (!application) return null;

  async function handleStatusChange(status: ApplicationStatus) {
    setSaving(true);
    setActionError(null);
    try {
      await applicationApi.update(application!.id, { status });
      toast.show("Status updated.");
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await applicationApi.remove(application!.id);
      navigate("/applications");
    } catch (err) {
      setActionError(describeError(err));
      setConfirmOpen(false);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-fg-subtle transition-colors hover:text-brand-400"
      >
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>

      <div className="mb-4 flex items-center justify-between gap-4">
        <h1 className={`text-2xl font-bold tracking-tight ${application.role_title ? "text-fg" : "italic text-fg-subtle"}`}>
          {application.role_title ?? "Role not detected"}
        </h1>
        <Badge tone={statusTone(application.status)}>{application.status.replace("_", " ")}</Badge>
      </div>

      <Card className="mb-4">
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-fg-subtle">ATS platform</dt>
            <dd className="mt-1 capitalize text-fg-muted">{application.ats_platform ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-fg-subtle">Source URL</dt>
            <dd className="mt-1 truncate">
              {application.source_url ? (
                <a
                  href={application.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-400 hover:text-brand-300 hover:underline"
                >
                  {application.source_url}
                </a>
              ) : (
                <span className="text-fg-muted">—</span>
              )}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-fg-subtle">Created</dt>
            <dd className="mt-1 text-fg-muted">{new Date(application.created_at).toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium uppercase tracking-wide text-fg-subtle">Last updated</dt>
            <dd className="mt-1 text-fg-muted">{new Date(application.updated_at).toLocaleString()}</dd>
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
          className="w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm text-fg shadow-sm transition-colors hover:border-line-strong focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s.replace("_", " ")}
            </option>
          ))}
        </select>
      </Card>

      {actionError && (
        <div className="mb-4">
          <ErrorBanner message={actionError} />
        </div>
      )}

      <Button variant="danger" onClick={() => setConfirmOpen(true)}>
        <Trash2 className="h-4 w-4" />
        Delete application
      </Button>

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Delete this application?"
        description={
          <>
            <span className="font-medium text-fg">
              {application.role_title ?? "Role not detected"}
            </span>{" "}
            and its saved answers will be permanently removed. This cannot be undone.
          </>
        }
        busy={deleting}
        onConfirm={handleDelete}
      />
    </div>
  );
}
