import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";

const NAV_ITEMS = [
  { to: "/applications", label: "Applications" },
  { to: "/agent-run", label: "Test Agent (Dev Tool)" },
  { to: "/resumes", label: "Resumes" },
  { to: "/saved-answers", label: "Saved Answers" },
  { to: "/profile", label: "Profile" },
];

export function DashboardLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <span className="font-semibold text-slate-800">AI Job Application Agent</span>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <span>{user?.email}</span>
          <button onClick={logout} className="rounded border border-slate-300 px-2 py-1 hover:bg-slate-100">
            Log out
          </button>
        </div>
      </header>

      <div className="flex flex-1">
        <nav className="w-52 shrink-0 border-r border-slate-200 bg-white p-4">
          <ul className="flex flex-col gap-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `block rounded px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-blue-50 text-blue-700" : "text-slate-600 hover:bg-slate-100"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
