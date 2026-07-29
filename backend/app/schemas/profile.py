from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class WorkExperienceEntry(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None
    is_current: bool = False
    start_month: Optional[int] = None
    start_year: Optional[int] = None
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    description: Optional[str] = None


class EducationEntry(BaseModel):
    school: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    gpa: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None

    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    twitter_url: Optional[str] = None

    current_company: Optional[str] = None
    current_job_title: Optional[str] = None
    highest_education: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None

    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    notice_period_days: Optional[int] = None
    years_experience: Optional[float] = None
    visa_status: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    remote_preference: Optional[str] = None
    availability: Optional[str] = None
    cover_letter: Optional[str] = None

    preferred_locations: List[str] = []
    preferred_roles: List[str] = []
    languages_spoken: List[str] = []
    certifications: List[str] = []

    # Personal information
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    legal_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None

    # Contact / address
    alternate_email: Optional[str] = None
    country_code: Optional[str] = None
    whatsapp_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    # Job preferences
    employment_type: Optional[str] = None

    # Additional social / community profile links
    kaggle_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    hackerrank_url: Optional[str] = None
    codechef_url: Optional[str] = None
    geeksforgeeks_url: Optional[str] = None
    stackoverflow_url: Optional[str] = None
    medium_url: Optional[str] = None

    # Education detail
    degree: Optional[str] = None
    specialization: Optional[str] = None
    current_cgpa: Optional[float] = None
    percentage: Optional[float] = None
    tenth_percentage: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    academic_achievements: Optional[str] = None

    # Experience detail
    is_fresher: Optional[bool] = None
    relevant_experience_years: Optional[float] = None
    reason_for_leaving: Optional[str] = None

    # Work authorization
    work_authorized: Optional[bool] = None
    requires_visa_sponsorship: Optional[bool] = None
    passport_number: Optional[str] = None
    citizenship: Optional[str] = None

    # Voluntary diversity self-identification (optional)
    disability_status: Optional[str] = None
    veteran_status: Optional[str] = None
    ethnicity: Optional[str] = None

    # Availability
    immediate_joiner: Optional[bool] = None
    time_zone: Optional[str] = None

    # Additional
    awards: List[str] = []
    publications: List[str] = []
    hobbies_interests: List[str] = []

    # Structured, repeatable history (Workday-style "Add Another" sections)
    work_experience: List[WorkExperienceEntry] = []
    education_history: List[EducationEntry] = []

    # User-curated skills (distinct from a resume's raw parsed skills) and
    # any other relevant links
    skills: List[str] = []
    websites: List[str] = []


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
