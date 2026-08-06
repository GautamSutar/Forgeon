import { AnimatePresence, motion } from "framer-motion";
import {
  Bookmark,
  FileText,
  Home,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  User,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useMatch, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import { AgentSidebar } from "@/components/AgentSidebar";
import { MarketplaceSidebar } from "@/components/MarketplaceSidebar";
import { LogoLockup, LogoMark } from "@/components/brand/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Kbd } from "@/components/ui";
import { cn } from "@/lib/cn";

const SECTIONS = [
  {
    heading: "Workspace",
    items: [
      { to: "/applications", label: "Applications", icon: FileText },
      { to: "/agent-run", label: "Run Agent", icon: Zap },
      { to: "/resumes", label: "Resumes", icon: FileText },
      { to: "/saved-answers", label: "Saved Answers", icon: Bookmark },
    ],
  },
  { heading: "Account", items: [{ to: "/profile", label: "Profile", icon: User }] },
];

const STORAGE_KEY = "forgeon-sidebar-collapsed";

function initials(name?: string | null, email?: string | null): string {
  if (name?.trim()) {
    const p = name.trim().split(/\s+/);
    return (p[0][0] + (p[1]?.[0] ?? "")).toUpperCase();
  }
  return (email?.[0] ?? "?").toUpperCase();
}

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  // Matches only an individual agent's page (/agents/:slug), not the
  // marketplace list itself (/agents) — that keeps browsing the catalog on
  // the generic nav and only swaps in agent-specific chrome once you've
  // actually opened one.
  const agentMatch = useMatch("/agents/:slug");
  const agentSlug = agentMatch?.params.slug;
  const activeConversationId = searchParams.get("c") ?? undefined;
  // Exact match only — /agents itself, not /agents/:slug (that's agentMatch,
  // handled separately above).
  const onMarketplaceList = Boolean(useMatch({ path: "/agents", end: true }));
  const activeCategory = searchParams.get("category");

  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem(STORAGE_KEY) === "true",
  );

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(collapsed));
  }, [collapsed]);

  // The URL (?c=<conversationId>) is the single source of truth shared
  // between this sidebar and AgentChatPage — they're siblings under the
  // same route (this renders <Outlet/>, so it can't hold the page's state
  // directly), and driving both off the URL means a refresh or a shared
  // link reproduces the exact same view instead of just the sidebar or
  // just the transcript.
  function openConversation(id: string) {
    if (!agentSlug) return;
    navigate(`/agents/${agentSlug}?c=${id}`);
  }

  function startNewChat() {
    if (!agentSlug) return;
    navigate(`/agents/${agentSlug}`);
  }

  function handleConversationDeleted(deletedId: string) {
    if (deletedId === activeConversationId) startNewChat();
  }

  function selectCategory(category: string | null) {
    const next = new URLSearchParams();
    if (category) next.set("category", category);
    navigate({ pathname: "/agents", search: next.toString() });
  }

  return (
    <div className="flex min-h-screen bg-bg">
      <motion.aside
        animate={{ width: collapsed ? 68 : 244 }}
        transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
        className="sticky top-0 flex h-screen shrink-0 flex-col border-r border-line bg-bg-elevated/70 backdrop-blur-xl"
      >
        <div className={cn("flex items-center px-4 py-4", collapsed ? "justify-center" : "justify-between")}>
          {collapsed ? (
            <LogoMark className="h-8 w-8" id="rail" />
          ) : (
            <LogoLockup id="side" markClassName="h-8 w-8" tagline="AI Agent OS" />
          )}
        </div>

        {/* Persistent regardless of mode (agent chat / marketplace browse /
            generic nav) — an escape hatch back to the public landing page so
            opening an agent or filtering by category never strands you. */}
        <div className="px-3 pb-2">
          <NavLink
            to="/"
            end
            title={collapsed ? "Home" : undefined}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                collapsed && "justify-center px-0",
                isActive
                  ? "bg-brand-500/15 text-brand-300"
                  : "text-fg-muted hover:bg-surface-hover hover:text-fg",
              )
            }
          >
            <Home className="h-[18px] w-[18px] shrink-0" />
            {!collapsed && "Home"}
          </NavLink>
        </div>

        {/* Collapsed: always the generic icon-only nav. Otherwise: an open
            agent gets its own branding + history; the marketplace list gets
            category browsing; anywhere else gets the generic workspace nav. */}
        {agentSlug && !collapsed ? (
          <AgentSidebar
            key={agentSlug}
            slug={agentSlug}
            activeConversationId={activeConversationId}
            onNewChat={startNewChat}
            onSelectConversation={openConversation}
            onConversationDeleted={handleConversationDeleted}
          />
        ) : onMarketplaceList && !collapsed ? (
          <MarketplaceSidebar activeCategory={activeCategory} onSelectCategory={selectCategory} />
        ) : (
          <>
            <div className="px-3 pb-3">
              <button
                onClick={() => window.dispatchEvent(new Event("forgeon:open-palette"))}
                className={cn(
                  "flex w-full items-center gap-2 rounded-lg border border-line bg-surface px-2.5 py-2 text-sm text-fg-subtle transition-colors hover:border-line-strong hover:text-fg-muted",
                  collapsed && "justify-center px-0",
                )}
              >
                <Search className="h-4 w-4 shrink-0" />
                {!collapsed && (
                  <>
                    <span className="flex-1 text-left">Search…</span>
                    <span className="flex gap-0.5">
                      <Kbd>⌘</Kbd>
                      <Kbd>K</Kbd>
                    </span>
                  </>
                )}
              </button>
            </div>

            <nav className="flex-1 overflow-y-auto px-3">
              {SECTIONS.map((section) => (
                <div key={section.heading} className="mb-5">
                  <AnimatePresence initial={false}>
                    {!collapsed && (
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="mb-1.5 px-3 text-[0.65rem] font-semibold uppercase tracking-wider text-fg-subtle"
                      >
                        {section.heading}
                      </motion.p>
                    )}
                  </AnimatePresence>
                  <ul className="flex flex-col gap-0.5">
                    {section.items.map((item) => (
                      <li key={item.to}>
                        <NavLink
                          to={item.to}
                          end={(item as { end?: boolean }).end}
                          title={collapsed ? item.label : undefined}
                          className={({ isActive }) =>
                            cn(
                              "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                              collapsed && "justify-center px-0",
                              isActive
                                ? "bg-brand-500/15 text-brand-300"
                                : "text-fg-muted hover:bg-surface-hover hover:text-fg",
                            )
                          }
                        >
                          {({ isActive }) => (
                            <>
                              {isActive && (
                                <motion.span
                                  layoutId="nav-active"
                                  className="absolute -left-3 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand-400"
                                />
                              )}
                              <item.icon className="h-[18px] w-[18px] shrink-0" />
                              {!collapsed && <span className="truncate">{item.label}</span>}
                            </>
                          )}
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </nav>
          </>
        )}

        <div className="border-t border-line p-3">
          <div className={cn("flex items-center gap-2.5 rounded-lg px-1 py-1.5", collapsed && "justify-center")}>
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-cyan-400 text-xs font-semibold text-white">
              {initials(user?.full_name, user?.email)}
            </div>
            {!collapsed && (
              <>
                <p className="min-w-0 flex-1 truncate text-xs font-medium text-fg-muted">
                  {user?.full_name || user?.email}
                </p>
                <ThemeToggle />
                <button
                  onClick={logout}
                  title="Log out"
                  className="rounded-md p-1.5 text-fg-subtle transition-colors hover:bg-surface-hover hover:text-fg"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </>
            )}
          </div>
          <button
            onClick={() => setCollapsed((v) => !v)}
            className={cn(
              "mt-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-fg-subtle transition-colors hover:bg-surface-hover hover:text-fg-muted",
              collapsed && "justify-center px-0",
            )}
          >
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            {!collapsed && "Collapse"}
          </button>
        </div>
      </motion.aside>

      <main className="min-w-0 flex-1">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname + location.search}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto max-w-6xl px-6 py-8 sm:px-8"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
