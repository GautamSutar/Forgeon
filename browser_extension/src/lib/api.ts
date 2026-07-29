import type { AgentRunResponse, AuthTokens } from "@/lib/types";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface ResumeSummary {
  id: string;
  filename: string;
  is_default: boolean;
}

/** Thin REST client for the backend. Lives in the background service worker
 * (which holds host_permissions for the API origin) rather than the popup,
 * so auth/CORS handling stays in one place.
 */
export class ApiClient {
  constructor(
    private baseUrl: string,
    private tokens: AuthTokens | null,
    private onTokensRefreshed: (tokens: AuthTokens) => Promise<void>,
  ) {}

  private async request<T>(
    path: string,
    options: { method?: string; body?: unknown; auth?: boolean; params?: Record<string, string | boolean> } = {},
  ): Promise<T> {
    const { method = "GET", body, auth = true, params } = options;

    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
      }
    }

    const headers: Record<string, string> = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth && this.tokens) headers["Authorization"] = `Bearer ${this.tokens.accessToken}`;

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (response.status === 401 && auth && this.tokens?.refreshToken) {
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        return this.request<T>(path, options);
      }
    }

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      const message = errorBody?.error?.message ?? errorBody?.detail ?? response.statusText;
      throw new ApiError(message, response.status);
    }

    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  }

  private async tryRefresh(): Promise<boolean> {
    if (!this.tokens?.refreshToken) return false;
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: this.tokens.refreshToken }),
      });
      if (!response.ok) return false;
      const data = (await response.json()) as LoginResponse;
      const tokens: AuthTokens = { accessToken: data.access_token, refreshToken: data.refresh_token };
      this.tokens = tokens;
      await this.onTokensRefreshed(tokens);
      return true;
    } catch {
      return false;
    }
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const data = await this.request<LoginResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
    return { accessToken: data.access_token, refreshToken: data.refresh_token };
  }

  async listResumes(): Promise<ResumeSummary[]> {
    return this.request<ResumeSummary[]>("/resumes");
  }

  async runAgent(html: string, jobDescription: string, resumeId?: string): Promise<AgentRunResponse> {
    return this.request<AgentRunResponse>("/agent/run", {
      method: "POST",
      body: { html, job_description: jobDescription, resume_id: resumeId },
    });
  }

  async approveRun(runId: string, editedAnswers: Record<string, string>): Promise<AgentRunResponse> {
    return this.request<AgentRunResponse>(`/agent/${runId}/approve`, {
      method: "POST",
      body: { edited_answers: editedAnswers },
    });
  }

  async rejectRun(runId: string, reason?: string): Promise<AgentRunResponse> {
    return this.request<AgentRunResponse>(`/agent/${runId}/reject`, {
      method: "POST",
      body: { reason },
    });
  }
}
