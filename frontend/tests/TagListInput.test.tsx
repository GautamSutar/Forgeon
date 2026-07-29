import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TagListInput } from "@/components/TagListInput";

describe("TagListInput", () => {
  it("adds a value on Enter and clears the draft", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagListInput label="Preferred roles" values={[]} onChange={onChange} />);

    const input = screen.getByPlaceholderText("Type a value and press Enter");
    await user.type(input, "Backend Engineer{Enter}");

    expect(onChange).toHaveBeenCalledWith(["Backend Engineer"]);
  });

  it("adds a value via the Add button", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagListInput label="Preferred roles" values={["Backend Engineer"]} onChange={onChange} />);

    await user.type(screen.getByPlaceholderText("Type a value and press Enter"), "SRE");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(onChange).toHaveBeenCalledWith(["Backend Engineer", "SRE"]);
  });

  it("does not add duplicate values", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<TagListInput label="Preferred roles" values={["Backend Engineer"]} onChange={onChange} />);

    await user.type(screen.getByPlaceholderText("Type a value and press Enter"), "Backend Engineer{Enter}");

    expect(onChange).not.toHaveBeenCalled();
  });

  it("removes a value when its chip's × is clicked", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(
      <TagListInput label="Preferred roles" values={["Backend Engineer", "SRE"]} onChange={onChange} />,
    );

    await user.click(screen.getByRole("button", { name: "Remove SRE" }));

    expect(onChange).toHaveBeenCalledWith(["Backend Engineer"]);
  });
});
