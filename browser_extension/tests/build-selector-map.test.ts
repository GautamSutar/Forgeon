import { describe, expect, it } from "vitest";
import { buildSelectorMap } from "@/popup/build-selector-map";
import type { FormField } from "@/lib/types";

function field(overrides: Partial<FormField>): FormField {
  return {
    name: null,
    label: null,
    cssSelector: "#x",
    xpath: "//x",
    type: "text",
    required: false,
    options: [],
    placeholder: null,
    tagId: null,
    ...overrides,
  };
}

describe("buildSelectorMap", () => {
  it("keys by name when present", () => {
    const map = buildSelectorMap([field({ name: "email", cssSelector: "#email" })]);
    expect(map).toEqual({ email: "#email" });
  });

  it("falls back to label when name is missing", () => {
    const map = buildSelectorMap([field({ name: null, label: "Cover Letter", cssSelector: "#cl" })]);
    expect(map).toEqual({ "Cover Letter": "#cl" });
  });

  it("skips fields with neither name nor label", () => {
    const map = buildSelectorMap([field({ name: null, label: null })]);
    expect(map).toEqual({});
  });
});
