import { beforeEach, describe, expect, it } from "vitest";
import { findFormRoot, guessJobDescription, parseFormFields } from "@/content/parser";

const SAMPLE_HTML = `
  <form id="app-form">
    <label for="fname">Full Name</label>
    <input type="text" id="fname" name="full_name" required />

    <label for="email">Email Address</label>
    <input type="email" id="email" name="email" required />

    <input type="hidden" name="csrf" value="abc" />

    <select name="experience">
      <option value="0-1">0-1 years</option>
      <option value="2-4">2-4 years</option>
    </select>

    <textarea name="cover_letter" placeholder="Why do you want this role?"></textarea>

    <input type="radio" name="visa" value="yes" /> Yes
    <input type="radio" name="visa" value="no" /> No

    <button type="submit">Submit</button>
  </form>
`;

describe("parseFormFields", () => {
  beforeEach(() => {
    document.body.innerHTML = SAMPLE_HTML;
  });

  it("extracts visible fields and excludes hidden/submit", () => {
    const fields = parseFormFields(document);
    const names = fields.map((f) => f.name);

    expect(names).toContain("full_name");
    expect(names).toContain("email");
    expect(names).toContain("experience");
    expect(names).toContain("cover_letter");
    expect(names).toContain("visa");
    expect(names).not.toContain("csrf");
  });

  it("resolves labels via <label for> and required flag", () => {
    const fields = parseFormFields(document);
    const fullName = fields.find((f) => f.name === "full_name");
    expect(fullName?.label).toBe("Full Name");
    expect(fullName?.required).toBe(true);
  });

  it("extracts select options", () => {
    const fields = parseFormFields(document);
    const experience = fields.find((f) => f.name === "experience");
    expect(experience?.options).toEqual(["0-1 years", "2-4 years"]);
  });

  it("dedupes radio groups and resolves bare-text labels", () => {
    const fields = parseFormFields(document);
    const visaFields = fields.filter((f) => f.name === "visa");
    expect(visaFields).toHaveLength(1);
    expect(new Set(visaFields[0].options)).toEqual(new Set(["Yes", "No"]));
  });

  it("uses placeholder as label fallback", () => {
    const fields = parseFormFields(document);
    const coverLetter = fields.find((f) => f.name === "cover_letter");
    expect(coverLetter?.label).toBe("Why do you want this role?");
  });

  it("gives every field a non-empty css selector", () => {
    const fields = parseFormFields(document);
    for (const field of fields) {
      expect(field.cssSelector.length).toBeGreaterThan(0);
    }
  });
});

describe("findFormRoot", () => {
  it("picks the form with the most fields when multiple forms exist", () => {
    document.body.innerHTML = `
      <form id="small"><input name="a" /></form>
      <form id="big">
        <input name="b" />
        <input name="c" />
        <input name="d" />
      </form>
    `;
    const root = findFormRoot() as HTMLElement;
    expect(root.id).toBe("big");
  });

  it("falls back to the document when there is no form", () => {
    document.body.innerHTML = `<div><input name="a" /></div>`;
    expect(findFormRoot()).toBe(document);
  });
});

describe("guessJobDescription", () => {
  it("finds a long text block in a job-description container", () => {
    document.body.innerHTML = `<div class="job-description">${"Backend Engineer role. ".repeat(10)}</div>`;
    expect(guessJobDescription().length).toBeGreaterThan(100);
  });

  it("returns empty string when nothing matches", () => {
    document.body.innerHTML = `<div>short</div>`;
    expect(guessJobDescription()).toBe("");
  });
});
