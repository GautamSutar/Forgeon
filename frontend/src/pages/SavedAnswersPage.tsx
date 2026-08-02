import { useState, type FormEvent } from "react";
import { savedAnswerApi } from "@/api/endpoints";
import { Button, Card, CardSkeletonList, EmptyState, ErrorBanner, FieldLabel, Input, PageHeader, Textarea } from "@/components/ui";
import { describeError, useAsync } from "@/lib/useAsync";
import { useToast } from "@/lib/toast";

export default function SavedAnswersPage() {
  const { data: answers, loading, error, refetch } = useAsync(() => savedAnswerApi.list());
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [canonicalKey, setCanonicalKey] = useState("");
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const toast = useToast();

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
      toast.show("Saved answer added.");
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
      toast.show("Saved answer deleted.", "info");
      refetch();
    } catch (err) {
      setFormError(describeError(err));
    }
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Saved answers"
        subtitle="Reusable answers to common questions. These give the agent grounded context to draw from instead of generating an answer from scratch every time."
      />

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

      {loading && <CardSkeletonList count={2} />}
      {error && <ErrorBanner message={error} />}
      {answers && answers.length === 0 && <EmptyState message="No saved answers yet." />}

      {answers && answers.length > 0 && (
        <div className="flex flex-col gap-3">
          {answers.map((a) => (
            <Card key={a.id} className="transition-shadow hover:shadow-card-hover">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium text-fg">{a.question_text}</p>
                  <p className="mt-1 text-sm text-fg-muted">{a.answer_text}</p>
                  <p className="mt-1.5 text-xs text-fg-subtle">Used {a.usage_count} time(s)</p>
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
