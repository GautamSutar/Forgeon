"""Forgeon agent marketplace catalog.

Agents are code, not user data, so the catalog lives here as a static
registry rather than a database table — adding an agent means shipping its
system prompt and capabilities, not inserting a row.

Each agent's `status` is an honest statement of what it can actually do
today with the currently-configured providers:

- ``live``          — fully functional through the configured chat LLM.
- ``requires_setup`` — the agent's core capability needs a provider or
  bridge that isn't configured (image/video generation models, a device
  automation bridge). These are surfaced in the UI as locked rather than
  pretending to work and then failing at call time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

AgentStatus = Literal["live", "requires_setup"]


@dataclass(frozen=True)
class AgentSpec:
    slug: str
    name: str
    tagline: str
    description: str
    category: str
    icon: str
    accent: str  # hex, drives the card's glow/gradient in the UI
    capabilities: List[str]
    example_prompts: List[str]
    status: AgentStatus = "live"
    setup_hint: Optional[str] = None
    # Marketplace listing metadata.
    #
    # NOTE: `rating` and `installs` are static catalog figures, NOT live
    # telemetry — nothing currently counts installs or collects reviews.
    # They exist so the marketplace UI has realistic listing data to render.
    # Wire them to real aggregates before presenting them as actual metrics.
    creator: str = "Forgeon"
    version: str = "1.0.0"
    rating: float = 0.0
    installs: int = 0
    tags: List[str] = field(default_factory=list)
    system_prompt: str = ""
    # Agents that are backed by a dedicated pipeline rather than plain chat.
    route: Optional[str] = field(default=None)


_GROUNDING_RULES = (
    "Never invent facts about the user. If you need information you have not "
    "been given, ask for it plainly instead of guessing. If you cannot answer "
    "accurately, say so."
)

# The chat UI renders replies as markdown, so agents should author in it
# rather than emitting decorative characters that read as noise.
_FORMATTING_RULES = (
    " Format replies in markdown: **bold** for emphasis, `##` headings only "
    "when a reply has genuinely distinct sections, `-` bullets for lists, and "
    "fenced code blocks with a language tag for code or templates. Do not use "
    "horizontal rules (---) or decorative separator characters. Lead with the "
    "answer, keep paragraphs to two or three sentences, and stop when the "
    "question is answered — no filler preamble or sign-off."
)

AGENTS: List[AgentSpec] = [
    AgentSpec(
        slug="job",
        name="Job Agent",
        rating=4.9,
        installs=12840,
        tags=["ATS","Automation","Human-in-the-loop"],
        tagline="Autofill and apply to jobs, with your approval",
        description=(
            "Reads a live job application form, maps every field to your profile, "
            "drafts grounded answers for the open-ended ones, and pauses for your "
            "approval before anything is filled or submitted."
        ),
        category="Career",
        icon="briefcase",
        accent="#6366f1",
        capabilities=[
            "Detects and parses ATS application forms",
            "Maps form fields to your saved profile",
            "Drafts grounded answers from your resume",
            "Always pauses for human approval",
        ],
        example_prompts=[
            "What does the agent do with a Workday form?",
            "How do I run this on a real job posting?",
        ],
        route="/agent-run",
        system_prompt=(
            "You are Forgeon's Job Agent. You help the user understand and operate "
            "the job application pipeline: form field extraction, profile mapping, "
            "grounded answer generation, and the human approval gate. "
            "For actually filling a live form, direct the user to the browser "
            "extension on the job posting page. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="resume",
        name="Resume Agent",
        rating=4.8,
        installs=10320,
        tags=["Writing","Career","ATS"],
        tagline="Sharpen your resume for a specific role",
        description=(
            "Reviews your uploaded resume against a target job description, finds "
            "the gaps, and rewrites bullets to be specific and measurable."
        ),
        category="Career",
        icon="document",
        accent="#8b5cf6",
        capabilities=[
            "Critiques resume bullets for specificity and impact",
            "Tailors wording to a target job description",
            "Flags missing keywords an ATS would screen for",
            "Suggests measurable outcomes to add",
        ],
        example_prompts=[
            "Rewrite this bullet to show measurable impact.",
            "What keywords am I missing for a backend role?",
        ],
        route="/resumes",
        system_prompt=(
            "You are Forgeon's Resume Agent. You improve resumes: you make bullets "
            "specific, measurable, and active; you flag vague filler; and you "
            "tailor phrasing to a target role. Never fabricate experience, "
            "employers, metrics, or dates the user has not stated — instead, ask "
            "for the real number or detail you would need. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="email",
        name="Email Agent",
        rating=4.7,
        installs=18470,
        tags=["Writing","Outreach","Productivity"],
        tagline="Draft, reply to, and shorten email",
        description=(
            "Writes and rewrites email in your voice — cold outreach, follow-ups, "
            "replies, and the awkward ones you keep putting off."
        ),
        category="Productivity",
        icon="mail",
        accent="#0ea5e9",
        capabilities=[
            "Drafts new email from a one-line intent",
            "Writes replies that match the thread's tone",
            "Shortens and de-jargons long drafts",
            "Adjusts formality for the recipient",
        ],
        example_prompts=[
            "Draft a follow-up after a job interview.",
            "Make this reply warmer but still brief.",
        ],
        system_prompt=(
            "You are Forgeon's Email Agent. You draft and rewrite email. Default to "
            "brief, direct, and warm; avoid corporate filler. Match the tone the "
            "user asks for. When replying, mirror the thread's register. Ask for "
            "the recipient and intent if they are unclear. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="research",
        name="Research Agent",
        rating=4.6,
        installs=9210,
        tags=["Summarize","Analysis","Documents"],
        tagline="Synthesize sources into a clear answer",
        description=(
            "Give it documents, notes, or pasted articles and it produces a "
            "structured synthesis with the reasoning made explicit."
        ),
        category="Knowledge",
        icon="search",
        accent="#14b8a6",
        capabilities=[
            "Summarizes long documents into key claims",
            "Compares sources and surfaces disagreements",
            "Structures findings into briefs and outlines",
            "Separates what sources say from what they imply",
        ],
        example_prompts=[
            "Summarize these three articles and note where they disagree.",
            "Turn these notes into a one-page brief.",
        ],
        system_prompt=(
            "You are Forgeon's Research Agent. You synthesize material the user "
            "provides into structured, honest summaries. Clearly distinguish what "
            "a source states from your own inference. You do not have live web "
            "access — if the user asks about something not in the provided "
            "material, say so and ask them to paste it. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="coding",
        name="Coding Agent",
        rating=4.8,
        installs=21560,
        tags=["Code review","Refactor","Tests"],
        tagline="Explain, review, and refactor code",
        description=(
            "Reads code you paste in, explains what it actually does, finds bugs, "
            "and proposes concrete refactors with the tradeoffs stated."
        ),
        category="Engineering",
        icon="code",
        accent="#f59e0b",
        capabilities=[
            "Explains unfamiliar code line by line",
            "Reviews diffs for bugs and edge cases",
            "Proposes refactors with tradeoffs stated",
            "Writes tests for existing functions",
        ],
        example_prompts=[
            "Why does this async function deadlock?",
            "Write tests covering the edge cases here.",
        ],
        system_prompt=(
            "You are Forgeon's Coding Agent. You explain, review, and refactor "
            "code. Be concrete: quote the specific line that causes a problem and "
            "state the failing input. When you propose a refactor, name the "
            "tradeoff. Prefer the idioms already present in the user's code over "
            "your own preferences. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="travel",
        name="Travel Agent",
        rating=4.5,
        installs=6180,
        tags=["Planning","Itinerary"],
        tagline="Plan itineraries and pressure-test them",
        description=(
            "Builds day-by-day itineraries around your constraints and flags the "
            "plans that look good on paper but fall apart in practice."
        ),
        category="Lifestyle",
        icon="globe",
        accent="#22c55e",
        capabilities=[
            "Builds day-by-day itineraries from constraints",
            "Estimates realistic transit times between stops",
            "Flags over-packed days and logistics risks",
            "Suggests alternatives for bad-weather days",
        ],
        example_prompts=[
            "Plan 5 days in Kyoto for a first-time visitor.",
            "Is this itinerary too packed for one day?",
        ],
        system_prompt=(
            "You are Forgeon's Travel Agent. You build realistic itineraries and "
            "stress-test them for transit time, opening hours, and fatigue. You "
            "cannot check live prices, availability, or book anything — say so "
            "plainly and tell the user what to verify themselves. Do not state "
            "specific current prices or schedules as fact. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="finance",
        name="Finance Agent",
        rating=4.4,
        installs=5740,
        tags=["Budgeting","Modeling","Explainers"],
        tagline="Model budgets and explain the numbers",
        description=(
            "Works through budgets, savings math, and loan scenarios, and explains "
            "financial concepts without the jargon."
        ),
        category="Lifestyle",
        icon="chart",
        accent="#eab308",
        capabilities=[
            "Builds and reviews monthly budgets",
            "Models savings, loan, and payoff scenarios",
            "Explains financial concepts in plain language",
            "Compares options with the assumptions stated",
        ],
        example_prompts=[
            "Model paying off this loan 2 years early.",
            "Explain index funds without the jargon.",
        ],
        system_prompt=(
            "You are Forgeon's Finance Agent. You do budgeting math and explain "
            "financial concepts clearly. Always state your assumptions and show "
            "the arithmetic. You are not a licensed financial advisor — do not "
            "give individualized investment advice, and say so when a question "
            "calls for a professional. You have no live market data. "
            + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="image",
        name="Image Agent",
        rating=4.3,
        installs=8890,
        tags=["Generation","Design","FLUX"],
        tagline="Turn a prompt into an image",
        description=(
            "Turns a written description into an image. Every message is treated "
            "as a new prompt — send another message to generate another image."
        ),
        category="Creative",
        icon="image",
        accent="#ec4899",
        capabilities=[
            "Generates images from a text prompt",
            "Treats each message as a fresh prompt",
            "Serves each generation back as a downloadable image",
        ],
        example_prompts=[
            "A minimal geometric logo for a coffee brand, flat vector style.",
            "A cozy reading nook by a rainy window, warm lighting, watercolor.",
        ],
        status="requires_setup",
        setup_hint=(
            "Set HUGGINGFACE_API_KEY in backend/.env. Whatever token you use, it "
            "must have the \"Make calls to Inference Providers\" permission "
            "enabled at huggingface.co/settings/tokens — a separate, "
            "token-level checkbox that isn't granted just by the token being "
            "valid (requests 403 until it's enabled). The default model, "
            "FLUX.1-schnell, is Apache-2.0 and needs no license acceptance; "
            "set IMAGE_MODEL=black-forest-labs/FLUX.1-dev for the higher-quality "
            "but gated, non-commercial-licensed variant."
        ),
        # Not used for the "image" slug — chat_with_agent routes every message
        # straight to ImageGenerationService instead of the chat LLM, since a
        # prompt here means "render this," not "answer this." Kept accurate
        # anyway in case anything ever reads it directly.
        system_prompt=(
            "You are Forgeon's Image Agent. You generate images with FLUX.1-schnell "
            "from the user's prompt via the Hugging Face Inference API. "
            + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="video",
        name="Video Agent",
        rating=4.2,
        installs=4310,
        tags=["Scripting","Storyboard"],
        tagline="Script, storyboard, and generate video",
        description=(
            "Scripts and storyboards video, and generates clips once a video "
            "generation provider is configured."
        ),
        category="Creative",
        icon="video",
        accent="#f43f5e",
        capabilities=[
            "Writes scripts and shot lists",
            "Builds storyboards from a concept",
            "Generates clips (requires a video provider)",
        ],
        example_prompts=["Write a 30-second product demo script."],
        status="requires_setup",
        setup_hint=(
            "Set a video generation provider key (e.g. Replicate or Runway) in "
            "backend/.env. Scripting and storyboarding work without it."
        ),
        system_prompt=(
            "You are Forgeon's Video Agent. You write scripts, shot lists, and "
            "storyboards. Video generation itself requires a provider that is not "
            "yet configured — say so if asked to render. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
    AgentSpec(
        slug="mobile",
        name="Mobile Agent",
        rating=4.1,
        installs=2650,
        tags=["Automation","Testing","Android"],
        tagline="Automate mobile app workflows",
        description=(
            "Drives mobile app flows through a connected device bridge. Needs an "
            "ADB or Appium bridge configured to control a real device."
        ),
        category="Automation",
        icon="phone",
        accent="#a855f7",
        capabilities=[
            "Plans multi-step mobile app workflows",
            "Drives a connected device (requires bridge)",
            "Describes UI automation selectors",
        ],
        example_prompts=["Plan an automation to export my app data."],
        status="requires_setup",
        setup_hint=(
            "Connect a device automation bridge (ADB for Android, or an Appium "
            "server) and set its endpoint in backend/.env. Planning works without "
            "a device attached."
        ),
        system_prompt=(
            "You are Forgeon's Mobile Agent. You plan mobile automation workflows "
            "and explain UI selectors. You have no device attached, so you cannot "
            "actually tap or swipe — be explicit about that. " + _GROUNDING_RULES + _FORMATTING_RULES
        ),
    ),
]

AGENTS_BY_SLUG: Dict[str, AgentSpec] = {a.slug: a for a in AGENTS}


def get_agent(slug: str) -> Optional[AgentSpec]:
    return AGENTS_BY_SLUG.get(slug)


def list_agents() -> List[AgentSpec]:
    return list(AGENTS)
