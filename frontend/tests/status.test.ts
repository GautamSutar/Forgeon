import { describe, expect, it } from "vitest";
import { statusTone } from "@/lib/status";

describe("statusTone", () => {
  it("maps submitted to green", () => {
    expect(statusTone("submitted")).toBe("green");
  });

  it("maps pending_approval to amber", () => {
    expect(statusTone("pending_approval")).toBe("amber");
  });

  it("maps rejected and failed to red", () => {
    expect(statusTone("rejected")).toBe("red");
    expect(statusTone("failed")).toBe("red");
  });

  it("maps draft to slate", () => {
    expect(statusTone("draft")).toBe("slate");
  });
});
