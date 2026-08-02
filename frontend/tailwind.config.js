/** @type {import('tailwindcss').Config} */

// Semantic tokens resolve to CSS variables (defined in index.css) so one class
// is correct in every theme — `bg-surface` works in dark and light without
// `dark:` variants scattered through components.
const token = (name) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      colors: {
        bg: token("bg"),
        "bg-elevated": token("bg-elevated"),
        surface: token("surface"),
        "surface-hover": token("surface-hover"),
        line: token("line"),
        "line-strong": token("line-strong"),
        fg: token("fg"),
        "fg-muted": token("fg-muted"),
        "fg-subtle": token("fg-subtle"),

        // Brand ramp sampled from the logo gradient (deep blue -> cyan).
        brand: {
          50: "#eef4ff",
          100: "#dbe7ff",
          200: "#bcd3ff",
          300: "#8eb5ff",
          400: "#5b8dfa",
          500: "#3566ef",
          600: "#1e4fd8",
          700: "#1a3fae",
          800: "#1b378a",
          900: "#1b326d",
        },
        cyan: { 300: "#7ee7e0", 400: "#3fd0c9", 500: "#1fb5ae", 600: "#0f918c" },
        violet: { 300: "#c4b5fd", 400: "#a78bfa", 500: "#8b5cf6", 600: "#7c3aed" },
      },
      borderRadius: { xl: "0.875rem", "2xl": "1.125rem", "3xl": "1.5rem" },
      boxShadow: {
        soft: "0 1px 2px 0 rgb(0 0 0 / 0.16)",
        card: "0 1px 3px 0 rgb(0 0 0 / 0.22), 0 8px 24px -10px rgb(0 0 0 / 0.35)",
        "card-hover": "0 8px 24px -6px rgb(0 0 0 / 0.34), 0 28px 56px -18px rgb(0 0 0 / 0.5)",
        glow: "0 0 0 1px rgb(53 102 239 / 0.30), 0 10px 40px -8px rgb(53 102 239 / 0.42)",
        "glow-cyan": "0 0 0 1px rgb(63 208 201 / 0.30), 0 10px 40px -8px rgb(63 208 201 / 0.40)",
      },
      keyframes: {
        "fade-up": { "0%": { opacity: "0", transform: "translateY(10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
        "pulse-ring": { "0%": { transform: "scale(0.85)", opacity: "0.7" }, "100%": { transform: "scale(1.7)", opacity: "0" } },
        "gradient-pan": { "0%,100%": { backgroundPosition: "0% 50%" }, "50%": { backgroundPosition: "100% 50%" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
        "dash-flow": { to: { strokeDashoffset: "-24" } },
      },
      animation: {
        "fade-up": "fade-up 0.45s cubic-bezier(0.16,1,0.3,1) both",
        float: "float 6s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2.2s cubic-bezier(0.24,0,0.38,1) infinite",
        "gradient-pan": "gradient-pan 12s ease infinite",
        shimmer: "shimmer 2.4s linear infinite",
        "dash-flow": "dash-flow 1s linear infinite",
      },
    },
  },
  plugins: [],
};
