import { AlertTriangle, Download } from "lucide-react";
import { useEffect, useState } from "react";
import { API_BASE_URL, getAccessToken } from "@/api/client";
import { cn } from "@/lib/cn";

/**
 * Renders an image from an endpoint that requires an Authorization header.
 *
 * A plain <img src> can't send one, and the generated-image route is
 * per-user authenticated, so the bytes are fetched with the token and handed
 * to the tag as an object URL instead. The URL is revoked on unmount — object
 * URLs leak the whole blob until they are.
 */
export function AuthedImage({ src, alt, className }: { src: string; alt?: string; className?: string }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Absolute URLs (e.g. a future CDN) need no auth and no fetch dance.
    if (/^https?:\/\//i.test(src)) {
      setObjectUrl(src);
      return;
    }

    let revoked = false;
    let created: string | null = null;

    (async () => {
      try {
        // Backend returns an app-absolute path like /api/v1/images/... , so
        // join it to the API origin rather than the base (which already
        // includes the /api/v1 prefix).
        const origin = new URL(API_BASE_URL, window.location.origin).origin;
        const token = getAccessToken();
        const response = await fetch(`${origin}${src}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!response.ok) throw new Error(`Couldn't load image (${response.status})`);

        const blob = await response.blob();
        if (revoked) return;
        created = URL.createObjectURL(blob);
        setObjectUrl(created);
      } catch (err) {
        if (!revoked) setError(err instanceof Error ? err.message : "Couldn't load image");
      }
    })();

    return () => {
      revoked = true;
      if (created) URL.revokeObjectURL(created);
    };
  }, [src]);

  if (error) {
    return (
      <div className="my-3 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
        <AlertTriangle className="h-4 w-4 shrink-0" />
        {error}
      </div>
    );
  }

  if (!objectUrl) {
    return (
      <div className="my-3 aspect-square w-full max-w-sm animate-shimmer rounded-xl border border-line bg-[linear-gradient(90deg,rgb(var(--surface)),rgb(var(--surface-hover)),rgb(var(--surface)))] bg-[length:200%_100%]" />
    );
  }

  return (
    <figure className="group/img relative my-3 w-full max-w-sm">
      <img
        src={objectUrl}
        alt={alt ?? "Generated image"}
        loading="lazy"
        className={cn("w-full rounded-xl border border-line shadow-card", className)}
      />
      <a
        href={objectUrl}
        download={`${(alt ?? "image").slice(0, 40).replace(/[^a-z0-9]+/gi, "-")}.png`}
        title="Download"
        className="absolute right-2 top-2 rounded-lg border border-line bg-bg-elevated/90 p-2 text-fg-muted opacity-0 backdrop-blur transition-opacity hover:text-fg group-hover/img:opacity-100"
      >
        <Download className="h-4 w-4" />
      </a>
      {alt && <figcaption className="mt-1.5 text-xs text-fg-subtle">{alt}</figcaption>}
    </figure>
  );
}
