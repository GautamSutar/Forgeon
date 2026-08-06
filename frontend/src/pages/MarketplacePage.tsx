import { motion } from "framer-motion";
import { ArrowRight, Download, Search, Star } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { marketplaceApi } from "@/api/endpoints";
import type { AgentCard as AgentCardType } from "@/api/types";
import { AgentIcon } from "@/components/AgentIcon";
import { TiltCard } from "@/components/TiltCard";
import { Badge, Button, ErrorBanner, Input, PageHeader, Skeleton } from "@/components/ui";
import { cn } from "@/lib/cn";
import { useAsync } from "@/lib/useAsync";

export default function MarketplacePage() {
  const { data: agents, loading, error } = useAsync(() => marketplaceApi.listAgents());
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  // URL-driven (?category=) rather than local state, so MarketplaceSidebar —
  // a sibling under the same layout, not a parent/child of this page — can
  // read and set it too without lifting state through a shared ancestor.
  const [searchParams, setSearchParams] = useSearchParams();
  const category = searchParams.get("category");

  function setCategory(next: string | null) {
    setSearchParams(next ? { category: next } : {}, { replace: true });
  }

  const categories = useMemo(
    () => (agents ? Array.from(new Set(agents.map((a) => a.category))) : []),
    [agents],
  );

  const filtered = useMemo(() => {
    if (!agents) return [];
    const q = query.trim().toLowerCase();
    return agents.filter((a) => {
      // A typed search searches every agent, not just the currently
      // selected category — combining both as a strict AND meant typing
      // into the box while a narrow category was active (e.g. "Productivity",
      // 1 agent) silently returned nothing unless that one agent happened to
      // match the query, which read as "search is broken."
      if (!q && category && a.category !== category) return false;
      if (!q) return true;
      return `${a.name} ${a.tagline} ${a.category} ${a.tags.join(" ")} ${a.capabilities.join(" ")}`
        .toLowerCase()
        .includes(q);
    });
  }, [agents, query, category]);

  return (
    <div>
      <PageHeader
        title="Agent Marketplace"
        subtitle="Specialized agents for applications, email, research, code and more. Each ships with its own capabilities and honest limits."
        actions={
          agents && (
            <div className="flex items-center gap-4 text-sm">
              <div className="text-right">
                <p className="font-semibold text-fg">{agents.length}</p>
                <p className="text-xs text-fg-subtle">Agents</p>
              </div>
              <div className="h-8 w-px bg-line" />
              <div className="text-right">
                <p className="font-semibold text-fg">
                  {agents.filter((a) => a.status === "live").length}
                </p>
                <p className="text-xs text-fg-subtle">Live</p>
              </div>
            </div>
          )
        }
      />

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="relative min-w-[16rem] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-fg-subtle" />
          <Input
            className="pl-9"
            placeholder="Search agents, tags, capabilities…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          <Chip active={category === null} onClick={() => setCategory(null)}>All</Chip>
          {categories.map((c) => (
            <Chip key={c} active={category === c} onClick={() => setCategory(c)}>{c}</Chip>
          ))}
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {loading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-64" />)}
        </div>
      )}

      {agents && filtered.length === 0 && (
        <p className="rounded-xl border border-dashed border-line p-12 text-center text-sm text-fg-subtle">
          No agents match “{query}”.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((agent, i) => (
          <motion.div
            key={agent.slug}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: Math.min(i, 8) * 0.05, ease: [0.16, 1, 0.3, 1] }}
          >
            <AgentTile agent={agent} onOpen={() => navigate(`/agents/${agent.slug}`)} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
        active
          ? "border-brand-500/40 bg-brand-500/15 text-brand-300"
          : "border-line bg-surface text-fg-muted hover:border-line-strong hover:text-fg",
      )}
    >
      {children}
    </button>
  );
}

function AgentTile({ agent, onOpen }: { agent: AgentCardType; onOpen: () => void }) {
  const locked = agent.status === "requires_setup";

  return (
    <TiltCard accent={agent.accent} className="group h-full">
      <div className="flex h-full flex-col p-5">
        <div className="preserve-3d flex items-start justify-between">
          <div
            className="translate-z-4 flex h-12 w-12 items-center justify-center rounded-xl text-white"
            style={{
              background: `linear-gradient(135deg, ${agent.accent}, ${agent.accent}aa)`,
              boxShadow: `0 10px 24px -8px ${agent.accent}`,
            }}
          >
            <AgentIcon name={agent.icon} />
          </div>
          {locked ? <Badge tone="amber">Setup needed</Badge> : <Badge tone="green">Live</Badge>}
        </div>

        <div className="preserve-3d mt-4">
          <div className="flex items-center gap-2">
            <h3 className="translate-z-8 font-semibold text-fg">{agent.name}</h3>
            <span className="text-[0.65rem] text-fg-subtle">v{agent.version}</span>
          </div>
          <p className="mt-1 text-sm leading-relaxed text-fg-muted">{agent.tagline}</p>
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5">
          {agent.tags.slice(0, 3).map((t) => (
            <span
              key={t}
              className="rounded-md border border-line bg-surface-hover px-1.5 py-0.5 text-[0.65rem] text-fg-subtle"
            >
              {t}
            </span>
          ))}
        </div>

        {/* Meta row — rating / installs / creator */}
        <div className="mt-4 flex items-center gap-3 text-xs text-fg-subtle">
          <span className="flex items-center gap-1">
            <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
            <span className="font-medium text-fg-muted">{agent.rating.toFixed(1)}</span>
          </span>
          <span className="flex items-center gap-1">
            <Download className="h-3.5 w-3.5" />
            {agent.installs.toLocaleString()}
          </span>
          <span className="ml-auto truncate">by {agent.creator}</span>
        </div>

        <div className="mt-4 flex items-center gap-2 border-t border-line pt-4">
          <Button onClick={onOpen} className="flex-1" size="sm">
            Open <ArrowRight className="h-3.5 w-3.5" />
          </Button>
          <span className="text-[0.65rem] uppercase tracking-wide text-fg-subtle">
            {agent.category}
          </span>
        </div>
      </div>
    </TiltCard>
  );
}
