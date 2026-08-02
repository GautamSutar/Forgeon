import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { marketplaceApi } from "@/api/endpoints";
import type { ChatMessage } from "@/api/types";
import { AgentIcon } from "@/components/AgentIcon";
import { Markdown } from "@/components/Markdown";
import { Badge, Button, ErrorBanner, Textarea } from "@/components/ui";
import { PageLoader } from "@/components/PageLoader";
import { describeError, useAsync } from "@/lib/useAsync";

export default function AgentChatPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const conversationParam = searchParams.get("c");
  const { data: agent, loading, error } = useAsync(() => marketplaceApi.getAgent(slug!), [slug]);

  // DashboardLayout remounts this page whenever the path or ?c= changes (it
  // keys the outlet on pathname+search), so these only need to seed once per
  // mount rather than being reset by a slug-watching effect.
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(conversationParam ?? undefined);
  const [loadingConversation, setLoadingConversation] = useState(Boolean(conversationParam));
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Opened via the sidebar's history list or a shared link — load that
  // conversation's transcript instead of starting blank.
  useEffect(() => {
    if (!conversationParam) return;
    let cancelled = false;
    marketplaceApi
      .getConversation(conversationParam)
      .then((detail) => {
        if (cancelled) return;
        setMessages(detail.messages);
        setConversationId(detail.id);
      })
      .catch(() => {
        if (!cancelled) setSendError("Couldn't load that conversation.");
      })
      .finally(() => {
        if (!cancelled) setLoadingConversation(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  if (loading || loadingConversation) return <PageLoader label="Loading agent" />;
  if (error) return <ErrorBanner message={error} />;
  if (!agent) return null;

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || sending) return;

    const optimistic: ChatMessage = {
      id: `local-${Date.now()}`,
      role: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);
    setDraft("");
    setSending(true);
    setSendError(null);

    try {
      const response = await marketplaceApi.chat(agent!.slug, trimmed, conversationId);
      const isNewConversation = !conversationId;
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.message]);

      // Reflect a newly-created conversation in the URL (so the sidebar can
      // highlight it, and a refresh reopens the same thread) without adding
      // a history entry per message.
      if (isNewConversation) {
        navigate(`/agents/${agent!.slug}?c=${response.conversation_id}`, { replace: true });
      }
      // Tells AgentSidebar to refetch this agent's conversation list — picks
      // up both a brand-new conversation appearing and the title the backend
      // sets from the first exchange.
      window.dispatchEvent(new Event("lumini:conversations-changed"));
    } catch (err) {
      setSendError(describeError(err));
      // Roll the optimistic turn back out so the transcript doesn't show a
      // message the server never accepted, and hand the text back to the box.
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id));
      setDraft(trimmed);
    } finally {
      setSending(false);
    }
  }

  const locked = agent.status === "requires_setup";

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      {/* Header */}
      <div className="mb-4 flex items-start gap-4">
        <button
          onClick={() => navigate("/agents")}
          className="mt-1 rounded-lg p-1.5 text-fg-subtle transition-colors hover:bg-surface-hover hover:text-fg"
          title="Back to marketplace"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-white"
          style={{
            background: `linear-gradient(135deg, ${agent.accent}, ${agent.accent}99)`,
            boxShadow: `0 8px 20px -6px ${agent.accent}88`,
          }}
        >
          <AgentIcon name={agent.icon} className="h-6 w-6" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-fg">{agent.name}</h1>
            {locked ? <Badge tone="amber">Setup needed</Badge> : <Badge tone="green">Live</Badge>}
          </div>
          <p className="mt-0.5 text-sm text-fg-muted">{agent.description}</p>
        </div>
        {agent.route && (
          <Link to={agent.route}>
            <Button variant="secondary">Open tool</Button>
          </Link>
        )}
      </div>

      {locked && agent.setup_hint && (
        <div className="mb-4 flex gap-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">
          <svg className="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M18 10A8 8 0 112 10a8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"
              clipRule="evenodd"
            />
          </svg>
          <p>
            <span className="font-medium">This agent needs setup. </span>
            {agent.setup_hint} You can still chat with it about the parts that don&apos;t need that
            provider.
          </p>
        </div>
      )}

      {/* Transcript */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-line bg-bg-elevated/50 p-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-5 text-center">
            <div
              className="flex h-14 w-14 animate-float items-center justify-center rounded-2xl text-white"
              style={{
                background: `linear-gradient(135deg, ${agent.accent}, ${agent.accent}99)`,
                boxShadow: `0 12px 32px -8px ${agent.accent}aa`,
              }}
            >
              <AgentIcon name={agent.icon} className="h-7 w-7" />
            </div>
            <div>
              <p className="font-medium text-fg">{agent.tagline}</p>
              <p className="mt-1 text-sm text-fg-subtle">Start with one of these, or ask anything.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {agent.example_prompts.map((p) => (
                <button
                  key={p}
                  onClick={() => void send(p)}
                  className="rounded-full border border-line bg-surface px-3.5 py-2 text-xs text-fg-muted transition-all hover:border-line-strong hover:bg-surface-hover hover:text-fg"
                >
                  {p}
                </button>
              ))}
            </div>
            <div className="mt-2 grid max-w-lg gap-1.5">
              {agent.capabilities.map((c) => (
                <div key={c} className="flex items-center gap-2 text-xs text-fg-subtle">
                  <svg className="h-3.5 w-3.5 shrink-0" viewBox="0 0 20 20" fill={agent.accent}>
                    <path
                      fillRule="evenodd"
                      d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {c}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} accent={agent.accent} icon={agent.icon} />
          ))}
          {sending && (
            <TypingIndicator
              accent={agent.accent}
              icon={agent.icon}
              note={agent.slug === "image" ? "Generating — can take up to a minute on a cold model…" : undefined}
            />
          )}
        </div>
        <div ref={endRef} />
      </div>

      {sendError && (
        <div className="mt-3">
          <ErrorBanner message={sendError} />
        </div>
      )}

      {/* Composer */}
      <div className="mt-3 flex items-end gap-2">
        <Textarea
          rows={2}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            // Enter sends; Shift+Enter inserts a newline.
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send(draft);
            }
          }}
          placeholder={agent.slug === "image" ? "Describe the image to generate…" : `Message ${agent.name}…`}
          className="resize-none"
        />
        <Button onClick={() => void send(draft)} disabled={sending || !draft.trim()} className="h-[42px]">
          {sending ? "Sending…" : "Send"}
        </Button>
      </div>
      <p className="mt-1.5 text-center text-xs text-fg-subtle">
        Enter to send · Shift+Enter for a new line
      </p>
    </div>
  );
}

