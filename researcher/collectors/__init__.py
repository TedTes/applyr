"""Source collectors for researcher."""

from researcher.collectors.reddit import collect_reddit_signals
from researcher.collectors.reviews import collect_review_signals

__all__ = ["collect_reddit_signals", "collect_review_signals"]
