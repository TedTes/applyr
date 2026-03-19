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
from applyr.agents.research.evals import ResearchWorkflowEvaluation, evaluate_research_workflow
from applyr.agents.research.service import (
    ResearchWorkflowResult,
    build_title,
    cluster_signals,
    collect_signals,
    generate_content_briefs,
    load_research_fixture,
    run_research_workflow,
    score_cluster,
)
from applyr.agents.research.orchestration import ResearchState, run_research_graph

__all__ = [
    "ContentBrief",
    "OpportunityScoreBreakdown",
    "Platform",
    "ResearchQuery",
    "ResearchSignal",
    "ResearchState",
    "SearchIntent",
    "TrendCluster",
    "ResearchWorkflowEvaluation",
    "ResearchWorkflowResult",
    "build_title",
    "cluster_signals",
    "collect_signals",
    "evaluate_research_workflow",
    "generate_content_briefs",
    "load_research_fixture",
    "run_research_graph",
    "run_research_workflow",
    "score_cluster",
]
