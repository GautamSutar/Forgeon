from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.user import User


class Profile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Identity — seeded from the User account on first creation (see
    # ProfileService.get_or_create) but editable here, since a candidate may
    # want a display name that differs slightly from their account name.
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    current_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    highest_education: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    university: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    current_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    years_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    visa_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    willing_to_relocate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    remote_preference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    preferred_locations: Mapped[List[str]] = mapped_column(JSON, default=list)
    preferred_roles: Mapped[List[str]] = mapped_column(JSON, default=list)
    languages_spoken: Mapped[List[str]] = mapped_column(JSON, default=list)
    certifications: Mapped[List[str]] = mapped_column(JSON, default=list)

    # --- Personal information -----------------------------------------
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # --- Contact / address ----------------------------------------------
    alternate_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # --- Job preferences --------------------------------------------------
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # --- Additional social / community profile links ----------------------
    kaggle_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    leetcode_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hackerrank_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    codechef_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    geeksforgeeks_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    stackoverflow_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    medium_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # --- Education detail ---------------------------------------------
    degree: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_cgpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tenth_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    twelfth_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    academic_achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- Experience detail -------------------------------------------
    is_fresher: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    relevant_experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reason_for_leaving: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- Work authorization ------------------------------------------
    work_authorized: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    requires_visa_sponsorship: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    passport_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    citizenship: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # --- Voluntary diversity self-identification (optional; the agent
    # never infers or invents these — only ever pulled verbatim if the
    # candidate has explicitly filled them in here) ---------------------
    disability_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    veteran_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # --- Availability ---------------------------------------------------
    immediate_joiner: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    time_zone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # --- Additional -----------------------------------------------------
    awards: Mapped[List[str]] = mapped_column(JSON, default=list)
    publications: Mapped[List[str]] = mapped_column(JSON, default=list)
    hobbies_interests: Mapped[List[str]] = mapped_column(JSON, default=list)

    # --- Structured, repeatable history (Workday-style "Add Another"
    # sections). Stored as JSON lists of objects — see
    # app/schemas/profile.py's WorkExperienceEntry / EducationEntry for the
    # validated shape of each item. Editable directly on the Profile page,
    # independent of (and not auto-derived from) resume parsing, since
    # resume-extracted dates/titles are heuristic and not reliably
    # structured enough to safely auto-populate a form's dated history.
    work_experience: Mapped[List[dict]] = mapped_column(JSON, default=list)
    education_history: Mapped[List[dict]] = mapped_column(JSON, default=list)

    # User-curated skills list, distinct from a resume's raw parsed skills
    # (which are often noisy — "Languages: Python", duplicated fragments,
    # etc.) — this is what the candidate has explicitly reviewed and wants
    # presented as their skill set.
    skills: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Any other relevant links not covered by the named URL fields above.
    websites: Mapped[List[str]] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship(back_populates="profile")
