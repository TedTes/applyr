from __future__ import annotations

import asyncio
from collections.abc import Iterable

from core.logging import get_logger
from researcher.fixtures import default_signal_seed
from researcher.models import SignalQuery, SignalRecord, SourceType

logger = get_logger(__name__)


async def collect_review_signals(
    query: SignalQuery,
    records: list[SignalRecord] | None = None,
) -> list[SignalRecord]:
    await asyncio.sleep(0)
    if records is None:
        logger.info("live review collection not implemented yet; using seeded review records")
        records = default_signal_seed()
    allowed_sources = set(query.review_sites) & {SourceType.G2, SourceType.CAPTERRA}
    return _filter_records(records, query, allowed_sources)


def _filter_records(
    records: Iterable[SignalRecord],
    query: SignalQuery,
    allowed_sources: set[SourceType],
) -> list[SignalRecord]:
    phrases = [phrase.lower() for phrase in query.pain_phrases]
    verticals = [vertical.lower() for vertical in query.verticals]
    filtered: list[SignalRecord] = []
    for record in records:
        if record.source not in allowed_sources:
            continue
        text = f"{record.title} {record.body} {' '.join(str(value) for value in record.metadata.values())}".lower()
        if verticals and not any(vertical in text for vertical in verticals):
            continue
        is_three_star_review = record.metadata.get("star_rating") == 3
        if phrases and not is_three_star_review and not any(phrase in text for phrase in phrases):
            continue
        filtered.append(record)
        if len(filtered) >= query.max_results_per_source:
            break
    return filtered
