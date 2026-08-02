import { motion } from "framer-motion";
import { Bell, Briefcase, CheckCircle2, FileText, Mail, ScanLine, User } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";

const STEPS = [
  { label: "User Request", icon: User, color: "#5b8dfa" },
  { label: "Job Agent", icon: Briefcase, color: "#3566ef" },
  { label: "Resume Agent", icon: FileText, color: "#8b5cf6" },
  { label: "ATS Agent", icon: ScanLine, color: "#a78bfa" },
  { label: "Email Agent", icon: Mail, color: "#3fd0c9" },
  { label: "Notification", icon: Bell, color: "#1fb5ae" },
  { label: "Completed", icon: CheckCircle2, color: "#10b981" },
];

/**
 * Animated multi-agent workflow canvas. Steps light up in sequence to show
 * how agents hand off to each other.
 *
 * The advancing cursor is driven by a single interval rather than one timer
 * per node, so the sequence can't drift out of order.
 */
export function AgentFlow({ className }: { className?: string }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setStep((s) => (s + 1) % (STEPS.length + 2)), 900);
    return () => clearInterval(id);
  }, []);

  return (
    <div className={cn("relative", className)}>
      <div className="flex flex-col gap-0 sm:flex-row sm:items-stretch sm:gap-0">
        {STEPS.map((s, i) => {
          const done = i < step;
          const active = i === step;
          const Icon = s.icon;

          return (
            <div key={s.label} className="flex flex-1 items-center gap-0 sm:flex-col sm:gap-3">
              <div className="flex flex-col items-center sm:w-full">
                <motion.div
                  animate={{
                    scale: active ? 1.1 : 1,
                    borderColor: done || active ? s.color : "rgb(var(--line))",
                  }}
                  transition={{ duration: 0.3 }}
                  className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border bg-surface"
                  style={{
                    boxShadow: active ? `0 0 24px -4px ${s.color}` : undefined,
                  }}
                >
                  {active && (
                    <span
                      className="absolute inset-0 animate-pulse-ring rounded-xl"
                      style={{ border: `1px solid ${s.color}` }}
                    />
                  )}
                  <Icon
                    className="h-5 w-5 transition-colors"
                    style={{ color: done || active ? s.color : "rgb(var(--fg-subtle))" }}
                  />
                </motion.div>
                <p
                  className="mt-2 hidden text-center text-[0.7rem] font-medium transition-colors sm:block"
                  style={{ color: done || active ? "rgb(var(--fg))" : "rgb(var(--fg-subtle))" }}
                >
                  {s.label}
                </p>
              </div>

              {/* Connector to the next node — vertical stacked, horizontal wide. */}
              {i < STEPS.length - 1 && (
                <div className="relative mx-3 my-1 h-8 w-px flex-1 sm:mx-0 sm:my-0 sm:h-px sm:w-full">
                  <div className="absolute inset-0 bg-line" />
                  <motion.div
                    className="absolute inset-0 origin-top sm:origin-left"
                    initial={false}
                    animate={{ scaleY: done ? 1 : 0, scaleX: done ? 1 : 0 }}
                    transition={{ duration: 0.35 }}
                    style={{ background: `linear-gradient(90deg, ${s.color}, ${STEPS[i + 1].color})` }}
                  />
                </div>
              )}

              {/* Label for the stacked (mobile) layout. */}
              <p
                className="flex-1 text-sm font-medium transition-colors sm:hidden"
                style={{ color: done || active ? "rgb(var(--fg))" : "rgb(var(--fg-subtle))" }}
              >
                {s.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
