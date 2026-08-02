export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface WorkExperienceEntry {
  job_title: string;
  company: string;
  location: string | null;
  is_current: boolean;
  start_month: number | null;
  start_year: number | null;
  end_month: number | null;
  end_year: number | null;
  description: string | null;
}

export interface EducationEntry {
  school: string;
  degree: string | null;
  field_of_study: string | null;
  gpa: string | null;
  start_year: number | null;
  end_year: number | null;
}

export interface Profile {
  id: string;
  user_id: string;

  full_name: string | null;
  headline: string | null;
  summary: string | null;

  phone: string | null;
  location: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  twitter_url: string | null;

  current_company: string | null;
  current_job_title: string | null;
  highest_education: string | null;
  university: string | null;
  graduation_year: number | null;

  current_salary: number | null;
  expected_salary: number | null;
  notice_period_days: number | null;
  years_experience: number | null;
  visa_status: string | null;
  willing_to_relocate: boolean | null;
  remote_preference: string | null;
  availability: string | null;
  cover_letter: string | null;

  preferred_locations: string[];
  preferred_roles: string[];
  languages_spoken: string[];
  certifications: string[];

  // Personal information
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  preferred_name: string | null;
  legal_name: string | null;
  gender: string | null;
  date_of_birth: string | null;
  nationality: string | null;
  marital_status: string | null;

  // Contact / address
  alternate_email: string | null;
  country_code: string | null;
  whatsapp_number: string | null;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;

  // Job preferences
  employment_type: string | null;

  // Additional social / community profile links
  kaggle_url: string | null;
  leetcode_url: string | null;
  hackerrank_url: string | null;
  codechef_url: string | null;
  geeksforgeeks_url: string | null;
  stackoverflow_url: string | null;
  medium_url: string | null;

  // Education detail
  degree: string | null;
  specialization: string | null;
  current_cgpa: number | null;
  percentage: number | null;
  tenth_percentage: number | null;
  twelfth_percentage: number | null;
  academic_achievements: string | null;

  // Experience detail
  is_fresher: boolean | null;
  relevant_experience_years: number | null;
  reason_for_leaving: string | null;

  // Work authorization
  work_authorized: boolean | null;
  requires_visa_sponsorship: boolean | null;
  passport_number: string | null;
  citizenship: string | null;

  // Voluntary diversity self-identification (optional)
  disability_status: string | null;
  veteran_status: string | null;
  ethnicity: string | null;

  // Availability
  immediate_joiner: boolean | null;
  time_zone: string | null;

  // Additional
  awards: string[];
  publications: string[];
  hobbies_interests: string[];

  // Structured, repeatable history (Workday-style "Add Another" sections)
  work_experience: WorkExperienceEntry[];
  education_history: EducationEntry[];

  // User-curated skills + any other relevant links
  skills: string[];
  websites: string[];

  created_at: string;
  updated_at: string;
}

export type ProfileUpdate = Partial<
  Omit<Profile, "id" | "user_id" | "created_at" | "updated_at">
>;

export interface ContactInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
}

export interface ParsedResumeData {
  contact: ContactInfo;
  skills: string[];
  experience: Record<string, string>[];
  education: Record<string, string>[];
  projects: Record<string, string>[];
  certifications: string[];
  links: string[];
}

export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  is_default: boolean;
  parsed_data: ParsedResumeData | null;
  created_at: string;
}

export type ApplicationStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "submitted"
  | "failed";

export interface Application {
  id: string;
  user_id: string;
  company_id: string | null;
  job_description_id: string | null;
  resume_id: string;
  role_title: string | null;
  status: ApplicationStatus;
  ats_platform: string | null;
  source_url: string | null;
  screenshot_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  resume_id: string;
  company_id?: string;
  job_description_id?: string;
  role_title?: string;
  ats_platform?: string;
  source_url?: string;
}

export interface ApplicationUpdate {
  status?: ApplicationStatus;
  role_title?: string;
  screenshot_path?: string;
}

export type QuestionType = "static" | "dynamic";
export type AnswerSource = "profile" | "generated" | "saved_answer";

export interface ApplicationAnswer {
  id: string;
  application_id: string;
  field_label: string;
  field_name: string;
  canonical_key: string | null;
  question_type: QuestionType;
  generated_answer: string | null;
  final_answer: string | null;
  was_edited: boolean;
  source: AnswerSource;
}

export interface SavedAnswer {
  id: string;
  user_id: string;
  canonical_key: string | null;
  question_text: string;
  answer_text: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface SavedAnswerCreate {
  canonical_key?: string;
  question_text: string;
  answer_text: string;
}

export type SavedAnswerUpdate = Partial<SavedAnswerCreate>;

export interface GeneratedAnswerEntry {
  answer: string;
  source: "profile" | "generated";
  canonical_key: string | null;
  refused: boolean;
  reasoning?: string;
  was_edited?: boolean;
}

export interface AgentPreview {
  run_id: string;
  fields: Record<string, unknown>[];
  answers: Record<string, GeneratedAnswerEntry>;
  validation_errors: string[];
  job_description: string;
}

export interface AgentRunResponse {
  run_id: string;
  status: "interrupted" | "completed";
  preview: AgentPreview | null;
  application_id: string | null;
  application_status: string | null;
}

// --- Agent marketplace ---

export type AgentStatus = "live" | "requires_setup";

export interface AgentCard {
  slug: string;
  name: string;
  tagline: string;
  description: string;
  category: string;
  icon: string;
  accent: string;
  capabilities: string[];
  example_prompts: string[];
  status: AgentStatus;
  setup_hint: string | null;
  route: string | null;
  creator: string;
  version: string;
  /** Static catalog figures, not live telemetry — see backend registry.py. */
  rating: number;
  installs: number;
  tags: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  agent_slug: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: ChatMessage[];
}

export interface ChatResponse {
  conversation_id: string;
  message: ChatMessage;
}
