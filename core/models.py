from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SignalBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class SourceRef(SignalBaseModel):
    name: str
    url: HttpUrl | None = None
    collected_at: datetime | None = None


class ScoredItem(SignalBaseModel):
    score: float = Field(ge=0, le=10)
    rationale: str
