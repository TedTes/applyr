from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from applyr.agents.research.models import (
    ContentBrief,
    OpportunityScoreBreakdown,
    Platform,
    ResearchQuery,
    ResearchSignal,
    SearchIntent,
    TrendCluster,
)
from applyr.core.models import SourceRef


@dataclass(frozen=True)
class ResearchWorkflowResult:
    query: ResearchQuery
    signals: list[ResearchSignal]
    clusters: list[TrendCluster]
    briefs: list[ContentBrief]


def run_research_workflow(query: ResearchQuery, limit: int = 5) -> ResearchWorkflowResult:
    signals = collect_signals(query)
    clusters = cluster_signals(signals)
    briefs = generate_content_briefs(query, clusters, limit=limit)
    return ResearchWorkflowResult(query=query, signals=signals, clusters=clusters, briefs=briefs)


def collect_signals(query: ResearchQuery) -> list[ResearchSignal]:
    topic = query.topic
    return [
        ResearchSignal(
            title=f"{topic}: beginner setup tutorial",
            platform=Platform.YOUTUBE,
            url="https://youtube.com/watch?v=example1",
            source=SourceRef(name="YouTube Seed", url="https://youtube.com"),
            summary="High-intent tutorial content aimed at developers who want a first project.",
            author="BuildFast",
            view_count=185000,
            like_count=9200,
            comment_count=480,
            relevance_score=8.9,
            intent=SearchIntent.EDUCATIONAL,
            keywords=["tutorial", "beginner", "setup", "project"],
            hooks=["Build your first working system", "Avoid setup mistakes"],
        ),
        ResearchSignal(
            title=f"Best tools for {topic}",
            platform=Platform.WEB,
            url="https://example.com/best-tools-ai-agents",
            source=SourceRef(name="Web Seed", url="https://example.com"),
            summary="Tool comparison pages are attracting commercial and comparison intent.",
            relevance_score=8.1,
            intent=SearchIntent.COMPARISON,
            keywords=["best tools", "comparison", "stack"],
            hooks=["Which tool should you pick", "Fast stack comparison"],
        ),
        ResearchSignal(
            title=f"{topic} mistakes everyone makes",
            platform=Platform.YOUTUBE,
            url="https://youtube.com/watch?v=example2",
            source=SourceRef(name="YouTube Seed", url="https://youtube.com"),
            summary="Mistake-driven content is performing because it reduces fear and speeds entry.",
            author="ShipLabs",
            view_count=94000,
            like_count=5300,
            comment_count=310,
            relevance_score=8.4,
            intent=SearchIntent.EDUCATIONAL,
            keywords=["mistakes", "avoid", "beginner"],
            hooks=["Stop wasting time", "Common failure modes"],
        ),
        ResearchSignal(
            title=f"How companies use {topic} in production",
            platform=Platform.WEB,
            url="https://example.com/production-ai-agents",
            source=SourceRef(name="Web Seed", url="https://example.com"),
            summary="Case-study content suggests strong interest in practical business adoption.",
            relevance_score=7.7,
            intent=SearchIntent.COMMERCIAL,
            keywords=["case study", "production", "business"],
            hooks=["Real business outcomes", "Behind the scenes architecture"],
        ),
        ResearchSignal(
            title=f"{topic} news and trends",
            platform=Platform.WEB,
            url="https://example.com/ai-agent-trends",
            source=SourceRef(name="Web Seed", url="https://example.com"),
            summary="Trend roundups capture top-of-funnel interest but age quickly.",
            relevance_score=6.8,
            intent=SearchIntent.NEWS,
            keywords=["trends", "news", "2026"],
            hooks=["What changed this month", "What to watch next"],
        ),
    ]


