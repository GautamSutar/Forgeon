import { Link } from "react-router-dom";
import { applicationApi } from "@/api/endpoints";
import { Badge, Card, EmptyState, ErrorBanner, Spinner } from "@/components/ui";
import { useAsync } from "@/lib/useAsync";
import { statusTone } from "@/lib/status";

export default function ApplicationsPage() {
  const { data: applications, loading, error } = useAsync(() => applicationApi.list());

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Applications</h1>

      {loading && <Spinner />}
      {error && <ErrorBanner message={error} />}
      {applications && applications.length === 0 && (
        <EmptyState message="No applications yet. Run the agent on a job posting from the extension, or use Run Agent to test." />
      )}

      {applications && applications.length > 0 && (
        <div className="flex flex-col gap-2">
          {applications.map((app) => (
            <Link key={app.id} to={`/applications/${app.id}`}>
              <Card className="transition-shadow hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{app.role_title ?? "Untitled role"}</p>
                    <p className="text-xs text-slate-500">
                      {app.ats_platform ?? "unknown platform"} · {new Date(app.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Badge tone={statusTone(app.status)}>{app.status.replace("_", " ")}</Badge>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
