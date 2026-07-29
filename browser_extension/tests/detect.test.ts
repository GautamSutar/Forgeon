import { describe, expect, it } from "vitest";
import { detectPlatform } from "@/content/detect";

describe("detectPlatform", () => {
  it("detects linkedin", () => {
    expect(detectPlatform("www.linkedin.com")).toBe("linkedin");
  });

  it("detects greenhouse boards subdomain", () => {
    expect(detectPlatform("boards.greenhouse.io")).toBe("greenhouse");
  });

  it("detects lever", () => {
    expect(detectPlatform("jobs.lever.co")).toBe("lever");
  });

  it("detects ashby", () => {
    expect(detectPlatform("jobs.ashbyhq.com")).toBe("ashby");
  });

  it("detects workday", () => {
    expect(detectPlatform("acme.myworkdayjobs.com")).toBe("workday");
  });

  it("falls back to generic for unknown hosts", () => {
    expect(detectPlatform("careers.some-random-startup.com")).toBe("generic");
  });
});
