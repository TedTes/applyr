from datetime import datetime
from enum import Enum

from pydantic import Field, HttpUrl

from core.models import SignalBaseModel, SourceRef


class SourceType(str, Enum):
    REDDIT = "reddit"
    G2 = "g2"
    CAPTERRA = "capterra"
    INDEED = "indeed"


class SignalQuery(SignalBaseModel):
    verticals: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=lambda: ["smallbusiness", "entrepreneur", "marketing"])
    review_sites: list[SourceType] = Field(default_factory=lambda: [SourceType.G2, SourceType.CAPTERRA])
    pain_phrases: list[str] = Field(
        default_factory=lambda: [
            "manually do",
            "wish there was a tool",
            "takes me hours",
            "spreadsheet",
            "reconcile",
            "data entry",
        ]
    )
    max_results_per_source: int = Field(default=5, ge=1, le=25)
    use_claude: bool = False


class SignalRecord(SignalBaseModel):
    id: str
    source: SourceType
    title: str
    body: str
    url: HttpUrl
    source_ref: SourceRef | None = None
    source_score: float = Field(default=0, ge=0)
    raw_score: float | None = Field(default=None, ge=0, le=50)
    collected_at: datetime | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class OpportunityScoreBreakdown(SignalBaseModel):
    pain_intensity: float = Field(ge=0, le=10)
    willingness_to_pay: float = Field(ge=0, le=10)
    frequency: float = Field(ge=0, le=10)
    market_size: float = Field(ge=0, le=10)
    competition_gap: float = Field(ge=0, le=10)

    @property
    def total(self) -> float:
        return round(sum(self.model_dump().values()), 2)


class ScoredOpportunity(SignalBaseModel):
    record: SignalRecord
    breakdown: OpportunityScoreBreakdown
    total_score: float = Field(ge=0, le=50)
    pain_summary: str
    rationale: str
