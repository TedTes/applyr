from statistics import mean

from pydantic import Field

from core.models import SignalBaseModel
from researcher.workflow.pipeline import SignalWorkflowResult


class SignalWorkflowEvaluation(SignalBaseModel):
    collected_records: int = Field(ge=0)
    normalized_records: int = Field(ge=0)
    opportunities_ranked: int = Field(ge=0)
    average_total_score: float = Field(ge=0, le=50)
    top_total_score: float = Field(ge=0, le=50)


def evaluate_signal_workflow(result: SignalWorkflowResult) -> SignalWorkflowEvaluation:
    scores = [item.total_score for item in result.opportunities]
    return SignalWorkflowEvaluation(
        collected_records=len(result.collected_records),
        normalized_records=len(result.normalized_records),
        opportunities_ranked=len(result.opportunities),
        average_total_score=round(mean(scores), 2) if scores else 0,
        top_total_score=max(scores, default=0),
    )
