import { Check, Copy } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AuthedImage } from "@/components/AuthedImage";
import { cn } from "@/lib/cn";

/**
 * Renders assistant messages as formatted markdown.
 *
 * Agents reply in markdown (headings, bold, lists, tables, code). Rendering
 * that as plain text leaks the raw syntax — `**bold**`, `---`, `###` — into
 * the transcript.
 *
 * Raw HTML is deliberately NOT enabled (no rehype-raw): message content is
 * model output, and letting it inject HTML would be an XSS vector.
 */
export function Markdown({ content, className }: { content: string; className?: string }) {
  return (
    <div className={cn("text-sm leading-relaxed", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="mb-2 mt-4 text-base font-bold text-fg first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="mb-2 mt-4 text-[0.95rem] font-bold text-fg first:mt-0">{children}</h2>,
          h3: ({ children }) => <h3 className="mb-1.5 mt-3 text-sm font-semibold text-fg first:mt-0">{children}</h3>,

          p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold text-fg">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,

          ul: ({ children }) => <ul className="mb-3 ml-1 list-none space-y-1.5 last:mb-0">{children}</ul>,
          ol: ({ children }) => (
            <ol className="mb-3 ml-5 list-decimal space-y-1.5 marker:text-fg-subtle last:mb-0">{children}</ol>
          ),
          li: ({ children, ...props }) => {
            // Ordered-list items keep the native marker; unordered ones get a
            // custom dot so bullets align with the design system.
            const ordered = (props as { node?: { parentNode?: { tagName?: string } } }).node?.parentNode?.tagName === "ol";
            if (ordered) return <li className="pl-1">{children}</li>;
            return (
              <li className="relative pl-4">
                <span className="absolute left-0 top-[0.6em] h-1 w-1 rounded-full bg-brand-400" />
                {children}
              </li>
            );
          },

          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noreferrer noopener"
              className="font-medium text-brand-400 underline underline-offset-2 hover:text-brand-300"
            >
              {children}
            </a>
          ),

          blockquote: ({ children }) => (
            <blockquote className="my-3 border-l-2 border-brand-500/50 bg-brand-500/5 py-1 pl-3 text-fg-muted">
              {children}
            </blockquote>
          ),

          hr: () => <hr className="my-4 border-line" />,

          // Generated images come back as standard markdown ![alt](src).
          // The image-serving endpoint requires an Authorization header a
          // plain <img> can't send, so route it through AuthedImage instead.
          img: ({ src, alt }) => <AuthedImage src={String(src ?? "")} alt={alt} />,

          code: ({ className: cls, children }) => {
            // react-markdown only sets a `language-*` class on fenced blocks,
            // which is how we tell them from inline spans.
            const isBlock = /language-/.test(cls ?? "");
            if (!isBlock) {
              return (
                <code className="rounded border border-line bg-bg-elevated px-1.5 py-0.5 font-mono text-[0.8em] text-cyan-300">
                  {children}
                </code>
              );
            }
            return <CodeBlock language={(cls ?? "").replace("language-", "")}>{String(children)}</CodeBlock>;
          },
          pre: ({ children }) => <>{children}</>,

          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-line">
              <table className="w-full border-collapse text-left text-xs">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-surface-hover">{children}</thead>,
          th: ({ children }) => <th className="border-b border-line px-3 py-2 font-semibold text-fg">{children}</th>,
          td: ({ children }) => <td className="border-b border-line px-3 py-2 text-fg-muted">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

function CodeBlock({ language, children }: { language: string; children: string }) {
  const [copied, setCopied] = useState(false);
  const code = children.replace(/\n$/, "");

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      // Clipboard is unavailable over plain HTTP on some browsers — leave the
      // button silent rather than throwing; the text is still selectable.
    }
  }

  return (
    <div className="group/code my-3 overflow-hidden rounded-lg border border-line bg-bg-elevated">
      <div className="flex items-center justify-between border-b border-line px-3 py-1.5">
        <span className="font-mono text-[0.65rem] uppercase tracking-wider text-fg-subtle">
          {language || "code"}
        </span>
        <button
          onClick={copy}
          aria-label="Copy code"
          className="rounded p-1 text-fg-subtle transition-colors hover:bg-surface-hover hover:text-fg"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>
      <pre className="overflow-x-auto p-3">
        <code className="font-mono text-xs leading-relaxed text-fg">{code}</code>
      </pre>
    </div>
  );
}
