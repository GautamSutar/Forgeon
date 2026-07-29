import { useState, type FormEvent } from "react";

interface Props {
  onSubmit: (email: string, password: string) => Promise<void>;
  busy: boolean;
  error: string | null;
}

export function LoginForm({ onSubmit, busy, error }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void onSubmit(email, password);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 p-4">
      <h1 className="text-lg font-semibold">Sign in</h1>
      <p className="text-sm text-slate-500">Sign in with your AI Job Application Agent account.</p>

      <label className="text-sm font-medium">
        Email
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
          placeholder="you@example.com"
        />
      </label>

      <label className="text-sm font-medium">
        Password
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
        />
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={busy}
        className="mt-1 rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {busy ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
