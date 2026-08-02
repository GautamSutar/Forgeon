import { Link } from "react-router-dom";
import { applicationApi } from "@/api/endpoints";
import { Badge, Card, CardSkeletonList, EmptyState, ErrorBanner, PageHeader } from "@/components/ui";
import { useAsync } from "@/lib/useAsync";
import { statusTone } from "@/lib/status";

export default function ApplicationsPage() {
  const { data: applications, loading, error } = useAsync(() => applicationApi.list());

  return (
    <div>
      <PageHeader
        title="Applications"
        subtitle="Every run the agent has drafted or submitted, from the extension or the test tool."
      />

      {loading && <CardSkeletonList />}
      {error && <ErrorBanner message={error} />}
      {applications && applications.length === 0 && (
        <EmptyState message="No applications yet. Run the agent on a job posting from the extension, or use Test Agent to try it out." />
      )}

      {applications && applications.length > 0 && (
        <div className="flex flex-col gap-2.5">
          {applications.map((app) => (
            <Link key={app.id} to={`/applications/${app.id}`} className="block">
              <Card className="transition-all duration-150 hover:-translate-y-0.5 hover:shadow-card-hover">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className={`truncate font-medium ${app.role_title ? "text-fg" : "italic text-fg-subtle"}`}>
                      {app.role_title ?? "Role not detected"}
                    </p>
                    <p className="mt-0.5 text-xs text-fg-subtle">
                      {app.ats_platform ? (
                        <span className="capitalize">{app.ats_platform}</span>
                      ) : (
                        <span className="text-fg-subtle">Platform not detected</span>
                      )}
                      <span className="mx-1.5 text-fg-subtle">·</span>
                      {new Date(app.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge tone={statusTone(app.status)}>{app.status.replace("_", " ")}</Badge>
                    <svg
                      className="h-4 w-4 shrink-0 text-fg-muted transition-transform group-hover:translate-x-0.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
