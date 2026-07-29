import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import "@testing-library/jest-dom/vitest";

// vitest.config.ts doesn't enable `globals: true`, so RTL's automatic
// afterEach(cleanup) registration never fires — without this, DOM from one
// test leaks into the next and queries like getByRole start matching
// multiple elements.
afterEach(() => {
  cleanup();
});
