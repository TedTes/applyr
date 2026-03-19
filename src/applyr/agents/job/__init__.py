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
from applyr.agents.job.evals import JobWorkflowEvaluation, evaluate_job_workflow
from applyr.agents.job.service import (
    JobWorkflowResult,
    draft_application,
    load_job_fixture,
    rank_jobs,
    run_job_workflow,
    score_job,
    search_jobs,
)
from applyr.agents.job.submission import SubmissionBatchResult, SubmissionResult, submit_applications

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
    "JobWorkflowEvaluation",
    "JobWorkflowResult",
    "SubmissionBatchResult",
    "SubmissionResult",
    "draft_application",
    "evaluate_job_workflow",
    "load_job_fixture",
    "rank_jobs",
    "run_job_workflow",
    "score_job",
    "search_jobs",
    "submit_applications",
]
