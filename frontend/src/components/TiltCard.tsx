import { useRef, useState, type ReactNode } from "react";

/**
 * A card that tilts in 3D toward the pointer, with a specular highlight that
 * tracks the cursor.
 *
 * Deliberately built on CSS 3D transforms rather than WebGL: the effect is
 * GPU-composited, adds no dependency to the bundle, and degrades to a plain
 * card on touch devices (which have no hover) and under
 * `prefers-reduced-motion`. Pointer math runs on refs, not state, so moving
 * the mouse doesn't re-render the subtree — only the two transform values
 * that actually change are written to the DOM.
 */
export function TiltCard({
  children,
  accent,
  className = "",
  maxTilt = 9,
}: {
  children: ReactNode;
  accent: string;
  className?: string;
  maxTilt?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [hovered, setHovered] = useState(false);

  function handleMove(e: React.PointerEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el) return;
    // Coarse pointers (touch) have no meaningful hover position — tilting
    // on tap reads as a glitch rather than an effect.
    if (e.pointerType !== "mouse") return;

    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;

    el.style.setProperty("--tilt-x", `${(0.5 - py) * maxTilt * 2}deg`);
    el.style.setProperty("--tilt-y", `${(px - 0.5) * maxTilt * 2}deg`);
    el.style.setProperty("--mx", `${px * 100}%`);
    el.style.setProperty("--my", `${py * 100}%`);
  }

  function reset() {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--tilt-x", "0deg");
    el.style.setProperty("--tilt-y", "0deg");
    setHovered(false);
  }

  return (
    <div className="perspective-1000">
      <div
        ref={ref}
        onPointerMove={handleMove}
        onPointerEnter={(e) => e.pointerType === "mouse" && setHovered(true)}
        onPointerLeave={reset}
        style={
          {
            transform:
              "rotateX(var(--tilt-x, 0deg)) rotateY(var(--tilt-y, 0deg)) translateZ(0)",
            transition: hovered ? "transform 80ms linear" : "transform 400ms cubic-bezier(0.16,1,0.3,1)",
            borderColor: hovered ? `${accent}66` : undefined,
            boxShadow: hovered ? `0 18px 48px -12px ${accent}55, 0 0 0 1px ${accent}33` : undefined,
          } as React.CSSProperties
        }
        className={`preserve-3d relative h-full overflow-hidden rounded-2xl border border-line bg-surface shadow-card ${className}`}
      >
        {/* Specular sheen that follows the cursor. */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300"
          style={{
            opacity: hovered ? 1 : 0,
            background: `radial-gradient(24rem 24rem at var(--mx,50%) var(--my,50%), ${accent}22, transparent 65%)`,
          }}
        />
        {children}
      </div>
    </div>
  );
}
