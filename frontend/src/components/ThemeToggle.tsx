import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { Check, Monitor, Moon, Sun } from "lucide-react";
import { useTheme, type Theme } from "@/lib/theme";
import { cn } from "@/lib/cn";

const OPTIONS: { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: "dark", label: "Dark", icon: Moon },
  { value: "light", label: "Light", icon: Sun },
  { value: "system", label: "System", icon: Monitor },
];

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, resolved, setTheme } = useTheme();
  const Icon = theme === "system" ? Monitor : resolved === "dark" ? Moon : Sun;

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          aria-label="Change theme"
          className={cn(
            "rounded-lg p-2 text-fg-muted transition-colors hover:bg-surface-hover hover:text-fg",
            className,
          )}
        >
          <Icon className="h-4 w-4" />
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={6}
          className="z-50 min-w-[9rem] rounded-lg border border-line bg-bg-elevated p-1 shadow-card-hover"
        >
          {OPTIONS.map((o) => (
            <DropdownMenu.Item
              key={o.value}
              onSelect={() => setTheme(o.value)}
              className="flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm text-fg-muted outline-none transition-colors data-[highlighted]:bg-surface-hover data-[highlighted]:text-fg"
            >
              <o.icon className="h-4 w-4" />
              <span className="flex-1">{o.label}</span>
              {theme === o.value && <Check className="h-3.5 w-3.5 text-brand-400" />}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
