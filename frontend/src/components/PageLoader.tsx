import { motion } from "framer-motion";
import { LogoMark } from "@/components/brand/Logo";
import { cn } from "@/lib/cn";

/**
 * Centered, branded loading state.
 *
 * `fullscreen` covers the viewport (app boot / auth check); the default
 * fills its parent and vertically centers within the content area, so a
 * page-level load doesn't collapse the layout or jump when content lands.
 *
 * Everything animated here is transform/opacity only, so the whole thing is
 * GPU-composited and costs nothing while the network request is in flight.
 */
export function PageLoader({
  label = "Loading",
  sublabel,
  fullscreen = false,
  overlay = false,
  className,
}: {
  label?: string;
  sublabel?: string;
  /** Covers the viewport — for app boot, before any shell exists. */
  fullscreen?: boolean;
  /** Covers the nearest positioned ancestor — blocks a panel in place. */
  overlay?: boolean;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className={cn(
        "flex flex-col items-center justify-center gap-6",
        fullscreen
          ? "fixed inset-0 z-50 bg-bg"
          : overlay
            ? "absolute inset-0 z-20 rounded-xl bg-bg/80 backdrop-blur-sm"
            : "min-h-[60vh] w-full",
        className,
      )}
    >
      <div className="relative flex h-24 w-24 items-center justify-center">
        {/* Expanding rings radiating from the mark. */}
        {[0, 0.6, 1.2].map((delay) => (
          <motion.span
            key={delay}
            className="absolute h-16 w-16 rounded-2xl border border-brand-500/40"
            initial={{ scale: 0.7, opacity: 0.6 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ duration: 1.8, repeat: Infinity, delay, ease: "easeOut" }}
          />
        ))}

        {/* Sweeping gradient arc. */}
        <motion.svg
          viewBox="0 0 100 100"
          className="absolute h-20 w-20"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "linear" }}
        >
          <defs>
            <linearGradient id="loader-arc" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#1e4fd8" stopOpacity="0" />
              <stop offset="60%" stopColor="#3566ef" />
              <stop offset="100%" stopColor="#3fd0c9" />
            </linearGradient>
          </defs>
          <circle
            cx="50"
            cy="50"
            r="44"
            fill="none"
            stroke="url(#loader-arc)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="150 130"
          />
        </motion.svg>

        {/* The mark itself, breathing. */}
        <motion.div
          animate={{ scale: [1, 1.07, 1], opacity: [0.85, 1, 0.85] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <LogoMark className="h-10 w-10" id="loader" />
        </motion.div>
      </div>

      <div className="flex flex-col items-center gap-2">
        <p className="text-sm font-medium text-fg-muted">{label}</p>
        {sublabel && (
          <p className="max-w-xs text-center text-xs leading-relaxed text-fg-subtle">{sublabel}</p>
        )}
        {/* Indeterminate track — a real progress bar would be a lie, since
            we don't know how long the request will take. */}
        <div className="h-0.5 w-28 overflow-hidden rounded-full bg-line">
          <motion.div
            className="h-full w-1/3 rounded-full bg-gradient-to-r from-brand-500 to-cyan-400"
            animate={{ x: ["-120%", "360%"] }}
            transition={{ duration: 1.3, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </div>

      <span className="sr-only">{label}…</span>
    </div>
  );
}

/**
 * Small inline spinner for buttons and rows — the branded PageLoader would
 * be absurd at 16px.
 */
export function InlineLoader({ className }: { className?: string }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-line border-t-brand-400",
        className,
      )}
    />
  );
}
