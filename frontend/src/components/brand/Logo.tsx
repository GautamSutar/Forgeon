/**
 * FORGEON brand mark — an angular monogram with a neural-graph motif on the
 * upper arm, in the deep-blue -> cyan gradient.
 *
 * NOTE: this SVG's geometry was originally drawn as a stylized "L" for the
 * product's previous name (LuminAI). It still reads fine as an abstract
 * angular mark, but it is not literally an "F" — redraw the path data below
 * (or commission new brand art) if an F-monogram is wanted here.
 *
 * Built as inline SVG rather than shipping a raster so it stays crisp at any
 * size and costs no image request. To use raster art instead, drop it at
 * `frontend/public/logo.png` and swap <LogoMark> for an <img>.
 *
 * `id` is required: SVG gradient IDs are document-global, so two marks sharing
 * an ID would make the second inherit the first's gradient.
 */
export function LogoMark({ className = "h-8 w-8", id = "forgeon" }: { className?: string; id?: string }) {
  const gid = `forgeon-grad-${id}`;
  const glow = `forgeon-glow-${id}`;

  return (
    <svg viewBox="0 0 120 140" className={className} fill="none" aria-hidden="true">
      <defs>
        <linearGradient id={gid} x1="24" y1="14" x2="104" y2="128" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#1e4fd8" />
          <stop offset="50%" stopColor="#2183c0" />
          <stop offset="100%" stopColor="#3fd0c9" />
        </linearGradient>
        <filter id={glow} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2.5" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g stroke={`url(#${gid})`} fill="none" strokeWidth="5.5" strokeLinejoin="round" strokeLinecap="round">
        {/* Outer angular frame */}
        <path d="M26 46 L26 126 L100 126 L100 110 L44 110 L44 46 Z" />
        {/* Inner stem */}
        <path d="M56 34 L56 96 L88 96" opacity="0.95" />
        {/* Hook cresting the inner stem */}
        <path d="M56 40 a13 13 0 0 1 22 9 l0 8" />
        {/* Swoosh sweeping out of the stem into the graph */}
        <path d="M32 122 C32 84 48 66 72 56" opacity="0.9" />
      </g>

      {/* Neural graph */}
      <g stroke={`url(#${gid})`} strokeWidth="3.5" strokeLinecap="round" filter={`url(#${glow})`}>
        <path d="M76 44 L98 60 M98 60 L72 76 M72 76 L76 44 M72 76 L90 94 M90 94 L98 60" />
      </g>
      <g fill={`url(#${gid})`} filter={`url(#${glow})`}>
        <circle cx="76" cy="44" r="7.5" />
        <circle cx="98" cy="60" r="7.5" />
        <circle cx="72" cy="76" r="6.5" />
        <circle cx="90" cy="94" r="7.5" />
      </g>
    </svg>
  );
}

/** Mark + wordmark lockup, matching the logo's letter-spaced treatment. */
export function LogoLockup({
  className = "",
  markClassName = "h-9 w-9",
  tagline,
  id = "lockup",
}: {
  className?: string;
  markClassName?: string;
  tagline?: string;
  id?: string;
}) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <LogoMark className={markClassName} id={id} />
      <div className="leading-tight">
        <p className="text-sm font-bold tracking-[0.2em] text-fg">FORGEON</p>
        {tagline && <p className="mt-0.5 text-[0.7rem] tracking-normal text-fg-subtle">{tagline}</p>}
      </div>
    </div>
  );
}
