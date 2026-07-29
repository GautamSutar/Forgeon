export type AtsPlatform =
  | "linkedin"
  | "workday"
  | "greenhouse"
  | "lever"
  | "ashby"
  | "smartrecruiters"
  | "successfactors"
  | "oracle"
  | "sap"
  | "generic";

export interface FormField {
  name: string | null;
  label: string | null;
  cssSelector: string;
  xpath: string;
  type: string;
  required: boolean;
  options: string[];
  placeholder: string | null;
  tagId: string | null;
}

export interface ExtractedForm {
  platform: AtsPlatform;
  url: string;
  html: string;
  fields: FormField[];
  jobDescriptionGuess: string;
}

export interface GeneratedAnswerEntry {
  answer: string;
  source: "profile" | "generated";
  canonical_key: string | null;
  refused: boolean;
  reasoning?: string;
  was_edited?: boolean;
}

export interface AgentRunResponse {
  run_id: string;
  status: "interrupted" | "completed";
  preview: {
    run_id: string;
    fields: Record<string, unknown>[];
    answers: Record<string, GeneratedAnswerEntry>;
    validation_errors: string[];
    job_description: string;
  } | null;
  application_id: string | null;
  application_status: string | null;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface ExtensionSettings {
  apiBaseUrl: string;
}

/** Messages sent from popup/options -> background service worker. */
export type BackgroundRequest =
  | { type: "LOGIN"; email: string; password: string }
  | { type: "LOGOUT" }
  | { type: "GET_AUTH_STATE" }
  | { type: "GET_SETTINGS" }
  | { type: "SET_SETTINGS"; settings: ExtensionSettings }
  | { type: "LIST_RESUMES" }
  | {
      type: "RUN_AGENT";
      html: string;
      jobDescription: string;
      resumeId?: string;
    }
  | { type: "APPROVE_RUN"; runId: string; editedAnswers: Record<string, string> }
  | { type: "REJECT_RUN"; runId: string; reason?: string };

/** Messages sent from popup -> content script (relayed via chrome.tabs.sendMessage). */
export type ContentRequest =
  | { type: "PING" }
  | { type: "EXTRACT_FORM" }
  | { type: "FILL_FIELDS"; answers: Record<string, string>; fieldsBySelector: Record<string, string> };
