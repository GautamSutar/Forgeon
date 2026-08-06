/**
 * FORGEON brand mark — a flame monogram, shipped as a cropped, transparent
 * PNG (`frontend/public/logo-mark.png`) rather than inline SVG, since the
 * art came from a raster source. `id` is unused now (the SVG-gradient-ID
 * concern that required it no longer applies) but kept so call sites don't
 * need to change.
 */
export function LogoMark({ className = "h-8 w-8", id: _id = "forgeon" }: { className?: string; id?: string }) {
  return <img src="/logo-mark.png" alt="" className={`${className} object-contain`} />;
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
