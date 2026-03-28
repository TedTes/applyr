from __future__ import annotations

from typing import TypedDict

from researcher.models import ScoredOpportunity, SignalQuery, SignalRecord
from researcher.workflow.aggregator import normalize_records
from researcher.workflow.pipeline import collect_signals
from researcher.workflow.scorer import rank_opportunities

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover
    END = "__end__"
    StateGraph = None


class SignalState(TypedDict):
    query: SignalQuery
    collected_records: list[SignalRecord]
    normalized_records: list[SignalRecord]
    opportunities: list[ScoredOpportunity]


def run_signal_graph(
    query: SignalQuery,
    seed_records: list[SignalRecord] | None = None,
) -> SignalState:
    if StateGraph is None:
        collected = collect_signals(query, seed_records=seed_records)
        normalized = normalize_records(collected)
        opportunities = rank_opportunities(query, normalized)
        return {
            "query": query,
            "collected_records": collected,
            "normalized_records": normalized,
            "opportunities": opportunities,
        }

    workflow = StateGraph(SignalState)

    def collect_node(state: SignalState) -> SignalState:
        return {**state, "collected_records": collect_signals(state["query"], seed_records=seed_records)}

    def normalize_node(state: SignalState) -> SignalState:
        return {**state, "normalized_records": normalize_records(state["collected_records"])}

    def rank_node(state: SignalState) -> SignalState:
        return {**state, "opportunities": rank_opportunities(state["query"], state["normalized_records"])}

    workflow.add_node("collect", collect_node)
    workflow.add_node("normalize", normalize_node)
    workflow.add_node("rank", rank_node)
    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "normalize")
    workflow.add_edge("normalize", "rank")
    workflow.add_edge("rank", END)
    graph = workflow.compile()
    return graph.invoke(
        {
            "query": query,
            "collected_records": [],
            "normalized_records": [],
            "opportunities": [],
        }
    )
