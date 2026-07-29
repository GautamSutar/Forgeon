import { useEffect, useState } from "react";
import { LoginForm } from "@/popup/components/LoginForm";
import { PreviewPanel } from "@/popup/components/PreviewPanel";
import { ResultPanel } from "@/popup/components/ResultPanel";
import { ScanPanel } from "@/popup/components/ScanPanel";
import { buildSelectorMap } from "@/popup/build-selector-map";
import { callBackground, callContentScript, MessagingError } from "@/lib/messaging";
import type { AgentRunResponse, ExtractedForm } from "@/lib/types";

interface ResumeSummary {
  id: string;
  filename: string;
  is_default: boolean;
}

type View = "loading" | "login" | "scan" | "preview" | "result";

export default function App() {
  const [view, setView] = useState<View>("loading");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string | undefined>(undefined);
  const [extractedForm, setExtractedForm] = useState<ExtractedForm | null>(null);
  const [jobDescription, setJobDescription] = useState("");

  const [runResponse, setRunResponse] = useState<AgentRunResponse | null>(null);
  const [editedAnswers, setEditedAnswers] = useState<Record<string, string>>({});
  const [fillFailures, setFillFailures] = useState<string[]>([]);
  const [finalStatus, setFinalStatus] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    try {
      const { authenticated } = await callBackground<{ authenticated: boolean }>({ type: "GET_AUTH_STATE" });
      if (!authenticated) {
        setView("login");
        return;
      }
      await enterScanView();
    } catch (err) {
      setError(describeError(err));
      setView("login");
    }
  }

  async function enterScanView() {
    setError(null);
    setView("scan");
    try {
      const [form, resumeList] = await Promise.all([
        callContentScript<ExtractedForm>({ type: "EXTRACT_FORM" }),
        callBackground<ResumeSummary[]>({ type: "LIST_RESUMES" }).catch(() => []),
      ]);
      setExtractedForm(form);
      setJobDescription(form.jobDescriptionGuess);
      setResumes(resumeList);
      const defaultResume = resumeList.find((r) => r.is_default);
      setSelectedResumeId(defaultResume?.id);
    } catch (err) {
      setError(
        `Couldn't read this page's form: ${describeError(err)}. Make sure you're on a job application page and try again.`,
      );
    }
  }

  async function handleLogin(email: string, password: string) {
    setBusy(true);
    setError(null);
    try {
      await callBackground({ type: "LOGIN", email, password });
      await enterScanView();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleAnalyze() {
    if (!extractedForm) return;
    setBusy(true);
    setError(null);
    try {
      const response = await callBackground<AgentRunResponse>({
        type: "RUN_AGENT",
        html: extractedForm.html,
        jobDescription,
        resumeId: selectedResumeId,
      });
      setRunResponse(response);
      setEditedAnswers({});
      if (response.status === "interrupted") {
        setView("preview");
      } else {
        setFinalStatus(response.application_status);
        setView("result");
      }
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleApprove() {
    if (!runResponse || !extractedForm) return;
    setBusy(true);
    setError(null);
    try {
      const response = await callBackground<AgentRunResponse>({
        type: "APPROVE_RUN",
        runId: runResponse.run_id,
        editedAnswers,
      });

      const approvedAnswers: Record<string, string> = {};
      const previewAnswers = runResponse.preview?.answers ?? {};
      for (const [key, entry] of Object.entries(previewAnswers)) {
        approvedAnswers[key] = editedAnswers[key] ?? entry.answer;
      }

      const selectorMap = buildSelectorMap(extractedForm.fields);
      const fieldsBySelector: Record<string, string> = {};
      const failures: string[] = [];
      for (const [key, value] of Object.entries(approvedAnswers)) {
        const selector = selectorMap[key];
        if (selector) {
          fieldsBySelector[selector] = value;
        } else {
          failures.push(key);
        }
      }

      if (Object.keys(fieldsBySelector).length > 0) {
        await callContentScript({ type: "FILL_FIELDS", answers: approvedAnswers, fieldsBySelector });
      }

      setFillFailures(failures);
      setFinalStatus(response.application_status);
      setView("result");
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleReject() {
    if (!runResponse) return;
    setBusy(true);
    setError(null);
    try {
      const response = await callBackground<AgentRunResponse>({
        type: "REJECT_RUN",
        runId: runResponse.run_id,
        reason: "Rejected from extension popup",
      });
      setFinalStatus(response.application_status ?? "rejected");
      setFillFailures([]);
      setView("result");
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  function handleStartOver() {
    setRunResponse(null);
    setEditedAnswers({});
    setFillFailures([]);
    setFinalStatus(null);
    void enterScanView();
  }

  if (view === "loading") {
    return <div className="p-4 text-sm text-slate-500">Loading…</div>;
  }

  return (
    <div>
      {error && (
        <div className="m-2 rounded border border-red-300 bg-red-50 p-2 text-xs text-red-700">{error}</div>
      )}

      {view === "login" && <LoginForm onSubmit={handleLogin} busy={busy} error={null} />}

      {view === "scan" && (
        <ScanPanel
          jobDescription={jobDescription}
          onJobDescriptionChange={setJobDescription}
          resumes={resumes}
          selectedResumeId={selectedResumeId}
          onSelectResume={setSelectedResumeId}
          onAnalyze={handleAnalyze}
          busy={busy}
          fieldCount={extractedForm?.fields.length ?? null}
          platform={extractedForm?.platform ?? null}
        />
      )}

      {view === "preview" && runResponse?.preview && (
        <PreviewPanel
          answers={runResponse.preview.answers}
          edited={editedAnswers}
          onEdit={(key, value) => setEditedAnswers((prev) => ({ ...prev, [key]: value }))}
          validationErrors={runResponse.preview.validation_errors}
          onApprove={handleApprove}
          onReject={handleReject}
          busy={busy}
        />
      )}

      {view === "result" && (
        <ResultPanel status={finalStatus} fillFailures={fillFailures} onStartOver={handleStartOver} />
      )}
    </div>
  );
}

function describeError(err: unknown): string {
  if (err instanceof MessagingError) return err.message;
  if (err instanceof Error) return err.message;
  return String(err);
}
