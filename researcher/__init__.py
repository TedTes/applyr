"""Researcher agent package."""

from researcher.evals import SignalWorkflowEvaluation, evaluate_signal_workflow
from researcher.models import (
    OpportunityScoreBreakdown,
    ScoredOpportunity,
    SignalQuery,
    SignalRecord,
    SourceType,
)
from researcher.workflow.orchestration import SignalState, run_signal_graph
from researcher.workflow.rendering import format_terminal_report, serialize_workflow_result
from researcher.workflow.pipeline import SignalWorkflowResult, collect_signals, run_signal_workflow
from researcher.workflow.scorer import rank_opportunities, score_record
from researcher.fixtures import default_signal_seed, load_signal_fixture
from researcher.service import (
    collect_reddit_signals,
    collect_review_signals,
    normalize_records,
    parse_reddit_response,
)

__all__ = [
    "OpportunityScoreBreakdown",
    "ScoredOpportunity",
    "SignalQuery",
    "SignalRecord",
    "SignalState",
    "SignalWorkflowEvaluation",
    "SignalWorkflowResult",
    "SourceType",
    "collect_reddit_signals",
    "collect_review_signals",
    "collect_signals",
    "default_signal_seed",
    "evaluate_signal_workflow",
    "format_terminal_report",
    "load_signal_fixture",
    "normalize_records",
    "parse_reddit_response",
    "rank_opportunities",
    "run_signal_graph",
    "run_signal_workflow",
    "score_record",
    "serialize_workflow_result",
]
