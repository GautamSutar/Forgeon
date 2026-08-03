import * as Dialog from "@radix-ui/react-dialog";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  Braces,
  Command as CommandIcon,
  CornerDownLeft,
  FileText,
  LayoutGrid,
  Moon,
  Search,
  Sparkles,
  Sun,
  User,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { marketplaceApi } from "@/api/endpoints";
import type { AgentCard } from "@/api/types";
import { Kbd } from "@/components/ui";
import { cn } from "@/lib/cn";
import { useTheme } from "@/lib/theme";

interface Command {
  id: string;
  label: string;
  hint?: string;
  group: string;
  icon: React.ReactNode;
  run: () => void;
  keywords?: string;
}

/**
 * Raycast/VS Code style command palette. Opens on Ctrl/Cmd+K anywhere.
 *
 * The agent list is fetched once on first open and cached — reopening the
 * palette shouldn't re-hit the network on every keystroke or toggle.
 */
export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [agents, setAgents] = useState<AgentCard[] | null>(null);
  const navigate = useNavigate();
  const { setTheme } = useTheme();
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    const onOpen = () => setOpen(true);
    window.addEventListener("keydown", onKey);
    window.addEventListener("luminai:open-palette", onOpen);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("luminai:open-palette", onOpen);
    };
  }, []);

  useEffect(() => {
    if (!open || agents) return;
    marketplaceApi
      .listAgents()
      .then(setAgents)
      .catch(() => setAgents([]));
  }, [open, agents]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
    }
  }, [open]);

  const go = useCallback(
    (to: string) => () => {
      setOpen(false);
      navigate(to);
    },
    [navigate],
  );

  const commands = useMemo<Command[]>(() => {
    const nav: Command[] = [
      { id: "n-market", label: "Agent Marketplace", group: "Navigate", icon: <LayoutGrid className="h-4 w-4" />, run: go("/agents") },
      { id: "n-apps", label: "Applications", group: "Navigate", icon: <FileText className="h-4 w-4" />, run: go("/applications") },
      { id: "n-resumes", label: "Resumes", group: "Navigate", icon: <FileText className="h-4 w-4" />, run: go("/resumes") },
      { id: "n-saved", label: "Saved Answers", group: "Navigate", icon: <Braces className="h-4 w-4" />, run: go("/saved-answers") },
      { id: "n-profile", label: "Profile", group: "Navigate", icon: <User className="h-4 w-4" />, run: go("/profile") },
    ];

    const agentCmds: Command[] = (agents ?? []).map((a) => ({
      id: `a-${a.slug}`,
      label: a.name,
      hint: a.tagline,
      group: "Run agent",
      keywords: `${a.category} ${a.tags.join(" ")}`,
      icon: <Sparkles className="h-4 w-4" style={{ color: a.accent }} />,
      run: go(`/agents/${a.slug}`),
    }));

    const theme: Command[] = [
      { id: "t-dark", label: "Theme: Dark", group: "Preferences", icon: <Moon className="h-4 w-4" />, run: () => { setTheme("dark"); setOpen(false); } },
      { id: "t-light", label: "Theme: Light", group: "Preferences", icon: <Sun className="h-4 w-4" />, run: () => { setTheme("light"); setOpen(false); } },
      { id: "t-system", label: "Theme: System", group: "Preferences", icon: <CommandIcon className="h-4 w-4" />, run: () => { setTheme("system"); setOpen(false); } },
    ];

    return [...agentCmds, ...nav, ...theme];
  }, [agents, go, setTheme]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter((c) =>
      `${c.label} ${c.hint ?? ""} ${c.group} ${c.keywords ?? ""}`.toLowerCase().includes(q),
    );
  }, [commands, query]);

  // Clamp the cursor whenever filtering shrinks the list, so it can't point
  // past the end and "Enter" can never fire nothing.
  useEffect(() => setActive((i) => Math.min(i, Math.max(0, filtered.length - 1))), [filtered.length]);

  const grouped = useMemo(() => {
    const out: Record<string, Command[]> = {};
    for (const c of filtered) (out[c.group] ??= []).push(c);
    return out;
  }, [filtered]);

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => (i + 1) % Math.max(1, filtered.length));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => (i - 1 + filtered.length) % Math.max(1, filtered.length));
    } else if (e.key === "Enter") {
      e.preventDefault();
      filtered[active]?.run();
    }
  }

  useEffect(() => {
    listRef.current
      ?.querySelector<HTMLElement>(`[data-idx="${active}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [active]);

  let flatIndex = -1;

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
              />
            </Dialog.Overlay>
            <Dialog.Content asChild aria-describedby={undefined}>
              <motion.div
                initial={{ opacity: 0, scale: 0.97, y: -8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98, y: -4 }}
                transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
                onKeyDown={onKeyDown}
                className="fixed left-1/2 top-[12vh] z-50 w-[min(40rem,92vw)] -translate-x-1/2 overflow-hidden rounded-2xl border border-line-strong bg-bg-elevated shadow-card-hover"
              >
                <Dialog.Title className="sr-only">Command palette</Dialog.Title>

                <div className="flex items-center gap-3 border-b border-line px-4">
                  <Search className="h-4 w-4 shrink-0 text-fg-subtle" />
                  <input
                    autoFocus
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search agents, pages, commands…"
                    className="w-full bg-transparent py-4 text-sm text-fg outline-none placeholder:text-fg-subtle"
                  />
                  <Kbd>ESC</Kbd>
                </div>

                <div ref={listRef} className="max-h-[52vh] overflow-y-auto p-2">
                  {filtered.length === 0 && (
                    <p className="px-3 py-8 text-center text-sm text-fg-subtle">
                      No results for “{query}”
                    </p>
                  )}
                  {Object.entries(grouped).map(([group, items]) => (
                    <div key={group} className="mb-1">
                      <p className="px-3 py-1.5 text-[0.65rem] font-semibold uppercase tracking-wider text-fg-subtle">
                        {group}
                      </p>
                      {items.map((c) => {
                        flatIndex += 1;
                        const idx = flatIndex;
                        return (
                          <button
                            key={c.id}
                            data-idx={idx}
                            onMouseEnter={() => setActive(idx)}
                            onClick={c.run}
                            className={cn(
                              "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                              idx === active ? "bg-brand-500/15 text-fg" : "text-fg-muted hover:bg-surface-hover",
                            )}
                          >
                            <span className="shrink-0 text-fg-subtle">{c.icon}</span>
                            <span className="min-w-0 flex-1">
                              <span className="block truncate font-medium text-fg">{c.label}</span>
                              {c.hint && <span className="block truncate text-xs text-fg-subtle">{c.hint}</span>}
                            </span>
                            {idx === active && <CornerDownLeft className="h-3.5 w-3.5 shrink-0 text-fg-subtle" />}
                          </button>
                        );
                      })}
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-between border-t border-line px-4 py-2.5 text-[0.7rem] text-fg-subtle">
                  <span className="flex items-center gap-2">
                    <Kbd>↑</Kbd><Kbd>↓</Kbd> navigate <Kbd>↵</Kbd> select
                  </span>
                  <span className="flex items-center gap-1.5">
                    LuminAI <ArrowRight className="h-3 w-3" /> Command
                  </span>
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}
