import { motion } from "framer-motion";
import {
  ArrowRight,
  Check,
  Code2,
  Layers,
  Lock,
  Puzzle,
  ShieldCheck,
  Star,
  Terminal,
  Zap,
} from "lucide-react";
import { Link } from "react-router-dom";
import { marketplaceApi } from "@/api/endpoints";
import { AgentFlow } from "@/components/AgentFlow";
import { AgentIcon } from "@/components/AgentIcon";
import { LogoLockup, LogoMark } from "@/components/brand/Logo";
import { Badge, Button, Kbd, MagneticButton, Skeleton } from "@/components/ui";
import { useAsync } from "@/lib/useAsync";
import { ThemeToggle } from "@/components/ThemeToggle";

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.55, ease: [0.16, 1, 0.3, 1] as const },
};

export default function LandingPage() {
  const { data: agents, loading } = useAsync(() => marketplaceApi.listAgents());
  const featured = (agents ?? []).slice(0, 6);

  return (
    <div className="min-h-screen bg-bg">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-line/60 bg-bg/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
          <LogoLockup id="nav" markClassName="h-8 w-8" />
          <nav className="hidden items-center gap-7 text-sm text-fg-muted md:flex">
            <a href="#agents" className="transition-colors hover:text-fg">Agents</a>
            <a href="#workflow" className="transition-colors hover:text-fg">Workflow</a>
            <a href="#capabilities" className="transition-colors hover:text-fg">Capabilities</a>
            <a href="#pricing" className="transition-colors hover:text-fg">Pricing</a>
          </nav>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link to="/login">
              <Button variant="ghost" size="sm">Sign in</Button>
            </Link>
            <Link to="/register">
              <Button size="sm">Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="aurora grid-bg relative overflow-hidden">
        <div className="relative mx-auto max-w-6xl px-6 pb-24 pt-20 text-center sm:pt-28">
          <motion.div {...fadeUp}>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-3.5 py-1.5 text-xs font-medium text-brand-300">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-pulse-ring rounded-full bg-brand-400" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand-400" />
              </span>
              {agents ? `${agents.length} agents live` : "Loading agents"}
              <span className="text-fg-subtle">·</span>
              Human-in-the-loop by default
            </div>
          </motion.div>

          <motion.h1
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.05 }}
            className="mx-auto max-w-4xl text-4xl font-extrabold leading-[1.08] tracking-tight text-fg sm:text-6xl"
          >
            The multi-agent
            <br />
            <span className="text-gradient">AI platform</span>
          </motion.h1>

          <motion.p
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.1 }}
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-fg-muted"
          >
            Specialized agents for applications, email, research, and code — composed into
            workflows, grounded in your data, and never acting without your approval.
          </motion.p>

          <motion.div
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.15 }}
            className="mt-9 flex flex-wrap items-center justify-center gap-3"
          >
            <Link to="/register">
              <MagneticButton>
                Start building <ArrowRight className="h-4 w-4" />
              </MagneticButton>
            </Link>
            <Link to="/agents">
              <Button variant="outline" size="lg">Browse marketplace</Button>
            </Link>
          </motion.div>

          <motion.p
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.2 }}
            className="mt-5 flex items-center justify-center gap-2 text-xs text-fg-subtle"
          >
            Press <Kbd>Ctrl</Kbd><Kbd>K</Kbd> anywhere to command it
          </motion.p>

          {/* Product preview */}
          <motion.div
            initial={{ opacity: 0, y: 40, rotateX: 8 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.9, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="perspective-1000 mx-auto mt-16 max-w-4xl"
          >
            <div className="gradient-border overflow-hidden rounded-2xl shadow-card-hover">
              <div className="flex items-center gap-2 border-b border-line bg-bg-elevated px-4 py-2.5">
                <span className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-500/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/70" />
                <span className="ml-3 font-mono text-[0.7rem] text-fg-subtle">forgeon · workspace</span>
              </div>
              <div className="bg-surface p-6 text-left">
                <p className="mb-4 text-[0.7rem] font-semibold uppercase tracking-wider text-fg-subtle">
                  Multi-agent execution
                </p>
                <AgentFlow />
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Featured agents */}
      <section id="agents" className="mx-auto max-w-6xl px-6 py-24">
        <motion.div {...fadeUp} className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-fg">A marketplace of specialists</h2>
          <p className="mx-auto mt-3 max-w-lg text-sm text-fg-muted">
            Each agent ships with its own capabilities, grounding rules, and honest limits.
          </p>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {loading && Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-44" />)}
          {featured.map((a, i) => (
            <motion.div
              key={a.slug}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.45, delay: Math.min(i, 5) * 0.06, ease: [0.16, 1, 0.3, 1] }}
            >
              <Link
                to={`/agents/${a.slug}`}
                className="group block h-full rounded-xl border border-line bg-surface p-5 transition-all duration-200 hover:-translate-y-1 hover:border-line-strong hover:shadow-card-hover"
              >
                <div className="flex items-start justify-between">
                  <div
                    className="flex h-11 w-11 items-center justify-center rounded-xl text-white"
                    style={{
                      background: `linear-gradient(135deg, ${a.accent}, ${a.accent}aa)`,
                      boxShadow: `0 8px 22px -8px ${a.accent}`,
                    }}
                  >
                    <AgentIcon name={a.icon} />
                  </div>
                  <span className="flex items-center gap-1 text-xs text-fg-muted">
                    <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                    {a.rating.toFixed(1)}
                  </span>
                </div>
                <h3 className="mt-4 font-semibold text-fg">{a.name}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-fg-muted">{a.tagline}</p>
                <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                  <span className="text-xs text-fg-subtle">
                    {a.installs.toLocaleString()} installs
                  </span>
                  <span className="flex items-center gap-1 text-xs font-medium text-brand-400 transition-transform group-hover:translate-x-0.5">
                    Open <ArrowRight className="h-3 w-3" />
                  </span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        <motion.div {...fadeUp} className="mt-10 text-center">
          <Link to="/agents">
            <Button variant="outline" size="lg">
              See all agents <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* Workflow */}
      <section id="workflow" className="border-y border-line bg-bg-elevated/50">
        <div className="mx-auto max-w-6xl px-6 py-24">
          <motion.div {...fadeUp} className="mb-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-fg">Agents that hand off to each other</h2>
            <p className="mx-auto mt-3 max-w-lg text-sm text-fg-muted">
              One request fans out across specialists. Every step is visible, inspectable, and
              stops at a human gate before anything irreversible.
            </p>
          </motion.div>
          <motion.div {...fadeUp} className="rounded-2xl border border-line bg-surface p-8">
            <AgentFlow />
          </motion.div>
        </div>
      </section>

      {/* Capabilities */}
      <section id="capabilities" className="mx-auto max-w-6xl px-6 py-24">
        <motion.div {...fadeUp} className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-fg">Built like a developer tool</h2>
        </motion.div>
        <div className="grid gap-4 md:grid-cols-3">
          {[
            { icon: ShieldCheck, title: "Never auto-submits", body: "A real interrupt pauses every run before submission. The approval flag is enforced in code, not prompted for.", tone: "#10b981" },
            { icon: Lock, title: "Grounded, or it refuses", body: "Answers come from your profile and resume. With no grounding context, the agent declines instead of inventing.", tone: "#3566ef" },
            { icon: Zap, title: "Parallel execution", body: "Independent fields generate concurrently under a bounded semaphore — fast without tripping rate limits.", tone: "#f59e0b" },
            { icon: Terminal, title: "Command palette", body: "Ctrl+K to search agents, jump pages, and run commands without touching the mouse.", tone: "#8b5cf6" },
            { icon: Layers, title: "Full execution trace", body: "Every step, tool call, and retry is recorded so you always know what the AI actually did.", tone: "#3fd0c9" },
            { icon: Puzzle, title: "Provider agnostic", body: "LiteLLM under the hood — Anthropic, OpenAI, Gemini, or OpenRouter by changing one setting.", tone: "#ec4899" },
          ].map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.45, delay: (i % 3) * 0.08, ease: [0.16, 1, 0.3, 1] }}
              className="rounded-xl border border-line bg-surface p-6 transition-colors hover:border-line-strong"
            >
              <div
                className="flex h-10 w-10 items-center justify-center rounded-lg"
                style={{ background: `${f.tone}1a`, color: f.tone }}
              >
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 font-semibold text-fg">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-fg-muted">{f.body}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-6xl px-6 py-24">
        <motion.div {...fadeUp} className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-fg">Pricing</h2>
          <p className="mx-auto mt-3 max-w-lg text-sm text-fg-muted">
            Self-hosted and free while Forgeon is in development. Bring your own model key.
          </p>
        </motion.div>
        <div className="mx-auto grid max-w-4xl gap-4 md:grid-cols-3">
          {[
            { name: "Self-hosted", price: "Free", note: "Run it yourself", features: ["All 10 agents", "Bring your own API key", "Full source access"], cta: "Get started", highlight: false },
            { name: "Pro", price: "Soon", note: "Hosted, managed", features: ["Managed infrastructure", "Team workspaces", "Priority models"], cta: "Coming soon", highlight: true },
            { name: "Enterprise", price: "Soon", note: "For organizations", features: ["SSO & audit logs", "Custom agents", "Dedicated support"], cta: "Coming soon", highlight: false },
          ].map((p) => (
            <motion.div
              key={p.name}
              {...fadeUp}
              className={`relative rounded-2xl border p-6 ${p.highlight ? "border-brand-500/50 bg-surface shadow-glow" : "border-line bg-surface"}`}
            >
              {p.highlight && (
                <Badge tone="blue" className="absolute -top-2.5 left-6">Planned</Badge>
              )}
              <p className="text-sm font-medium text-fg">{p.name}</p>
              <p className="mt-3 text-3xl font-bold tracking-tight text-fg">{p.price}</p>
              <p className="mt-1 text-xs text-fg-subtle">{p.note}</p>
              <ul className="mt-5 flex flex-col gap-2.5">
                {p.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-fg-muted">
                    <Check className="h-4 w-4 shrink-0 text-brand-400" /> {f}
                  </li>
                ))}
              </ul>
              <Link to="/register" className="mt-6 block">
                <Button variant={p.highlight ? "primary" : "secondary"} className="w-full" disabled={p.price === "Soon"}>
                  {p.cta}
                </Button>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="aurora relative overflow-hidden border-t border-line">
        <div className="relative mx-auto max-w-3xl px-6 py-24 text-center">
          <motion.div {...fadeUp}>
            <LogoMark className="mx-auto h-14 w-14 animate-float" id="cta" />
            <h2 className="mt-6 text-3xl font-bold tracking-tight text-fg">
              Put your agents to work
            </h2>
            <p className="mx-auto mt-3 max-w-md text-sm text-fg-muted">
              Free, self-hosted, and open. Start with the Job Agent and grow from there.
            </p>
            <Link to="/register" className="mt-8 inline-block">
              <MagneticButton>
                Create your workspace <ArrowRight className="h-4 w-4" />
              </MagneticButton>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-line bg-bg-elevated/40">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="flex flex-wrap justify-between gap-10">
            <div className="max-w-xs">
              <LogoLockup id="footer" markClassName="h-8 w-8" />
              <p className="mt-3 text-sm leading-relaxed text-fg-subtle">
                An AI agent operating system. Specialized, grounded, and always under your control.
              </p>
            </div>
            {[
              { heading: "Product", links: ["Marketplace", "Agents", "Workflow", "Pricing"] },
              { heading: "Developers", links: ["Documentation", "API reference", "Extension", "Changelog"] },
              { heading: "Company", links: ["About", "Privacy", "Terms", "Contact"] },
            ].map((col) => (
              <div key={col.heading}>
                <p className="text-xs font-semibold uppercase tracking-wider text-fg-subtle">{col.heading}</p>
                <ul className="mt-3 flex flex-col gap-2">
                  {col.links.map((l) => (
                    <li key={l}>
                      <span className="cursor-default text-sm text-fg-muted transition-colors hover:text-fg">{l}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-10 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-6">
            <p className="text-xs text-fg-subtle">© {new Date().getFullYear()} Forgeon. MIT licensed.</p>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="text-fg-subtle transition-colors hover:text-fg"
              aria-label="GitHub"
            >
              <Code2 className="h-4 w-4" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
