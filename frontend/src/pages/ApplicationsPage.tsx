import { ChevronRight, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { applicationApi } from "@/api/endpoints";
import type { Application } from "@/api/types";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Badge, Card, CardSkeletonList, EmptyState, ErrorBanner, PageHeader } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";
import { statusTone } from "@/lib/status";
import { useToast } from "@/lib/toast";

export default function ApplicationsPage() {
  const { data: applications, loading, error, refetch } = useAsync(() => applicationApi.list());
  const [pendingDelete, setPendingDelete] = useState<Application | null>(null);
  const [deleting, setDeleting] = useState(false);
  // Rows removed locally so the list updates the instant the server confirms,
  // without waiting for the refetch round-trip to come back.
  const [removedIds, setRemovedIds] = useState<Set<string>>(new Set());
  const toast = useToast();

  const visible = (applications ?? []).filter((a) => !removedIds.has(a.id));

  async function handleDelete() {
    if (!pendingDelete) return;
    const target = pendingDelete;
    setDeleting(true);
    try {
      await applicationApi.remove(target.id);
      setRemovedIds((prev) => new Set(prev).add(target.id));
      setPendingDelete(null);
      toast.show("Application deleted.", "info");
      refetch();
    } catch (err) {
      toast.show(describeError(err), "error");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Applications"
        subtitle="Every run the agent has drafted or submitted, from the extension or the test tool."
        actions={
          visible.length > 0 && (
            <div className="text-right">
              <p className="font-semibold text-fg">{visible.length}</p>
              <p className="text-xs text-fg-subtle">Total</p>
            </div>
          )
        }
      />

      {loading && <CardSkeletonList />}
      {error && <ErrorBanner message={error} />}
      {applications && visible.length === 0 && (
        <EmptyState message="No applications yet. Run the agent on a job posting from the extension, or use Test Agent to try it out." />
      )}

      {visible.length > 0 && (
        <div className="flex flex-col gap-2.5">
          {visible.map((app) => (
            <Card
              key={app.id}
              className="group transition-all duration-150 hover:-translate-y-0.5 hover:border-line-strong hover:shadow-card-hover"
            >
              <div className="flex items-center gap-3">
                {/* The link wraps only the content, not the delete button —
                    a <button> nested inside an <a> is invalid HTML and traps
                    the click. */}
                <Link to={`/applications/${app.id}`} className="min-w-0 flex-1">
                  <p className={`truncate font-medium ${app.role_title ? "text-fg" : "italic text-fg-subtle"}`}>
                    {app.role_title ?? "Role not detected"}
                  </p>
                  <p className="mt-0.5 text-xs text-fg-subtle">
                    {app.ats_platform ? (
                      <span className="capitalize">{app.ats_platform}</span>
                    ) : (
                      "Platform not detected"
                    )}
                    <span className="mx-1.5">·</span>
                    {new Date(app.created_at).toLocaleString()}
                  </p>
                </Link>

                <Badge tone={statusTone(app.status)}>{app.status.replace("_", " ")}</Badge>

                <button
                  onClick={() => setPendingDelete(app)}
                  title="Delete application"
                  aria-label={`Delete ${app.role_title ?? "application"}`}
                  className="rounded-lg p-2 text-fg-subtle opacity-0 transition-all hover:bg-red-500/10 hover:text-red-400 focus-visible:opacity-100 group-hover:opacity-100"
                >
                  <Trash2 className="h-4 w-4" />
                </button>

                <Link to={`/applications/${app.id}`} aria-hidden tabIndex={-1}>
                  <ChevronRight className="h-4 w-4 shrink-0 text-fg-subtle transition-transform group-hover:translate-x-0.5" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        onOpenChange={(o) => !o && setPendingDelete(null)}
        title="Delete this application?"
        description={
          <>
            <span className="font-medium text-fg">
              {pendingDelete?.role_title ?? "Role not detected"}
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
