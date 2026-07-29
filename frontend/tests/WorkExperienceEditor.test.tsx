import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { WorkExperienceEditor } from "@/components/WorkExperienceEditor";
import type { WorkExperienceEntry } from "@/api/types";

describe("WorkExperienceEditor", () => {
  it("adds a new blank entry when Add Another is clicked", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<WorkExperienceEditor entries={[]} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: "Add Another" }));

    expect(onChange).toHaveBeenCalledWith([
      expect.objectContaining({ job_title: "", company: "", is_current: false }),
    ]);
  });

  it("updates an existing entry's field without affecting others", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    const entries: WorkExperienceEntry[] = [
      {
        job_title: "AI Intern",
        company: "Globex Analytics",
        location: null,
        is_current: true,
        start_month: 12,
        start_year: 2025,
        end_month: null,
        end_year: null,
        description: null,
      },
    ];

    render(<WorkExperienceEditor entries={entries} onChange={onChange} />);
    const jobTitleInput = screen.getAllByDisplayValue("AI Intern")[0];
    await user.clear(jobTitleInput);
    await user.type(jobTitleInput, "Senior AI Intern");

    const lastCall = onChange.mock.calls.at(-1)?.[0];
    expect(lastCall[0].company).toBe("Globex Analytics");
  });

  it("removes an entry when Delete is clicked", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    const entries: WorkExperienceEntry[] = [
      {
        job_title: "AI Intern",
        company: "Globex Analytics",
        location: null,
        is_current: true,
        start_month: null,
        start_year: null,
        end_month: null,
        end_year: null,
        description: null,
      },
    ];

    render(<WorkExperienceEditor entries={entries} onChange={onChange} />);
    await user.click(screen.getByRole("button", { name: "Delete" }));

    expect(onChange).toHaveBeenCalledWith([]);
  });
});
