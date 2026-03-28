from __future__ import annotations

import asyncio
from collections.abc import Iterable
from datetime import datetime, UTC

import requests

from core.config import get_settings
from core.logging import get_logger
from core.models import SourceRef
from core.retry import retry
from researcher.fixtures import default_signal_seed
from researcher.models import SignalQuery, SignalRecord, SourceType

logger = get_logger(__name__)


async def collect_reddit_signals(
    query: SignalQuery,
    records: list[SignalRecord] | None = None,
) -> list[SignalRecord]:
    if records is not None:
        return _filter_records(records, query, {SourceType.REDDIT})
    return await asyncio.to_thread(fetch_reddit_signals, query)


@retry(exceptions=(requests.RequestException,))
def fetch_reddit_signals(query: SignalQuery) -> list[SignalRecord]:
    settings = get_settings()
    headers = {"User-Agent": settings.reddit_user_agent}
    collected: list[SignalRecord] = []
    seen_urls: set[str] = set()

    for subreddit in query.subreddits:
        for search_term in _build_search_terms(query):
            response = requests.get(
                f"https://www.reddit.com/r/{subreddit}/search.json",
                headers=headers,
                params={
                    "q": search_term,
                    "restrict_sr": "1",
                    "sort": "top",
                    "limit": str(query.max_results_per_source),
                    "t": "year",
                },
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            for record in parse_reddit_response(payload, subreddit=subreddit):
                url_key = str(record.url)
                if url_key in seen_urls:
                    continue
                seen_urls.add(url_key)
                collected.append(record)
                if len(collected) >= query.max_results_per_source:
                    return collected

    if collected:
        return collected

    logger.info("reddit live collection returned no records; falling back to seed data")
    return _filter_records(default_signal_seed(), query, {SourceType.REDDIT})


def parse_reddit_response(payload: dict, subreddit: str) -> list[SignalRecord]:
    children = payload.get("data", {}).get("children", [])
    records: list[SignalRecord] = []
    for child in children:
        data = child.get("data", {})
        permalink = data.get("permalink")
        if not permalink:
            continue
        body = data.get("selftext") or data.get("title") or ""
        created_utc = data.get("created_utc")
        collected_at = (
            datetime.fromtimestamp(created_utc, tz=UTC) if isinstance(created_utc, int | float) else None
        )
        records.append(
            SignalRecord(
                id=f"reddit_{data.get('id', permalink.split('/')[-2])}",
                source=SourceType.REDDIT,
                title=data.get("title") or "Untitled Reddit post",
                body=body,
                url=f"https://www.reddit.com{permalink}",
                source_ref=SourceRef(name="Reddit", url=f"https://www.reddit.com/r/{subreddit}"),
                source_score=float(data.get("score", 0)),
                collected_at=collected_at,
                metadata={
                    "subreddit": data.get("subreddit") or subreddit,
                    "author": data.get("author"),
                    "num_comments": data.get("num_comments"),
                },
            )
        )
    return records


def _build_search_terms(query: SignalQuery) -> list[str]:
    if not query.verticals:
        return query.pain_phrases

    terms: list[str] = []
    for vertical in query.verticals:
        for phrase in query.pain_phrases:
            terms.append(f'"{vertical}" "{phrase}"')
    return terms


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
        if phrases and not any(phrase in text for phrase in phrases):
            continue
        filtered.append(record)
        if len(filtered) >= query.max_results_per_source:
            break
    return filtered
