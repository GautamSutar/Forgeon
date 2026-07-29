import { useState } from "react";
import { Link } from "react-router-dom";
import { agentApi, resumeApi } from "@/api/endpoints";
import type { AgentRunResponse } from "@/api/types";
import { Badge, Button, Card, ErrorBanner, FieldLabel, Textarea } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";

export default function AgentRunPage() {
  const { data: resumes } = useAsync(() => resumeApi.list());
  const [html, setHtml] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeId, setResumeId] = useState<string | undefined>(undefined);

  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runResponse, setRunResponse] = useState<AgentRunResponse | null>(null);
  const [editedAnswers, setEditedAnswers] = useState<Record<string, string>>({});

  async function handleRun() {
    setRunning(true);
    setError(null);
    setRunResponse(null);
    setEditedAnswers({});
    try {
      const response = await agentApi.run(html, jobDescription, resumeId);
      setRunResponse(response);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setRunning(false);
    }
  }

  async function handleApprove() {
    if (!runResponse) return;
    setRunning(true);
    setError(null);
    try {
      const response = await agentApi.approve(runResponse.run_id, editedAnswers);
      setRunResponse(response);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setRunning(false);
    }
  }

  async function handleReject() {
    if (!runResponse) return;
    setRunning(true);
    setError(null);
    try {
      const response = await agentApi.reject(runResponse.run_id, "Rejected from dashboard");
      setRunResponse(response);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setRunning(false);
    }
  }

  const preview = runResponse?.preview;

  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-xl font-semibold">Test Agent — Developer Tool</h1>

      <div className="mb-4 rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
        <p className="font-medium">This is not how you apply to real jobs.</p>
        <p className="mt-1">
          For actual job applications, use the <span className="font-medium">browser extension</span> on a real job
          posting — it reads the live page and can fill the real form. This page exists only to test the backend's
          AI pipeline (field extraction, grounded answer generation, human approval) by hand, without needing the
          extension or a real browser tab. Paste raw form HTML below and nothing gets filled into any actual
          page — it just exercises the same approve/reject flow the extension uses.
        </p>
      </div>

      {!runResponse && (
        <Card className="flex flex-col gap-3">
          <div>
            <FieldLabel htmlFor="html">Form HTML</FieldLabel>
            <Textarea
              id="html"
              rows={6}
              value={html}
              onChange={(e) => setHtml(e.target.value)}
              placeholder="<form>...</form>"
            />
          </div>
          <div>
            <FieldLabel htmlFor="jd">Job description</FieldLabel>
            <Textarea
              id="jd"
              rows={6}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>
          {resumes && resumes.length > 0 && (
            <div>
              <FieldLabel htmlFor="resume">Resume</FieldLabel>
              <select
                id="resume"
                value={resumeId ?? ""}
                onChange={(e) => setResumeId(e.target.value || undefined)}
                className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">Default resume</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.filename}
                  </option>
                ))}
              </select>
            </div>
          )}
          {error && <ErrorBanner message={error} />}
          <Button onClick={handleRun} disabled={running || !html.trim() || !jobDescription.trim()} className="w-fit">
            {running ? "Running…" : "Run agent"}
          </Button>
        </Card>
      )}

      {runResponse?.status === "interrupted" && preview && (
        <Card className="mt-4 flex flex-col gap-3">
          <h2 className="font-medium">Review generated answers</h2>

          {preview.validation_errors.length > 0 && (
            <div className="rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800">
              <p className="font-medium">Validation warnings:</p>
              <ul className="list-disc pl-4">
                {preview.validation_errors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-col gap-3">
            {Object.entries(preview.answers).map(([fieldKey, entry]) => (
              <div key={fieldKey} className="rounded border border-slate-200 p-2">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-700">{fieldKey}</span>
                  <Badge tone={entry.refused ? "amber" : entry.source === "profile" ? "green" : "blue"}>
                    {entry.refused ? "refused" : entry.source}
                  </Badge>
                </div>
                <Textarea
                  rows={2}
                  value={editedAnswers[fieldKey] ?? entry.answer}
                  onChange={(e) => setEditedAnswers((prev) => ({ ...prev, [fieldKey]: e.target.value }))}
                />
              </div>
            ))}
          </div>

          {error && <ErrorBanner message={error} />}

          <div className="flex gap-2">
            <Button variant="secondary" onClick={handleReject} disabled={running}>
              Reject
            </Button>
            <Button onClick={handleApprove} disabled={running}>
              {running ? "Submitting…" : "Approve"}
            </Button>
          </div>
        </Card>
      )}

      {runResponse?.status === "completed" && (
        <Card className="mt-4">
          <p className="font-medium">
            Run finished — application status:{" "}
            <Badge tone={runResponse.application_status === "submitted" ? "green" : "red"}>
              {runResponse.application_status ?? "unknown"}
            </Badge>
          </p>
          {runResponse.application_id && (
            <Link to={`/applications/${runResponse.application_id}`} className="mt-2 inline-block text-sm text-blue-600">
              View application →
            </Link>
          )}
          <div className="mt-3">
            <Button
              variant="secondary"
              onClick={() => {
                setRunResponse(null);
                setHtml("");
                setJobDescription("");
              }}
            >
              Run another
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
