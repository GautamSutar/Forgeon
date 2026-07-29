import type { AtsPlatform } from "@/lib/types";

interface PlatformRule {
  platform: AtsPlatform;
  hostnamePatterns: RegExp[];
  domMarkers?: () => boolean;
}

const RULES: PlatformRule[] = [
  { platform: "linkedin", hostnamePatterns: [/(^|\.)linkedin\.com$/] },
  { platform: "greenhouse", hostnamePatterns: [/(^|\.)greenhouse\.io$/] },
  { platform: "lever", hostnamePatterns: [/(^|\.)lever\.co$/] },
  { platform: "ashby", hostnamePatterns: [/(^|\.)ashbyhq\.com$/] },
  { platform: "smartrecruiters", hostnamePatterns: [/(^|\.)smartrecruiters\.com$/] },
  { platform: "successfactors", hostnamePatterns: [/(^|\.)successfactors\.com$/, /(^|\.)sapsf\.com$/] },
  {
    platform: "workday",
    hostnamePatterns: [/(^|\.)myworkdayjobs\.com$/, /(^|\.)workday\.com$/],
  },
  {
    platform: "oracle",
    hostnamePatterns: [/(^|\.)oraclecloud\.com$/],
    domMarkers: () => Boolean(document.querySelector('[class*="oracle-"], [id*="oracle"]')),
  },
  { platform: "sap", hostnamePatterns: [/(^|\.)sap\.com$/] },
];

/** Detects which ATS platform the current page belongs to via hostname
 * matching, with a DOM-marker fallback for platforms with generic hostnames.
 * Falls back to "generic" so custom/self-hosted HTML application forms are
 * still supported end to end.
 */
export function detectPlatform(hostname: string = window.location.hostname): AtsPlatform {
  for (const rule of RULES) {
    if (rule.hostnamePatterns.some((re) => re.test(hostname))) {
      return rule.platform;
    }
  }
  for (const rule of RULES) {
    if (rule.domMarkers?.()) {
      return rule.platform;
    }
  }
  return "generic";
}
