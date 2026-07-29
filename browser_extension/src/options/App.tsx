import { useEffect, useState } from "react";
import { callBackground } from "@/lib/messaging";
import type { ExtensionSettings } from "@/lib/types";

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState("");
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void callBackground<ExtensionSettings>({ type: "GET_SETTINGS" }).then((settings) => {
      setApiBaseUrl(settings.apiBaseUrl);
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    await callBackground({ type: "SET_SETTINGS", settings: { apiBaseUrl } });
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  }

  if (loading) return <p className="text-sm text-slate-500">Loading…</p>;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold">Settings</h1>

      <label className="text-sm font-medium">
        Backend API base URL
        <input
          type="url"
          value={apiBaseUrl}
          onChange={(e) => setApiBaseUrl(e.target.value)}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
          placeholder="http://localhost:8000/api/v1"
        />
        <p className="mt-1 text-xs text-slate-500">
          Point this at your deployed backend. For local development this is usually
          http://localhost:8000/api/v1.
        </p>
      </label>

      <button
        type="button"
        onClick={handleSave}
        className="w-fit rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white"
      >
        Save
      </button>

      {saved && <p className="text-sm text-emerald-600">Saved.</p>}
    </div>
  );
}
