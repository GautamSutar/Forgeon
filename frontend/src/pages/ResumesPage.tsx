import { useRef, useState } from "react";
import { resumeApi } from "@/api/endpoints";
import { Badge, Button, Card, EmptyState, ErrorBanner, Spinner } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";

export default function ResumesPage() {
  const { data: resumes, loading, error, refetch } = useAsync(() => resumeApi.list());
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleUpload() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setActionError(null);
    try {
      const hasResumes = (resumes?.length ?? 0) > 0;
      await resumeApi.upload(file, !hasResumes);
      if (fileInputRef.current) fileInputRef.current.value = "";
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
      refetch();
    } catch (err) {
      setActionError(describeError(err));
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="mb-4 text-xl font-semibold">Resumes</h1>

      <Card className="mb-4">
        <div className="flex items-center gap-3">
          <input ref={fileInputRef} type="file" accept="application/pdf" className="text-sm" />
          <Button onClick={handleUpload} disabled={uploading}>
            {uploading ? "Uploading…" : "Upload PDF"}
          </Button>
        </div>
        {actionError && (
          <div className="mt-3">
            <ErrorBanner message={actionError} />
          </div>
        )}
      </Card>

      {loading && <Spinner />}
      {error && <ErrorBanner message={error} />}

      {resumes && resumes.length === 0 && <EmptyState message="No resumes uploaded yet." />}

      {resumes && resumes.length > 0 && (
        <div className="flex flex-col gap-3">
          {resumes.map((resume) => (
            <Card key={resume.id}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{resume.filename}</p>
                  <p className="text-xs text-slate-500">
                    Uploaded {new Date(resume.created_at).toLocaleDateString()}
                    {resume.parsed_data?.skills?.length ? ` · ${resume.parsed_data.skills.length} skills detected` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-2">
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
                <div className="mt-2 flex flex-wrap gap-1">
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
