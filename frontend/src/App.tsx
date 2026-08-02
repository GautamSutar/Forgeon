import { Navigate, Route, Routes } from "react-router-dom";
import { CommandPalette } from "@/components/CommandPalette";
import { DashboardLayout } from "@/components/DashboardLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import MarketplacePage from "@/pages/MarketplacePage";
import AgentChatPage from "@/pages/AgentChatPage";
import ProfilePage from "@/pages/ProfilePage";
import ResumesPage from "@/pages/ResumesPage";
import ApplicationsPage from "@/pages/ApplicationsPage";
import ApplicationDetailPage from "@/pages/ApplicationDetailPage";
import SavedAnswersPage from "@/pages/SavedAnswersPage";
import AgentRunPage from "@/pages/AgentRunPage";

export default function App() {
  return (
    <>
      {/* Global — Ctrl/Cmd+K works on every route, including the landing page. */}
      <CommandPalette />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/agents" element={<MarketplacePage />} />
          <Route path="/agents/:slug" element={<AgentChatPage />} />
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailPage />} />
          <Route path="/agent-run" element={<AgentRunPage />} />
          <Route path="/resumes" element={<ResumesPage />} />
          <Route path="/saved-answers" element={<SavedAnswersPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
