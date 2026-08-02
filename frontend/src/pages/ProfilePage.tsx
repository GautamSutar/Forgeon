import { useEffect, useState, type FormEvent } from "react";
import { profileApi } from "@/api/endpoints";
import type { ProfileUpdate } from "@/api/types";
import { Button, Card, ErrorBanner, FieldLabel, Input, PageHeader, Spinner, Textarea } from "@/components/ui";
import { TagListInput } from "@/components/TagListInput";
import { WorkExperienceEditor } from "@/components/WorkExperienceEditor";
import { EducationHistoryEditor } from "@/components/EducationHistoryEditor";
import { describeError, useAsync } from "@/lib/useAsync";
import { useToast } from "@/lib/toast";

const FIELD_KEYS: (keyof ProfileUpdate)[] = [
  "full_name",
  "headline",
  "summary",
  "phone",
  "location",
  "linkedin_url",
  "github_url",
  "portfolio_url",
  "twitter_url",
  "current_company",
  "current_job_title",
  "highest_education",
  "university",
  "graduation_year",
  "current_salary",
  "expected_salary",
  "notice_period_days",
  "years_experience",
  "visa_status",
  "willing_to_relocate",
  "remote_preference",
  "availability",
  "cover_letter",
  "preferred_locations",
  "preferred_roles",
  "languages_spoken",
  "certifications",
  "first_name",
  "middle_name",
  "last_name",
  "preferred_name",
  "legal_name",
  "gender",
  "date_of_birth",
  "nationality",
  "marital_status",
  "alternate_email",
  "country_code",
  "whatsapp_number",
  "address_line1",
  "address_line2",
  "city",
  "state",
  "country",
  "postal_code",
  "employment_type",
  "kaggle_url",
  "leetcode_url",
  "hackerrank_url",
  "codechef_url",
  "geeksforgeeks_url",
  "stackoverflow_url",
  "medium_url",
  "degree",
  "specialization",
  "current_cgpa",
  "percentage",
  "tenth_percentage",
  "twelfth_percentage",
  "academic_achievements",
  "is_fresher",
  "relevant_experience_years",
  "reason_for_leaving",
  "work_authorized",
  "requires_visa_sponsorship",
  "passport_number",
  "citizenship",
  "disability_status",
  "veteran_status",
  "ethnicity",
  "immediate_joiner",
  "time_zone",
  "awards",
  "publications",
  "hobbies_interests",
  "work_experience",
  "education_history",
  "skills",
  "websites",
];

