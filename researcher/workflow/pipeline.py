from __future__ import annotations

import asyncio
from dataclasses import dataclass

from core.cache import FileCache
from core.config import get_settings
from core.logging import get_logger
from researcher.collectors import collect_reddit_signals, collect_review_signals
from researcher.fixtures import default_signal_seed, load_signal_fixture
from researcher.models import ScoredOpportunity, SignalQuery, SignalRecord
from researcher.workflow.aggregator import normalize_records
from researcher.workflow.scorer import rank_opportunities

logger = get_logger(__name__)
cache = FileCache(get_settings().cache_dir)


@dataclass(frozen=True)
class SignalWorkflowResult:
    query: SignalQuery
    collected_records: list[SignalRecord]
    normalized_records: list[SignalRecord]
    opportunities: list[ScoredOpportunity]


def collect_signals(query: SignalQuery, seed_records: list[SignalRecord] | None = None) -> list[SignalRecord]:
    if seed_records is not None:
        logger.info("using seeded signal records")
        source_records = seed_records
    else:
        source_records = _load_source_records(query)

    async def gather() -> list[SignalRecord]:
        tasks = [collect_reddit_signals(query, source_records)]
        if query.review_sites:
            tasks.append(collect_review_signals(query, source_records))
        collected_by_source = await asyncio.gather(*tasks)
        merged: list[SignalRecord] = []
        for batch in collected_by_source:
            merged.extend(batch)
        return merged

    collected = asyncio.run(gather())
    if seed_records is None and source_records is None and collected:
        cache.set("signals", query.model_dump_json(), [item.model_dump(mode="json") for item in collected])
    logger.info("signal collection returned %s records", len(collected))
    return collected


def run_signal_workflow(
    query: SignalQuery,
    limit: int = 10,
    seed_records: list[SignalRecord] | None = None,
) -> SignalWorkflowResult:
    collected = collect_signals(query, seed_records=seed_records)
    normalized = normalize_records(collected)
    opportunities = rank_opportunities(query, normalized, limit=limit)
    return SignalWorkflowResult(
        query=query,
        collected_records=collected,
        normalized_records=normalized,
        opportunities=opportunities,
    )


def _load_source_records(query: SignalQuery) -> list[SignalRecord] | None:
    cache_key = query.model_dump_json()
    cached = cache.get("signals", cache_key)
    if cached:
        logger.info("signal cache hit")
        return [SignalRecord.model_validate(item) for item in cached]

    logger.info("signal cache miss; attempting live collection")
    return None
