import json
from typing import Any

from core.config import get_settings
from core.logging import get_logger
from researcher.models import OpportunityScoreBreakdown, ScoredOpportunity, SignalQuery, SignalRecord, SourceType

logger = get_logger(__name__)


def rank_opportunities(
    query: SignalQuery,
    records: list[SignalRecord],
    limit: int = 10,
) -> list[ScoredOpportunity]:
    opportunities = [score_record(query, record) for record in records]
    return sorted(opportunities, key=lambda item: item.total_score, reverse=True)[:limit]


def score_record(query: SignalQuery, record: SignalRecord) -> ScoredOpportunity:
    if query.use_claude:
        scored = _score_record_with_claude(record)
        if scored is not None:
            return scored
        logger.info("falling back to heuristic scoring for %s", record.id)

    text = f"{record.title} {record.body}".lower()
    pain_intensity = _score_from_keywords(text, ["takes me hours", "painful", "drop", "manual", "duplicate"], base=5.5)
    willingness_to_pay = _score_from_keywords(
        text,
        ["manager", "team", "clinic", "customers", "leads", "insurance", "contractors"],
        base=5.0,
    )
    frequency = _score_from_keywords(text, ["every week", "daily", "every friday", "half the day", "recurring"], base=5.5)
    market_size = _score_market_size(text, query.verticals)
    competition_gap = _score_competition_gap(record)

    breakdown = OpportunityScoreBreakdown(
        pain_intensity=pain_intensity,
        willingness_to_pay=willingness_to_pay,
        frequency=frequency,
        market_size=market_size,
        competition_gap=competition_gap,
    )
    summary = _build_pain_summary(record)
    rationale = (
        f"{record.source.value} signal with source score {record.source_score} suggests repeatable workflow friction "
        f"and a software gap around {summary.lower()}."
    )
    return ScoredOpportunity(
        record=record,
        breakdown=breakdown,
        total_score=breakdown.total,
        pain_summary=summary,
        rationale=rationale,
    )


def _score_record_with_claude(record: SignalRecord) -> ScoredOpportunity | None:
    settings = get_settings()
    if not settings.anthropic_api_key:
        return None

    try:
        from anthropic import Anthropic
    except Exception:
        logger.warning("anthropic sdk unavailable; using heuristic scoring")
        return None

    client = Anthropic(api_key=settings.anthropic_api_key)
    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=350,
            temperature=0,
            system=(
                "You score SaaS opportunity signals. "
                "Return only JSON with keys: pain_intensity, willingness_to_pay, "
                "frequency, market_size, competition_gap, pain_summary, rationale."
            ),
            messages=[
                {
                    "role": "user",
                    "content": _build_claude_prompt(record),
                }
            ],
        )
    except Exception as exc:
        logger.warning("anthropic scoring failed for %s: %s", record.id, exc)
        return None

    payload = _extract_json_payload(response.content)
    if payload is None:
        logger.warning("anthropic response was not valid JSON for %s", record.id)
        return None

    try:
        breakdown = OpportunityScoreBreakdown(
            pain_intensity=float(payload["pain_intensity"]),
            willingness_to_pay=float(payload["willingness_to_pay"]),
            frequency=float(payload["frequency"]),
            market_size=float(payload["market_size"]),
            competition_gap=float(payload["competition_gap"]),
        )
        pain_summary = str(payload["pain_summary"]).strip()
        rationale = str(payload["rationale"]).strip()
    except (KeyError, TypeError, ValueError):
        logger.warning("anthropic response missing required scoring fields for %s", record.id)
        return None

    return ScoredOpportunity(
        record=record,
        breakdown=breakdown,
        total_score=breakdown.total,
        pain_summary=pain_summary,
        rationale=rationale,
    )


def _build_claude_prompt(record: SignalRecord) -> str:
    return (
        "Score this SaaS opportunity signal on a 0-10 scale for each dimension.\n"
        f"Source: {record.source.value}\n"
        f"Title: {record.title}\n"
        f"Body: {record.body}\n"
        f"Source score: {record.source_score}\n"
        f"Metadata: {json.dumps(record.metadata, sort_keys=True)}\n"
        "Dimensions:\n"
        "- pain_intensity\n"
        "- willingness_to_pay\n"
        "- frequency\n"
        "- market_size\n"
        "- competition_gap\n"
        "Also include a one-line pain_summary and a short rationale."
    )


def _extract_json_payload(content_blocks: list[Any]) -> dict[str, Any] | None:
    text_parts: list[str] = []
    for block in content_blocks:
        text = getattr(block, "text", None)
        if text:
            text_parts.append(text)

    text = "\n".join(text_parts).strip()
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None


def _score_from_keywords(text: str, keywords: list[str], base: float) -> float:
    hits = sum(1 for keyword in keywords if keyword in text)
    return round(min(10.0, base + hits * 0.9), 2)


def _score_market_size(text: str, verticals: list[str]) -> float:
    role_hits = sum(
        1
        for keyword in ["team", "staff", "customers", "clinic", "dispatch", "front-desk", "contractors", "leads"]
        if keyword in text
    )
    vertical_bonus = 0.5 if verticals else 0
    return round(min(10.0, 5.5 + role_hits * 0.5 + vertical_bonus), 2)


def _score_competition_gap(record: SignalRecord) -> float:
    if record.source in {SourceType.G2, SourceType.CAPTERRA}:
        return 8.4
    if record.source == SourceType.REDDIT and record.source_score >= 600:
        return 7.8
    return 7.2


def _build_pain_summary(record: SignalRecord) -> str:
    body = record.body.lower()
    if "spreadsheet" in body:
        return "teams are still managing core workflow steps in spreadsheets"
    if "duplicate data entry" in body or "re-enter" in body:
        return "staff are wasting time on duplicate data entry"
    if "reconcile" in body:
        return "financial reconciliation is still manual"
    if "call customers" in body:
        return "schedule changes trigger manual customer coordination"
    return "teams are relying on manual process workarounds"
