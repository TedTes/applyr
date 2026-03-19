from statistics import mean

from pydantic import Field

from applyr.agents.research.service import ResearchWorkflowResult
from applyr.core.models import ApplyrBaseModel


class ResearchWorkflowEvaluation(ApplyrBaseModel):
    signals_collected: int = Field(ge=0)
    clusters_found: int = Field(ge=0)
    briefs_generated: int = Field(ge=0)
    average_brief_score: float = Field(ge=0, le=10)
    best_opportunity_score: float = Field(ge=0, le=10)


def evaluate_research_workflow(result: ResearchWorkflowResult) -> ResearchWorkflowEvaluation:
    brief_scores = [brief.score for brief in result.briefs]
    opportunity_scores = [cluster.opportunity_score for cluster in result.clusters]
    return ResearchWorkflowEvaluation(
        signals_collected=len(result.signals),
        clusters_found=len(result.clusters),
        briefs_generated=len(result.briefs),
        average_brief_score=round(mean(brief_scores), 2) if brief_scores else 0,
        best_opportunity_score=max(opportunity_scores, default=0),
    )
