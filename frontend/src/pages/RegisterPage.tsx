import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import { Button, Card, ErrorBanner, FieldLabel, Input } from "@/components/ui";
import { describeError } from "@/lib/useAsync";

export default function RegisterPage() {
  const { register, user } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (user) return <Navigate to="/applications" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(email, password, fullName);
      navigate("/applications");
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex flex-col items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-400 via-brand-500 to-cyan-400 text-white shadow-lg shadow-brand-500/40">
            <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L20 12l-4.714 2.143L13 21l-2.286-6.857L6 12l4.714-2.143L13 3z" />
            </svg>
          </div>
          <p className="text-sm font-medium text-fg-subtle">Lumini — AI Agent Marketplace</p>
        </div>

        <Card className="shadow-card-hover">
          <h1 className="mb-1 text-lg font-semibold text-fg">Create account</h1>
          <p className="mb-5 text-sm text-fg-muted">Get access to every agent in the marketplace</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
            <div>
              <FieldLabel htmlFor="fullName">Full name</FieldLabel>
              <Input id="fullName" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && <ErrorBanner message={error} />}

            <Button type="submit" disabled={busy} className="mt-1 w-full">
              {busy ? "Creating account…" : "Create account"}
            </Button>
          </form>
        </Card>

        <p className="mt-5 text-center text-sm text-fg-muted">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-400 hover:text-brand-300">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
