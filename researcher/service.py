"""Compatibility facade for the researcher pipeline."""

from researcher.workflow.aggregator import normalize_records
from researcher.collectors.reddit import collect_reddit_signals, parse_reddit_response
from researcher.collectors.reviews import collect_review_signals
from researcher.fixtures import default_signal_seed, load_signal_fixture
from researcher.workflow.pipeline import (
    SignalWorkflowResult,
    collect_signals,
    run_signal_workflow,
)
from researcher.workflow.scorer import rank_opportunities, score_record

__all__ = [
    "SignalWorkflowResult",
    "collect_reddit_signals",
    "collect_review_signals",
    "collect_signals",
    "default_signal_seed",
    "load_signal_fixture",
    "normalize_records",
    "parse_reddit_response",
    "rank_opportunities",
    "run_signal_workflow",
    "score_record",
]