function MessageBubble({ message, accent, icon }: { message: ChatMessage; accent: string; icon: string }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex animate-fade-in-up gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white ${isUser ? "bg-surface-hover" : ""}`}
        style={isUser ? undefined : { background: `linear-gradient(135deg, ${accent}, ${accent}99)` }}
      >
        {isUser ? (
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <AgentIcon name={icon} className="h-4 w-4" />
        )}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "whitespace-pre-wrap rounded-tr-sm bg-brand-600 text-white"
            : "rounded-tl-sm border border-line bg-surface text-fg"
        }`}
      >
        {/* User turns are literal text the person typed — parsing them as
            markdown would reformat their own words. Only agent replies,
            which are authored in markdown, get rendered. */}
        {isUser ? message.content : <Markdown content={message.content} />}
      </div>
    </div>
  );
}

function TypingIndicator({ accent, icon, note }: { accent: string; icon: string; note?: string }) {
  return (
    <div className="flex animate-fade-in-up gap-3">
      <div
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white"
        style={{ background: `linear-gradient(135deg, ${accent}, ${accent}99)` }}
      >
        <AgentIcon name={icon} className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-2.5 rounded-2xl rounded-tl-sm border border-line bg-surface px-4 py-3">
        <div className="flex items-center gap-1.5">
          {[0, 150, 300].map((delay) => (
            <span
              key={delay}
              className="h-1.5 w-1.5 animate-bounce rounded-full bg-fg-subtle"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </div>
        {note && <span className="text-xs text-fg-subtle">{note}</span>}
      </div>
    </div>
  );
}
