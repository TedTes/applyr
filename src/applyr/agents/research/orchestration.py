from __future__ import annotations

from typing import TypedDict

from applyr.agents.research.models import ContentBrief, ResearchQuery, ResearchSignal, TrendCluster
from applyr.agents.research.service import cluster_signals, collect_signals, generate_content_briefs

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover
    END = "__end__"
    StateGraph = None


class ResearchState(TypedDict):
    query: ResearchQuery
    signals: list[ResearchSignal]
    clusters: list[TrendCluster]
    briefs: list[ContentBrief]


def run_research_graph(
    query: ResearchQuery,
    seed_signals: list[ResearchSignal] | None = None,
) -> ResearchState:
    if StateGraph is None:
        signals = collect_signals(query, seed_signals=seed_signals)
        clusters = cluster_signals(signals)
        briefs = generate_content_briefs(query, clusters)
        return {
            "query": query,
            "signals": signals,
            "clusters": clusters,
            "briefs": briefs,
        }

    workflow = StateGraph(ResearchState)

    def collect_node(state: ResearchState) -> ResearchState:
        return {**state, "signals": collect_signals(state["query"], seed_signals=seed_signals)}

    def cluster_node(state: ResearchState) -> ResearchState:
        return {**state, "clusters": cluster_signals(state["signals"])}

    def brief_node(state: ResearchState) -> ResearchState:
        return {**state, "briefs": generate_content_briefs(state["query"], state["clusters"])}

    workflow.add_node("collect", collect_node)
    workflow.add_node("cluster", cluster_node)
    workflow.add_node("brief", brief_node)
    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "cluster")
    workflow.add_edge("cluster", "brief")
    workflow.add_edge("brief", END)
    graph = workflow.compile()
    return graph.invoke(
        {
            "query": query,
            "signals": [],
            "clusters": [],
            "briefs": [],
        }
    )
