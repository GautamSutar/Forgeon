import { motion } from "framer-motion";
import { AlertTriangle, FileText, Loader2 } from "lucide-react";
import { useRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type LabelHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

/* ------------------------------------------------------------------ Button */

const BUTTON_VARIANTS = {
  primary:
    "bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm hover:shadow-glow disabled:from-brand-900 disabled:to-brand-900 disabled:text-fg-subtle disabled:shadow-none",
  secondary: "border border-line bg-surface text-fg hover:border-line-strong hover:bg-surface-hover",
  ghost: "text-fg-muted hover:bg-surface-hover hover:text-fg",
  danger: "bg-red-600 text-white hover:bg-red-500 disabled:bg-red-900 disabled:text-fg-subtle",
  outline:
    "border border-line-strong bg-transparent text-fg hover:border-brand-500 hover:bg-brand-500/10",
} as const;

const BUTTON_SIZES = {
  sm: "px-2.5 py-1.5 text-xs",
  md: "px-3.5 py-2 text-sm",
  lg: "px-5 py-2.5 text-sm",
} as const;

export function Button({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: keyof typeof BUTTON_VARIANTS;
  size?: keyof typeof BUTTON_SIZES;
}) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150 active:scale-[0.98] disabled:cursor-not-allowed disabled:active:scale-100",
        BUTTON_VARIANTS[variant],
        BUTTON_SIZES[size],
        className,
      )}
      {...props}
    />
  );
}

/**
 * Button that drifts toward the cursor. Pointer math writes transforms
 * directly to the node rather than through state, so hovering doesn't
 * re-render; touch pointers are ignored since they have no hover.
 */
export function MagneticButton({
  children,
  className,
  strength = 0.25,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { strength?: number }) {
  const ref = useRef<HTMLButtonElement>(null);

  return (
    <button
      ref={ref}
      onPointerMove={(e) => {
        if (e.pointerType !== "mouse" || !ref.current) return;
        const r = ref.current.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * strength;
        const dy = (e.clientY - (r.top + r.height / 2)) * strength;
        ref.current.style.transform = `translate(${dx}px, ${dy}px)`;
      }}
      onPointerLeave={() => {
        if (ref.current) ref.current.style.transform = "translate(0,0)";
      }}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-[transform,box-shadow] duration-200 ease-out hover:shadow-glow",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------- Fields */

const FIELD =
  "w-full rounded-lg border border-line bg-bg-elevated px-3 py-2 text-sm text-fg shadow-sm transition-colors placeholder:text-fg-subtle hover:border-line-strong focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/25";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(FIELD, className)} {...props} />;
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(FIELD, className)} {...props} />;
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn(FIELD, className)} {...props} />;
}

export function FieldLabel({ className, ...props }: LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={cn("mb-1.5 block text-sm font-medium text-fg-muted", className)} {...props} />;
}

/* ----------------------------------------------------------------- Surfaces */

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-xl border border-line bg-surface p-4 shadow-card", className)}>
      {children}
    </div>
  );
}

const BADGE_TONES = {
  slate: "bg-surface-hover text-fg-muted ring-line",
  green: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/30",
  amber: "bg-amber-500/10 text-amber-400 ring-amber-500/30",
  red: "bg-red-500/10 text-red-400 ring-red-500/30",
  blue: "bg-brand-500/10 text-brand-300 ring-brand-500/30",
  violet: "bg-violet-500/10 text-violet-300 ring-violet-500/30",
  cyan: "bg-cyan-500/10 text-cyan-300 ring-cyan-500/30",
} as const;

export function Badge({
  children,
  tone = "slate",
  className,
}: {
  children: ReactNode;
  tone?: keyof typeof BADGE_TONES;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        BADGE_TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mb-6 flex flex-wrap items-start justify-between gap-4"
    >
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-fg">{title}</h1>
        {subtitle && <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-fg-muted">{subtitle}</p>}
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </motion.div>
  );
}

/* ------------------------------------------------------------------- States */

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-shimmer rounded-lg bg-[linear-gradient(90deg,rgb(var(--surface)),rgb(var(--surface-hover)),rgb(var(--surface)))] bg-[length:200%_100%]",
        className,
      )}
    />
  );
}

export function CardSkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border border-line bg-surface p-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="mt-2 h-3 w-32" />
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <div className="flex items-center justify-center p-8">
      <Loader2 className={cn("h-5 w-5 animate-spin text-brand-400", className)} />
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{message}</span>
    </div>
  );
}

export function EmptyState({ message, action }: { message: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-line p-12 text-center">
      <FileText className="h-8 w-8 text-fg-subtle" />
      <p className="max-w-sm text-sm text-fg-muted">{message}</p>
      {action}
    </div>
  );
}

/** Keyboard key cap, for shortcut hints. */
export function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="rounded border border-line bg-bg-elevated px-1.5 py-0.5 font-mono text-[0.65rem] font-medium text-fg-muted">
      {children}
    </kbd>
  );
}
