import { useState, type FormEvent } from "react";
import { savedAnswerApi } from "@/api/endpoints";
import { Button, Card, EmptyState, ErrorBanner, FieldLabel, Input, Spinner, Textarea } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";

export default function SavedAnswersPage() {
  const { data: answers, loading, error, refetch } = useAsync(() => savedAnswerApi.list());
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [canonicalKey, setCanonicalKey] = useState("");
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreating(true);
    setFormError(null);
    try {
      await savedAnswerApi.create({
        question_text: question,
        answer_text: answer,
        canonical_key: canonicalKey || undefined,
      });
      setQuestion("");
      setAnswer("");
      setCanonicalKey("");
      refetch();
    } catch (err) {
      setFormError(describeError(err));
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this saved answer?")) return;
    try {
      await savedAnswerApi.remove(id);
      refetch();
    } catch (err) {
      setFormError(describeError(err));
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="mb-4 text-xl font-semibold">Saved answers</h1>
      <p className="mb-4 text-sm text-slate-500">
        Reusable answers to common questions. These give the agent grounded context to draw from instead of
        generating an answer from scratch every time.
      </p>

      <Card className="mb-4">
        <form onSubmit={handleCreate} className="flex flex-col gap-3">
          <div>
            <FieldLabel htmlFor="question">Question</FieldLabel>
            <Input id="question" required value={question} onChange={(e) => setQuestion(e.target.value)} />
          </div>
          <div>
            <FieldLabel htmlFor="answer">Answer</FieldLabel>
            <Textarea id="answer" required rows={3} value={answer} onChange={(e) => setAnswer(e.target.value)} />
          </div>
          <div>
            <FieldLabel htmlFor="canonicalKey">Canonical key (optional)</FieldLabel>
            <Input
              id="canonicalKey"
              placeholder="e.g. salary, visa_status"
              value={canonicalKey}
              onChange={(e) => setCanonicalKey(e.target.value)}
            />
          </div>
          {formError && <ErrorBanner message={formError} />}
          <Button type="submit" disabled={creating} className="w-fit">
            {creating ? "Saving…" : "Add saved answer"}
          </Button>
        </form>
      </Card>

      {loading && <Spinner />}
      {error && <ErrorBanner message={error} />}
      {answers && answers.length === 0 && <EmptyState message="No saved answers yet." />}

      {answers && answers.length > 0 && (
        <div className="flex flex-col gap-3">
          {answers.map((a) => (
            <Card key={a.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{a.question_text}</p>
                  <p className="mt-1 text-sm text-slate-600">{a.answer_text}</p>
                  <p className="mt-1 text-xs text-slate-400">Used {a.usage_count} time(s)</p>
                </div>
                <Button variant="danger" onClick={() => handleDelete(a.id)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
