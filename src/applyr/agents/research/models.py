from datetime import datetime
from enum import Enum

from pydantic import Field, HttpUrl

from applyr.core.models import ApplyrBaseModel, ScoredItem, SourceRef


class Platform(str, Enum):
    WEB = "web"
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    X = "x"
    OTHER = "other"


class SearchIntent(str, Enum):
    EDUCATIONAL = "educational"
    COMPARISON = "comparison"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"
    COMMERCIAL = "commercial"
    OTHER = "other"


class ResearchQuery(ApplyrBaseModel):
    topic: str
    audience: str | None = None
    market: str | None = None
    goals: list[str] = Field(default_factory=list)
    platforms: list[Platform] = Field(default_factory=lambda: [Platform.WEB, Platform.YOUTUBE])
    max_results_per_source: int = Field(default=10, ge=1, le=50)


class ResearchSignal(ApplyrBaseModel):
    title: str
    platform: Platform
    url: HttpUrl | None = None
    source: SourceRef | None = None
    summary: str | None = None
    published_at: datetime | None = None
    author: str | None = None
    view_count: int | None = Field(default=None, ge=0)
    like_count: int | None = Field(default=None, ge=0)
    comment_count: int | None = Field(default=None, ge=0)
    relevance_score: float | None = Field(default=None, ge=0, le=10)
    intent: SearchIntent = SearchIntent.OTHER
    keywords: list[str] = Field(default_factory=list)
    hooks: list[str] = Field(default_factory=list)


class TrendCluster(ApplyrBaseModel):
    name: str
    description: str
    signals: list[ResearchSignal] = Field(default_factory=list)
    core_keywords: list[str] = Field(default_factory=list)
    audience_pains: list[str] = Field(default_factory=list)
    audience_desires: list[str] = Field(default_factory=list)
    competition_level: float = Field(ge=0, le=10)
    opportunity_score: float = Field(ge=0, le=10)


class OpportunityScoreBreakdown(ApplyrBaseModel):
    demand: float = Field(ge=0, le=10)
    competition: float = Field(ge=0, le=10)
    novelty: float = Field(ge=0, le=10)
    monetization: float = Field(ge=0, le=10)
    execution_fit: float = Field(ge=0, le=10)


class ContentBrief(ScoredItem):
    title: str
    angle: str
    target_audience: str
    primary_keyword: str
    supporting_keywords: list[str] = Field(default_factory=list)
    hook: str
    outline: list[str] = Field(default_factory=list)
    thumbnail_concept: str
    cluster: TrendCluster
    breakdown: OpportunityScoreBreakdown
    references: list[SourceRef] = Field(default_factory=list)
