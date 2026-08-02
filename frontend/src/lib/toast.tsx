import { toast as sonner } from "sonner";

type Tone = "success" | "error" | "info";

/**
 * Thin adapter over sonner so existing `useToast().show(msg, tone)` call sites
 * keep working after the migration, without touching every page.
 */
export function useToast() {
  return {
    show: (message: string, tone: Tone = "success") => {
      if (tone === "error") sonner.error(message);
      else if (tone === "info") sonner.info(message);
      else sonner.success(message);
    },
  };
}