def cluster_signals(signals: list[ResearchSignal]) -> list[TrendCluster]:
    buckets: dict[str, list[ResearchSignal]] = {
        "Beginner Tutorials": [],
        "Tooling Comparisons": [],
        "Production Use Cases": [],
    }
    for signal in signals:
        title = signal.title.lower()
        keywords = {keyword.lower() for keyword in signal.keywords}
        if keywords & {"tutorial", "mistakes", "beginner", "setup", "project"} or any(
            phrase in title for phrase in ["setup tutorial", "mistakes everyone makes"]
        ):
            buckets["Beginner Tutorials"].append(signal)
        elif keywords & {"best tools", "comparison", "stack"} or "best tools" in title:
            buckets["Tooling Comparisons"].append(signal)
        else:
            buckets["Production Use Cases"].append(signal)

    clusters: list[TrendCluster] = []
    for name, items in buckets.items():
        if not items:
            continue
        avg_relevance = mean([(item.relevance_score or 0) for item in items])
        if name == "Beginner Tutorials":
            competition_level = 7.0
            opportunity_score = round(min(10.0, avg_relevance + 0.3), 2)
            pains = ["Too much setup confusion", "No fast first win"]
            desires = ["Clear first project", "Simple roadmap"]
            keywords = ["tutorial", "beginner", "project"]
        elif name == "Tooling Comparisons":
            competition_level = 6.4
            opportunity_score = round(min(10.0, avg_relevance + 0.5), 2)
            pains = ["Too many tools", "Hard to compare tradeoffs"]
            desires = ["Fast decision making", "Clear recommendations"]
            keywords = ["comparison", "stack", "best tools"]
        else:
            competition_level = 5.9
            opportunity_score = round(min(10.0, avg_relevance + 0.7), 2)
            pains = ["Hard to see business value", "Few real implementation examples"]
            desires = ["Real-world proof", "Production patterns"]
            keywords = ["production", "case study", "business"]

        clusters.append(
            TrendCluster(
                name=name,
                description=f"Cluster derived from {len(items)} normalized signals.",
                signals=items,
                core_keywords=keywords,
                audience_pains=pains,
                audience_desires=desires,
                competition_level=competition_level,
                opportunity_score=opportunity_score,
            )
        )

    return sorted(clusters, key=lambda cluster: cluster.opportunity_score, reverse=True)


def generate_content_briefs(
    query: ResearchQuery,
    clusters: list[TrendCluster],
    limit: int = 5,
) -> list[ContentBrief]:
    briefs: list[ContentBrief] = []
    audience = query.audience or "builders and creators evaluating this topic"
    for cluster in clusters[:limit]:
        breakdown = score_cluster(cluster)
        primary_keyword = cluster.core_keywords[0] if cluster.core_keywords else query.topic
        title = build_title(query.topic, cluster.name)
        hook = cluster.audience_desires[0] if cluster.audience_desires else "Clear takeaway and execution path"
        references = [signal.source for signal in cluster.signals if signal.source]
        briefs.append(
            ContentBrief(
                title=title,
                angle=f"{cluster.name.lower()} angle for {query.topic}",
                target_audience=audience,
                primary_keyword=primary_keyword,
                supporting_keywords=cluster.core_keywords[1:],
                hook=hook,
                outline=[
                    f"Explain why {cluster.name.lower()} matters now.",
                    f"Walk through the core friction points: {', '.join(cluster.audience_pains)}.",
                    "Show a specific example or workflow.",
                    "Close with a practical next step for the viewer.",
                ],
                thumbnail_concept=f"Bold promise around {primary_keyword} with one concrete visual contrast.",
                cluster=cluster,
                breakdown=breakdown,
                score=round(mean(breakdown.model_dump().values()), 2),
                rationale=f"{cluster.name} balances demand and practical execution for this topic.",
                references=references,
            )
        )
    return briefs


def score_cluster(cluster: TrendCluster) -> OpportunityScoreBreakdown:
    demand = min(10.0, round(cluster.opportunity_score + 0.4, 1))
    competition = max(0.0, round(10 - cluster.competition_level, 1))
    novelty = 7.5 if cluster.name != "Beginner Tutorials" else 6.5
    monetization = 7.8 if cluster.name in {"Tooling Comparisons", "Production Use Cases"} else 6.8
    execution_fit = 8.2
    return OpportunityScoreBreakdown(
        demand=demand,
        competition=competition,
        novelty=novelty,
        monetization=monetization,
        execution_fit=execution_fit,
    )


def build_title(topic: str, cluster_name: str) -> str:
    if cluster_name == "Beginner Tutorials":
        return f"How to Start with {topic} Without Getting Lost"
    if cluster_name == "Tooling Comparisons":
        return f"The Best Stack for {topic}: What Actually Matters"
    return f"How {topic} Works in Production"
