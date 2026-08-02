import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";
import { PageLoader } from "@/components/PageLoader";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();

  // Fullscreen: this runs before the dashboard shell exists, so there is no
  // content area to center inside yet.
  if (loading) return <PageLoader fullscreen label="Starting Lumini" />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
