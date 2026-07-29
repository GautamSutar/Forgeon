import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const __dirname = dirname(fileURLToPath(import.meta.url));

// No chrome-extension-specific Vite plugin is used here on purpose: those
// plugins move fast and break across MV3 spec changes. Instead this drives
// a plain multi-entry Vite build.
//
// The background service worker is declared as `"type": "module"` in
// manifest.json, so it's fine for Vite to emit it as an ES module with
// normal code-splitting. The content script, however, CANNOT be an ES
// module — MV3's `content_scripts` field has no module-type option — so it
// is built separately in IIFE format by vite.content.config.ts to produce a
// single self-contained dist/content.js with no import statements.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        background: resolve(__dirname, "src/background/index.ts"),
        popup: resolve(__dirname, "popup.html"),
        options: resolve(__dirname, "options.html"),
      },
      output: {
        entryFileNames: (chunk) => (chunk.name === "background" ? "[name].js" : "assets/[name]-[hash].js"),
        chunkFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
});
