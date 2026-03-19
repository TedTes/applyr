from statistics import mean

from pydantic import Field

from applyr.agents.job.service import JobWorkflowResult
from applyr.core.models import ApplyrBaseModel


class JobWorkflowEvaluation(ApplyrBaseModel):
    listings_found: int = Field(ge=0)
    drafts_generated: int = Field(ge=0)
    average_fit_score: float = Field(ge=0, le=10)
    top_score: float = Field(ge=0, le=10)
    ready_rate: float = Field(ge=0, le=1)


def evaluate_job_workflow(result: JobWorkflowResult) -> JobWorkflowEvaluation:
    scores = [item.score for item in result.scored_jobs]
    ready_count = sum(1 for draft in result.drafts if not draft.missing_information)
    return JobWorkflowEvaluation(
        listings_found=len(result.listings),
        drafts_generated=len(result.drafts),
        average_fit_score=round(mean(scores), 2) if scores else 0,
        top_score=max(scores, default=0),
        ready_rate=round((ready_count / len(result.drafts)), 2) if result.drafts else 0,
    )
