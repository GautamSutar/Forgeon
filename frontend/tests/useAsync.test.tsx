import { act, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useAsync } from "@/lib/useAsync";

function TestComponent({ fetcher }: { fetcher: () => Promise<string> }) {
  const { data, loading, error, refetch } = useAsync(fetcher);
  return (
    <div>
      <span data-testid="state">{loading ? "loading" : error ? `error:${error}` : `data:${data}`}</span>
      <button onClick={refetch}>refetch</button>
    </div>
  );
}

describe("useAsync", () => {
  it("transitions from loading to data", async () => {
    const fetcher = vi.fn().mockResolvedValue("hello");
    render(<TestComponent fetcher={fetcher} />);

    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    await screen.findByText("data:hello");
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("surfaces errors", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("boom"));
    render(<TestComponent fetcher={fetcher} />);

    await screen.findByText("error:boom");
  });

  it("refetch re-invokes the fetcher", async () => {
    const fetcher = vi.fn().mockResolvedValue("v1");
    render(<TestComponent fetcher={fetcher} />);
    await screen.findByText("data:v1");

    await act(async () => {
      screen.getByRole("button", { name: "refetch" }).click();
    });

    expect(fetcher).toHaveBeenCalledTimes(2);
  });
});
