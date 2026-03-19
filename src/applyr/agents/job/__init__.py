"""Job agent package scaffold."""

from applyr.agents.job.models import (
    ApplicationDraft,
    ApplicationQuestion,
    ApplicationStatus,
    CompensationRange,
    JobFitScore,
    JobListing,
    JobScoreBreakdown,
    JobSearchQuery,
    JobType,
    ResumeProfile,
    WorkMode,
)
from applyr.agents.job.service import JobWorkflowResult, draft_application, rank_jobs, run_job_workflow, score_job, search_jobs

__all__ = [
    "ApplicationDraft",
    "ApplicationQuestion",
    "ApplicationStatus",
    "CompensationRange",
    "JobFitScore",
    "JobListing",
    "JobScoreBreakdown",
    "JobSearchQuery",
    "JobType",
    "ResumeProfile",
    "WorkMode",
    "JobWorkflowResult",
    "draft_application",
    "rank_jobs",
    "run_job_workflow",
    "score_job",
    "search_jobs",
]
