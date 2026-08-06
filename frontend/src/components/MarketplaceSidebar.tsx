import { LayoutGrid } from "lucide-react";
import { useEffect, useState } from "react";
import { marketplaceApi } from "@/api/endpoints";
import type { AgentCard } from "@/api/types";
import { Skeleton } from "@/components/ui";
import { cn } from "@/lib/cn";

/**
 * Replaces the dashboard's Workspace/Account nav while browsing the
 * marketplace itself (/agents, not a specific /agents/:slug) — categories to
 * browse by instead of links to pages that aren't relevant until you've
 * actually opened an agent. Applications/Resumes/Saved Answers/Profile stay
 * reachable via the command palette (⌘K) in the meantime.
 */
export function MarketplaceSidebar({
  activeCategory,
  onSelectCategory,
}: {
  activeCategory: string | null;
  onSelectCategory: (category: string | null) => void;
}) {
  const [agents, setAgents] = useState<AgentCard[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    marketplaceApi.listAgents().then((a) => !cancelled && setAgents(a));
    return () => {
      cancelled = true;
    };
  }, []);

  const counts = new Map<string, number>();
  for (const a of agents ?? []) counts.set(a.category, (counts.get(a.category) ?? 0) + 1);
  const categories = Array.from(counts.keys()).sort();

  return (
    <div className="flex h-full flex-col px-3">
      <p className="mb-1.5 px-1 text-[0.65rem] font-semibold uppercase tracking-wider text-fg-subtle">
        Browse
      </p>

      {agents === null ? (
        <div className="flex flex-col gap-1.5">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-9" />
          ))}
        </div>
      ) : (
        <ul className="flex flex-col gap-0.5">
          <li>
            <button
              onClick={() => onSelectCategory(null)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                activeCategory === null
                  ? "bg-brand-500/15 text-brand-300"
                  : "text-fg-muted hover:bg-surface-hover hover:text-fg",
              )}
            >
              <LayoutGrid className="h-[18px] w-[18px] shrink-0" />
              <span className="flex-1 truncate text-left">All agents</span>
              <span className="text-xs text-fg-subtle">{agents.length}</span>
            </button>
          </li>
          {categories.map((c) => (
            <li key={c}>
              <button
                onClick={() => onSelectCategory(c)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  activeCategory === c
                    ? "bg-brand-500/15 text-brand-300"
                    : "text-fg-muted hover:bg-surface-hover hover:text-fg",
                )}
              >
                <span
                  className={cn(
                    "flex h-[18px] w-[18px] shrink-0 items-center justify-center",
                    activeCategory === c ? "text-brand-400" : "text-fg-subtle",
                  )}
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-current" />
                </span>
                <span className="flex-1 truncate text-left">{c}</span>
                <span className="text-xs text-fg-subtle">{counts.get(c)}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
