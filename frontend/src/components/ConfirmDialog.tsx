import * as Dialog from "@radix-ui/react-dialog";
import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "@/components/ui";

/**
 * Confirmation dialog for destructive actions — replaces `window.confirm`,
 * which can't be styled and is blocked outright by some browsers.
 *
 * Radix supplies focus trapping, Escape-to-close, and the ARIA wiring; the
 * confirm button takes initial focus so the whole flow is keyboard-driven.
 */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  onConfirm,
  busy = false,
  destructive = true,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  busy?: boolean;
  destructive?: boolean;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
              />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div
                initial={{ opacity: 0, scale: 0.96, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98, y: 4 }}
                transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
                className="fixed left-1/2 top-1/2 z-50 w-[min(26rem,92vw)] -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-line-strong bg-bg-elevated p-6 shadow-card-hover"
              >
                <div className="flex gap-4">
                  {destructive && (
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-500/10 text-red-400">
                      <AlertTriangle className="h-5 w-5" />
                    </div>
                  )}
                  <div className="min-w-0">
                    <Dialog.Title className="text-base font-semibold text-fg">{title}</Dialog.Title>
                    <Dialog.Description className="mt-1.5 text-sm leading-relaxed text-fg-muted">
                      {description}
                    </Dialog.Description>
                  </div>
                </div>

                <div className="mt-6 flex justify-end gap-2">
                  <Dialog.Close asChild>
                    <Button variant="secondary" disabled={busy}>
                      {cancelLabel}
                    </Button>
                  </Dialog.Close>
                  <Button
                    autoFocus
                    variant={destructive ? "danger" : "primary"}
                    onClick={onConfirm}
                    disabled={busy}
                  >
                    {busy ? "Deleting…" : confirmLabel}
                  </Button>
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}
