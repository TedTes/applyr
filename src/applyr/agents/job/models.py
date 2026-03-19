from datetime import date, datetime
from enum import Enum

from pydantic import Field, HttpUrl

from applyr.core.models import ApplyrBaseModel, ScoredItem, SourceRef


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    OTHER = "other"


class WorkMode(str, Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


class ApplicationStatus(str, Enum):
    DISCOVERED = "discovered"
    SHORTLISTED = "shortlisted"
    DRAFTED = "drafted"
    READY_TO_APPLY = "ready_to_apply"
    APPLIED = "applied"
    SKIPPED = "skipped"


class CompensationRange(ApplyrBaseModel):
    currency: str = Field(default="USD", min_length=3, max_length=3)
    min_amount: float | None = Field(default=None, ge=0)
    max_amount: float | None = Field(default=None, ge=0)
    period: str = Field(default="yearly")


class ResumeProfile(ApplyrBaseModel):
    candidate_name: str | None = None
    title: str | None = None
    summary: str
    skills: list[str] = Field(default_factory=list)
    years_experience: float | None = Field(default=None, ge=0)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_job_types: list[JobType] = Field(default_factory=list)
    preferred_work_modes: list[WorkMode] = Field(default_factory=list)
    salary_floor: float | None = Field(default=None, ge=0)


class JobSearchQuery(ApplyrBaseModel):
    keywords: list[str] = Field(min_length=1)
    location: str | None = None
    work_modes: list[WorkMode] = Field(default_factory=list)
    job_types: list[JobType] = Field(default_factory=list)
    seniority: str | None = None
    max_results: int = Field(default=20, ge=1, le=100)


class JobListing(ApplyrBaseModel):
    title: str
    company: str
    url: HttpUrl
    location: str | None = None
    work_mode: WorkMode = WorkMode.UNKNOWN
    job_type: JobType = JobType.OTHER
    compensation: CompensationRange | None = None
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    posted_date: date | None = None
    source: SourceRef | None = None
    external_id: str | None = None
    discovered_at: datetime | None = None
    application_status: ApplicationStatus = ApplicationStatus.DISCOVERED


class JobScoreBreakdown(ApplyrBaseModel):
    skill_match: float = Field(ge=0, le=10)
    seniority_match: float = Field(ge=0, le=10)
    location_match: float = Field(ge=0, le=10)
    compensation_match: float = Field(ge=0, le=10)
    interest_match: float = Field(ge=0, le=10)


class JobFitScore(ScoredItem):
    job: JobListing
    breakdown: JobScoreBreakdown
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class ApplicationQuestion(ApplyrBaseModel):
    prompt: str
    answer: str | None = None
    required: bool = True


class ApplicationDraft(ApplyrBaseModel):
    job: JobListing
    resume_profile: ResumeProfile
    tailored_summary: str
    cover_letter: str
    key_points: list[str] = Field(default_factory=list)
    screening_answers: list[ApplicationQuestion] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    status: ApplicationStatus = ApplicationStatus.DRAFTED