export default function ProfilePage() {
  const { data: profile, loading, error, refetch } = useAsync(() => profileApi.get());
  const [form, setForm] = useState<ProfileUpdate>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (profile) {
      const next: ProfileUpdate = {};
      for (const key of FIELD_KEYS) {
        (next as Record<string, unknown>)[key] = profile[key];
      }
      setForm(next);
    }
  }, [profile]);

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;

  function setField<K extends keyof ProfileUpdate>(key: K, value: ProfileUpdate[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      await profileApi.update(form);
      setSaved(true);
      toast.show("Profile saved.");
      refetch();
    } catch (err) {
      setSaveError(describeError(err));
    } finally {
      setSaving(false);
    }
  }

  const numberOrUndefined = (value: string): number | undefined => (value === "" ? undefined : Number(value));

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Profile"
        subtitle="This is what the agent uses to answer static form fields directly, without any AI call — the more you fill in here, the fewer fields it has to guess (or correctly refuse) at application time."
      />

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Identity</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="fullName">Full name</FieldLabel>
              <Input
                id="fullName"
                value={form.full_name ?? ""}
                onChange={(e) => setField("full_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="headline">Headline</FieldLabel>
              <Input
                id="headline"
                placeholder="e.g. Aspiring AI / Backend Developer"
                value={form.headline ?? ""}
                onChange={(e) => setField("headline", e.target.value)}
              />
            </div>
          </div>
          <div>
            <FieldLabel htmlFor="summary">Summary / bio</FieldLabel>
            <Textarea
              id="summary"
              rows={3}
              value={form.summary ?? ""}
              onChange={(e) => setField("summary", e.target.value)}
            />
          </div>
          <div>
            <FieldLabel htmlFor="phone">Phone</FieldLabel>
            <Input id="phone" value={form.phone ?? ""} onChange={(e) => setField("phone", e.target.value)} />
          </div>
          <div>
            <FieldLabel htmlFor="location">Location</FieldLabel>
            <Input id="location" value={form.location ?? ""} onChange={(e) => setField("location", e.target.value)} />
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Personal information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="firstName">First name</FieldLabel>
              <Input
                id="firstName"
                value={form.first_name ?? ""}
                onChange={(e) => setField("first_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="middleName">Middle name</FieldLabel>
              <Input
                id="middleName"
                value={form.middle_name ?? ""}
                onChange={(e) => setField("middle_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="lastName">Last name</FieldLabel>
              <Input
                id="lastName"
                value={form.last_name ?? ""}
                onChange={(e) => setField("last_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="preferredName">Preferred name</FieldLabel>
              <Input
                id="preferredName"
                value={form.preferred_name ?? ""}
                onChange={(e) => setField("preferred_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="legalName">Legal name</FieldLabel>
              <Input
                id="legalName"
                value={form.legal_name ?? ""}
                onChange={(e) => setField("legal_name", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="gender">Gender</FieldLabel>
              <Input id="gender" value={form.gender ?? ""} onChange={(e) => setField("gender", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="dob">Date of birth</FieldLabel>
              <Input
                id="dob"
                type="date"
                value={form.date_of_birth ?? ""}
                onChange={(e) => setField("date_of_birth", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="nationality">Nationality</FieldLabel>
              <Input
                id="nationality"
                value={form.nationality ?? ""}
                onChange={(e) => setField("nationality", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="maritalStatus">Marital status</FieldLabel>
              <Input
                id="maritalStatus"
                value={form.marital_status ?? ""}
                onChange={(e) => setField("marital_status", e.target.value)}
              />
            </div>
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Address & alternate contact</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="altEmail">Alternate email</FieldLabel>
              <Input
                id="altEmail"
                value={form.alternate_email ?? ""}
                onChange={(e) => setField("alternate_email", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="whatsapp">WhatsApp number</FieldLabel>
              <Input
                id="whatsapp"
                value={form.whatsapp_number ?? ""}
                onChange={(e) => setField("whatsapp_number", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="countryCode">Phone country code</FieldLabel>
              <Input
                id="countryCode"
                placeholder="e.g. +91"
                value={form.country_code ?? ""}
                onChange={(e) => setField("country_code", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="addr1">Address line 1</FieldLabel>
              <Input
                id="addr1"
                value={form.address_line1 ?? ""}
                onChange={(e) => setField("address_line1", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="addr2">Address line 2</FieldLabel>
              <Input
                id="addr2"
                value={form.address_line2 ?? ""}
                onChange={(e) => setField("address_line2", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="city">City</FieldLabel>
              <Input id="city" value={form.city ?? ""} onChange={(e) => setField("city", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="state">State</FieldLabel>
              <Input id="state" value={form.state ?? ""} onChange={(e) => setField("state", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="country">Country</FieldLabel>
              <Input id="country" value={form.country ?? ""} onChange={(e) => setField("country", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="postal">Postal / ZIP code</FieldLabel>
              <Input
                id="postal"
                value={form.postal_code ?? ""}
                onChange={(e) => setField("postal_code", e.target.value)}
              />
            </div>
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Links</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="linkedin">LinkedIn URL</FieldLabel>
              <Input
                id="linkedin"
                value={form.linkedin_url ?? ""}
                onChange={(e) => setField("linkedin_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="github">GitHub URL</FieldLabel>
              <Input
                id="github"
                value={form.github_url ?? ""}
                onChange={(e) => setField("github_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="portfolio">Portfolio URL</FieldLabel>
              <Input
                id="portfolio"
                value={form.portfolio_url ?? ""}
                onChange={(e) => setField("portfolio_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="twitter">Twitter / X URL</FieldLabel>
              <Input
                id="twitter"
                value={form.twitter_url ?? ""}
                onChange={(e) => setField("twitter_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="kaggle">Kaggle URL</FieldLabel>
              <Input id="kaggle" value={form.kaggle_url ?? ""} onChange={(e) => setField("kaggle_url", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="leetcode">LeetCode URL</FieldLabel>
              <Input
                id="leetcode"
                value={form.leetcode_url ?? ""}
                onChange={(e) => setField("leetcode_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="hackerrank">HackerRank URL</FieldLabel>
              <Input
                id="hackerrank"
                value={form.hackerrank_url ?? ""}
                onChange={(e) => setField("hackerrank_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="codechef">CodeChef URL</FieldLabel>
              <Input
                id="codechef"
                value={form.codechef_url ?? ""}
                onChange={(e) => setField("codechef_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="gfg">GeeksforGeeks URL</FieldLabel>
              <Input
                id="gfg"
                value={form.geeksforgeeks_url ?? ""}
                onChange={(e) => setField("geeksforgeeks_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="so">Stack Overflow URL</FieldLabel>
              <Input
                id="so"
                value={form.stackoverflow_url ?? ""}
                onChange={(e) => setField("stackoverflow_url", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="medium">Medium URL</FieldLabel>
              <Input id="medium" value={form.medium_url ?? ""} onChange={(e) => setField("medium_url", e.target.value)} />
            </div>
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Career & education</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="currentCompany">Current company</FieldLabel>
              <Input
                id="currentCompany"
                value={form.current_company ?? ""}
                onChange={(e) => setField("current_company", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="currentTitle">Current job title</FieldLabel>
              <Input
                id="currentTitle"
                value={form.current_job_title ?? ""}
                onChange={(e) => setField("current_job_title", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="highestEducation">Highest education</FieldLabel>
              <Input
                id="highestEducation"
                placeholder="e.g. B.Tech"
                value={form.highest_education ?? ""}
                onChange={(e) => setField("highest_education", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="university">University</FieldLabel>
              <Input
                id="university"
                value={form.university ?? ""}
                onChange={(e) => setField("university", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="gradYear">Graduation year</FieldLabel>
              <Input
                id="gradYear"
                type="number"
                value={form.graduation_year ?? ""}
                onChange={(e) => setField("graduation_year", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="years">Years of experience</FieldLabel>
              <Input
                id="years"
                type="number"
                step="0.5"
                value={form.years_experience ?? ""}
                onChange={(e) => setField("years_experience", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="degree">Degree / branch</FieldLabel>
              <Input id="degree" value={form.degree ?? ""} onChange={(e) => setField("degree", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="specialization">Specialization</FieldLabel>
              <Input
                id="specialization"
                value={form.specialization ?? ""}
                onChange={(e) => setField("specialization", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="cgpa">Current CGPA</FieldLabel>
              <Input
                id="cgpa"
                type="number"
                step="0.01"
                value={form.current_cgpa ?? ""}
                onChange={(e) => setField("current_cgpa", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="percentage">Percentage</FieldLabel>
              <Input
                id="percentage"
                type="number"
                step="0.01"
                value={form.percentage ?? ""}
                onChange={(e) => setField("percentage", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="tenth">10th percentage</FieldLabel>
              <Input
                id="tenth"
                type="number"
                step="0.01"
                value={form.tenth_percentage ?? ""}
                onChange={(e) => setField("tenth_percentage", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="twelfth">12th percentage</FieldLabel>
              <Input
                id="twelfth"
                type="number"
                step="0.01"
                value={form.twelfth_percentage ?? ""}
                onChange={(e) => setField("twelfth_percentage", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="employmentType">Employment type preference</FieldLabel>
              <Input
                id="employmentType"
                placeholder="e.g. Full-time"
                value={form.employment_type ?? ""}
                onChange={(e) => setField("employment_type", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="relevantExp">Relevant experience (years)</FieldLabel>
              <Input
                id="relevantExp"
                type="number"
                step="0.5"
                value={form.relevant_experience_years ?? ""}
                onChange={(e) => setField("relevant_experience_years", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={form.is_fresher ?? false}
              onChange={(e) => setField("is_fresher", e.target.checked)}
            />
            I am a fresher (no prior full-time experience)
          </label>
          <div>
            <FieldLabel htmlFor="academicAchievements">Academic achievements</FieldLabel>
            <Textarea
              id="academicAchievements"
              rows={2}
              value={form.academic_achievements ?? ""}
              onChange={(e) => setField("academic_achievements", e.target.value)}
            />
          </div>
          <div>
            <FieldLabel htmlFor="reasonForLeaving">Reason for leaving (current/last role)</FieldLabel>
            <Textarea
              id="reasonForLeaving"
              rows={2}
              value={form.reason_for_leaving ?? ""}
              onChange={(e) => setField("reason_for_leaving", e.target.value)}
            />
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Work authorization</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="passport">Passport number</FieldLabel>
              <Input
                id="passport"
                value={form.passport_number ?? ""}
                onChange={(e) => setField("passport_number", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="citizenship">Citizenship</FieldLabel>
              <Input
                id="citizenship"
                value={form.citizenship ?? ""}
                onChange={(e) => setField("citizenship", e.target.value)}
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={form.work_authorized ?? false}
              onChange={(e) => setField("work_authorized", e.target.checked)}
            />
            Legally authorized to work in my current country
          </label>
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={form.requires_visa_sponsorship ?? false}
              onChange={(e) => setField("requires_visa_sponsorship", e.target.checked)}
            />
            Requires visa sponsorship
          </label>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Diversity information (optional)</h2>
          <p className="text-xs text-fg-subtle">
            Entirely voluntary self-identification. The agent only ever uses what you explicitly enter here — it
            never infers or guesses these.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="disability">Disability status</FieldLabel>
              <Input
                id="disability"
                value={form.disability_status ?? ""}
                onChange={(e) => setField("disability_status", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="veteran">Veteran status</FieldLabel>
              <Input
                id="veteran"
                value={form.veteran_status ?? ""}
                onChange={(e) => setField("veteran_status", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="ethnicity">Ethnicity</FieldLabel>
              <Input
                id="ethnicity"
                value={form.ethnicity ?? ""}
                onChange={(e) => setField("ethnicity", e.target.value)}
              />
            </div>
          </div>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Compensation & logistics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel htmlFor="currentSalary">Current salary</FieldLabel>
              <Input
                id="currentSalary"
                type="number"
                value={form.current_salary ?? ""}
                onChange={(e) => setField("current_salary", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="expectedSalary">Expected salary</FieldLabel>
              <Input
                id="expectedSalary"
                type="number"
                value={form.expected_salary ?? ""}
                onChange={(e) => setField("expected_salary", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="notice">Notice period (days)</FieldLabel>
              <Input
                id="notice"
                type="number"
                value={form.notice_period_days ?? ""}
                onChange={(e) => setField("notice_period_days", numberOrUndefined(e.target.value) ?? null)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="availability">Availability</FieldLabel>
              <Input
                id="availability"
                placeholder="e.g. Immediate, 2 weeks notice"
                value={form.availability ?? ""}
                onChange={(e) => setField("availability", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="visa">Visa status</FieldLabel>
              <Input id="visa" value={form.visa_status ?? ""} onChange={(e) => setField("visa_status", e.target.value)} />
            </div>
            <div>
              <FieldLabel htmlFor="remotePref">Remote preference</FieldLabel>
              <Input
                id="remotePref"
                placeholder="e.g. Remote, Hybrid, Onsite"
                value={form.remote_preference ?? ""}
                onChange={(e) => setField("remote_preference", e.target.value)}
              />
            </div>
            <div>
              <FieldLabel htmlFor="timeZone">Time zone</FieldLabel>
              <Input
                id="timeZone"
                placeholder="e.g. Asia/Kolkata"
                value={form.time_zone ?? ""}
                onChange={(e) => setField("time_zone", e.target.value)}
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={form.willing_to_relocate ?? false}
              onChange={(e) => setField("willing_to_relocate", e.target.checked)}
            />
            Willing to relocate
          </label>
          <label className="flex items-center gap-2 text-sm text-fg-muted">
            <input
              type="checkbox"
              checked={form.immediate_joiner ?? false}
              onChange={(e) => setField("immediate_joiner", e.target.checked)}
            />
            Immediate joiner
          </label>
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Preferences</h2>
          <TagListInput
            label="Preferred roles"
            values={form.preferred_roles ?? []}
            onChange={(values) => setField("preferred_roles", values)}
            placeholder="e.g. Backend Engineer"
          />
          <TagListInput
            label="Preferred locations"
            values={form.preferred_locations ?? []}
            onChange={(values) => setField("preferred_locations", values)}
            placeholder="e.g. Bangalore, Remote"
          />
          <TagListInput
            label="Languages spoken"
            values={form.languages_spoken ?? []}
            onChange={(values) => setField("languages_spoken", values)}
            placeholder="e.g. English"
          />
          <TagListInput
            label="Certifications"
            values={form.certifications ?? []}
            onChange={(values) => setField("certifications", values)}
            placeholder="e.g. AWS Certified Solutions Architect"
          />
          <TagListInput
            label="Awards"
            values={form.awards ?? []}
            onChange={(values) => setField("awards", values)}
            placeholder="e.g. Dekathon Runner-Up"
          />
          <TagListInput
            label="Publications"
            values={form.publications ?? []}
            onChange={(values) => setField("publications", values)}
            placeholder="e.g. Paper title, venue"
          />
          <TagListInput
            label="Hobbies & interests"
            values={form.hobbies_interests ?? []}
            onChange={(values) => setField("hobbies_interests", values)}
            placeholder="e.g. Chess"
          />
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Skills</h2>
          <p className="text-xs text-fg-subtle">
            Curated by you — distinct from the raw skills auto-extracted from your uploaded resume, which can be
            noisy. This is what the agent presents when a form asks for a skills list.
          </p>
          <TagListInput
            label="Skills"
            values={form.skills ?? []}
            onChange={(values) => setField("skills", values)}
            placeholder="e.g. Python, FastAPI, LangGraph"
          />
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Websites</h2>
          <p className="text-xs text-fg-subtle">Any other relevant links not covered above.</p>
          <TagListInput
            label="Websites"
            values={form.websites ?? []}
            onChange={(values) => setField("websites", values)}
            placeholder="https://…"
          />
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Work experience</h2>
          <p className="text-xs text-fg-subtle">
            Please provide details of your prior work history / industrial experience here.
          </p>
          <WorkExperienceEditor
            entries={form.work_experience ?? []}
            onChange={(entries) => setField("work_experience", entries)}
          />
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Education</h2>
          <p className="text-xs text-fg-subtle">Please provide details of your formal education.</p>
          <EducationHistoryEditor
            entries={form.education_history ?? []}
            onChange={(entries) => setField("education_history", entries)}
          />
        </Card>

        <Card className="flex flex-col gap-4">
          <h2 className="border-l-2 border-brand-400 pl-2.5 text-sm font-semibold uppercase tracking-wide text-fg-muted">Default cover letter</h2>
          <p className="text-xs text-fg-subtle">
            Used as grounding context when a form asks for a cover letter — the agent will adapt it rather than
            invent one from nothing.
          </p>
          <Textarea
            rows={5}
            value={form.cover_letter ?? ""}
            onChange={(e) => setField("cover_letter", e.target.value)}
          />
        </Card>

        {saveError && <ErrorBanner message={saveError} />}

        <div className="sticky bottom-4 z-10 flex items-center gap-3 rounded-xl border border-line bg-surface/90 p-3 shadow-card-hover backdrop-blur">
          <Button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save profile"}
          </Button>
          {saved && (
            <span className="flex animate-fade-in-up items-center gap-1.5 text-sm font-medium text-emerald-400">
              <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                  clipRule="evenodd"
                />
              </svg>
              Saved
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
