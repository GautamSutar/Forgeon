import { useRef, useState } from "react";
import { resumeApi } from "@/api/endpoints";
import { Badge, Button, Card, CardSkeletonList, EmptyState, ErrorBanner, PageHeader } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";
import { useToast } from "@/lib/toast";

export default function ResumesPage() {
  const { data: resumes, loading, error, refetch } = useAsync(() => resumeApi.list());
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const toast = useToast();

  async function handleUpload() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setActionError(null);
    try {
      const hasResumes = (resumes?.length ?? 0) > 0;
      await resumeApi.upload(file, !hasResumes);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setSelectedName(null);
      toast.show("Resume uploaded and parsed.");
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    } finally {
      setUploading(false);
    }
  }

  async function handleSetDefault(id: string) {
    setActionError(null);
    try {
      await resumeApi.setDefault(id);
      toast.show("Default resume updated.");
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this resume? This cannot be undone.")) return;
    setActionError(null);
    try {
      await resumeApi.remove(id);
      toast.show("Resume deleted.", "info");
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    }
  }

  return (
    <div className="max-w-3xl">
      <PageHeader title="Resumes" subtitle="Upload PDF resumes and choose which one the agent uses by default." />

      <Card className="mb-4">
        <label
          htmlFor="resume-file"
          className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-line px-4 py-6 text-center transition-colors hover:border-brand-500/50 hover:bg-brand-500/10"
        >
          <svg className="h-7 w-7 text-fg-subtle" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0L7 9m5-5l5 5M5 20h14" />
          </svg>
          <p className="text-sm text-fg-subtle">
            {selectedName ?? <><span className="font-medium text-brand-400">Choose a PDF</span> or drop it here</>}
          </p>
          <input
            id="resume-file"
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => setSelectedName(e.target.files?.[0]?.name ?? null)}
          />
        </label>

        <div className="mt-3 flex justify-end">
          <Button onClick={handleUpload} disabled={uploading || !selectedName}>
            {uploading ? "Uploading…" : "Upload"}
          </Button>
        </div>

        {actionError && (
          <div className="mt-3">
            <ErrorBanner message={actionError} />
          </div>
        )}
      </Card>

      {loading && <CardSkeletonList count={2} />}
      {error && <ErrorBanner message={error} />}

      {resumes && resumes.length === 0 && <EmptyState message="No resumes uploaded yet." />}

      {resumes && resumes.length > 0 && (
        <div className="flex flex-col gap-3">
          {resumes.map((resume) => (
            <Card key={resume.id} className="transition-shadow hover:shadow-card-hover">
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-500/10 text-brand-400">
                    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-medium text-fg">{resume.filename}</p>
                    <p className="text-xs text-fg-subtle">
                      Uploaded {new Date(resume.created_at).toLocaleDateString()}
                      {resume.parsed_data?.skills?.length ? ` · ${resume.parsed_data.skills.length} skills detected` : ""}
                    </p>
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  {resume.is_default && <Badge tone="green">Default</Badge>}
                  {!resume.is_default && (
                    <Button variant="secondary" onClick={() => handleSetDefault(resume.id)}>
                      Set default
                    </Button>
                  )}
                  <Button variant="danger" onClick={() => handleDelete(resume.id)}>
                    Delete
                  </Button>
                </div>
              </div>

              {resume.parsed_data?.skills && resume.parsed_data.skills.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5 border-t border-line pt-3">
                  {resume.parsed_data.skills.slice(0, 12).map((skill) => (
                    <Badge key={skill}>{skill}</Badge>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
