import { apiRequest } from "@/api/client";
import type {
  AgentRunResponse,
  Application,
  ApplicationCreate,
  ApplicationUpdate,
  Profile,
  ProfileUpdate,
  Resume,
  SavedAnswer,
  SavedAnswerCreate,
  SavedAnswerUpdate,
  TokenResponse,
  User,
} from "@/api/types";

export const authApi = {
  register: (email: string, password: string, fullName: string) =>
    apiRequest<User>("/auth/register", {
      method: "POST",
      body: { email, password, full_name: fullName },
      auth: false,
    }),
  login: (email: string, password: string) =>
    apiRequest<TokenResponse>("/auth/login", { method: "POST", body: { email, password }, auth: false }),
  me: () => apiRequest<User>("/auth/me"),
};

export const profileApi = {
  get: () => apiRequest<Profile>("/profiles/me"),
  update: (data: ProfileUpdate) => apiRequest<Profile>("/profiles/me", { method: "PUT", body: data }),
};

export const resumeApi = {
  list: () => apiRequest<Resume[]>("/resumes"),
  get: (id: string) => apiRequest<Resume>(`/resumes/${id}`),
  upload: (file: File, setDefault: boolean) => {
    const form = new FormData();
    form.append("file", file);
    return apiRequest<Resume>("/resumes/upload", {
      method: "POST",
      body: form,
      isForm: true,
      params: { set_default: setDefault },
    });
  },
  setDefault: (id: string) => apiRequest<Resume>(`/resumes/${id}/set-default`, { method: "POST" }),
  reparse: (id: string) => apiRequest<Resume>(`/resumes/${id}/parse`, { method: "POST" }),
  remove: (id: string) => apiRequest<void>(`/resumes/${id}`, { method: "DELETE" }),
};

export const applicationApi = {
  list: (offset = 0, limit = 50) =>
    apiRequest<Application[]>("/applications", { params: { offset: String(offset), limit: String(limit) } }),
  get: (id: string) => apiRequest<Application>(`/applications/${id}`),
  create: (data: ApplicationCreate) => apiRequest<Application>("/applications", { method: "POST", body: data }),
  update: (id: string, data: ApplicationUpdate) =>
    apiRequest<Application>(`/applications/${id}`, { method: "PATCH", body: data }),
  remove: (id: string) => apiRequest<void>(`/applications/${id}`, { method: "DELETE" }),
};

export const savedAnswerApi = {
  list: () => apiRequest<SavedAnswer[]>("/saved-answers"),
  create: (data: SavedAnswerCreate) => apiRequest<SavedAnswer>("/saved-answers", { method: "POST", body: data }),
  update: (id: string, data: SavedAnswerUpdate) =>
    apiRequest<SavedAnswer>(`/saved-answers/${id}`, { method: "PATCH", body: data }),
  remove: (id: string) => apiRequest<void>(`/saved-answers/${id}`, { method: "DELETE" }),
};

export const agentApi = {
  run: (html: string, jobDescription: string, resumeId?: string) =>
    apiRequest<AgentRunResponse>("/agent/run", {
      method: "POST",
      body: { html, job_description: jobDescription, resume_id: resumeId },
    }),
  approve: (runId: string, editedAnswers: Record<string, string>) =>
    apiRequest<AgentRunResponse>(`/agent/${runId}/approve`, {
      method: "POST",
      body: { edited_answers: editedAnswers },
    }),
  reject: (runId: string, reason?: string) =>
    apiRequest<AgentRunResponse>(`/agent/${runId}/reject`, { method: "POST", body: { reason } }),
};
