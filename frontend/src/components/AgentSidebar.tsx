import { AnimatePresence, motion } from "framer-motion";
import { ChevronLeft, MessageSquarePlus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { marketplaceApi } from "@/api/endpoints";
import type { AgentCard, Conversation } from "@/api/types";
import { AgentIcon } from "@/components/AgentIcon";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { Badge, Skeleton } from "@/components/ui";
import { cn } from "@/lib/cn";
import { useToast } from "@/lib/toast";

/**
 * Replaces the dashboard's generic nav while an agent is open — this agent's
 * branding, capabilities, and its own conversation history, so the sidebar
 * reflects whichever agent you're actually talking to instead of a static
 * global menu.
 */
export function AgentSidebar({
  slug,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onConversationDeleted,
}: {
  slug: string;
  activeConversationId?: string;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onConversationDeleted: (id: string) => void;
}) {
  const [agent, setAgent] = useState<AgentCard | null>(null);
  const [conversations, setConversations] = useState<Conversation[] | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Conversation | null>(null);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    let cancelled = false;
    setAgent(null);
    marketplaceApi.getAgent(slug).then((a) => !cancelled && setAgent(a));
    return () => {
      cancelled = true;
    };
  }, [slug]);

  useEffect(() => {
    let cancelled = false;
    function fetchList() {
      marketplaceApi.listConversations(slug).then((c) => !cancelled && setConversations(c));
    }
    fetchList();
    // AgentChatPage dispatches this after every successful send — covers
    // both a brand-new conversation appearing and the title the backend
    // sets from the first exchange, neither of which this component would
    // otherwise know happened.
    window.addEventListener("lumini:conversations-changed", fetchList);
    return () => {
      cancelled = true;
      window.removeEventListener("lumini:conversations-changed", fetchList);
    };
  }, [slug]);

  async function handleDelete() {
    if (!pendingDelete) return;
    const target = pendingDelete;
    setDeleting(true);
    try {
      await marketplaceApi.deleteConversation(target.id);
      setConversations((prev) => prev?.filter((c) => c.id !== target.id) ?? null);
      setPendingDelete(null);
      if (target.id === activeConversationId) {
        onConversationDeleted(target.id);
      }
      toast.show("Conversation deleted.", "info");
    } catch {
      toast.show("Couldn't delete that conversation.", "error");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="px-3 pb-3">
        <Link
          to="/agents"
          className="mb-3 flex items-center gap-1.5 text-xs font-medium text-fg-subtle transition-colors hover:text-fg"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          All agents
        </Link>

        {agent ? (
          <div className="flex items-center gap-2.5 rounded-lg border border-line bg-surface p-2.5">
            <div
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-white"
              style={{ background: `linear-gradient(135deg, ${agent.accent}, ${agent.accent}99)` }}
            >
              <AgentIcon name={agent.icon} className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-fg">{agent.name}</p>
              {agent.status === "requires_setup" ? (
                <Badge tone="amber" className="mt-0.5">Setup needed</Badge>
              ) : (
                <Badge tone="green" className="mt-0.5">Live</Badge>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2.5 rounded-lg border border-line bg-surface p-2.5">
            <Skeleton className="h-9 w-9 rounded-lg" />
            <Skeleton className="h-4 flex-1" />
          </div>
        )}
      </div>

      <div className="px-3 pb-2">
        <button
          onClick={onNewChat}
          className="flex w-full items-center gap-2 rounded-lg border border-dashed border-line px-3 py-2 text-sm font-medium text-fg-muted transition-colors hover:border-line-strong hover:bg-surface-hover hover:text-fg"
        >
          <MessageSquarePlus className="h-4 w-4" />
          New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3">
        <p className="mb-1.5 px-1 text-[0.65rem] font-semibold uppercase tracking-wider text-fg-subtle">
          History
        </p>

        {conversations === null && (
          <div className="flex flex-col gap-1.5">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-9" />
            ))}
          </div>
        )}

        {conversations?.length === 0 && (
          <p className="px-1 text-xs text-fg-subtle">No conversations yet — start one above.</p>
        )}

        <ul className="flex flex-col gap-0.5">
          <AnimatePresence initial={false}>
            {conversations?.map((c) => (
              <motion.li
                key={c.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.18 }}
              >
                <div
                  className={cn(
                    "group flex items-center gap-1 rounded-lg px-2 py-2 text-sm transition-colors",
                    c.id === activeConversationId
                      ? "bg-brand-500/15 text-brand-300"
                      : "text-fg-muted hover:bg-surface-hover hover:text-fg",
                  )}
                >
                  <button
                    onClick={() => onSelectConversation(c.id)}
                    className="min-w-0 flex-1 truncate text-left"
                    title={c.title}
                  >
                    {c.title}
                  </button>
                  <button
                    onClick={() => setPendingDelete(c)}
                    aria-label={`Delete "${c.title}"`}
                    className="shrink-0 rounded p-1 text-fg-subtle opacity-0 transition-all hover:bg-red-500/10 hover:text-red-400 focus-visible:opacity-100 group-hover:opacity-100"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      </div>

      <ConfirmDialog
        open={pendingDelete !== null}
        onOpenChange={(o) => !o && setPendingDelete(null)}
        title="Delete this conversation?"
        description={
          <>
            <span className="font-medium text-fg">{pendingDelete?.title}</span> and its messages
            will be permanently removed. This cannot be undone.
          </>
        }
        busy={deleting}
        onConfirm={handleDelete}
      />
    </div>
  );
}
