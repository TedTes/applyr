"""Research agent package scaffold."""

from applyr.agents.research.models import (
    ContentBrief,
    OpportunityScoreBreakdown,
    Platform,
    ResearchQuery,
    ResearchSignal,
    SearchIntent,
    TrendCluster,
)
from applyr.agents.research.service import (
    ResearchWorkflowResult,
    build_title,
    cluster_signals,
    collect_signals,
    generate_content_briefs,
    run_research_workflow,
    score_cluster,
)

__all__ = [
    "ContentBrief",
    "OpportunityScoreBreakdown",
    "Platform",
    "ResearchQuery",
    "ResearchSignal",
    "SearchIntent",
    "TrendCluster",
    "ResearchWorkflowResult",
    "build_title",
    "cluster_signals",
    "collect_signals",
    "generate_content_briefs",
    "run_research_workflow",
    "score_cluster",
]
